"""Tests for new production features:
- Independent OVA appliance backups and restore
- Host low-disk space monitoring and alerts
- VM template cloning and request/approval workflow
- Student role, workstation view, and student restore requests
- Web user administration
- Recovery duration tracking
"""
import pytest
from app import services
from app.vbox import SimulatedVBox


def test_disk_space_check(tmp_path):
    disk = services.check_disk_space(str(tmp_path), min_free_gb=0.0001, min_free_pct=0.001)
    assert disk["total_gb"] > 0
    assert disk["free_gb"] > 0
    assert not disk["is_low"]

    # When threshold is impossibly high, is_low is True
    disk_low = services.check_disk_space(str(tmp_path), min_free_gb=999999.0)
    assert disk_low["is_low"] is True


def test_independent_backup_and_retention(conn, vbox, vm, tmp_path):
    backup_dir = str(tmp_path / "backups")
    # Create 3 backups
    b1 = services.create_backup(conn, vbox, vm, backup_dir, retention_count=2)
    b2 = services.create_backup(conn, vbox, vm, backup_dir, retention_count=2)
    b3 = services.create_backup(conn, vbox, vm, backup_dir, retention_count=2)

    backups = services.list_backups(conn, vm["vm_id"])
    # Retention limit is 2, so only 2 should remain in database
    assert len(backups) == 2
    assert backups[0]["backup_id"] == b3
    assert backups[1]["backup_id"] == b2

    # Restore from backup
    ok = services.restore_backup(conn, vbox, vm, b3)
    assert ok is True
    fresh = services.get_vm(conn, vm["vm_id"])
    assert fresh["status"] == "running"


def test_template_cloning_and_request_workflow(conn, vbox, vm, users):
    admin_id, trainer_id = users
    # 1. Mark VM as template
    services.set_vm_template(conn, vm["vm_id"], True, user_id=admin_id)
    templates = services.list_templates(conn)
    assert len(templates) == 1
    assert templates[0]["vm_id"] == vm["vm_id"]

    # 2. Trainer submits VM request
    req_id = services.request_vm(
        conn,
        user_id=trainer_id,
        template_vbox_uuid=vm["vbox_uuid"],
        template_name=vm["vm_name"],
        requested_name="TRAIN-LAB-01",
        class_group="Networking",
        clone_type="linked"
    )
    reqs = services.list_vm_requests(conn, status="pending")
    assert len(reqs) == 1
    assert reqs[0]["requested_name"] == "TRAIN-LAB-01"

    # 3. Admin approves request
    new_vm_id = services.approve_vm_request(conn, vbox, req_id, admin_id)
    new_vm = services.get_vm(conn, new_vm_id)
    assert new_vm["vm_name"] == "TRAIN-LAB-01"
    assert new_vm["class_group"] == "Networking"

    # Check request is now marked ready
    req_after = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (req_id,)).fetchone()
    assert req_after["status"] == "ready"
    assert req_after["created_vm_id"] == new_vm_id

    # 4. Reject workflow test
    req_id2 = services.request_vm(
        conn,
        user_id=trainer_id,
        template_vbox_uuid=vm["vbox_uuid"],
        template_name=vm["vm_name"],
        requested_name="TRAIN-LAB-02",
        class_group="Networking"
    )
    services.reject_vm_request(conn, req_id2, admin_id, reason="Capacity full")
    req2_after = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (req_id2,)).fetchone()
    assert req2_after["status"] == "rejected"
    assert req2_after["rejection_reason"] == "Capacity full"


def test_direct_create_vm(conn, vbox, vm, users):
    admin_id, _ = users
    new_vm_id = services.direct_create_vm(
        conn, vbox, "DIRECT-LAB-01", "Security", vm["vbox_uuid"],
        clone_type="linked", user_id=admin_id
    )
    created = services.get_vm(conn, new_vm_id)
    assert created["vm_name"] == "DIRECT-LAB-01"
    assert created["class_group"] == "Security"
    # Should have baseline snapshot taken
    snaps = services.list_snapshots(conn, new_vm_id)
    assert len(snaps) == 1
    assert snaps[0]["snapshot_type"] == "baseline"


def test_student_assignment_and_restore(conn, vbox, vm, users):
    admin_id, _ = users
    # Create student
    stu_id = services.create_user(conn, "student_jane", "password123", "student")
    services.assign_student(conn, vm["vm_id"], stu_id, admin_id)

    student_vms = services.get_student_vms(conn, stu_id)
    assert len(student_vms) == 1
    assert student_vms[0]["vm_id"] == vm["vm_id"]

    # Student requests restore
    services.request_restore(conn, vm["vm_id"], user_id=stu_id)
    events = services.list_events(conn, vm_id=vm["vm_id"], event_type="restore_requested")
    assert len(events) == 1
    assert events[0]["user_id"] == stu_id


def test_user_management_crud(conn):
    # Create
    uid = services.create_user(conn, "bob_trainer", "securepass123", "trainer")
    users = services.list_users(conn)
    assert any(u["username"] == "bob_trainer" for u in users)

    # Password reset
    services.reset_user_password(conn, uid, "newsecurepass456")

    # Delete
    services.delete_user(conn, uid)
    users_after = services.list_users(conn)
    assert not any(u["username"] == "bob_trainer" for u in users_after)


def test_restore_duration_tracking(conn, vbox, vm):
    # Take a snapshot first
    services.take_snapshot(conn, vbox, vm, "baseline")
    # Recover VM
    ok = services.recover(conn, vbox, vm)
    assert ok is True
    # Verify event contains duration measurement
    events = services.list_events(conn, vm_id=vm["vm_id"], event_type="restore_success")
    assert len(events) >= 1
    assert " in " in events[0]["details"]
    assert "s" in events[0]["details"]
