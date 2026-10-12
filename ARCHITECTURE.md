# Architecture

```
run.py ──► create_app() ──► views.py (Flask pages)  ──┐
   │                                                  ├──► services.py ──► vbox.py ──► VBoxManage
   └──► Worker thread (worker.py) ───────────────────┘          │
                                                                 └──► db.py ──► SQLite (schema.sql)
```

| File | Role | Chapter Two model |
|---|---|---|
| `app/schema.sql`, `app/db.py` | database tables, schema migrations, and connection pooling | ERD |
| `app/vbox.py` | `VBoxController` (real) and `SimulatedVBox` (demo, tests): executes VBoxManage CLI commands (snapshots, clone, export, import) | `VBoxController` class, VirtualBox external entity |
| `app/services.py` | registry, templates, requests, snapshots, independent backups, health checks, recovery, reports | processes 2.0 to 5.0 in the Level 1 DFD, `HealthMonitor` |
| `app/worker.py` | background loop that calls `run_cycle()` every `VMR_CHECK_SECONDS` | recovery flowchart (Figure 2.3.2b) |
| `app/views.py`, `templates/` | login, dashboard (admin/trainer/student), VMs, templates, requests, backups, users, events, reports | UI mockups, process 1.0 |
| `manage.py` | CLI admin tool: create users, reset passwords | deployment & admin utility |
| `deploy/vmrecovery.service` | systemd service unit for 24/7 unattended execution on host boot | deployment milestone |

## One cycle (`services.run_cycle`)

1. **Storage check**: inspects free disk space on host backup directory (`check_disk_space`). Raises low-disk alert if storage falls below thresholds (e.g. < 5 GB or < 10%).
2. For each registered VM:
   - `observe()` turns VirtualBox's state into running / powered off / crashed / frozen / busy / unknown.
   - `monitor_vm()` counts consecutive bad readings. At `VMR_FAIL_THRESHOLD` it logs the failure and calls `recover()`.
   - `recover()`: powers off if needed, restores latest valid snapshot, boots VM with `startvm`, measures exact recovery duration in seconds, and logs the outcome. If it fails, retries up to `VMR_MAX_RESTORES_PER_HOUR`, then raises one alert for the administrator.
   - If the VM is healthy and its snapshot interval has passed (and it is not marked as a static golden template), takes a scheduled snapshot and prunes snapshots beyond the retention count.

## Core Features & Workflow

- **Independent Backups**: Pairs snapshots with independent `.ova` appliance exports (`create_backup`, `restore_backup`) stored in `instance/backups/`. Unlike snapshots, independent backups protect against disk/medium failure.
- **VM Template Cloning & Request Queue**:
  - Admins can designate VMs as golden templates (`is_template = 1`).
  - Trainers submit VM requests from approved templates (`vm_requests` table).
  - Admins approve requests to trigger linked or full clones (`VBoxManage clonevm`), registering new VMs with initial baseline snapshots.
- **Student Workstation Role**:
  - Students log in to view their assigned VM, status badge, and last saved time ("Your work is protected up to...").
  - Students can submit a restore request directly to the trainer/admin.
- **Web User Management**:
  - Administrators can create users (`admin`, `trainer`, `student`), reset passwords, and remove accounts directly from `/users`.
- **Concurrency & Safety**:
  - Thread-level lock (`vbox_lock`) ensures web actions and background cycles never issue conflicting `VBoxManage` commands simultaneously.
  - Fail-safe isolation: One failing VM never stops monitoring or recovery for other VMs.

## Database Entities (`app/schema.sql`)

- `users`: accounts and roles (`admin`, `trainer`, `student`).
- `snapshot_policies`: interval, retention limit, pre-session snapshot flag.
- `vms`: managed VirtualBox VMs, link to policy, `is_template` flag, `assigned_student_id`, operational health counters.
- `snapshots`: recorded snapshots taken for each VM.
- `backups`: independent OVA appliance exports on host disk with file path and byte size.
- `vm_requests`: trainer provisioning requests with status lifecycle (`pending` -> `approved`/`rejected` -> `ready`/`failed`).
- `events`: audit log of all system actions (crashes, recoveries with durations, alerts, backups, sessions).
