"""Web pages. Every page requires login; changing things also requires the right role and a CSRF token."""
import hmac
import secrets
import time
from collections import defaultdict, deque
from datetime import date, timedelta
from functools import wraps
from pathlib import Path

from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

from . import db, services
from .vbox import VBoxError

bp = Blueprint("main", __name__)

_failed_logins = defaultdict(deque)           # ip -> timestamps of recent failures
MAX_FAILS, WINDOW = 5, 300                    # 5 failures per 5 minutes


# ------------------------------------------------------------------ plumbing
def settings():
    return current_app.extensions["settings"]


def vbox():
    return current_app.extensions["vbox"]


def vbox_lock():
    return current_app.extensions["lock"]


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


@bp.app_context_processor
def inject():
    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]
    return {"csrf_token": csrf_token, "user": g.get("user"), "simulate": settings().simulate,
            "pill": lambda s: {"running": "run", "frozen": "frz", "crashed": "crash",
                               "restoring": "frz"}.get(s, "off")}


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


# ------------------------------------------------------------------ login & auth
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr or "?"
        now = time.time()
        recent = _failed_logins[ip]
        while recent and now - recent[0] > WINDOW:
            recent.popleft()
        if len(recent) >= MAX_FAILS:
            flash("Too many failed attempts. Wait a few minutes and try again.", "error")
            return render_template("login.html"), 429
        row = get_db().execute("SELECT * FROM users WHERE username=?",
                               (request.form.get("username", "").strip(),)).fetchone()
        if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = row["user_id"]
            session["csrf"] = secrets.token_hex(16)
            return redirect(url_for("main.dashboard"))
        recent.append(now)
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.login"))


# ------------------------------------------------------------------ dashboard
@bp.route("/")
@login_required
def dashboard():
    conn = get_db()
    if g.user["role"] == "student":
        student_vms = services.get_student_vms(conn, g.user["user_id"])
        return render_template("dashboard.html", student_vms=student_vms)
    data = services.dashboard_data(conn, settings=settings())
    pending = services.pending_requests(conn) if g.user["role"] == "admin" else []
    return render_template("dashboard.html", pending=pending, **data)


@bp.route("/sessions/start", methods=["POST"])
@role_required("admin", "trainer")
def start_session():
    group = request.form.get("class_group", "")
    with vbox_lock():
        taken, skipped = services.start_session(get_db(), vbox(), group, g.user["user_id"])
    flash(f"Session started for {group}: {taken} pre-session snapshot(s) taken, {skipped} skipped.", "ok")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ VM registry & templates (admin)
@bp.route("/vms")
@role_required("admin")
def vms():
    conn = get_db()
    registered = services.list_vms(conn)
    templates = services.list_templates(conn)
    known = {v["vbox_uuid"] for v in registered}
    available, vbox_error = [], None
    try:
        available = [(n, u) for n, u in vbox().list_vms() if u not in known]
    except VBoxError as exc:
        vbox_error = str(exc)
    return render_template("vms.html", vms=registered, available=available,
                           templates=templates, vbox_error=vbox_error)


