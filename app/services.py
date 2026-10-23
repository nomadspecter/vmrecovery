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

from .vbox import (BUSY_STATES, CRASHED_STATES, PAUSED_STATES, POWERED_OFF_STATES,
                   SAVED_STATES, VBoxError, state_is_busy)

log = logging.getLogger("vmrecovery")

FMT = "%Y-%m-%d %H:%M:%S"
FAILING = ("crashed", "frozen")


def now_local() -> datetime:
    return datetime.now().replace(microsecond=0)


def ts(dt: datetime) -> str:
    return dt.strftime(FMT)


def parse_ts(text: str) -> datetime:
    return datetime.strptime(text, FMT)


def _seconds_since(text: str, now: datetime) -> float:
    """How long ago a timestamp was. Unreadable or missing means "just now"."""
    if not text:
        return 0.0
    try:
        return max(0.0, (now - parse_ts(text)).total_seconds())
    except (ValueError, TypeError):
        return 0.0


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
def log_event(conn, event_type, vm_id=None, user_id=None, details="", result="", now=None,
              duration=None):
    now = now or now_local()
    conn.execute(
        "INSERT INTO events (vm_id, user_id, event_type, details, result, duration_seconds, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (vm_id, user_id, event_type, details, result, duration, ts(now)))
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
        notify(conn, "Alert: " + message[:80], message, severity="warning", vm_id=vm_id, now=now)


# ---------------------------------------------------------------- notifications
def notify(conn, subject, body, severity="info", vm_id=None, now=None):
    """Send a notification over the configured channels.

    Never raises: a notification problem must not abort the recovery flow
    that triggered it. The attempt is recorded in the notifications table
    either way.
    """
    from . import notifier
    from .config import Settings

    settings = _settings_holder.get("settings")
    if settings is None:
        settings = Settings.from_env()
    try:
        notifier.send(conn, settings, subject, body, severity=severity, vm_id=vm_id, now=now)
    except Exception:
        log.exception("Notification could not be sent")


# Holds the live Settings object so helpers that only receive a database
# connection can still reach the notification channels.
_settings_holder: dict = {}


def set_runtime_settings(settings) -> None:
    """Publish the live settings object used by :func:`notify`."""
    _settings_holder["settings"] = settings


# ---------------------------------------------------------------- runtime settings
SETTING_TYPES = {
    "check_seconds": int,
    "fail_threshold": int,
    "max_restores_per_hour": int,
    "heartbeat_timeout": int,
    "vbox_timeout": int,
    "vbox_query_timeout": int,
    "vbox_lock_timeout": int,
    "live_snapshots": bool,
    "busy_timeout": int,
    "session_hours": int,
    "backup_retention_count": int,
    "disk_min_free_gb": float,
    "disk_min_free_pct": float,
    "event_retention_days": int,
    "login_max_failures": int,
    "login_window_seconds": int,
    "db_backup_keep": int,
    "smtp_port": int,
    "notify_email_enabled": bool,
    "smtp_use_tls": bool,
    "notify_webhook_enabled": bool,
    "backup_dir": str,
    "db_backup_dir": str,
    "smtp_host": str,
    "smtp_user": str,
    "smtp_password": str,
    "smtp_from": str,
    "smtp_to": str,
    "webhook_url": str,
    "webhook_secret": str,
    "api_token": str,
    "log_level": str,
}

# Values an administrator may not change from the browser.
SETTINGS_READ_ONLY = {"host", "port", "db_path", "secret_key", "simulate", "vboxmanage",
                      "run_worker", "dev_server", "cookie_secure"}


def all_overrides(conn) -> dict:
    """Every runtime override stored in the database."""
    return {row["key"]: row["value"]
            for row in conn.execute("SELECT key, value FROM app_settings").fetchall()}


def get_override(conn, key, default=None):
    row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_override(conn, key, value, user_id=None, now=None):
    """Store one runtime override. Returns the stored value."""
    if key in SETTINGS_READ_ONLY:
        raise ValueError(f"'{key}' cannot be changed from the Settings page.")
    if key not in SETTING_TYPES:
        raise ValueError(f"'{key}' is not a known setting.")
    now = now or now_local()
    value = "" if value is None else str(value).strip()
    want = SETTING_TYPES[key]
    if want is bool:
        value = "1" if value.lower() in ("1", "true", "yes", "on") else "0"
    elif want is int:
        value = str(int(value))
    elif want is float:
        value = str(float(value))
    conn.execute(
        "INSERT INTO app_settings (key, value, updated_at, updated_by) VALUES (?,?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at, "
        "updated_by=excluded.updated_by",
        (key, value, ts(now), user_id))
    conn.commit()
    log_event(conn, "setting_changed", None, user_id, f"{key} set to '{_redact(key, value)}'",
              "Success", now)
    return value


def clear_override(conn, key, user_id=None, now=None):
    if key not in SETTING_TYPES:
        raise ValueError(f"'{key}' is not a known setting.")
    now = now or now_local()
    conn.execute("DELETE FROM app_settings WHERE key=?", (key,))
    conn.commit()
    log_event(conn, "setting_changed", None, user_id, f"{key} reset to the configured default",
              "Success", now)


def _redact(key, value):
    if key in ("smtp_password", "webhook_secret", "api_token") and value:
        return "***"
    return value


def apply_overrides(conn, settings):
    """Push the database overrides onto the live settings object."""
    overrides = all_overrides(conn)
    settings.apply_overrides(overrides)
    return overrides



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


def remove_vm(conn, vm_id, user_id=None, now=None, vbox=None, delete_from_vbox=False):
    """Stop managing a VM.

    The VM itself and its snapshots in VirtualBox are left alone unless
    ``delete_from_vbox`` is asked for, in which case the machine is
    unregistered and its files are deleted as well.
    """
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    name = vm["vm_name"]
    if delete_from_vbox:
        if vbox is None:
            raise ValueError("No VirtualBox connection is available.")
        try:
            vbox.unregister_and_delete(vm["vbox_uuid"])
        except VBoxError as exc:
            log_event(conn, "vm_delete_failed", vm_id, user_id,
                      f"Could not delete {name} from VirtualBox", str(exc), now)
            raise ValueError(f"VirtualBox refused to delete {name}: {exc}")
    log_event(conn, "vm_removed", None, user_id, f"Removed {name} from the system", "Success", now)
    conn.execute("DELETE FROM vms WHERE vm_id=?", (vm_id,))
    conn.commit()


# ---------------------------------------------------------------- power control
POWER_ACTIONS = ("start", "stop", "pause", "resume", "reset", "restart")


def power_action(conn, vbox, vm_id, action, user_id=None, now=None):
    """Change the power state of one virtual machine.

    Returns a short message describing what happened. Raises ValueError when
    the action is not possible and VBoxError when VirtualBox refuses.
    """
    action = (action or "").strip().lower()
    if action not in POWER_ACTIONS:
        raise ValueError(f"Unknown power action '{action}'.")
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    uuid, name = vm["vbox_uuid"], vm["vm_name"]
    state = vbox.wait_until_ready(uuid).lower()

    if action == "start":
        if state == "running":
            return f"{name} is already running."
        if state == "paused":
            vbox.resume_vm(uuid)
            return f"{name} was resumed."
        vbox.start_vm(uuid)
    elif action == "stop":
        if state in ("poweroff", "aborted"):
            return f"{name} is already powered off."
        if state == "saved":
            vbox.discard_state(uuid)
            vbox.wait_for_state(uuid, ("poweroff", "aborted"))
        else:
            vbox.power_off(uuid)
    elif action == "pause":
        if state != "running":
            raise ValueError(f"{name} can only be paused while it is running (it is {state}).")
        vbox.pause_vm(uuid)
    elif action == "resume":
        if state != "paused":
            raise ValueError(f"{name} can only be resumed while it is paused (it is {state}).")
        vbox.resume_vm(uuid)
    elif action == "reset":
        if state in ("poweroff", "aborted"):
            vbox.start_vm(uuid)
        else:
            vbox.power_off(uuid)
            # A machine that is still going down cannot be started again yet;
            # VirtualBox refuses the start with "Current object state
            # prohibits operation".
            vbox.wait_for_state(uuid, ("poweroff", "aborted"))
            vbox.start_vm(uuid)
    elif action == "restart":
        if state in ("poweroff", "aborted"):
            vbox.start_vm(uuid)
        else:
            vbox.power_off(uuid)
            vbox.wait_for_state(uuid, ("poweroff", "aborted"))
            vbox.start_vm(uuid)

    new_state = vbox.wait_until_ready(uuid).lower()
    # Only a deliberate pause is remembered; anything else clears the flag so
    # the monitor judges the machine normally again.
    admin_paused = 1 if (action == "pause" and new_state == "paused") else 0
    status = "paused" if admin_paused else _friendly_state(new_state)
    conn.execute("UPDATE vms SET status=?, fail_count=0, last_checked=?, admin_paused=? WHERE vm_id=?",
                 (status, ts(now or now_local()), admin_paused, vm_id))
    conn.commit()
    log_event(conn, f"vm_{action}", vm_id, user_id, f"{name}: {action} (was {state})",
              "Success", now)
    return f"{name}: {action} completed, the machine is now {new_state}."


def _friendly_state(state: str) -> str:
    """Map a VirtualBox state word onto the vocabulary the dashboard uses."""
    state = (state or "").lower()
    if state == "running":
        return "running"
    if state == "paused":
        return "frozen"
    if state in ("poweroff", "saved", "aborted-saved"):
        return "powered off"
    if state in ("aborted", "gurumeditation", "stuck"):
        return "crashed"
    return state or "unknown"


def bulk_power_action(conn, vbox, vm_ids, action, user_id=None, now=None):
    """Apply one power action to several machines. Returns a result summary."""
    summary = {"done": [], "failed": []}
    for vm_id in vm_ids:
        vm = get_vm(conn, vm_id)
        if not vm:
            summary["failed"].append((vm_id, "Unknown virtual machine."))
            continue
        try:
            summary["done"].append(power_action(conn, vbox, vm_id, action, user_id, now))
        except (ValueError, VBoxError) as exc:
            summary["failed"].append((vm["vm_name"], str(exc)))
    return summary



# ---------------------------------------------------------------- snapshots
def due_for_snapshot(conn, vm, now) -> bool:
    last = conn.execute("SELECT MAX(created_at) AS t FROM snapshots WHERE vm_id=?",
                        (vm["vm_id"],)).fetchone()["t"]
    return last is None or now - parse_ts(last) >= timedelta(minutes=vm["interval_minutes"])


def list_snapshots(conn, vm_id):
    return conn.execute("SELECT * FROM snapshots WHERE vm_id=? ORDER BY created_at DESC, snapshot_id DESC",
                        (vm_id,)).fetchall()


def take_snapshot(conn, vbox, vm, snap_type, now=None, user_id=None, live=None):
    """Take one snapshot, record it and apply the retention limit. Returns the name or None.

    A live snapshot is *not* the default. ``VBoxManage snapshot take --live`` asks
    the guest to write its memory out, and a guest that does not answer never
    lets the command return: VirtualBox sits in ``onlinesnapshotting`` and the
    command holds the VirtualBox lock until it is killed. A normal snapshot of
    a running machine is crash-consistent, is taken in a second, and never
    wedges the service. Live snapshots are therefore opt-in, via
    ``VMR_LIVE_SNAPSHOTS=1`` or the Settings page.
    """
    now = now or now_local()
    base = f"{snap_type}-{now:%Y%m%d-%H%M%S}"
    name = base
    if live is None:
        settings = _settings_holder.get("settings")
        live = bool(getattr(settings, "live_snapshots", False))
    try:
        vbox.wait_until_ready(vm["vbox_uuid"])   # never snapshot during LiveSnapshotting
        if live and vbox.get_state(vm["vbox_uuid"]) != "running":
            live = False                       # a live snapshot needs a running guest
        vbox.take_snapshot(vm["vbox_uuid"], name, live=live, description=f"{snap_type} snapshot by VM recovery system")
    except VBoxError as exc:
        if "already exists" in str(exc).lower():
            name = f"{base}-{secrets.token_hex(2)}"   # two actions in the same second
            try:
                vbox.take_snapshot(vm["vbox_uuid"], name, live=live,
                                   description=f"{snap_type} snapshot by VM recovery system")
            except VBoxError as retry_exc:
                log_event(conn, "snapshot_failed", vm["vm_id"], user_id,
                          f"{snap_type} snapshot failed", str(retry_exc), now_local())
                return None
        else:
            log_event(conn, "snapshot_failed", vm["vm_id"], user_id,
                      f"{snap_type} snapshot failed", str(exc), now_local())
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
    if not rows[vm["retention_count"]:]:
        return
    # A machine that is still taking the snapshot it was just asked for
    # refuses to delete the old one, so it is given time to settle first.
    try:
        vbox.wait_until_ready(vm["vbox_uuid"])
    except VBoxError as exc:
        log_event(conn, "snapshot_failed", vm["vm_id"], None,
                  "Could not prune old snapshots", str(exc), now)
        return
    for old in rows[vm["retention_count"]:]:
        try:
            vbox.delete_snapshot(vm["vbox_uuid"], old["snapshot_name"])
        except VBoxError as exc:
            log_event(conn, "snapshot_failed", vm["vm_id"], None,
                      f"Could not delete old snapshot {old['snapshot_name']}", str(exc), now)
            continue
        conn.execute("DELETE FROM snapshots WHERE snapshot_id=?", (old["snapshot_id"],))
        conn.commit()


# ---------------------------------------------------------------- training sessions
def active_session(conn, class_group):
    """The session currently open for a class group, if any."""
    return conn.execute(
        "SELECT s.*, u.username AS started_by_name FROM class_sessions s "
        "LEFT JOIN users u ON u.user_id = s.started_by "
        "WHERE s.class_group = ? AND s.status = 'active' "
        "ORDER BY s.session_id DESC LIMIT 1", (class_group,)).fetchone()


def list_active_sessions(conn):
    return conn.execute(
        "SELECT s.*, u.username AS started_by_name FROM class_sessions s "
        "LEFT JOIN users u ON u.user_id = s.started_by "
        "WHERE s.status = 'active' ORDER BY s.class_group").fetchall()


def _protected_in_session(conn, vm_id, session_started_at):
    """True when this VM already has a pre-session snapshot from the current session."""
    return conn.execute(
        "SELECT 1 FROM snapshots WHERE vm_id=? AND snapshot_type='pre-session' "
        "AND created_at >= ? LIMIT 1", (vm_id, session_started_at)).fetchone() is not None


def _bring_up(conn, vbox, vm, user_id, now, result, action):
    """Start or resume one VM. Returns True when it is running afterwards."""
    try:
        state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        was_running = state == "running"
        if state == "paused":
            vbox.resume_vm(vm["vbox_uuid"])
            state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        elif state != "running":
            vbox.start_vm(vm["vbox_uuid"])          # also resumes a saved VM
            state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        if state != "running":
            result["failed"].append((vm["vm_name"], f"machine ended up {state}"))
            log_event(conn, "session_vm_failed", vm["vm_id"], user_id,
                      f"{action}: {vm['vm_name']} ended up {state}", "Failed", now)
            return False
        if was_running:
            result["already_running"] += 1
        else:
            result["started"] += 1
        return True
    except VBoxError as exc:
        result["failed"].append((vm["vm_name"], str(exc)))
        log_event(conn, "session_vm_failed", vm["vm_id"], user_id,
                  f"{action}: {vm['vm_name']} failed", str(exc), now)
        return False


def start_session(conn, vbox, class_group, user_id=None, now=None):
    """Open a training session for a class group and bring its VMs up.

    The first press starts powered-off, aborted and saved VMs, resumes paused
    ones and takes one pre-session snapshot per VM whose policy enables it.
    Pressing Start again while the session is active is idempotent: it
    restarts VMs that stopped and protects VMs that have no pre-session snapshot
    for this session yet, but never duplicates an existing one.
    """
    class_group = (class_group or "").strip()
    if not class_group:
        raise ValueError("Choose a class group.")
    now = now or now_local()
    vms = [vm for vm in list_vms(conn) if vm["class_group"] == class_group]
    if not vms:
        raise ValueError(f"No virtual machines are registered in '{class_group}'.")

    result = {"session_id": None, "already_active": False, "session_started_at": None,
              "started": 0, "already_running": 0, "snapshots": 0, "already_protected": 0,
              "skipped": 0, "failed": []}

    active = active_session(conn, class_group)
    if active:
        result["already_active"] = True
        result["session_id"] = active["session_id"]
        result["session_started_at"] = active["started_at"]
        for vm in vms:
            if not _bring_up(conn, vbox, vm, user_id, now, result, "Session resume"):
                continue
            if not vm["pre_session_snapshot"]:
                result["skipped"] += 1
                continue
            if _protected_in_session(conn, vm["vm_id"], active["started_at"]):
                result["already_protected"] += 1
                continue
            # A VM added after the session opened, or one whose snapshot failed
            # or was pruned, still gets protected on this retry.
            if take_snapshot(conn, vbox, vm, "pre-session", now, user_id):
                result["snapshots"] += 1
            else:
                result["failed"].append((vm["vm_name"], "snapshot failed (see event log)"))
        details = (f"Session already active for {class_group} since {active['started_at']}: "
                   f"{result['started']} VM(s) started, {result['already_running']} already running, "
                   f"{result['snapshots']} new pre-session snapshot(s), "
                   f"{result['already_protected']} VM(s) already protected")
        if result["failed"]:
            details += f", {len(result['failed'])} failed"
        log_event(conn, "session_already_active", None, user_id, details,
                  "Partial" if result["failed"] else "Skipped", now)
        return result

    cur = conn.execute(
        "INSERT INTO class_sessions (class_group, status, started_by, started_at) VALUES (?, 'active', ?, ?)",
        (class_group, user_id, ts(now)))
    conn.commit()
    result["session_id"] = cur.lastrowid
    result["session_started_at"] = ts(now)

    for vm in vms:
        if not _bring_up(conn, vbox, vm, user_id, now, result, "Session start"):
            continue
        if not vm["pre_session_snapshot"]:
            result["skipped"] += 1
            continue
        if take_snapshot(conn, vbox, vm, "pre-session", now, user_id):
            result["snapshots"] += 1
        else:
            result["failed"].append((vm["vm_name"], "snapshot failed (see event log)"))

    details = (f"Session started for {class_group}: {result['started']} VM(s) started, "
               f"{result['already_running']} already running, "
               f"{result['snapshots']} snapshot(s) taken, {result['skipped']} skipped")
    if result["failed"]:
        details += f", {len(result['failed'])} failed"
    log_event(conn, "session_started", None, user_id, details,
              "Partial" if result["failed"] else "Success", now)
    return result


def end_session(conn, vbox, class_group, user_id=None, now=None, power_off=True):
    """Close the active session for a class group.

    Running VMs get a final post-session snapshot (when their pre-session
    snapshot policy is enabled) and are optionally powered off. The session row
    is marked ended even when one VM fails, so the group can start a new session.
    """
    class_group = (class_group or "").strip()
    if not class_group:
        raise ValueError("Choose a class group.")
    active = active_session(conn, class_group)
    if not active:
        raise ValueError(f"No active session for '{class_group}'.")
    now = now or now_local()
    result = {"session_id": active["session_id"], "snapshots": 0,
              "powered_off": 0, "already_off": 0, "failed": []}

    for vm in list_vms(conn):
        if vm["class_group"] != class_group:
            continue
        try:
            state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
            if vm["pre_session_snapshot"] and state in ("running", "paused"):
                if take_snapshot(conn, vbox, vm, "post-session", now, user_id):
                    result["snapshots"] += 1
                else:
                    result["failed"].append((vm["vm_name"], "post-session snapshot failed"))
            if power_off:
                if state in ("running", "paused"):
                    # The snapshot above may have left the machine busy for a
                    # moment, and a busy machine refuses to be powered off.
                    vbox.wait_until_ready(vm["vbox_uuid"])
                    vbox.power_off(vm["vbox_uuid"])
                    result["powered_off"] += 1
                else:
                    result["already_off"] += 1
        except VBoxError as exc:
            result["failed"].append((vm["vm_name"], str(exc)))
            log_event(conn, "session_vm_failed", vm["vm_id"], user_id,
                      f"Session end: {vm['vm_name']} failed", str(exc), now)

    conn.execute("UPDATE class_sessions SET status='ended', ended_by=?, ended_at=? WHERE session_id=?",
                 (user_id, ts(now), active["session_id"]))
    conn.commit()
    details = (f"Session ended for {class_group}: {result['snapshots']} post-session snapshot(s), "
               f"{result['powered_off']} VM(s) powered off")
    if result["failed"]:
        details += f", {len(result['failed'])} failed"
    log_event(conn, "session_ended", None, user_id, details,
              "Partial" if result["failed"] else "Success", now)
    return result


# ---------------------------------------------------------------- backups (.ova export)
def list_backups(conn, vm_id):
    return conn.execute("SELECT * FROM backups WHERE vm_id=? ORDER BY created_at DESC, backup_id DESC",
                        (vm_id,)).fetchall()


def create_backup(conn, vbox, vm, backup_dir: str, user_id=None, retention_count: int = 3, now=None):
    """Export the VM to an independent OVA appliance.

    VirtualBox refuses to export a running machine, so a running or paused VM is
    saved to disk for the export and started again afterwards, even if the export
    fails. Saved state is discarded when the VM is resumed so it boots cleanly.
    """
    now = now or now_local()
    b_path = Path(backup_dir)
    b_path.mkdir(parents=True, exist_ok=True)
    suffix = secrets.token_hex(4)
    filename = f"backup-{vm['vm_name']}-{now:%Y%m%d-%H%M%S}-{suffix}.ova"
    dest = b_path / filename

    was_active = False
    settings = _settings_holder.get("settings")
    save_timeout = int(getattr(settings, "vbox_timeout", 1800) or 1800)
    try:
        state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        was_active = state in ("running", "paused")
        if was_active:
            vbox.save_state(vm["vbox_uuid"])
            # The export has to wait for the machine to settle into "saved",
            # otherwise VirtualBox refuses it with "Current object state
            # prohibits operation". Saving a large machine takes a while, so
            # the wait is given the long timeout rather than the short one.
            vbox.wait_for_state(vm["vbox_uuid"], ("saved", "aborted-saved"),
                                timeout=save_timeout)
        vbox.export_vm(vm["vbox_uuid"], str(dest))
    except VBoxError as exc:
        log_event(conn, "backup_failed", vm["vm_id"], user_id,
                  f"Backup {filename} failed", str(exc), now)
        raise
    finally:
        if was_active:
            try:
                vbox.discard_state(vm["vbox_uuid"])
                vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted"))
                vbox.start_vm(vm["vbox_uuid"])
            except VBoxError as exc:
                log_event(conn, "alert", vm["vm_id"], user_id,
                          f"{vm['vm_name']} could not be restarted after the backup: {exc}", "Alert sent", now)

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
    """Restore a VM from an independent OVA appliance backup.

    The original VM is renamed first, the appliance is imported under the real
    name, and only after the import succeeds is the old copy unregistered and
    deleted. A failed import therefore leaves the original VM intact.
    """
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
    old_uuid = vm["vbox_uuid"]
    old_name = vm["vm_name"]
    parked_name = f"{old_name}-pre-restore-{now:%Y%m%d-%H%M%S}"
    parked = False
    try:
        state = vbox.wait_until_ready(old_uuid).lower()
        if state in ("saved", "aborted-saved"):
            vbox.discard_state(old_uuid)      # a saved state blocks both export and import
            vbox.wait_for_state(old_uuid, ("poweroff", "aborted"))
        elif state not in ("poweroff", "aborted"):
            vbox.power_off(old_uuid)
            vbox.wait_for_state(old_uuid, ("poweroff", "aborted"))
        base_folder = vbox.base_folder(old_uuid)
        vbox.rename_vm(old_uuid, parked_name)   # free the name for the import
        parked = True
        new_name, new_uuid = vbox.import_vm(str(p), old_name, base_folder=base_folder)
    except VBoxError as exc:
        if parked:
            try:                                # put the original back if it still exists
                vbox.rename_vm(parked_name, old_name)
            except VBoxError:
                pass
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        dur = round(time.monotonic() - t0, 2)
        log_event(conn, "backup_restore_failed", vm["vm_id"], user_id,
                  f"Restore from backup {b['backup_name']} failed after {dur}s", str(exc), now, dur)
        notify(conn, f"Backup restore failed: {vm['vm_name']}",
               f"Restoring {vm['vm_name']} from {b['backup_name']} failed after {dur}s.\n\n{exc}",
               severity="critical", vm_id=vm["vm_id"], now=now)
        return False

    # The import succeeded, so the new machine is the one to keep. Removing the
    # parked copy is housekeeping: if it fails, the restore still succeeded.
    try:
        vbox.unregister_and_delete(parked_name)
    except VBoxError as exc:
        log_event(conn, "alert", vm["vm_id"], user_id,
                  f"Restored {old_name} but could not remove the old copy '{parked_name}': {exc}",
                  "Alert sent", now)

    conn.execute("UPDATE vms SET vbox_uuid=?, vm_name=?, status='running', fail_count=0 WHERE vm_id=?",
                 (new_uuid, new_name, vm["vm_id"]))
    conn.commit()
    try:
        # The import registers the machine while its disk is still being
        # written; starting it too early fails to open the disk.
        vbox.wait_for_state(new_uuid, ("poweroff", "aborted"))
        vbox.start_vm(new_uuid)
    except VBoxError as exc:
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        dur = round(time.monotonic() - t0, 2)
        log_event(conn, "backup_restore_failed", vm["vm_id"], user_id,
                  f"Imported {new_name} from {b['backup_name']} but it would not start after {dur}s",
                  str(exc), now)
        return False

    dur = round(time.monotonic() - t0, 2)
    log_event(conn, "backup_restore_success", vm["vm_id"], user_id,
              f"Restored from backup {b['backup_name']} in {dur}s", "Success", now, dur)
    return True


# ---------------------------------------------------------------- vm requests & creation
def list_templates(conn):
    return conn.execute("SELECT * FROM vms WHERE is_template=1 ORDER BY vm_name").fetchall()


def set_vm_template(conn, vm_id, is_template: bool, vbox=None, user_id=None, now=None):
    """Mark or unmark a VM as a golden template.

    A linked clone can only be made from a snapshot, so a template without one
    gets a baseline snapshot as soon as it is marked.
    """
    now = now or now_local()
    vm = get_vm(conn, vm_id)
    if not vm:
        raise ValueError("Unknown virtual machine.")
    conn.execute("UPDATE vms SET is_template=? WHERE vm_id=?", (int(is_template), vm_id))
    conn.commit()
    state = "marked as template" if is_template else "unmarked as template"
    log_event(conn, "vm_updated", vm_id, user_id, f"{vm['vm_name']} {state}", "Success", now)
    if is_template and vbox is not None and not list_snapshots(conn, vm_id):
        take_snapshot(conn, vbox, vm, "template", now=now, user_id=user_id)


def _template_snapshot(conn, vbox, template_uuid):
    """The newest snapshot of a template, which a linked clone must name."""
    try:
        existing = vbox.list_snapshots(template_uuid)
    except VBoxError:
        existing = []
    if not existing:
        raise ValueError("This template has no snapshot yet. Mark it as a template again "
                         "or take a snapshot, then retry the clone.")
    return existing[-1]


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
    notify(conn, f"New virtual machine request: {name}",
           f"A {clone_type} clone of '{template_name}' was requested for class group "
           f"'{class_group}'. Approve or reject it on the VM Requests page.",
           severity="info", now=now)
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


def _prepare_clone_source(vbox, vm_uuid):
    """Make a machine clonable. Returns a callable that puts it back as it was.

    VirtualBox refuses to clone a machine that is running — it answers
    "Current object state prohibits operation" — so a template that is in use
    has to be suspended first. The machine is put back the way it was found
    afterwards, so cloning a template does not quietly stop it.

    The state is not just reached, it has to settle. VirtualBox tears the
    running process down in several steps, and a clone issued in the middle of
    that is refused, which is why saving the state and cloning it straight
    afterwards used to fail.
    """
    settings = _settings_holder.get("settings")
    # Writing the memory image of a large machine to disk takes a while, and
    # the wait has to outlast it — otherwise the clone is attempted while
    # VirtualBox is still saving.
    save_timeout = int(getattr(settings, "vbox_timeout", 1800) or 1800)
    state = vbox.get_state(vm_uuid).lower()
    if state_is_busy(state):
        # The machine is mid-something — a snapshot, a start, a probe. It is
        # not clonable now, and the reason is worth saying out loud.
        raise ValueError(f"The template is busy ('{state}') and cannot be cloned "
                         f"at the moment. Try again in a moment.")
    state = vbox.wait_until_ready(vm_uuid).lower()
    if state in ("poweroff", "off", "aborted"):
        return None                    # already clonable
    if state in ("saved", "aborted-saved"):
        vbox.wait_for_state(vm_uuid, ("saved", "aborted-saved"), timeout=save_timeout)
        return None
    if state == "paused":
        vbox.resume_vm(vm_uuid)
        state = "running"
    if state != "running":
        raise ValueError(f"The template is in the state '{state}' and cannot be cloned "
                         f"at the moment.")
    vbox.save_state(vm_uuid)
    vbox.wait_for_state(vm_uuid, ("saved", "aborted-saved"), timeout=save_timeout)

    def restore():
        vbox.discard_state(vm_uuid)
        vbox.wait_for_state(vm_uuid, ("poweroff", "aborted"))
        vbox.start_vm(vm_uuid)

    return restore


def purge_clone_leftovers(vbox, new_name, conn=None):
    """Clear everything a failed clone left behind, so the name can be used again.

    A failed clone leaves its disk in VirtualBox's media registry even though
    the machine was never registered. The next attempt to clone the same name
    then fails for that reason alone — "Clone VM failed", with nothing else to
    show for it — and the name stays unusable until the registry is cleaned
    by hand. This is what made a failed clone permanent.
    """
    folder = Path(vbox.default_machine_folder() or "") / new_name
    if not folder.is_absolute():
        # Without a known machine folder there is nothing safe to delete.
        folder = None
    for name, uuid in vbox.list_vms():
        if name != new_name:
            continue
        known = conn is not None and conn.execute(
            "SELECT 1 FROM vms WHERE vbox_uuid=? OR vm_name=?", (uuid, new_name)).fetchone()
        if known:
            # It is one of ours and existed before this clone, so it is not
            # ours to delete.
            log.warning("'%s' is already a registered machine, leaving it alone", new_name)
            break
        try:
            vbox.unregister_and_delete(new_name)   # the clone was registered after all
        except VBoxError as exc:
            log.warning("Could not unregister the failed clone '%s': %s", new_name, exc)
        break
    # The disks first, deepest first: a differencing disk holds its base open.
    if folder is not None:
        for vdi in sorted(folder.glob("**/*.vdi"), key=lambda p: len(p.parts), reverse=True):
            try:
                vbox.close_medium(str(vdi))
            except VBoxError as exc:
                log.warning("Could not close the failed clone's disk %s: %s", vdi, exc)
        # And any disk still registered under this folder, whether or not its
        # file is still on disk.
        for medium in vbox.list_media():
            loc = medium.get("Location", "")
            if loc and str(folder) in loc:
                try:
                    vbox.close_medium(loc)
                except VBoxError as exc:
                    log.warning("Could not close the stale disk %s: %s", loc, exc)
        shutil.rmtree(folder, ignore_errors=True)


def _clone_from_template(vbox, template_uuid, new_name, linked, snapshot, conn=None):
    """Clone a template, suspending it first if it is running.

    The template is always put back the way it was, whether the clone worked
    or not. A failed clone is cleared away and tried once more, because the
    failure usually leaves something behind that would make the second
    attempt fail for a completely different reason.
    """
    restore = _prepare_clone_source(vbox, template_uuid)
    try:
        for attempt in (1, 2):
            try:
                name, uuid = vbox.clone_vm(template_uuid, new_name, linked=linked,
                                           snapshot=snapshot)
                # A fresh clone is registered while its disk is still being
                # written, and it inherits the template's saved state. Both
                # are settled here: the saved state is thrown away so the
                # machine boots cleanly when it is started.
                vbox.wait_for_state(uuid, ("poweroff", "aborted", "saved"))
                if vbox.get_state(uuid).lower() in ("saved", "aborted-saved"):
                    vbox.discard_state(uuid)
                    vbox.wait_for_state(uuid, ("poweroff", "aborted"))
                return name, uuid
            except VBoxError:
                if attempt == 2:
                    raise
                log.warning("The clone of '%s' failed, clearing what it left behind "
                            "and trying once more", new_name)
                purge_clone_leftovers(vbox, new_name, conn=conn)
    finally:
        if restore is not None:
            try:
                restore()
            except VBoxError as exc:
                log.error("Could not start the template again after cloning it: %s", exc)


def approve_vm_request(conn, vbox, request_id, admin_user_id, interval=30, keep=5,
                       pre_session=True, now=None):
    now = now or now_local()
    req = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (request_id,)).fetchone()
    if not req:
        raise ValueError("Unknown request.")
    # A request that failed can be tried again. The usual reason for the
    # failure is transient — the template was busy, or VirtualBox was in the
    # middle of something — and making the trainer write the request out a
    # second time helps nobody.
    #
    # A request left in 'creating' is one whose process died mid-clone. It
    # can be retried too, but only once it is obviously abandoned, so that a
    # clone that is still running is not started a second time.
    if req["status"] == "creating":
        age = _seconds_since(req["updated_at"], now)
        if age < 3600:
            raise ValueError("This request is already being processed. "
                             "Wait for it to finish, or retry it in an hour.")
    elif req["status"] not in ("pending", "failed"):
        raise ValueError(f"Request is already {req['status']}.")

    conn.execute("UPDATE vm_requests SET status='creating', updated_at=? WHERE request_id=?",
                 (ts(now), request_id))
    conn.commit()

    try:
        snap_name = _template_snapshot(conn, vbox, req["template_vbox_uuid"]) \
            if req["clone_type"] == "linked" else None
        new_name, new_uuid = _clone_from_template(
            vbox, req["template_vbox_uuid"], req["requested_name"],
            linked=(req["clone_type"] == "linked"), snapshot=snap_name, conn=conn)
        vm_id = register_vm(conn, new_name, new_uuid, req["class_group"], interval, keep,
                            pre_session=pre_session, user_id=req["user_id"], now=now)
        take_snapshot(conn, vbox, get_vm(conn, vm_id), "baseline", now=now, user_id=admin_user_id)
        conn.execute("UPDATE vm_requests SET status='ready', created_vm_id=?, updated_at=?, "
                     "rejection_reason=NULL WHERE request_id=?",
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
                  f"Failed creating '{req['requested_name']}': {exc}", "Failed", now_local())
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

    snap_name = _template_snapshot(conn, vbox, template_vbox_uuid) \
        if clone_type == "linked" else None
    new_name, new_uuid = _clone_from_template(vbox, template_vbox_uuid, name,
                                               linked=(clone_type == "linked"),
                                               snapshot=snap_name, conn=conn)
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
    except VBoxError as exc:
        log.warning("Could not read the state of %s: %s", vm["vm_name"], exc)
        return "unknown"
    low = (raw or "").strip().lower()
    if low in BUSY_STATES:
        # VirtualBox is working on the machine. It is not crashed and it is not
        # switched off, and acting on it now would fail.
        if vm["status"] != "busy":
            log.warning("%s is busy: VirtualBox reports the state '%s'. It will not be "
                        "touched until VirtualBox settles.", vm["vm_name"], raw)
        return "busy"
    if low in CRASHED_STATES:
        return "crashed"
    if low in PAUSED_STATES:
        # A machine an administrator paused on purpose is left alone.
        return "paused" if vm["admin_paused"] else "frozen"
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
    if low in POWERED_OFF_STATES or low in SAVED_STATES:
        return "powered off"
    # A state word this code does not know is not "powered off". Calling it
    # that would make the dashboard claim the machine is off while it is in
    # fact stuck in something VirtualBox will refuse to act on.
    log.warning("VirtualBox reports an unfamiliar state for %s: %r", vm["vm_name"], raw)
    return "unknown"


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
        state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        if state in ("saved", "aborted-saved"):
            vbox.discard_state(vm["vbox_uuid"])   # saved state blocks snapshot restore
            vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted"))
        elif state not in ("poweroff", "aborted"):
            vbox.power_off(vm["vbox_uuid"])
            vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted"))
        vbox.restore_snapshot(vm["vbox_uuid"], snap["snapshot_name"])
        # The restore returns while the machine is still settling out of it,
        # and a start in the middle of that is refused.
        vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted", "saved"))
        vbox.start_vm(vm["vbox_uuid"])
    except VBoxError as exc:
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        dur = round(time.monotonic() - t0, 2)
        log_event(conn, "restore_failed", vm["vm_id"], user_id,
                  f"Restore of {snap['snapshot_name']} failed after {dur}s", str(exc), now_local(), dur)
        notify(conn, f"Restore failed: {vm['vm_name']}",
               f"Restoring {vm['vm_name']} to {snap['snapshot_name']} failed after {dur}s.\n\n{exc}",
               severity="critical", vm_id=vm["vm_id"], now=now)
        return False
    conn.execute("UPDATE vms SET status='running', fail_count=0 WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    dur = round(time.monotonic() - t0, 2)
    who = "Manual restore" if user_id else "Automatic restore"
    log_event(conn, "restore_success", vm["vm_id"], user_id,
              f"{who} ({snap['snapshot_name']}) in {dur}s", "Success", now, dur)
    return True


def monitor_vm(conn, vbox, vm, settings, now) -> str:
    health = observe(vbox, vm, now, settings)
    fails = vm["fail_count"] + 1 if health in FAILING else 0
    # The row is refreshed even for a busy or unreadable machine. Leaving the
    # old status in place would show a machine as running while it is stuck,
    # and a stale last_checked is how a dead worker looks like a live one.
    status_since = vm["status_since"] or vm["last_checked"]
    if health != vm["status"] or not status_since:
        status_since = ts(now)
    conn.execute("UPDATE vms SET status=?, fail_count=?, last_checked=?, status_since=? WHERE vm_id=?",
                 (health, fails, ts(now), status_since, vm["vm_id"]))
    conn.commit()
    if health == "busy":
        # VirtualBox has been working on the machine for too long. It is not
        # going to settle on its own, and nothing can be done to the machine
        # until an administrator looks at it.
        busy_for = _seconds_since(status_since, now)
        limit = getattr(settings, "busy_timeout", 300)
        if busy_for >= limit:
            alert_once(conn, vm, f"VirtualBox has been busy with {vm['vm_name']} for more "
                                 f"than {limit}s. The machine looks stuck and needs an "
                                 f"administrator.", now)
            log.error("VirtualBox is stuck on %s (busy for %ds)", vm["vm_name"], int(busy_for))
            return "needs_admin"
        return "busy"
    if health == "unknown":
        return "unknown"
    if health not in FAILING:
        return health
    if fails < settings.fail_threshold:
        return "suspect"                     # one bad reading is not proof; check again
    if fails == settings.fail_threshold:
        kind = "crash_detected" if health == "crashed" else "freeze_detected"
        log_event(conn, kind, vm["vm_id"], None, f"VirtualBox reports the machine as {health}", "Detected", now)
        notify(conn, f"{'Crash' if health == 'crashed' else 'Freeze'} detected: {vm['vm_name']}",
               f"VirtualBox reports {vm['vm_name']} ({vm['class_group']}) as {health}. "
               f"The recovery service is taking action.",
               severity="critical", vm_id=vm["vm_id"], now=now)
    if recent_auto_attempts(conn, vm["vm_id"], now) >= settings.max_restores_per_hour:
        alert_once(conn, vm, f"Automatic recovery stopped after {settings.max_restores_per_hour} "
                             f"attempts in an hour. Manual action needed.", now)
        return "needs_admin"
    fresh = get_vm(conn, vm["vm_id"])
    return "recovered" if recover(conn, vbox, fresh, now) else "recovery_failed"


def run_cycle(conn, vbox, settings, now=None, lock=None) -> dict:
    """One pass of the background service: check every VM, then snapshot those that are due.

    The lock is taken per VM, not for the whole cycle, so a slow snapshot or
    export of one machine does not freeze the web UI for the others.

    Runtime overrides stored in the database are re-read at the start of every
    cycle, so a change made on the Settings page takes effect on the next pass
    without restarting the service.
    """
    now = now or now_local()
    apply_overrides(conn, settings)
    summary = {"checked": 0, "snapshots": 0, "recoveries": 0, "failed_recoveries": 0, "suspect": 0}

    # Host low-disk warning check
    b_dir = getattr(settings, "backup_dir", "instance/backups")
    min_gb = getattr(settings, "disk_min_free_gb", 5.0)
    min_pct = getattr(settings, "disk_min_free_pct", 10.0)
    disk = check_disk_space(b_dir, min_gb, min_pct)
    if disk["is_low"]:
        alert_once(conn, None, f"Low host disk space: {disk['free_gb']} GB ({disk['free_pct']}%) free.", now)

    for row in conn.execute("SELECT vm_id FROM vms").fetchall():
        acquired = False
        try:
            if lock is not None:
                # A bounded wait. The lock is held for the whole of a VirtualBox
                # command, and a command that never returns would otherwise stop
                # the monitoring without a word.
                acquired = lock.acquire(timeout=getattr(settings, "vbox_lock_timeout", 30))
                if not acquired:
                    log.warning("Skipped vm_id=%s: another VirtualBox operation is still running",
                                row["vm_id"])
                    continue
            try:
                vm = get_vm(conn, row["vm_id"])
                outcome = monitor_vm(conn, vbox, vm, settings, now)
                summary["checked"] += 1
                if outcome == "recovered":
                    summary["recoveries"] += 1
                    continue                  # just restored: no snapshot needed this cycle
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
            finally:
                if acquired and lock is not None:
                    lock.release()
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
    notify(conn, f"Restore requested: {vm['vm_name']}",
           f"User {user_id} asked for {vm['vm_name']} to be restored. "
           f"Review it on the dashboard and restore it from a snapshot.",
           severity="warning", vm_id=vm_id, now=now)


def pending_requests(conn):
    return conn.execute(
        "SELECT e.*, v.vm_name, u.username, u.role FROM events e "
        "JOIN vms v ON v.vm_id = e.vm_id "
        "LEFT JOIN users u ON u.user_id = e.user_id "
        "WHERE e.event_type='restore_requested' AND NOT EXISTS ("
        "  SELECT 1 FROM events r WHERE r.vm_id = e.vm_id AND r.event_id > e.event_id "
        "  AND r.event_type IN ('restore_success','restore_failed')) "
        "ORDER BY e.event_id DESC").fetchall()


# ---------------------------------------------------------------- health of VirtualBox itself
def check_vbox_health(vbox, timeout: float = 5.0) -> dict:
    """Can the system talk to VirtualBox at all? Used by the dashboard banner and /system."""
    try:
        version = vbox.get_version(timeout=timeout)
        vms = vbox.list_vms(timeout=timeout)
        return {"ok": True, "version": version, "vm_count": len(vms), "error": None}
    except VBoxError as exc:
        return {"ok": False, "version": None, "vm_count": 0, "error": str(exc)}


# ---------------------------------------------------------------- dashboard, logs, reports
def dashboard_data(conn, now=None, settings=None, vbox=None):
    """Everything the dashboard needs, in one call."""
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
    counts["failed_recoveries_24h"] = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE event_type='restore_failed' "
        "AND created_at >= ?", (ts(now - timedelta(hours=24)),)).fetchone()["n"]
    counts["mean_recovery_seconds"] = _mean_recovery_seconds(conn, now - timedelta(days=30))
    recent = conn.execute(
        "SELECT e.*, v.vm_name FROM events e LEFT JOIN vms v ON v.vm_id = e.vm_id "
        "WHERE e.event_type IN ('crash_detected','freeze_detected','restore_success','restore_failed',"
        "'alert','backup_created','vm_request_submitted','vm_request_approved',"
        "'session_started','session_already_active','session_ended') "
        "AND e.created_at >= ? ORDER BY e.event_id DESC LIMIT 8",
        (ts(now - timedelta(hours=24)),)).fetchall()
    groups = sorted({vm["class_group"] for vm in vms})
    active_sessions = list_active_sessions(conn)
    b_dir = getattr(settings, "backup_dir", "instance/backups") if settings else "instance/backups"
    min_gb = getattr(settings, "disk_min_free_gb", 5.0) if settings else 5.0
    min_pct = getattr(settings, "disk_min_free_pct", 10.0) if settings else 10.0
    disk = check_disk_space(b_dir, min_gb, min_pct)
    health = check_vbox_health(vbox) if vbox is not None else None
    stale_after = getattr(settings, "check_seconds", 30) * 3 if settings else 90
    stale = []
    if getattr(settings, "run_worker", True):     # no worker = no expectation of fresh checks
        for vm in vms:
            last = vm["last_checked"]
            try:
                if last is None or now - parse_ts(last) > timedelta(seconds=stale_after):
                    stale.append(vm)
            except ValueError:
                stale.append(vm)
    return {"vms": vms, "counts": counts, "recent": recent, "groups": groups, "disk": disk,
            "health": health, "stale": stale, "active_sessions": active_sessions}


