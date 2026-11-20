"""Tests for the enterprise features:
- layered configuration (.env, .env.local, environment variables)
- runtime settings stored in the database and applied live
- email and webhook notifications, and the record of every attempt
- power control of individual machines, including a deliberate pause
- deleting a machine from VirtualBox
- the read-only JSON API and its token
- role scoping, event pagination and CSV export
- versioned schema migrations and database backup
"""
import os
import re
from datetime import datetime

import pytest

from app import create_app, db, services
from app.config import Settings, parse_dotenv
from app.vbox import SimulatedVBox
from tests.conftest import T0


# --------------------------------------------------------------------- config
def test_parse_dotenv_handles_quotes_comments_and_export():
    text = """
# a comment
VMR_PORT=6000
VMR_HOST="0.0.0.0"
VMR_SECRET='abc'
export VMR_LOG_LEVEL=DEBUG
not a pair
VMR_EMPTY=
"""
    values = parse_dotenv(text)
    assert values["VMR_PORT"] == "6000"
    assert values["VMR_HOST"] == "0.0.0.0"
    assert values["VMR_SECRET"] == "abc"
    assert values["VMR_LOG_LEVEL"] == "DEBUG"
    assert values["VMR_EMPTY"] == ""
    assert "not a pair" not in values


def test_real_environment_variable_beats_the_file(tmp_path, monkeypatch):
    from app.config import load_dotenv
    env_file = tmp_path / ".env"
    env_file.write_text("VMR_PORT=6000\nVMR_HOST=10.0.0.1\n")
    monkeypatch.setenv("VMR_PORT", "7000")
    monkeypatch.delenv("VMR_HOST", raising=False)
    env = dict(os.environ)                    # the real environment is the starting point
    applied = load_dotenv(files=(env_file,), env=env)
    assert env["VMR_PORT"] == "7000"          # the real variable wins
    assert env["VMR_HOST"] == "10.0.0.1"      # the file fills the gap
    assert applied == {"VMR_HOST": "10.0.0.1"}


def test_local_dotenv_is_skipped_in_production(tmp_path, monkeypatch):
    from app import config
    from app.config import load_dotenv
    local = tmp_path / ".env.local"
    local.write_text("VMR_SIMULATE=1\n")
    monkeypatch.setattr(config, "LOCAL_DOTENV", local)   # this is "the" local file
    monkeypatch.setenv("VMR_ENV", "production")
    env = {}
    load_dotenv(files=(local,), env=env)
    assert "VMR_SIMULATE" not in env


def test_the_local_file_is_loaded_outside_production(tmp_path, monkeypatch):
    from app import config
    from app.config import load_dotenv
    local = tmp_path / ".env.local"
    local.write_text("VMR_SIMULATE=1\n")
    monkeypatch.setattr(config, "LOCAL_DOTENV", local)
    monkeypatch.delenv("VMR_ENV", raising=False)
    monkeypatch.delenv("INVOCATION_ID", raising=False)
    env = {}
    load_dotenv(files=(local,), env=env)
    assert env["VMR_SIMULATE"] == "1"


def test_invocation_id_alone_does_not_mean_production(monkeypatch):
    """systemd passes INVOCATION_ID to everything it spawns, shells included."""
    from app.config import is_production
    monkeypatch.setenv("INVOCATION_ID", "abc123")
    monkeypatch.delenv("VMR_ENV", raising=False)
    # This process is not systemd's own main process, so it is not production.
    assert is_production() is (os.getppid() == 1)


def test_a_later_file_overrides_an_earlier_one(tmp_path):
    """The files are read lowest priority first, so the last one wins."""
    from app.config import load_dotenv
    shared = tmp_path / ".env"
    machine = tmp_path / "vmrecovery.env"
    local = tmp_path / ".env.local"
    shared.write_text("VMR_PORT=5000\nVMR_CHECK_SECONDS=30\n")
    machine.write_text("VMR_PORT=5100\n")
    local.write_text("VMR_PORT=5200\n")

    env = dict(os.environ)
    load_dotenv(files=(shared, machine, local), env=env)
    assert env["VMR_PORT"] == "5200"        # .env.local wins over both
    assert env["VMR_CHECK_SECONDS"] == "30"  # only the shared file set it

    env = dict(os.environ)
    load_dotenv(files=(shared, machine), env=env)
    assert env["VMR_PORT"] == "5100"        # the machine file wins over the shared one


def test_a_real_environment_variable_still_wins_over_every_file(tmp_path):
    from app.config import load_dotenv
    shared = tmp_path / ".env"
    local = tmp_path / ".env.local"
    shared.write_text("VMR_PORT=5000\n")
    local.write_text("VMR_PORT=5200\n")
    env = dict(os.environ)
    env["VMR_PORT"] = "6000"
    load_dotenv(files=(shared, local), env=env)
    assert env["VMR_PORT"] == "6000"


