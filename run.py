"""Start the web dashboard and the background recovery service.

    python run.py                    # production WSGI server (waitress)
    VMR_DEV_SERVER=1 python run.py   # Flask development server, for local work
    VMR_SIMULATE=1 python run.py     # demo with a simulated VirtualBox
"""
import atexit
import logging
import signal
import sys

from app import create_app
from app.config import Settings
from app.worker import Worker


def main() -> int:
    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log = logging.getLogger("vmrecovery")

    app = create_app(settings)
    worker = None
    if settings.run_worker:
        worker = Worker(settings, app.extensions["vbox"], app.extensions["lock"])
        app.extensions["worker"] = worker
        worker.start()
        atexit.register(worker.stop)

    def shutdown(_signum, _frame):
        if worker is not None:
            worker.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, shutdown)

    log.info("Listening on http://%s:%s (simulate=%s, worker=%s)",
             settings.host, settings.port, settings.simulate, settings.run_worker)

    if settings.dev_server:
        app.run(host=settings.host, port=settings.port, debug=False, threaded=True)
        return 0

    try:
        from waitress import serve
    except ImportError:
        log.warning("waitress is not installed; using Flask's development server instead. "
                    "Run 'pip install -r requirements.txt' for production.")
        app.run(host=settings.host, port=settings.port, debug=False, threaded=True)
        return 0

    serve(app, host=settings.host, port=settings.port, threads=8, ident="VMRecovery")
    return 0


if __name__ == "__main__":
    sys.exit(main())
