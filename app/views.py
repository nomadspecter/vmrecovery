"""Web pages. Every page requires login; changing things also requires the right role and a CSRF token."""
import csv
import hmac
import io
import logging
import secrets
import time
from collections import defaultdict, deque
from datetime import date, timedelta
from functools import wraps
from pathlib import Path

from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, services
from .vbox import VBoxError

bp = Blueprint("main", __name__)

log = logging.getLogger("vmrecovery")

_failed_logins = defaultdict(deque)           # ip -> timestamps of recent failures


# ------------------------------------------------------------------ plumbing
def settings():
    return current_app.extensions["settings"]


def vbox():
    return current_app.extensions["vbox"]


class _BoundedLock:
    """The VirtualBox lock, acquired with a timeout.

    The lock is held for the whole of a VirtualBox command, so a command that
    never returns would freeze every page of the dashboard. Waiting a bounded
    time and then saying so is much better than a browser that spins forever.
    """

    def __init__(self, lock, timeout: float):
        self.lock, self.timeout = lock, timeout

    def __enter__(self):
        if not self.lock.acquire(timeout=self.timeout):
            raise VBoxError("Another VirtualBox operation is still running. "
                            "Please try again in a moment.")
        return self.lock

    def __exit__(self, *exc_info):
        self.lock.release()
        return False


def vbox_lock():
    return _BoundedLock(current_app.extensions["lock"],
                        getattr(settings(), "vbox_lock_timeout", 30))


def get_db():
    if "db" not in g:
        g.db = db.connect(settings().db_path)
    return g.db


@bp.teardown_app_request
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@bp.before_app_request
def load_user_and_check_csrf():
    g.user = None
    uid = session.get("user_id")
    if uid:
        g.user = get_db().execute("SELECT user_id, username, role FROM users WHERE user_id=?",
                                  (uid,)).fetchone()
        if g.user is None:
            session.clear()
    if request.method == "POST":
        sent, real = request.form.get("csrf_token", ""), session.get("csrf", "")
        if not real or not hmac.compare_digest(sent, real):
            abort(400, "Invalid or missing security token. Reload the page and try again.")


def flash_error(message):
    """Show an error on the page *and* write it to the log.

    A failed action used to leave no trace: the message went to the next page
    and nowhere else, so the log stayed empty while the dashboard kept saying
    it could not do the thing.
    """
    log.warning("Action failed: %s", message)
    flash(message, "error")


@bp.app_context_processor
def inject():
    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]
    return {"csrf_token": csrf_token, "user": g.get("user"), "simulate": settings().simulate,
            "pill": lambda s: {"running": "run", "frozen": "frz", "crashed": "crash",
                               "restoring": "frz", "paused": "off", "suspect": "frz",
                               "needs_admin": "crash", "recovery_failed": "crash",
                               "recovered": "run", "unknown": "off", "busy": "frz",
                   "needs_admin": "crash"}.get(s, "off")}


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if g.user is None:
            return redirect(url_for("main.login"))
        return fn(*a, **kw)
    return wrapper


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def wrapper(*a, **kw):
            if g.user["role"] not in roles:
                abort(403, "Your role is not allowed to do that.")
            return fn(*a, **kw)
        return wrapper
    return deco


def to_int(name, default):
    try:
        return int(request.form.get(name, default))
    except (TypeError, ValueError):
        return default


def vm_or_404(vm_id):
    vm = services.get_vm(get_db(), vm_id)
    if vm is None:
        abort(404)
    return vm


def is_student():
    return g.user is not None and g.user["role"] == "student"


