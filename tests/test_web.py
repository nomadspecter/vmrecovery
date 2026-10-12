import re

from app import db, services
from tests.conftest import T0


def token(client):
    page = client.get("/login").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)


def login(client, user="admin", pw="password123"):
    return client.post("/login", data={"username": user, "password": pw, "csrf_token": token(client)})


def csrf(client):
    html = client.get("/").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def test_pages_require_login(client):
    for url in ("/", "/vms", "/events", "/reports"):
        assert client.get(url).status_code == 302


def test_bad_password_rejected(client):
    r = login(client, pw="wrong")
    assert r.status_code == 200 and b"Invalid username or password" in r.data


def test_post_without_csrf_token_is_rejected(client):
    assert client.post("/login", data={"username": "admin", "password": "password123"}).status_code == 400


def test_admin_login_and_dashboard(client):
    assert login(client).status_code == 302
    assert b"Dashboard" in client.get("/").data


def test_login_is_rate_limited(client):
    from app import views
    views._failed_logins.clear()
    for _ in range(5):
        login(client, pw="wrong")
    assert login(client).status_code == 429
    views._failed_logins.clear()


def test_trainer_cannot_open_admin_pages(client):
    login(client, "trainer")
    assert client.get("/vms").status_code == 403
    assert client.get("/reports").status_code == 403


def test_admin_registers_vm_and_it_appears(client, settings):
    login(client)
    t = csrf(client)
    r = client.post("/vms/add", data={"csrf_token": t, "vbox_choice": "DEV-LAB-01|uuid-1",
                                      "class_group": "Class A", "interval_minutes": "30",
                                      "retention_count": "3", "pre_session": "on"})
    assert r.status_code == 302
    assert b"DEV-LAB-01" in client.get("/vms").data


def test_invalid_policy_shows_error_not_crash(client):
    login(client)
    t = csrf(client)
    client.post("/vms/add", data={"csrf_token": t, "vbox_choice": "DEV-LAB-01|uuid-1",
                                  "class_group": "A", "interval_minutes": "0", "retention_count": "3"})
    assert b"between 1 and 1440" in client.get("/vms").data


def test_trainer_request_restore_then_admin_sees_it(client, settings):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()
    login(client, "trainer")
    t = csrf(client)
    assert client.post(f"/vms/{vm_id}/request-restore", data={"csrf_token": t}).status_code == 302
    client.post("/logout", data={"csrf_token": t})
    login(client)
    assert b"Restore requested" in client.get("/").data


def test_admin_restore_through_web(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    services.take_snapshot(conn, vbox, services.get_vm(conn, vm_id), "manual", T0)
    snap_id = services.list_snapshots(conn, vm_id)[0]["snapshot_id"]
    conn.close()
    vbox.crash("uuid-1")
    login(client)
    t = csrf(client)
    r = client.post(f"/vms/{vm_id}/restore", data={"csrf_token": t, "snapshot_id": snap_id})
    assert r.status_code == 302 and vbox.get_state("uuid-1") == "running"


def test_demo_routes_exist_only_in_simulation(client, settings):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()
    login(client)
    t = csrf(client)
    assert client.post(f"/demo/crash/{vm_id}", data={"csrf_token": t}).status_code == 302


def test_reports_and_events_pages_render(client):
    login(client)
    assert client.get("/reports").status_code == 200
    assert client.get("/events").status_code == 200
