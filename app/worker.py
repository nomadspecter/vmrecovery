"""Background service: every few seconds, check all VMs, recover failures, take due snapshots."""
import logging
import threading

from . import db, services

log = logging.getLogger("vmrecovery")


class Worker(threading.Thread):
    def __init__(self, settings, vbox, lock: threading.Lock):
        super().__init__(name="vm-recovery-worker", daemon=True)
        self.settings, self.vbox, self.lock = settings, vbox, lock
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        log.info("Worker started (every %ss)", self.settings.check_seconds)
        while not self._stop_event.is_set():
            try:
                with self.lock:                       # web actions and the worker never overlap
                    conn = db.connect(self.settings.db_path)
                    try:
                        summary = services.run_cycle(conn, self.vbox, self.settings)
                    finally:
                        conn.close()
                if summary["snapshots"] or summary["recoveries"] or summary["failed_recoveries"]:
                    log.info("Cycle: %s", summary)
            except Exception:
                log.exception("Worker cycle failed")
            self._stop_event.wait(self.settings.check_seconds)