@bp.route("/vms/add", methods=["POST"])
@role_required("admin")
def vms_add():
    choice = request.form.get("vbox_choice", "")
    name, _, uuid = choice.partition("|")
    if not uuid:
        name, uuid = request.form.get("vm_name", ""), request.form.get("vbox_uuid", "")
    try:
        is_template = request.form.get("is_template") == "on"
        services.register_vm(get_db(), name, uuid, request.form.get("class_group", "General"),
                             to_int("interval_minutes", 30), to_int("retention_count", 5),
                             request.form.get("pre_session") == "on", g.user["user_id"],
                             request.form.get("heartbeat_property"), is_template=is_template)
        flash(f"{name} registered.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("main.vms"))


@bp.route("/vms/direct-create", methods=["POST"])
@role_required("admin")
def vms_direct_create():
    name = request.form.get("name", "").strip()
    tpl_uuid = request.form.get("template_uuid", "").strip()
    group = request.form.get("class_group", "General").strip()
    clone_type = request.form.get("clone_type", "linked")
    try:
        with vbox_lock():
            vm_id = services.direct_create_vm(get_db(), vbox(), name, group, tpl_uuid,
                                               clone_type=clone_type, user_id=g.user["user_id"])
        flash(f"VM '{name}' cloned from template and registered.", "ok")
    except (ValueError, VBoxError) as exc:
        flash(str(exc), "error")
    return redirect(url_for("main.vms"))


@bp.route("/vms/<int:vm_id>/toggle-template", methods=["POST"])
@role_required("admin")
def vm_toggle_template(vm_id):
    vm = vm_or_404(vm_id)
    services.set_vm_template(get_db(), vm_id, not vm["is_template"], g.user["user_id"])
    flash(f"Updated template status for {vm['vm_name']}.", "ok")
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
            flash(str(exc), "error")
    students = [u for u in services.list_users(conn) if u["role"] == "student"]
    return render_template("vm_edit.html", vm=vm, students=students)


@bp.route("/vms/<int:vm_id>/delete", methods=["POST"])
@role_required("admin")
def vm_delete(vm_id):
    vm_or_404(vm_id)
    services.remove_vm(get_db(), vm_id, g.user["user_id"])
    flash("VM removed from the system. It was not deleted from VirtualBox.", "ok")
    return redirect(url_for("main.vms"))


# ------------------------------------------------------------------ snapshots and restore
@bp.route("/vms/<int:vm_id>/snapshots")
@role_required("admin", "trainer")
def snapshots(vm_id):
    vm = vm_or_404(vm_id)
    return render_template("snapshots.html", vm=vm, snaps=services.list_snapshots(get_db(), vm_id))


@bp.route("/vms/<int:vm_id>/snapshot", methods=["POST"])
@role_required("admin", "trainer")
def snapshot_now(vm_id):
    vm = vm_or_404(vm_id)
    with vbox_lock():
        name = services.take_snapshot(get_db(), vbox(), vm, "manual", user_id=g.user["user_id"])
    flash(f"Snapshot {name} taken." if name else "Snapshot failed. See the event log.", "ok" if name else "error")
    return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/vms/<int:vm_id>/restore", methods=["POST"])
@role_required("admin")
def restore(vm_id):
    vm = vm_or_404(vm_id)
    snap = get_db().execute("SELECT * FROM snapshots WHERE snapshot_id=? AND vm_id=?",
                            (to_int("snapshot_id", 0), vm_id)).fetchone()
    if snap is None:
        abort(404)
    with vbox_lock():
        ok = services.recover(get_db(), vbox(), vm, snapshot=snap, user_id=g.user["user_id"])
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
        flash(f"Backup failed: {exc}", "error")
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
            flash("Restore from backup failed. See event log.", "error")
    except Exception as exc:
        flash(str(exc), "error")
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
        flash(str(exc), "error")
    return redirect(url_for("main.requests_list"))


@bp.route("/requests/<int:request_id>/approve", methods=["POST"])
@role_required("admin")
def request_approve(request_id):
    try:
        with vbox_lock():
            services.approve_vm_request(get_db(), vbox(), request_id, g.user["user_id"])
        flash("Request approved. Virtual machine created and registered.", "ok")
    except Exception as exc:
        flash(f"Approval failed: {exc}", "error")
    return redirect(url_for("main.requests_list"))


@bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@role_required("admin")
def request_reject(request_id):
    reason = request.form.get("reason", "").strip()
    try:
        services.reject_vm_request(get_db(), request_id, g.user["user_id"], reason)
        flash("Request rejected.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("main.requests_list"))


# ------------------------------------------------------------------ user management (admin)
@bp.route("/users")
@role_required("admin")
def users_page():
    return render_template("users.html", users=services.list_users(get_db()))


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
        flash(str(exc), "error")
    return redirect(url_for("main.users_page"))


@bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@role_required("admin")
def user_reset_password(user_id):
    p = request.form.get("new_password", "")
    try:
        services.reset_user_password(get_db(), user_id, p)
        flash("Password updated.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("main.users_page"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def user_delete(user_id):
    try:
        services.delete_user(get_db(), user_id)
        flash("User deleted.", "ok")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("main.users_page"))


# ------------------------------------------------------------------ demo helpers (simulation only)
@bp.route("/demo/<action>/<int:vm_id>", methods=["POST"])
@role_required("admin")
def demo(action, vm_id):
    if not settings().simulate or action not in ("crash", "freeze"):
        abort(404)
    vm = vm_or_404(vm_id)
    getattr(vbox(), action)(vm["vbox_uuid"])
    flash(f"Simulated {action} on {vm['vm_name']}. The monitor will react within a minute.", "ok")
    return redirect(url_for("main.dashboard"))


# ------------------------------------------------------------------ logs and reports
@bp.route("/events")
@login_required
def events():
    vm_id = request.args.get("vm_id", type=int)
    etype = request.args.get("event_type") or None
    day = request.args.get("day") or None
    conn = get_db()
    rows = services.list_events(conn, vm_id, etype, day)
    types = [r["event_type"] for r in conn.execute("SELECT DISTINCT event_type FROM events ORDER BY 1")]
    return render_template("events.html", events=rows, vms=services.list_vms(conn), types=types,
                           f_vm=vm_id, f_type=etype, f_day=day or "")


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
