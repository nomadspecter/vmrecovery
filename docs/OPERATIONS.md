# Operations runbook

Everything an administrator needs to install, run, check, and fix the service.

---

## 1. Install

On the host that owns the VirtualBox machines:

```bash
sudo apt install python3-venv virtualbox       # or the equivalent for your distribution
cd /opt
sudo git clone <repository> vmrecovery
cd vmrecovery

sudo useradd --system --create-home --home-dir /opt/vmrecovery vmrecovery
sudo chown -R vmrecovery:vmrecovery /opt/vmrecovery

sudo -u vmrecovery python3 -m venv .venv
sudo -u vmrecovery .venv/bin/pip install -r requirements.txt
```

Add the service user to the VirtualBox group so it can talk to the installed VMs:

```bash
sudo usermod -aG vboxusers vmrecovery
```

Copy the configuration and edit it:

```bash
sudo -u vmrecovery cp .env.example .env
sudo -u vmrecovery cp deploy/vmrecovery.env.example instance/vmrecovery.env
sudo -u vmrecovery cp .env.local.example .env.local    # optional
sudo -u vmrecovery nano .env
```

At minimum, set these in `.env`:

| Variable | Why |
|---|---|
| `VMR_SECRET` | the session signing key. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `VMR_API_TOKEN` | the token for the read-only JSON API. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `VMR_DB` | an absolute path to the database file |
| `VMR_BACKUP_DIR` | an absolute path with room for the `.ova` files |
| `VMR_VBOXMANAGE` | the absolute path to `VBoxManage`, because systemd gives the service a minimal `PATH` |
| `VMR_HOST` | `127.0.0.1` when a reverse proxy is in front |

The installer in the next section generates the first two for you when it creates `.env`.

Create the first administrator:

```bash
sudo -u vmrecovery .venv/bin/python manage.py create-user admin
```

The password is asked for interactively and must be at least 8 characters. `manage.py` creates the
database and applies any pending migrations on the way.

---

## 2. Run it as a service

```bash
sudo ./deploy/install_service.sh
sudo systemctl daemon-reload
sudo systemctl enable --now vmrecovery
sudo systemctl status vmrecovery
```

The installer renders `deploy/vmrecovery.service` for the current checkout and user and writes it
to `/etc/systemd/system`. It reads `.env` and then `instance/vmrecovery.env`; the unit sets
`VMR_ENV=production`, which is what makes the system ignore `.env.local`.

If `.env` does not exist yet, the installer creates it from `.env.example` and fills in a fresh
session key and API token, and prints the token. If it does exist, the installer leaves it alone —
it never overwrites a configuration that is already in place.

```bash
grep VMR_API_TOKEN .env        # the token for the JSON API
```

The machine layer is created from `deploy/vmrecovery.env.example` and holds the effective
configuration of the service on this host.

If the unit needs adjusting:

```bash
sudo systemctl edit vmrecovery       # a drop-in override
sudo systemctl daemon-reload
sudo systemctl restart vmrecovery
```

The service restarts automatically after a crash, starts after VirtualBox, runs as the VM-owning
user, and applies `UMask=0077` so the database and the secret key are not world-readable.

### Without systemd

```bash
VMR_ENV=production .venv/bin/python run.py
```

The process serves the app with waitress and runs the worker in the same process. `SIGTERM` stops
the worker cleanly and exits.

---

## 3. Secure Ingress with Cloudflare Zero-Trust Tunnel & Cloud Deployment

For secure off-premises and campus-wide access without port forwarding or exposed router ports, use the Cloudflare Zero-Trust tunnel (`cloudflared`):

```bash
# Run the automated Cloudflare tunnel setup script:
./deploy/install_cloudflare_tunnel.sh
```

This tooling:
1. Creates an encrypted, outbound-only tunnel to Cloudflare's global edge network.
2. Automatically terminates SSL/TLS with wildcard certificates at the edge.
3. Forwards requests locally to Waitress on `http://127.0.0.1:5000`.
4. Mitigates DDoS attacks and eliminates public port vulnerability.

Access options:
- Local browser: `http://127.0.0.1:5000`
- Zero-Trust tunnel: `https://vmrecovery.lab.domain` (or Cloudflare quick tunnel URL)
- Cloud demonstration platform: `https://vmrecovery-demo.onrender.com` (Render PaaS + Supabase Managed PostgreSQL)

See [`docs/DEPLOYMENT_AND_SSL.md`](DEPLOYMENT_AND_SSL.md) for full hybrid edge-cloud architecture and configuration details.

---

