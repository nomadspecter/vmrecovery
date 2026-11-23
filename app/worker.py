"""Background service: every few seconds, check all VMs, recover failures, take due snapshots.

It also does the housekeeping that should not depend on somebody opening the
dashboard: pruning old events, and taking a daily backup of the application
database so a mistake in the web interface can always be undone.
"""
import logging
import threading

from . import db, services

log = logging.getLogger("vmrecovery")


class Worker(threading.Thread):
    def __init__(self, settings, vbox, lock: threading.Lock):
        super().__init__(name="vm-recovery-worker", daemon=True)
        self.settings, self.vbox, self.lock = settings, vbox, lock
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self.started_at = None
        self.last_cycle = None
        self.last_summary = None
        self.last_error = None
        self.cycles = 0
        self.last_maintenance = None
        self.last_backup = None

    def stop(self):
        self._stop_event.set()
        self._wake_event.set()

    def wake(self, delay: float = 0.0):
        """Trigger the next monitoring cycle early (e.g. right after a fault test)."""
        if delay <= 0:
            self._wake_event.set()
        else:
            t = threading.Timer(delay, self._wake_event.set)
            t.daemon = True
            t.start()

    def status(self) -> dict:
        """A small snapshot for the System Health page and /healthz."""
        return {
            "running": self.is_alive() and not self._stop_event.is_set(),
            "started_at": self.started_at,
            "last_cycle": self.last_cycle,
            "last_summary": self.last_summary,
            "last_error": self.last_error,
            "cycles": self.cycles,
            "last_maintenance": self.last_maintenance,
            "last_backup": self.last_backup,
        }

    def run(self):
        self.started_at = services.ts(services.now_local())
        log.info("Worker started (every %ss)", self.settings.check_seconds)
        while not self._stop_event.is_set():
            try:
                conn = db.connect(self.settings.db_path)
                try:
                    summary = services.run_cycle(conn, self.vbox, self.settings, lock=self.lock)
                    self._housekeeping(conn)
                finally:
                    conn.close()
                self.last_cycle = services.ts(services.now_local())
                self.last_summary = summary
                self.last_error = None
                self.cycles += 1
                if summary["snapshots"] or summary["recoveries"] or summary["failed_recoveries"]:
                    log.info("Cycle: %s", summary)
            except Exception as exc:
                self.last_error = str(exc) or exc.__class__.__name__
                log.exception("Worker cycle failed")
            self._wake_event.clear()
            self._wake_event.wait(self.settings.check_seconds)

    # ------------------------------------------------------------------ housekeeping
    def _housekeeping(self, conn) -> None:
        """Prune old events and keep a rolling set of database backups.

        Runs once an hour, not on every cycle, so the database is not written
        to more often than it has to be.
        """
        now = services.now_local()
        last = self.last_maintenance
        if last is not None:
            try:
                if (now - services.parse_ts(last)).total_seconds() < 3600:
                    return
            except ValueError:
                pass

        removed = services.prune_events(conn, getattr(self.settings, "event_retention_days", 0),
                                        now)
        if removed:
            log.info("Pruned %s event(s) older than the retention window", removed)

        keep = getattr(self.settings, "db_backup_keep", 0)
        if keep:
            try:
                path = db.backup_database(self.settings.db_path,
                                          getattr(self.settings, "db_backup_dir",
                                                  "instance/db-backups"), keep)
                self.last_backup = path
                log.info("Application database backed up to %s", path)
            except Exception:
                log.exception("Could not back up the application database")
        self.last_maintenance = services.ts(now)
