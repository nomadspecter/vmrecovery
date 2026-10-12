-- Database design for the Automated Virtual Machine Recovery System.
-- Matches Chapter Two ERD and Class Diagrams with additions for:
-- templates, requests, independent backups, and student assignment.

CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin', 'trainer', 'student'))
);

CREATE TABLE IF NOT EXISTS snapshot_policies (
    policy_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    interval_minutes     INTEGER NOT NULL CHECK (interval_minutes > 0),
    retention_count      INTEGER NOT NULL CHECK (retention_count > 0),
    pre_session_snapshot INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vms (
    vm_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id           INTEGER NOT NULL REFERENCES snapshot_policies(policy_id),
    created_by          INTEGER REFERENCES users(user_id),
    vm_name             TEXT NOT NULL,
    vbox_uuid           TEXT NOT NULL UNIQUE,
    class_group         TEXT NOT NULL DEFAULT 'General',
    status              TEXT NOT NULL DEFAULT 'unknown',
    heartbeat_property  TEXT,
    fail_count          INTEGER NOT NULL DEFAULT 0,
    last_checked        TEXT,
    is_template         INTEGER NOT NULL DEFAULT 0,
    assigned_student_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id         INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE,
    snapshot_name TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS backups (
    backup_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id        INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE,
    backup_name  TEXT NOT NULL,
    file_path    TEXT NOT NULL,
    size_bytes   INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vm_requests (
    request_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    template_vbox_uuid TEXT NOT NULL,
    template_name      TEXT NOT NULL,
    requested_name     TEXT NOT NULL,
    class_group        TEXT NOT NULL DEFAULT 'General',
    clone_type         TEXT NOT NULL DEFAULT 'linked' CHECK (clone_type IN ('linked', 'full')),
    status             TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'creating', 'ready', 'rejected', 'failed')),
    rejection_reason   TEXT,
    created_vm_id      INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL,
    created_at         TEXT NOT NULL,
    updated_at         TEXT
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
CREATE INDEX IF NOT EXISTS idx_backups_vm ON backups(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_vm_requests_user ON vm_requests(user_id, status);
CREATE INDEX IF NOT EXISTS idx_events_vm ON events(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, created_at);
