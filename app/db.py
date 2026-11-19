"""SQLite helpers: one connection per request (web) or per cycle (worker).

The schema lives in ``schema.sql`` and is applied on every start with
``CREATE TABLE IF NOT EXISTS``, so a fresh database and an upgraded one follow
the same path. Changes to *existing* tables are numbered migrations that run
exactly once and are recorded in the ``schema_meta`` table.
"""
import logging
import sqlite3
from pathlib import Path

from .pg_db import connect_pg, init_pg_db, is_postgres_url

SCHEMA = Path(__file__).with_name("schema.sql")

# The schema file is split in two: the tables first, then the indexes. The
# indexes are applied after the migrations, because an index on a column that
# an old database does not have yet cannot be created.
INDEX_MARKER = "-- INDEXES ---"

# Bump this and add a migration to match whenever the schema changes.
SCHEMA_VERSION = 8

log = logging.getLogger("vmrecovery")


def connect(path: str):
    """Open a connection to the application database (SQLite or PostgreSQL)."""
    if is_postgres_url(path):
        return connect_pg(path)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # timeout= sets the busy handler, so the pragmas below wait for a lock
    # held by another connection instead of failing straight away.
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    # The journal mode is a property of the file, not of the connection, so
    # it only has to be set once. Asking for it on every connection takes a
    # lock for nothing, and that lock is what the rest of the system waits on.
    if conn.execute("PRAGMA journal_mode").fetchone()[0].lower() != "wal":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list:
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                        (table,)).fetchone() is not None


def _add_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if _has_table(conn, table) and column not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
        log.info("Migration: added %s.%s", table, column)


# ---------------------------------------------------------------- migrations
def _m1_columns(conn):
    """Template and student-assignment columns on the VM registry.

    Every column the current code expects is checked, not just the two that
    were added in this release, so a database from any older version of the
    project is brought up to date in one pass.
    """
    _add_column(conn, "vms", "policy_id", "INTEGER NOT NULL DEFAULT 0")
    _add_column(conn, "vms", "created_by", "INTEGER REFERENCES users(user_id)")
    _add_column(conn, "vms", "class_group", "TEXT NOT NULL DEFAULT 'General'")
    _add_column(conn, "vms", "status", "TEXT NOT NULL DEFAULT 'unknown'")
    _add_column(conn, "vms", "heartbeat_property", "TEXT")
    _add_column(conn, "vms", "fail_count", "INTEGER NOT NULL DEFAULT 0")
    _add_column(conn, "vms", "last_checked", "TEXT")
    _add_column(conn, "vms", "is_template", "INTEGER NOT NULL DEFAULT 0")
    _add_column(conn, "vms", "assigned_student_id",
                "INTEGER REFERENCES users(user_id) ON DELETE SET NULL")
    _add_column(conn, "vms", "admin_paused", "INTEGER NOT NULL DEFAULT 0")


def _m2_user_roles(conn):
    """Allow the 'student' role.

    Older databases created the users table with a CHECK constraint that only
    knew admin and trainer. Rebuilding the table is the only way to change
    that, so the documented SQLite procedure is used: build a replacement,
    copy the rows, drop the old table, rename the replacement into place.
    Foreign keys are off for the duration so the rebuild cannot cascade.
    """
    if not _has_table(conn, "users"):
        return
    sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if not sql or "'student'" in sql["sql"]:
        return
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("""
            CREATE TABLE users_migrated (
                user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL CHECK (role IN ('admin', 'trainer', 'student'))
            )""")
        conn.execute("INSERT INTO users_migrated (user_id, username, password_hash, role) "
                     "SELECT user_id, username, password_hash, role FROM users")
        conn.execute("DROP TABLE users")
        conn.execute("ALTER TABLE users_migrated RENAME TO users")
        log.info("Migration: rebuilt users table with the student role")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def _m3_user_timestamps(conn):
    """When an account was created and when it was last used."""
    # SQLite refuses a non-constant default in ALTER TABLE, so the column is
    # added with an empty default and the existing rows are filled in after.
    _add_column(conn, "users", "created_at", "TEXT NOT NULL DEFAULT ''")
    conn.execute("UPDATE users SET created_at = datetime('now','localtime') "
                 "WHERE created_at IS NULL OR created_at = ''")
    _add_column(conn, "users", "last_login_at", "TEXT")


def _m4_event_duration(conn):
    """Recovery duration as a number, not only as text in the details."""
    _add_column(conn, "events", "duration_seconds", "REAL")


def _m5_notification_vm(conn):
    """Link a notification to the machine it is about."""
    _add_column(conn, "notifications", "vm_id",
                "INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL")


_CANONICAL_TABLES = {
    "events": (
        "event_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "vm_id INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL, "
        "user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL, "
        "event_type TEXT NOT NULL, details TEXT NOT NULL DEFAULT '', "
        "result TEXT NOT NULL DEFAULT '', duration_seconds REAL, "
        "created_at TEXT NOT NULL"),
    "snapshots": (
        "snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "vm_id INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE, "
        "snapshot_name TEXT NOT NULL, snapshot_type TEXT NOT NULL, "
        "created_at TEXT NOT NULL"),
    "backups": (
        "backup_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "vm_id INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE, "
        "backup_name TEXT NOT NULL, file_path TEXT NOT NULL, "
        "size_bytes INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL"),
}