def test_settings_apply_overrides_coerces_and_ignores_unknown_keys():
    s = Settings()
    s.apply_overrides({"check_seconds": "45", "disk_min_free_gb": "2.5",
                       "notify_email_enabled": "yes", "not_a_setting": "x",
                       "backup_retention_count": "not a number"})
    assert s.check_seconds == 45
    assert s.disk_min_free_gb == 2.5
    assert s.notify_email_enabled is True
    assert not hasattr(s, "not_a_setting")
    assert s.backup_retention_count == 3      # unchanged, the bad value was dropped


# ------------------------------------------------------------------ settings
def test_runtime_overrides_are_stored_and_applied(conn, settings):
    services.set_override(conn, "check_seconds", "45", user_id=None, now=T0)
    assert services.get_override(conn, "check_seconds") == "45"
    services.apply_overrides(conn, settings)
    assert settings.check_seconds == 45


def test_reset_override_restores_the_environment_value(conn, settings):
    """Removing an override puts the setting back to the configured value.

    The whole point is that the running process and the database agree, so
    this has to set the override, apply it, remove it, and apply it again.
    """
    assert settings.check_seconds == 30      # the built-in default
    services.set_override(conn, "check_seconds", "45", now=T0)
    services.apply_overrides(conn, settings)
    assert settings.check_seconds == 45
    services.clear_override(conn, "check_seconds", now=T0)
    services.apply_overrides(conn, settings)
    assert settings.check_seconds == 30      # back to the configured value


def test_an_override_survives_a_later_application_of_the_others(conn, settings):
    """Applying the overrides again keeps the ones that are still set."""
    services.set_override(conn, "check_seconds", "45", now=T0)
    services.set_override(conn, "disk_min_free_gb", "2.5", now=T0)
    services.apply_overrides(conn, settings)
    assert settings.check_seconds == 45
    assert settings.disk_min_free_gb == 2.5
    # The same overrides applied a second time must not drift.
    services.apply_overrides(conn, settings)
    assert settings.check_seconds == 45
    assert settings.disk_min_free_gb == 2.5


def test_unknown_setting_is_rejected(conn):
    with pytest.raises(ValueError):
        services.set_override(conn, "no_such_setting", "1")
    with pytest.raises(ValueError):
        services.set_override(conn, "db_path", "/etc/passwd")     # read-only


# -------------------------------------------------------------- notifications
def test_alert_is_recorded_and_delivered_over_a_stub_channel(conn, settings, monkeypatch):
    from app import notifier
    sent = []

    def fake_send(settings_obj, recipient, subject, body):
        sent.append((recipient, subject))

    monkeypatch.setattr(notifier, "_send_email", fake_send)
    settings.notify_email_enabled = True
    settings.smtp_host = "smtp.test"
    settings.smtp_to = "admin@test, lab@test"
    notifier.configure(settings)

    services.set_runtime_settings(settings)
    services.notify(conn, "Subject line", "Body text", severity="critical", now=T0)

    assert len(sent) == 2
    rows = conn.execute("SELECT * FROM notifications").fetchall()
    assert len(rows) == 2
    assert all(r["status"] == "sent" for r in rows)
    assert all(r["severity"] == "critical" for r in rows)
    notifier.configure(Settings())


def test_notification_failure_is_recorded_not_raised(conn, settings, monkeypatch):
    from app import notifier

    def boom(settings_obj, recipient, subject, body):
        raise RuntimeError("smtp is down")

    monkeypatch.setattr(notifier, "_send_email", boom)
    settings.notify_email_enabled = True
    settings.smtp_host = "smtp.test"
    settings.smtp_to = "admin@test"
    notifier.configure(settings)
    services.set_runtime_settings(settings)

    services.notify(conn, "Subject", "Body", now=T0)   # must not raise

    row = conn.execute("SELECT * FROM notifications").fetchone()
    assert row["status"] == "failed"
    assert "smtp is down" in row["error"]
    notifier.configure(Settings())


def test_webhook_payload_is_signed(conn, settings, vbox):
    from app import notifier
    captured = {}
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["body"] = request.data
        captured["headers"] = request.headers
        return FakeResponse()

    import urllib.request
    original = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    try:
        settings.notify_webhook_enabled = True
        settings.webhook_url = "https://hooks.test/abc"
        settings.webhook_secret = "s3cret"
        notifier.configure(settings)
        results = notifier.send(conn, settings, "Subject", "Body", vm_id=vm_id, now=T0)
    finally:
        urllib.request.urlopen = original
        notifier.configure(Settings())

    assert results[0]["status"] == "sent"
    assert captured["url"] == "https://hooks.test/abc"
    # HTTP header names are case-insensitive, and urllib normalises the case.
    signature = next(v for k, v in captured["headers"].items()
                     if k.lower() == "x-vmrecovery-signature")
    assert signature.startswith("sha256=")
    row = conn.execute("SELECT * FROM notifications").fetchone()
    assert row["status"] == "sent"
    assert row["vm_id"] == vm_id


