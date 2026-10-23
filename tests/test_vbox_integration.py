"""VirtualBox integration behaviour that only shows up with real VMs.

These cover the failures seen in the real event log: linked clones without a
snapshot, snapshots taken while VirtualBox was busy, exports of running VMs,
and restores that deleted the original before the import had succeeded.
"""
import pytest

from app import services
from app.vbox import VBoxError


def test_marking_a_template_creates_the_snapshot_linked_clones_need(conn, vbox, vm, users):
    admin_id, _ = users
    services.set_vm_template(conn, vm["vm_id"], True, vbox=vbox, user_id=admin_id)
    snaps = vbox.list_snapshots(vm["vbox_uuid"])
    assert len(snaps) == 1 and snaps[0].startswith("template-")

    new_id = services.direct_create_vm(conn, vbox, "CLONE-01", "General", vm["vbox_uuid"],
                                       clone_type="linked", user_id=admin_id)
    assert services.get_vm(conn, new_id)["vm_name"] == "CLONE-01"


def test_linked_clone_without_a_snapshot_fails_with_a_clear_message(conn, vbox, vm, users):
    admin_id, _ = users
    with pytest.raises(ValueError, match="no snapshot"):
        services.direct_create_vm(conn, vbox, "CLONE-02", "General", vm["vbox_uuid"],
                                  clone_type="linked", user_id=admin_id)


def test_full_clone_needs_no_snapshot(conn, vbox, vm, users):
    admin_id, _ = users
    new_id = services.direct_create_vm(conn, vbox, "FULL-01", "General", vm["vbox_uuid"],
                                       clone_type="full", user_id=admin_id)
    assert services.get_vm(conn, new_id)["vm_name"] == "FULL-01"


def test_recovery_from_saved_state_discards_it_before_restoring(conn, vbox, vm):
    services.take_snapshot(conn, vbox, vm, "auto")
    vbox.save_state(vm["vbox_uuid"])
    assert vbox.get_state(vm["vbox_uuid"]) == "saved"

    assert services.recover(conn, vbox, vm) is True
    assert vbox.get_state(vm["vbox_uuid"]) == "running"


def test_snapshot_waits_for_a_busy_machine(conn, vbox, vm, monkeypatch):
    seen = []
    original = vbox.wait_until_ready
    monkeypatch.setattr(vbox, "wait_until_ready",
                        lambda v, timeout=120.0, poll=1.0: seen.append(v) or original(v))
    assert services.take_snapshot(conn, vbox, vm, "auto") is not None
    assert seen == [vm["vbox_uuid"]]


def test_snapshot_name_collision_is_retried(conn, vbox, vm):
    first = services.take_snapshot(conn, vbox, vm, "manual")
    second = services.take_snapshot(conn, vbox, vm, "manual")   # same second
    assert second and second != first
    assert {first, second} <= set(vbox.list_snapshots(vm["vbox_uuid"]))


def test_backup_saves_running_vm_then_starts_it_again(conn, vbox, vm, tmp_path):
    assert vbox.get_state(vm["vbox_uuid"]) == "running"
    backup_id = services.create_backup(conn, vbox, vm, str(tmp_path / "b"))
    assert backup_id
    assert vbox.get_state(vm["vbox_uuid"]) == "running", "the VM must be running again after an export"
    assert services.list_backups(conn, vm["vm_id"])[0]["size_bytes"] > 0


def test_failed_export_still_restarts_the_vm(conn, vbox, vm, tmp_path):
    vbox.fail_next.add("export_vm")
    with pytest.raises(VBoxError):
        services.create_backup(conn, vbox, vm, str(tmp_path / "b"))
    assert vbox.get_state(vm["vbox_uuid"]) == "running"


def test_failed_import_leaves_the_original_vm_registered(conn, vbox, vm, tmp_path):
    backup_id = services.create_backup(conn, vbox, vm, str(tmp_path / "b"))
    vbox.fail_next.add("import_vm")

    assert services.restore_backup(conn, vbox, vm, backup_id) is False
    names = [name for name, _ in vbox.list_vms()]
    assert vm["vm_name"] in names, "the original must survive a failed import"
    assert services.get_vm(conn, vm["vm_id"])["vbox_uuid"] == vm["vbox_uuid"]


def test_successful_restore_replaces_the_machine_under_the_same_name(conn, vbox, vm, tmp_path):
    backup_id = services.create_backup(conn, vbox, vm, str(tmp_path / "b"))
    assert services.restore_backup(conn, vbox, vm, backup_id) is True
    fresh = services.get_vm(conn, vm["vm_id"])
    assert fresh["vm_name"] == vm["vm_name"]
    assert fresh["vbox_uuid"] != vm["vbox_uuid"]
    assert vbox.get_state(fresh["vbox_uuid"]) == "running"
    parked = [n for n, _ in vbox.list_vms() if "-pre-restore-" in n]
    assert parked == [], "the old copy must be removed after a successful import"


def test_restore_from_a_saved_state_backup_succeeds(conn, vbox, vm, tmp_path):
    """A saved-state VM must be parked under a new name before the import."""
    backup_id = services.create_backup(conn, vbox, vm, str(tmp_path / "b"))
    vbox.save_state(vm["vbox_uuid"])                 # leave the original in the 'saved' state
    assert vbox.get_state(vm["vbox_uuid"]) == "saved"

    assert services.restore_backup(conn, vbox, vm, backup_id) is True
    fresh = services.get_vm(conn, vm["vm_id"])
    assert fresh["vm_name"] == vm["vm_name"]
    assert fresh["vbox_uuid"] != vm["vbox_uuid"]
    assert vbox.get_state(fresh["vbox_uuid"]) == "running"
    assert [n for n, _ in vbox.list_vms() if "-pre-restore-" in n] == []


def test_health_check_reports_a_broken_vbox():
    class Broken:
        def get_version(self, timeout=None):
            raise VBoxError("VBoxManage not found")

    health = services.check_vbox_health(Broken())
    assert health["ok"] is False
    assert "not found" in health["error"]
