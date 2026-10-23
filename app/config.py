"""Settings, read from environment variables so nothing is hard-coded.

Configuration is layered. Highest priority first:

  1. real environment variables (what systemd, Docker, or your shell set)
  2. ``.env.local``        - developer overrides, never committed, skipped in
                             production so the service can never be pointed at
                             a development database by accident
  3. ``instance/vmrecovery.env`` - machine-specific overrides for this host
  4. ``.env``              - shared local defaults, never committed
  5. the built-in defaults below

A sixth layer lives in the database: overrides written from the Settings page.
They are applied on top of everything above at runtime, so an administrator can
change a threshold without editing a file and without restarting the service.
"""
import os
import secrets
from dataclasses import dataclass, field, fields
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"

# Files searched for "KEY=value" lines, lowest priority first.
# instance/vmrecovery.env is the machine-specific override file, so it is read
# after the shared .env and therefore wins over it.
DOTENV_FILES = (
    BASE_DIR / ".env",
    INSTANCE_DIR / "vmrecovery.env",
    BASE_DIR / ".env.local",
)

# The file that holds developer-only overrides.
LOCAL_DOTENV = BASE_DIR / ".env.local"


def is_production() -> bool:
    """True when this process is serving the real system.

    ``.env.local`` holds developer overrides (a separate database, the
    simulator, a different port). Loading it in production would silently
    point the service at the wrong data, so it is skipped there.

    ``VMR_ENV=production`` is the explicit switch, and the systemd unit sets
    it. ``INVOCATION_ID`` is the fallback for a unit that was installed
    without it, but systemd passes that variable to everything the service
    spawns, so it is only trusted when this process is the service's own main
    process, whose parent is systemd itself. Without that check, a shell
    started from a systemd service would look like production and quietly lose
    the developer layer.
    """
    if os.environ.get("VMR_ENV", "").strip().lower() == "production":
        return True
    if os.environ.get("INVOCATION_ID") and os.getppid() == 1:
        return True
    return False


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _str(name: str, default: str = "") -> str:
    raw = os.environ.get(name)
    return raw if raw is not None else default


def parse_dotenv(text: str) -> dict:
    """Parse a ``KEY=value`` file into a dictionary.

    Blank lines and ``#`` comments are ignored, values may be wrapped in single
    or double quotes, and ``export KEY=value`` is accepted. Malformed lines are
    skipped rather than raising, because a typo in a local file must not stop
    the service from starting.
    """
    out: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        out[key] = value
    return out


def load_dotenv(files=DOTENV_FILES, env=None) -> dict:
    """Load configuration files into the environment.

    The files are read from the lowest priority to the highest, so a later file
    overrides an earlier one: ``instance/vmrecovery.env`` wins over ``.env``,
    and ``.env.local`` wins over both.

    Real environment variables always win over every file, so an operator can
    override a file with ``VMR_PORT=6000 python run.py`` without editing
    anything. Returns the mapping of variables that were actually applied, for
    logging.

    ``.env.local`` is skipped in production: it holds developer overrides that
    would otherwise point the service at a different database.
    """
    env = os.environ if env is None else env
    # The variables that were already in the environment belong to the
    # operator, and no file may overwrite them.
    protected = set(env)
    production = is_production()
    applied: dict[str, str] = {}
    for path in files:
        if Path(path).resolve() == LOCAL_DOTENV.resolve() and production:
            continue
        try:
            text = Path(path).read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for key, value in parse_dotenv(text).items():
            if key in protected:       # a real environment variable wins
                continue
            env[key] = value
            applied[key] = value
    return applied


def _secret_key() -> str:
    """Use VMR_SECRET if set, otherwise create and reuse a random key file."""
    env = os.environ.get("VMR_SECRET")
    if env:
        return env
    INSTANCE_DIR.mkdir(exist_ok=True)
    key_file = INSTANCE_DIR / "secret.key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32))
        key_file.chmod(0o600)
    return key_file.read_text().strip()


