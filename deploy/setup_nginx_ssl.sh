#!/bin/bash
# setup_nginx_ssl.sh - Configure Nginx as a reverse proxy with SSL for VMRecovery
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
NGINX_CONF_SRC="$SCRIPT_DIR/nginx-vmrecovery.conf"
NGINX_CONF_DEST="/etc/nginx/conf.d/vmrecovery.conf"
SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/vmrecovery.crt"
KEY_FILE="$SSL_DIR/vmrecovery.key"

if [ "${EUID}" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

echo "========================================================"
echo " Setting up Nginx Reverse Proxy with SSL for VMRecovery "
echo "========================================================"

# 1. Detect Host Information
HOSTNAME="$(hostname)"
PRIMARY_IP="$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}' || echo "127.0.0.1")"
echo "Host info: Hostname=${HOSTNAME}, Primary IP=${PRIMARY_IP}"

# 2. Prepare directories
echo "Creating Nginx directories..."
$SUDO mkdir -p /etc/nginx/conf.d "$SSL_DIR"

# 3. Generate SSL Certificate with Subject Alternative Names if not exists
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed SSL certificate with SAN..."
    SAN="DNS:localhost,DNS:${HOSTNAME},IP:127.0.0.1"
    if [ -n "$PRIMARY_IP" ] && [ "$PRIMARY_IP" != "127.0.0.1" ]; then
        SAN="${SAN},IP:${PRIMARY_IP}"
    fi

    $SUDO openssl req -x509 -nodes -days 825 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/CN=${HOSTNAME}/O=VMRecovery Lab/OU=Hypervisor" \
        -addext "subjectAltName = ${SAN}"
    $SUDO chmod 600 "$KEY_FILE"
    $SUDO chmod 644 "$CERT_FILE"
    echo "Generated certificate at: $CERT_FILE"
else
    echo "SSL certificate already exists at: $CERT_FILE"
fi

# 4. Install site configuration
echo "Installing Nginx site configuration to $NGINX_CONF_DEST..."
$SUDO cp "$NGINX_CONF_SRC" "$NGINX_CONF_DEST"

# 5. Ensure nginx.conf loads /etc/nginx/conf.d/*.conf
if ! grep -q "include /etc/nginx/conf.d/\*\.conf;" /etc/nginx/nginx.conf; then
    echo "Configuring /etc/nginx/nginx.conf to include conf.d/*.conf..."
    $SUDO cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak."$(date +%s)"
    $SUDO python3 -c '
with open("/etc/nginx/nginx.conf", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
inserted = False
for i, line in enumerate(lines, 1):
    if not inserted and "server {" in line and i < 80:
        skip = True
        inserted = True
        new_lines.append("    # Default server replaced by /etc/nginx/conf.d/vmrecovery.conf\n")
        new_lines.append("    include /etc/nginx/conf.d/*.conf;\n")
        continue
    if skip:
        if line.strip() == "}":
            skip = False
        continue
    new_lines.append(line)

with open("/etc/nginx/nginx.conf", "w") as f:
    f.writelines(new_lines)
'
fi

# 6. Test Nginx configuration
echo "Testing Nginx configuration syntax..."
$SUDO nginx -t

# 7. Enable secure cookies in VMRecovery environment
if [ -f "$APP_DIR/instance/vmrecovery.env" ]; then
    if grep -q "VMR_COOKIE_SECURE=" "$APP_DIR/instance/vmrecovery.env"; then
        sed -i 's/^VMR_COOKIE_SECURE=.*/VMR_COOKIE_SECURE=1/' "$APP_DIR/instance/vmrecovery.env"
    else
        echo "VMR_COOKIE_SECURE=1" >> "$APP_DIR/instance/vmrecovery.env"
    fi
    echo "Enabled VMR_COOKIE_SECURE=1 in instance/vmrecovery.env"
elif [ -f "$APP_DIR/.env" ]; then
    if grep -q "VMR_COOKIE_SECURE=" "$APP_DIR/.env"; then
        sed -i 's/^VMR_COOKIE_SECURE=.*/VMR_COOKIE_SECURE=1/' "$APP_DIR/.env"
    else
        echo "VMR_COOKIE_SECURE=1" >> "$APP_DIR/.env"
    fi
    echo "Enabled VMR_COOKIE_SECURE=1 in .env"
fi

# 8. Start/Reload Nginx
echo "Enabling and restarting Nginx service..."
$SUDO systemctl enable nginx
$SUDO systemctl restart nginx

echo ""
echo "========================================================"
echo " Nginx Reverse Proxy with SSL is successfully setup!   "
echo "========================================================"
echo " - HTTP Access (Port 80):   Redirects automatically to HTTPS"
echo " - HTTPS Access (Port 443): https://localhost or https://${PRIMARY_IP}"
echo " - Upstream:                http://127.0.0.1:5000 (Waitress)"
echo "========================================================"
