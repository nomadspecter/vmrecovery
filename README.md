# Automated Virtual Machine Recovery System

Takes snapshots of VirtualBox training VMs on a schedule and before every session, detects crashed
or frozen VMs, and restores them to their latest good snapshot automatically.
Python 3 + Flask + SQLite + the `VBoxManage` command line. School project (Zetech University, Simon Ndonga).

## Run it

```bash
cd vmrecovery
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py create-user admin admin        # asks for a password (8+ characters)
python manage.py create-user trainer trainer

python run.py                                   # real VirtualBox
# open http://127.0.0.1:5000
```

**No VirtualBox handy? Try the simulation** (fake VMs, "Sim. crash" and "Sim. freeze" buttons on the dashboard):

```bash
VMR_SIMULATE=1 VMR_CHECK_SECONDS=5 python run.py
```

Run the tests (no VirtualBox needed): `python -m pytest -q`

## Settings (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `VMR_SIMULATE` | `0` | `1` = fake VirtualBox for demos |
| `VMR_VBOXMANAGE` | `VBoxManage` | path to the command if it is not on PATH |
| `VMR_CHECK_SECONDS` | `30` | how often the background service checks every VM |
| `VMR_FAIL_THRESHOLD` | `2` | bad checks in a row before a VM counts as failed (avoids false alarms) |
| `VMR_MAX_RESTORES_PER_HOUR` | `3` | automatic restores per VM per hour before it alerts the admin instead |
| `VMR_HEARTBEAT_TIMEOUT` | `90` | seconds without a guest heartbeat before a VM counts as frozen |
| `VMR_HOST` / `VMR_PORT` | `127.0.0.1` / `5000` | bind address. Use `0.0.0.0` only on a trusted lab network (no HTTPS) |
| `VMR_DB` | `instance/vmrecovery.db` | database file |

## Important to know

- **Run it as the same Linux user that owns the VMs.** VirtualBox keeps a separate VM list per user.
- **"Frozen" detection.** VirtualBox reports `paused` for a VM that has stopped, and that is caught automatically.
  A guest OS that hangs while VirtualBox still says `running` can only be caught with the optional
  heartbeat: see `docs/REAL_VIRTUALBOX_TEST_GUIDE.md`.
- **Powered-off VMs are not treated as crashed.** Only `aborted`, `guru meditation`, `stuck`, `paused`
  and a stale heartbeat count as failures.
- **Restores are destructive by design.** Work done after the restored snapshot is lost. Test on throwaway VMs.
- Removing a VM in the dashboard only stops managing it. The VM and its snapshots stay in VirtualBox.

See `ARCHITECTURE.md` for how the code is organised and `docs/REAL_VIRTUALBOX_TEST_GUIDE.md` for testing
with real VMs.
