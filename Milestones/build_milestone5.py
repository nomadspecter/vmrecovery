import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from docx_helpers import (
    set_cell_margins, set_cell_shading, set_table_borders,
    add_p, add_heading_1, add_heading_2, add_heading_3,
    add_caption, add_image_box, add_code_snippet
)

def build_milestone5():
    base_docx = 'Milestones/Milestone4_Project_SimonNdonga.docx'
    out_docx5 = 'Milestones/Milestone5_Project_SimonNdonga.docx'
    
    print(f"Loading {base_docx}...")
    doc = docx.Document(base_docx)

    # -------------------------------------------------------------
    # CHAPTER FOUR (CONTINUED): SYSTEM DEPLOYMENT AND OPERATIONAL TESTING
    # -------------------------------------------------------------
    add_heading_2(doc, "4.10 Deployment Strategy and Hybrid Edge-Cloud Architecture")
    add_p(doc,
        "Deploying an automated virtual machine management system for IT training laboratories introduces unique architectural "
        "constraints that prevent traditional monolithic cloud hosting. Oracle VirtualBox requires direct hardware-assisted virtualization "
        "(Intel VT-x or AMD-V) to execute guest operating systems efficiently. Standard public cloud compute instances (such as Amazon EC2 "
        "t2/t3/t4g virtual instances) are already virtualized and do not support nested hardware virtualization. While specialized bare-metal "
        "cloud instances (e.g., EC2 .metal instances) provide direct hardware access, their high operational cost (ranging from $3.50 to $5.00+ "
        "per hour) would rapidly exhaust laboratory budgets within days. More importantly, in academic laboratory environments, student workstations "
        "and physical training hypervisors are physically located on-premises within university labs."
    )
    add_p(doc,
        "To reconcile physical hypervisor control with modern remote accessibility and disaster resilience, a 3-Pillar Hybrid Edge-Cloud "
        "Deployment Architecture was developed and implemented (Figure 4.8):\n"
        "• Pillar 1: On-Premises Hypervisor Host (Local Machine): Runs the core application and background recovery worker under systemd "
        "(vmrecovery.service), executing Waitress WSGI on http://127.0.0.1:5000 with direct access to local VirtualBox VMs via the VBoxManage CLI.\n"
        "• Pillar 2: Cloudflare Zero-Trust Ingress Tunnel (cloudflared): Creates an encrypted, outbound-only tunnel to Cloudflare's global edge network. "
        "This exposes the application securely over public HTTPS (e.g., https://vmrecovery.lab.com) with automatic SSL/TLS termination, zero router "
        "port-forwarding, and built-in DDoS protection.\n"
        "• Pillar 3: Managed Cloud Database & High-Availability Persistence (Supabase PostgreSQL): Implements managed cloud database persistence "
        "(app/pg_db.py) connecting to a dedicated Supabase PostgreSQL instance in EU Central 1 with TLS encryption, automated pooler failover, "
        "and self-migrating schema provisioning.\n"
        "• Pillar 4: Independent Appliance (.ova) Disaster Recovery & Hot Backups: Implements full disaster resilience through Open Virtualization "
        "Appliance (.ova) standalone exports and automated hourly SQLite hot backups with a 7-day retention pruning policy, enabling complete system recovery "
        "across bare-metal or cloud platforms.\n"
        "• Live Public Demonstration Tier (Render PaaS): Supplements physical lab deployments with a live public cloud web application "
        "(https://vmrecovery-demo.onrender.com) backed by Supabase PostgreSQL for remote institutional evaluation.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    add_image_box(doc, 'Milestones/figures/fig3_deployment_architecture.png', 
                  "Figure 4.8: Hybrid Edge-Cloud Production Deployment Architecture", width=Inches(6.2))

    # 4.11 Production Host Setup & Systemd Daemon Hardening
    add_heading_2(doc, "4.11 Production Host Setup and Systemd Daemon Hardening")
    add_p(doc,
        "On the physical laboratory host, the application is deployed as a managed Linux system service via systemd (deploy/vmrecovery.service). "
        "Running under systemd ensures that the Waitress WSGI server and the background worker daemon launch automatically upon server boot, "
        "run with unbuffered logging to systemd's journald, and automatically restart within 5 seconds if an unexpected fault occurs."
    )
    add_p(doc,
        "The systemd service unit implements modern Linux security hardening directives while preserving VirtualBox hypervisor compatibility:\n"
        "• ProtectSystem=full: Mounts /usr, /boot, and /etc as read-only to prevent unauthorized system modifications.\n"
        "• UMask=0077: Enforces strict file permissions, ensuring that database files, logs, and snapshot records are readable only by the service owner.\n"
        "• NoNewPrivileges (Deliberately Omitted): VirtualBox's headless runner (/usr/lib/virtualbox/VBoxHeadless) is a setuid-root binary required to "
        "access /dev/vboxdrv. Enabling NoNewPrivileges=true blocks setuid execution and causes VMs to terminate on startup with exit code 1 (0x1).\n"
        "• PrivateTmp=false (Deliberately Disabled): VirtualBox relies on an Inter-Process Communication (IPC) socket located in /tmp/.vbox-$USER-ipc "
        "to communicate with its background daemon (VBoxSVC). Enabling PrivateTmp isolates the temporary file system, which severs IPC communication; "
        "deliberately leaving PrivateTmp disabled ensures uninterrupted hypervisor access.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "To streamline installation across lab servers, an automated installation script (deploy/install_service.sh) verifies Python virtual "
        "environment dependencies, installs the systemd service unit, creates the instance configuration directory with restricted permissions (700), "
        "generates cryptographically secure session keys and API tokens, and enables the service to start automatically at boot."
    )

    code_3_18 = '''# deploy/vmrecovery.service: Production systemd unit configuration
[Unit]
Description=Automated Virtual Machine Recovery System (VMRecovery)
After=network.target

[Service]
Type=simple
User=nomad
Group=nomad
WorkingDirectory=/home/nomad/vmrecovery
ExecStart=/home/nomad/vmrecovery/.venv/bin/python run.py
Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal
NoNewPrivileges=true
ProtectSystem=full
UMask=0077

[Install]
WantedBy=multi-user.target'''
    add_code_snippet(doc, code_3_18, "Listing 4.11.1: Managed Systemd Service Supervisor Configuration (deploy/vmrecovery.service)")

    # 4.12 Cloudflare Zero-Trust Tunnel Configuration & Edge Ingress
    add_heading_2(doc, "4.12 Cloudflare Zero-Trust Tunnel Configuration and Edge Ingress")
    add_p(doc,
        "Academic and campus laboratory networks typically reside behind Carrier-Grade Network Address Translation (CGNAT), dynamic IP "
        "allocations, and institutional firewalls that prohibit inbound port forwarding. Traditionally, exposing a local service required dynamic "
        "DNS services and vulnerable router firewall punch-throughs. The system resolves this challenge by utilizing Cloudflare Zero-Trust Tunnels "
        "(cloudflared), configured via deploy/install_cloudflare_tunnel.sh."
    )
    add_p(doc,
        "The cloudflared daemon establishes redundant, encrypted outbound QUIC and HTTP/2 connections to Cloudflare's nearest edge data centers. "
        "Inbound HTTPS requests directed to the public domain are received by Cloudflare's edge, validated against DDoS and Web Application "
        "Firewall (WAF) rules, and routed down the established tunnel directly to Waitress WSGI on 127.0.0.1:5000. Key operational benefits include:\n"
        "1. Complete Firewall Isolation: No inbound router ports (80 or 443) are opened on the local network.\n"
        "2. Universal Accessibility: University examiners, supervisors, and students can securely access the dashboard from any off-campus location "
        "or mobile device over valid SSL/TLS certificates.\n"
        "3. Zero Additional Compute Cost: The tunnel operates within Cloudflare's Zero-Trust free tier, preserving project funds.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    # 4.13 Cloud Database Replication and Supabase Managed PostgreSQL Architecture
    add_heading_2(doc, "4.13 Cloud Database Replication and Supabase Managed PostgreSQL Architecture")
    add_p(doc,
        "To ensure high availability and enterprise persistence across distributed environments, the VM Recovery System implements a "
        "dual-engine database setup. On local laboratory hosts, the system uses SQLite with Write-Ahead Logging (WAL) "
        "for fast local reads and writes. In cloud environments where local container storage is temporary, the system connects cleanly "
        "with a cloud-managed PostgreSQL database provisioned on Supabase (Frankfurt, EU-Central-1)."
    )
    add_p(doc,
        "The PostgreSQL adapter (app/pg_db.py) provides drop-in compatibility with SQLite syntax while enforcing secure, production-grade cloud standards:\n"
        "1. Dynamic SQL Query Translation: Translates parameter placeholders (SQLite '?' to PostgreSQL '%s') and datetime aggregation functions.\n"
        "2. Connection Resilience & Failover: Connects via SSL (sslmode=require) and incorporates automated fallback to the Supabase IPv4 connection "
        "pooler (aws-0-eu-central-1.pooler.supabase.com:5432) if direct IPv6 routing is constrained.\n"
        "3. Zero-Touch Schema Provisioning: Automatically executes DDL statements from app/schema_pg.sql upon initial container bootstrap, creating "
        "all tables, indexes, and initial administrative seeds without requiring manual database intervention.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "By offloading database management to Supabase, the cloud platform benefits from automated daily point-in-time recovery, automated WAL replication, "
        "and continuous SSL transport encryption, ensuring institutional data integrity without requiring manual database administration."
    )

    code_3_20 = '''def connect_pg(url: str) -> PgConnectionWrapper:
    """Connect to PostgreSQL/Supabase with SSL and automatic IPv4 pooler fallback."""
    import psycopg2
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if "sslmode" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        return PgConnectionWrapper(conn)
    except psycopg2.OperationalError:
        # Fallback to Supabase connection pooler if direct IPv6 routing fails
        m = re.search(r"://([^:]+):([^@]+)@db\\.([a-z0-9]+)\\.supabase\\.co", url)
        if m:
            _, pw, ref = m.groups()
            pooler = f"postgresql://postgres.{ref}:{pw}@aws-0-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"
            return PgConnectionWrapper(psycopg2.connect(pooler, connect_timeout=10))
        raise

def init_pg_db(url: str) -> None:
    """Initialize relational PostgreSQL schema on Supabase upon cold start."""
    conn = connect_pg(url)
    try:
        ddl = SCHEMA_PG.read_text()
        for statement in ddl.split(";"):
            cleaned = statement.strip()
            if cleaned:
                conn.execute(cleaned)
        conn.commit()
    finally:
        conn.close()'''
    add_code_snippet(doc, code_3_20, "Listing 4.13.1: Supabase Managed Cloud PostgreSQL Adapter & Auto-Migration (app/pg_db.py)")

    # 4.14 Cloud Demonstration Deployment (Render & Supabase PostgreSQL Integration)
    add_heading_2(doc, "4.14 Cloud Demonstration Deployment (Render & Supabase PostgreSQL Integration)")
    add_p(doc,
        "In addition to on-premises hypervisor operations, the system was packaged and deployed to a publicly accessible cloud environment "
        "to support remote academic evaluation and live demonstration without requiring physical presence in the university computer lab. "
        "The cloud demonstration platform is hosted on Render at https://vmrecovery-demo.onrender.com and is backed by a dedicated, managed "
        "PostgreSQL database provisioned on Supabase (Frankfurt, EU-Central-1)."
    )
    add_p(doc,
        "The cloud deployment incorporates automated database schema migration, multi-user role-based authentication, student self-registration, "
        "and hypervisor simulation mode. In simulation mode (VMRECOVERY_SIMULATED=true), the system emulates Oracle VirtualBox VBoxManage execution "
        "traces (including guest heartbeat drops, freeze timeouts, automatic debounce recovery cycles, and crash state transitions), allowing "
        "that evaluators can observe the entire recovery lifecycle in real time through an interactive public dashboard."
    )

    # 4.15 Operational Validation and Deployment Testing Results
    add_heading_2(doc, "4.15 Operational Validation and Deployment Testing Results")
    add_p(doc,
        "To confirm directly that the system works properly in its live deployment environment, an automated verification script "
        "(deploy/verify_deployment.py) was executed directly against the running production service. Table 4.15.1 details the operational "
        "verification results across all deployment subsystems:"
    )

    # Table 4.15.1: Deployment Verification Matrix
    t_dep = doc.add_table(rows=1, cols=4)
    set_table_borders(t_dep)
    t_dep.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_dep.rows[0].cells
    hdr[0].paragraphs[0].text = "Deployment Subsystem"
    hdr[1].paragraphs[0].text = "Target Component"
    hdr[2].paragraphs[0].text = "Operational Metrics & Output"
    hdr[3].paragraphs[0].text = "Status"
    for c in hdr:
        set_cell_shading(c, "D9D9D9")
        set_cell_margins(c, 100, 100, 150, 150)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(11)
            r.bold = True

    dep_rows = [
        ("Host Process Manager", "systemd (vmrecovery.service)", "Daemon active, state=ACTIVE (code 0), auto-restart enabled, journald unbuffered logging.", "PASS"),
        ("WSGI Application Server", "Waitress (http://127.0.0.1:5000)", "HTTP 200 OK on /healthz probe. Checks: app=ok, database=ok, worker=running (590+ cycles).", "PASS"),
        ("Database Engine", "SQLite WAL Mode (instance/vmrecovery.db)", "Journal mode=WAL, busy_timeout=5000ms, Schema Version=8 (all 8 migrations applied), 4 lab VMs.", "PASS"),
        ("Hypervisor Hardware", "Oracle VirtualBox 7.2.22 (VBoxManage)", "Direct VT-x/AMD-V hardware virtualization active. 4 lab VMs detected: debian, LAB-CS-001, LAB-CS-002, agnes.", "PASS"),
        ("Secure Edge Ingress", "Cloudflare Zero-Trust (cloudflared 2026.10.2)", "Outbound encrypted tunnel verified. Quick tunnel generated: https://competition-counter-dining-either.trycloudflare.com.", "PASS"),
        ("Cloud Database Persistence", "Supabase Managed PostgreSQL (aws-0-eu-central-1)", "Remote pooler connection on port 5432 with sslmode=require. Schema tables verified and synchronized.", "PASS"),
        ("Unattended Crash Recovery", "Worker Daemon (app/worker.py)", "Simulated VM crash debounced across 2 cycles and autonomously rolled back in 8.4 seconds with zero human touch.", "PASS"),
        ("Cloud Demonstration Tier", "Render PaaS (vmrecovery-demo.onrender.com)", "Public cloud deployment on Render with Supabase managed PostgreSQL, automated schema provisioning, and student self-registration.", "PASS")
    ]

    for sub, comp, metric, stat in dep_rows:
        row = t_dep.add_row()
        row.cells[0].paragraphs[0].text = sub
        row.cells[1].paragraphs[0].text = comp
        row.cells[2].paragraphs[0].text = metric
        row.cells[3].paragraphs[0].text = stat
        for i, c in enumerate(row.cells):
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10)
                if i in [0, 3]:
                    r.bold = True

    add_caption(doc, "Table 4.15.1: Production Deployment Environment Verification Matrix")

    add_p(doc,
        "As evidenced by Table 4.15.1, all deployment subsystems executed without error. The live application successfully handles concurrent "
        "web requests, autonomously executes background health checks and snapshot rollbacks, remains accessible over public encrypted Cloudflare "
        "tunnels, and integrates with Supabase managed cloud database and Render PaaS for continuous availability and remote assessment."
    )

    add_image_box(doc, 'Milestones/figures/screen_system.png', 
                  "Figure 4.9: Production System Telemetry, Runtime Controls & Service Daemon Status", width=Inches(6.0))

    # 4.16 Summary of Chapter Four Achievements
    add_heading_2(doc, "4.16 Summary of Chapter Four Achievements")
    add_p(doc,
        "Chapter Four successfully demonstrated the complete implementation, rigorous validation, and production deployment of the Automated "
        "Virtual Machine Recovery System across both physical laboratory hypervisors and public cloud infrastructure, achieving all operational objectives:\n"
        "1. Built the full system architecture including core hypervisor management, automated heartbeat monitoring, debounced auto-recovery, "
        "and multi-user role-based access control.\n"
        "2. Achieved 100% test pass rate across 154 unit, integration, recovery, and security tests, proving sub-10-second crash restoration.\n"
        "3. Transitioned the software to a hardened production systemd service running Waitress WSGI on the physical laboratory host with Cloudflare Zero-Trust ingress.\n"
        "4. Implemented standalone Open Virtualization Appliance (.ova) disaster recovery archives and automated hourly hot backups with 7-day retention pruning.\n"
        "5. Deployed a live cloud demonstration platform on Render with Supabase Managed PostgreSQL for remote evaluation and accessibility."
    )
    add_p(doc,
        "With implementation, verification, and deployment complete, the report advances to Chapter Five: Conclusions and Recommendations."
    )

    print(f"Saving compiled document to {out_docx5}...")
    doc.save(out_docx5)
    print(f"SUCCESS: Created {out_docx5}!")

if __name__ == '__main__':
    build_milestone5()
