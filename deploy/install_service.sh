#!/bin/bash
# Install (or update) the VMRecovery systemd service for this checkout.
# Run as the lab user:   ./deploy/install_service.sh
# It will ask for sudo only when it needs to write /etc or change ownership.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_SRC="$SCRIPT_DIR/vmrecovery.service"
SERVICE_DEST="/etc/systemd/system/vmrecovery.service"
ENV_EXAMPLE="$APP_DIR/.env.example"
ENV_FILE="$APP_DIR/.env"
LOCAL_ENV_EXAMPLE="$APP_DIR/.env.local.example"
LOCAL_ENV_FILE="$APP_DIR/.env.local"
MACHINE_ENV_EXAMPLE="$APP_DIR/deploy/vmrecovery.env.example"
MACHINE_ENV_FILE="$APP_DIR/instance/vmrecovery.env"

if [ "${EUID}" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# The service must run as the user who owns the VMs and the .venv.
if [ -n "${SUDO_USER:-}" ] && [ "${SUDO_USER}" != "root" ]; then
    RUN_USER="$SUDO_USER"
else
    RUN_USER="$(stat -c '%U' "$APP_DIR")"
fi
RUN_GROUP="$(id -gn "$RUN_USER")"

if [ ! -x "$APP_DIR/.venv/bin/python" ]; then
    echo "error: $APP_DIR/.venv/bin/python not found." >&2
    echo "Create the virtual environment first:" >&2
    echo "  python -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi
if [ ! -x "$APP_DIR/.venv/bin/waitress-serve" ] && ! "$APP_DIR/.venv/bin/python" -c 'import waitress' 2>/dev/null; then
    echo "warning: waitress is not installed in .venv; the app will fall back to Flask's dev server." >&2
    echo "         Run: $APP_DIR/.venv/bin/pip install -r $APP_DIR/requirements.txt" >&2
fi
if ! command -v VBoxManage >/dev/null 2>&1; then
    echo "warning: VBoxManage is not on PATH. Set VMR_VBOXMANAGE in $ENV_FILE if it lives elsewhere." >&2
fi

# Render the unit for this user and checkout.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
escaped_app_dir="$(printf '%s' "$APP_DIR" | sed -e 's/[\\&|]/\\&/g')"
sed -e "s|/home/nomad/vmrecovery|${escaped_app_dir}|g" \
    -e "s|^User=nomad$|User=${RUN_USER}|" \
    -e "s|^Group=nomad$|Group=${RUN_GROUP}|" \
    "$SERVICE_SRC" > "$TMP"

# SupplementaryGroups=vboxusers fails to start the unit if the group is absent.
if ! getent group vboxusers >/dev/null 2>&1; then
    echo "warning: group 'vboxusers' not found; removing SupplementaryGroups from the unit." >&2
    sed -i '/^SupplementaryGroups=vboxusers$/d' "$TMP"
fi

echo "Installing VMRecovery systemd service for user ${RUN_USER} (${RUN_GROUP}) from ${APP_DIR}..."

$SUDO install -d -m 700 -o "$RUN_USER" -g "$RUN_GROUP" "$APP_DIR/instance"
if [ ! -f "$ENV_FILE" ]; then
    $SUDO install -m 600 -o "$RUN_USER" -g "$RUN_GROUP" "$ENV_EXAMPLE" "$ENV_FILE"
    echo "Created $ENV_FILE (edit it to change host/port or thresholds)."
    # Give the new installation a working session key and API token, so the
    # service is usable straight away instead of leaving both empty.
    SESSION_KEY="$("$APP_DIR/.venv/bin/python" -c 'import secrets; print(secrets.token_hex(32))')"
    API_TOKEN="$("$APP_DIR/.venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(32))')"
    $SUDO sed -i \
        -e "s|^VMR_SECRET=.*|VMR_SECRET=${SESSION_KEY}|" \
        -e "s|^VMR_API_TOKEN=.*|VMR_API_TOKEN=${API_TOKEN}|" \
        "$ENV_FILE"
    echo "Generated a session key and an API token in $ENV_FILE."
    echo "  The API token is: $API_TOKEN"
    echo "  Read it back with: grep VMR_API_TOKEN $ENV_FILE"
else
    echo "Using the existing $ENV_FILE."
fi
if [ ! -f "$MACHINE_ENV_FILE" ]; then
    $SUDO install -m 600 -o "$RUN_USER" -g "$RUN_GROUP" "$MACHINE_ENV_EXAMPLE" "$MACHINE_ENV_FILE"
    echo "Created $MACHINE_ENV_FILE for host-specific overrides."
fi

$SUDO install -m 644 "$TMP" "$SERVICE_DEST"
$SUDO systemctl daemon-reload
$SUDO systemctl enable vmrecovery.service

echo
echo "Service installed and enabled at boot."
echo "  Start now:   sudo systemctl start vmrecovery"
echo "  Status:      sudo systemctl status vmrecovery"
echo "  Logs:        sudo journalctl -u vmrecovery -f"
echo "  Health:      curl -fsS http://127.0.0.1:5000/healthz"
echo
echo "Configuration: $ENV_FILE, then $MACHINE_ENV_FILE for host-specific overrides."
echo "Runtime changes can also be made from the Settings page in the dashboard."
