import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

def create_fig3_1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Styles
    box_blue = dict(boxstyle="round,pad=0.5", fc="#EBF3FB", ec="#2B4C7E", lw=2)
    box_green = dict(boxstyle="round,pad=0.5", fc="#EAF7ED", ec="#2E7D32", lw=2)
    box_orange = dict(boxstyle="round,pad=0.5", fc="#FFF3E0", ec="#E65100", lw=2)
    box_purple = dict(boxstyle="round,pad=0.5", fc="#F3E5F5", ec="#6A1B9A", lw=2)
    box_gray = dict(boxstyle="round,pad=0.5", fc="#F5F5F5", ec="#616161", lw=2)

    # Outer Container
    ax.add_patch(patches.Rectangle((2.0, 0.4), 7.8, 6.2, fill=True, fc="#FAFAFA", ec="#BDBDBD", ls="--", lw=1.5, zorder=0))
    ax.text(2.2, 6.35, "Single Process Execution (Waitress WSGI + Worker Daemon)", fontsize=11, fontweight='bold', color="#424242")

    # Ingress
    ax.text(0.8, 5.2, "Browser / Client\n(Admin, Trainer, Student)", ha="center", va="center", bbox=box_gray, fontsize=10)
    ax.text(0.8, 2.5, "External Monitoring\n(REST API / Cloud Sentry)", ha="center", va="center", bbox=box_gray, fontsize=10)

    # Web Tier
    ax.text(4.0, 5.2, "Web Tier (Flask Blueprints)\n• app/views.py (UI Routes)\n• app/api.py (JSON API)", ha="center", va="center", bbox=box_blue, fontsize=10)
    
    # Worker Tier
    ax.text(4.0, 2.5, "Worker Daemon (app/worker.py)\n• Periodic Monitoring Loop\n• Hourly DB Backup & Prune", ha="center", va="center", bbox=box_orange, fontsize=10)

    # Core Services
    ax.text(7.2, 3.85, "Core Services (app/services.py)\n• Registry & Provisioning\n• Snapshot Policies & Pruning\n• Crash Detection & Restore\n• Class Sessions & Auditing", ha="center", va="center", bbox=box_green, fontsize=10)

    # Subsystems
    ax.text(7.2, 5.7, "Hypervisor Driver (app/vbox.py)\n• VBoxManage CLI Wrapper\n• SimulatedVBox (Testing)", ha="center", va="center", bbox=box_purple, fontsize=9.5)
    ax.text(7.2, 1.8, "Database (app/db.py)\n• SQLite in WAL Mode\n• 8 Numbered Migrations", ha="center", va="center", bbox=box_blue, fontsize=9.5)
    ax.text(7.2, 0.75, "Notifications (app/notifier.py)\n• SMTP with STARTTLS\n• HMAC Signed Webhooks", ha="center", va="center", bbox=box_orange, fontsize=9.5)

    # Arrows
    arrow = dict(arrowstyle="->", lw=1.8, color="#37474F")
    d_arrow = dict(arrowstyle="<->", lw=1.8, color="#37474F")

    ax.annotate("", xy=(2.7, 5.2), xytext=(1.8, 5.2), arrowprops=arrow)
    ax.annotate("", xy=(2.7, 2.5), xytext=(1.8, 2.5), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 4.3), xytext=(5.1, 4.9), arrowprops=d_arrow)
    ax.annotate("", xy=(5.5, 3.4), xytext=(5.1, 2.8), arrowprops=d_arrow)
    ax.annotate("", xy=(7.2, 5.1), xytext=(7.2, 4.6), arrowprops=d_arrow)
    ax.annotate("", xy=(7.2, 2.3), xytext=(7.2, 3.1), arrowprops=d_arrow)
    ax.annotate("", xy=(7.2, 1.25), xytext=(7.2, 1.35), arrowprops=arrow)

    plt.tight_layout()
    plt.savefig('Milestones/figures/fig3_1_architecture.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_1_architecture.svg', '-o', 'Milestones/figures/fig3_1_architecture.png'], check=True)
    print("Created fig3_1_architecture.png via rsvg-convert")

def create_fig3_2():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    box_blue = dict(boxstyle="round,pad=0.5", fc="#E3F2FD", ec="#1565C0", lw=2)
    box_green = dict(boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#2E7D32", lw=2)
    box_gold = dict(boxstyle="round,pad=0.5", fc="#FFF8E1", ec="#F57F17", lw=2)
    box_red = dict(boxstyle="round,pad=0.5", fc="#FFEBEE", ec="#C62828", lw=2)

    ax.text(2.2, 4.8, "Web Tier Connection\n(One connection per HTTP request)\n• Read/Write operations\n• Non-blocking via WAL", ha="center", va="center", bbox=box_blue, fontsize=9.5)
    ax.text(7.8, 4.8, "Worker Daemon Connection\n(One connection per monitoring cycle)\n• State checks, crash recovery\n• Non-blocking via WAL", ha="center", va="center", bbox=box_blue, fontsize=9.5)

    ax.text(5.0, 3.0, "SQLite Database Engine\n• PRAGMA journal_mode = WAL (Concurrent read/write)\n• PRAGMA busy_timeout = 15000 (15s lock wait)\n• PRAGMA foreign_keys = ON (Referential Integrity)", ha="center", va="center", bbox=box_gold, fontsize=10, fontweight='bold')

    ax.text(2.2, 1.0, "Schema Evolution Engine\n• schema_meta table\n• Migrations 1 to 8 (auto-upgrade)\n• Safe table reconstruction", ha="center", va="center", bbox=box_green, fontsize=9.5)
    ax.text(7.8, 1.0, "Online Backup Manager\n• sqlite3 online backup API\n• Consistent copy during live use\n• Hourly rotation of backups", ha="center", va="center", bbox=box_red, fontsize=9.5)

    arrow = dict(arrowstyle="<->", lw=1.8, color="#37474F")
    d_arrow = dict(arrowstyle="->", lw=1.8, color="#37474F")

    ax.annotate("", xy=(3.6, 3.5), xytext=(2.6, 4.1), arrowprops=arrow)
    ax.annotate("", xy=(6.4, 3.5), xytext=(7.4, 4.1), arrowprops=arrow)
    ax.annotate("", xy=(3.5, 1.6), xytext=(4.3, 2.4), arrowprops=d_arrow)
    ax.annotate("", xy=(6.5, 1.6), xytext=(5.7, 2.4), arrowprops=d_arrow)

    plt.tight_layout()
    plt.savefig('Milestones/figures/fig3_2_database_wal.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_2_database_wal.svg', '-o', 'Milestones/figures/fig3_2_database_wal.png'], check=True)
    print("Created fig3_2_database_wal.png via rsvg-convert")

