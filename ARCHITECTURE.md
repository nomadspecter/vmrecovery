# Architecture

## The shape of the system

```
                       ┌──────────────────────────────────────────┐
   browser  ──HTTP──►  │  run.py (waitress, threaded WSGI)        │
   monitoring ──API─►  │    ├── app/views.py   the web pages      │
                       │    ├── app/api.py     the JSON API        │
                       │    └── app/worker.py  the monitoring loop │
                       └───────────────┬──────────────────────────┘
                                       │
                            app/services.py  (the core logic)
                            ┌──────────┴──────────┐
                            │                     │
                     app/vbox.py            app/notifier.py
                    (VirtualBox)            (email, webhook)
                            │                     │
                     VBoxManage CLI        SMTP / HTTPS webhook
                            │
                            └──────────► app/db.py ──► SQLite
                                             │
                                     app/config.py (settings)
```

Two entry points share one process: the **web tier** (Flask blueprints) and the **worker** (a
daemon thread). Both call into `app/services.py`, which owns every rule. `app/vbox.py` is the only
module that shells out to VirtualBox, and `app/db.py` is the only module that touches SQLite, so
the rules stay testable without either.

| File | Role |
|---|---|
| `app/schema.sql` | the database design, applied on every start with `CREATE TABLE IF NOT EXISTS` |
| `app/db.py` | connections, numbered migrations, online backup and restore |
| `app/config.py` | settings, the layered `.env` loader, runtime override handling |
| `app/vbox.py` | `VBoxController` (real) and `SimulatedVBox` (demo and tests) |
| `app/services.py` | registry, snapshots, backups, recovery, sessions, requests, reports, settings |
| `app/notifier.py` | email and webhook delivery, and the record of every attempt |
| `app/worker.py` | the background monitoring and recovery loop, plus hourly housekeeping |
| `app/views.py` | the web pages and their form handling |
| `app/api.py` | the read-only, token-authenticated JSON API |
| `app/templates/` | the Jinja templates |
| `manage.py` | the command line admin tool |
| `deploy/` | the systemd unit and the installer |

## Configuration

Six layers, highest priority first. A layer only fills in a variable that no higher layer has
defined, so a real environment variable always beats a file, and a file always beats a default.

| Priority | Layer | Notes |
|---|---|---|
| 1 | `app_settings` (database) | runtime overrides written from the Settings page |
| 2 | Real environment variables | the shell, systemd, Docker |
| 3 | `.env.local` | developer overrides; **skipped in production** |
| 4 | `instance/vmrecovery.env` | machine-specific overrides |
| 5 | `.env` | shared defaults, copied from `.env.example` |
| 6 | Built-in defaults | `app/config.py` |

Layer 5 is the reason the service can be retuned without a restart: the Settings page writes a row,
and the worker applies it on the next cycle. `Settings.apply_overrides()` coerces the value to the
declared type, ignores unknown keys, and never raises — a bad value in the database degrades to the
previous one rather than taking the service down.

`.env.local` is skipped when `VMR_ENV=production` is set or when `INVOCATION_ID` is present (the
process is running under systemd). Without that guard a developer's `.env.local` — a simulator
switch and a separate database — would silently take the production service off the real data.

## Database

SQLite in WAL mode, with `PRAGMA foreign_keys = ON` so the foreign keys in the schema are real.
The web tier holds a connection per request and the worker one per cycle; WAL lets them read and
write at the same time. A 15-second busy timeout makes a concurrent writer wait for the lock
instead of failing with "database is locked". The journal mode is a property of the file, not of
the connection, so it is set once rather than on every open.

**Applying the schema.** `init_db()` splits `schema.sql` at the `-- INDEXES ---` marker and runs
the tables first, then the migrations, then the indexes. The order matters: an index on a column
that an old database does not have yet cannot be created, and the index block would fail before the
migration that adds the column had a chance to run. Each index is created inside its own
`try/except`, so one that still cannot be built does not stop the service from starting.

**Migrations.** Changes to existing tables are numbered migrations in `app/db.py`:

| # | What it does |
|---|---|
| 1 | adds every column the current code expects to `vms` |
| 2 | rebuilds `users` so the `student` role is allowed |
| 3 | adds `users.created_at` and `users.last_login_at` |
| 4 | adds `events.duration_seconds` |
| 5 | links `notifications` to a machine |
| 6 | repairs tables left pointing at a renamed table by a very old upgrade |
| 7 | adds `vms.admin_paused` |

Each one runs exactly once and is recorded in `schema_meta`, so an old database is upgraded in place
on the next start. Migrations that rebuild a table use the documented SQLite procedure — build a
replacement, copy the rows, drop the old table, rename the new one into place — with foreign keys
switched off for the duration so the rebuild cannot cascade.

**Tables.**

| Table | Holds |
|---|---|
| `users` | accounts, roles (`admin`, `trainer`, `student`), creation and last-login times |
| `snapshot_policies` | interval, retention count, pre-session snapshot flag |
| `vms` | the registry: name, VirtualBox UUID, class group, policy, status, heartbeat property, fail count, template flag, assigned student, administrator-pause flag |
| `snapshots` | the snapshots taken for each machine, with its type |
| `backups` | independent `.ova` exports, with their path and size |
| `vm_requests` | provisioning requests: `pending` → `approved` → `ready`, or `rejected` / `failed` |
| `class_sessions` | one row per session, with a partial unique index allowing one active session per class group |
| `events` | the audit trail: type, details, result, duration, who did it, when |
| `app_settings` | runtime configuration overrides |
| `notifications` | one row per delivery attempt: channel, recipient, severity, status, error |

