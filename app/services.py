"""Core logic of the system: registry, snapshots, backups, health monitoring, recovery, reports.

Every function takes the database connection and the VirtualBox object it should
use, so the same code runs against real VirtualBox or the simulator, and tests
can pass a fixed `now`.
"""
import logging
import re
import secrets
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

from .vbox import BUSY_STATES, VBoxError

log = logging.getLogger("vmrecovery")

FMT = "%Y-%m-%d %H:%M:%S"
FAILING = ("crashed", "frozen")


def now_local() -> datetime:
    return datetime.now().replace(microsecond=0)


def ts(dt: datetime) -> str:
    return dt.strftime(FMT)


def parse_ts(text: str) -> datetime:
    return datetime.strptime(text, FMT)


# ---------------------------------------------------------------- disk monitoring
def check_disk_space(path: str, min_free_gb: float = 5.0, min_free_pct: float = 10.0) -> dict:
    """Check host storage available at the given path."""
    try:
        total, used, free = shutil.disk_usage(path)
        total_gb = total / (1024 ** 3)
        free_gb = free / (1024 ** 3)
        free_pct = (free / total) * 100 if total > 0 else 0.0
        is_low = (free_gb < min_free_gb) or (free_pct < min_free_pct)
        return {
            "total_gb": round(total_gb, 2),
            "free_gb": round(free_gb, 2),
            "free_pct": round(free_pct, 1),
            "is_low": is_low,
        }
    except Exception:
        return {"total_gb": 0.0, "free_gb": 0.0, "free_pct": 0.0, "is_low": False}


# ---------------------------------------------------------------- events
def log_event(conn, event_type, vm_id=None, user_id=None, details="", result="", now=None):
    now = now or now_local()
    conn.execute(
        "INSERT INTO events (vm_id, user_id, event_type, details, result, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (vm_id, user_id, event_type, details, result, ts(now)))
    conn.commit()


def alert_once(conn, vm, message, now):
    """Raise an alert, but not more than once an hour for the same message."""
    since = ts(now - timedelta(hours=1))
    vm_id = vm["vm_id"] if vm else None
    if vm_id is not None:
        seen = conn.execute(
            "SELECT 1 FROM events WHERE vm_id=? AND event_type='alert' AND details=? AND created_at>=?",
            (vm_id, message, since)).fetchone()
    else:
        seen = conn.execute(
            "SELECT 1 FROM events WHERE vm_id IS NULL AND event_type='alert' AND details=? AND created_at>=?",
            (message, since)).fetchone()
    if not seen:
        log_event(conn, "alert", vm_id, details=message, result="Alert sent", now=now)


# ---------------------------------------------------------------- registry
def get_vm(conn, vm_id):
    return conn.execute(
        "SELECT v.*, p.interval_minutes, p.retention_count, p.pre_session_snapshot, "
        "u.username AS student_username "
        "FROM vms v JOIN snapshot_policies p ON p.policy_id = v.policy_id "
        "LEFT JOIN users u ON u.user_id = v.assigned_student_id WHERE v.vm_id = ?",
        (vm_id,)).fetchone()


def list_vms(conn):
    return conn.execute(
        "SELECT v.*, p.interval_minutes, p.retention_count, p.pre_session_snapshot, "
        "u.username AS student_username, "
        "(SELECT MAX(created_at) FROM snapshots s WHERE s.vm_id = v.vm_id) AS last_snapshot, "
        "(SELECT COUNT(*) FROM backups b WHERE b.vm_id = v.vm_id) AS backup_count "
        "FROM vms v JOIN snapshot_policies p ON p.policy_id = v.policy_id "
        "LEFT JOIN users u ON u.user_id = v.assigned_student_id "
        "ORDER BY v.class_group, v.vm_name").fetchall()


def _policy_id(conn, interval, keep, pre_session):
    row = conn.execute(
        "SELECT policy_id FROM snapshot_policies WHERE interval_minutes=? AND retention_count=? "
        "AND pre_session_snapshot=?", (interval, keep, int(pre_session))).fetchone()
    if row:
        return row["policy_id"]
    cur = conn.execute(
        "INSERT INTO snapshot_policies (interval_minutes, retention_count, pre_session_snapshot) "
        "VALUES (?, ?, ?)", (interval, keep, int(pre_session)))
    return cur.lastrowid


def _check_policy(interval, keep):
    if interval < 1 or interval > 24 * 60:
        raise ValueError("Snapshot interval must be between 1 and 1440 minutes.")
    if keep < 1 or keep > 20:
        raise ValueError("Snapshots to keep must be between 1 and 20.")


def register_vm(conn, name, uuid, class_group, interval, keep, pre_session=True,
                user_id=None, heartbeat_property=None, is_template=False,
                assigned_student_id=None, now=None):
    name, uuid = (name or "").strip(), (uuid or "").strip()
    if not name or not uuid:
        raise ValueError("VM name and VirtualBox UUID are required.")
    _check_policy(interval, keep)
    if conn.execute("SELECT 1 FROM vms WHERE vbox_uuid=?", (uuid,)).fetchone():
        raise ValueError("That virtual machine is already registered.")
    policy = _policy_id(conn, interval, keep, pre_session)
    cur = conn.execute(
        "INSERT INTO vms (policy_id, created_by, vm_name, vbox_uuid, class_group, "
        "heartbeat_property, is_template, assigned_student_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (policy, user_id, name, uuid, (class_group or "General").strip() or "General",
         (heartbeat_property or "").strip() or None, int(is_template), assigned_student_id))
    conn.commit()
    log_event(conn, "vm_registered", cur.lastrowid, user_id, f"Registered {name}", "Success", now)
    return cur.lastrowid


