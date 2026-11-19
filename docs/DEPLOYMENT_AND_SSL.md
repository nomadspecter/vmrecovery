# Deployment & Reverse Proxy SSL Guide

This guide details how to deploy **VMRecovery** on the host server with an **Nginx reverse proxy** and **SSL/TLS encryption**, allowing secure access across your local lab network or remote access gateways while keeping VirtualBox hypervisor control directly on this machine.

---

## Architecture & System Topology

Because VMRecovery directly manages virtual machines via the `VBoxManage` CLI, the application and background recovery worker **must reside directly on the physical hypervisor server** that hosts the VirtualBox VMs.

```
       [ Lab Workstations / Trainers / Students ]
                           │
                           │ HTTPS (Port 443) / HTTP (Port 80)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ HYPERVISOR SERVER (specter / 192.168.100.3)                │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Nginx Reverse Proxy (Frontend)                      │   │
│   │   ├── Port 80  ──► 301 Redirect to HTTPS (Port 443) │   │
│   │   ├── Port 443 ──► SSL Termination (TLS 1.2 / 1.3)  │   │
│   │   ├── Security Headers (HSTS, nosniff, DENY frame)  │   │
│   │   └── Proxy Headers (X-Forwarded-For, X-Real-IP)    │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │                              │
│                              │ HTTP Proxy (127.0.0.1:5000)   │
│                              ▼                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ VMRecovery Waitress WSGI Application & Worker       │   │
│   │   ├── Werkzeug ProxyFix Middleware                  │   │
│   │   ├── Secure Session Cookies (VMR_COOKIE_SECURE=1)   │   │
│   │   ├── Flask Web Dashboards & JSON REST API          │   │
│   │   └── Background Worker Daemon Thread               │   │
│   └──────────────┬───────────────────────────┬──────────┘   │
│                  │                           │              │
│                  ▼                           ▼              │
│       SQLite Database (WAL)         Oracle VirtualBox Engine│
│       (instance/vmrecovery.db)      (VBoxManage CLI)        │
│                                              │              │
│                                     ┌────────┴────────┐     │
│                                     │ Virtual Machines│     │
│                                     │  - agnes        │     │
│                                     │  - debian       │     │
│                                     │  - LAB-CS-001   │     │
│                                     │  - LAB-CS-002   │     │
│                                     └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Quick Automated Deployment

Two automated scripts configure the entire stack:

### Step 1: Install & Start Systemd Service
Renders the systemd service unit, prepares virtual environments, and sets file permissions:
```bash
sudo ./deploy/install_service.sh
sudo systemctl daemon-reload
sudo systemctl reset-failed vmrecovery
sudo systemctl enable --now vmrecovery
```

Verify the backend service is listening on `127.0.0.1:5000`:
```bash
curl -fsS http://127.0.0.1:5000/healthz | python -m json.tool
```

### Step 2: Configure Nginx & SSL
Run the turnkey Nginx and SSL provisioning script:
```bash
sudo ./deploy/setup_nginx_ssl.sh
```

This script will automatically:
1. Detect host network interfaces, hostname (`specter`), and primary LAN IP (`192.168.100.3`).
2. Generate an SSL certificate with **Subject Alternative Names (SAN)** for `localhost`, `specter`, `127.0.0.1`, and your LAN IP.
3. Install [`deploy/nginx-vmrecovery.conf`](../deploy/nginx-vmrecovery.conf) into `/etc/nginx/conf.d/vmrecovery.conf`.
4. Update `/etc/nginx/nginx.conf` to include site configurations.
5. Set `VMR_COOKIE_SECURE=1` in `instance/vmrecovery.env`.
6. Test Nginx syntax and restart `nginx.service`.

---

## 2. SSL/TLS Options

### Option A: Self-Signed Certificate with SAN (Default)
Generated automatically by `deploy/setup_nginx_ssl.sh`. 

Because it includes Subject Alternative Names (SAN), modern browsers accept it for the local IP:
```bash
openssl req -x509 -nodes -days 825 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/vmrecovery.key \
    -out /etc/nginx/ssl/vmrecovery.crt \
    -subj "/CN=$(hostname)/O=VMRecovery Lab/OU=Hypervisor" \
    -addext "subjectAltName = DNS:localhost,DNS:$(hostname),IP:127.0.0.1,IP:192.168.100.3"