## 4. Health checks

```bash
curl -fsS http://127.0.0.1:5000/healthz | python -m json.tool
```

`200` means the database, the worker, and the disk are all healthy. `503` means the worker is not
running or its last cycle is overdue. A monitoring system can poll it directly:

```
# 5xx means the service is down, 200 is fine
curl -fsS http://127.0.0.1:5000/healthz
```

The dashboard's **System Health** page shows the same information, plus the VirtualBox
connectivity check and the notification delivery log.

The API's `GET /api/health` reports the same state as JSON and needs no token.

---

## 4. Everyday tasks

| I want to… | Do this |
|---|---|
| Check the service | `systemctl status vmrecovery` |
| Read the logs | `journalctl -u vmrecovery -f` |
| The logs of yesterday | `journalctl -u vmrecovery --since yesterday` |
| Follow one machine | `journalctl -u vmrecovery -f \| grep DEV-LAB-01` |
| Run a monitoring cycle now | `python manage.py check` |
| Change a threshold | **Settings** on the dashboard, or `python manage.py set-setting check_seconds 45` |
| See the current settings | `python manage.py list-settings` |
| Back up the database | `python manage.py backup-db` |
| Export the event log | `python manage.py export-events events.csv --days 30` |
| Start a training session | **Dashboard → Start session**, or `python manage.py start-session "Class A"` |
| Add a machine | **Virtual Machines → Register**, then `python manage.py list-vms` to confirm |

Settings changed on the dashboard take effect on the next monitoring cycle. There is no restart and
no reload.

---

## 5. Notifications

Configure a channel in `.env` (or on the Settings page) and test it:

```bash
# on the dashboard: Settings -> Send a test notification
```

The test writes a row to the `notifications` table whatever happens, so you can see the outcome
even when the mail server is unreachable.

| Problem | What to check |
|---|---|
| Nothing arrives | `VMR_NOTIFY_EMAIL=1`, `VMR_SMTP_HOST`, `VMR_SMTP_TO` are set; the *System Health* page lists the enabled channels |
| "Connection refused" | the host and port are right, and the server is reachable from this host |
| "SMTP auth failed" | `VMR_SMTP_USER` and `VMR_SMTP_PASSWORD`; some relays want the full address as the username |
| "certificate verify failed" | the server's certificate is not trusted here; add its CA to `/etc/ssl/certs` rather than disabling verification |
| The webhook returns a non-2xx | the URL is wrong, or the endpoint expects a different payload; the `error` column on the delivery log has the status |
| The signature does not match | the receiver must sign the **raw request body**, not the re-serialised JSON |

The webhooks carry an `X-VMRecovery-Signature: sha256=<hex>` header when `VMR_WEBHOOK_SECRET` is
set. The receiver should verify it before acting on the message.

---

## 6. Backups

### The application database

The worker takes one every hour into `VMR_DB_BACKUP_DIR` and keeps `VMR_DB_BACKUP_KEEP` of them.
To take one by hand:

```bash
python manage.py backup-db
python manage.py backup-db --list
```

To restore:

```bash
sudo systemctl stop vmrecovery
python manage.py restore-db instance/db-backups/vmrecovery-20260601-091500.db
sudo systemctl start vmrecovery
```

The copy is made with SQLite's online backup API, so it is consistent even while the service is
running. Restore it while the service is stopped, or the running process will keep writing to the
old file.

### The virtual machines

Independent `.ova` exports live in `VMR_BACKUP_DIR`. Take one from the machine's page (**Back up
now**) or from the command line:

```bash
python manage.py snapshot DEV-LAB-01       # a snapshot, in VirtualBox
```

A snapshot is cheap and fast but shares the disk with the machine. An independent export is a
complete appliance and survives the loss of that disk, but it is slow and large. Use both: the
snapshot for fast recovery, the export for disaster recovery.

Check what is being kept:

```bash
du -sh instance/backups/
ls -lh instance/backups/
```

### What is not backed up

The configuration. Copy `.env` and `instance/vmrecovery.env` somewhere safe. A lost `VMR_SECRET`
invalidates every session but is otherwise harmless.

---

## 7. Failure modes

### The service will not start

```bash
sudo systemctl status vmrecovery
sudo journalctl -u vmrecovery -n 50 --no-pager
```