def update_vm(conn, vm_id, class_group, interval, keep, pre_session, heartbeat_property=None,
              is_template=False, assigned_student_id=None, user_id=None, now=None):
    _check_policy(interval, keep)
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    policy = _policy_id(conn, interval, keep, pre_session)
    conn.execute(
        "UPDATE vms SET policy_id=?, class_group=?, heartbeat_property=?, is_template=?, "
        "assigned_student_id=? WHERE vm_id=?",
        (policy, (class_group or "General").strip() or "General",
         (heartbeat_property or "").strip() or None, int(is_template), assigned_student_id, vm_id))
    conn.commit()
    log_event(conn, "vm_updated", vm_id, user_id, f"Updated policy for {vm['vm_name']}", "Success", now)


def remove_vm(conn, vm_id, user_id=None, now=None):
    """Stop managing a VM. The VM itself and its snapshots in VirtualBox are left alone."""
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    log_event(conn, "vm_removed", None, user_id, f"Removed {vm['vm_name']} from the system", "Success", now)
    conn.execute("DELETE FROM vms WHERE vm_id=?", (vm_id,))
    conn.commit()


# ---------------------------------------------------------------- snapshots
def due_for_snapshot(conn, vm, now) -> bool:
    last = conn.execute("SELECT MAX(created_at) AS t FROM snapshots WHERE vm_id=?",
                        (vm["vm_id"],)).fetchone()["t"]
    return last is None or now - parse_ts(last) >= timedelta(minutes=vm["interval_minutes"])


def list_snapshots(conn, vm_id):
    return conn.execute("SELECT * FROM snapshots WHERE vm_id=? ORDER BY created_at DESC, snapshot_id DESC",
                        (vm_id,)).fetchall()


def take_snapshot(conn, vbox, vm, snap_type, now=None, user_id=None):
    """Take one snapshot, record it and apply the retention limit. Returns the name or None."""
    now = now or now_local()
    name = f"{snap_type}-{now:%Y%m%d-%H%M%S}"
    try:
        live = vbox.get_state(vm["vbox_uuid"]) == "running"
        vbox.take_snapshot(vm["vbox_uuid"], name, live=live, description=f"{snap_type} snapshot by VM recovery system")
    except VBoxError as exc:
        log_event(conn, "snapshot_failed", vm["vm_id"], user_id, f"{snap_type} snapshot failed", str(exc), now)
        return None
    conn.execute("INSERT INTO snapshots (vm_id, snapshot_name, snapshot_type, created_at) VALUES (?,?,?,?)",
                 (vm["vm_id"], name, snap_type, ts(now)))
    conn.commit()
    log_event(conn, "snapshot_taken", vm["vm_id"], user_id, f"{snap_type} snapshot {name}", "Success", now)
    apply_retention(conn, vbox, vm, now)
    return name


