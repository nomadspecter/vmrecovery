# Automated Virtual Machine Recovery System

Recovers VirtualBox training machines automatically. A background service watches every registered
machine, takes scheduled snapshots, detects crashes and freezes, and restores the machine to its last
good snapshot without anyone touching it. On top of that it adds the operational pieces a lab
actually needs: independent `.ova` appliance backups, template cloning with an approval queue,
per-student workstations, email and webhook alerts, a read-only JSON API, a live settings page, and
a full audit trail.

Python 3 · Flask · SQLite · the `VBoxManage` command line. Runs unattended as a systemd service.

---

## Table of contents

- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Install](#install)
- [Configuration](#configuration)
- [Running it](#running-it)
- [The dashboard](#the-dashboard)
- [Roles and permissions](#roles-and-permissions)
- [Training sessions](#training-sessions)
- [Cloning VMs from templates](#cloning-vms-from-templates)
- [Notifications](#notifications)
- [The JSON API](#the-json-api)
- [Command line](#command-line)
- [Production deployment](#production-deployment)
- [Security](#security)
- [Backups and disaster recovery](#backups-and-disaster-recovery)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Project layout](#project-layout)

---

## What it does

**Automated crash and freeze recovery.** Every `VMR_CHECK_SECONDS` the worker asks VirtualBox for the
state of each machine. Two consecutive bad readings (by default) mean the machine is really broken,
not just unlucky. It powers the machine off, restores the newest snapshot that still exists in
VirtualBox, and starts it again. The time this takes is measured and recorded.

**Scheduled and session snapshots.** Each machine has its own policy: how often to snapshot, how many
to keep, and whether to take one before every training session. Old snapshots are pruned
automatically, both in VirtualBox and in the database, so they never disagree.

**Independent appliance backups.** `VBoxManage export` writes a standalone `.ova` file. Unlike a
snapshot it shares no disk with the machine, so it survives the loss of the disk the machine lives on.
Restoring from a backup parks the original machine under a temporary name and only removes it once
the import has succeeded, so a failed restore never leaves you with nothing.

**Template cloning with an approval queue.** Mark a machine as a golden template and trainers can
request new machines from it. An administrator approves the request, the clone is created, and the
new machine is registered with its own baseline snapshot.

**Student workstations.** A student logs in and sees their own machine, its status, and when it was
last protected. They can ask for a restore; the administrator sees the request on the dashboard.

**Alerts that actually go somewhere.** Crashes, failed restores, restore requests, new machine
requests, and low disk space are sent by email or posted to a webhook. Every attempt is recorded,
whether it succeeded or not, so you can see what was sent and whether it arrived.

**A live settings page.** Thresholds, retention, storage limits, and notification credentials can be
changed from the browser and take effect on the next monitoring cycle. Nothing needs a restart, and
nothing needs a text editor on the server.

**A full audit trail.** Every state change lands in an append-only event log with the user who made
it. It is searchable, filterable, and downloadable as CSV.

---

## Requirements

| Component | Version | Notes |
|---|---|---|
| Python | 3.10 or newer | 3.14 is what this was developed against |
| Flask | 3.0 or newer | `requirements.txt` |
| waitress | 3.0 or newer | the production WSGI server |
| SQLite | 3.35 or newer | ships with Python; WAL mode is used |
| VirtualBox | 6.1 or newer | only needed on the machine that owns the VMs |
| Linux | any with systemd | for the unattended deployment; the app itself runs anywhere |

You do **not** need VirtualBox to try the system out. The built-in simulator pretends to be
VirtualBox, with fake machines you can crash and freeze on demand.

---

## Install

```bash
cd vmrecovery
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # configuration, read at start-up
$EDITOR .env                   # optional: the defaults are usable as they are

python manage.py create-user admin admin      # asks for a password (8+ characters)
python manage.py create-user trainer trainer
python manage.py create-user student student

python run.py
# open http://127.0.0.1:5000
```

Try it without VirtualBox:

```bash
VMR_SIMULATE=1 VMR_CHECK_SECONDS=5 python run.py
```

The dashboard then shows five simulated lab machines, and the **Sim. crash** and **Sim. freeze**
buttons let you watch the recovery loop work end to end.

---

## Configuration

Configuration is layered. The first layer that defines a variable wins:

| Priority | Layer | Where | Committed? |
|---|---|---|---|
| 1 | Runtime overrides | the database, set from the Settings page | no |
| 2 | Real environment variables | shell, systemd, Docker | no |
| 3 | `.env.local` | the checkout | **no** — developer overrides, ignored in production |
| 4 | `instance/vmrecovery.env` | the checkout | **no** — machine-specific overrides |
| 5 | `.env` | the checkout | **no** — shared defaults, copy `.env.example` |
| 6 | Built-in defaults | `app/config.py` | yes |

Two things are worth knowing:

- **`.env.local` is ignored in production.** It is the developer layer, and it usually points at a
  separate database with the simulator switched on. Loading it under systemd would quietly take the
  service off the real data, so it is skipped whenever `VMR_ENV=production` is set, or when the
  process is systemd's own main process (`INVOCATION_ID` is present *and* the parent is PID 1).
  The second condition is deliberately narrow: systemd passes `INVOCATION_ID` to everything it
  spawns, so trusting it alone would silence the developer layer inside any shell started from a
  service.
- **Runtime overrides win over every file.** Anything changed on the Settings page is stored in the
  database and applied to the live process on the next monitoring cycle. The "Reset" button on that
  page removes the override and hands control back to the environment.

### The files on disk

| File | Holds | Committed? |
|---|---|---|
| `.env` | the shared configuration for this host: paths, thresholds, credentials | no, mode 600 |
| `instance/vmrecovery.env` | the machine layer the systemd unit reads, and the effective service configuration | no, mode 600 |
| `.env.local` | the local layer for a hand-started instance | no, mode 600 |
| `.env.example` | the annotated template for `.env` | yes |
| `.env.local.example` | the annotated template for `.env.local` | yes |
| `deploy/vmrecovery.env.example` | the annotated template for the machine layer | yes |

All three real files are gitignored. `deploy/install_service.sh` creates `.env` from the template
and fills in a fresh session key and API token, so a new installation is usable immediately.

### Environment variables

#### Web server

| Variable | Default | Meaning |
|---|---|---|
| `VMR_HOST` | `127.0.0.1` | bind address. Use `0.0.0.0` only on a trusted lab network |
| `VMR_PORT` | `5000` | bind port |
| `VMR_DEV_SERVER` | `0` | `1` uses Flask's development server. Never in production |
| `VMR_COOKIE_SECURE` | `0` | `1` makes the session cookie HTTPS-only. Set behind a TLS proxy |
| `VMR_SESSION_HOURS` | `12` | how long a login lasts |
| `VMR_LOGIN_MAX_FAILURES` | `5` | failed logins from one IP before the lockout starts |
| `VMR_LOGIN_WINDOW_SECONDS` | `300` | how long that lockout lasts |
| `VMR_ENV` | unset | set to `production` to skip `.env.local` |

#### Background recovery service

| Variable | Default | Meaning |
|---|---|---|
| `VMR_WORKER` | `1` | `0` serves the web interface without the recovery loop |
| `VMR_CHECK_SECONDS` | `30` | how often every machine is checked |
| `VMR_FAIL_THRESHOLD` | `2` | bad readings in a row before a machine counts as failed |
| `VMR_MAX_RESTORES_PER_HOUR` | `3` | automatic restores per machine per hour before the system stops and alerts |
| `VMR_HEARTBEAT_TIMEOUT` | `90` | seconds without a guest heartbeat before a running machine counts as frozen |
| `VMR_VBOX_TIMEOUT` | `1800` | seconds before a `VBoxManage` command is killed. Exports are slow |
| `VMR_VBOX_QUERY_TIMEOUT` | `60` | seconds before a read-only `VBoxManage` query is killed |
| `VMR_VBOX_ACTION_TIMEOUT` | `180` | seconds before a short `VBoxManage` command (power, suspend, start) is killed |
| `VMR_VBOX_RESTORE_TIMEOUT` | `600` | seconds before a snapshot restore is killed. Merging the disks takes minutes |
| `VMR_VBOX_LOCK_TIMEOUT` | `30` | seconds a web action waits for the VirtualBox lock before it gives up |

#### VirtualBox

| Variable | Default | Meaning |
|---|---|---|
| `VMR_VBOXMANAGE` | `VBoxManage` | full path when it is not on `PATH` |
| `VMR_SIMULATE` | `0` | `1` uses the built-in simulator instead of real VirtualBox |
| `VMR_LIVE_SNAPSHOTS` | `0` | `1` snapshots a running machine with `--live`. The guest must support it |
| `VMR_BUSY_TIMEOUT` | `300` | seconds a machine may stay in a transitional VirtualBox state before it counts as stuck |

#### Storage

| Variable | Default | Meaning |
|---|---|---|
| `VMR_BACKUP_DIR` | `instance/backups` | where independent `.ova` exports are written |
| `VMR_BACKUP_RETENTION` | `3` | independent appliance backups kept per machine |
| `VMR_DB_BACKUP_DIR` | `instance/db-backups` | where rotating application database backups are written |
| `VMR_DB_BACKUP_KEEP` | `10` | how many database backups to keep |
| `VMR_DISK_MIN_FREE_GB` | `5.0` | low-disk warning when free space drops below this |
| `VMR_DISK_MIN_FREE_PCT` | `10.0` | low-disk warning when free space drops below this percentage |
| `VMR_EVENT_RETENTION_DAYS` | `90` | days of event history to keep. `0` keeps everything |

#### Notifications

| Variable | Default | Meaning |
|---|---|---|
| `VMR_NOTIFY_EMAIL` | `0` | `1` sends notifications by email |
| `VMR_SMTP_HOST` | — | the mail server |
| `VMR_SMTP_PORT` | `587` | `587` for STARTTLS, `25` for plain |
| `VMR_SMTP_USER` | — | leave empty for an open relay |
| `VMR_SMTP_PASSWORD` | — | the password for that user |
| `VMR_SMTP_FROM` | — | the `From` address on outgoing mail |
| `VMR_SMTP_TO` | — | comma separated recipients |
| `VMR_SMTP_TLS` | `1` | `1` upgrades the connection with STARTTLS |
| `VMR_NOTIFY_WEBHOOK` | `0` | `1` posts notifications to a JSON endpoint |
| `VMR_WEBHOOK_URL` | — | the endpoint that receives the JSON |
| `VMR_WEBHOOK_SECRET` | — | signs the payload with HMAC-SHA256 |

#### Storage locations and API

| Variable | Default | Meaning |
|---|---|---|
| `VMR_DB` | `instance/vmrecovery.db` | the application database |
| `VMR_SECRET` | generated in `instance/secret.key` | Flask session signing key |
| `VMR_API_TOKEN` | — | bearer token for the JSON API. Empty means the API is off |
| `VMR_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

---

## Running it

```bash
python run.py                    # waitress WSGI server + the worker thread
VMR_DEV_SERVER=1 python run.py   # Flask's development server, for local work only
VMR_WORKER=0 python run.py       # the web interface without monitoring
VMR_SIMULATE=1 python run.py     # the built-in simulator
```

`run.py` serves the dashboard and runs the recovery worker in the same process. `SIGTERM` stops the
worker cleanly and exits, which is what `systemctl stop` sends.

**Two instances, one command.** The files decide which configuration a start picks up:

| Started as | Loads | Points at |
|---|---|---|
| `systemctl start vmrecovery` | `.env` and `instance/vmrecovery.env` | the production stack |
| `VMR_ENV=production python run.py` | the same two files | the production stack |
| `python run.py` | the same two files **and** `.env.local` | the local layer |

So a hand-started instance and the service can differ, and the difference should be deliberate. On
a lab host, keep `.env.local` pointing at the same database and port as the service and change only
the developer conveniences, so that starting the app by hand behaves exactly like the running
service. On a development machine, point `.env.local` at the simulator and a throwaway database
instead. Both shapes are in `.env.local.example`.

The health probe is public and machine readable:

```bash
curl -fsS http://127.0.0.1:5000/healthz
```

It answers `200` when the database and the worker are healthy, and `503` when the database is
unreachable, the worker is not running, or its last cycle is overdue, so a proxy or an uptime
monitor can use it directly. The body carries the disk figures as well.

---

## The dashboard

| Page | What it is for |
|---|---|
| **Dashboard** | machine status, one-click session start and end, bulk power actions, recent activity |
| **Virtual Machines** | register existing machines, clone from templates, edit policies, assign students |
| **VM detail** | one machine: power control, snapshots, backups, and its own event history |
| **VM Requests** | trainers request machines, administrators approve or reject them |
| **Users** | create accounts, reset passwords, change roles |
| **Event Log** | the full audit trail, filterable and downloadable as CSV |
| **Reports** | crashes against recoveries over time, per machine, with mean recovery time |
| **Settings** | live runtime configuration, API token, notification test |
| **System Health** | VirtualBox connectivity, worker status, storage, notification delivery log |
| **My Account** | change your own password |

---

## Roles and permissions

| | admin | trainer | student |
|---|:---:|:---:|:---:|
| See the dashboard | ✓ | ✓ | own machines only |
| Start and end training sessions | ✓ | ✓ | |
| Power control a machine | ✓ | ✓ | |
| Take a snapshot | ✓ | ✓ | |
| Restore a machine from a snapshot | ✓ | | |
| Restore a machine from an appliance backup | ✓ | | |
| Register, edit, and remove machines | ✓ | | |
| Clone from a template | ✓ | | |
| Approve machine requests | ✓ | | |
| Manage users | ✓ | | |
| Read the full event log | ✓ | ✓ | own machines only |
| Reports and settings | ✓ | | |
| Request a restore | ✓ | ✓ | ✓ |

A student only ever sees the events for the machines assigned to them.

---

## Training sessions

A class group can have **one active session at a time**, recorded in the `class_sessions` table and
enforced by a partial unique index. That makes the Start button safe to press repeatedly.

1. **Start session** starts powered-off, aborted, and saved machines, resumes paused ones, and takes
   one `pre-session` snapshot per machine whose policy enables it. The session is now active.
2. **Pressing Start again while the session is active does not duplicate snapshots.** The second
   press restarts machines that stopped and protects any machine added after the session opened (or
   whose snapshot failed or was pruned), but a machine that already has a pre-session snapshot for
   this session is left alone. The dashboard says *"Session for … is already active"* and the event
   log records `session_already_active`.
3. **End session** takes a final `post-session` snapshot of each running machine, optionally powers
   the group off, and marks the session ended. The next Start begins a fresh session.

---

## Cloning VMs from templates

Mark a registered machine as a **golden template** on the *Virtual Machines* page. Marking a template
takes a baseline snapshot if it has none, because a linked clone can only be made from a snapshot.

| Clone mode | VirtualBox option | Disk usage | Independence | Use it when |
|---|---|---|---|---|
| **Linked** | `clonevm --options link --snapshot <baseline>` | very small (differencing disk) | depends on the template's base disk | fast classroom provisioning; keep the template intact |
| **Full** | `clonevm --mode all` | full copy | complete independent machine and disk | long-lived or standalone student machines |

Every clone is registered and gets a `baseline` snapshot automatically. Deleting the template or its
base disk breaks linked clones, so keep templates registered while linked clones exist.

For a step-by-step demo with terminal commands, see [`docs/CLONING_GUIDE.md`](docs/CLONING_GUIDE.md).

---

## Notifications

Set up an email relay or a webhook, then press **Send a test notification** on the Settings page.
The System Health page shows the delivery log: what was sent, to whom, and whether it arrived.

The webhook receives JSON like this:

```json
{
  "source": "vmrecovery",
  "severity": "critical",
  "subject": "Crash detected: DEV-LAB-01",
  "message": "VirtualBox reports DEV-LAB-01 (Class A) as crashed. ...",
  "vm_id": 4,
  "timestamp": "2026-06-01 09:14:22"
}
```

When `VMR_WEBHOOK_SECRET` is set, the body is signed and the request carries an
`X-VMRecovery-Signature: sha256=<hex digest>` header. Verify it with:

```python
import hashlib, hmac
expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
assert hmac.compare_digest(expected, header.removeprefix("sha256="))
```

Notifications are sent for: a crash or freeze detected, a failed restore, a restore requested by a
student or trainer, a new machine request, and low host storage. A channel that fails is recorded
and never stops the recovery service.

---

## The JSON API

The API is read-only, token authenticated, and safe to expose to a monitoring system. It never
changes anything.

```bash
curl -H "Authorization: Bearer $VMR_API_TOKEN" http://127.0.0.1:5000/api/vms
```

| Endpoint | Returns |
|---|---|
| `GET /api/health` | liveness, worker state, disk, enabled channels. Public, no token needed |
| `GET /api/vms` | every registered machine with its status and policy |
| `GET /api/vms/<id>` | one machine with its snapshots, backups, and recent events |
| `GET /api/events` | the event log, with `vm_id`, `event_type`, `limit`, and `offset` |
| `GET /api/sessions` | the active training sessions |
| `GET /api/reports` | the same totals as the reports page, as JSON |
| `GET /api/notifications` | the notification delivery log |

While no token is configured the API answers `503` and says so, rather than exposing anything by
accident. A token can be set with `VMR_API_TOKEN` or generated from the Settings page. Full
reference: [`docs/API.md`](docs/API.md).

---

## Command line

`manage.py` does the same things as the dashboard, for a machine where the dashboard is not
reachable.

```bash
python manage.py init-db                     # create or upgrade the database
python manage.py create-user alice trainer   # add an account
python manage.py reset-password alice        # change a password
python manage.py set-role alice admin        # change a role
python manage.py delete-user alice
python manage.py list-users
python manage.py list-vms
python manage.py list-settings               # overrides and their effective values
python manage.py set-setting check_seconds 45
python manage.py reset-setting check_seconds
python manage.py check                       # run one monitoring cycle right now
python manage.py snapshot DEV-LAB-01
python manage.py restore DEV-LAB-01
python manage.py start-session "Class A"
python manage.py end-session "Class A"
python manage.py backup-db                   # back up the application database
python manage.py backup-db --list
python manage.py restore-db instance/db-backups/vmrecovery-20260601-091500.db
python manage.py export-events events.csv --days 30
python manage.py status
```

`create-user` and `reset-password` ask for the password interactively. Pass `--password` instead
when a script needs to do it unattended.

---

## Production deployment

The installer renders the systemd unit for the current checkout and user, creates the configuration
file, enables the service at boot, and prints the next steps:

```bash
./deploy/install_service.sh          # asks for sudo when it writes /etc/systemd/system
sudo systemctl start vmrecovery
sudo systemctl status vmrecovery
sudo journalctl -u vmrecovery -f     # live logs
```

The service restarts automatically, waits for VirtualBox, runs as the VM-owning user (with the
`vboxusers` group when it exists), and stops cleanly on `systemctl stop`.

**Behind a proxy with SSL.** Run Nginx as a reverse proxy in front of Waitress to enforce HTTPS, terminate TLS, and preserve client IP addresses across the lab network:

```bash
sudo ./deploy/setup_nginx_ssl.sh       # generates SSL cert with SAN, installs Nginx site config
sudo systemctl enable --now nginx
```

Full deployment architecture, SSL certificate setup, and network options are detailed in
[`docs/DEPLOYMENT_AND_SSL.md`](docs/DEPLOYMENT_AND_SSL.md).

A day in the life:

```bash
sudo systemctl status vmrecovery
curl -fsS http://127.0.0.1:5000/healthz | python -m json.tool
sudo journalctl -u vmrecovery --since today | grep -i alert
```

The operations runbook, with the failure modes and what to do about them, is in
[`docs/OPERATIONS.md`](docs/OPERATIONS.md).

---

## Security

- Passwords are hashed with Werkzeug's PBKDF2 and never stored or logged in the clear.
- Every state-changing request requires a CSRF token.
- Logins are rate limited per IP address, and the limits are configurable.
- Sessions expire after `VMR_SESSION_HOURS` and are `HttpOnly` and `SameSite=Lax`.
- Responses carry `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, and
  `Referrer-Policy` headers, and HTML is never cached.
- The API is token authenticated and read-only.
- Students are scoped to their own machines.
- The database, the secret key, the backups, and the `.env` files live under paths that are excluded
  from git.

**Before putting this on a network:** change the `admin` password, set `VMR_SECRET` to a value you
keep, and put it behind a reverse proxy with TLS.

---

## Backups and disaster recovery

There are three things worth backing up, and the system does two of them for you.

| What | How | Where |
|---|---|---|
| Independent VM backups | **Automatic** — on demand from the UI, or `manage.py` | `instance/backups/` |
| The application database | **Automatic** — the worker rotates one every hour | `instance/db-backups/` |
| The configuration | **Manual** — copy `.env` and `instance/vmrecovery.env` somewhere safe | — |

The database backup uses SQLite's online backup API, so a copy taken while the service is running is
consistent rather than a torn copy of a live file. To restore:

```bash
sudo systemctl stop vmrecovery
python manage.py restore-db instance/db-backups/vmrecovery-20260601-091500.db
sudo systemctl start vmrecovery
```

If the machine that owns the VirtualBox VMs is lost entirely, the independent `.ova` files are what
you restore from: import them on the new host and register them again.

---

## Troubleshooting

**"VirtualBox is not reachable" on the dashboard.**
`VBoxManage` is not installed, not on `PATH`, or the service user is not in the `vboxusers` group.
Check it by hand: `VBoxManage --version`. Then `id nomad | grep vboxusers`.

**The worker is not running.**
`VMR_WORKER=0` is set somewhere, or the unit failed to start. `journalctl -u vmrecovery` will say
which. `manage.py check` runs one cycle in the foreground and prints the summary.

**A machine is restored but the student loses their work.**
Restoring always loses everything after the snapshot. The snapshot interval is the trade-off: a
shorter interval protects less between snapshots but costs more storage. Change it on the machine's
edit page.

**A machine keeps being restored.**
The restore limit is three per hour, after which the system stops and raises an alert rather than
looping. Look for `alert` events on that machine.

**Disk is filling up.**
Check *System Health* for the free space. Independent `.ova` backups are the usual culprit: lower
`VMR_BACKUP_RETENTION`, delete old ones from the backups page, or point `VMR_BACKUP_DIR` at a
bigger disk.

**A paused machine gets restored.**
It should not: a deliberate pause is remembered (`admin_paused`) and the monitor leaves it alone. If
it happens, the pause was done in VirtualBox directly rather than through the dashboard.

**Everything is in simulation mode.**
`.env.local` sets `VMR_SIMULATE=1` and it was loaded. It is skipped under systemd; check that the
service is started by systemd and not by hand from a shell.

---

## Development

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                       # 119 tests, no VirtualBox needed
```

The tests use the simulator, so they run anywhere. A typical change:

```bash
git switch -c feature/my-change
# ... edit, then:
python -m pytest -q
```

The project layout is small enough to read in one sitting. `app/services.py` holds the logic,
`app/views.py` holds the pages, `app/vbox.py` is the only module that talks to VirtualBox, and
`app/db.py` owns the schema.

### Schema changes

`app/schema.sql` is the source of truth and is applied on every start with `CREATE TABLE IF NOT
EXISTS`, so it never destroys data. To change an existing table, add a numbered migration to
`MIGRATIONS` in `app/db.py` and bump `SCHEMA_VERSION`. Migrations run once and are recorded in the
`schema_meta` table, so a deployment can be upgraded in place.

---

## Project layout

```
app/
  __init__.py     the Flask application, security headers, startup wiring
  config.py       settings, the layered .env loader, runtime overrides
  db.py           connections, the schema, migrations, database backup
  schema.sql      the database design
  services.py     the core logic: registry, snapshots, backups, recovery, reports
  vbox.py         the only module that talks to VirtualBox (real and simulated)
  notifier.py     email and webhook delivery, and the delivery log
  worker.py       the background monitoring and recovery loop
  views.py        the web pages
  api.py          the read-only JSON API
  templates/      the Jinja templates
  static/         the stylesheet
tests/            the test suite
deploy/           the systemd unit and the installer
docs/             the operations runbook, the API reference, the cloning guide
manage.py         the command line admin tool
run.py            the entry point
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the pieces fit together, and
[`CHANGELOG.md`](CHANGELOG.md) for what changed.
