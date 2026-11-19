#!/bin/bash
# ==============================================================================
# Cloudflare Zero-Trust Tunnel Installer for VMRecovery
# ==============================================================================
# Creates an outbound encrypted tunnel between the local Waitress WSGI server
# on port 5000 and Cloudflare's global edge network.
#
# No router port-forwarding or public static IP required.
# ==============================================================================
set -euo pipefail

SERVICE_DEST="/etc/systemd/system/cloudflared-vmrecovery.service"

if [ "${EUID}" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

if ! command -v cloudflared >/dev/null 2>&1; then
    echo "Error: cloudflared is not installed. Install via package manager first." >&2
    exit 1
fi

echo "========================================================================"
echo "INSTALLING CLOUDFLARE ZERO-TRUST TUNNEL SERVICE"
echo "========================================================================"

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

cat << 'EOF' > "$TMP"
[Unit]
Description=Cloudflare Zero-Trust Ingress Tunnel for VMRecovery
After=network.target vmrecovery.service
Wants=vmrecovery.service

[Service]
Type=notify
ExecStart=/usr/bin/cloudflared tunnel --no-autoupdate run
Restart=on-failure
RestartSec=5s
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

$SUDO install -m 644 "$TMP" "$SERVICE_DEST"
$SUDO systemctl daemon-reload

echo "Service unit installed to: $SERVICE_DEST"
echo "To link your Cloudflare Zero Trust tunnel:"
echo "  1. cloudflared tunnel login"
echo "  2. cloudflared tunnel create vmrecovery-lab"
echo "  3. cloudflared tunnel route dns vmrecovery-lab <your-domain.com>"
echo "  4. Point ingress to http://127.0.0.1:5000"
echo "  5. sudo systemctl enable --now cloudflared-vmrecovery"
echo
echo "For instant quick-tunnel testing without a domain:"
echo "  cloudflared tunnel --url http://127.0.0.1:5000"
echo "========================================================================"
