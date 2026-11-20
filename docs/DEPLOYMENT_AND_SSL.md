# Production Deployment & Ingress Security Guide

This guide details the **4-Pillar Hybrid Edge-Cloud Deployment Architecture** for **VMRecovery**, integrating on-premises hypervisor operations with zero-trust edge ingress, managed cloud persistence, and disaster recovery.

---

## 1. Architectural Topology

Because VMRecovery directly interrogates and manages virtual machines via the Oracle VirtualBox `VBoxManage` CLI, physical hypervisor control resides directly on the host machine, while modern cloud tiers provide secure remote access and multi-region disaster resilience.

```
       [ Lab Workstations / Trainers / Students / Examiners ]
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
   HTTPS (Edge TLS)                                  HTTPS (Cloud Web)
         │                                                 │
         ▼                                                 ▼
┌────────────────────────────────┐               ┌────────────────────────────────┐
│ PILLAR 1: CLOUDFLARE TUNNEL   │               │ PILLAR 2: RENDER PAAS APP     │
│ (cloudflared Zero-Trust Edge)  │               │ (vmrecovery-demo.onrender.com) │
│ - Outbound-only tunnel         │               │ - Continuous GitHub CI/CD      │
│ - Zero open firewall ports     │               │ - Simulated VBox Engine        │
│ - Edge SSL/TLS Termination     │               │ - Waitress Multi-Threaded WSGI │
└──────────────┬─────────────────┘               └──────────────┬─────────────────┘
               │                                                │
               │ HTTP (127.0.0.1:5000)                          │ Encrypted SSL (5432)
               ▼                                                ▼
┌────────────────────────────────┐               ┌────────────────────────────────┐
│ ON-PREMISES HYPERVISOR HOST    │               │ PILLAR 3: SUPABASE POSTGRESQL  │
│ - Ubuntu / Linux Server        │               │ (aws-0-eu-central-1.pooler)    │
│ - systemd (vmrecovery.service) │               │ - High-Availability Managed DB │
│ - Waitress WSGI (threads=8)    │               │ - Auto-migrating schema        │
│ - app/worker.py (Auto-Healing) │               │ - Dual-database adapter        │
│ - SQLite WAL (instance/db)     │               └────────────────────────────────┘
│ - Oracle VirtualBox 7.2 Engine │
└──────────────┬─────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ PILLAR 4: INDEPENDENT APPLIANCE (.OVA) DISASTER RECOVERY & HOT BACKUPS          │
│ - Standalone Open Virtualization Appliance (.ova) exports for bare-metal restore│
│ - Hourly online SQLite hot backups (PRAGMA wal_checkpoint)                      │
│ - 7-day automatic backup retention pruning policy                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. On-Premises Host Deployment (Waitress & Systemd)

On the physical laboratory host, the application runs as a systemd-managed Linux service:

### Step 1: Install & Start Service
```bash
sudo ./deploy/install_service.sh
sudo systemctl daemon-reload
sudo systemctl enable --now vmrecovery.service
```

### Step 2: Verify Service Health
```bash
sudo systemctl status vmrecovery.service
curl -fsS http://127.0.0.1:5000/healthz | python -m json.tool
```

The systemd service unit (`deploy/vmrecovery.service`) enforces modern security hardening:
- `NoNewPrivileges=true`: Disallows privilege escalation.
- `ProtectSystem=full`: Mounts OS binaries as read-only.
- `UMask=0077`: Protects private database records and configuration files.
- `PrivateTmp=false`: Preserves IPC communication with the VirtualBox host daemon (`/tmp/.vbox-$USER-ipc`).

---

## 3. Secure Remote Access (Cloudflare Zero-Trust Ingress)

To access the hypervisor dashboard remotely without exposing public router ports or configuring fragile dynamic DNS:

```bash
# Automated installer for Cloudflare tunnel:
./deploy/install_cloudflare_tunnel.sh
```

**Security advantages:**
- **Zero Inbound Ports:** Establishes an outbound-only connection to Cloudflare's edge network.
- **Edge SSL/TLS Termination:** Automated SSL certificates managed entirely by Cloudflare.
- **WAF & DDoS Mitigation:** Blocks automated bot scrapers and DDoS traffic before reaching the lab server.

---

## 4. Public Cloud Demonstration Tier (Render & Supabase)

For remote institutional assessment and evaluation where physical hypervisor hardware is unavailable:

- **Live Public URL:** [https://vmrecovery-demo.onrender.com](https://vmrecovery-demo.onrender.com)
- **Managed Database:** Supabase PostgreSQL instance in Frankfurt (`aws-0-eu-central-1.pooler.supabase.com:5432`)
- **Simulation Engine:** `VMRECOVERY_SIMULATED=true` emulates guest heartbeats, crash states, and debounce rollbacks in real time.

---

## 5. Deployment Verification

Run the automated verification suite to validate all deployment subsystems:

```bash
.venv/bin/python deploy/verify_deployment.py
```

This validates:
1. Systemd process status (`vmrecovery.service`)
2. Waitress WSGI `/healthz` endpoint
3. SQLite database WAL mode and migration versions
4. Oracle VirtualBox hypervisor CLI and registered VMs
5. Cloudflare tunnel tooling (`cloudflared`)
6. Cloud demo platform health and Supabase database connectivity