@dataclass
class Settings:
    db_path: str = str(INSTANCE_DIR / "vmrecovery.db")
    simulate: bool = False                 # True = fake VirtualBox (demo and tests)
    vboxmanage: str = "VBoxManage"         # path or command name
    check_seconds: int = 30                # how often the background worker runs
    fail_threshold: int = 2                # bad checks in a row before a VM counts as failed
    max_restores_per_hour: int = 3         # stops endless restore loops
    heartbeat_timeout: int = 90            # seconds without a heartbeat = frozen
    vbox_timeout: int = 1800               # seconds before a long VBoxManage command is killed
    vbox_query_timeout: int = 60           # seconds before a read-only VBoxManage query is killed
    vbox_action_timeout: int = 180         # seconds before a power/suspend/start command is killed
    vbox_restore_timeout: int = 600        # seconds before a snapshot restore is killed
    vbox_lock_timeout: int = 30            # seconds the worker waits for the VirtualBox lock
    live_snapshots: bool = False           # --live snapshots need a cooperative guest
    busy_timeout: int = 300                # seconds VirtualBox may stay busy before it counts as stuck
    run_worker: bool = True
    dev_server: bool = False               # True = Flask's development server, not waitress
    host: str = "127.0.0.1"
    port: int = 5000
    cookie_secure: bool = False            # set VMR_COOKIE_SECURE=1 when served over HTTPS
    session_hours: int = 12                # how long a login lasts
    log_level: str = "INFO"
    secret_key: str = ""
    backup_dir: str = str(INSTANCE_DIR / "backups")
    backup_retention_count: int = 3
    disk_min_free_gb: float = 5.0
    disk_min_free_pct: float = 10.0

    # --- added for the enterprise build -----------------------------------
    api_token: str = ""                    # bearer token for the read-only JSON API
    login_max_failures: int = 5            # failed logins per IP before a lockout
    login_window_seconds: int = 300        # length of the login lockout window
    event_retention_days: int = 90         # 0 = keep every event forever
    db_backup_dir: str = str(INSTANCE_DIR / "db-backups")
    db_backup_keep: int = 10               # rotated application-database backups to keep

    # --- notifications ------------------------------------------------------
    notify_email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""                      # comma separated recipients
    smtp_use_tls: bool = True
    notify_webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_secret: str = ""              # sent as X-VMRecovery-Signature

    # Runtime overrides applied on top of the file/environment configuration.
    overrides: dict = field(default_factory=dict)

    # The values the configuration files and the environment gave us, kept so
    # that a setting whose override is removed can go back to them. Filled in
    # on the first call to apply_overrides().
    base_values: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        b_dir = os.environ.get("VMR_BACKUP_DIR", str(INSTANCE_DIR / "backups"))
        Path(b_dir).mkdir(parents=True, exist_ok=True)
        d_dir = os.environ.get("VMR_DB_BACKUP_DIR", str(INSTANCE_DIR / "db-backups"))
        Path(d_dir).mkdir(parents=True, exist_ok=True)
        return cls(
            db_path=os.environ.get("VMR_DB", str(INSTANCE_DIR / "vmrecovery.db")),
            simulate=_bool("VMR_SIMULATE", False),
            vboxmanage=os.environ.get("VMR_VBOXMANAGE", "VBoxManage"),
            check_seconds=_int("VMR_CHECK_SECONDS", 30),
            fail_threshold=_int("VMR_FAIL_THRESHOLD", 2),
            max_restores_per_hour=_int("VMR_MAX_RESTORES_PER_HOUR", 3),
            heartbeat_timeout=_int("VMR_HEARTBEAT_TIMEOUT", 90),
            vbox_timeout=_int("VMR_VBOX_TIMEOUT", 1800),
            vbox_query_timeout=_int("VMR_VBOX_QUERY_TIMEOUT", 60),
            vbox_action_timeout=_int("VMR_VBOX_ACTION_TIMEOUT", 180),
            vbox_restore_timeout=_int("VMR_VBOX_RESTORE_TIMEOUT", 600),
            vbox_lock_timeout=_int("VMR_VBOX_LOCK_TIMEOUT", 30),
            live_snapshots=_bool("VMR_LIVE_SNAPSHOTS", False),
            busy_timeout=_int("VMR_BUSY_TIMEOUT", 300),
            run_worker=_bool("VMR_WORKER", True),
            dev_server=_bool("VMR_DEV_SERVER", False),
            host=os.environ.get("VMR_HOST", "127.0.0.1"),
            port=_int("VMR_PORT", 5000),
            cookie_secure=_bool("VMR_COOKIE_SECURE", False),
            session_hours=_int("VMR_SESSION_HOURS", 12),
            log_level=os.environ.get("VMR_LOG_LEVEL", "INFO").upper(),
            secret_key=_secret_key(),
            backup_dir=b_dir,
            backup_retention_count=_int("VMR_BACKUP_RETENTION", 3),
            disk_min_free_gb=_float("VMR_DISK_MIN_FREE_GB", 5.0),
            disk_min_free_pct=_float("VMR_DISK_MIN_FREE_PCT", 10.0),
            api_token=os.environ.get("VMR_API_TOKEN", "").strip(),
            login_max_failures=_int("VMR_LOGIN_MAX_FAILURES", 5),
            login_window_seconds=_int("VMR_LOGIN_WINDOW_SECONDS", 300),
            event_retention_days=_int("VMR_EVENT_RETENTION_DAYS", 90),
            db_backup_dir=d_dir,
            db_backup_keep=_int("VMR_DB_BACKUP_KEEP", 10),
            notify_email_enabled=_bool("VMR_NOTIFY_EMAIL", False),
            smtp_host=os.environ.get("VMR_SMTP_HOST", ""),
            smtp_port=_int("VMR_SMTP_PORT", 587),
            smtp_user=os.environ.get("VMR_SMTP_USER", ""),
            smtp_password=os.environ.get("VMR_SMTP_PASSWORD", ""),
            smtp_from=os.environ.get("VMR_SMTP_FROM", ""),
            smtp_to=os.environ.get("VMR_SMTP_TO", ""),
            smtp_use_tls=_bool("VMR_SMTP_TLS", True),
            notify_webhook_enabled=_bool("VMR_NOTIFY_WEBHOOK", False),
            webhook_url=os.environ.get("VMR_WEBHOOK_URL", ""),
            webhook_secret=os.environ.get("VMR_WEBHOOK_SECRET", ""),
        )

    # ------------------------------------------------------------------ helpers
    def apply_overrides(self, overrides: dict) -> None:
        """Apply database overrides on top of the current values.

        Unknown keys are ignored and values are coerced to the type of the
        matching dataclass field, so a bad value in the database can never
        break the running service.

        The values the configuration files and the environment provided are
        remembered on the first call. Every later call starts from them again
        and then applies the current overrides, so removing an override puts
        the setting back to what the configuration says. Without that, a
        setting that was reset in the browser would keep the old value in the
        running process until it was restarted, and the database and the
        process would disagree.
        """
        types = {f.name: f.type for f in fields(self)}
        if not self.base_values:
            # First time: remember where the configured values came from.
            self.base_values = {name: getattr(self, name) for name in types
                                if name not in ("overrides", "base_values")}
        else:
            for name, value in self.base_values.items():
                setattr(self, name, value)
        for key, value in (overrides or {}).items():
            if key not in types or key in ("overrides", "base_values"):
                continue
            want = types[key]
            try:
                if want is bool or want == "bool":
                    coerced = str(value).strip().lower() in ("1", "true", "yes", "on")
                elif want is int or want == "int":
                    coerced = int(str(value).strip())
                elif want is float or want == "float":
                    coerced = float(str(value).strip())
                else:
                    coerced = str(value)
            except (TypeError, ValueError):
                continue
            setattr(self, key, coerced)
        self.overrides = dict(overrides or {})

    def to_dict(self) -> dict:
        """The settings as a plain dictionary, with the secret key redacted."""
        data = {f.name: getattr(self, f.name) for f in fields(self)
                if f.name not in ("overrides", "base_values")}
        data["secret_key"] = "***" if data.get("secret_key") else ""
        data["smtp_password"] = "***" if data.get("smtp_password") else ""
        data["webhook_secret"] = "***" if data.get("webhook_secret") else ""
        data["api_token"] = "***" if data.get("api_token") else ""
        return data
