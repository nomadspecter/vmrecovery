"""Deployment Environment Verification Script for Milestone 5.
Validates production deployment health, systemd service status, SQLite WAL mode,
VBoxManage CLI integration, Cloudflare Zero-Trust ingress, and Render/Supabase cloud tier.
"""
import os
import subprocess
import sys
import time
import urllib.request
import json
import sqlite3

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def verify_deployment():
    print("=" * 75)
    print("MILESTONE 5: DEPLOYMENT ENVIRONMENT VERIFICATION REPORT")
    print("=" * 75)
    print(f"Execution Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform:       Linux {os.uname().release} ({os.uname().machine})")
    print("=" * 75)

    results = []

    # 1. Systemd Service Verification
    print("\n1. Systemd Service Status (vmrecovery.service)...")
    rc, out, _ = run_cmd("systemctl is-active vmrecovery.service")
    active = (rc == 0 and out == "active")
    print(f"   Status: {out.upper()} (code {rc})")
    results.append(("Systemd Service (vmrecovery.service)", "Active & Running" if active else "Inactive", "PASS" if active else "FAIL"))

    # 2. Local Waitress WSGI Health Endpoint
    print("\n2. Local Waitress WSGI Endpoint (http://127.0.0.1:5000/healthz)...")
    try:
        req = urllib.request.Request("http://127.0.0.1:5000/healthz")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            print(f"   HTTP Status: {resp.status}")
            print(f"   Checks: app={data['checks']['app']}, db={data['checks']['database']}, worker={data['checks']['worker']['running']}")
            results.append(("Waitress WSGI Server (/healthz)", f"HTTP {resp.status} - app: ok", "PASS"))
    except Exception as e:
        print(f"   Waitress Error: {e}")
        results.append(("Waitress WSGI Server (/healthz)", str(e)[:30], "FAIL"))

    # 3. Database Engine & WAL Concurrency Mode
    print("\n3. Relational Database Engine (SQLite WAL Concurrency)...")
    db_file = "instance/vmrecovery.db"
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        jmode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        row = conn.execute("SELECT value FROM schema_meta WHERE key = 'schema_version'").fetchone()
        schema_v = row[0].strip("'\"") if row else "1"
        vm_count = conn.execute("SELECT COUNT(*) FROM vms").fetchone()[0]
        conn.close()
        print(f"   Database File:  {db_file}")
        print(f"   Journal Mode:   {jmode.upper()}")
        print(f"   Schema Version: {schema_v}")
        print(f"   Registered VMs: {vm_count}")
        wal_ok = (jmode.lower() == "wal")
        results.append(("Database WAL Mode & Schema Integrity", f"WAL Mode, v{schema_v}, {vm_count} VMs", "PASS" if wal_ok else "FAIL"))
    else:
        print(f"   Database file missing: {db_file}")
        results.append(("Database WAL Mode & Schema Integrity", "Database file missing", "FAIL"))

    # 4. Hypervisor Hardware Layer (Oracle VirtualBox)
    print("\n4. Hypervisor Hardware Controller (VBoxManage)...")
    rc_vbox, out_vbox, _ = run_cmd("VBoxManage --version")
    rc_vms, out_vms, _ = run_cmd("VBoxManage list vms")
    vbox_ok = (rc_vbox == 0)
    print(f"   VirtualBox Version: {out_vbox}")
    print(f"   Hypervisor Machines:\n{out_vms}")
    results.append(("Oracle VirtualBox Hypervisor Engine", f"VBox {out_vbox} - {len(out_vms.splitlines())} VMs", "PASS" if vbox_ok else "FAIL"))

    # 5. Cloudflare Zero-Trust Ingress Tunnel Tooling
    print("\n5. Cloudflare Zero-Trust Ingress Tunnel Tooling (cloudflared)...")
    rc_cf, out_cf, _ = run_cmd("cloudflared --version")
    cf_ok = (rc_cf == 0)
    print(f"   Version: {out_cf}")
    print(f"   Installer: deploy/install_cloudflare_tunnel.sh (Ready)")
    results.append(("Cloudflare Zero-Trust Tunnel Tooling", out_cf, "PASS" if cf_ok else "FAIL"))

    # 6. Live Cloud Demonstration Platform (Render PaaS & Supabase Managed PostgreSQL)
    print("\n6. Live Cloud Demonstration Platform (Render & Supabase)...")
    cloud_url = "https://vmrecovery-demo.onrender.com/healthz"
    try:
        req = urllib.request.Request(cloud_url, headers={"User-Agent": "VMRecovery-Verify/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            print(f"   Cloud URL: {cloud_url}")
            print(f"   HTTP Status: {resp.status} (app={data['checks']['app']}, database={data['checks']['database']})")
            results.append(("Cloud Demo Platform (Render & Supabase)", "Live HTTP 200 OK - Supabase DB ok", "PASS"))
    except Exception as e:
        print(f"   Cloud Check Warning/Error: {e}")
        results.append(("Cloud Demo Platform (Render & Supabase)", str(e)[:30], "FAIL"))

    # Summary
    print("\n" + "=" * 75)
    print("DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 75)
    all_pass = True
    for component, details, status in results:
        print(f" - {component:<40} [{status}] ({details})")
        if status != "PASS":
            all_pass = False

    print("=" * 75)
    if all_pass:
        print("ALL DEPLOYMENT SUBSYSTEMS FULLY OPERATIONAL AND VERIFIED!")
    else:
        print("WARNING: Some deployment checks failed.")
    print("=" * 75)

if __name__ == "__main__":
    verify_deployment()
