"""Outbound notifications: email and webhooks.

The dashboard used to say "the administrator has been notified" without
anything actually happening. This module makes that true. Every notification
is written to the ``notifications`` table first, so the dashboard can show
what was sent, to whom, and whether it arrived, whether or not a channel is
configured at all.

Channels are configured through environment variables and can be overridden
from the Settings page:

    VMR_NOTIFY_EMAIL=1
    VMR_SMTP_HOST=smtp.example.org
    VMR_SMTP_PORT=587
    VMR_SMTP_USER=vmrecovery@example.org
    VMR_SMTP_PASSWORD=...
    VMR_SMTP_FROM=vmrecovery@example.org
    VMR_SMTP_TO=admin@example.org,lab.manager@example.org

    VMR_NOTIFY_WEBHOOK=1
    VMR_WEBHOOK_URL=https://chat.example.org/hooks/vmrecovery
    VMR_WEBHOOK_SECRET=shared-secret-for-signing
"""
import hashlib
import hmac
import json
import logging
import smtplib
import sqlite3
import urllib.error
import urllib.request
from email.message import EmailMessage

from .services import ts, now_local

log = logging.getLogger("vmrecovery")

# The effective channel configuration, refreshed whenever the settings change.
_CONFIG: dict = {"email": False, "webhook": False}


def configure(settings) -> None:
    """Point the notifier at the channels described by ``settings``."""
    global _CONFIG
    _CONFIG = {
        "email": bool(getattr(settings, "notify_email_enabled", False)
                      and getattr(settings, "smtp_host", "")),
        "webhook": bool(getattr(settings, "notify_webhook_enabled", False)
                        and getattr(settings, "webhook_url", "")),
    }
    log.info("Notification channels enabled: %s",
             ", ".join(k for k, v in _CONFIG.items() if v) or "none")


def enabled_channels() -> list:
    return [name for name, on in _CONFIG.items() if on]


def _record(conn, channel, recipient, subject, body, severity, status, error="", vm_id=None,
            now=None):
    """Write the delivery attempt to the notifications table.

    A failure here is logged but not raised: losing the audit record is bad,
    but losing the caller because of it is worse.
    """
    now = now or now_local()
    try:
        conn.execute(
            "INSERT INTO notifications (vm_id, channel, recipient, subject, body, severity, status, "
            "error, created_at, sent_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (vm_id, channel, recipient, subject, body, severity, status, error, ts(now),
             ts(now) if status == "sent" else None))
        conn.commit()
    except sqlite3.Error as exc:
        log.warning("Could not record the notification attempt: %s", exc)


def _send_email(settings, recipient, subject, body):
    """Deliver one message over SMTP. Raises on failure."""
    host = settings.smtp_host
    port = settings.smtp_port
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from or settings.smtp_user or "vmrecovery@localhost"
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


def _send_webhook(settings, subject, body, severity, vm_id):
    """POST the notification as JSON to the configured webhook."""
    payload = {
        "source": "vmrecovery",
        "severity": severity,
        "subject": subject,
        "message": body,
        "vm_id": vm_id,
        "timestamp": ts(now_local()),
    }
    raw = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "VMRecovery/1.0"}
    if settings.webhook_secret:
        signature = hmac.new(settings.webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
        headers["X-VMRecovery-Signature"] = f"sha256={signature}"
    request = urllib.request.Request(settings.webhook_url, data=raw, headers=headers,
                                     method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status >= 300:
            raise RuntimeError(f"webhook returned HTTP {response.status}")


def send(conn, settings, subject, body, severity="info", vm_id=None, now=None) -> list:
    """Send a notification over every enabled channel.

    Returns one result dictionary per channel. A channel that fails never
    stops the others, and a failure is recorded rather than raised: a broken
    mail server must not take the recovery service down with it.
    """
    now = now or now_local()
    results = []
    channels = enabled_channels()
    if not channels:
        _record(conn, "none", "", subject, body, severity, "skipped",
                "No notification channel is configured", vm_id, now)
        return results

    if "email" in channels:
        recipients = [r.strip() for r in settings.smtp_to.split(",") if r.strip()]
        if not recipients:
            _record(conn, "email", "", subject, body, severity, "skipped",
                    "No recipient address configured", vm_id, now)
        for recipient in recipients:
            try:
                _send_email(settings, recipient, subject, body)
                _record(conn, "email", recipient, subject, body, severity, "sent", vm_id=vm_id, now=now)
                results.append({"channel": "email", "recipient": recipient, "status": "sent"})
            except Exception as exc:
                log.warning("Email notification failed: %s", exc)
                _record(conn, "email", recipient, subject, body, severity, "failed", str(exc),
                        vm_id, now)
                results.append({"channel": "email", "recipient": recipient, "status": "failed",
                                "error": str(exc)})

    if "webhook" in channels:
        try:
            _send_webhook(settings, subject, body, severity, vm_id)
            _record(conn, "webhook", settings.webhook_url, subject, body, severity, "sent",
                    vm_id=vm_id, now=now)
            results.append({"channel": "webhook", "recipient": settings.webhook_url,
                            "status": "sent"})
        except Exception as exc:
            log.warning("Webhook notification failed: %s", exc)
            _record(conn, "webhook", settings.webhook_url, subject, body, severity, "failed",
                    str(exc), vm_id, now)
            results.append({"channel": "webhook", "recipient": settings.webhook_url,
                            "status": "failed", "error": str(exc)})
    return results


def list_notifications(conn, limit=100):
    return conn.execute(
        "SELECT n.*, v.vm_name FROM notifications n LEFT JOIN vms v ON v.vm_id = n.vm_id "
        "ORDER BY n.notification_id DESC LIMIT ?", (limit,)).fetchall()