def _mean_recovery_seconds(conn, since) -> float | None:
    """Average time to recover a machine, over the given window."""
    row = conn.execute(
        "SELECT AVG(duration_seconds) AS avg FROM events "
        "WHERE event_type='restore_success' AND duration_seconds IS NOT NULL AND created_at >= ?",
        (ts(since),)).fetchone()
    return round(row["avg"], 1) if row and row["avg"] is not None else None


def list_events(conn, vm_id=None, event_type=None, day=None, limit=200, offset=0,
                student_user_id=None, severity=None):
    """Return audit-trail events, newest first.

    ``student_user_id`` restricts the result to the machines assigned to that
    student, so a student can look at their own history without seeing the
    rest of the lab.
    """
    sql = ("SELECT e.*, v.vm_name, u.username FROM events e "
           "LEFT JOIN vms v ON v.vm_id = e.vm_id LEFT JOIN users u ON u.user_id = e.user_id WHERE 1=1")
    args = []
    if vm_id:
        sql += " AND e.vm_id = ?"; args.append(vm_id)
    if event_type:
        sql += " AND e.event_type = ?"; args.append(event_type)
    if day:
        sql += " AND e.created_at LIKE ?"; args.append(day + "%")
    if student_user_id is not None:
        sql += (" AND (e.vm_id IN (SELECT vm_id FROM vms WHERE assigned_student_id = ?) "
                "OR e.user_id = ?)")
        args += [student_user_id, student_user_id]
    sql += " ORDER BY e.event_id DESC LIMIT ? OFFSET ?"
    args += [limit, offset]
    return conn.execute(sql, args).fetchall()


