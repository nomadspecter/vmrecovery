import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
os.makedirs('Milestones/figures', exist_ok=True)

def create_fig_deployment():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Color boxes
    b_local = dict(boxstyle="round,pad=0.6", fc="#F8F9FA", ec="#1565C0", lw=2)
    b_cf = dict(boxstyle="round,pad=0.5", fc="#FFF3E0", ec="#F57C00", lw=2)
    b_aws = dict(boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#2E7D32", lw=2)
    b_client = dict(boxstyle="round,pad=0.4", fc="#EDE7F6", ec="#512DA8", lw=1.5)

    # 1. On-Premises Local Host Boundary
    ax.add_patch(patches.Rectangle((0.5, 0.4), 6.2, 7.6, fill=True, fc="#F4F6F9", ec="#1565C0", ls="-", lw=2))
    ax.text(3.6, 7.65, "ON-PREMISES LAB HYPERVISOR (LOCAL HOST)\nSystemd Managed Daemon (vmrecovery.service)", 
            ha="center", va="center", fontsize=10.5, fontweight='bold', color="#0D47A1")

    # Inside Local Host
    ax.text(3.6, 6.3, "Waitress Multi-Threaded WSGI Server\n(Listening on http://127.0.0.1:5000)", 
            ha="center", va="center", bbox=dict(boxstyle="round4,pad=0.4", fc="#E3F2FD", ec="#1976D2", lw=1.5), fontsize=9.5, fontweight='bold')

    ax.text(2.0, 4.4, "Background Worker\n(app/worker.py)\n• 10s Monitoring Loop\n• Zero-Touch Recovery\n• Hourly DB Backup", 
            ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#FFFFFF", ec="#0288D1", lw=1.2), fontsize=8.5)

    ax.text(5.2, 4.4, "SQLite Database (WAL)\n(instance/vmrecovery.db)\n• PRAGMA journal_mode=WAL\n• 8 Numbered Migrations\n• Online Hot Backup API", 
            ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#FFFFFF", ec="#0288D1", lw=1.2), fontsize=8.5)

    ax.text(3.6, 2.2, "Oracle VirtualBox 7.2 Hypervisor (VBoxManage CLI)\n• Direct VT-x/AMD-V Hardware Virtualization\n• Guest Property Heartbeat Telemetry (/VirtualBox/.../heartbeat)\n• Fast Differencing Snapshots (<10s Rollback)\n• Standalone Appliance (.ova) Export Engine", 
            ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", fc="#ECEFF1", ec="#455A64", lw=1.5), fontsize=8.5)

    ax.text(3.6, 0.9, "Real Registered Lab VMs: debian, LAB-CS-001, LAB-CS-002, agnes", 
            ha="center", va="center", fontsize=8.5, fontstyle='italic', color="#37474F")

    # 2. Cloudflare Zero-Trust Tunnel
    ax.text(9.5, 6.3, "CLOUDFLARE ZERO-TRUST\nEDGE NETWORK (cloudflared)\n• Outbound Encrypted TLS Tunnel\n• Automatic SSL/TLS Certificate\n• Zero Router Port-Forwarding\n• Global DDoS Protection & CDN\n(e.g., https://vmrecovery.lab.com)", 
            ha="center", va="center", bbox=b_cf, fontsize=9, fontweight='bold', color="#E65100")

    # 3. AWS Cloud Storage ($100 Credits)
    ax.text(9.5, 2.6, "AMAZON WEB SERVICES (AWS CLOUD)\nOffsite Disaster Recovery & Cloud Sentry\n• AWS S3 Bucket: Offsite 3-2-1 Backups\n  - Standalone .ova Appliance Archives\n  - Hourly SQLite Online Hot Backups\n• Storage Class: STANDARD_IA / GLACIER\n• Automated Sync: deploy/sync_s3_backups.sh\n• External Cloud Health Monitor (EC2 Sentry)", 
            ha="center", va="center", bbox=b_aws, fontsize=8.5, fontweight='bold', color="#1B5E20")

    # 4. External Clients
    ax.text(9.5, 7.8, "External Clients: University Examiners, Supervisors, Trainers & Students (Mobile / Laptop)", 
            ha="center", va="center", bbox=b_client, fontsize=8.5, fontweight='bold', color="#4A148C")

    # Arrows
    arrow_blue = dict(arrowstyle="<->", lw=2.0, color="#1565C0")
    arrow_orange = dict(arrowstyle="<->", lw=2.0, color="#E65100")
    arrow_green = dict(arrowstyle="->", lw=2.0, color="#2E7D32")
    arrow_purple = dict(arrowstyle="<->", lw=1.8, color="#512DA8")

    # Inside local connections
    ax.annotate("", xy=(3.6, 5.7), xytext=(2.0, 5.1), arrowprops=arrow_blue)
    ax.annotate("", xy=(3.6, 5.7), xytext=(5.2, 5.1), arrowprops=arrow_blue)
    ax.annotate("", xy=(3.6, 3.1), xytext=(2.0, 3.7), arrowprops=arrow_blue)
    ax.annotate("", xy=(3.6, 3.1), xytext=(5.2, 3.7), arrowprops=arrow_blue)

    # Local to Cloudflare
    ax.annotate("", xy=(7.8, 6.3), xytext=(5.3, 6.3), arrowprops=arrow_orange)
    ax.text(6.5, 6.55, "Outbound TLS\nTunnel", fontsize=8, color="#E65100", ha="center")

    # Cloudflare to External Clients
    ax.annotate("", xy=(9.5, 7.2), xytext=(9.5, 7.4), arrowprops=arrow_purple)

    # Local to AWS S3
    ax.annotate("", xy=(7.8, 2.6), xytext=(6.2, 2.6), arrowprops=arrow_green)
    ax.text(7.0, 2.85, "Offsite Sync\n(aws s3 sync)", fontsize=8, color="#2E7D32", ha="center")

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig3_deployment_architecture.png', dpi=300, bbox_inches='tight')
    fig.savefig('Milestones/figures/fig3_deployment_architecture.svg', bbox_inches='tight')
    plt.close()
    print("Created Figure 3.17 (Hybrid Edge-Cloud Production Deployment Architecture)")

if __name__ == '__main__':
    create_fig_deployment()
