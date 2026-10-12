import sys
from datetime import datetime
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app, db, services  # noqa: E402
from app.config import Settings  # noqa: E402
from app.vbox import SimulatedVBox  # noqa: E402

T0 = datetime(2026, 6, 1, 9, 0, 0)


@pytest.fixture
def settings(tmp_path):
    return Settings(db_path=str(tmp_path / "t.db"), simulate=True, run_worker=False,
                    secret_key="test-secret", fail_threshold=2, max_restores_per_hour=3,
                    heartbeat_timeout=90)


@pytest.fixture
def conn(settings):
    db.init_db(settings.db_path)
    c = db.connect(settings.db_path)
    yield c
    c.close()


@pytest.fixture
def vbox():
    v = SimulatedVBox()
    v.add_vm("DEV-LAB-01", "uuid-1", "running")
    v.add_vm("NET-LAB-03", "uuid-3", "running")
    return v


@pytest.fixture
def vm(conn, vbox):
    """A registered VM with a 30-minute snapshot interval, keeping 3 snapshots."""
    vm_id = services.register_vm(conn, "DEV-LAB-01", "uuid-1", "Class A", 30, 3, now=T0)
    return services.get_vm(conn, vm_id)


@pytest.fixture
def client(settings, vbox):
    app = create_app(settings, vbox)
    app.config["TESTING"] = True
    conn = db.connect(settings.db_path)
    for name, role in (("admin", "admin"), ("trainer", "trainer")):
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                     (name, generate_password_hash("password123"), role))
    conn.commit()
    conn.close()
    return app.test_client()


@pytest.fixture
def users(conn):
    """Two real users so events can be attributed to someone. Returns (admin_id, trainer_id)."""
    ids = []
    for name, role in (("admin", "admin"), ("trainer", "trainer")):
        cur = conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                           (name, "x", role))
        ids.append(cur.lastrowid)
    conn.commit()
    return tuple(ids)
