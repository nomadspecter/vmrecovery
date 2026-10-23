"""The failure modes that made every dashboard action fail at once.

A live snapshot of a running guest that does not support them never returns.
The command held the VirtualBox lock for half an hour, the background worker
stopped with it, and every other button queued behind the same lock. These
tests pin the behaviour that prevents that from happening again.
"""
import re
import threading
import time

import pytest

from app import db, services
from app.vbox import SimulatedVBox, VBoxError
from tests.conftest import T0


def token(client):
    page = client.get("/login").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)


def login(client, user="admin", pw="password123"):
    return client.post("/login", data={"username": user, "password": pw, "csrf_token": token(client)})


def csrf(client):
    html = client.get("/").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


# ------------------------------------------------------------------ the state words
def test_a_machine_in_a_live_snapshot_is_busy_not_powered_off(conn, vbox, vm, settings):
    """VirtualBox 7.2 reports 'onlinesnapshotting' during a live snapshot.

    The state was missing from the busy list, so a machine that was stuck
    mid-snapshot was reported as "powered off" and the recovery then tried to
    act on a machine VirtualBox had locked.
    """
    vbox.vms["uuid-1"]["state"] = "onlinesnapshotting"
    health = services.observe(vbox, vm, T0, settings)
    assert health == "busy"


@pytest.mark.parametrize("state", ["onlinesnapshotting", "onlinsnapshotting", "livesnapshotting",
                                    "probing", "settingup", "teleporting"])
def test_every_transitional_state_counts_as_busy(state):
    from app.vbox import state_is_busy
    assert state_is_busy(state)


def test_an_unfamiliar_state_is_unknown_not_powered_off(conn, vbox, vm, settings):
    """A state word this code has never seen is not proof that the machine is off."""
    vbox.vms["uuid-1"]["state"] = "quantum"
    health = services.observe(vbox, vm, T0, settings)
    assert health == "unknown"


def test_a_machine_stuck_in_a_busy_state_is_reported_as_such(conn, vbox, vm, settings):
    """A machine that stays busy is a machine nobody can act on, and that has
    to be visible rather than silently 'powered off'."""
    vbox.vms["uuid-1"]["state"] = "onlinesnapshotting"
    services.monitor_vm(conn, vbox, vm, settings, T0)          # it becomes busy here
    later = T0.replace(hour=9, minute=30)                      # and stays that way
    outcome = services.monitor_vm(conn, vbox, services.get_vm(conn, vm["vm_id"]), settings, later)
    assert outcome == "needs_admin"
    alerts = conn.execute("SELECT * FROM events WHERE event_type='alert'").fetchall()
    assert alerts and "stuck" in alerts[0]["details"]


def test_a_busy_machine_still_refreshes_its_row(conn, vbox, vm, settings):
    """A stale last_checked is how a dead worker looks like a live one."""
    vbox.vms["uuid-1"]["state"] = "onlinesnapshotting"
    later = T0.replace(hour=9, minute=30)
    services.monitor_vm(conn, vbox, vm, settings, later)
    row = services.get_vm(conn, vm["vm_id"])
    assert row["status"] == "busy"
    assert row["last_checked"] == services.ts(later)
    assert row["status_since"] == services.ts(later)


# ------------------------------------------------------------------ live snapshots
def test_a_running_machine_is_not_snapshotted_live(conn, vbox, vm, settings, monkeypatch):
    """--live asks the guest to write its memory out, and a guest that does not
    answer never lets the command return. It is opt-in, not the default."""
    services.set_runtime_settings(settings)
    seen = {}
    original = vbox.take_snapshot

    def spy(name, snap_name, live=False, description=""):
        seen["live"] = live
        return original(name, snap_name, live=live, description=description)

    vbox.take_snapshot = spy
    services.take_snapshot(conn, vbox, vm, "manual", now=T0)
    assert seen["live"] is False


