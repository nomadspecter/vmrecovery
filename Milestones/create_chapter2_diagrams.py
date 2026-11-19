import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
os.makedirs('Milestones/figures', exist_ok=True)

# -------------------------------------------------------------
# 1. Figure 2.3.3a: Level 0 DFD (Context Diagram)
# -------------------------------------------------------------
def create_fig2_3_3a():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    b_entity = dict(boxstyle="square,pad=0.5", fc="#ECEFF1", ec="#37474F", lw=2)
    b_process = dict(boxstyle="round4,pad=0.8", fc="#E3F2FD", ec="#1565C0", lw=2.5)
    b_sys = dict(boxstyle="square,pad=0.5", fc="#FFF3E0", ec="#E65100", lw=2)

    # Center Process
    ax.text(5.5, 4.4, "0.0\nVM INSTABILITY\nMANAGEMENT SYSTEM", ha="center", va="center", 
            bbox=b_process, fontsize=11, fontweight='bold', color="#0D47A1")

    # External Entities
    ax.text(1.4, 7.2, "Lab Administrator", ha="center", va="center", bbox=b_entity, fontsize=10, fontweight='bold')
    ax.text(1.4, 4.4, "Trainer", ha="center", va="center", bbox=b_entity, fontsize=10, fontweight='bold')
    ax.text(1.4, 1.6, "Student", ha="center", va="center", bbox=b_entity, fontsize=10, fontweight='bold')

    ax.text(9.6, 6.0, "Oracle VirtualBox\nHypervisor\n(VBoxManage)", ha="center", va="center", bbox=b_sys, fontsize=9.5, fontweight='bold')
    ax.text(9.6, 2.8, "Notification Gateways\n(SMTP / Webhook)", ha="center", va="center", bbox=b_sys, fontsize=9.5, fontweight='bold')

    arrow = dict(arrowstyle="->", lw=1.5, color="#263238")
    
    # Administrator Flows
    ax.annotate("", xy=(4.2, 5.2), xytext=(2.6, 7.2), arrowprops=arrow)
    ax.text(3.1, 6.4, "Credentials, VM Config,\nPolicies, Settings", fontsize=7.5, color="#1A237E", rotation=-20)
    
    ax.annotate("", xy=(2.6, 6.9), xytext=(4.1, 4.9), arrowprops=arrow)
    ax.text(3.8, 5.8, "Dashboard, Logs,\nReports, Health Status", fontsize=7.5, color="#1A237E", rotation=-20)

    # Trainer Flows
    ax.annotate("", xy=(4.0, 4.6), xytext=(2.2, 4.6), arrowprops=arrow)
    ax.text(3.1, 4.75, "Session Controls,\nRestore Requests", fontsize=7.5, color="#1A237E", ha="center")
    
    ax.annotate("", xy=(2.2, 4.2), xytext=(4.0, 4.2), arrowprops=arrow)
    ax.text(3.1, 3.85, "VM Status, Alerts,\nSession Confirmations", fontsize=7.5, color="#1A237E", ha="center")

    # Student Flows
    ax.annotate("", xy=(4.2, 3.6), xytext=(2.4, 1.8), arrowprops=arrow)
    ax.text(3.1, 2.4, "VM Clone Request,\nPassword Change", fontsize=7.5, color="#1A237E", rotation=20)
    
    ax.annotate("", xy=(2.4, 1.4), xytext=(4.2, 3.2), arrowprops=arrow)
    ax.text(3.8, 2.0, "Assigned VM Status,\nRequest Approval State", fontsize=7.5, color="#1A237E", rotation=20)

    # Hypervisor Flows
    ax.annotate("", xy=(8.4, 6.2), xytext=(6.9, 5.0), arrowprops=arrow)
    ax.text(7.9, 5.75, "VBoxManage Commands\n(Snapshot, Restore, Power)", fontsize=7.5, color="#BF360C", rotation=25)

    ax.annotate("", xy=(6.9, 4.6), xytext=(8.4, 5.8), arrowprops=arrow)
    ax.text(7.6, 4.85, "Execution States,\nHeartbeats, Exit Codes", fontsize=7.5, color="#BF360C", rotation=25)

    # Notification Flows
    ax.annotate("", xy=(8.4, 3.0), xytext=(7.0, 4.0), arrowprops=arrow)
    ax.text(8.0, 3.75, "Incident Alert Body,\nSigned Webhook JSON", fontsize=7.5, color="#E65100", rotation=-25)

    ax.annotate("", xy=(7.0, 3.6), xytext=(8.4, 2.6), arrowprops=arrow)
    ax.text(7.5, 2.85, "SMTP / HTTP\nDelivery Status", fontsize=7.5, color="#E65100", rotation=-25)

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig2_3_3a_dfd_level0.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_3a_dfd_level0.svg', '-o', 'Milestones/figures/fig2_3_3a_dfd_level0.png'], check=True)
    print("Created Figure 2.3.3a (Level 0 DFD) via rsvg-convert")

