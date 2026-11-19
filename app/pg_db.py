"""PostgreSQL / Supabase adapter for VM Recovery System.

Provides seamless drop-in compatibility for connections, queries, and row
mappings when DATABASE_URL or SUPABASE_DB_URL points to a PostgreSQL instance.
"""
import logging
import re
from pathlib import Path

log = logging.getLogger("vmrecovery.pg")
SCHEMA_PG = Path(__file__).with_name("schema_pg.sql")


class PgRow:
    """Dict- and sequence-like row wrapper matching sqlite3.Row behavior."""

    def __init__(self, data: dict, col_order: list):
        self._data = dict(data)
        self._order = list(col_order)

    def __getitem__(self, item):
        if isinstance(item, int):
            col = self._order[item]
            return self._data[col]
        return self._data[item]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"PgRow({self._data})"


def _translate_sql(sql: str) -> tuple[str, bool]:
    """Translate SQLite query conventions to PostgreSQL."""
    is_insert = False
    cleaned = sql.strip()

    # Translate strftime('%Y-W%W', col) to Postgres to_char
    if "strftime('%Y-W%W'" in sql:
        sql = re.sub(
            r"strftime\('%Y-W%W',\s*([^)]+)\)",
            r"to_char(\1::timestamp, 'IYYY-IW')",
            sql
        )

    # Convert SQLite '?' paramstyle to PostgreSQL '%s'
    # We replace '?' that are not inside single quotes
    parts = []
    in_quote = False
    for ch in sql:
        if ch == "'":
            in_quote = not in_quote
            parts.append(ch)
        elif ch == "?" and not in_quote:
            parts.append("%s")
        else:
            parts.append(ch)
    translated = "".join(parts)

    # For INSERT statements without RETURNING, append RETURNING so cursor.lastrowid works
    if cleaned.upper().startswith("INSERT INTO") and "RETURNING" not in cleaned.upper():
        is_insert = True
        translated = translated.rstrip(";") + " RETURNING *"

    return translated, is_insert


class PgCursorWrapper:
    """Cursor wrapper that translates queries and wraps rows as PgRow."""

    def __init__(self, raw_cursor):
        self._cur = raw_cursor
        self.lastrowid = None
        self._col_names = []

    def execute(self, sql: str, params=None):
        translated, is_insert = _translate_sql(sql)
        args = tuple(params) if params is not None else ()
        self._cur.execute(translated, args)

        if self._cur.description:
            self._col_names = [d[0] for d in self._cur.description]
        else:
            self._col_names = []

        if is_insert:
            try:
                row = self._cur.fetchone()
                if row:
                    self.lastrowid = row[0]
                    # Restore cursor state if possible
                    self._insert_row = row
            except Exception:
                self.lastrowid = None
        return self

    def fetchone(self):
        if getattr(self, "_insert_row", None) is not None:
            r = self._insert_row
            self._insert_row = None
            d = dict(zip(self._col_names, r))
            return PgRow(d, self._col_names)

        row = self._cur.fetchone()
        if row is None:
            return None
        d = dict(zip(self._col_names, row))
        return PgRow(d, self._col_names)

    def fetchall(self):
        rows = self._cur.fetchall()
        out = []
        for r in rows:
            d = dict(zip(self._col_names, r))
            out.append(PgRow(d, self._col_names))
        return out

    def __iter__(self):
        while True:
            row = self.fetchone()
            if row is None:
                break
            yield row

    def close(self):
        self._cur.close()


class PgConnectionWrapper:
    """Connection wrapper conforming to DB-API 2.0 with .execute helper."""

    def __init__(self, raw_conn):
        self._conn = raw_conn

    def execute(self, sql: str, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def cursor(self):
        return PgCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def is_postgres_url(url: str) -> bool:
    if not url:
        return False
    u = url.strip().lower()
    return u.startswith("postgres://") or u.startswith("postgresql://")


def connect_pg(url: str) -> PgConnectionWrapper:
    """Connect to a PostgreSQL database using psycopg2.

    Automatically handles Supabase direct vs IPv4 connection poolers if direct
    IPv6 access is unreachable from cloud containers or local environments.
    """
    import psycopg2
    # Ensure protocol is postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    # Ensure sslmode=require for Supabase
    if "sslmode" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        return PgConnectionWrapper(conn)
    except psycopg2.OperationalError as exc:
        # Check if this is a Supabase direct URL that failed due to IPv6 routing
        m = re.search(r"://([^:]+):([^@]+)@db\.([a-z0-9]+)\.supabase\.co(?::\d+)?/([^\?]+)", url)
        if m:
            _, pw, ref, dbname = m.groups()
            candidate_regions = ["eu-central-1", "eu-west-1", "eu-west-2", "us-east-1", "us-west-1", "ap-southeast-1"]
            for reg in candidate_regions:
                pooler_host = f"aws-0-{reg}.pooler.supabase.com"
                for port in (5432, 6543):
                    pooler_url = f"postgresql://postgres.{ref}:{pw}@{pooler_host}:{port}/{dbname}?sslmode=require"
                    try:
                        conn = psycopg2.connect(pooler_url, connect_timeout=5)
                        log.info("Connected to Supabase via IPv4 pooler %s:%s", pooler_host, port)
                        return PgConnectionWrapper(conn)
                    except Exception:
                        continue
        raise exc


def init_pg_db(url: str) -> None:
    """Initialize PostgreSQL schema for Supabase."""
    conn = connect_pg(url)
    try:
        ddl = SCHEMA_PG.read_text()
        for statement in ddl.split(";"):
            cleaned = statement.strip()
            if cleaned:
                conn.execute(cleaned)
        conn.commit()
        log.info("Initialized PostgreSQL schema from %s", SCHEMA_PG.name)
    except Exception as exc:
        conn.rollback()
        log.exception("Could not initialize PostgreSQL schema: %s", exc)
        raise
    finally:
        conn.close()
