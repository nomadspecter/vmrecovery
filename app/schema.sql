-- Database design for the Automated Virtual Machine Recovery System.
-- Matches the ERD in Chapter Two, plus three small operational columns on vms
-- (heartbeat_property, fail_count, last_checked) used by the health monitor.

CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin', 'trainer'))
);

CREATE TABLE IF NOT EXISTS snapshot_policies (
    policy_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    interval_minutes     INTEGER NOT NULL CHECK (interval_minutes > 0),
    retention_count      INTEGER NOT NULL CHECK (retention_count > 0),
    pre_session_snapshot INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vms (
    vm_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id          INTEGER NOT NULL REFERENCES snapshot_policies(policy_id),
    created_by         INTEGER REFERENCES users(user_id),
    vm_name            TEXT NOT NULL,
    vbox_uuid          TEXT NOT NULL UNIQUE,
    class_group        TEXT NOT NULL DEFAULT 'General',
    status             TEXT NOT NULL DEFAULT 'unknown',
    heartbeat_property TEXT,
    fail_count         INTEGER NOT NULL DEFAULT 0,
    last_checked       TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id         INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE,
    snapshot_name TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id      INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL,
    user_id    INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    details    TEXT NOT NULL DEFAULT '',
    result     TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_vm ON snapshots(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_vm ON events(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, created_at);
