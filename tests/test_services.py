from datetime import timedelta

import pytest

from app import services
from app.vbox import SimulatedVBox
from tests.conftest import T0


def minutes(n):
    return T0 + timedelta(minutes=n)


# ------------------------------------------------------------ registry
def test_register_rejects_duplicates_and_bad_policy(conn, vm):
    with pytest.raises(ValueError):
        services.register_vm(conn, "again", "uuid-1", "A", 30, 3)
    with pytest.raises(ValueError):
        services.register_vm(conn, "x", "uuid-9", "A", 0, 3)
    with pytest.raises(ValueError):
        services.register_vm(conn, "", "", "A", 30, 3)


def test_identical_policies_are_shared(conn, vbox, vm):
    vbox.add_vm("B", "uuid-b")
    services.register_vm(conn, "B", "uuid-b", "A", 30, 3)
    assert conn.execute("SELECT COUNT(*) FROM snapshot_policies").fetchone()[0] == 1


# ------------------------------------------------------------ snapshots
def test_cycle_takes_first_snapshot_then_waits_for_interval(conn, vbox, vm, settings):
    assert services.run_cycle(conn, vbox, settings, T0)["snapshots"] == 1
    assert services.run_cycle(conn, vbox, settings, minutes(10))["snapshots"] == 0
    assert services.run_cycle(conn, vbox, settings, minutes(31))["snapshots"] == 1
    assert len(vbox.list_snapshots("uuid-1")) == 2


def test_retention_deletes_oldest(conn, vbox, vm, settings):
    for i in range(5):
        services.run_cycle(conn, vbox, settings, minutes(31 * i))
    names = vbox.list_snapshots("uuid-1")
    assert len(names) == 3
    assert [s["snapshot_name"] for s in services.list_snapshots(conn, vm["vm_id"])][::-1] == names


def test_failed_snapshot_is_logged_and_not_recorded(conn, vbox, vm, settings):
    vbox.fail_next.add("take_snapshot")
    assert services.run_cycle(conn, vbox, settings, T0)["snapshots"] == 0
    assert services.list_snapshots(conn, vm["vm_id"]) == []
    assert services.list_events(conn, event_type="snapshot_failed")


def test_powered_off_vm_gets_one_baseline_snapshot_only(conn, vbox, vm, settings):
    vbox.vms["uuid-1"]["state"] = "poweroff"
    services.run_cycle(conn, vbox, settings, T0)
    services.run_cycle(conn, vbox, settings, minutes(60))
    assert len(vbox.list_snapshots("uuid-1")) == 1


def test_start_session_starts_off_vms_and_snapshots_the_group(conn, vbox, vm):
    vbox.add_vm("OFF", "uuid-off", "poweroff")
    services.register_vm(conn, "OFF", "uuid-off", "Class A", 30, 3)
    vbox.add_vm("OTHER", "uuid-other", "poweroff")
    services.register_vm(conn, "OTHER", "uuid-other", "Class B", 30, 3)

    result = services.start_session(conn, vbox, "Class A", None, T0)

    assert result["started"] == 1 and result["already_running"] == 1
    assert result["snapshots"] == 2 and result["skipped"] == 0 and result["failed"] == []
    assert vbox.get_state("uuid-off") == "running"
    assert vbox.get_state("uuid-other") == "poweroff"          # another group is untouched
    assert vbox.list_snapshots("uuid-off")[0].startswith("pre-session-")
    assert vbox.list_snapshots("uuid-1")[0].startswith("pre-session-")


def test_start_session_resumes_a_paused_vm(conn, vbox, vm):
    vbox.freeze("uuid-1")
    result = services.start_session(conn, vbox, "Class A", None, T0)
    assert result["started"] == 1 and result["already_running"] == 0
    assert vbox.get_state("uuid-1") == "running"


