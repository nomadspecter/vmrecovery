"""Settings, read from environment variables so nothing is hard-coded."""
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"


def _bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(int(default))).lower() in ("1", "true", "yes", "on")


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
    run_worker: bool = True
    host: str = "127.0.0.1"
    port: int = 5000
    secret_key: str = ""
    backup_dir: str = str(INSTANCE_DIR / "backups")
    backup_retention_count: int = 3
    disk_min_free_gb: float = 5.0
    disk_min_free_pct: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        b_dir = os.environ.get("VMR_BACKUP_DIR", str(INSTANCE_DIR / "backups"))
        Path(b_dir).mkdir(parents=True, exist_ok=True)
        return cls(
            db_path=os.environ.get("VMR_DB", str(INSTANCE_DIR / "vmrecovery.db")),
            simulate=_bool("VMR_SIMULATE", False),
            vboxmanage=os.environ.get("VMR_VBOXMANAGE", "VBoxManage"),
            check_seconds=int(os.environ.get("VMR_CHECK_SECONDS", 30)),
            fail_threshold=int(os.environ.get("VMR_FAIL_THRESHOLD", 2)),
            max_restores_per_hour=int(os.environ.get("VMR_MAX_RESTORES_PER_HOUR", 3)),
            heartbeat_timeout=int(os.environ.get("VMR_HEARTBEAT_TIMEOUT", 90)),
            run_worker=_bool("VMR_WORKER", True),
            host=os.environ.get("VMR_HOST", "127.0.0.1"),
            port=int(os.environ.get("VMR_PORT", 5000)),
            secret_key=_secret_key(),
            backup_dir=b_dir,
            backup_retention_count=int(os.environ.get("VMR_BACKUP_RETENTION", 3)),
            disk_min_free_gb=float(os.environ.get("VMR_DISK_MIN_FREE_GB", 5.0)),
            disk_min_free_pct=float(os.environ.get("VMR_DISK_MIN_FREE_PCT", 10.0)),
        )
