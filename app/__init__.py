import logging
import threading
from datetime import timedelta

from flask import Flask, render_template, request

from .config import Settings
from .db import init_db
from .vbox import make_vbox

log = logging.getLogger("vmrecovery")


def create_app(settings: Settings | None = None, vbox=None) -> Flask:
    settings = settings or Settings.from_env()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.cookie_secure,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=settings.session_hours),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    app.extensions["settings"] = settings
    app.extensions["vbox"] = vbox or make_vbox(settings)
    app.extensions["lock"] = threading.Lock()   # one VirtualBox operation at a time
    init_db(settings.db_path)

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    _load_runtime_settings(app)
    _seed_initial_data(app)
    _hydrate_simulated_vbox(app)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; form-action 'self'; base-uri 'self'; "
            "frame-ancestors 'none'")
        if response.mimetype == "text/html":
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.after_request
    def access_log(response):
        """Write every request to the log.

        Without this the log showed the service starting and nothing else, so
        a button that did nothing left no trace and there was no way to tell
        which action had been pressed.
        """
        if request.path != "/healthz":
            log.info("%s %s -> %s", request.method, request.path, response.status_code)
        return response

    @app.errorhandler(Exception)
    def unhandled_error(exc):
        """Log anything that escapes a view, with the path that caused it."""
        from werkzeug.exceptions import HTTPException
        if isinstance(exc, HTTPException):
            code = exc.code or 500
            if code >= 500:
                log.error("%s %s -> %s: %s", request.method, request.path, code, exc.description)
            else:
                log.info("%s %s -> %s: %s", request.method, request.path, code, exc.description)
            return render_template("error.html", message=exc.description), code
        log.exception("Unhandled error on %s %s", request.method, request.path)
        return render_template("error.html",
                               message="Something went wrong. The failure has been written to the log."), 500

    from .views import bp
    app.register_blueprint(bp)

    from .api import bp as api_bp
    app.register_blueprint(api_bp)
    return app


def _load_runtime_settings(app: Flask) -> None:
    """Apply the database overrides and point the notifier at its channels.

    The environment and the configuration files provide the defaults; the
    Settings page can override them at runtime without a restart.
    """
    from . import db, notifier, services

    settings = app.extensions["settings"]
    services.set_runtime_settings(settings)
    conn = db.connect(settings.db_path)
    try:
        services.apply_overrides(conn, settings)
    except Exception:
        log.exception("Could not apply the stored settings overrides")
    finally:
        conn.close()
    notifier.configure(settings)


def _seed_initial_data(app: Flask) -> None:
    """Seed default accounts and demo VMs if database is newly initialized."""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    from . import db, services
    settings = app.extensions["settings"]
    conn = db.connect(settings.db_path)
    try:
        user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if user_count == 0:
            admin_id = services.create_user(conn, "admin", "Admin1234!", role="admin")
            services.create_user(conn, "trainer", "Trainer1234!", role="trainer")
            student_id = services.create_user(conn, "student", "Student1234!", role="student")
            log.info("Initialized default users: admin, trainer, student")

            if settings.simulate:
                vbox = app.extensions["vbox"]
                demo_vms = [
                    ("DEV-LAB-01", "00000000-0000-4000-8000-000000000001", "Software Dev", student_id, False),
                    ("DEV-LAB-02", "00000000-0000-4000-8000-000000000002", "Software Dev", None, False),
                    ("NET-LAB-03", "00000000-0000-4000-8000-000000000003", "Networking", None, False),
                    ("NET-LAB-04", "00000000-0000-4000-8000-000000000004", "Networking", None, False),
                    ("SEC-LAB-05", "00000000-0000-4000-8000-000000000005", "Cybersecurity", None, True),
                ]
                for name, uuid, group, assigned_to, is_tpl in demo_vms:
                    try:
                        vm_id = services.register_vm(
                            conn, name, uuid, group,
                            interval=30, keep=5, pre_session=True,
                            user_id=admin_id,
                            is_template=is_tpl,
                            assigned_student_id=assigned_to
                        )
                        vbox.take_snapshot(uuid, "baseline-clean")
                        conn.execute(
                            "INSERT INTO snapshots (vm_id, snapshot_name, snapshot_type, created_at) "
                            "VALUES (?, ?, 'scheduled', ?)",
                            (vm_id, "baseline-clean", services.ts(services.now_local()))
                        )
                    except Exception as e:
                        log.debug("Demo VM setup note: %s", e)
                conn.commit()
                log.info("Initialized demo lab VMs for simulation mode.")
    except Exception as exc:
        log.warning("Could not check/seed initial database records: %s", exc)
    finally:
        conn.close()


def _hydrate_simulated_vbox(app: Flask) -> None:
    """Sync existing DB VMs and snapshots into SimulatedVBox after a restart.

    In cloud deployments (Render + Supabase PostgreSQL), the database persists
    across container restarts while SimulatedVBox starts fresh in memory.
    Hydrating here guarantees auto-recovery, Sim. freeze/crash, and manual
    'Review and restore' always find their recorded snapshots.
    """
    settings = app.extensions["settings"]
    if not settings.simulate:
        return
    from . import db
    vbox = app.extensions["vbox"]
    if not hasattr(vbox, "vms"):
        return
    conn = db.connect(settings.db_path)
    try:
        state_map = {
            "running": "running",
            "powered off": "poweroff",
            "crashed": "aborted",
            "frozen": "paused",
            "paused": "paused",
        }
        for vm in conn.execute("SELECT vm_id, vm_name, vbox_uuid, status FROM vms").fetchall():
            uuid = vm["vbox_uuid"]
            desired_state = state_map.get(vm["status"], "running")
            if uuid not in vbox.vms:
                vbox.add_vm(vm["vm_name"], uuid, state=desired_state)
            else:
                vbox.vms[uuid]["name"] = vm["vm_name"]
                vbox.vms[uuid]["state"] = desired_state
            snaps = conn.execute(
                "SELECT snapshot_name FROM snapshots WHERE vm_id=? ORDER BY snapshot_id ASC",
                (vm["vm_id"],),
            ).fetchall()
            mem_snaps = vbox.vms[uuid]["snapshots"]
            for s in snaps:
                if s["snapshot_name"] not in mem_snaps:
                    mem_snaps.append(s["snapshot_name"])
        log.info("Hydrated %d simulated VM(s) and their snapshots from database.", len(vbox.vms))
    except Exception as exc:
        log.warning("Could not hydrate simulated VBox from database: %s", exc)
    finally:
        conn.close()