def test_start_session_starts_vms_even_without_a_pre_session_snapshot(conn, vbox, vm):
    services.update_vm(conn, vm["vm_id"], "Class A", 30, 3, False)
    vbox.vms["uuid-1"]["state"] = "poweroff"

    result = services.start_session(conn, vbox, "Class A", None, T0)

    assert result["started"] == 1 and result["snapshots"] == 0 and result["skipped"] == 1
    assert vbox.get_state("uuid-1") == "running"
    assert vbox.list_snapshots("uuid-1") == []


def test_start_session_reports_a_vm_that_will_not_start(conn, vbox, vm):
    vbox.vms["uuid-1"]["state"] = "poweroff"
    vbox.fail_next.add("start_vm")

    result = services.start_session(conn, vbox, "Class A", None, T0)

    assert result["started"] == 0
    assert result["failed"] and result["failed"][0][0] == "DEV-LAB-01"
    assert services.list_events(conn, event_type="session_vm_failed")


def test_pressing_start_again_does_not_take_another_snapshot(conn, vbox, vm):
    first = services.start_session(conn, vbox, "Class A", None, T0)
    assert first["already_active"] is False
    assert first["snapshots"] == 1
    session_id = first["session_id"]

    vbox.vms["uuid-1"]["state"] = "poweroff"                  # a VM dropped out of the class
    second = services.start_session(conn, vbox, "Class A", None, minutes(5))

    assert second["already_active"] is True
    assert second["session_id"] == session_id
    assert second["started"] == 1 and second["already_running"] == 0
    assert second["snapshots"] == 0 and second["already_protected"] == 1
    assert vbox.get_state("uuid-1") == "running"
    assert len(services.list_snapshots(conn, vm["vm_id"])) == 1
    assert [e["event_type"] for e in services.list_events(conn)][0] == "session_already_active"


def test_repeating_start_protects_a_vm_added_after_the_session_opened(conn, vbox, vm):
    services.start_session(conn, vbox, "Class A", None, T0)
    vbox.add_vm("LATE-LAB", "uuid-late", "running")
    late_id = services.register_vm(conn, "LATE-LAB", "uuid-late", "Class A", 30, 3, now=minutes(1))

    result = services.start_session(conn, vbox, "Class A", None, minutes(2))

    assert result["already_active"] is True
    assert result["snapshots"] == 1 and result["already_protected"] == 1
    assert len(services.list_snapshots(conn, late_id)) == 1
    assert len(services.list_snapshots(conn, vm["vm_id"])) == 1


def test_end_session_snapshots_powers_off_and_closes_the_session(conn, vbox, vm):
    services.start_session(conn, vbox, "Class A", None, T0)

    result = services.end_session(conn, vbox, "Class A", None, minutes(60))

    assert result["snapshots"] == 1 and result["powered_off"] == 1
    assert vbox.get_state("uuid-1") == "poweroff"
    assert services.active_session(conn, "Class A") is None
    names = [s["snapshot_name"] for s in services.list_snapshots(conn, vm["vm_id"])]
    assert names[0].startswith("post-session-")

    with pytest.raises(ValueError):
        services.end_session(conn, vbox, "Class A", None, minutes(61))

    again = services.start_session(conn, vbox, "Class A", None, minutes(62))
    assert again["already_active"] is False and again["started"] == 1
    assert again["snapshots"] == 1


def test_end_session_can_leave_vms_running(conn, vbox, vm):
    services.start_session(conn, vbox, "Class A", None, T0)
    result = services.end_session(conn, vbox, "Class A", None, minutes(30), power_off=False)

    assert result["snapshots"] == 1 and result["powered_off"] == 0
    assert vbox.get_state("uuid-1") == "running"
    assert services.active_session(conn, "Class A") is None


def test_end_session_still_closes_when_a_snapshot_fails(conn, vbox, vm):
    services.start_session(conn, vbox, "Class A", None, T0)
    vbox.fail_next.add("take_snapshot")

    result = services.end_session(conn, vbox, "Class A", None, minutes(30))

    assert result["failed"] and result["failed"][0][0] == "DEV-LAB-01"
    assert result["snapshots"] == 0 and result["powered_off"] == 1
    assert vbox.get_state("uuid-1") == "poweroff"
    assert services.active_session(conn, "Class A") is None