# -------------------------------------------------------------
# 2. Figure 2.3.3b: Level 1 DFD
# -------------------------------------------------------------
def create_fig2_3_3b():
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis('off')

    b_proc = dict(boxstyle="round4,pad=0.5", fc="#E3F2FD", ec="#1565C0", lw=2)
    b_store = dict(boxstyle="square,pad=0.4", fc="#FFFDE7", ec="#FBC02D", lw=2)
    b_ent = dict(boxstyle="square,pad=0.4", fc="#ECEFF1", ec="#455A64", lw=2)

    # External Entities
    ax.text(1.2, 9.8, "Administrator", ha="center", va="center", bbox=b_ent, fontsize=9.5, fontweight='bold')
    ax.text(1.2, 6.0, "Trainer", ha="center", va="center", bbox=b_ent, fontsize=9.5, fontweight='bold')
    ax.text(1.2, 2.2, "Student", ha="center", va="center", bbox=b_ent, fontsize=9.5, fontweight='bold')
    ax.text(10.8, 7.5, "Oracle VirtualBox\nHypervisor", ha="center", va="center", bbox=b_ent, fontsize=9, fontweight='bold')
    ax.text(10.8, 1.8, "SMTP / Webhook\nGateways", ha="center", va="center", bbox=b_ent, fontsize=9, fontweight='bold')

    # 8 Processes
    procs = [
        (4.0, 9.8, "1.0 User Authentication\n& RBAC Authorization"),
        (4.0, 7.8, "2.0 VM Registry & Policy\nConfiguration Management"),
        (4.0, 5.8, "3.0 Snapshot & Class Session\nLifecycle Management"),
        (4.0, 3.8, "4.0 Health Monitoring &\nAutonomous Recovery"),
        (4.0, 1.8, "5.0 Event Audit Logging\n& Statistical Reports"),
        (8.0, 9.8, "6.0 Template Provisioning\n& Request Management"),
        (8.0, 5.8, "7.0 Multi-Channel Alert &\nNotification Dispatching"),
        (8.0, 1.8, "8.0 Standalone Appliance\n& Database Backup Engine")
    ]
    for x, y, name in procs:
        ax.text(x, y, name, ha="center", va="center", bbox=b_proc, fontsize=8.5, fontweight='bold', color="#0D47A1")

    # Data Stores
    stores = [
        (6.0, 10.5, "D1: Users"),
        (6.0, 8.8, "D2: VMs & Policies"),
        (6.0, 6.8, "D3: Snapshots"),
        (6.0, 4.8, "D4: Event Logs"),
        (10.0, 9.8, "D5: VM Requests"),
        (6.0, 2.8, "D6: Class Sessions"),
        (10.0, 3.5, "D7: OVA Backups"),
        (6.0, 0.8, "D8: Runtime Settings"),
        (10.0, 5.0, "D9: Notifications")
    ]
    for x, y, name in stores:
        ax.text(x, y, name, ha="center", va="center", bbox=b_store, fontsize=8, fontweight='bold', color="#5D4037")

    arrow = dict(arrowstyle="->", lw=1.2, color="#37474F")
    
    # Entity to Process links
    ax.annotate("", xy=(3.0, 9.8), xytext=(2.0, 9.8), arrowprops=arrow)
    ax.annotate("", xy=(3.0, 7.8), xytext=(2.0, 9.5), arrowprops=arrow)
    ax.annotate("", xy=(3.0, 5.8), xytext=(1.8, 6.0), arrowprops=arrow)
    ax.annotate("", xy=(3.0, 2.2), xytext=(1.8, 2.2), arrowprops=arrow)
    ax.annotate("", xy=(7.0, 9.8), xytext=(6.7, 9.8), arrowprops=arrow)
    
    # Process to Store links
    ax.annotate("", xy=(5.5, 10.3), xytext=(5.0, 9.8), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 8.5), xytext=(5.0, 7.8), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 6.5), xytext=(5.0, 5.8), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 4.5), xytext=(5.0, 3.8), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 2.5), xytext=(5.0, 2.0), arrowprops=arrow)

    # Process to Hypervisor
    ax.annotate("", xy=(9.8, 7.5), xytext=(5.1, 7.8), arrowprops=arrow)
    ax.annotate("", xy=(9.8, 7.2), xytext=(5.1, 5.8), arrowprops=arrow)
    ax.annotate("", xy=(9.8, 6.8), xytext=(5.1, 3.8), arrowprops=arrow)
    ax.annotate("", xy=(9.8, 8.0), xytext=(8.9, 9.5), arrowprops=arrow)
    
    # Process to Notification
    ax.annotate("", xy=(9.8, 2.0), xytext=(8.9, 5.5), arrowprops=arrow)

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig2_3_3b_dfd_level1.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_3b_dfd_level1.svg', '-o', 'Milestones/figures/fig2_3_3b_dfd_level1.png'], check=True)
    print("Created Figure 2.3.3b (Level 1 DFD) via rsvg-convert")