def test_no_channel_configured_is_recorded_as_skipped(conn, settings):
    from app import notifier
    notifier.configure(Settings())
    results = notifier.send(conn, settings, "Subject", "Body", now=T0)
    assert results == []
    row = conn.execute("SELECT * FROM notifications").fetchone()
    assert row["status"] == "skipped"


# -------------------------------------------------------------- power control
def test_power_actions_change_the_machine_state(conn, vbox, vm):
    assert services.power_action(conn, vbox, vm["vm_id"], "stop") is not None
    assert vbox.get_state(vm["vbox_uuid"]) == "poweroff"
    services.power_action(conn, vbox, vm["vm_id"], "start")
    assert vbox.get_state(vm["vbox_uuid"]) == "running"
    services.power_action(conn, vbox, vm["vbox_uuid"] and vm["vm_id"], "pause")
    assert vbox.get_state(vm["vbox_uuid"]) == "paused"
    services.power_action(conn, vbox, vm["vm_id"], "resume")
    assert vbox.get_state(vm["vbox_uuid"]) == "running"


def test_a_paused_machine_is_treated_as_frozen_for_auto_recovery(conn, vbox, vm, settings):
    services.power_action(conn, vbox, vm["vm_id"], "pause")
    fresh = services.get_vm(conn, vm["vm_id"])
    assert services.observe(vbox, fresh, T0, settings) == "frozen"
    assert fresh["fail_count"] == 1


def test_power_action_records_an_event(conn, vbox, vm, users):
    admin_id, _ = users
    services.power_action(conn, vbox, vm["vm_id"], "stop", user_id=admin_id)
    events = services.list_events(conn, vm_id=vm["vm_id"], event_type="vm_stop")
    assert len(events) == 1
    assert events[0]["user_id"] == admin_id


def test_bulk_action_reports_success_and_failure(conn, vbox, vm):
    summary = services.bulk_power_action(conn, vbox, [vm["vm_id"], 9999], "stop")
    assert len(summary["done"]) == 1
    assert len(summary["failed"]) == 1


# ----------------------------------------------------------------- removal
def test_remove_vm_can_delete_the_machine_from_virtualbox(conn, vbox, vm):
    services.remove_vm(conn, vm["vm_id"], vbox=vbox, delete_from_vbox=True)
    assert services.get_vm(conn, vm["vm_id"]) is None
    with pytest.raises(Exception):
        vbox.get_state(vm["vbox_uuid"])


def test_remove_vm_leaves_the_machine_alone_by_default(conn, vbox, vm):
    services.remove_vm(conn, vm["vm_id"], vbox=vbox)
    assert vbox.get_state(vm["vbox_uuid"]) == "running"


# --------------------------------------------------------------------- API
@pytest.fixture
def api_client(settings, vbox):
    settings.api_token = "test-token"
    app = create_app(settings, vbox)
    return app.test_client()


def test_api_is_disabled_without_a_token(settings, vbox):
    settings.api_token = ""
    app = create_app(settings, vbox)
    r = app.test_client().get("/api/vms")
    assert r.status_code == 503
    assert "disabled" in r.get_json()["error"]


def test_api_rejects_a_missing_or_wrong_token(api_client):
    assert api_client.get("/api/vms").status_code == 401
    assert api_client.get("/api/vms", headers={"X-API-Token": "nope"}).status_code == 401