def test_live_snapshots_can_be_turned_on_explicitly(conn, vbox, vm, settings):
    settings.live_snapshots = True
    services.set_runtime_settings(settings)
    seen = {}
    original = vbox.take_snapshot

    def spy(name, snap_name, live=False, description=""):
        seen["live"] = live
        return original(name, snap_name, live=live, description=description)

    vbox.take_snapshot = spy
    services.take_snapshot(conn, vbox, vm, "manual", now=T0)
    assert seen["live"] is True


# ------------------------------------------------------------------ the lock
def test_a_web_action_does_not_wait_for_the_lock_forever(client, conn, settings):
    """One slow VirtualBox command must not freeze every page of the dashboard."""
    settings.vbox_lock_timeout = 1
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    login(client)
    held = threading.Lock()
    held.acquire()
    try:
        client.application.extensions["lock"] = held
        started = time.monotonic()
        r = client.post(f"/vms/{vm_id}/snapshot", data={"csrf_token": csrf(client)})
        assert time.monotonic() - started < 10
        assert r.status_code == 302
        page = client.get("/").get_data(as_text=True)
        assert "Another VirtualBox operation is still running" in page
    finally:
        held.release()


def test_the_worker_skips_a_machine_rather_than_stopping(conn, vbox, vm, settings):
    """The worker used to block on the lock with no word, and monitoring simply
    stopped without anybody noticing."""
    settings.vbox_lock_timeout = 1
    held = threading.Lock()
    held.acquire()
    try:
        summary = services.run_cycle(conn, vbox, settings, now=T0, lock=held)
    finally:
        held.release()
    assert summary["checked"] == 0       # it skipped, it did not hang


# ------------------------------------------------------------------ the restore page
def test_a_restore_without_a_snapshot_says_so_instead_of_404(client, conn, vbox, settings):
    login(client)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    r = client.post(f"/vms/{vm_id}/restore", data={"csrf_token": csrf(client)})
    assert r.status_code == 302
    page = client.get("/vms/%d" % vm_id).get_data(as_text=True)
    assert "Choose one of this machine" in page


def test_a_restore_of_a_snapshot_of_another_machine_is_refused(client, conn, vbox, settings):
    login(client)
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    other = services.register_vm(conn, "NET-LAB-03", "uuid-3", "Class A", 30, 3, now=T0)
    snap_id = services.take_snapshot(conn, vbox, services.get_vm(conn, other), "manual", now=T0)
    row = conn.execute("SELECT snapshot_id FROM snapshots WHERE snapshot_name=?", (snap_id,)).fetchone()
    r = client.post(f"/vms/{vm_id}/restore",
                    data={"csrf_token": csrf(client), "snapshot_id": row["snapshot_id"]})
    assert r.status_code == 302
    page = client.get(f"/vms/{vm_id}").get_data(as_text=True)
    assert "Choose one of this machine" in page


# ------------------------------------------------------------------ the log
def test_a_failed_action_is_written_to_the_log(client, caplog):
    """A failed action used to leave no trace at all, so the log was empty
    while the dashboard kept saying it could not do the thing."""
    import logging
    with caplog.at_level(logging.WARNING, logger="vmrecovery"):
        login(client, pw="wrong")
    assert any("Action failed" in r.getMessage() for r in caplog.records)


# ------------------------------------------------------------------ cloning
def test_the_template_is_suspended_and_settled_before_it_is_cloned(vbox):
    """Cloning a running machine is refused by VirtualBox, and saving its
    state and then cloning it straight away is refused too, because
    VirtualBox has not finished tearing the running process down.

    The state has to be reached AND settle before the clone is issued, and
    the template has to be started again afterwards, exactly as it was.
    """
    order = []
    original = {name: getattr(vbox, name) for name in
                ("save_state", "discard_state", "start_vm", "clone_vm", "wait_for_state")}

    def track(name, fn):
        def wrapper(*args, **kwargs):
            order.append(name)
            return fn(*args, **kwargs)
        return wrapper

    for name, fn in original.items():
        setattr(vbox, name, track(name, fn))

    services._clone_from_template(vbox, "uuid-1", "LAB-CS-002", linked=False, snapshot=None)

    assert order == ["save_state", "wait_for_state", "clone_vm", "wait_for_state",
                     "discard_state", "wait_for_state",
                     "discard_state", "wait_for_state", "start_vm"]
    assert vbox.get_state("uuid-1") == "running"
    assert vbox.get_state("LAB-CS-002") == "poweroff"