def test_session_actions_reject_unknown_or_empty_groups(conn, vbox):
    with pytest.raises(ValueError):
        services.start_session(conn, vbox, "", None, T0)
    with pytest.raises(ValueError):
        services.start_session(conn, vbox, "Missing", None, T0)
    with pytest.raises(ValueError):
        services.end_session(conn, vbox, "Class A", None, T0)


# ------------------------------------------------------------ crash recovery
def prepare_with_snapshot(conn, vbox, settings):
    services.run_cycle(conn, vbox, settings, T0)          # takes snapshot while healthy


def test_crash_is_debounced_then_restored(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.crash("uuid-1")
    first = services.run_cycle(conn, vbox, settings, minutes(1))
    assert first["suspect"] == 1 and vbox.get_state("uuid-1") == "aborted"   # not restored yet
    second = services.run_cycle(conn, vbox, settings, minutes(2))
    assert second["recoveries"] == 1 and vbox.get_state("uuid-1") == "running"
    types = [e["event_type"] for e in services.list_events(conn)]
    assert "crash_detected" in types and "restore_success" in types
    assert services.get_vm(conn, vm["vm_id"])["status"] == "running"


def test_frozen_vm_is_powered_off_restored_and_restarted(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.freeze("uuid-1")
    services.run_cycle(conn, vbox, settings, minutes(1))
    services.run_cycle(conn, vbox, settings, minutes(2))
    assert vbox.get_state("uuid-1") == "running"
    assert services.list_events(conn, event_type="freeze_detected")


def test_stale_heartbeat_counts_as_frozen(conn, vbox, vm, settings):
    services.update_vm(conn, vm["vm_id"], "Class A", 30, 3, True, "/Lab/Heartbeat")
    prepare_with_snapshot(conn, vbox, settings)
    vbox.heartbeats[("uuid-1", "/Lab/Heartbeat")] = str(minutes(1).timestamp() - 300)  # 5 min old
    services.run_cycle(conn, vbox, settings, minutes(1))
    services.run_cycle(conn, vbox, settings, minutes(2))
    assert services.list_events(conn, event_type="freeze_detected")


def test_fresh_heartbeat_is_healthy(conn, vbox, vm, settings):
    services.update_vm(conn, vm["vm_id"], "Class A", 30, 3, True, "/Lab/Heartbeat")
    vbox.heartbeats[("uuid-1", "/Lab/Heartbeat")] = str(minutes(1).timestamp() - 5)
    services.run_cycle(conn, vbox, settings, minutes(1))
    services.run_cycle(conn, vbox, settings, minutes(2))
    assert not services.list_events(conn, event_type="freeze_detected")


def test_intentionally_powered_off_vm_is_not_a_crash(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.vms["uuid-1"]["state"] = "poweroff"
    for i in range(1, 5):
        services.run_cycle(conn, vbox, settings, minutes(i))
    assert vbox.get_state("uuid-1") == "poweroff"
    assert not services.list_events(conn, event_type="crash_detected")


def test_crashed_vm_never_gets_a_snapshot_of_its_broken_state(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.crash("uuid-1")
    vbox.fail_next.add("restore_snapshot")
    services.run_cycle(conn, vbox, settings, minutes(40))     # suspect (interval is due!)
    services.run_cycle(conn, vbox, settings, minutes(41))     # restore fails
    assert len(vbox.list_snapshots("uuid-1")) == 1


def test_busy_vm_is_left_alone(conn, vbox, vm, settings):
    vbox.vms["uuid-1"]["state"] = "restoring"
    assert services.run_cycle(conn, vbox, settings, T0)["suspect"] == 0
    assert not services.list_events(conn, event_type="crash_detected")


def test_failed_restore_is_logged_and_retried_then_stops(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.crash("uuid-1")
    vbox.vms["uuid-1"]["snapshots"].clear()                    # snapshot vanished in VirtualBox
    for i in range(1, 6):
        services.run_cycle(conn, vbox, settings, minutes(i))
    assert services.list_events(conn, event_type="alert")
    assert vbox.get_state("uuid-1") == "aborted"


def test_restore_failure_triggers_alert_after_max_attempts(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.crash("uuid-1")
    for i in range(1, 12):
        vbox.fail_next.add("restore_snapshot")
        services.run_cycle(conn, vbox, settings, minutes(i))
    failed = services.list_events(conn, event_type="restore_failed")
    assert len(failed) == settings.max_restores_per_hour
    alerts = services.list_events(conn, event_type="alert")
    assert len(alerts) == 1                                    # raised once, not every cycle


def test_one_bad_vm_does_not_stop_the_cycle(conn, vbox, vm, settings):
    vbox.add_vm("N", "uuid-n")
    services.register_vm(conn, "N", "uuid-n", "B", 30, 3)
    del vbox.vms["uuid-1"]                                     # first VM vanishes from VirtualBox
    summary = services.run_cycle(conn, vbox, settings, T0)
    assert summary["snapshots"] == 1                           # second VM still handled


# ------------------------------------------------------------ manual restore and requests
def test_manual_restore_is_attributed_to_user(conn, vbox, vm, settings, users):
    admin_id, _ = users
    prepare_with_snapshot(conn, vbox, settings)
    snap = services.list_snapshots(conn, vm["vm_id"])[0]
    assert services.recover(conn, vbox, vm, minutes(5), snapshot=snap, user_id=admin_id)
    event = services.list_events(conn, event_type="restore_success")[0]
    assert event["user_id"] == admin_id and event["details"].startswith("Manual")


def test_restore_request_stays_pending_until_a_restore_happens(conn, vbox, vm, settings, users):
    admin_id, trainer_id = users
    prepare_with_snapshot(conn, vbox, settings)
    services.request_restore(conn, vm["vm_id"], trainer_id, minutes(3))
    assert len(services.pending_requests(conn)) == 1
    services.recover(conn, vbox, vm, minutes(4), user_id=admin_id)
    assert services.pending_requests(conn) == []


# ------------------------------------------------------------ dashboard and reports
def test_report_totals_and_weekly_series(conn, vbox, vm, settings):
    prepare_with_snapshot(conn, vbox, settings)
    vbox.crash("uuid-1")
    services.run_cycle(conn, vbox, settings, minutes(1))
    services.run_cycle(conn, vbox, settings, minutes(2))
    rep = services.report(conn, "2026-06-01", "2026-06-30", "All")
    assert rep["totals"]["snapshots"] == 1
    assert rep["totals"]["crashes"] == 1
    assert rep["totals"]["auto_recovered"] == 1
    assert rep["weekly"][0]["crashes"] == 1 and rep["weekly"][0]["recoveries"] == 1
    assert services.report(conn, "2026-06-01", "2026-06-30", "Other")["totals"]["crashes"] == 0


def test_dashboard_counts(conn, vbox, vm, settings):
    services.run_cycle(conn, vbox, settings, T0)
    data = services.dashboard_data(conn, T0)
    assert data["counts"]["total"] == 1 and data["counts"]["running"] == 1
    assert data["counts"]["snapshots_today"] == 1


def test_dashboard_reports_virtualbox_health(conn, vbox, vm, settings):
    data = services.dashboard_data(conn, settings=settings, vbox=vbox)
    assert data["health"]["ok"] is True
    assert data["health"]["version"] == "simulated"

    class Broken:
        def get_version(self, timeout=None):
            raise services.VBoxError("VBoxManage not found")

    data = services.dashboard_data(conn, settings=settings, vbox=Broken())
    assert data["health"]["ok"] is False
    assert data["stale"] == []                   # the worker is disabled in this fixture


def test_dashboard_marks_unchecked_vms_stale_when_the_worker_is_enabled(conn, vbox, vm, settings):
    settings.run_worker = True
    data = services.dashboard_data(conn, settings=settings)
    assert [v["vm_name"] for v in data["stale"]] == ["DEV-LAB-01"]