def count_events(conn, vm_id=None, event_type=None, day=None, student_user_id=None) -> int:
    """The number of events matching the same filters as :func:`list_events`."""
    sql = "SELECT COUNT(*) AS n FROM events e LEFT JOIN vms v ON v.vm_id = e.vm_id WHERE 1=1"
    args = []
    if vm_id:
        sql += " AND e.vm_id = ?"; args.append(vm_id)
    if event_type:
        sql += " AND e.event_type = ?"; args.append(event_type)
    if day:
        sql += " AND e.created_at LIKE ?"; args.append(day + "%")
    if student_user_id is not None:
        sql += (" AND (e.vm_id IN (SELECT vm_id FROM vms WHERE assigned_student_id = ?) "
                "OR e.user_id = ?)")
        args += [student_user_id, student_user_id]
    return conn.execute(sql, args).fetchone()["n"]


def prune_events(conn, retention_days: int, now=None) -> int:
    """Delete events older than the retention window. Returns the number removed."""
    if not retention_days or retention_days <= 0:
        return 0
    now = now or now_local()
    cutoff = ts(now - timedelta(days=retention_days))
    cur = conn.execute("DELETE FROM events WHERE created_at < ?", (cutoff,))
    conn.commit()
    return cur.rowcount


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
    avg = conn.execute(
        f"SELECT AVG(e.duration_seconds) AS avg FROM events e {join} WHERE {where} "
        f"AND e.event_type='restore_success' AND e.duration_seconds IS NOT NULL", args).fetchone()
    totals["mean_recovery_seconds"] = round(avg["avg"], 1) if avg and avg["avg"] is not None else None
    weekly = conn.execute(
        f"SELECT strftime('%Y-W%W', e.created_at) AS week, "
        f"SUM(e.event_type IN ('crash_detected','freeze_detected')) AS crashes, "
        f"SUM(e.event_type = 'restore_success') AS recoveries "
        f"FROM events e {join} WHERE {where} GROUP BY week ORDER BY week", args).fetchall()

    group_where = where
    group_args = list(args)
    if class_group and class_group != "All":
        group_where += " AND v.class_group = ?"
        group_args.append(class_group)
    per_vm = conn.execute(
        f"SELECT v.vm_id, v.vm_name, v.class_group, "
        f"SUM(e.event_type IN ('crash_detected','freeze_detected')) AS crashes, "
        f"SUM(e.event_type = 'restore_success') AS recoveries, "
        f"SUM(e.event_type = 'snapshot_taken') AS snapshots, "
        f"AVG(CASE WHEN e.event_type='restore_success' THEN e.duration_seconds END) AS mean_seconds "
        f"FROM events e {join} WHERE {group_where} AND e.vm_id IS NOT NULL "
        f"GROUP BY v.vm_id ORDER BY crashes DESC, v.vm_name", group_args).fetchall()
    return {"totals": totals, "weekly": [dict(r) for r in weekly],
            "per_vm": [dict(r) for r in per_vm]}