# ------------------------------------------------------------------ login & auth
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr or "?"
        now = time.time()
        window = settings().login_window_seconds
        max_failures = settings().login_max_failures
        recent = _failed_logins[ip]
        while recent and now - recent[0] > window:
            recent.popleft()
        if len(recent) >= max_failures:
            flash_error("Too many failed attempts. Wait a few minutes and try again.")
            return render_template("login.html"), 429
        row = get_db().execute("SELECT * FROM users WHERE username=?",
                               (request.form.get("username", "").strip(),)).fetchone()
        if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = row["user_id"]
            session["csrf"] = secrets.token_hex(16)
            session.permanent = True
            get_db().execute("UPDATE users SET last_login_at=? WHERE user_id=?",
                             (services.ts(services.now_local()), row["user_id"]))
            get_db().commit()
            return redirect(url_for("main.dashboard"))
        recent.append(now)
        flash_error("Invalid username or password.")
    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not username:
            flash_error("Username is required.")
            return render_template("register.html")
        if len(username) < 3:
            flash_error("Username must be at least 3 characters.")
            return render_template("register.html")
        if len(password) < 8:
            flash_error("Password must be at least 8 characters.")
            return render_template("register.html")
        if password != confirm:
            flash_error("Passwords do not match.")
            return render_template("register.html")
        conn = get_db()
        existing = conn.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
        if existing:
            flash_error("That username is already taken. Please choose another.")
            return render_template("register.html")
        try:
            user_id = services.create_user(conn, username, password, role="student")
            services.log_event(conn, "user_registered", None, user_id,
                               f"Student account '{username}' registered", "Success")
            flash("Registration successful! You can now log in.", "ok")
            return redirect(url_for("main.login"))
        except Exception as exc:
            flash_error(f"Registration failed: {exc}")
    return render_template("register.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Let any signed-in user change their own password."""
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        row = get_db().execute("SELECT * FROM users WHERE user_id=?", (g.user["user_id"],)).fetchone()
        if not check_password_hash(row["password_hash"], current):
            flash_error("Your current password is not correct.")
        else:
            try:
                services.reset_user_password(get_db(), g.user["user_id"], new)
            except ValueError as exc:
                flash_error(str(exc))
            else:
                services.log_event(get_db(), "password_changed", None, g.user["user_id"],
                                   f"{g.user['username']} changed their password", "Success")
                flash("Your password was changed.", "ok")
                return redirect(url_for("main.account"))
    return render_template("account.html")



# ------------------------------------------------------------------ dashboard
@bp.route("/")
@login_required
def dashboard():
    conn = get_db()
    if g.user["role"] == "student":
        student_vms = services.get_student_vms(conn, g.user["user_id"])
        student_requests = services.list_vm_requests(conn, user_id=g.user["user_id"])
        worker_state, worker_stale = _worker_state()
        student_counts = {
            "assigned": len(student_vms),
            "running": sum(1 for v in student_vms if v["status"] == "running"),
            "needs_attention": sum(1 for v in student_vms if v["status"] in ("frozen", "crashed", "needs_admin")),
            "pending_requests": sum(1 for r in student_requests if r["status"] in ("pending", "creating")),
        }
        monitoring_active = bool(worker_state and worker_state.get("running") and not worker_stale)
        return render_template(
            "dashboard.html",
            student_vms=student_vms,
            student_requests=student_requests[:5],
            student_counts=student_counts,
            monitoring_active=monitoring_active,
            worker_last_cycle=worker_state.get("last_cycle") if worker_state else None,
        )
    data = services.dashboard_data(conn, settings=settings(), vbox=vbox())
    pending = services.pending_requests(conn) if g.user["role"] == "admin" else []
    return render_template("dashboard.html", pending=pending, **data)


@bp.route("/sessions/start", methods=["POST"])
@role_required("admin", "trainer")
def start_session():
    group = request.form.get("class_group", "").strip()
    try:
        with vbox_lock():
            result = services.start_session(get_db(), vbox(), group, g.user["user_id"])
    except (ValueError, VBoxError) as exc:
        flash_error(str(exc))
        return redirect(url_for("main.dashboard"))
    if result["already_active"]:
        message = (f"Session for {group} is already active (started {result['session_started_at']}). "
                   f"{result['started']} VM(s) started/restarted, {result['already_running']} already running; "
                   f"{result['already_protected']} VM(s) already protected, "
                   f"{result['snapshots']} new pre-session snapshot(s) taken.")
    else:
        message = (f"Session started for {group}: {result['started']} VM(s) started, "
                   f"{result['already_running']} already running, "
                   f"{result['snapshots']} pre-session snapshot(s) taken, "
                   f"{result['skipped']} skipped.")
    if result["failed"]:
        reasons = "; ".join(f"{name}: {err}" for name, err in result["failed"][:3])
        flash_error(f"{message} {len(result['failed'])} failed - {reasons}")
    else:
        flash(message, "ok")
    return redirect(url_for("main.dashboard"))


@bp.route("/sessions/end", methods=["POST"])
@role_required("admin", "trainer")
def end_session():
    group = request.form.get("class_group", "").strip()
    power_off = request.form.get("power_off") == "on"
    try:
        with vbox_lock():
            result = services.end_session(get_db(), vbox(), group, g.user["user_id"],
                                          power_off=power_off)
    except (ValueError, VBoxError) as exc:
        flash_error(str(exc))
        return redirect(url_for("main.dashboard"))
    message = (f"Session ended for {group}: {result['snapshots']} post-session snapshot(s) taken, "
               f"{result['powered_off']} VM(s) powered off.")
    if result["failed"]:
        reasons = "; ".join(f"{name}: {err}" for name, err in result["failed"][:3])
        flash_error(f"{message} {len(result['failed'])} failed - {reasons}")
    else:
        flash(message, "ok")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ VM registry & templates (admin)
@bp.route("/vms")
@role_required("admin")
def vms():
    conn = get_db()
    registered = services.list_vms(conn)
    templates = services.list_templates(conn)
    students = [u for u in services.list_users(conn) if u["role"] == "student"]
    known = {v["vbox_uuid"] for v in registered}
    available, vbox_error = [], None
    try:
        available = [(n, u) for n, u in vbox().list_vms() if u not in known]
    except VBoxError as exc:
        vbox_error = str(exc)
    return render_template("vms.html", vms=registered, available=available,
                           templates=templates, students=students, vbox_error=vbox_error)


@bp.route("/vms/add", methods=["POST"])
@role_required("admin")
def vms_add():
    choice = request.form.get("vbox_choice", "")
    name, _, uuid = choice.partition("|")
    if not uuid:
        name, uuid = request.form.get("vm_name", ""), request.form.get("vbox_uuid", "")
    student_id = request.form.get("assigned_student_id")
    student_id = int(student_id) if student_id else None
    try:
        is_template = request.form.get("is_template") == "on"
        services.register_vm(get_db(), name, uuid, request.form.get("class_group", "General"),
                             to_int("interval_minutes", 30), to_int("retention_count", 5),
                             request.form.get("pre_session") == "on", g.user["user_id"],
                             request.form.get("heartbeat_property"), is_template=is_template,
                             assigned_student_id=student_id)
        flash(f"{name} registered.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(url_for("main.vms"))


@bp.route("/vms/direct-create", methods=["POST"])
@role_required("admin")
def vms_direct_create():
    name = request.form.get("name", "").strip()
    tpl_uuid = request.form.get("template_uuid", "").strip()
    group = request.form.get("class_group", "General").strip()
    clone_type = request.form.get("clone_type", "linked")
    student_id = request.form.get("assigned_student_id")
    student_id = int(student_id) if student_id else None
    try:
        with vbox_lock():
            vm_id = services.direct_create_vm(get_db(), vbox(), name, group, tpl_uuid,
                                               clone_type=clone_type, user_id=g.user["user_id"])
            if student_id:
                services.assign_student(get_db(), vm_id, student_id, admin_user_id=g.user["user_id"])
        flash(f"VM '{name}' cloned from template and registered.", "ok")
    except (ValueError, VBoxError) as exc:
        flash_error(str(exc))
    return redirect(url_for("main.vms"))


@bp.route("/vms/<int:vm_id>/assign", methods=["POST"])
@role_required("admin")
def vm_assign(vm_id):
    vm = vm_or_404(vm_id)
    student_id = request.form.get("assigned_student_id")
    student_id = int(student_id) if student_id else None
    conn = get_db()
    try:
        services.assign_student(conn, vm_id, student_id, admin_user_id=g.user["user_id"])
        if student_id:
            student = conn.execute("SELECT username FROM users WHERE user_id = ?", (student_id,)).fetchone()
            sname = student["username"] if student else str(student_id)
            flash(f"VM '{vm['vm_name']}' assigned to student '{sname}'.", "ok")
        else:
            flash(f"VM '{vm['vm_name']}' is now unassigned.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(request.referrer or url_for("main.vms"))


@bp.route("/vms/<int:vm_id>/toggle-template", methods=["POST"])
@role_required("admin")
def vm_toggle_template(vm_id):
    vm = vm_or_404(vm_id)
    try:
        with vbox_lock():
            services.set_vm_template(get_db(), vm_id, not vm["is_template"], vbox(),
                                     user_id=g.user["user_id"])
        flash(f"Updated template status for {vm['vm_name']}.", "ok")
    except VBoxError as exc:
        flash_error(f"Template status saved, but the baseline snapshot failed: {exc}")
    return redirect(url_for("main.vms"))


@bp.route("/vms/<int:vm_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def vm_edit(vm_id):
    vm = vm_or_404(vm_id)
    conn = get_db()
    if request.method == "POST":
        try:
            student_id = request.form.get("assigned_student_id")
            student_id = int(student_id) if student_id else None
            services.update_vm(conn, vm_id, request.form.get("class_group", "General"),
                               to_int("interval_minutes", vm["interval_minutes"]),
                               to_int("retention_count", vm["retention_count"]),
                               request.form.get("pre_session") == "on",
                               request.form.get("heartbeat_property"),
                               is_template=request.form.get("is_template") == "on",
                               assigned_student_id=student_id,
                               user_id=g.user["user_id"])
            flash("Policy updated.", "ok")
            return redirect(url_for("main.vms"))
        except ValueError as exc:
            flash_error(str(exc))
    students = [u for u in services.list_users(conn) if u["role"] == "student"]
    return render_template("vm_edit.html", vm=vm, students=students)


@bp.route("/vms/<int:vm_id>/delete", methods=["POST"])
@role_required("admin")
def vm_delete(vm_id):
    vm = vm_or_404(vm_id)
    delete_from_vbox = request.form.get("delete_from_vbox") == "on"
    try:
        # Deleting a machine talks to VirtualBox, so it waits for the lock
        # like every other action does. Without it a delete could run while
        # the worker is taking a snapshot of the same machine.
        with vbox_lock():
            services.remove_vm(get_db(), vm_id, g.user["user_id"], vbox=vbox(),
                               delete_from_vbox=delete_from_vbox)
    except ValueError as exc:
        flash_error(str(exc))
        return redirect(url_for("main.vms"))
    except VBoxError as exc:
        flash_error(f"VirtualBox refused the request: {exc}")
        return redirect(url_for("main.vms"))
    if delete_from_vbox:
        flash(f"{vm['vm_name']} was deleted from VirtualBox and removed from the system.", "ok")
    else:
        flash("VM removed from the system. It was not deleted from VirtualBox.", "ok")
    return redirect(url_for("main.vms"))


# ------------------------------------------------------------------ power control
@bp.route("/vms/<int:vm_id>/power", methods=["POST"])
@role_required("admin", "trainer")
def vm_power(vm_id):
    """Start, stop, pause, resume or reset one virtual machine."""
    vm_or_404(vm_id)
    action = request.form.get("action", "").strip().lower()
    try:
        with vbox_lock():
            message = services.power_action(get_db(), vbox(), vm_id, action, g.user["user_id"])
        flash(message, "ok")
    except ValueError as exc:
        flash_error(str(exc))
    except VBoxError as exc:
        flash_error(f"VirtualBox refused the request: {exc}")
    return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/vms/bulk", methods=["POST"])
@role_required("admin", "trainer")
def vms_bulk():
    """Apply one action to a selection of machines."""
    action = request.form.get("action", "").strip().lower()
    ids = [int(i) for i in request.form.getlist("vm_ids") if str(i).isdigit()]
    if not ids:
        flash_error("Select at least one virtual machine first.")
        return redirect(url_for("main.dashboard"))
    try:
        with vbox_lock():
            summary = services.bulk_power_action(get_db(), vbox(), ids, action, g.user["user_id"])
    except ValueError as exc:
        flash_error(str(exc))
        return redirect(url_for("main.dashboard"))
    except VBoxError as exc:
        flash_error(f"VirtualBox refused the request: {exc}")
        return redirect(url_for("main.dashboard"))
    if summary["done"]:
        flash(f"{action} finished for {len(summary['done'])} machine(s).", "ok")
    if summary["failed"]:
        reasons = "; ".join(f"{name}: {err}" for name, err in summary["failed"][:3])
        flash_error(f"{len(summary['failed'])} machine(s) failed - {reasons}")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ snapshots and restore
@bp.route("/vms/<int:vm_id>")
@role_required("admin", "trainer")
def vm_detail(vm_id):
    """One page with everything an operator needs about a single machine."""
    vm = vm_or_404(vm_id)
    conn = get_db()
    events = services.list_events(conn, vm_id=vm_id, limit=20)
    return render_template("vm_detail.html", vm=vm, events=events,
                           backups=services.list_backups(conn, vm_id),
                           snaps=services.list_snapshots(conn, vm_id))


@bp.route("/vms/<int:vm_id>/snapshots")
@role_required("admin", "trainer")
def snapshots(vm_id):
    vm = vm_or_404(vm_id)
    return render_template("snapshots.html", vm=vm, snaps=services.list_snapshots(get_db(), vm_id))


@bp.route("/vms/<int:vm_id>/snapshot", methods=["POST"])
@role_required("admin", "trainer")
def snapshot_now(vm_id):
    vm = vm_or_404(vm_id)
    try:
        with vbox_lock():
            name = services.take_snapshot(get_db(), vbox(), vm, "manual", user_id=g.user["user_id"])
    except (VBoxError, ValueError) as exc:
        flash_error(f"Snapshot failed: {exc}")
        return redirect(request.referrer or url_for("main.dashboard"))
    if name:
        flash(f"Snapshot {name} taken.", "ok")
    else:
        flash_error("Snapshot failed. See the event log.")
    return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/vms/<int:vm_id>/restore", methods=["POST"])
@role_required("admin")
def restore(vm_id):
    vm = vm_or_404(vm_id)
    snap = get_db().execute("SELECT * FROM snapshots WHERE snapshot_id=? AND vm_id=?",
                            (to_int("snapshot_id", 0), vm_id)).fetchone()
    if snap is None:
        # A restore without a valid snapshot of this machine is a mistake in
        # the form, not a missing page. Say which snapshot to pick.
        flash_error("Choose one of this machine's snapshots to restore it to.")
        return redirect(url_for("main.vm_detail", vm_id=vm_id))
    try:
        with vbox_lock():
            ok = services.recover(get_db(), vbox(), vm, snapshot=snap, user_id=g.user["user_id"])
    except (VBoxError, ValueError) as exc:
        flash_error(f"Restore failed: {exc}")
        return redirect(url_for("main.vm_detail", vm_id=vm_id))
    flash(f"{vm['vm_name']} restored to {snap['snapshot_name']}." if ok else "Restore failed. See the event log.",
          "ok" if ok else "error")
    return redirect(url_for("main.dashboard"))


@bp.route("/vms/<int:vm_id>/request-restore", methods=["POST"])
@role_required("trainer", "admin", "student")
def request_restore(vm_id):
    vm = vm_or_404(vm_id)
    services.request_restore(get_db(), vm_id, g.user["user_id"])
    flash("Restore requested. The administrator has been notified on the dashboard.", "ok")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ independent backups (.ova)
@bp.route("/vms/<int:vm_id>/backups")
@role_required("admin", "trainer")
def backups(vm_id):
    vm = vm_or_404(vm_id)
    b_list = services.list_backups(get_db(), vm_id)
    return render_template("backups.html", vm=vm, backups=b_list, backup_dir=settings().backup_dir)


@bp.route("/vms/<int:vm_id>/backups/create", methods=["POST"])
@role_required("admin", "trainer")
def backup_create(vm_id):
    vm = vm_or_404(vm_id)
    try:
        with vbox_lock():
            services.create_backup(get_db(), vbox(), vm, settings().backup_dir,
                                   user_id=g.user["user_id"],
                                   retention_count=settings().backup_retention_count)
        flash("Independent OVA backup created successfully.", "ok")
    except Exception as exc:
        flash_error(f"Backup failed: {exc}")
    return redirect(url_for("main.backups", vm_id=vm_id))


@bp.route("/vms/<int:vm_id>/backups/<int:backup_id>/restore", methods=["POST"])
@role_required("admin")
def backup_restore(vm_id, backup_id):
    vm = vm_or_404(vm_id)
    try:
        with vbox_lock():
            ok = services.restore_backup(get_db(), vbox(), vm, backup_id, user_id=g.user["user_id"])
        if ok:
            flash(f"{vm['vm_name']} successfully restored from appliance backup.", "ok")
        else:
            flash_error("Restore from backup failed. See event log.")
    except Exception as exc:
        flash_error(str(exc))
    return redirect(url_for("main.backups", vm_id=vm_id))


@bp.route("/vms/<int:vm_id>/backups/<int:backup_id>/delete", methods=["POST"])
@role_required("admin")
def backup_delete(vm_id, backup_id):
    vm_or_404(vm_id)
    conn = get_db()
    b = conn.execute("SELECT * FROM backups WHERE backup_id=? AND vm_id=?", (backup_id, vm_id)).fetchone()
    if b:
        try:
            Path(b["file_path"]).unlink(missing_ok=True)
        except OSError:
            pass
        conn.execute("DELETE FROM backups WHERE backup_id=?", (backup_id,))
        conn.commit()
        services.log_event(conn, "backup_deleted", vm_id, g.user["user_id"],
                           f"Deleted backup {b['backup_name']}", "Success")
        flash("Backup deleted.", "ok")
    return redirect(url_for("main.backups", vm_id=vm_id))


# ------------------------------------------------------------------ VM requests & approval
@bp.route("/requests")
@role_required("admin", "trainer")
def requests_list():
    conn = get_db()
    uid = None if g.user["role"] == "admin" else g.user["user_id"]
    reqs = services.list_vm_requests(conn, user_id=uid)
    templates = services.list_templates(conn)
    return render_template("requests.html", requests=reqs, templates=templates)


@bp.route("/requests/new", methods=["POST"])
@role_required("admin", "trainer")
def request_new():
    choice = request.form.get("template_choice", "")
    uuid, _, name = choice.partition("|")
    req_name = request.form.get("requested_name", "")
    group = request.form.get("class_group", "General")
    mode = request.form.get("clone_type", "linked")
    try:
        services.request_vm(get_db(), g.user["user_id"], uuid, name, req_name, group, mode)
        flash("VM request submitted for administrator review.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(url_for("main.requests_list"))


@bp.route("/requests/<int:request_id>/approve", methods=["POST"])
@role_required("admin")
def request_approve(request_id):
    try:
        with vbox_lock():
            services.approve_vm_request(get_db(), vbox(), request_id, g.user["user_id"])
        flash("Request approved. Virtual machine created and registered.", "ok")
    except Exception as exc:
        flash_error(f"Approval failed: {exc}")
    return redirect(url_for("main.requests_list"))


@bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@role_required("admin")
def request_reject(request_id):
    reason = request.form.get("reason", "").strip()
    try:
        services.reject_vm_request(get_db(), request_id, g.user["user_id"], reason)
        flash("Request rejected.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(url_for("main.requests_list"))


# ------------------------------------------------------------------ user management (admin)
@bp.route("/users")
@role_required("admin")
def users_page():
    conn = get_db()
    return render_template("users.html", users=services.list_users(conn), vms=services.list_vms(conn))


@bp.route("/users/create", methods=["POST"])
@role_required("admin")
def user_create():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    r = request.form.get("role", "trainer")
    try:
        services.create_user(get_db(), u, p, r)
        flash(f"User '{u}' created.", "ok")
    except (ValueError, Exception) as exc:
        flash_error(str(exc))
    return redirect(url_for("main.users_page"))


@bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@role_required("admin")
def user_reset_password(user_id):
    p = request.form.get("new_password", "")
    try:
        services.reset_user_password(get_db(), user_id, p)
        flash("Password updated.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(url_for("main.users_page"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def user_delete(user_id):
    try:
        services.delete_user(get_db(), user_id)
        flash("User deleted.", "ok")
    except ValueError as exc:
        flash_error(str(exc))
    return redirect(url_for("main.users_page"))


@bp.route("/users/<int:user_id>/assign-vm", methods=["POST"])
@role_required("admin")
def user_assign_vm(user_id):
    vm_id = request.form.get("vm_id")
    vm_id = int(vm_id) if vm_id else None
    conn = get_db()
    if vm_id:
        try:
            services.assign_student(conn, vm_id, user_id, admin_user_id=g.user["user_id"])
            vm = services.get_vm(conn, vm_id)
            flash(f"VM '{vm['vm_name']}' assigned successfully.", "ok")
        except ValueError as exc:
            flash_error(str(exc))
    return redirect(url_for("main.users_page"))


# ------------------------------------------------------------------ system health
def _worker_state():
    """Worker status plus whether its last cycle is older than expected."""
    worker = current_app.extensions.get("worker")
    if worker is None:
        return None, False
    state = worker.status()
    stale = False
    last = state["last_cycle"] or state["started_at"]
    if state["running"]:
        try:
            age = (services.now_local() - services.parse_ts(last)).total_seconds() if last else None
            stale = age is not None and age > settings().check_seconds * 3
        except (TypeError, ValueError):
            stale = True
    return state, stale


@bp.route("/system")
@role_required("admin")
def system_page():
    from . import notifier
    state, stale = _worker_state()
    conn = get_db()
    return render_template("system.html", health=services.check_vbox_health(vbox()),
                           settings=settings(), worker=state, worker_stale=stale,
                           channels=notifier.enabled_channels(),
                           notifications=notifier.list_notifications(conn, limit=15),
                           disk=services.check_disk_space(settings().backup_dir,
                                                          settings().disk_min_free_gb,
                                                          settings().disk_min_free_pct))


@bp.route("/healthz")
def healthz():
    """Unauthenticated liveness/readiness probe for systemd, uptime checks, or a proxy."""
    status = 200
    checks = {"app": "ok"}
    try:
        get_db().execute("SELECT 1").fetchone()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
        status = 503

    disk = services.check_disk_space(settings().backup_dir, settings().disk_min_free_gb,
                                     settings().disk_min_free_pct)
    checks["disk"] = {"free_gb": disk["free_gb"], "low": disk["is_low"]}

    state, stale = _worker_state()
    if state is None:
        checks["worker"] = {"running": False, "last_cycle": None}
        if settings().run_worker:
            status = 503
    else:
        checks["worker"] = {k: state[k] for k in ("running", "last_cycle", "cycles", "last_error")}
        if settings().run_worker and (not state["running"] or stale):
            status = 503
    return jsonify(status="ok" if status == 200 else "degraded", checks=checks), status


# ------------------------------------------------------------------ demo helpers (simulation only)
@bp.route("/demo/<action>/<int:vm_id>", methods=["POST"])
@role_required("admin")
def demo(action, vm_id):
    if not settings().simulate or action not in ("crash", "freeze"):
        abort(404)
    vm = vm_or_404(vm_id)
    conn = get_db()
    with vbox_lock():
        getattr(vbox(), action)(vm["vbox_uuid"])
        # Ensure admin_paused never suppresses recovery and surface the fault immediately
        status = "crashed" if action == "crash" else "frozen"
        conn.execute(
            "UPDATE vms SET status=?, fail_count=1, admin_paused=0, last_checked=? WHERE vm_id=?",
            (status, services.ts(services.now_local()), vm_id),
        )
        conn.commit()
    flash(f"Simulated {action} on {vm['vm_name']}. Auto-recovery will restore it on the next monitor cycle (~10s).", "ok")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ logs and reports
@bp.route("/events")
@login_required
def events():
    vm_id = request.args.get("vm_id", type=int)
    etype = request.args.get("event_type") or None
    day = request.args.get("day") or None
    page = max(request.args.get("page", default=1, type=int), 1)
    per_page = min(max(request.args.get("per_page", default=50, type=int), 10), 200)
    conn = get_db()
    student_id = g.user["user_id"] if is_student() else None
    total = services.count_events(conn, vm_id, etype, day, student_user_id=student_id)
    rows = services.list_events(conn, vm_id, etype, day, limit=per_page,
                                offset=(page - 1) * per_page, student_user_id=student_id)
    types = [r["event_type"] for r in conn.execute("SELECT DISTINCT event_type FROM events ORDER BY 1")]
    vms = services.get_student_vms(conn, g.user["user_id"]) if is_student() else services.list_vms(conn)
    return render_template("events.html", events=rows, vms=vms, types=types,
                           f_vm=vm_id, f_type=etype, f_day=day or "",
                           page=page, per_page=per_page, total=total,
                           pages=max(1, (total + per_page - 1) // per_page))


@bp.route("/events.csv")
@login_required
def events_csv():
    """Download the filtered event log as CSV."""
    vm_id = request.args.get("vm_id", type=int)
    etype = request.args.get("event_type") or None
    day = request.args.get("day") or None
    conn = get_db()
    student_id = g.user["user_id"] if is_student() else None
    rows = services.list_events(conn, vm_id, etype, day, limit=100000,
                                student_user_id=student_id)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["event_id", "created_at", "event_type", "vm", "details", "result",
                     "duration_seconds", "user"])
    for r in rows:
        writer.writerow([r["event_id"], r["created_at"], r["event_type"], r["vm_name"] or "",
                         r["details"], r["result"], r["duration_seconds"] or "",
                         r["username"] or "system"])
    return current_app.response_class(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=vmrecovery-events.csv"})


@bp.route("/reports")
@role_required("admin")
def reports():
    today = date.today()
    start = request.args.get("start") or (today - timedelta(days=30)).isoformat()
    end = request.args.get("end") or today.isoformat()
    group = request.args.get("class_group", "All")
    conn = get_db()
    groups = sorted({v["class_group"] for v in services.list_vms(conn)})
    result = services.report(conn, start, end, group)
    peak = max([1] + [max(w["crashes"] or 0, w["recoveries"] or 0) for w in result["weekly"]])
    return render_template("reports.html", r=result, start=start, end=end, group=group,
                           groups=groups, peak=peak)


# ------------------------------------------------------------------ settings
SETTINGS_SECTIONS = (
    ("Monitoring", (
        ("check_seconds", "Check interval (seconds)", "How often every machine is checked."),
        ("fail_threshold", "Failure threshold", "Bad checks in a row before a machine is "
                                                "treated as failed."),
        ("heartbeat_timeout", "Heartbeat timeout (seconds)", "Seconds without a guest "
                                                              "heartbeat before a running "
                                                              "machine counts as frozen."),
        ("max_restores_per_hour", "Maximum automatic restores per hour", "Stops endless "
                                                                        "restore loops."),
    )),
    ("Snapshots and backups", (
        ("backup_retention_count", "Appliance backups kept per machine", "Older .ova exports "
                                                                         "are deleted."),
        ("backup_dir", "Backup directory", "Where independent .ova exports are written."),
        ("db_backup_dir", "Database backup directory", "Where application database "
                                                       "backups are written."),
        ("db_backup_keep", "Database backups kept", "How many rotated database backups "
                                                    "to keep."),
    )),
    ("Storage safeguards", (
        ("disk_min_free_gb", "Minimum free storage (GB)", "Warn when the host has less "
                                                         "free space than this."),
        ("disk_min_free_pct", "Minimum free storage (%)", "Warn when the host has less "
                                                          "free space than this."),
    )),
    ("Sessions and access", (
        ("session_hours", "Session length (hours)", "How long a login lasts."),
        ("login_max_failures", "Failed logins before lockout", "Per IP address."),
        ("login_window_seconds", "Login lockout window (seconds)", "How long the lockout "
                                                                  "lasts."),
        ("event_retention_days", "Event retention (days)", "0 keeps every event forever."),
    )),
    ("Email notifications", (
        ("notify_email_enabled", "Email notifications", "1 to send them, 0 to switch off."),
        ("smtp_host", "SMTP host", "The mail server to relay through."),
        ("smtp_port", "SMTP port", "587 for STARTTLS, 25 for plain."),
        ("smtp_user", "SMTP user", "Leave empty for an open relay."),
        ("smtp_password", "SMTP password", "Stored encrypted-at-rest only in the database "
                                            "file, which is excluded from git."),
        ("smtp_from", "Sender address", "The From header on outgoing mail."),
        ("smtp_to", "Recipients", "Comma separated list of people to notify."),
        ("smtp_use_tls", "Use STARTTLS", "1 to upgrade the connection."),
    )),
    ("Webhook notifications", (
        ("notify_webhook_enabled", "Webhook notifications", "1 to send them, 0 to switch off."),
        ("webhook_url", "Webhook URL", "A chat or automation endpoint that accepts JSON."),
        ("webhook_secret", "Webhook secret", "Signs the payload with X-VMRecovery-Signature."),
    )),
)


@bp.route("/settings", methods=["GET", "POST"])
@role_required("admin")
def settings_page():
    """Runtime configuration. Values here win over the environment files."""
    conn = get_db()
    if request.method == "POST":
        key = request.form.get("key", "")
        try:
            services.set_override(conn, key, request.form.get("value", ""), g.user["user_id"])
        except ValueError as exc:
            flash_error(str(exc))
        else:
            flash(f"{key} updated. The change is live.", "ok")
        return redirect(url_for("main.settings_page"))

    overrides = services.all_overrides(conn)
    effective = settings()
    values = {}
    for _, entries in SETTINGS_SECTIONS:
        for key, _, _ in entries:
            values[key] = overrides.get(key, getattr(effective, key, ""))
    return render_template("settings.html", sections=SETTINGS_SECTIONS, values=values,
                           overrides=overrides, effective=effective,
                           api_token_set=bool(getattr(effective, "api_token", "")))


@bp.route("/settings/reset", methods=["POST"])
@role_required("admin")
def settings_reset():
    key = request.form.get("key", "")
    try:
        services.clear_override(get_db(), key, g.user["user_id"])
    except ValueError as exc:
        flash_error(str(exc))
    else:
        services.apply_overrides(get_db(), settings())
        flash(f"{key} was reset to the configured default.", "ok")
    return redirect(url_for("main.settings_page"))


@bp.route("/settings/api-token", methods=["POST"])
@role_required("admin")
def settings_api_token():
    """Generate a fresh API token. The old one stops working immediately."""
    token = secrets.token_urlsafe(32)
    services.set_override(get_db(), "api_token", token, g.user["user_id"])
    services.apply_overrides(get_db(), settings())
    flash(f"New API token generated: {token}", "ok")
    return redirect(url_for("main.settings_page"))


@bp.route("/settings/test-notification", methods=["POST"])
@role_required("admin")
def settings_test_notification():
    from . import notifier
    conn = get_db()
    services.apply_overrides(conn, settings())
    notifier.configure(settings())
    results = notifier.send(conn, settings(), "VMRecovery test notification",
                             "This is a test message from the VM Recovery System. "
                             "If you received it, notifications are working.")
    if not results:
        flash_error("No notification channel is enabled. Configure email or a webhook first.")
    elif any(r["status"] == "sent" for r in results):
        flash("Test notification sent.", "ok")
    else:
        errors = "; ".join(r.get("error", "unknown error") for r in results)
        flash_error(f"The test notification could not be delivered: {errors}")
    return redirect(url_for("main.settings_page"))
