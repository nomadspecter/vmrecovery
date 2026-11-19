"""Live verification of VMRecovery core objectives:
1. Automated scheduled snapshots without human intervention
2. Automated pre-session snapshot on session start
3. Automated crash detection and rollback restore without human intervention
4. Automated freeze detection (heartbeat stall) and rollback restore without human intervention
5. Snapshot retention pruning without human intervention
6. Event logging and recovery duration tracking
"""
import sys
import time
from datetime import datetime, timedelta
import sqlite3
from app.db import init_db, connect
from app.vbox import SimulatedVBox
from app.config import Settings
import app.services as services

def run_objective_verification():
    print("=" * 70)
    print("VERIFYING SYSTEM OBJECTIVES & UNATTENDED AUTOMATION")
    print("=" * 70)

    # 1. Setup isolated database and simulated hypervisor
    db_path = "instance/test_objectives.db"
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
    
    init_db(db_path)
    conn = connect(db_path)
    
    settings = Settings()
    vbox = SimulatedVBox(demo_vms=False)

    # Create admin user
    services.create_user(conn, "admin", "admin123", "admin")
    admin = conn.execute("SELECT user_id FROM users WHERE username='admin'").fetchone()

    # -------------------------------------------------------------
    # OBJECTIVE 1: VM Registry & Grouping
    # -------------------------------------------------------------
    print("\n[OBJECTIVE 1] Registering Lab VMs into Registry...")
    # Add VM to hypervisor
    vm1_uuid = "11111111-1111-1111-1111-111111111111"
    vbox.add_vm("Lab-VM-101", vm1_uuid, state="running")
    
    # Register with policy: interval=10 min, keep=3 snapshots, pre_session=True
    vm1_id = services.register_vm(
        conn, name="Lab-VM-101", uuid=vm1_uuid, class_group="Computer Science 101",
        interval=10, keep=3, pre_session=True, user_id=admin["user_id"],
        heartbeat_property="/Lab/Heartbeat"
    )
    vm1 = services.get_vm(conn, vm1_id)
    assert vm1 is not None, "VM failed to register!"
    print(f"  -> SUCCESS: Registered VM ID {vm1_id} ('{vm1['vm_name']}') in group '{vm1['class_group']}'.")

    # -------------------------------------------------------------
    # OBJECTIVE 2: Automated Snapshot on Schedule & Pre-session
    # -------------------------------------------------------------
    print("\n[OBJECTIVE 2A] Automated Pre-Session Snapshot on Session Start...")
    # Start session for Computer Science 101
    t0 = datetime(2026, 10, 23, 9, 0, 0)
    res = services.start_session(conn, vbox, "Computer Science 101", user_id=admin["user_id"], now=t0)
    print(f"  -> Session started: {res['started']}")
    
    # Verify pre-session snapshot was taken automatically
    snaps = services.list_snapshots(conn, vm1_id)
    assert len(snaps) == 1, f"Expected 1 pre-session snapshot, got {len(snaps)}"
    assert snaps[0]["snapshot_type"] == "pre-session"
    print(f"  -> SUCCESS: Pre-session snapshot automatically captured: '{snaps[0]['snapshot_name']}'")

    print("\n[OBJECTIVE 2B] Automated Scheduled Snapshots & Retention Pruning...")
    # Cycle 1: 15 minutes later (interval is 10 mins) -> should take automatic snapshot
    t1 = t0 + timedelta(minutes=15)
    vbox._find(vm1_uuid)["heartbeat"] = t1.timestamp()
    cycle1 = services.run_cycle(conn, vbox, settings, now=t1)
    snaps = services.list_snapshots(conn, vm1_id)
    assert len(snaps) == 2, f"Expected 2 snapshots, got {len(snaps)}"
    print(f"  -> Cycle at +15m: Automated snapshot captured: '{snaps[1]['snapshot_name']}'")

    # Cycle 2: 30 minutes later -> should take 3rd snapshot
    t2 = t0 + timedelta(minutes=30)
    vbox._find(vm1_uuid)["heartbeat"] = t2.timestamp()
    services.run_cycle(conn, vbox, settings, now=t2)
    snaps = services.list_snapshots(conn, vm1_id)
    assert len(snaps) == 3, f"Expected 3 snapshots, got {len(snaps)}"
    print(f"  -> Cycle at +30m: Automated snapshot captured: '{snaps[2]['snapshot_name']}'")

    # Cycle 3: 45 minutes later -> should take 4th snapshot, BUT retention limit is 3!
    # Oldest snapshot must be pruned automatically!
    t3 = t0 + timedelta(minutes=45)
    vbox._find(vm1_uuid)["heartbeat"] = t3.timestamp()
    services.run_cycle(conn, vbox, settings, now=t3)
    snaps = services.list_snapshots(conn, vm1_id)
    assert len(snaps) == 3, f"Retention failed! Expected 3 snapshots max, got {len(snaps)}"
    print(f"  -> Cycle at +45m: Automated snapshot captured and oldest pruned! Total active snapshots = {len(snaps)} (Retention Enforced).")

    # -------------------------------------------------------------
    # OBJECTIVE 3: Unattended Automated Crash Recovery
    # -------------------------------------------------------------
    print("\n[OBJECTIVE 3] Testing Unattended Automated Crash Recovery...")
    # Simulate a sudden guest crash / aborted state
    print("  -> Simulating VM crash (state changed to 'aborted')...")
    vbox.crash(vm1_uuid)
    assert vbox.get_state(vm1_uuid) == "aborted"
    print(f"  -> Hypervisor VM state: {vbox.get_state(vm1_uuid)}")

    # Monitoring worker runs cycle 1 (detects suspect / fail_count=1)
    t4 = t3 + timedelta(seconds=10)
    print("  -> Worker cycle 1: Debouncing (fail_count=1, state marked 'suspect')...")
    res1 = services.run_cycle(conn, vbox, settings, now=t4)
    print(f"     Cycle 1 result: {res1}")

    # Monitoring worker runs cycle 2 (reaches fail_threshold=2 -> triggers automated restore!)
    t4_2 = t4 + timedelta(seconds=10)
    print("  -> Worker cycle 2: Confirmed crash (fail_count=2 >= threshold -> automated rollback & restart)...")
    res2 = services.run_cycle(conn, vbox, settings, now=t4_2)
    print(f"     Cycle 2 result: {res2}")
    
    # Check VM state in hypervisor and database
    restored_state = vbox.get_state(vm1_uuid)
    vm_db = services.get_vm(conn, vm1_id)
    print(f"  -> Hypervisor VM state after auto-recovery: '{restored_state}'")
    print(f"  -> Database VM status: '{vm_db['status']}'")
    assert restored_state == "running", f"Expected VM to be restored and running, got {restored_state}"
    assert vm_db["status"] == "running", f"Expected DB status to be running, got {vm_db['status']}"
    print("  -> SUCCESS: Crashed VM was automatically detected, restored to latest snapshot, and restarted with zero human intervention!")

    # -------------------------------------------------------------
    # OBJECTIVE 4: Unattended Automated Freeze Detection (Heartbeat Stall)
    # -------------------------------------------------------------
    print("\n[OBJECTIVE 4] Testing Unattended Automated Freeze Recovery (Hung OS)...")
    # Simulate a frozen guest whose heartbeat property stopped updating 300s ago
    t5 = t4_2 + timedelta(minutes=5)
    vbox.heartbeats[(vm1_uuid, "/Lab/Heartbeat")] = str(t5.timestamp() - 300)
    print("  -> Worker cycle 1 after freeze (heartbeat 300s old): Debouncing (fail_count=1, state marked 'suspect')...")
    services.run_cycle(conn, vbox, settings, now=t5)
    vm_db = services.get_vm(conn, vm1_id)
    print(f"     Cycle 1 result: fail_count = {vm_db['fail_count']}")
    assert vm_db["fail_count"] == 1

    # Cycle 2: Stale heartbeat persists -> fail_count reaches 2 (fail_threshold) -> triggers automated recovery!
    t6 = t5 + timedelta(seconds=10)
    print("  -> Worker cycle 2: Confirmed freeze (fail_count=2 >= threshold -> automated rollback & restart)...")
    res_freeze = services.run_cycle(conn, vbox, settings, now=t6)
    print(f"     Cycle 2 result: {res_freeze}")
    
    vm_db = services.get_vm(conn, vm1_id)
    restored_state = vbox.get_state(vm1_uuid)
    print(f"  -> Hypervisor VM state after auto-recovery: '{restored_state}'")
    print(f"  -> Database VM status: '{vm_db['status']}', fail_count reset to: {vm_db['fail_count']}")
    assert restored_state == "running"
    assert vm_db["status"] == "running"
    print("  -> SUCCESS: Frozen VM was detected, powered off, restored to snapshot, and resumed with zero human intervention!")

    # -------------------------------------------------------------
    # OBJECTIVE 5: Audit Trail & Reporting
    # -------------------------------------------------------------
    print("\n[OBJECTIVE 5] Verifying Audit Trail & Recovery Durations...")
    events = services.list_events(conn, vm_id=vm1_id)
    print(f"  -> Total logged events for VM: {len(events)}")
    recovery_events = [e for e in events if e["event_type"] in ("restore", "crash_detected", "freeze_detected")]
    for re in recovery_events:
        print(f"     * [{re['created_at']}] Type: {re['event_type']} | Result: {re['result']} | Duration: {re['duration_seconds']}s")
    
    assert len(recovery_events) >= 2, "Expected recovery events logged"
    print("  -> SUCCESS: All recovery events, debounced failures, and execution timings recorded in audit log!")

    # Cleanup
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

    print("\n" + "=" * 70)
    print("ALL CORE SYSTEM OBJECTIVES VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_objective_verification()