# -------------------------------------------------------------
# 3. Figure 2.3.4: Complete Entity Relationship Diagram (ERD)
# -------------------------------------------------------------
def create_fig2_3_4():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9.5)
    ax.axis('off')

    b_tbl = dict(boxstyle="square,pad=0.5", fc="#FAFAFA", ec="#1565C0", lw=2)

    def draw_table(x, y, title, pks, fks, attrs):
        content = f"  {title.upper()}  \n" + "─" * 28 + "\n"
        for p in pks:
            content += f" [PK] {p}\n"
        for f in fks:
            content += f" [FK] {f}\n"
        for a in attrs:
            content += f"      {a}\n"
        ax.text(x, y, content.strip(), ha="left", va="top", bbox=b_tbl, 
                fontsize=7.5, fontfamily="monospace", color="#212121")

    # Table nodes
    draw_table(0.5, 9.2, "users", ["user_id"], [], 
               ["username (UQ)", "password_hash", "role", "created_at", "last_login_at"])

    draw_table(0.5, 5.8, "snapshot_policies", ["policy_id"], [], 
               ["interval_minutes", "retention_count", "pre_session_snapshot"])

    draw_table(4.0, 9.2, "vms", ["vm_id"], ["policy_id", "created_by", "assigned_student_id"], 
               ["vm_name", "vbox_uuid (UQ)", "class_group", "status", "heartbeat_prop", 
                "fail_count", "is_template", "admin_paused", "status_since"])

    draw_table(8.0, 9.2, "snapshots", ["snapshot_id"], ["vm_id"], 
               ["snapshot_name", "snapshot_type", "created_at"])

    draw_table(8.0, 6.2, "backups", ["backup_id"], ["vm_id"], 
               ["backup_name", "file_path", "size_bytes", "created_at"])

    draw_table(4.0, 4.6, "vm_requests", ["request_id"], ["user_id", "created_vm_id"], 
               ["template_uuid", "template_name", "requested_name", "class_group", 
                "clone_type", "status", "rejection_reason"])

    draw_table(8.0, 3.6, "class_sessions", ["session_id"], ["started_by", "ended_by"], 
               ["class_group", "status", "started_at", "ended_at"])

    draw_table(11.2, 9.2, "events", ["event_id"], ["vm_id", "user_id"], 
               ["event_type", "details", "result", "duration_seconds", "created_at"])

    draw_table(11.2, 5.4, "notifications", ["notification_id"], ["vm_id"], 
               ["channel", "recipient", "subject", "body", "severity", "status", "sent_at"])

    draw_table(0.5, 2.6, "app_settings", ["key"], ["updated_by"], 
               ["value", "updated_at"])

    # Relationship connectors
    arrow_rel = dict(arrowstyle="->", lw=1.5, color="#D32F2F", ls="--")
    
    # users -> vms
    ax.annotate("", xy=(4.0, 8.5), xytext=(2.6, 8.5), arrowprops=arrow_rel)
    # policies -> vms
    ax.annotate("", xy=(4.0, 7.0), xytext=(2.6, 5.0), arrowprops=arrow_rel)
    # vms -> snapshots
    ax.annotate("", xy=(8.0, 8.2), xytext=(6.7, 8.2), arrowprops=arrow_rel)
    # vms -> backups
    ax.annotate("", xy=(8.0, 5.6), xytext=(6.7, 6.5), arrowprops=arrow_rel)
    # vms -> events
    ax.annotate("", xy=(11.2, 8.2), xytext=(6.7, 8.8), arrowprops=arrow_rel)
    # vms -> notifications
    ax.annotate("", xy=(11.2, 4.6), xytext=(6.7, 6.0), arrowprops=arrow_rel)
    # users -> requests
    ax.annotate("", xy=(4.0, 3.8), xytext=(2.4, 7.5), arrowprops=arrow_rel)
    # vms -> requests
    ax.annotate("", xy=(5.2, 4.7), xytext=(5.2, 5.5), arrowprops=arrow_rel)
    # users -> sessions
    ax.annotate("", xy=(8.0, 2.8), xytext=(2.6, 7.2), arrowprops=arrow_rel)

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig2_3_4_erd_complete.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_4_erd_complete.svg', '-o', 'Milestones/figures/fig2_3_4_erd_complete.png'], check=True)
    print("Created Figure 2.3.4 (Complete 10-Table ERD) via rsvg-convert")

