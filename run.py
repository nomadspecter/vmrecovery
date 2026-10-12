"""Start the web dashboard and the background recovery service.

    python run.py                 # real VirtualBox
    VMR_SIMULATE=1 python run.py  # demo with a simulated VirtualBox
"""
import logging

from app import create_app
from app.config import Settings
from app.worker import Worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = Settings.from_env()
app = create_app(settings)

if __name__ == "__main__":
    if settings.run_worker:
        Worker(settings, app.extensions["vbox"], app.extensions["lock"]).start()
    app.run(host=settings.host, port=settings.port, debug=False, threaded=True)
