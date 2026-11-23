import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from docx_helpers import (
    set_cell_margins, set_cell_shading, set_table_borders,
    add_p, add_heading_1, add_heading_2, add_heading_3,
    add_caption
)

def build_milestone6():
    base_docx = 'Milestones/Milestone5_Project_SimonNdonga.docx'
    out_docx6 = 'Milestones/Milestone6_Final_Documentation_SimonNdonga.docx'
    
    print(f"Loading {base_docx}...")
    doc = docx.Document(base_docx)

    # -------------------------------------------------------------
    # 1. PRELIMINARY PAGES (Inserted before Chapter One)
    # -------------------------------------------------------------
    # Target insertion point: Paragraph 13 ("CHAPTER ONE: PROJECT PLANNING AND ANALYSIS")
    target_idx = None
    for i, p in enumerate(doc.paragraphs):
        if "CHAPTER ONE: PROJECT PLANNING AND ANALYSIS" in p.text:
            target_idx = i
            break
            
    if target_idx is None:
        raise ValueError("Could not find Chapter One anchor!")

    p_anchor = doc.paragraphs[target_idx]
    
    def ins_p(text="", bold_prefix="", is_heading=False, heading_level=1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=10, line_spacing=1.15, italic=False):
        new_p = p_anchor.insert_paragraph_before()
        new_p.alignment = align
        new_p.paragraph_format.space_before = Pt(space_before)
        new_p.paragraph_format.space_after = Pt(space_after)
        new_p.paragraph_format.line_spacing = line_spacing

        if is_heading:
            new_p.style = f'Heading {heading_level}'
            r = new_p.add_run(text)
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(16 if heading_level == 1 else 13)
            r.bold = True
            return new_p

        if bold_prefix:
            rb = new_p.add_run(bold_prefix)
            rb.font.name = 'Montserrat Medium'
            rb.font.size = Pt(12)
            rb.bold = True

        if text:
            r = new_p.add_run(text)
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(12)
            r.italic = italic
        return new_p

    def ins_page_break():
        p = p_anchor.insert_paragraph_before()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run()
        run.add_break(docx.enum.text.WD_BREAK.PAGE)

    print("Inserting Preliminary Pages before Chapter One...")

    # --- Page Break after Cover Page ---
    ins_page_break()

    # --- DECLARATION AND APPROVAL ---
    ins_p("DECLARATION AND APPROVAL", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    ins_p("Student's Declaration", bold_prefix="", is_heading=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    ins_p("I, SIMON NDONGA (Admission Number: DCS-02-0200/2025), declare that this project documentation entitled "
          "'VIRTUAL MACHINE INSTABILITY MANAGEMENT SYSTEM FOR IT TRAINING LABS' is my original work and has not been presented "
          "for the award of a diploma, degree, or any academic certification in any other college or university.")
    
    ins_p("\nSignature: ____________________________________          Date: ________________________\n"
          "SIMON NDONGA (DCS-02-0200/2025)\n", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=18)

    ins_p("Supervisor's Approval", is_heading=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    ins_p("This project documentation has been submitted for examination with my approval as the designated university supervisor.")

    ins_p("\nSignature: ____________________________________          Date: ________________________\n"
          "PROJECT SUPERVISOR\n"
          "Department of ICT and Computer Science\n"
          "Zetech University\n", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=14)

    ins_page_break()

    # --- DEDICATION ---
    ins_p("DEDICATION", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    ins_p("I dedicate this project documentation to my beloved family for their steadfast prayers, boundless encouragement, "
          "and sacrifices throughout my academic journey at Zetech University; to my lecturers and mentors who ignited my passion "
          "for systems programming and virtualization; and to all technical students who strive to master computing through hands-on "
          "laboratory practice.")

    ins_page_break()

    # --- ACKNOWLEDGEMENTS ---
    ins_p("ACKNOWLEDGEMENTS", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    ins_p("First and foremost, I offer my profound gratitude to the Almighty God for granting me health, intellect, and perseverance "
          "to successfully design, build, and document this project.")
    ins_p("I express my deepest appreciation to my project supervisor for their invaluable technical guidance, insightful critiques, "
          "and rigorous academic standards throughout each milestone of this development lifecycle. Their guidance was instrumental "
          "in refining both the system architecture and this documentation.")
    ins_p("I extend sincere thanks to the Department of ICT and Computer Science at Zetech University, the project coordinators, and the "
          "technical laboratory staff for providing an enabling environment. Lastly, I am grateful to my colleagues and peers whose feedback "
          "and shared discussions enriched this work.")

    ins_page_break()

    # --- ABSTRACT ---
    ins_p("ABSTRACT", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    ins_p("Virtual machines (VMs) form the educational backbone of modern technical training institutions, allowing learners to experiment "
          "with operating systems, networking, and security in isolated environments. However, student experimentation frequently triggers "
          "catastrophic operating system crashes, frozen kernels, and misconfigurations that disrupt instructional continuity, waste valuable lab time, "
          "and place immense operational burdens on technical staff. Traditional laboratory solutions—relying on manual hypervisor snapshots or complete "
          "operating system reinstalls—are slow, uncoordinated, and reactive.")
    ins_p("This project details the design, implementation, and deployment of the Automated Virtual Machine Instability Management System "
          "(VMRecovery) for IT training laboratories. Developed using Python 3.14, Flask, SQLite with Write-Ahead Logging (WAL) concurrency, and "
          "Oracle VirtualBox VBoxManage CLI integration, the system delivers unattended, zero-touch self-healing for lab virtual machines. The system "
          "implements scheduled snapshot automation, event-driven pre-session baselines, non-intrusive guest property heartbeat interrogation, debounced "
          "fault detection, and autonomous rollback to pristine snapshots in under 10 seconds without human intervention. Beyond core recovery, the platform "
          "provides student self-service provisioning from Golden Master templates (linked and full clones), independent .ova appliance disaster recovery, "
          "multi-channel alerting via SMTP and HMAC-SHA256 signed webhooks, and a token-authenticated RESTful API.")
    ins_p("The system was deployed and validated within a hybrid edge-cloud architecture utilizing Linux systemd service hardening on the physical lab "
          "hypervisor host, Cloudflare Zero-Trust ingress tunneling for firewall-free remote HTTPS access, an offsite 3-2-1 disaster recovery pipeline "
          "managed cloud database persistence on Supabase PostgreSQL, and a live public demonstration platform deployed on Render PaaS. Empirical validation across an automated suite of 154 test cases achieved a 100% pass rate with zero defects. The resulting system "
          "guarantees instructional continuity, protects learning progress, and automates laboratory administration.")

    ins_page_break()

    def ins_auto_field(instr: str, placeholder_text: str):
        """Insert a true Word OOXML field (TOC / List of Figures / List of Tables)
        that auto-generates with live page numbers when Update Field is clicked."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        p = p_anchor.insert_paragraph_before()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)

        r_begin = p.add_run()
        fld_begin = OxmlElement('w:fldChar')
        fld_begin.set(qn('w:fldCharType'), 'begin')
        fld_begin.set(qn('w:dirty'), 'true')
        r_begin._r.append(fld_begin)

        r_instr = p.add_run()
        instr_el = OxmlElement('w:instrText')
        instr_el.set(qn('xml:space'), 'preserve')
        instr_el.text = f' {instr} '
        r_instr._r.append(instr_el)

        r_sep = p.add_run()
        fld_sep = OxmlElement('w:fldChar')
        fld_sep.set(qn('w:fldCharType'), 'separate')
        r_sep._r.append(fld_sep)

        r_txt = p.add_run(placeholder_text)
        r_txt.font.name = 'Montserrat Medium'
        r_txt.font.size = Pt(10.5)
        r_txt.italic = True

        r_end = p.add_run()
        fld_end = OxmlElement('w:fldChar')
        fld_end.set(qn('w:fldCharType'), 'end')
        r_end._r.append(fld_end)
        return p

    # --- TABLE OF CONTENTS (Auto-Generated Word Field) ---
    ins_p("TABLE OF CONTENTS", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    ins_auto_field(
        'TOC \\o "1-3" \\h \\z \\u',
        '[Table of Contents — Right-click and select "Update Field" (or press F9 / allow automatic update on open) to populate live page numbers.]'
    )

    ins_page_break()

    # --- LIST OF FIGURES (Auto-Generated Word Field) ---
    ins_p("LIST OF FIGURES", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    ins_auto_field(
        'TOC \\h \\z \\t "FigureCaption,1"',
        '[List of Figures & Code Listings — Right-click and select "Update Field" to auto-generate all figures with live page numbers.]'
    )

    ins_page_break()

    # --- LIST OF TABLES (Auto-Generated Word Field) ---
    ins_p("LIST OF TABLES", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    ins_auto_field(
        'TOC \\h \\z \\t "TableCaption,1"',
        '[List of Tables — Right-click and select "Update Field" to auto-generate all tables with live page numbers.]'
    )

    ins_page_break()

    # --- LIST OF ABBREVIATIONS AND ACRONYMS ---
    ins_p("LIST OF ABBREVIATIONS AND ACRONYMS", is_heading=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    acronyms = [
        ("API", "Application Programming Interface"),
        ("CLI", "Command Line Interface"),
        ("CPU", "Central Processing Unit"),
        ("CSRF", "Cross-Site Request Forgery"),
        ("DFD", "Data Flow Diagram"),
        ("ERD", "Entity Relationship Diagram"),
        ("FK", "Foreign Key"),
        ("GUI", "Graphical User Interface"),
        ("HMAC", "Hash-based Message Authentication Code"),
        ("HTTP", "Hypertext Transfer Protocol"),
        ("HTTPS", "Hypertext Transfer Protocol Secure"),
        ("IPC", "Inter-Process Communication"),
        ("IT", "Information Technology"),
        ("JSON", "JavaScript Object Notation"),
        ("NAT", "Network Address Translation"),
        ("NVMe", "Non-Volatile Memory Express"),
        ("OS", "Operating System"),
        ("OVA", "Open Virtualization Appliance"),
        ("PaaS", "Platform as a Service"),
        ("PBKDF2", "Password-Based Key Derivation Function 2"),
        ("PK", "Primary Key"),
        ("RAM", "Random Access Memory"),
        ("RBAC", "Role-Based Access Control"),
        ("RDBMS", "Relational Database Management System"),
        ("REST", "Representational State Transfer"),
        ("RFC", "Request for Comments"),
        ("SHA", "Secure Hash Algorithm"),
        ("SIEM", "Security Information and Event Management"),
        ("SMTP", "Simple Mail Transfer Protocol"),
        ("SQL", "Structured Query Language"),
        ("SSL", "Secure Sockets Layer"),
        ("TLS", "Transport Layer Security"),
        ("UI", "User Interface"),
        ("UML", "Unified Modeling Language"),
        ("UUID", "Universally Unique Identifier"),
        ("VBox", "Oracle VirtualBox"),
        ("VM", "Virtual Machine"),
        ("VMM", "Virtual Machine Monitor / Hypervisor"),
        ("VT-x", "Intel Virtualization Technology"),
        ("WAL", "Write-Ahead Logging"),
        ("WSGI", "Web Server Gateway Interface")
    ]
    for acr, full in acronyms:
        ins_p(f"{acr:<8} :  {full}", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2, line_spacing=1.0)

    ins_page_break()
    print("Preliminary pages inserted successfully.")

    # -------------------------------------------------------------
    # 2. CHAPTER FIVE: CONCLUSIONS AND RECOMMENDATIONS
    # -------------------------------------------------------------
    print("Appending Chapter Five and References at document end...")
    doc.add_page_break()

    add_heading_1(doc, "CHAPTER FIVE: CONCLUSIONS AND RECOMMENDATIONS")

    add_heading_2(doc, "5.1 Summary of Project Achievements")
    add_p(doc,
        "The primary purpose of this project was to resolve the severe operational and educational disruption caused by virtual machine "
        "instabilities in IT training laboratories. By designing, developing, and deploying the Automated Virtual Machine Recovery System "
        "(VMRecovery), this research successfully achieved every general and specific objective established in Chapter One:"
    )
    add_p(doc,
        "1. Realization of the Virtual Machine Registry Module: Successfully established a centralized repository linking Oracle VirtualBox "
        "hardware UUIDs to academic class groups, custom snapshot cadences, and student ownership, verified by direct CLI hardware discovery.\n"
        "2. Implementation of Automated Snapshot Scheduling: Engineered an automated snapshot engine executing both interval-based snapshots "
        "and pre-session baseline captures, protected by automated retention pruning and disk space thresholds.\n"
        "3. Development of Autonomous Zero-Touch Recovery: Built a self-healing recovery worker that interrogates guest property heartbeats, "
        "debounces transient operating system stalls, and autonomously executes snapshot rollbacks upon confirmed crashes or kernel freezes in under "
        "10 seconds without human intervention.\n"
        "4. Deployment of an Operational Dashboard and Audit Trail: Created a centralized web dashboard providing real-time health indicators, "
        "bulk machine power controls, and an immutable audit log tracking state transitions and recovery elapsed durations.\n"
        "5. Provisioning and Disaster Recovery Architecture: Developed a self-service student VM request portal based on Golden Master "
        "templates, integrated multi-channel alerting (SMTP/Webhooks), deployed independent Open Virtualization Appliance (.ova) backups, "
        "and architected cloud database replication with Supabase Managed PostgreSQL.\n"
        "6. Public Cloud Demonstration Platform: Deployed a live cloud demonstration tier on Render with Supabase Managed PostgreSQL for "
        "remote assessment, complete with role-based authentication and hypervisor execution simulation.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    add_heading_2(doc, "5.2 Challenges Encountered and Technical Mitigations")
    add_p(doc,
        "Throughout the practical implementation and deployment of this system, several significant technical and architectural hurdles were "
        "encountered. The engineering mitigations devised during this project provide valuable insights for systems engineering:"
    )
    add_p(doc,
        "• Public Cloud Virtualization Limitations: Standard cloud container and shared virtual server environments do not permit direct bare-metal "
        "hardware virtualization (VT-x/AMD-V) access. This was mitigated by architecting a 4-Pillar Hybrid Edge-Cloud Deployment: running bare-metal "
        "hypervisor execution and sub-second rollbacks on the physical laboratory host, using Cloudflare Zero-Trust edge tunnels for secure off-campus "
        "administrative ingress, utilizing Supabase managed cloud PostgreSQL for persistent database replication, and deploying a public demonstration "
        "platform on Render with simulated hypervisor telemetry.\n"
        "• SQLite Concurrency Lock Contention: Default SQLite rollback journals locked the entire database during worker write cycles, causing "
        "concurrent web requests to throw 'database is locked' errors. This was resolved by enabling Write-Ahead Logging (WAL) mode and setting a "
        "15-second busy timeout (PRAGMA busy_timeout = 15000), allowing non-blocking concurrent reads and writes.\n"
        "• Intentional Pause Misidentification: Initial recovery routines mistook an instructor's instructional pause for an operating system freeze. "
        "This was corrected by creating database migration #7, introducing an admin_paused flag that suppresses automated rollback during deliberate pauses.\n"
        "• Hypervisor Inter-Process Communication (IPC) Socket Isolation: Systemd's default PrivateTmp security hardening severed communication "
        "with VirtualBox's background daemon (/tmp/.vbox-$USER-ipc). This was resolved by explicitly disabling PrivateTmp in the service unit.\n"
        "• Recovery Thrashing Prevention: Repeatedly rolling back an intrinsically corrupted guest operating system caused continuous recovery loops. "
        "This was resolved by implementing an anti-thrashing circuit breaker that caps automated restores at 3 attempts per hour before flagging "
        "the machine for administrative intervention.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    add_heading_2(doc, "5.3 Recommendations for Future Work")
    add_p(doc,
        "While the VMRecovery system successfully fulfills all operational requirements for single-server laboratory environments, "
        "the following architectural enhancements are recommended for future academic research and commercial expansion:"
    )
    add_p(doc,
        "1. Distributed Multi-Node Hypervisor Clustering: Extend the single-node architecture into a distributed cluster. A central management "
        "controller could coordinate lightweight worker agents installed across multiple physical laboratory servers, enabling centralized "
        "snapshot policies and cross-node live migrations.\n"
        "2. Multi-Hypervisor Abstraction Layer: Expand the hypervisor integration module (app/vbox.py) to support Type-1 bare-metal and open-source "
        "hypervisors, including Kernel-based Virtual Machine (KVM/QEMU), Proxmox VE, and VMware ESXi, using a standardized virtualization driver interface.\n"
        "3. Hardware-Level Out-of-Band Power Management: Integrate IPMI (Intelligent Platform Management Interface) and Wake-on-LAN protocols to allow "
        "the management system to autonomously power on physical host servers before scheduled morning laboratory classes and gracefully shut them down "
        "in the evening to reduce institutional power consumption.\n"
        "4. Institutional Single Sign-On (SSO) Integration: Integrate the user authentication module with campus-wide directory services such as "
        "OpenLDAP, Microsoft Active Directory, or OAuth2/SAML, allowing students and faculty to log in using their institutional credentials.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )

    add_heading_2(doc, "5.4 Concluding Remarks")
    add_p(doc,
        "The Automated Virtual Machine Recovery System establishes a resilient, scalable, and autonomous platform for managing virtualized technical "
        "training environments. By eliminating reliance on manual hypervisor interventions, the software guarantees that student technical progress "
        "is continuously protected and that laboratory classes proceed without interruption. The empirical testing and real-world deployment results "
        "validate that hybrid edge-cloud architectures combine the performance of local hardware virtualization with the resilience and accessibility "
        "of enterprise cloud computing. This system delivers a cost-effective, dependable solution for educational institutions striving to provide "
        "world-class, uninterrupted hands-on technical training."
    )

    # -------------------------------------------------------------
    # 3. REFERENCES (APA 7th Edition)
    # -------------------------------------------------------------
    doc.add_page_break()
    add_heading_1(doc, "REFERENCES")

    references = [
        "Beck, K. (2003). Test-driven development: By example. Addison-Wesley Professional.",
        "Cloudflare. (2025). Cloudflare Zero Trust: Secure access to internal resources without a VPN. Cloudflare, Inc. https://developers.cloudflare.com/cloudflare-one/",
        "Fielding, R. T. (2000). Architectural styles and the design of network-based software architectures (Doctoral dissertation, University of California, Irvine).",
        "Grinberg, M. (2018). Flask web development: Developing web applications with Python (2nd ed.). O'Reilly Media.",
        "Hipp, R. D. (2024). SQLite Write-Ahead Logging (WAL) technical specification. SQLite Consortium. https://www.sqlite.org/wal.html",
        "Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., & Schwarz, P. (1992). ARIES: A transaction recovery method supporting fine-granularity locking and partial rollbacks using write-ahead logging. ACM Transactions on Database Systems (TODS), 17(1), 94-162. https://doi.org/10.1145/128765.128770",
        "Oracle Corporation. (2024). Oracle VM VirtualBox® user manual for release 7.0 & 7.1. Oracle Corporation. https://www.virtualbox.org/manual/",
        "Owens, M., & Allen, G. (2010). The definitive guide to SQLite (2nd ed.). Apress.",
        "Popek, G. J., & Goldberg, R. P. (1974). Formal requirements for virtualizable third generation architectures. Communications of the ACM, 17(7), 412-421. https://doi.org/10.1145/361011.361073",
        "PostgreSQL Global Development Group. (2024). PostgreSQL 16.0 documentation: High availability, load balancing, and replication. PostgreSQL Global Development Group. https://www.postgresql.org/docs/16/high-availability.html",
        "Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). Zero Trust Architecture (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207",
        "Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). Operating system concepts (10th ed.). John Wiley & Sons.",
        "Smith, J. E., & Nair, R. (2005). Virtual machines: Versatile platforms for systems and processes. Elsevier / Morgan Kaufmann.",
        "Tanenbaum, A. S., & Bos, H. (2015). Modern operating systems (4th ed.). Pearson Education.",
        "van Rossum, G., & Drake, F. L. (2024). Python 3.14 reference manual. Python Software Foundation. https://docs.python.org/3.14/"
    ]

    for ref in references:
        add_p(doc, ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.15)

    # -------------------------------------------------------------
    # 4. APPENDICES
    # -------------------------------------------------------------
    doc.add_page_break()
    add_heading_1(doc, "APPENDICES")

    def add_appendix_table(headers, rows):
        tbl = doc.add_table(rows=1, cols=len(headers))
        set_table_borders(tbl)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = tbl.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].paragraphs[0].text = h
            set_cell_shading(hdr[i], "D9D9D9")
            set_cell_margins(hdr[i], 80, 80, 110, 110)
            p = hdr[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10.5)
                r.bold = True
        for row_vals in rows:
            row = tbl.add_row()
            for i, val in enumerate(row_vals):
                c = row.cells[i]
                c.paragraphs[0].text = val
                set_cell_margins(c, 65, 65, 100, 100)
                p = c.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                for r in p.runs:
                    r.font.name = 'Montserrat Medium'
                    r.font.size = Pt(9.5)
                    if i == 0:
                        r.bold = True

    # Appendix A: Project Schedule & Budget
    add_heading_2(doc, "Appendix A: Project Schedule and Budget")
    add_p(doc, "Table A.1 summarizes the phased execution timeline from proposal approval through final defense, and Table A.2 outlines the total project expenditure.")
    add_appendix_table(
        ["Phase / Milestone", "Key Deliverables", "Dates (2026)", "Status"],
        [
            ("Milestone 1: Planning & Analysis", "Problem statement, objectives, scope, Gantt schedule", "31 Aug – 11 Sep 2026", "Completed"),
            ("Milestone 2: Design & Modeling", "DFDs (Level 0 & 1), 10-table ERD, UML Use Case & Class Diagrams", "14 Sep – 2 Oct 2026", "Completed"),
            ("Milestone 3: Architecture & Core", "Flask backend, VBoxManage wrapper, SQLite WAL, worker daemon", "5 Oct – 23 Oct 2026", "Completed"),
            ("Milestone 4: Build & Testing", "Snapshots, auto-recovery, student portal, 154 automated pytest cases", "26 Oct – 6 Nov 2026", "Completed"),
            ("Milestone 5: Deployment", "Systemd service, Cloudflare Zero-Trust, Render PaaS + Supabase DB", "9 Nov – 13 Nov 2026", "Completed"),
            ("Milestone 6: Final Documentation", "Compiled documentation book, appendices & slides finalization", "16 Nov – 20 Nov 2026", "Completed"),
            ("Project Presentation & Defense", "Live demonstration & oral project defense at Zetech University", "23rd Nov 2026", "Scheduled"),
        ]
    )
    add_caption(doc, "Table A.1: Project Implementation Schedule")

    add_appendix_table(
        ["Item / Resource", "Specification / Provider", "Estimated Cost (KES)"],
        [
            ("Development & Hypervisor Workstation", "Existing Student Laptop (Linux, 16 GB RAM, Intel VT-x)", "0 (Existing)"),
            ("Software & Virtualization Stack", "Python 3.14, Flask, SQLite, Oracle VirtualBox 7.2 (Open Source)", "0"),
            ("Cloud Hosting & Managed Database", "Render PaaS Free Tier + Supabase PostgreSQL Free Tier + Cloudflare Tunnel", "0"),
            ("Internet Connectivity & Data Bundles", "Research, package installation, GitHub sync & cloud testing", "3,500"),
            ("Documentation Printing & Spiral Binding", "Final project book hardcopy submission & defense copies", "2,000"),
            ("Total Estimated Project Expenditure", "", "5,500"),
        ]
    )
    add_caption(doc, "Table A.2: Project Development Budget")

    # Appendix B: Installation & User Manual
    add_heading_2(doc, "Appendix B: Installation and Role-Based User Manual")
    add_p(doc,
        "1. On-Premises Linux Hypervisor Setup:\n"
        "• Clone the repository: git clone https://github.com/nomadspecter/vmrecovery.git && cd vmrecovery\n"
        "• Create virtual environment and install dependencies: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt\n"
        "• Initialize database and create an administrator: .venv/bin/python manage.py init-db && .venv/bin/python manage.py create-user admin admin\n"
        "• Install and start the systemd service: sudo ./deploy/install_service.sh && sudo systemctl enable --now vmrecovery.service\n"
        "• Verify service health: curl -fsS http://127.0.0.1:5000/healthz\n"
        "• Optional remote HTTPS access: ./deploy/install_cloudflare_tunnel.sh\n"
        "2. Live Cloud Evaluation Access:\n"
        "• Open https://vmrecovery-demo.onrender.com in any modern web browser (runs in Simulation Mode backed by Supabase Managed PostgreSQL).",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_appendix_table(
        ["User Role", "Primary Capabilities & Operational Workflow"],
        [
            ("Administrator", "Full system governance: register/edit/delete VMs, configure snapshot policies, mark Golden Master templates, approve/reject student VM requests, manage users, restore snapshots, export .ova backups, tune runtime settings, and inspect System Health & Audit Logs."),
            ("Trainer", "Classroom operations: start and end training sessions (triggering pre-session and post-session snapshots), monitor live classroom VM statuses, request emergency restores, and view lab reliability reports."),
            ("Student", "Self-service lab access: view personal Status Summary Cards (Assigned VMs, Running, Pending Requests, Monitoring Service), check Last Checked timestamps, request emergency snapshot restores, and submit Golden Master VM cloning requests."),
        ]
    )
    add_caption(doc, "Table B.1: Role-Based User Manual Summary")

    # Appendix C: CLI & Environment Reference
    add_heading_2(doc, "Appendix C: Administrative CLI and Configuration Reference")
    add_p(doc, "Table C.1 documents the administrative CLI commands provided by manage.py, and Table C.2 lists the primary environment variables supported by the system.")
    add_appendix_table(
        ["CLI Command", "Function / Operational Purpose"],
        [
            ("python manage.py init-db", "Initialize database tables and apply all pending schema migrations (v1–v8)."),
            ("python manage.py create-user <user> <role>", "Create a new user account with PBKDF2 password hashing (admin, trainer, or student)."),
            ("python manage.py set-role <user> <role>", "Update an existing user's RBAC role."),
            ("python manage.py check", "Execute a single monitoring, fault-detection, and snapshot cycle immediately."),
            ("python manage.py snapshot <vm>", "Take an immediate manual crash-consistent snapshot of the named VM."),
            ("python manage.py restore <vm>", "Power off and restore the named VM to its newest valid snapshot."),
            ("python manage.py start-session <group>", "Boot all VMs in a class group and capture pre-session baseline snapshots."),
            ("python manage.py end-session <group>", "Capture post-session snapshots, optionally power off VMs, and close session."),
            ("python manage.py backup-db / restore-db", "Create or restore a consistent online SQLite hot backup."),
            ("python manage.py export-events <file.csv>", "Export the immutable system audit log to CSV for institutional reporting."),
        ]
    )
    add_caption(doc, "Table C.1: Administrative CLI Reference (manage.py)")

    add_appendix_table(
        ["Environment Variable", "Default / Example", "Purpose"],
        [
            ("DATABASE_URL", "postgresql://... (Supabase)", "Enables cloud PostgreSQL mode via app/pg_db.py; falls back to SQLite if unset."),
            ("VMR_SIMULATE", "0 (1 on Render Cloud)", "Toggles SimulatedVBox engine for hardware-free testing and cloud demonstrations."),
            ("VMR_CHECK_SECONDS", "10", "Interval in seconds between background worker health polling cycles."),
            ("VMR_FAIL_THRESHOLD", "2", "Consecutive failed checks required before triggering autonomous rollback."),
            ("VMR_MAX_RESTORES_PER_HOUR", "3", "Anti-thrashing circuit breaker limit before escalating to administrator alerts."),
            ("VMR_API_TOKEN", "(32-byte hex secret)", "Bearer token securing the read-only /api/v1 JSON telemetry endpoints."),
        ]
    )
    add_caption(doc, "Table C.2: Core Runtime Environment Variables")

    # Appendix D: Laboratory User Evaluation Questionnaire
    add_heading_2(doc, "Appendix D: Laboratory User Evaluation Questionnaire")
    add_p(doc,
        "The following structured evaluation instrument was designed to gather post-deployment feedback from laboratory technicians, "
        "instructors, and Computer Science students regarding system usability, recovery responsiveness, and operational reliability "
        "(Scale: 1 = Strongly Disagree, 2 = Disagree, 3 = Neutral, 4 = Agree, 5 = Strongly Agree):"
    )
    add_appendix_table(
        ["No.", "Evaluation Statement", "Rating (1 – 5)"],
        [
            ("1", "The web dashboard clearly communicates the real-time operational status (Running, Frozen, Crashed) of laboratory virtual machines.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
            ("2", "Automated pre-session and scheduled snapshots eliminate the risk of losing clean lab baselines during practical classes.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
            ("3", "Zero-touch autonomous recovery restores crashed or frozen virtual machines significantly faster than manual VirtualBox troubleshooting.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
            ("4", "The student self-service portal makes requesting a new lab VM or emergency restore straightforward and transparent.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
            ("5", "Role-based access control (Admin, Trainer, Student) appropriately restricts sensitive hypervisor actions to authorized staff.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
            ("6", "Overall, the VMRecovery system improves practical class continuity and reduces laboratory downtime.", "[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]"),
        ]
    )
    add_caption(doc, "Table D.1: Post-Deployment Laboratory Evaluation Questionnaire")

    # -------------------------------------------------------------
    # 5. POST-PASS: AUTO-GENERATE TAGS, COMPACT MARGINS & IMAGE CAP
    # -------------------------------------------------------------
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx_helpers import _ensure_caption_style

    fig_style = _ensure_caption_style(doc, "FigureCaption")
    tbl_style = _ensure_caption_style(doc, "TableCaption")
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith(("Figure ", "Listing ")) and len(t) < 160:
            p.style = fig_style
        elif t.startswith("Table ") and len(t) < 160:
            p.style = tbl_style

    # Compact margins to reduce total page count & eliminate excessive white gaps
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.85)
        sec.right_margin = Inches(0.85)

    # Cap any tall legacy Chapter 1/2 images (> 3.25" tall) proportionally
    max_h_emu = int(Inches(3.25))
    for shape in doc.inline_shapes:
        if shape.height > max_h_emu:
            scale = max_h_emu / shape.height
            new_w = int(shape.width * scale)
            new_h = max_h_emu
            shape.width = new_w
            shape.height = new_h
            for ext in shape._inline.xpath('.//a:ext'):
                ext.set('cx', str(new_w))
                ext.set('cy', str(new_h))

    # Enable automatic field update on open in Word / LibreOffice / WPS
    settings_el = doc.settings.element
    if not settings_el.xpath('.//w:updateFields'):
        upd = OxmlElement('w:updateFields')
        upd.set(qn('w:val'), 'true')
        settings_el.append(upd)

    print(f"Saving compiled final documentation book to {out_docx6}...")
    doc.save(out_docx6)
    print(f"SUCCESS: Created {out_docx6}!")

if __name__ == '__main__':
    build_milestone6()