def apply_retention(conn, vbox, vm, now):
    """Keep only the newest `retention_count` snapshots."""
    rows = list_snapshots(conn, vm["vm_id"])
    for old in rows[vm["retention_count"]:]:
        try:
            vbox.delete_snapshot(vm["vbox_uuid"], old["snapshot_name"])
        except VBoxError as exc:
            log_event(conn, "snapshot_failed", vm["vm_id"], None,
                      f"Could not delete old snapshot {old['snapshot_name']}", str(exc), now)
            continue
        conn.execute("DELETE FROM snapshots WHERE snapshot_id=?", (old["snapshot_id"],))
        conn.commit()


def start_session(conn, vbox, class_group, user_id=None, now=None):
    """Take a pre-session snapshot of every running VM in a class group."""
    now = now or now_local()
    taken = skipped = 0
    for vm in list_vms(conn):
        if vm["class_group"] != class_group or not vm["pre_session_snapshot"]:
            continue
        try:
            running = vbox.get_state(vm["vbox_uuid"]) == "running"
        except VBoxError:
            running = False
        if running and take_snapshot(conn, vbox, vm, "pre-session", now, user_id):
            taken += 1
        else:
            skipped += 1
    log_event(conn, "session_started", None, user_id,
              f"Session started for {class_group}: {taken} snapshot(s), {skipped} skipped", "Success", now)
    return taken, skipped


# ---------------------------------------------------------------- backups (.ova export)
def list_backups(conn, vm_id):
    return conn.execute("SELECT * FROM backups WHERE vm_id=? ORDER BY created_at DESC, backup_id DESC",
                        (vm_id,)).fetchall()


def create_backup(conn, vbox, vm, backup_dir: str, user_id=None, retention_count: int = 3, now=None):
    """Export the VM to an independent OVA appliance."""
    now = now or now_local()
    b_path = Path(backup_dir)
    b_path.mkdir(parents=True, exist_ok=True)
    suffix = secrets.token_hex(4)
    filename = f"backup-{vm['vm_name']}-{now:%Y%m%d-%H%M%S}-{suffix}.ova"
    dest = b_path / filename

    try:
        vbox.export_vm(vm["vbox_uuid"], str(dest))
    except VBoxError as exc:
        log_event(conn, "backup_failed", vm["vm_id"], user_id,
                  f"Backup {filename} failed", str(exc), now)
        raise

    size = dest.stat().st_size if dest.exists() else 0
    cur = conn.execute(
        "INSERT INTO backups (vm_id, backup_name, file_path, size_bytes, created_at) VALUES (?, ?, ?, ?, ?)",
        (vm["vm_id"], filename, str(dest), size, ts(now)))
    conn.commit()
    mb = round(size / (1024 * 1024), 1)
    log_event(conn, "backup_created", vm["vm_id"], user_id,
              f"Created independent backup {filename} ({mb} MB)", "Success", now)

    apply_backup_retention(conn, vm["vm_id"], retention_count, now)
    return cur.lastrowid


def apply_backup_retention(conn, vm_id, retention_count: int, now=None):
    rows = list_backups(conn, vm_id)
    for old in rows[retention_count:]:
        try:
            p = Path(old["file_path"])
            if p.exists():
                p.unlink()
        except OSError:
            pass
        conn.execute("DELETE FROM backups WHERE backup_id=?", (old["backup_id"],))
        conn.commit()
        log_event(conn, "backup_deleted", vm_id, None,
                  f"Pruned old backup {old['backup_name']}", "Success", now)