def test_a_clone_of_a_suspended_template_is_left_powered_off(vbox):
    """A clone of a suspended machine inherits its saved state, and a machine
    that is still suspended cannot be started cleanly. The saved state is
    thrown away, and the template is left exactly as it was found."""
    vbox.vms["uuid-1"]["state"] = "saved"
    services._clone_from_template(vbox, "uuid-1", "LAB-CS-002", linked=False, snapshot=None)
    assert vbox.get_state("LAB-CS-002") == "poweroff"
    assert vbox.get_state("uuid-1") == "saved"


def test_a_machine_that_is_already_saved_is_cloned_without_being_touched(vbox):
    """A template that is already suspended is clonable as it is, and it is
    left suspended — the system does not start machines nobody asked it to."""
    vbox.vms["uuid-1"]["state"] = "saved"
    services._clone_from_template(vbox, "uuid-1", "LAB-CS-003", linked=False, snapshot=None)
    assert vbox.get_state("uuid-1") == "saved"


def test_a_template_in_a_state_that_cannot_be_cloned_says_so(vbox):
    """A template that is mid-snapshot is not clonable, and the reason has to
    reach the user instead of a bare VirtualBox error."""
    vbox.vms["uuid-1"]["state"] = "onlinesnapshotting"
    with pytest.raises(ValueError, match="onlinesnapshotting"):
        services._clone_from_template(vbox, "uuid-1", "LAB-CS-004", linked=False, snapshot=None)


def test_a_failed_clone_is_cleared_away_and_tried_again(vbox):
    """A failed clone leaves its disk in VirtualBox's media registry, and the
    next attempt then fails for that reason alone — "Clone VM failed", with
    nothing else to show for it. The name was unusable until the registry was
    cleaned by hand, so the clone is cleared away and tried once more."""
    calls = []
    original = vbox.clone_vm

    def flaky(source, name, **kwargs):
        calls.append(name)
        if len(calls) == 1:
            raise VBoxError("VBoxManage: error: Clone VM failed")
        return original(source, name, **kwargs)

    vbox.clone_vm = flaky
    name, uuid = services._clone_from_template(vbox, "uuid-1", "LAB-CS-009",
                                                linked=False, snapshot=None)
    assert calls == ["LAB-CS-009", "LAB-CS-009"]
    assert name == "LAB-CS-009"


def test_a_clone_that_fails_twice_reports_the_failure(vbox):
    """The retry is a retry, not an endless loop."""
    original = vbox.clone_vm
    calls = []

    def always_fails(source, name, **kwargs):
        calls.append(name)
        raise VBoxError("VBoxManage: error: Clone VM failed")

    vbox.clone_vm = always_fails
    with pytest.raises(VBoxError, match="Clone VM failed"):
        services._clone_from_template(vbox, "uuid-1", "LAB-CS-009",
                                      linked=False, snapshot=None)
    assert len(calls) == 2


def test_the_cleanup_leaves_a_machine_of_ours_alone(conn, vbox):
    """The cleanup removes what a failed clone left behind. It must never
    touch a machine that belongs to the system."""
    services.register_vm(conn, "NET-LAB-03", "uuid-3", "Class A", 30, 3, now=T0)
    services.purge_clone_leftovers(vbox, "NET-LAB-03", conn=conn)
    assert vbox.get_state("uuid-3") == "running"
    assert "NET-LAB-03" in [name for name, _ in vbox.list_vms()]
