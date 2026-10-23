# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

The release that turns a working prototype into a service you can leave running.

### Added

**Configuration**

- Layered configuration: real environment variables, `.env.local`,
  `instance/vmrecovery.env`, `.env`, and database overrides, each with a documented priority.
- `.env.local` is ignored in production, detected by `VMR_ENV=production` or by running under
  systemd (`INVOCATION_ID`). A developer's simulator configuration can no longer take the
  production service off the real data.
- Runtime settings stored in the database and applied on the next monitoring cycle, editable from
  a new **Settings** page without a restart.
- `.env.example` and `.env.local.example`, fully annotated.
- Six new settings, settable from the environment or from the Settings page:
  `VMR_VBOX_QUERY_TIMEOUT` (60) bounds a read-only `VBoxManage` query,
  `VMR_VBOX_ACTION_TIMEOUT` (180) bounds a short command such as power off, suspend or start,
  `VMR_VBOX_RESTORE_TIMEOUT` (600) bounds a snapshot restore, which merges the differencing
  disks and takes minutes,
  `VMR_VBOX_LOCK_TIMEOUT` (30) bounds the wait for the global VirtualBox lock,
  `VMR_LIVE_SNAPSHOTS` (off) opts in to `--live` snapshots, and
  `VMR_BUSY_TIMEOUT` (300) bounds how long VirtualBox may stay busy.

**Notifications**

- `app/notifier.py`: email over SMTP with STARTTLS, and a JSON webhook with an HMAC-SHA256
  `X-VMRecovery-Signature` header.
- Every delivery attempt is recorded — sent, failed, or skipped — and shown on the System Health
  page. A failing channel never stops the recovery service.

**API**

- `app/api.py`: a read-only, token-authenticated JSON API with `/api/health`, `/api/vms`,
  `/api/vms/<id>`, `/api/events`, `/api/sessions`, `/api/reports`, and `/api/notifications`.
- The token is accepted as `Authorization: Bearer` or `X-API-Token`, compared with
  `hmac.compare_digest`. While no token is configured the API answers `503` rather than exposing
  anything.
- An API token can be generated from the Settings page.

**Operations**

- Power control per machine — start, stop, pause, resume — and a bulk action over a selection.
- `vms.admin_paused`, so a machine an administrator paused on purpose is not mistaken for a frozen
  one and restored.
- A **My Account** page, so any user can change their own password.
- A per-machine detail page with its own snapshots, backups, and event history.
- The event log is paginated, filterable, and downloadable as CSV.
- Independent database backup and restore, using SQLite's online backup API, taken automatically
  every hour and rotated.
- Hourly housekeeping in the worker: event pruning and the database backup.
- `manage.py` grew from two commands to twenty: user management, settings, snapshots, restores,
  sessions, database backup and restore, and a CSV export of the event log.
- The installer generates a session key and an API token when it creates `.env`, so a new
  installation is usable immediately instead of leaving both empty. It also installs the machine
  layer from `deploy/vmrecovery.env.example` rather than from the shared template.
- Deleting a machine can optionally delete it from VirtualBox as well.
- Recovery durations are recorded as a number, and the reports page shows the mean.
- A notification can be sent from the command line for testing.
- A **Retry Clone** button on the request list, for a request that failed, so the clone can be
  tried again without writing the request from scratch.

**Documentation**

- A rewritten `README.md` with the full environment-variable reference, the feature list, the
  permission matrix, and the troubleshooting guide.
- `ARCHITECTURE.md` covers the new modules, the migration system, and the configuration layers.
- `docs/OPERATIONS.md`, an install-and-run runbook with the failure modes.
- `docs/API.md`, the API reference.

### Changed

- The schema is now versioned. `app/schema.sql` is applied with `CREATE TABLE IF NOT EXISTS`, and
  changes to existing tables are numbered migrations in `app/db.py` that run once and are recorded
  in `schema_meta`. `SCHEMA_VERSION` is 7.
- The index block in `schema.sql` is applied after the migrations, because an index on a column an
  old database does not have yet cannot be created. Each index is created in its own
  `try/except`, so one that cannot be built does not stop the service.
- The login rate limit is configurable instead of hard-coded.
- The systemd unit sets `VMR_ENV=production` and reads `.env` then `instance/vmrecovery.env`.
- `deploy/vmrecovery.env.example` was removed; `instance/vmrecovery.env` is now the machine-specific
  override file, and is excluded from git.
- `Settings.to_dict()` redacts the secret key, the SMTP password, the webhook secret, and the API
  token, so a configuration dump can be pasted into a ticket.

### Fixed

- Resetting a setting on the Settings page did not take effect in the running service. The
  override was removed from the database, but the live settings object kept the overridden value
  until the process was restarted, so the database and the running service disagreed. The
  configured values are now remembered, and every application of the overrides starts from them
  again, so removing an override puts the setting back immediately.
