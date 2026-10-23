# API reference

The JSON API is **read-only**. Every endpoint is a `GET`, nothing changes state, and nothing
returns a credential. It is meant for an uptime monitor, a chat bot, a provisioning script, or a
dashboard of your own.

## Authentication

The API needs a token. Send it in either header:

```bash
curl -H "Authorization: Bearer $VMR_API_TOKEN" http://127.0.0.1:5000/api/vms
curl -H "X-API-Token: $VMR_API_TOKEN"     http://127.0.0.1:5000/api/vms
```

The token is set with `VMR_API_TOKEN` in the environment, or generated from **Settings → API
token** on the dashboard. It is compared with `hmac.compare_digest`, so the comparison does not leak
its length through timing.

While no token is configured the API is off and answers `503`:

```json
{ "error": "The API is disabled. Set VMR_API_TOKEN or add an API token on the Settings page." }
```

A wrong or missing token answers `401`:

```json
{ "error": "A valid API token is required." }
```

`GET /api/health` is the one exception: it needs no token, so a health probe stays simple.

## Endpoints

### `GET /api/health`

Liveness, worker state, disk, and the enabled notification channels. No token required.

```json
{
  "status": "ok",
  "version": 1,
  "worker": { "running": true, "last_cycle": "2026-06-01 09:14:00", "cycles": 118 },
  "disk": { "free_gb": 142.7, "free_pct": 68.1, "low": false },
  "notifications": { "channels": ["email", "webhook"] },
  "time": "2026-06-01 09:15:04"
}
```

`status` is `"ok"` when the service is up. It does not change based on the worker, so a probe
should read `worker.running` and `disk.low` as well.

### `GET /api/vms`

Every registered machine.

```json
{
  "vms": [
    {
      "vm_id": 4,
      "name": "DEV-LAB-01",
      "uuid": "1a2b3c4d-...",
      "class_group": "Class A",
      "status": "running",
      "fail_count": 0,
      "is_template": false,
      "student": "jane",
      "interval_minutes": 30,
      "retention_count": 3,
      "last_snapshot": "2026-06-01 09:10:00",
      "last_checked": "2026-06-01 09:14:58",
      "backup_count": 2
    }
  ]
}
```

`status` is one of `running`, `poweroff`, `paused`, `crashed`, `frozen`, `busy`, `aborted`,
`unknown`.

### `GET /api/vms/<id>`

One machine with its snapshots, its independent backups, and its last 25 events. Answers `404`
when the id is unknown.

```json
{
  "vm": { "vm_id": 4, "name": "DEV-LAB-01", "…": "…" },
  "snapshots": [
    { "snapshot_id": 12, "vm_id": 4, "snapshot_name": "auto-20260601-091000",
      "snapshot_type": "auto", "created_at": "2026-06-01 09:10:00" }
  ],
  "backups": [
    { "backup_id": 3, "backup_name": "DEV-LAB-01-20260601-090000",
      "size_bytes": 2147483648, "created_at": "2026-06-01 09:00:00" }
  ],
  "events": [ { "event_id": 88, "event_type": "vm_restored", "…": "…" } ]
}
```

### `GET /api/events`

The audit trail.

| Parameter | Default | Meaning |
|---|---|---|
| `limit` | `100` | how many rows to return, 1 to 1000 |
| `offset` | `0` | how many rows to skip |
| `vm_id` | all | only this machine |
| `event_type` | all | only this type, for example `vm_restored` |

```bash
curl -H "Authorization: Bearer $VMR_API_TOKEN" \
  "http://127.0.0.1:5000/api/events?vm_id=4&event_type=vm_restored&limit=50"
```

```json
{
  "total": 34,
  "limit": 50,
  "offset": 0,
  "events": [
    { "event_id": 88, "vm_id": 4, "user_id": null, "event_type": "vm_restored",
      "details": "Restored from auto-20260601-091000", "result": "Success",
      "duration_seconds": 12.4, "created_at": "2026-06-01 09:14:22" }
  ]
}
```

`total` is the number of rows matching the filter, not the number returned, so a client can page.

### `GET /api/sessions`

The training sessions that are currently active.

```json
{
  "sessions": [
    { "session_id": 3, "class_group": "Class A", "status": "active",
      "started_by": 1, "started_at": "2026-06-01 09:00:00",
      "ended_by": null, "ended_at": null }
  ]
}
```

### `GET /api/reports`

The same totals as the reports page.

| Parameter | Default | Meaning |
|---|---|---|
| `start` | 30 days ago | `YYYY-MM-DD` |
| `end` | today | `YYYY-MM-DD` |
| `class_group` | `All` | one class group, or `All` |

```json
{
  "totals": {
    "snapshots": 412,
    "crashes": 31,
    "auto_recovered": 28,
    "manual_recovered": 1,
    "manual_action": 4,
    "backups": 12,
    "mean_recovery_seconds": 14.8
  },
  "weekly": [
    { "week": "2026-W18", "crashes": 9, "recoveries": 9 }
  ],
  "per_vm": [
    { "vm_id": 4, "vm_name": "DEV-LAB-01", "class_group": "Class A",
      "crashes": 7, "recoveries": 7, "snapshots": 96, "mean_seconds": 12.4 }
  ]
}
```

`auto_recovered` counts the restores the service did on its own; `manual_recovered` counts the ones
a person asked for. `mean_recovery_seconds` is `null` when nothing was recovered in the period.

### `GET /api/notifications`

The delivery log: what was sent, to whom, whether it arrived, and the error when it did not.

```json
{
  "notifications": [
    { "notification_id": 12, "vm_id": 4, "channel": "email",
      "recipient": "admin@example.org", "subject": "Crash detected: DEV-LAB-01",
      "body": "…", "severity": "critical", "status": "sent", "error": "",
      "created_at": "2026-06-01 09:14:22", "sent_at": "2026-06-01 09:14:23",
      "vm_name": "DEV-LAB-01" }
  ]
}
```

`status` is `sent`, `failed`, or `skipped`. A `skipped` row with the channel `none` means no
notification channel was configured at the time.

## Errors

| Status | Meaning |
|---|---|
| `200` | the request succeeded |
| `401` | the token is missing or wrong |
| `404` | the machine does not exist |
| `503` | the API is disabled because no token is configured |

Every error is JSON with an `error` key.

## Rate limiting and access

There is no built-in rate limiter on the API, so keep the token out of shared places and put the
service behind a reverse proxy if it is reachable from a wide network. The API never returns
password hashes, session cookies, SMTP passwords, or the webhook secret.
