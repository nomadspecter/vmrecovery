"""Read-only JSON API for monitoring and automation.

The API is authenticated with a bearer token, not with a session cookie, so it
can be used by an uptime monitor, a chat bot, or a provisioning script. It
never changes anything: every endpoint is a GET.

    curl -H "Authorization: Bearer $VMR_API_TOKEN" http://127.0.0.1:5000/api/vms

Set the token with ``VMR_API_TOKEN=...`` or from the Settings page. While no
token is configured the API answers ``503`` and explains what to do, rather
than exposing anything by accident.
"""
import hmac
from datetime import date, timedelta

from flask import Blueprint, current_app, jsonify, request

from . import db, services

bp = Blueprint("api", __name__, url_prefix="/api")


def settings():
    return current_app.extensions["settings"]


def _token() -> str:
    return (getattr(settings(), "api_token", "") or "").strip()


def _presented_token() -> str:
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return request.headers.get("X-API-Token", "").strip()


@bp.before_request
def require_token():
    if request.endpoint == "api.health":      # the liveness probe stays open
        return None
    expected = _token()
    if not expected:
        return jsonify(error="The API is disabled. Set VMR_API_TOKEN or add an API token "
                             "on the Settings page."), 503
    if not hmac.compare_digest(_presented_token(), expected):
        return jsonify(error="A valid API token is required."), 401
    return None


def _conn():
    return db.connect(settings().db_path)


@bp.get("/health")
def health():
    """Liveness information. Does not require a token, so probes stay simple."""
    from . import notifier
    worker = current_app.extensions.get("worker")
    state = worker.status() if worker else {"running": False, "last_cycle": None, "cycles": 0}
    disk = services.check_disk_space(settings().backup_dir, settings().disk_min_free_gb,
                                     settings().disk_min_free_pct)
    return jsonify(
        status="ok",
        version=1,
        worker={"running": state.get("running"), "last_cycle": state.get("last_cycle"),
                "cycles": state.get("cycles")},
        disk={"free_gb": disk["free_gb"], "free_pct": disk["free_pct"], "low": disk["is_low"]},
        notifications={"channels": notifier.enabled_channels()},
        time=services.ts(services.now_local()))


@bp.get("/vms")
def vms():
    conn = _conn()
    try:
        rows = services.list_vms(conn)
        return jsonify(vms=[{
            "vm_id": r["vm_id"],
            "name": r["vm_name"],
            "uuid": r["vbox_uuid"],
            "class_group": r["class_group"],
            "status": r["status"],
            "fail_count": r["fail_count"],
            "is_template": bool(r["is_template"]),
            "student": r["student_username"],
            "interval_minutes": r["interval_minutes"],
            "retention_count": r["retention_count"],
            "last_snapshot": r["last_snapshot"],
            "last_checked": r["last_checked"],
            "backup_count": r["backup_count"],
        } for r in rows])
    finally:
        conn.close()


@bp.get("/vms/<int:vm_id>")
def vm_detail(vm_id):
    conn = _conn()
    try:
        vm = services.get_vm(conn, vm_id)
        if vm is None:
            return jsonify(error="Unknown virtual machine."), 404
        snapshots = [dict(r) for r in services.list_snapshots(conn, vm_id)]
        backups = [{"backup_id": r["backup_id"], "backup_name": r["backup_name"],
                    "size_bytes": r["size_bytes"], "created_at": r["created_at"]}
                   for r in services.list_backups(conn, vm_id)]
        events = [dict(r) for r in services.list_events(conn, vm_id=vm_id, limit=25)]
        return jsonify(vm={
            "vm_id": vm["vm_id"],
            "name": vm["vm_name"],
            "uuid": vm["vbox_uuid"],
            "class_group": vm["class_group"],
            "status": vm["status"],
            "fail_count": vm["fail_count"],
            "is_template": bool(vm["is_template"]),
            "student": vm["student_username"],
            "heartbeat_property": vm["heartbeat_property"],
            "interval_minutes": vm["interval_minutes"],
            "retention_count": vm["retention_count"],
            "pre_session_snapshot": bool(vm["pre_session_snapshot"]),
            "last_checked": vm["last_checked"],
        }, snapshots=snapshots, backups=backups, events=events)
    finally:
        conn.close()


@bp.get("/events")
def events():
    conn = _conn()
    try:
        limit = min(max(request.args.get("limit", default=100, type=int), 1), 1000)
        offset = max(request.args.get("offset", default=0, type=int), 0)
        vm_id = request.args.get("vm_id", type=int)
        event_type = request.args.get("event_type") or None
        rows = services.list_events(conn, vm_id=vm_id, event_type=event_type,
                                    limit=limit, offset=offset)
        total = services.count_events(conn, vm_id=vm_id, event_type=event_type)
        return jsonify(total=total, limit=limit, offset=offset,
                       events=[dict(r) for r in rows])
    finally:
        conn.close()


@bp.get("/sessions")
def sessions():
    conn = _conn()
    try:
        return jsonify(sessions=[dict(r) for r in services.list_active_sessions(conn)])
    finally:
        conn.close()


@bp.get("/reports")
def reports():
    conn = _conn()
    try:
        today = date.today()
        start = request.args.get("start") or (today - timedelta(days=30)).isoformat()
        end = request.args.get("end") or today.isoformat()
        group = request.args.get("class_group", "All")
        return jsonify(services.report(conn, start, end, group))
    finally:
        conn.close()


@bp.get("/notifications")
def notifications():
    from . import notifier
    conn = _conn()
    try:
        return jsonify(notifications=[dict(r) for r in notifier.list_notifications(conn)])
    finally:
        conn.close()