```

To eliminate the browser "Self-Signed Warning" on lab computers:
- **Windows:** Import `/etc/nginx/ssl/vmrecovery.crt` into `Trusted Root Certification Authorities`.
- **Linux:** Copy `vmrecovery.crt` to `/etc/pki/ca-trust/source/anchors/` (or `/usr/local/share/ca-certificates/`) and run `update-ca-trust` or `update-ca-certificates`.
- **macOS:** Open Keychain Access and add to `System -> Certificates -> Always Trust`.

### Option B: Let's Encrypt / Certbot (For Public Domains)
If your server is assigned a public domain (e.g., `vms.yourinstitution.edu`):
```bash
sudo certbot --nginx -d vms.yourinstitution.edu
```
Certbot will automatically provision and renew public CA certificates.

---

## 3. Nginx Configuration Details

The site configuration in [`deploy/nginx-vmrecovery.conf`](../deploy/nginx-vmrecovery.conf) is tuned for hypervisor control:

### HTTP to HTTPS Redirection
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}
```

### Modern TLS & HTTP/2
```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name _;

    ssl_certificate     /etc/nginx/ssl/vmrecovery.crt;
    ssl_certificate_key /etc/nginx/ssl/vmrecovery.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
...
```

### Extended Timeouts for VirtualBox
VirtualBox cloning and snapshot creation can take several minutes for large virtual disks (3–50 GB). Standard 60-second reverse proxy timeouts would cause `504 Gateway Timeout` errors in the browser. 

Nginx is configured with extended timeouts:
```nginx
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
```

### Client IP Preservation (`ProxyFix`)
The application uses Werkzeug's `ProxyFix` middleware so that rate-limiting, event auditing, and student session tracking record the actual client's IP rather than `127.0.0.1`:
```nginx
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
```

---

## 4. Application Environment Configuration

In `/home/nomad/vmrecovery/instance/vmrecovery.env` (or `.env`):

| Variable | Recommended Value | Purpose |
|---|---|---|
| `VMR_HOST` | `127.0.0.1` | Ensures Waitress only accepts traffic from local Nginx |
| `VMR_PORT` | `5000` | Backend port |
| `VMR_COOKIE_SECURE` | `1` | Enforces `Secure` flag on session cookies (transmitted only over HTTPS) |
| `VMR_VBOX_TIMEOUT` | `1800` | Maximum time allowed for hypervisor disk exports |

---

## 5. Firewall Configuration

Ensure your firewall permits incoming web traffic on ports 80 and 443:

### If using Firewalld (Default on Arch / RHEL):
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### If using UFW (Debian / Ubuntu):
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## 6. Verification & Troubleshooting

### Check Service Health
```bash
# 1. Check systemd unit status
sudo systemctl status vmrecovery

# 2. Check Nginx status
sudo systemctl status nginx

# 3. Test HTTPS endpoint locally (bypassing cert check for self-signed)
curl -kfsS https://localhost/healthz | python -m json.tool
```

### Common Issues

| Symptom | Cause | Solution |
|---|---|---|
| `502 Bad Gateway` | Waitress backend is down or not listening on `127.0.0.1:5000` | Run `sudo systemctl status vmrecovery` and inspect `journalctl -u vmrecovery -e` |
| `504 Gateway Timeout` | VM clone or snapshot took longer than proxy read timeout | Increase `proxy_read_timeout` in `/etc/nginx/conf.d/vmrecovery.conf` |
| Browser "Not Secure" warning | Using self-signed SSL certificate | Normal for self-signed certs. Import `vmrecovery.crt` to client's trusted root store or click "Proceed anyway" |
| Cookies rejected / Logout loop | `VMR_COOKIE_SECURE=1` set but accessing over plain `http://` | Always access via `https://` (port 80 redirects automatically) |