- The configuration files were applied in the wrong order. The loader kept the value from the
  *first* file that defined a variable, so `instance/vmrecovery.env` and `.env.local` could never
  override `.env`, which is the opposite of what the documentation promised. The files are now
  read from the lowest priority to the highest, so a later file wins, and a real environment
  variable still wins over every file.
- The `INVOCATION_ID` check no longer treats any shell started from a systemd service as
  production. systemd passes that variable to everything it spawns, so it is now only trusted when
  the process is systemd's own main process.
- The `.env.local` skip now matches the actual file rather than any file with the same name.
- Every connection asked SQLite to switch the journal mode to WAL, which took a lock for nothing:
  the mode is a property of the file, not of the connection. It is now set only when it is needed,
  and the busy timeout is applied before it.
- The SQLite sidecar files (`-wal`, `-shm`) of a second database in `instance/` were not excluded
  from git, so a live write-ahead log could have been committed.
- A foreign-key rewrite bug during a table migration. Very old databases could be left with tables
  pointing at a table that no longer exists. Migration 6 repairs them from the canonical
  definitions, carrying the rows over.
- The `users` table is rebuilt so the `student` role is allowed. An older `CHECK` constraint knew
  only `admin` and `trainer`.
- `users.created_at` is added with a constant default and backfilled, because SQLite refuses a
  non-constant default in `ALTER TABLE`.
- Two database backups taken in the same second no longer collide; the second gets a numbered
  suffix.
- A failure to record a notification no longer raises, so a foreign-key problem cannot take down
  the caller.
- The webhook signature header is compared case-insensitively, because HTTP header names are
  case-insensitive and `urllib` normalises the case.
- A live snapshot (`--live`) of a running guest that does not support live snapshots never
  returned. It held the global VirtualBox lock, so the monitoring worker and every dashboard
  button froze. Live snapshots are now opt-in, and the snapshot command is bounded by a timeout.
- VirtualBox's `onlinesnapshotting` state was missing from the list of transitional states, so a
  machine stuck in the middle of a snapshot was reported as powered off. The state vocabulary is
  now complete, and an unfamiliar state word is reported as `unknown` rather than `powered off`.
- `VBoxManage clonevm` refuses to clone a running machine. The template is now suspended, allowed
  to settle, cloned, and put back the way it was found.
- `savestate` followed immediately by a clone or an export was a race: VirtualBox had not finished
  tearing the running process down. The saved state is now waited for before the next command runs.
- Failed actions were only flash messages and left no trace. Failures are now logged, and the
  access log records every request with its status.
- A machine stuck in a transitional state is now reported as `needs_admin` and raises an alert,
  instead of being silently misread as powered off.
- The monitoring worker now skips a machine it cannot reach instead of blocking, and a web action
  gives up on the VirtualBox lock with a clear message instead of waiting forever.
- A failed clone left its disk in VirtualBox's media registry even though the machine was never
  registered. Every later attempt to clone the same name then failed with the same bare
  `Clone VM failed`, and the name stayed unusable until the registry was cleaned by hand. A failed
  clone is now cleared away — the leftover disks are taken out of the registry and the folder is
  removed — and the clone is tried once more.
- A clone of a suspended template inherited its saved state, and a machine that is still suspended
  cannot be started cleanly. The saved state is now thrown away, so a new machine is always left
  powered off and ready to boot.
- Every `VBoxManage` command now has its own timeout. The short commands get minutes instead of the
  30-minute long-operation timeout, so a hung command can no longer hold the VirtualBox lock for
  half an hour and freeze the dashboard and the background worker.
- Two commands that depend on each other are now separated by a wait for the machine to settle:
  powering a machine off and starting it again, restoring a snapshot and starting it, taking a
  snapshot and deleting the old ones, and cloning a machine and taking its baseline snapshot.
  VirtualBox refuses the second command while the first is still in progress, which is what
  produced `Current object state prohibits operation` and `Clone VM failed`.
- The VirtualBox error code is now kept in the message the user sees. VirtualBox writes it behind
  its own `VBoxManage: error: ` prefix, so it was never picked up and the message only ever said
  `Clone VM failed` without saying why.
- Deleting a machine now waits for the VirtualBox lock like every other action, so a delete cannot
  run at the same time as the worker is taking a snapshot of the same machine.
- The reason of a failed request is now only shown while the request is actually failed or
  rejected, and not carried along on a request that later succeeded.

## [1.0.0] — 2026-10-12

The initial working system.

- A Flask dashboard with login, a machine registry, per-machine snapshot policies, and a
  background monitoring worker.
- Crash and freeze detection with automatic restore from the newest snapshot.
- The `VBoxManage` interface, with a built-in simulator for demonstrations and tests.
- The system health page and the `/healthz` probe.
- Independent `.ova` appliance backups, template cloning, the VM request queue, low-disk
  monitoring, the student role, web user administration, recovery duration tracking, and the
  systemd service.
- Better `VBoxManage` output parsing and error extraction.
- The initial `deploy/` unit and installer.

## [0.1.0] — 2026-10-12

- The first commit: the automated Virtual Machine recovery system, its schema, the VirtualBox
  interface, the worker, and the first pages.
