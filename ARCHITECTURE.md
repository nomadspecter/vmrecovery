# Architecture

```
run.py ──► create_app() ──► views.py (Flask pages)  ──┐
   │                                                  ├──► services.py ──► vbox.py ──► VBoxManage
   └──► Worker thread (worker.py) ───────────────────┘          │
                                                                 └──► db.py ──► SQLite (schema.sql)
```

| File | Role | Chapter Two model |
|---|---|---|
| `app/schema.sql`, `app/db.py` | database tables and connections | ERD |
| `app/vbox.py` | `VBoxController` (real) and `SimulatedVBox` (demo, tests): the only code that talks to VirtualBox | `VBoxController` class, VirtualBox external entity |
| `app/services.py` | registry, snapshots, health checks, recovery, reports | processes 2.0 to 5.0 in the Level 1 DFD, `HealthMonitor` |
| `app/worker.py` | background loop that calls `run_cycle()` every `VMR_CHECK_SECONDS` | recovery flowchart (Figure 2.3.2b) |
| `app/views.py`, `templates/` | login, dashboard, VMs, snapshots, event log, reports | UI mockups, process 1.0 |
| `manage.py` | create users, reset passwords | |

## One cycle (`services.run_cycle`)

For each registered VM:
1. `observe()` turns VirtualBox's state into running / powered off / crashed / frozen / busy / unknown.
2. `monitor_vm()` counts consecutive bad readings. At `VMR_FAIL_THRESHOLD` it logs the failure and calls `recover()`.
3. `recover()`: power off if needed, `snapshot restore`, `startvm`, then log the result. If it fails, retry on the next
   cycle, up to `VMR_MAX_RESTORES_PER_HOUR`, then raise one alert for the administrator.
4. If the VM is healthy and its snapshot interval has passed, take a snapshot and delete the oldest beyond the retention limit.
   Failed or crashed VMs are never snapshotted.

## Rules the design follows

- Only `vbox.py` runs commands, with argument lists, never a shell string.
- A lock ensures the worker and web actions never run VirtualBox commands at the same moment.
- One failing VM never stops the cycle for the others.
- Every action is written to the `events` table, which feeds the dashboard, event log and reports.
- Passwords are hashed; every POST needs a CSRF token; logins are rate limited; the admin role is required for changes.

## Differences from the Chapter Two diagrams

- `vms` has three extra operational columns: `heartbeat_property`, `fail_count`, `last_checked`.
- `vms.created_by` links a VM to the user who registered it (the class diagram's "managed by").
- Level 1 DFD process 4.0 also reads guest heartbeat data from VirtualBox when it is configured.
