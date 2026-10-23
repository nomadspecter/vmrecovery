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

    _load_runtime_settings(app)

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