def create_fig3_6():
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    b_start = dict(boxstyle="round,pad=0.5", fc="#ECEFF1", ec="#455A64", lw=2)
    b_step = dict(boxstyle="square,pad=0.5", fc="#E3F2FD", ec="#1976D2", lw=2)
    b_dec = dict(boxstyle="round4,pad=0.5", fc="#FFF9C4", ec="#FBC02D", lw=2)
    b_act = dict(boxstyle="square,pad=0.5", fc="#FFEBEE", ec="#D32F2F", lw=2)
    b_ok = dict(boxstyle="square,pad=0.5", fc="#E8F5E9", ec="#388E3C", lw=2)

    ax.text(5.0, 9.4, "Start Monitoring Cycle (every 10s)", ha="center", va="center", bbox=b_start, fontsize=10, fontweight='bold')
    ax.text(5.0, 8.2, "Query VirtualBox State\n(VBoxManage list runningvms)", ha="center", va="center", bbox=b_step, fontsize=9.5)
    ax.text(5.0, 6.7, "Is VM Registered\n& In Session?", ha="center", va="center", bbox=b_dec, fontsize=9.5)
    ax.text(1.8, 6.7, "Skip / Wait Next Cycle", ha="center", va="center", bbox=b_start, fontsize=9)
    ax.text(5.0, 5.0, "Is admin_paused\n== 1?", ha="center", va="center", bbox=b_dec, fontsize=9.5)
    ax.text(1.8, 5.0, "Maintain Paused State\n(Do not treat as fault)", ha="center", va="center", bbox=b_ok, fontsize=9)
    ax.text(5.0, 3.4, "Poll Guest Heartbeat\nProperty via VBoxManage", ha="center", va="center", bbox=b_step, fontsize=9.5)
    ax.text(5.0, 1.8, "Heartbeat Fresh\n& Running?", ha="center", va="center", bbox=b_dec, fontsize=9.5)
    ax.text(1.8, 1.8, "Reset fail_count = 0\nUpdate status = 'running'", ha="center", va="center", bbox=b_ok, fontsize=9)
    ax.text(8.2, 1.8, "Increment fail_count\nIs fail_count >= 3?", ha="center", va="center", bbox=b_dec, fontsize=9)
    ax.text(8.2, 0.4, "Trigger Auto-Recovery:\nRestore Snapshot & Restart", ha="center", va="center", bbox=b_act, fontsize=9, fontweight='bold')

    arrow = dict(arrowstyle="->", lw=1.6, color="#263238")
    ax.annotate("", xy=(5.0, 8.7), xytext=(5.0, 9.0), arrowprops=arrow)
    ax.annotate("", xy=(5.0, 7.3), xytext=(5.0, 7.7), arrowprops=arrow)
    ax.annotate("No", xy=(3.0, 6.7), xytext=(4.0, 6.7), arrowprops=arrow, ha="center", va="bottom")
    ax.annotate("Yes", xy=(5.0, 5.7), xytext=(5.0, 6.1), arrowprops=arrow, ha="right", va="center")
    ax.annotate("Yes", xy=(3.2, 5.0), xytext=(4.0, 5.0), arrowprops=arrow, ha="center", va="bottom")
    ax.annotate("No", xy=(5.0, 3.9), xytext=(5.0, 4.3), arrowprops=arrow, ha="right", va="center")
    ax.annotate("", xy=(5.0, 2.5), xytext=(5.0, 2.9), arrowprops=arrow)
    ax.annotate("Yes", xy=(3.2, 1.8), xytext=(3.9, 1.8), arrowprops=arrow, ha="center", va="bottom")
    ax.annotate("No", xy=(7.0, 1.8), xytext=(6.1, 1.8), arrowprops=arrow, ha="center", va="bottom")
    ax.annotate("Yes", xy=(8.2, 0.9), xytext=(8.2, 1.3), arrowprops=arrow, ha="right", va="center")

    plt.tight_layout()
    plt.savefig('Milestones/figures/fig3_6_worker_flowchart.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_6_worker_flowchart.svg', '-o', 'Milestones/figures/fig3_6_worker_flowchart.png'], check=True)
    print("Created fig3_6_worker_flowchart.png via rsvg-convert")

if __name__ == '__main__':
    create_fig3_1()
    create_fig3_2()
    create_fig3_6()