| Message | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: flask` | the virtualenv is not being used | the unit points at `.venv/bin/python`; check `WorkingDirectory` and `ExecStart` |
| `unable to open database file` | the path in `VMR_DB` does not exist or is not writable by the service user | `sudo chown -R vmrecovery:vmrecovery /opt/vmrecovery` and create the directory |
| `Address already in use` | something else is on the port | `sudo ss -ltnp \| grep 5000`, then change `VMR_PORT` |
| `Permission denied` on the secret key | `instance/` is not owned by the service user | `sudo chown -R vmrecovery:vmrecovery /opt/vmrecovery/instance` |

### VirtualBox is not reachable

```bash
VBoxManage --version
sudo -u vmrecovery VBoxManage list vms
```

| Symptom | Cause |
|---|---|
| `VBoxManage: command not found` | it is not installed, or `VMR_VBOXMANAGE` does not point at it |
| `VBoxManage: error: Could not find a registered machine named ...` | the UUID in the registry does not match a machine on this host |
| `VBoxManage: error: Cannot open the VirtualBox management XML file` | the service user has no access to `~/.config/VirtualBox` — usually a home directory or group problem |
| `insufficient permissions` | the service user is not in `vboxusers`; `id vmrecovery \| grep vboxusers` |

The *System Health* page runs the same check and shows the error text.

### The worker is not running

The worker runs inside the web process. If it is missing, the service started with `VMR_WORKER=0`
or it crashed out of its loop.

```bash
python manage.py status
python manage.py check          # runs one cycle in the foreground and prints the summary
journalctl -u vmrecovery | grep -i worker
```

### A machine is being restored over and over

The restore limit is `VMR_MAX_RESTORES_PER_HOUR` (three by default). After that the system stops
and raises an alert rather than looping. Look at the event log for that machine:

```bash
sqlite3 instance/vmrecovery.db "SELECT created_at, event_type, details FROM events WHERE vm_id=4 ORDER BY event_id DESC LIMIT 20;"
```

A machine that crashes on the same snapshot every time has a problem inside the image, not with
the recovery system. Restore a working image as its template and re-provision from that.

### A machine is paused and should not be

A machine paused from the dashboard is remembered (`admin_paused = 1`) and left alone. A machine
paused directly in VirtualBox looks frozen to the monitor and will be restored. That is intended:
a pause outside the dashboard is indistinguishable from a freeze.

### The disk is filling up

```bash
df -h /opt/vmrecovery
du -sh instance/backups instance/db-backups
```

The `.ova` exports are the usual culprit. Lower `VMR_BACKUP_RETENTION`, delete the old files, or
point `VMR_BACKUP_DIR` at a bigger disk. The worker warns when free space drops below
`VMR_DISK_MIN_FREE_GB` or `VMR_DISK_MIN_FREE_PCT`.

### Everything is in simulation mode

`.env.local` sets `VMR_SIMULATE=1`, and it was loaded. It is skipped when the process runs under
systemd or with `VMR_ENV=production`. Check that the service really is started by systemd:

```bash
systemctl show vmrecovery -p Environment
```

### The dashboard is up but the API answers 503

No token is configured. Set `VMR_API_TOKEN` in `.env`, or generate one on **Settings → API
token**, then restart the service.

---

## 8. Upgrading

```bash
cd /opt/vmrecovery
sudo systemctl stop vmrecovery
sudo -u vmrecovery git pull
sudo -u vmrecovery .venv/bin/pip install -r requirements.txt
sudo -u vmrecovery .venv/bin/python manage.py init-db    # applies pending migrations
sudo systemctl start vmrecovery
sudo systemctl status vmrecovery
```

`init-db` is safe to run twice and never destroys data: the tables are created with
`CREATE TABLE IF NOT EXISTS`, and the numbered migrations run exactly once and are recorded in
`schema_meta`. The service also applies them on start-up, so the explicit call is only there so
that a failed migration is noticed before the service is started again.

Take a database backup before an upgrade:

```bash
python manage.py backup-db
```

---

## 9. A routine week

**Monday.** Check that the backups exist and the service is healthy.

```bash
ls -lt instance/db-backups/ | head
curl -fsS http://127.0.0.1:5000/healthz
```

**Midweek.** Look at the recovery report. A cluster of recoveries on one machine usually means an
image problem, not a monitoring problem.

```bash
python manage.py export-events week.csv --days 7
```

**Friday.** Confirm the notification channels still work. A relay that quietly stopped accepting
mail is the usual reason a lab finds out about an outage from a student.

```bash
sqlite3 instance/vmrecovery.db "SELECT created_at, status, error FROM notifications ORDER BY notification_id DESC LIMIT 10;"
```

**Before a term starts.** Make sure the templates still exist and the snapshot interval is right,
and take a fresh independent backup of each golden template.