# -------------------------------------------------------------
# 4. Figure 2.3.5: Complete UML Use Case Diagram
# -------------------------------------------------------------
def create_fig2_3_5():
    fig, ax = plt.subplots(figsize=(12, 9), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # System boundary box
    ax.add_patch(patches.Rectangle((3.2, 0.4), 6.6, 10.2, fill=True, fc="#FAFAFA", ec="#78909C", ls="--", lw=2))
    ax.text(6.5, 10.3, "VM Instability Management System", ha="center", va="center", fontsize=11, fontweight='bold', color="#37474F")

    # Actors
    b_act = dict(boxstyle="round,pad=0.4", fc="#ECEFF1", ec="#37474F", lw=2)
    ax.text(1.4, 9.0, "«actor»\nLab Administrator", ha="center", va="center", bbox=b_act, fontsize=9.5, fontweight='bold')
    ax.text(1.4, 5.5, "«actor»\nTrainer", ha="center", va="center", bbox=b_act, fontsize=9.5, fontweight='bold')
    ax.text(1.4, 2.0, "«actor»\nStudent", ha="center", va="center", bbox=b_act, fontsize=9.5, fontweight='bold')
    ax.text(10.9, 5.5, "«system actor»\nOracle VirtualBox\nHypervisor", ha="center", va="center", bbox=b_act, fontsize=9, fontweight='bold')

    # Use cases
    b_uc = dict(boxstyle="round,pad=0.4", fc="#E3F2FD", ec="#1565C0", lw=1.5)
    cases = [
        (6.5, 9.8, "Authenticate & Change Password"),
        (6.5, 9.0, "Register Lab VM & Grouping"),
        (6.5, 8.2, "Configure Snapshot Policies"),
        (6.5, 7.4, "Execute VM Power Controls"),
        (6.5, 6.6, "Start / End Class Training Session"),
        (6.5, 5.8, "Trigger Pre-Session Snapshot"),
        (6.5, 5.0, "Request VM Crash Rollback"),
        (6.5, 4.2, "Autonomous Crash / Freeze Recovery"),
        (6.5, 3.4, "Request VM from Template"),
        (6.5, 2.6, "Approve / Reject Student Request"),
        (6.5, 1.8, "Export Independent OVA Appliance"),
        (6.5, 1.0, "Tune Runtime Settings & Review Health")
    ]
    for x, y, name in cases:
        ax.text(x, y, name, ha="center", va="center", bbox=b_uc, fontsize=8.5, color="#0D47A1")

    # Lines from Actors to Use Cases
    def link(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#455A64", lw=1.3)

    # Admin connections
    for uy in [9.8, 9.0, 8.2, 7.4, 6.6, 5.8, 2.6, 1.8, 1.0]:
        link(2.3, 9.0, 4.7, uy)

    # Trainer connections
    for uy in [9.8, 6.6, 5.8, 5.0]:
        link(2.0, 5.5, 4.7, uy)

    # Student connections
    for uy in [9.8, 3.4]:
        link(2.0, 2.0, 4.7, uy)

    # Hypervisor connections
    for uy in [7.4, 5.8, 4.2, 3.4, 1.8]:
        link(10.0, 5.5, 8.3, uy)

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig2_3_5_use_case_complete.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_5_use_case_complete.svg', '-o', 'Milestones/figures/fig2_3_5_use_case_complete.png'], check=True)
    print("Created Figure 2.3.5 (Complete Use Case Diagram) via rsvg-convert")

# -------------------------------------------------------------
# 5. Figure 2.3.6: Complete UML Class Diagram
# -------------------------------------------------------------
def create_fig2_3_6():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    b_cls = dict(boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#283593", lw=2)

    def draw_class(x, y, name, attrs, methods):
        content = f"«class» {name}\n" + "─" * 30 + "\n"
        for a in attrs:
            content += f" - {a}\n"
        content += "─" * 30 + "\n"
        for m in methods:
            content += f" + {m}\n"
        ax.text(x, y, content.strip(), ha="left", va="top", bbox=b_cls, 
                fontsize=7.5, fontfamily="monospace", color="#1A237E")

    draw_class(0.5, 9.8, "User", 
               ["user_id: int", "username: str", "role: str", "last_login: datetime"],
               ["check_password(pw)", "is_admin(): bool", "is_student(): bool"])

    draw_class(4.2, 9.8, "VirtualMachine", 
               ["vm_id: int", "vm_name: str", "vbox_uuid: str", "class_group: str", "status: str", "fail_count: int", "admin_paused: bool"],
               ["is_running(): bool", "is_frozen(): bool", "mark_restoring()"])

    draw_class(8.0, 9.8, "SnapshotPolicy", 
               ["policy_id: int", "interval_mins: int", "retention_count: int", "pre_session: bool"],
               ["is_due(now): bool", "validate()"])

    draw_class(11.2, 9.8, "Snapshot", 
               ["snapshot_id: int", "vm_id: int", "name: str", "snap_type: str", "created_at: str"],
               ["delete()", "restore()"])

    draw_class(0.5, 6.2, "VMRequest", 
               ["request_id: int", "user_id: int", "template_uuid: str", "clone_type: str", "status: str"],
               ["approve(admin_id)", "reject(reason)"])

    draw_class(4.2, 6.2, "VBoxController", 
               ["vboxmanage_path: str", "timeouts: dict"],
               ["get_state(uuid)", "get_guest_property()", "take_snapshot()", "restore_snapshot()", "clone_vm()", "export_vm()"])

    draw_class(8.0, 6.2, "Worker (Daemon)", 
               ["settings: Settings", "vbox: VBoxController", "lock: Lock"],
               ["run()", "run_cycle()", "_housekeeping()", "stop()"])

    draw_class(11.2, 6.2, "Notifier", 
               ["settings: Settings", "channels: list"],
               ["send(subject, body)", "_send_email()", "_send_webhook()"])

    draw_class(0.5, 2.6, "Backup (.ova)", 
               ["backup_id: int", "vm_id: int", "file_path: str", "size_bytes: int"],
               ["restore()", "delete()"])

    draw_class(4.2, 2.6, "ClassSession", 
               ["session_id: int", "class_group: str", "status: str", "started_at: str"],
               ["start()", "end(power_off=True)"])

    draw_class(8.0, 2.6, "EventLog", 
               ["event_id: int", "vm_id: int", "event_type: str", "duration: float"],
               ["log()", "prune(retention_days)"])

    draw_class(11.2, 2.6, "Settings", 
               ["host: str", "port: int", "fail_threshold: int", "timeouts: dict"],
               ["from_env()", "apply_overrides()", "to_dict()"])

    # Inheritance & Association arrows
    arrow = dict(arrowstyle="->", lw=1.5, color="#1B5E20")
    ax.annotate("", xy=(4.2, 8.5), xytext=(2.9, 8.5), arrowprops=arrow)
    ax.annotate("", xy=(8.0, 8.5), xytext=(7.1, 8.5), arrowprops=arrow)
    ax.annotate("", xy=(11.2, 8.5), xytext=(10.3, 8.5), arrowprops=arrow)
    ax.annotate("", xy=(4.2, 4.5), xytext=(4.2, 5.0), arrowprops=arrow)
    ax.annotate("", xy=(8.0, 4.5), xytext=(8.0, 5.0), arrowprops=arrow)

    plt.tight_layout()
    fig.savefig('Milestones/figures/fig2_3_6_class_diagram_complete.svg', bbox_inches='tight')
    plt.close()
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_6_class_diagram_complete.svg', '-o', 'Milestones/figures/fig2_3_6_class_diagram_complete.png'], check=True)
    print("Created Figure 2.3.6 (Complete Class Diagram) via rsvg-convert")

if __name__ == '__main__':
    create_fig2_3_3a()
    create_fig2_3_3b()
    create_fig2_3_4()
    create_fig2_3_5()
    create_fig2_3_6()