**Backups.** `backup_database()` uses SQLite's online backup API, so a copy taken while the service
is running is consistent rather than a torn copy of a live file. Old copies are pruned to the
configured count. The worker takes one every hour; `manage.py backup-db` takes one on demand.

## One monitoring cycle (`services.run_cycle`)

1. **Housekeeping.** Every hour the worker prunes events beyond the retention window and rotates
   the database backup.
2. **Storage check.** `check_disk_space()` inspects the free space on the host and raises a
   low-disk alert when it falls below `VMR_DISK_MIN_FREE_GB` or `VMR_DISK_MIN_FREE_PCT`.
3. For each registered machine:
   - `observe()` turns VirtualBox's state into running / powered off / crashed / frozen / busy /
     unknown. A machine that an administrator paused on purpose (`admin_paused`) reports `paused`
     and is left alone; a machine paused outside the dashboard is a frozen one.
   - `monitor_vm()` counts consecutive bad readings. At `VMR_FAIL_THRESHOLD` it logs the failure and
     calls `recover()`.
   - `recover()` powers the machine off if needed, restores the newest snapshot that still exists
     in VirtualBox, boots it with `startvm`, measures the recovery duration in seconds, and logs the
     outcome. A failure is retried up to `VMR_MAX_RESTORES_PER_HOUR`, after which the system stops
     trying and raises one alert instead of looping.
   - A healthy machine whose snapshot interval has passed gets a scheduled snapshot, and snapshots
     beyond the retention count are pruned — in the database and in VirtualBox, so the two never
     disagree.

## Concurrency and safety

- A thread-level lock (`vbox_lock`) keeps the web tier and the worker from issuing conflicting
  `VBoxManage` commands at the same time. It is taken per machine rather than for the whole pass,
  so a slow export of one machine does not block the web interface or the monitoring of the others.
- Operations wait for VirtualBox to leave transitional states (`LiveSnapshotting`, `restoring`, …)
  before acting on a machine.
- Restoring an independent backup parks the original machine under a temporary name and only
  removes it once the import has succeeded, so a failed restore never leaves you with nothing.
- One failing machine never stops monitoring or recovery for the others.
- A failing notification channel is recorded and swallowed: a broken mail server must not take the
  recovery service down with it.

## Features

- **Independent backups.** `VBoxManage export` writes a standalone `.ova` to `instance/backups/`.
  Unlike a snapshot it shares no disk with the machine, so it survives the loss of the disk the
  machine lives on.
- **Template cloning and the request queue.** A machine can be marked as a golden template, which
  takes a baseline snapshot if it has none. Trainers request machines from a template; an
  administrator approves the request and the clone is created — linked
  (`clonevm --options link --snapshot <baseline>`, small, dependent on the template) or full
  (`clonevm --mode all`, a complete independent copy). The new machine is registered and gets its
  own baseline snapshot.
- **Training sessions.** `class_sessions` allows one active session per class group, enforced by a
  partial unique index, which makes the Start button safe to press twice. Start brings up
  off/saved/paused machines and takes a pre-session snapshot where the policy allows it. A second
  press while the session is active restarts stopped machines and protects anything that was added
  or lost its snapshot, but leaves a machine that already has a pre-session snapshot alone. End
  takes a post-session snapshot of the running machines, optionally powers the group off, and closes
  the session.
- **Student workstations.** A student sees their own machine, its status, and when it was last
  protected, and can ask for a restore. The event log is scoped to their machines.
- **Web user management.** Administrators create accounts, reset passwords, change roles, and
  remove accounts.
- **Power control.** Start, stop, pause, resume, and a bulk action over a selection, with every
  action recorded in the audit trail.
- **Notifications.** Crashes, failed restores, restore requests, machine requests, and low disk
  are sent over email and webhooks. Every attempt is recorded whether it succeeded or not.
- **Runtime settings.** The thresholds, retention, storage limits, and notification credentials are
  editable from the browser and applied live.
- **Audit trail.** Every state change lands in `events`, filterable, paginated, and downloadable as
  CSV.

## The JSON API

`app/api.py` is a separate blueprint with its own `before_request` guard. It is read-only, it
requires a bearer token, and it never touches state. The guard answers `503` when no token is
configured — the API is off, and says so — and `401` when the token is wrong. `/api/health` is
exempt so a monitor can reach it without a credential.

## Production runtime

`run.py` starts one `Worker` thread and serves the Flask app through waitress. The systemd unit
sets `VMR_ENV=production`, uses `Restart=always`, starts after VirtualBox, runs as the VM-owning
user in the `vboxusers` group, and applies `UMask=0077` so the database and the secret key are not
world-readable. `SIGTERM` stops the worker and exits cleanly. `/healthz` reports the database, the
worker heartbeat, and the disk with HTTP 200 or 503, so an external monitor can use it directly.