def _m6_repair_legacy_refs(conn):
    """Repair tables left pointing at a temporary name by an old upgrade.

    Very old versions of this project renamed the users table during a
    migration. SQLite keeps the old foreign-key text in the referencing
    tables, which then point at a table that no longer exists. The affected
    table is rebuilt from its canonical definition, carrying the rows over.
    """
    for table, columns in _CANONICAL_TABLES.items():
        if not _has_table(conn, table):
            continue
        sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                           (table,)).fetchone()
        if not sql or ("_users_old" not in sql["sql"] and "_vms_old" not in sql["sql"]):
            continue
        wanted = [c.strip().split(" ")[0] for c in columns.split(",")]
        available = _columns(conn, table)
        shared = [c for c in wanted if c in available]
        conn.execute(f"PRAGMA foreign_keys = OFF")
        try:
            conn.execute(f"CREATE TABLE {table}_repaired ({columns})")
            conn.execute(f"INSERT INTO {table}_repaired ({', '.join(shared)}) "
                         f"SELECT {', '.join(shared)} FROM {table}")
            conn.execute(f"DROP TABLE {table}")
            conn.execute(f"ALTER TABLE {table}_repaired RENAME TO {table}")
            log.info("Migration: repaired foreign keys on %s", table)
        finally:
            conn.execute("PRAGMA foreign_keys = ON")


def _m7_admin_paused(conn):
    """Remember that an administrator paused a machine on purpose.

    Without the flag the monitor would treat a deliberately paused VM as a
    frozen one and restore it, undoing the administrator's decision.
    """
    _add_column(conn, "vms", "admin_paused", "INTEGER NOT NULL DEFAULT 0")


def _m8_status_since(conn):
    """When the machine last entered the state it is in now.

    Without it there is no way to tell a machine that is briefly busy from one
    that VirtualBox has wedged, and a wedged machine used to sit there for
    hours without anybody being told.
    """
    _add_column(conn, "vms", "status_since", "TEXT")


MIGRATIONS = (
    (1, "vms: template and student columns", _m1_columns),
    (2, "users: allow the student role", _m2_user_roles),
    (3, "users: created and last-login timestamps", _m3_user_timestamps),
    (4, "events: duration in seconds", _m4_event_duration),
    (5, "notifications: link to a VM", _m5_notification_vm),
    (6, "repair legacy foreign keys", _m6_repair_legacy_refs),
    (7, "vms: flag machines paused by an administrator", _m7_admin_paused),
    (8, "vms: remember when the current state began", _m8_status_since),
)


def _current_version(conn: sqlite3.Connection) -> int:
    if not _has_table(conn, "schema_meta"):
        return 0
    row = conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
    return int(row["value"]) if row else 0


def init_db(path: str) -> int:
    """Create or upgrade the database. Returns the schema version in use."""
    if is_postgres_url(path):
        init_pg_db(path)
        return SCHEMA_VERSION

    conn = connect(path)
    try:
        conn.execute("PRAGMA legacy_alter_table = OFF")
        text = SCHEMA.read_text()
        tables, _, indexes = text.partition(INDEX_MARKER)
        conn.executescript(tables)

        version = _current_version(conn)
        for number, description, migration in MIGRATIONS:
            if number <= version:
                continue
            migration(conn)
            log.info("Migration %s applied: %s", number, description)
            version = number
        conn.execute("INSERT INTO schema_meta (key, value) VALUES ('schema_version', ?) "
                     "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                     (str(max(version, SCHEMA_VERSION)),))

        # The indexes come last, and one that cannot be built must not stop
        # the service from starting.
        for statement in indexes.split(";"):
            if statement.strip():
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as exc:
                    log.warning("Could not create an index: %s", exc)
        conn.commit()
        return max(version, SCHEMA_VERSION)
    finally:
        conn.close()


def backup_database(path: str, dest_dir: str, keep: int = 10) -> str:
    """Copy the application database to ``dest_dir`` and return the new path.

    SQLite's online backup API is used, so a backup taken while the service
    is running is consistent rather than a torn copy of a live file.
    """
    import time
    from datetime import datetime

    out_dir = Path(dest_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = out_dir / f"vmrecovery-{stamp}.db"
    counter = 1
    while dest.exists():                     # two backups in the same second
        dest = out_dir / f"vmrecovery-{stamp}-{counter}.db"
        counter += 1
    source = connect(path)
    target = sqlite3.connect(dest)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    _prune_database_backups(out_dir, keep)
    return str(dest)


def _prune_database_backups(out_dir: Path, keep: int) -> None:
    if keep <= 0:
        return
    backups = sorted(out_dir.glob("vmrecovery-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[keep:]:
        try:
            old.unlink()
        except OSError:
            pass


def restore_database(path: str, backup_file: str) -> None:
    """Replace the live database with a backup file."""
    src = Path(backup_file)
    if not src.exists():
        raise FileNotFoundError(f"Backup file '{backup_file}' does not exist.")
    target = Path(path)
    for suffix in ("-wal", "-shm"):
        side = target.with_name(target.name + suffix)
        if side.exists():
            side.unlink()
    target.write_bytes(src.read_bytes())
