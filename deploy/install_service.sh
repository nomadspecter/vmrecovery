#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_SRC="$SCRIPT_DIR/vmrecovery.service"
SERVICE_DEST="/etc/systemd/system/vmrecovery.service"

echo "Installing VM Recovery Systemd Service..."
if [ "$EUID" -ne 0 ]; then
    sudo cp "$SERVICE_SRC" "$SERVICE_DEST"
    sudo systemctl daemon-reload
    sudo systemctl enable vmrecovery.service
    echo "Service enabled. To start now: sudo systemctl start vmrecovery"
    echo "To view status: sudo systemctl status vmrecovery"
else
    cp "$SERVICE_SRC" "$SERVICE_DEST"
    systemctl daemon-reload
    systemctl enable vmrecovery.service
    echo "Service enabled. To start now: systemctl start vmrecovery"
    echo "To view status: systemctl status vmrecovery"
fi