def test_api_accepts_the_token_in_either_header(api_client, settings, vbox):
    conn = db.connect(settings.db_path)
    services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()
    r = api_client.get("/api/vms", headers={"Authorization": "Bearer test-token"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["vms"][0]["name"] == "DEV-LAB-01"

    r = api_client.get("/api/vms", headers={"X-API-Token": "test-token"})
    assert r.status_code == 200


def test_api_health_is_public(api_client):
    r = api_client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_api_returns_the_event_log(api_client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    services.log_event(conn, "vm_registered", vm_id, None, "hello", "Success", T0)
    conn.close()
    r = api_client.get("/api/events", headers={"Authorization": "Bearer test-token"})
    assert r.status_code == 200
    assert r.get_json()["total"] >= 1


# ------------------------------------------------------------------- web
def token(client):
    page = client.get("/login").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)


def login(client, user="admin", pw="password123"):
    return client.post("/login", data={"username": user, "password": pw, "csrf_token": token(client)})


def csrf(client, url="/"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def test_students_only_see_events_for_their_own_machines(client, settings, vbox):
    conn = db.connect(settings.db_path)
    stu = services.create_user(conn, "jane", "password123", "student")
    mine = services.register_vm(conn, "MINE", "uuid-1", "Class A", 30, 3, now=T0)
    other = services.register_vm(conn, "OTHER", "uuid-3", "Class B", 30, 3, now=T0)
    services.assign_student(conn, mine, stu)
    services.log_event(conn, "vm_registered", other, None, "not for jane", "Success", T0)
    conn.close()

    login(client, "jane")
    r = client.get("/events")
    assert r.status_code == 200
    assert b"not for jane" not in r.data


def test_event_log_is_paginated(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    for i in range(25):
        services.log_event(conn, "vm_registered", vm_id, None, f"event {i}", "Success", T0)
    conn.close()

    login(client)
    r = client.get("/events?per_page=10&page=2")
    assert r.status_code == 200
    assert b"page 2 of" in r.data


def test_events_can_be_downloaded_as_csv(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    services.log_event(conn, "vm_registered", vm_id, None, "csv row", "Success", T0)
    conn.close()

    login(client)
    r = client.get("/events.csv")
    assert r.status_code == 200
    assert r.mimetype == "text/csv"
    assert b"csv row" in r.data


def test_admin_can_change_a_setting_from_the_web(client, settings):
    login(client)
    t = csrf(client, "/settings")
    r = client.post("/settings", data={"csrf_token": t, "key": "check_seconds", "value": "45"})
    assert r.status_code == 302
    conn = db.connect(settings.db_path)
    assert services.get_override(conn, "check_seconds") == "45"
    conn.close()


def test_trainer_cannot_open_the_settings_page(client):
    login(client, "trainer")
    assert client.get("/settings").status_code == 403


def test_any_user_can_change_their_own_password(client, settings):
    conn = db.connect(settings.db_path)
    services.create_user(conn, "carol", "password123", "trainer")
    conn.close()
    login(client, "carol")
    t = csrf(client, "/account")
    r = client.post("/account", data={"csrf_token": t, "current_password": "password123",
                                      "new_password": "newpassword456"})
    assert r.status_code == 302
    conn = db.connect(settings.db_path)
    from werkzeug.security import check_password_hash
    row = conn.execute("SELECT * FROM users WHERE username='carol'").fetchone()
    assert check_password_hash(row["password_hash"], "newpassword456")
    conn.close()


# ------------------------------------------------------------- database
def test_schema_is_versioned_and_migrations_are_idempotent(tmp_path):
    path = str(tmp_path / "m.db")
    version = db.init_db(path)
    assert version >= 7
    conn = db.connect(path)
    assert conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0]
    conn.close()
    assert db.init_db(path) == version       # running it again changes nothing


def test_an_old_database_is_upgraded_in_place(tmp_path):
    """A database from an older version gains the new columns and tables."""
    import sqlite3
    path = str(tmp_path / "old.db")
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password_hash TEXT NOT NULL,
                            role TEXT NOT NULL CHECK (role IN ('admin','trainer')));
        CREATE TABLE vms (vm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          policy_id INTEGER NOT NULL, vm_name TEXT NOT NULL,
                          vbox_uuid TEXT NOT NULL UNIQUE);
        INSERT INTO users (username, password_hash, role) VALUES ('old', 'x', 'admin');
    """)
    conn.commit()
    conn.close()

    db.init_db(path)
    conn = db.connect(path)
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(vms)")]
    assert "is_template" in columns
    assert "assigned_student_id" in columns
    assert "admin_paused" in columns
    assert conn.execute("SELECT COUNT(*) FROM app_settings").fetchone()[0] == 0
    assert conn.execute("SELECT role FROM users WHERE username='old'").fetchone()[0] == "admin"
    conn.close()


def test_database_backup_and_restore(tmp_path, conn):
    path = str(tmp_path / "b.db")
    db.init_db(path)
    conn2 = db.connect(path)
    conn2.execute("INSERT INTO users (username, password_hash, role) VALUES ('u1','x','admin')")
    conn2.commit()

    backup = db.backup_database(path, str(tmp_path / "backups"), keep=3)
    assert os.path.exists(backup)

    conn2.execute("DELETE FROM users")
    conn2.commit()
    assert conn2.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
    conn2.close()

    db.restore_database(path, backup)
    conn3 = db.connect(path)
    assert conn3.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    conn3.close()


def test_only_the_last_few_database_backups_are_kept(tmp_path):
    path = str(tmp_path / "r.db")
    db.init_db(path)
    out = tmp_path / "backups"
    for _ in range(4):
        db.backup_database(path, str(out), keep=2)
    assert len(list(out.glob("vmrecovery-*.db"))) == 2