def restore_backup(conn, vbox, vm, backup_id, user_id=None, now=None):
    """Restore/re-import a VM from an independent OVA appliance backup."""
    now = now or now_local()
    b = conn.execute("SELECT * FROM backups WHERE backup_id=? AND vm_id=?", (backup_id, vm["vm_id"])).fetchone()
    if not b:
        raise ValueError("Backup not found.")
    p = Path(b["file_path"])
    if not p.exists():
        raise ValueError(f"Backup file '{b['file_path']}' is missing on disk.")

    conn.execute("UPDATE vms SET status='restoring' WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    t0 = time.monotonic()
    try:
        state = vbox.get_state(vm["vbox_uuid"]).lower()
        if state not in ("poweroff", "aborted", "saved", "aborted-saved"):
            vbox.power_off(vm["vbox_uuid"])
        old_uuid = vm["vbox_uuid"]
        vbox.unregister_and_delete(old_uuid)
        new_name, new_uuid = vbox.import_vm(str(p), vm["vm_name"])
        conn.execute("UPDATE vms SET vbox_uuid=?, status='running', fail_count=0 WHERE vm_id=?",
                     (new_uuid, vm["vm_id"]))
        conn.commit()
        vbox.start_vm(new_uuid)
    except VBoxError as exc:
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        dur = round(time.monotonic() - t0, 2)
        log_event(conn, "backup_restore_failed", vm["vm_id"], user_id,
                  f"Restore from backup {b['backup_name']} failed after {dur}s", str(exc), now)
        return False

    dur = round(time.monotonic() - t0, 2)
    log_event(conn, "backup_restore_success", vm["vm_id"], user_id,
              f"Restored from backup {b['backup_name']} in {dur}s", "Success", now)
    return True


# ---------------------------------------------------------------- vm requests & creation
def list_templates(conn):
    return conn.execute("SELECT * FROM vms WHERE is_template=1 ORDER BY vm_name").fetchall()


def set_vm_template(conn, vm_id, is_template: bool, user_id=None, now=None):
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    conn.execute("UPDATE vms SET is_template=? WHERE vm_id=?", (int(is_template), vm_id))
    conn.commit()
    state = "marked as template" if is_template else "unmarked as template"
    log_event(conn, "vm_updated", vm_id, user_id, f"{vm['vm_name']} {state}", "Success", now)


def request_vm(conn, user_id, template_vbox_uuid, template_name, requested_name,
               class_group="General", clone_type="linked", now=None):
    now = now or now_local()
    name = (requested_name or "").strip()
    if not re.match(r'^[A-Za-z0-9_-]+$', name):
        raise ValueError("VM name must contain only letters, numbers, hyphens, and underscores.")
    if conn.execute("SELECT 1 FROM vms WHERE vm_name=?", (name,)).fetchone():
        raise ValueError("A virtual machine with that name already exists.")
    if conn.execute("SELECT 1 FROM vm_requests WHERE requested_name=? AND status IN ('pending','creating')",
                    (name,)).fetchone():
        raise ValueError("A pending request for that VM name already exists.")

    cur = conn.execute(
        "INSERT INTO vm_requests (user_id, template_vbox_uuid, template_name, requested_name, "
        "class_group, clone_type, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)",
        (user_id, template_vbox_uuid, template_name, name, (class_group or "General").strip() or "General",
         clone_type, ts(now)))
    conn.commit()
    log_event(conn, "vm_request_submitted", None, user_id,
              f"Requested VM '{name}' from template '{template_name}' ({clone_type} clone)", "Pending", now)
    return cur.lastrowid


def list_vm_requests(conn, status=None, user_id=None):
    sql = ("SELECT r.*, u.username, v.vm_name AS created_vm_name "
           "FROM vm_requests r JOIN users u ON u.user_id = r.user_id "
           "LEFT JOIN vms v ON v.vm_id = r.created_vm_id WHERE 1=1")
    args = []
    if status:
        sql += " AND r.status = ?"; args.append(status)
    if user_id:
        sql += " AND r.user_id = ?"; args.append(user_id)
    sql += " ORDER BY r.request_id DESC"
    return conn.execute(sql, args).fetchall()


def approve_vm_request(conn, vbox, request_id, admin_user_id, interval=30, keep=5,
                       pre_session=True, now=None):
    now = now or now_local()
    req = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (request_id,)).fetchone()
    if not req:
        raise ValueError("Unknown request.")
    if req["status"] != "pending":
        raise ValueError(f"Request is already {req['status']}.")

    conn.execute("UPDATE vm_requests SET status='creating', updated_at=? WHERE request_id=?",
                 (ts(now), request_id))
    conn.commit()

    try:
        new_name, new_uuid = vbox.clone_vm(
            req["template_vbox_uuid"], req["requested_name"], linked=(req["clone_type"] == "linked"))
        vm_id = register_vm(conn, new_name, new_uuid, req["class_group"], interval, keep,
                            pre_session=pre_session, user_id=req["user_id"], now=now)
        take_snapshot(conn, vbox, get_vm(conn, vm_id), "baseline", now=now, user_id=admin_user_id)
        conn.execute("UPDATE vm_requests SET status='ready', created_vm_id=?, updated_at=? WHERE request_id=?",
                     (vm_id, ts(now), request_id))
        conn.commit()
        log_event(conn, "vm_request_approved", vm_id, admin_user_id,
                  f"Approved and created '{new_name}' for trainer", "Success", now)
        return vm_id
    except Exception as exc:
        conn.execute("UPDATE vm_requests SET status='failed', rejection_reason=?, updated_at=? WHERE request_id=?",
                     (str(exc), ts(now), request_id))
        conn.commit()
        log_event(conn, "vm_request_failed", None, admin_user_id,
                  f"Failed creating '{req['requested_name']}': {exc}", "Failed", now)
        raise


