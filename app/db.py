"""SQLite helpers: one connection per request (web) or per cycle (worker)."""
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")


def connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # web and worker can read/write together
    return conn


def init_db(path: str) -> None:
    conn = connect(path)
    try:
        conn.executescript(SCHEMA.read_text())
        # Migrations for existing databases
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(vms)").fetchall()]
        if columns and "is_template" not in columns:
            conn.execute("ALTER TABLE vms ADD COLUMN is_template INTEGER NOT NULL DEFAULT 0")
        if columns and "assigned_student_id" not in columns:
            conn.execute("ALTER TABLE vms ADD COLUMN assigned_student_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL")

        user_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if user_sql and "'student'" not in user_sql["sql"]:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("ALTER TABLE users RENAME TO _users_old")
            conn.execute("""
                CREATE TABLE users (
                    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role          TEXT NOT NULL CHECK (role IN ('admin', 'trainer', 'student'))
                )
            """)
            conn.execute("INSERT INTO users SELECT user_id, username, password_hash, role FROM _users_old")
            conn.execute("DROP TABLE _users_old")
            conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    finally:
        conn.close()
