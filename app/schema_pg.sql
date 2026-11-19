-- PostgreSQL schema for Automated Virtual Machine Recovery System (Supabase)
-- Matches app/schema.sql with PostgreSQL data types and conventions.

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin', 'trainer', 'student')),
    created_at    TEXT NOT NULL DEFAULT TO_CHAR(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS'),
    last_login_at TEXT
);

CREATE TABLE IF NOT EXISTS snapshot_policies (
    policy_id            SERIAL PRIMARY KEY,
    interval_minutes     INTEGER NOT NULL CHECK (interval_minutes > 0),
    retention_count      INTEGER NOT NULL CHECK (retention_count > 0),
    pre_session_snapshot INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vms (
    vm_id               SERIAL PRIMARY KEY,
    policy_id           INTEGER NOT NULL REFERENCES snapshot_policies(policy_id),
    created_by          INTEGER REFERENCES users(user_id),
    vm_name             TEXT NOT NULL,
    vbox_uuid           TEXT NOT NULL UNIQUE,
    class_group         TEXT NOT NULL DEFAULT 'General',
    status              TEXT NOT NULL DEFAULT 'unknown',
    heartbeat_property  TEXT,
    fail_count          INTEGER NOT NULL DEFAULT 0,
    last_checked        TEXT,
    status_since        TEXT,
    is_template         INTEGER NOT NULL DEFAULT 0,
    assigned_student_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    admin_paused        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id   SERIAL PRIMARY KEY,
    vm_id         INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE,
    snapshot_name TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS backups (
    backup_id    SERIAL PRIMARY KEY,
    vm_id        INTEGER NOT NULL REFERENCES vms(vm_id) ON DELETE CASCADE,
    backup_name  TEXT NOT NULL,
    file_path    TEXT NOT NULL,
    size_bytes   BIGINT NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vm_requests (
    request_id         SERIAL PRIMARY KEY,
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

CREATE TABLE IF NOT EXISTS class_sessions (
    session_id  SERIAL PRIMARY KEY,
    class_group TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'ended')),
    started_by  INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    started_at  TEXT NOT NULL,
    ended_by    INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    ended_at    TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id         SERIAL PRIMARY KEY,
    vm_id            INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL,
    user_id          INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    event_type       TEXT NOT NULL,
    details          TEXT NOT NULL DEFAULT '',
    result           TEXT NOT NULL DEFAULT '',
    duration_seconds DOUBLE PRECISION,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    vm_id           INTEGER REFERENCES vms(vm_id) ON DELETE SET NULL,
    channel         TEXT NOT NULL,
    recipient       TEXT NOT NULL DEFAULT '',
    subject         TEXT NOT NULL,
    body            TEXT NOT NULL DEFAULT '',
    severity        TEXT NOT NULL DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'skipped')),
    error           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL,
    sent_at         TEXT
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_class_sessions_group ON class_sessions(class_group, started_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_session ON class_sessions(class_group) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_snapshots_vm ON snapshots(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_backups_vm ON backups(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_vm_requests_user ON vm_requests(user_id, status);
CREATE INDEX IF NOT EXISTS idx_events_vm ON events(vm_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, created_at);
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_vms_group ON vms(class_group);
