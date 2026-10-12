import threading

from flask import Flask

from .config import Settings
from .db import init_db
from .vbox import make_vbox


def create_app(settings: Settings | None = None, vbox=None) -> Flask:
    settings = settings or Settings.from_env()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    app.extensions["settings"] = settings
    app.extensions["vbox"] = vbox or make_vbox(settings)
    app.extensions["lock"] = threading.Lock()   # one VirtualBox operation at a time
    init_db(settings.db_path)

    from .views import bp
    app.register_blueprint(bp)
    return app