def reject_vm_request(conn, request_id, admin_user_id, reason="", now=None):
    now = now or now_local()
    req = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (request_id,)).fetchone()
    if not req:
        raise ValueError("Unknown request.")
    if req["status"] != "pending":
        raise ValueError(f"Request is already {req['status']}.")
    conn.execute("UPDATE vm_requests SET status='rejected', rejection_reason=?, updated_at=? WHERE request_id=?",
                 (reason, ts(now), request_id))
    conn.commit()
    log_event(conn, "vm_request_rejected", None, admin_user_id,
              f"Rejected request for '{req['requested_name']}': {reason}", "Rejected", now)


def direct_create_vm(conn, vbox, name, class_group, template_vbox_uuid, clone_type="linked",
                     interval=30, keep=5, pre_session=True, user_id=None, now=None):
    now = now or now_local()
    name = (name or "").strip()
    if not re.match(r'^[A-Za-z0-9_-]+$', name):
        raise ValueError("VM name must contain only letters, numbers, hyphens, and underscores.")
    if conn.execute("SELECT 1 FROM vms WHERE vm_name=?", (name,)).fetchone():
        raise ValueError("A virtual machine with that name already exists.")

    new_name, new_uuid = vbox.clone_vm(template_vbox_uuid, name, linked=(clone_type == "linked"))
    vm_id = register_vm(conn, new_name, new_uuid, class_group, interval, keep,
                        pre_session=pre_session, user_id=user_id, now=now)
    take_snapshot(conn, vbox, get_vm(conn, vm_id), "baseline", now=now, user_id=user_id)
    return vm_id


# ---------------------------------------------------------------- student assignment
def assign_student(conn, vm_id, student_user_id, admin_user_id=None, now=None):
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    if student_user_id:
        user = conn.execute("SELECT * FROM users WHERE user_id=? AND role='student'",
                            (student_user_id,)).fetchone()
        if not user:
            raise ValueError("Selected user is not a valid student.")
    conn.execute("UPDATE vms SET assigned_student_id=? WHERE vm_id=?",
                 (student_user_id or None, vm_id))
    conn.commit()
    log_event(conn, "vm_assigned", vm_id, admin_user_id,
              f"Assigned {vm['vm_name']} to student ID {student_user_id}", "Success", now)


def get_student_vms(conn, student_user_id):
    return conn.execute(
        "SELECT v.*, p.interval_minutes, p.retention_count, p.pre_session_snapshot, "
        "(SELECT MAX(created_at) FROM snapshots s WHERE s.vm_id = v.vm_id) AS last_snapshot "
        "FROM vms v JOIN snapshot_policies p ON p.policy_id = v.policy_id "
        "WHERE v.assigned_student_id = ? ORDER BY v.vm_name",
        (student_user_id,)).fetchall()


