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


def test_health_endpoint_is_public_and_reports_database(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


def test_security_headers_are_set(client):
    r = client.get("/login")
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["Cache-Control"] == "no-store"


def test_admin_can_open_system_health_page(client):
    login(client)
    r = client.get("/system")
    assert r.status_code == 200
    assert b"System Health" in r.data
    assert b"Background recovery service" in r.data


def test_trainer_cannot_open_system_health_page(client):
    login(client, "trainer")
    assert client.get("/system").status_code == 403


def test_start_session_button_starts_powered_off_vms(client, settings, vbox):
    conn = db.connect(settings.db_path)
    services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()
    vbox.vms["uuid-1"]["state"] = "poweroff"

    login(client)
    t = csrf(client)
    r = client.post("/sessions/start", data={"csrf_token": t, "class_group": "Class A"})

    assert r.status_code == 302
    assert vbox.get_state("uuid-1") == "running"
    assert b"1 VM(s) started" in client.get("/").data


def test_second_start_session_click_does_not_take_another_snapshot(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()

    login(client)
    t = csrf(client)
    client.post("/sessions/start", data={"csrf_token": t, "class_group": "Class A"})
    vbox.vms["uuid-1"]["state"] = "poweroff"
    client.post("/sessions/start", data={"csrf_token": t, "class_group": "Class A"})

    page = client.get("/").data
    assert b"already active" in page
    assert b"Active training sessions" in page
    assert vbox.get_state("uuid-1") == "running"

    conn = db.connect(settings.db_path)
    assert conn.execute("SELECT COUNT(*) FROM snapshots WHERE vm_id=?", (vm_id,)).fetchone()[0] == 1
    conn.close()


def test_end_session_button_powers_off_and_closes_the_session(client, settings, vbox):
    conn = db.connect(settings.db_path)
    services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    conn.close()

    login(client)
    t = csrf(client)
    client.post("/sessions/start", data={"csrf_token": t, "class_group": "Class A"})
    r = client.post("/sessions/end", data={"csrf_token": t, "class_group": "Class A",
                                           "power_off": "on"})

    assert r.status_code == 302
    assert vbox.get_state("uuid-1") == "poweroff"
    page = client.get("/").data
    assert b"Session ended for Class A" in page
    assert b"Active training sessions" not in page

    conn = db.connect(settings.db_path)
    assert services.active_session(conn, "Class A") is None
    conn.close()


def test_student_vm_request_and_auto_assignment(client, settings, vbox):
    conn = db.connect(settings.db_path)
    student_id = services.create_user(conn, "student1", "Student1234!", "student")
    tpl_id = services.register_vm(conn, "TPL-BASE", "uuid-1", "CS", 30, 5, is_template=True, now=T0)
    services.take_snapshot(conn, vbox, services.get_vm(conn, tpl_id), "template", T0)
    conn.close()

    login(client, "student1", "Student1234!")
    page = client.get("/requests")
    assert page.status_code == 200
    assert b"Request a new virtual machine" in page.data

    t = csrf(client)
    r = client.post("/requests/new", data={
        "csrf_token": t,
        "template_choice": "uuid-1|TPL-BASE",
        "requested_name": "STU-VM-01",
        "class_group": "CS",
        "clone_type": "linked",
    })
    assert r.status_code == 302
    assert b"STU-VM-01" in client.get("/requests").data

    # Admin approves request -> VM should be auto-assigned to student1
    client.post("/logout", data={"csrf_token": t})
    login(client, "admin")
    t_admin = csrf(client)
    conn = db.connect(settings.db_path)
    req_id = conn.execute("SELECT request_id FROM vm_requests WHERE requested_name='STU-VM-01'").fetchone()[0]
    conn.close()
    assert client.post(f"/requests/{req_id}/approve", data={"csrf_token": t_admin}).status_code == 302

    conn = db.connect(settings.db_path)
    vm = conn.execute("SELECT * FROM vms WHERE vm_name='STU-VM-01'").fetchone()
    assert vm is not None
    assert vm["assigned_student_id"] == student_id
    conn.close()

    # Student sees View on Dashboard (not 403 Manage VM) and sees the VM on dashboard
    client.post("/logout", data={"csrf_token": t_admin})
    login(client, "student1", "Student1234!")
    req_page = client.get("/requests")
    assert req_page.status_code == 200
    assert b"View on Dashboard" in req_page.data
    assert b"Manage VM" not in req_page.data
    assert b"STU-VM-01" in client.get("/").data


def test_snapshots_page_and_delete_snapshot_route(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 5, now=T0)
    services.take_snapshot(conn, vbox, services.get_vm(conn, vm_id), "manual", T0)
    snap_id = services.list_snapshots(conn, vm_id)[0]["snapshot_id"]
    conn.close()

    login(client)
    r = client.get(f"/vms/{vm_id}/snapshots")
    assert r.status_code == 200
    t = csrf(client)
    d = client.post(f"/vms/{vm_id}/snapshots/{snap_id}/delete", data={"csrf_token": t})
    assert d.status_code == 302
    conn = db.connect(settings.db_path)
    assert services.list_snapshots(conn, vm_id) == []
    conn.close()


def test_demo_crash_and_freeze_auto_recover_in_next_cycle(client, settings, vbox):
    conn = db.connect(settings.db_path)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 5, now=T0)
    services.take_snapshot(conn, vbox, services.get_vm(conn, vm_id), "baseline", T0)
    conn.close()

    login(client)
    t = csrf(client)

    for action in ("crash", "freeze"):
        r = client.post(f"/demo/{action}/{vm_id}", data={"csrf_token": t})
        assert r.status_code == 302
        expected_vbox_state = "aborted" if action == "crash" else "paused"
        assert vbox.get_state("uuid-1") == expected_vbox_state

        conn = db.connect(settings.db_path)
        summary = services.run_cycle(conn, vbox, settings, now=T0)
        vm = services.get_vm(conn, vm_id)
        conn.close()
        assert summary["recoveries"] == 1
        assert vbox.get_state("uuid-1") == "running"
        assert vm["status"] == "running"
        assert vm["fail_count"] == 0


def test_dashboard_has_no_nested_forms(client, settings):
    from html.parser import HTMLParser
    conn = db.connect(settings.db_path)
    services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 5, now=T0)
    conn.close()
    login(client)
    html = client.get("/").data.decode("utf-8")

    class _Checker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.depth = 0
            self.nested = 0
        def handle_starttag(self, tag, attrs):
            if tag == "form":
                self.depth += 1
                if self.depth > 1:
                    self.nested += 1
        def handle_endtag(self, tag):
            if tag == "form":
                self.depth = max(0, self.depth - 1)

    c = _Checker()
    c.feed(html)
    assert c.nested == 0
