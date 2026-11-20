import os
import docx
from PIL import Image
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx_helpers import set_cell_margins, set_cell_shading, set_table_borders, add_heading_3, add_caption, add_p

def update_chapter2_doc(doc_path):
    print(f"Loading {doc_path} for Chapter Two complete update...")
    doc = docx.Document(doc_path)

    # 1. Update Image Blobs AND True Aspect-Ratio Dimensions for Figures in Chapter Two
    replacements = {
        'rId11': 'Milestones/figures/screen_login.png',                # Figure 2.2.1 Login page
        'rId12': 'Milestones/figures/screen_dashboard.png',            # Figure 2.2.2 Dashboard
        'rId13': 'Milestones/figures/screen_vms.png',                  # Figure 2.2.3 VM Registry & Policy
        'rId14': 'Milestones/figures/screen_snapshots.png',            # Figure 2.2.4 Snapshots & Restore
        'rId15': 'Milestones/figures/screen_events.png',               # Figure 2.2.5 Event Log
        'rId16': 'Milestones/figures/screen_reports.png',              # Figure 2.2.6 Reports
        'rId26': 'Milestones/figures/screen_requests.png',             # Figure 2.2.7 VM Provisioning Requests
        'rId27': 'Milestones/figures/screen_system.png',               # Figure 2.2.8 System Health & Notification Audit
        'rId20': 'Milestones/figures/fig2_3_3a_dfd_level0.png',        # Figure 2.3.3a Level 0 DFD (4K SVG)
        'rId21': 'Milestones/figures/fig2_3_3b_dfd_level1.png',        # Figure 2.3.3b Level 1 DFD (4K SVG)
        'rId22': 'Milestones/figures/fig2_3_4_erd_complete.png',       # Figure 2.3.4 Complete ERD (from SVG)
        'rId23': 'Milestones/figures/fig2_3_5_use_case_complete.png',  # Figure 2.3.5 Complete Use Case (from SVG)
        'rId24': 'Milestones/figures/fig2_3_6_class_diagram_complete.png' # Figure 2.3.6 Complete Class Diagram (from SVG)
    }

    for rid, img_file in replacements.items():
        if rid in doc.part.related_parts and os.path.exists(img_file):
            with open(img_file, 'rb') as f:
                doc.part.related_parts[rid]._blob = f.read()
            print(f"  -> Replaced image for {rid} with {img_file}")
        else:
            print(f"  -> Warning: {rid} not found in doc or {img_file} missing")

    # Fix inline_shape width & height to match each replacement PNG's TRUE aspect ratio
    # (prevents Word from squishing Level 0 DFD to 6.25"x1.79" or stretching Level 1 DFD!)
    max_w_in = 5.8
    max_h_in = 4.2
    for shape in doc.inline_shapes:
        blip = shape._inline.xpath('.//a:blip/@r:embed')
        rid = blip[0] if blip else None
        if rid in replacements and os.path.exists(replacements[rid]):
            with Image.open(replacements[rid]) as im:
                iw, ih = im.size
            ratio = iw / ih
            w_in = max_w_in
            h_in = w_in / ratio
            if h_in > max_h_in:
                h_in = max_h_in
                w_in = h_in * ratio
            new_cx = int(Inches(w_in))
            new_cy = int(Inches(h_in))
            shape.width = new_cx
            shape.height = new_cy
            # Also sync inner <a:ext> inside <pic:spPr><a:xfrm> so LibreOffice & Word both respect it
            for ext in shape._inline.xpath('.//a:ext'):
                ext.set('cx', str(new_cx))
                ext.set('cy', str(new_cy))

    # Remove unnecessary mid-Chapter-2 page breaks that cause half-page blank white gaps
    for idx, p in enumerate(list(doc.paragraphs)):
        brs = p._p.xpath('.//w:br[@w:type="page"]')
        if brs and idx > 0:
            prev_txt = doc.paragraphs[idx - 1].text.strip()
            if prev_txt.startswith("The first flowchart follows") or prev_txt.startswith("The context diagram"):
                for br in brs:
                    br.getparent().remove(br)
                if not p.text.strip() and not p._p.xpath('.//w:drawing'):
                    p._element.getparent().remove(p._element)
                print(f"  -> Removed unnecessary mid-section page break after: {prev_txt[:45]!r}")

    # 2. Update Narrative Paragraphs in Chapter One and Chapter Two
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        
        # P44: Client devices clarification (Chapter One)
        if text.startswith("Client devices:"):
            p.text = ''
            r_pre = p.add_run('Client devices: ')
            r_pre.bold = True
            r_pre.font.name = 'Montserrat Medium'
            r_pre.font.size = Pt(12)
            
            r_body = p.add_run(
                'desktop computers, laptops, and smartphones. Users interact with the environment through two distinct modalities: '
                '(1) Administrative & Self-Service Management: Standard web browsers on client devices navigate to the VMRecovery web portal for real-time status monitoring, manual snapshot capture/restoration, audit inspection, and student self-service VM provisioning requests. '
                '(2) Laboratory Hands-On VM Access: Students connect directly to their allocated guest virtual machine operating systems over the local laboratory network (LAN) using Secure Shell (SSH, port 22) for Linux/CLI environments and Remote Desktop Protocol (RDP/VRDP, port 3389) for graphical desktop environments, completely decoupling dashboard administration from low-level operating system practice.'
            )
            r_body.font.name = 'Montserrat Medium'
            r_body.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(10)

        # P99: Level 0 DFD description
        elif text.startswith("The context diagram shows the system as a single process with three external entities."):
            p.text = (
                "The context diagram (Figure 2.3.3a) shows the system as a single process (0.0 VM Instability Management System) "
                "interacting with four external entities: the Lab Administrator, the Trainer, the Student, the Oracle VirtualBox Hypervisor "
                "hardware layer, and external Notification Gateways (SMTP and Webhooks). The Administrator configures lab virtual machines, "
                "defines snapshot policies, approves student provisioning requests, tunes runtime settings, and receives real-time dashboards, "
                "health metrics, and audit logs. The Trainer manages class sessions, triggers pre-session snapshot baselines, requests restores "
                "for malfunctioning machines, and receives class status confirmations. The Student submits VM provisioning requests derived "
                "from Golden Master templates, monitors personal assigned virtual machine health, and manages account credentials. Oracle "
                "VirtualBox receives hypervisor management commands via the VBoxManage CLI and returns machine execution states, guest property "
                "heartbeats, and process exit codes. Outbound incident alerts are dispatched across external SMTP email servers and signed JSON "
                "webhook gateways."
            )
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # P103: Level 1 DFD description
        elif text.startswith("The Level 1 diagram divides the system into five processes:"):
            p.text = (
                "The Level 1 diagram (Figure 2.3.3b) presents the functional decomposition of the system into eight core operational processes "
                "interacting with nine dedicated data stores:\n"
                "• Process 1.0 (User Authentication & RBAC Authorization): Authenticates Administrators, Trainers, and Students against data store D1 (Users) using salted cryptographic hashes, enforcing session boundaries and preventing brute-force intrusion.\n"
                "• Process 2.0 (VM Registry & Policy Configuration Management): Registers lab machines, allocates course groupings, and associates retention rules within data store D2 (VMs & Policies).\n"
                "• Process 3.0 (Snapshot & Class Session Lifecycle Management): Governs training sessions in D6 (Class Sessions) and creates point-in-time snapshots in D3 (Snapshots) before lab classes commence.\n"
                "• Process 4.0 (Health Monitoring & Autonomous Recovery Engine): Continuously interrogates VirtualBox machine states and guest property heartbeats, debounces transient faults, and autonomously executes snapshot rollbacks upon confirmed crashes or operating system freezes without human intervention.\n"
                "• Process 5.0 (Event Audit Logging & Statistical Reporting): Captures an immutable trail of all state transitions, power actions, and recovery durations in D4 (Event Logs), generating aggregated reliability reports.\n"
                "• Process 6.0 (Template Provisioning & Request Management): Facilitates student self-service provisioning from approved Golden Master templates, tracking requests through approval and cloning workflows within D5 (VM Requests).\n"
                "• Process 7.0 (Multi-Channel Alert & Notification Dispatching): Dispatches critical incident notifications across SMTP email and HMAC-SHA256 signed webhooks, logging delivery audit attempts in D9 (Notifications).\n"
                "• Process 8.0 (Standalone Appliance & Database Backup Engine): Generates portable .ova appliance exports in D7 (OVA Backups) and manages hot, non-blocking online database backups guided by D8 (Runtime Settings)."
            )
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # P109: Use Case Diagram description
        elif text.startswith("The use case diagram shows how the actors interact with the system."):
            p.text = (
                "The use case diagram (Figure 2.3.5) illustrates the functional interactions between the primary human actors (Lab Administrator, "
                "Trainer, Student) and the secondary system actor (Oracle VirtualBox Hypervisor):\n"
                "• Lab Administrator: Can authenticate and update account credentials, register lab virtual machines and allocate class groups, "
                "configure snapshot intervals and retention limits, execute direct and bulk VM power controls, approve or reject student template "
                "clone requests, trigger manual snapshot rollbacks, export and import independent .ova disaster recovery appliances, tune runtime "
                "timeout settings without restarting the daemon, and inspect system health and notification delivery records.\n"
                "• Trainer: Can log in, initiate and terminate class training sessions, trigger automated pre-session snapshot baselines across class "
                "groups, monitor real-time virtual machine operational status, and submit restore requests for students experiencing operating system faults.\n"
                "• Student: Can log in securely, submit self-service requests for personal training virtual machines cloned from pre-configured Golden "
                "Master templates, monitor personal assigned machine health status, and update personal account passwords.\n"
                "• Oracle VirtualBox Hypervisor: Acts as a supporting hypervisor actor that executes command-line virtualization instructions "
                "(snapshotting, state restoration, cloning, headless booting) and provides guest property heartbeat telemetry."
            )
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # P113: Class Diagram description
        elif text.startswith("The class diagram shows the main classes that will be built in Python."):
            p.text = (
                "The class diagram (Figure 2.3.6) defines the object-oriented structure of the software, encompassing both entity domain models "
                "and service controller abstractions:\n"
                "• Domain Entities: User manages account credentials and RBAC privilege checks. VirtualMachine represents registered hypervisor nodes, "
                "tracking UUIDs, class groupings, health states, heartbeat properties, template designations, and administrative pause flags. "
                "SnapshotPolicy defines automated snapshot cadences and retention limits. Snapshot tracks point-in-time differencing disks. Backup "
                "encapsulates standalone .ova appliance packages. VMRequest models student self-service provisioning workflows. ClassSession manages "
                "active training session lifecycles. EventLog provides immutable audit trailing with recovery execution timing metrics. AppSetting "
                "stores dynamic runtime configuration overrides, and Notification records multi-channel alert delivery attempts.\n"
                "• Controller & Engine Classes: VBoxController encapsulates low-level VBoxManage CLI interactions with configurable execution timeout "
                "boundaries. Worker operates as an autonomous daemon thread executing periodic monitoring cycles and hourly database maintenance. "
                "Notifier orchestrates secure alert delivery via SMTP and HMAC-SHA256 signed JSON webhooks. Settings manages the six-tier layered "
                "configuration hierarchy and runtime database overrides."
            )
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 3. Add Sections 2.2.7 and 2.2.8 (UI Models for Requests and System Health)
    # Check if 2.2.7 is already added
    all_text = " ".join([p.text for p in doc.paragraphs])
    if "2.2.7 Virtual Machine Provisioning Requests" not in all_text:
        # Find index after Figure 2.2.6 caption and description
        target_idx = None
        for i, p in enumerate(doc.paragraphs):
            if "2.3 Logic Models" in p.text:
                target_idx = i
                break
        
        if target_idx is not None:
            # We can insert paragraphs before Section 2.3
            # In docx, inserting before a paragraph:
            p_logic = doc.paragraphs[target_idx]
            
            # Helper to insert paragraph before p_logic
            def insert_p(text, bold_prefix="", is_heading=False, is_caption=False):
                new_p = p_logic.insert_paragraph_before()
                if is_heading:
                    new_p.style = 'Heading 3'
                    new_p.paragraph_format.space_before = Pt(10)
                    new_p.paragraph_format.space_after = Pt(4)
                    r = new_p.add_run(text)
                    r.font.name = 'Montserrat Medium'
                    r.font.size = Pt(12)
                    r.bold = True
                elif is_caption:
                    new_p.paragraph_format.space_before = Pt(4)
                    new_p.paragraph_format.space_after = Pt(6)
                    r = new_p.add_run(text)
                    r.font.name = 'Montserrat Medium'
                    r.font.size = Pt(11)
                    r.bold = True
                else:
                    new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    new_p.paragraph_format.space_after = Pt(10)
                    new_p.paragraph_format.line_spacing = 1.15
                    if bold_prefix:
                        rb = new_p.add_run(bold_prefix)
                        rb.font.name = 'Montserrat Medium'
                        rb.font.size = Pt(12)
                        rb.bold = True
                    r = new_p.add_run(text)
                    r.font.name = 'Montserrat Medium'
                    r.font.size = Pt(12)
                return new_p

            insert_p("2.2.7 Virtual Machine Provisioning Requests", is_heading=True)
            p_img1 = p_logic.insert_paragraph_before()
            p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img1.paragraph_format.space_before = Pt(6)
            p_img1.paragraph_format.space_after = Pt(4)
            if os.path.exists('Milestones/figures/screen_requests.png'):
                p_img1.add_run().add_picture('Milestones/figures/screen_requests.png', width=Inches(5.8))
            insert_p("Figure 2.2.7 Virtual machine provisioning requests page", is_caption=True)
            insert_p("The provisioning requests page manages student self-service requests for virtual machines derived from pre-configured Golden Master templates. Students select an approved template and specify either a lightweight linked clone or a standalone full clone. Administrators review pending requests, approve deployment into designated class groups, or reject them with documented reasons.")

            insert_p("2.2.8 System Health and Notification Audit", is_heading=True)
            p_img2 = p_logic.insert_paragraph_before()
            p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img2.paragraph_format.space_before = Pt(6)
            p_img2.paragraph_format.space_after = Pt(4)
            if os.path.exists('Milestones/figures/screen_system.png'):
                p_img2.add_run().add_picture('Milestones/figures/screen_system.png', width=Inches(5.8))
            insert_p("Figure 2.2.8 System health and notification audit page", is_caption=True)
            insert_p("The system health page provides administrators with operational visibility across all subsystems: database file size, SQLite WAL journal status, hypervisor version, background worker thread execution count, and memory state. It also maintains a delivery audit log recording every outbound alert dispatched via SMTP email or signed HTTP webhooks, including delivery status, recipient, and error details.")

    doc.save(doc_path)
    print(f"SUCCESS: Saved updated Chapter Two in {doc_path}")

if __name__ == '__main__':
    # Update Milestone 2
    update_chapter2_doc('Milestones/Milestone2_Project_SimonNdonga.docx')
    # Re-build Milestone 3 so it incorporates the updated Chapter Two and Chapter Three
    from build_milestone3 import build_milestone3
    build_milestone3()
    update_chapter2_doc('Milestones/Milestone3_Project_SimonNdonga.docx')
    print("ALL MILESTONE DOCUMENTS SYNCHRONIZED AND UPDATED!")
