# Automated Virtual Machine Recovery System

Takes snapshots of VirtualBox training VMs on a schedule and before every session, detects crashed
or frozen VMs, and restores them to their latest good snapshot automatically. Pairs snapshots with
independent `.ova` appliance backups, low-disk monitoring, template cloning, and student workstations.
Python 3 + Flask + SQLite + the `VBoxManage` command line. School project (Zetech University, Simon Ndonga).

## Run it

```bash
cd vmrecovery
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py create-user admin admin        # asks for a password (8+ characters)
python manage.py create-user trainer trainer
python manage.py create-user student student

python run.py                                   # real VirtualBox
# open http://127.0.0.1:5000
```

**No VirtualBox handy? Try the simulation** (fake VMs, "Sim. crash" and "Sim. freeze" buttons on the dashboard):

```bash
VMR_SIMULATE=1 VMR_CHECK_SECONDS=5 python run.py
```

Run the tests (no VirtualBox needed): `python -m pytest -q`

## Production Deployment (Running Unattended)

To run 24/7 as a systemd service that starts on system boot:

```bash
sudo ./deploy/install_service.sh
sudo systemctl status vmrecovery
```

## Settings (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `VMR_SIMULATE` | `0` | `1` = fake VirtualBox for demos and tests |
| `VMR_VBOXMANAGE` | `VBoxManage` | path to the command if it is not on PATH |
| `VMR_CHECK_SECONDS` | `30` | how often the background service checks every VM |
| `VMR_FAIL_THRESHOLD` | `2` | bad checks in a row before a VM counts as failed (avoids false alarms) |
| `VMR_MAX_RESTORES_PER_HOUR` | `3` | automatic restores per VM per hour before alerting the admin |
| `VMR_HEARTBEAT_TIMEOUT` | `90` | seconds without a guest heartbeat before a VM counts as frozen |
| `VMR_BACKUP_DIR` | `instance/backups` | host directory where independent `.ova` exports are saved |
| `VMR_BACKUP_RETENTION` | `3` | independent appliance backups kept per VM |
| `VMR_DISK_MIN_FREE_GB` | `5.0` | minimum free host storage (GB) before triggering a low-disk warning |
| `VMR_DISK_MIN_FREE_PCT` | `10.0` | minimum free host storage (%) before triggering a low-disk warning |
| `VMR_HOST` / `VMR_PORT` | `127.0.0.1` / `5000` | bind address. Use `0.0.0.0` only on a trusted lab network |
| `VMR_DB` | `instance/vmrecovery.db` | database file |

## Key Capabilities

1. **Automated Crash & Freeze Recovery**:
   - Continuous background health loop checks VM state and optional guest heartbeat.
   - Restores latest valid snapshot automatically and measures recovery time in seconds.
2. **Independent Backups (`.ova` export)**:
   - Pairs local disk snapshots with independent appliance backups (`VBoxManage export`) stored in `instance/backups`.
   - Protects against storage medium corruption or accidental VM deletion.
3. **VM Template Cloning & Trainer Requests**:
   - Admins can mark any VM as a golden template.
   - Trainers submit requests for new VMs choosing from approved templates (linked or full clone).
   - Admins review and approve requests with automatic clone creation and baseline snapshotting.
4. **Student Workstation View**:
   - Students can log in to view their assigned VM, status badge, and last protected time ("Your work is protected up to...").
   - Students can submit a one-click restore request to notify their trainer/admin.
5. **Storage & Resource Safeguards**:
   - Proactive free-disk space checks prevent snapshot or backup creation from filling the host drive.
   - Low-disk space warnings trigger alerts on the dashboard and in event logs.
6. **Web User Administration**:
   - Full user management under `/users` to create users, reset passwords, and manage roles (`admin`, `trainer`, `student`).

See `ARCHITECTURE.md` for architecture details and `docs/REAL_VIRTUALBOX_TEST_GUIDE.md` for testing with real VMs.