# ---------------------------------------------------------------- user management
def list_users(conn):
    return conn.execute(
        "SELECT u.*, (SELECT COUNT(*) FROM vms v WHERE v.assigned_student_id = u.user_id) AS assigned_vm_count "
        "FROM users u ORDER BY u.role, u.username").fetchall()


def create_user(conn, username, password, role):
    username = (username or "").strip()
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if role not in ("admin", "trainer", "student"):
        raise ValueError("Invalid user role.")
    from werkzeug.security import generate_password_hash
    cur = conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), role))
    conn.commit()
    return cur.lastrowid


def reset_user_password(conn, user_id, new_password):
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    from werkzeug.security import generate_password_hash
    conn.execute("UPDATE users SET password_hash=? WHERE user_id=?",
                 (generate_password_hash(new_password), user_id))
    conn.commit()


def delete_user(conn, user_id):
    user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not user:
        raise ValueError("User not found.")
    if user["role"] == "admin":
        admin_count = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='admin'").fetchone()["c"]
        if admin_count <= 1:
            raise ValueError("Cannot delete the only administrator account.")
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()


# ---------------------------------------------------------------- health
def observe(vbox, vm, now, settings) -> str:
    """Translate VirtualBox's state into: running, powered off, crashed, frozen, busy or unknown."""
    try:
        raw = vbox.get_state(vm["vbox_uuid"])
    except VBoxError:
        return "unknown"
    low = raw.lower()
    if low in {s.lower() for s in BUSY_STATES}:
        return "busy"
    if low in ("aborted", "gurumeditation", "stuck", "aborted-saved"):
        return "crashed"
    if low == "paused":
        return "frozen"               # nobody should leave a lab VM paused
    if low == "running":
        prop = vm["heartbeat_property"]
        if prop:
            value = vbox.get_guest_property(vm["vbox_uuid"], prop)
            try:
                if value is not None and now.timestamp() - float(value) > settings.heartbeat_timeout:
                    return "frozen"   # the guest stopped updating its heartbeat
            except ValueError:
                pass
        return "running"
    return "powered off"


def recent_auto_attempts(conn, vm_id, now) -> int:
    since = ts(now - timedelta(hours=1))
    return conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE vm_id=? AND user_id IS NULL "
        "AND event_type IN ('restore_success','restore_failed') AND created_at>=?",
        (vm_id, since)).fetchone()["n"]


def latest_valid_snapshot(conn, vbox, vm):
    """Newest recorded snapshot that still exists in VirtualBox."""
    rows = list_snapshots(conn, vm["vm_id"])
    if not rows:
        return None
    try:
        existing = set(vbox.list_snapshots(vm["vbox_uuid"]))
    except VBoxError:
        return rows[0]
    for row in rows:
        if row["snapshot_name"] in existing:
            return row
    return None


def recover(conn, vbox, vm, now=None, snapshot=None, user_id=None) -> bool:
    """Power off if needed, restore a snapshot, start the VM, and log what happened."""
    now = now or now_local()
    snap = snapshot or latest_valid_snapshot(conn, vbox, vm)
    if snap is None:
        alert_once(conn, vm, "No usable snapshot exists. Manual recovery needed.", now)
        return False
    conn.execute("UPDATE vms SET status='restoring' WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    t0 = time.monotonic()
    try:
        state = vbox.get_state(vm["vbox_uuid"]).lower()
        if state not in ("poweroff", "aborted", "saved", "aborted-saved"):
            vbox.power_off(vm["vbox_uuid"])
        vbox.restore_snapshot(vm["vbox_uuid"], snap["snapshot_name"])
        vbox.start_vm(vm["vbox_uuid"])
    except VBoxError as exc:
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        dur = round(time.monotonic() - t0, 2)
        log_event(conn, "restore_failed", vm["vm_id"], user_id,
                  f"Restore of {snap['snapshot_name']} failed after {dur}s", str(exc), now)
        return False
    conn.execute("UPDATE vms SET status='running', fail_count=0 WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    dur = round(time.monotonic() - t0, 2)
    who = "Manual restore" if user_id else "Automatic restore"
    log_event(conn, "restore_success", vm["vm_id"], user_id,
              f"{who} ({snap['snapshot_name']}) in {dur}s", "Success", now)
    return True


def monitor_vm(conn, vbox, vm, settings, now) -> str:
    health = observe(vbox, vm, now, settings)
    if health == "unknown":
        return "unknown"
    if health == "busy":
        return "busy"
    fails = vm["fail_count"] + 1 if health in FAILING else 0
    conn.execute("UPDATE vms SET status=?, fail_count=?, last_checked=? WHERE vm_id=?",
                 (health, fails, ts(now), vm["vm_id"]))
    conn.commit()
    if health not in FAILING:
        return health
    if fails < settings.fail_threshold:
        return "suspect"                     # one bad reading is not proof; check again
    if fails == settings.fail_threshold:
        kind = "crash_detected" if health == "crashed" else "freeze_detected"
        log_event(conn, kind, vm["vm_id"], None, f"VirtualBox reports the machine as {health}", "Detected", now)
    if recent_auto_attempts(conn, vm["vm_id"], now) >= settings.max_restores_per_hour:
        alert_once(conn, vm, f"Automatic recovery stopped after {settings.max_restores_per_hour} "
                             f"attempts in an hour. Manual action needed.", now)
        return "needs_admin"
    fresh = get_vm(conn, vm["vm_id"])
    return "recovered" if recover(conn, vbox, fresh, now) else "recovery_failed"


def run_cycle(conn, vbox, settings, now=None) -> dict:
    """One pass of the background service: check every VM, then snapshot those that are due."""
    now = now or now_local()
    summary = {"checked": 0, "snapshots": 0, "recoveries": 0, "failed_recoveries": 0, "suspect": 0}

    # Host low-disk warning check
    b_dir = getattr(settings, "backup_dir", "instance/backups")
    min_gb = getattr(settings, "disk_min_free_gb", 5.0)
    min_pct = getattr(settings, "disk_min_free_pct", 10.0)
    disk = check_disk_space(b_dir, min_gb, min_pct)
    if disk["is_low"]:
        alert_once(conn, None, f"Low host disk space: {disk['free_gb']} GB ({disk['free_pct']}%) free.", now)

    for row in conn.execute("SELECT vm_id FROM vms").fetchall():
        try:
            vm = get_vm(conn, row["vm_id"])
            outcome = monitor_vm(conn, vbox, vm, settings, now)
            summary["checked"] += 1
            if outcome == "recovered":
                summary["recoveries"] += 1
                continue                      # just restored: no snapshot needed this cycle
            if outcome in ("recovery_failed", "needs_admin"):
                summary["failed_recoveries"] += 1
            if outcome == "suspect":
                summary["suspect"] += 1

            # Skip periodic snapshotting for templates
            if vm["is_template"]:
                continue

            vm = get_vm(conn, row["vm_id"])
            has_none = not list_snapshots(conn, vm["vm_id"])
            eligible = vm["status"] == "running" or (vm["status"] == "powered off" and has_none)
            if eligible and due_for_snapshot(conn, vm, now):
                if take_snapshot(conn, vbox, vm, "auto", now):
                    summary["snapshots"] += 1
        except Exception:                     # one bad VM must not stop the others
            log.exception("Cycle failed for vm_id=%s", row["vm_id"])
    return summary


# ---------------------------------------------------------------- restore requests
def request_restore(conn, vm_id, user_id, now=None):
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    log_event(conn, "restore_requested", vm_id, user_id,
              f"Restore requested for {vm['vm_name']}", "Pending", now)


def pending_requests(conn):
    return conn.execute(
        "SELECT e.*, v.vm_name, u.username, u.role FROM events e "
        "JOIN vms v ON v.vm_id = e.vm_id "
        "LEFT JOIN users u ON u.user_id = e.user_id "
        "WHERE e.event_type='restore_requested' AND NOT EXISTS ("
        "  SELECT 1 FROM events r WHERE r.vm_id = e.vm_id AND r.event_id > e.event_id "
        "  AND r.event_type IN ('restore_success','restore_failed')) "
        "ORDER BY e.event_id DESC").fetchall()


# ---------------------------------------------------------------- dashboard, logs, reports
def dashboard_data(conn, now=None, settings=None):
    if hasattr(now, "backup_dir"):
        settings, now = now, None
    elif now is not None and not isinstance(now, datetime):
        settings, now = now, None
    now = now or now_local()
    vms = list_vms(conn)
    counts = {"total": len(vms), "running": 0, "frozen": 0, "crashed": 0}
    for vm in vms:
        if vm["status"] in counts:
            counts[vm["status"]] += 1
    today = now.strftime("%Y-%m-%d")
    counts["snapshots_today"] = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE event_type='snapshot_taken' AND created_at LIKE ?",
        (today + "%",)).fetchone()["n"]
    counts["backups_total"] = conn.execute("SELECT COUNT(*) AS n FROM backups").fetchone()["n"]
    counts["pending_vm_requests"] = conn.execute(
        "SELECT COUNT(*) AS n FROM vm_requests WHERE status='pending'").fetchone()["n"]
    recent = conn.execute(
        "SELECT e.*, v.vm_name FROM events e LEFT JOIN vms v ON v.vm_id = e.vm_id "
        "WHERE e.event_type IN ('crash_detected','freeze_detected','restore_success','restore_failed',"
        "'alert','backup_created','vm_request_submitted','vm_request_approved') "
        "AND e.created_at >= ? ORDER BY e.event_id DESC LIMIT 8",
        (ts(now - timedelta(hours=24)),)).fetchall()
    groups = sorted({vm["class_group"] for vm in vms})
    b_dir = getattr(settings, "backup_dir", "instance/backups") if settings else "instance/backups"
    disk = check_disk_space(b_dir)
    return {"vms": vms, "counts": counts, "recent": recent, "groups": groups, "disk": disk}


def list_events(conn, vm_id=None, event_type=None, day=None, limit=200):
    sql = ("SELECT e.*, v.vm_name, u.username FROM events e "
           "LEFT JOIN vms v ON v.vm_id = e.vm_id LEFT JOIN users u ON u.user_id = e.user_id WHERE 1=1")
    args = []
    if vm_id:
        sql += " AND e.vm_id = ?"; args.append(vm_id)
    if event_type:
        sql += " AND e.event_type = ?"; args.append(event_type)
    if day:
        sql += " AND e.created_at LIKE ?"; args.append(day + "%")
    sql += " ORDER BY e.event_id DESC LIMIT ?"
    args.append(limit)
    return conn.execute(sql, args).fetchall()


def report(conn, start: str, end: str, class_group: str | None = None) -> dict:
    """Totals and a weekly crashes-versus-recoveries series between two dates (inclusive)."""
    lo, hi = start + " 00:00:00", end + " 23:59:59"
    join = "LEFT JOIN vms v ON v.vm_id = e.vm_id"
    where = "e.created_at BETWEEN ? AND ?"
    args = [lo, hi]
    if class_group and class_group != "All":
        where += " AND v.class_group = ?"
        args.append(class_group)

    def count(types, extra=""):
        marks = ",".join("?" * len(types))
        return conn.execute(f"SELECT COUNT(*) AS n FROM events e {join} WHERE {where} "
                            f"AND e.event_type IN ({marks}) {extra}", args + list(types)).fetchone()["n"]

    totals = {
        "snapshots": count(["snapshot_taken"]),
        "crashes": count(["crash_detected", "freeze_detected"]),
        "auto_recovered": count(["restore_success"], "AND e.user_id IS NULL"),
        "manual_recovered": count(["restore_success"], "AND e.user_id IS NOT NULL"),
        "manual_action": count(["alert"]),
        "backups": count(["backup_created"]),
    }
    weekly = conn.execute(
        f"SELECT strftime('%Y-W%W', e.created_at) AS week, "
        f"SUM(e.event_type IN ('crash_detected','freeze_detected')) AS crashes, "
        f"SUM(e.event_type = 'restore_success') AS recoveries "
        f"FROM events e {join} WHERE {where} GROUP BY week ORDER BY week", args).fetchall()
    return {"totals": totals, "weekly": [dict(r) for r in weekly]}
