"""Build a clean, concise 6-slide Zetech University Project Defense Presentation (.pptx)
matching the exact 6-slide structure of the official school template:
  /home/nomad/Downloads/4. Project presentation Template.pptx

Outputs:
  Milestones/Project_Presentation_SimonNdonga.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = "/home/nomad/Downloads/4. Project presentation Template.pptx"
OUTPUT_PATH = "Milestones/Project_Presentation_SimonNdonga.pptx"

# Zetech University Brand Palette (from the official template)
NAVY = RGBColor(0x00, 0x1C, 0x54)
MAROON = RGBColor(0x98, 0x00, 0x00)
DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
MUTED_TEXT = RGBColor(0x47, 0x55, 0x69)
CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)
CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
SOFT_NAVY_BG = RGBColor(0xEF, 0xF6, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT_HEADING = "Montserrat"
FONT_BODY = "Montserrat Medium"


def set_notes(slide, text: str):
    tf = slide.notes_slide.notes_text_frame
    tf.clear()
    tf.text = text


def style_slide_title(slide, title_text: str):
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == 0:
            shape.left = Inches(0.75)
            shape.top = Inches(0.42)
            shape.width = Inches(11.83)
            shape.height = Inches(0.80)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = title_text
            r.font.name = FONT_HEADING
            r.font.size = Pt(28)
            r.font.bold = True
            r.font.color.rgb = NAVY
            break


def clear_body_placeholder(slide):
    for shape in list(slide.placeholders):
        if shape.placeholder_format.idx == 1:
            sp = shape._element
            sp.getparent().remove(sp)


def add_footer(slide, page_num: int, total_pages: int = 6):
    tb = slide.shapes.add_textbox(Inches(0.75), Inches(7.05), Inches(9.8), Inches(0.30))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Zetech University  |  Simon Ndonga (DCS-02-0200/2025)  |  VM Instability Management System"
    r.font.name = FONT_BODY
    r.font.size = Pt(9.5)
    r.font.color.rgb = MUTED_TEXT

    nb = slide.shapes.add_textbox(Inches(11.4), Inches(7.05), Inches(1.18), Inches(0.30))
    ntf = nb.text_frame
    ntf.margin_left = ntf.margin_right = ntf.margin_top = ntf.margin_bottom = 0
    np = ntf.paragraphs[0]
    np.alignment = PP_ALIGN.RIGHT
    nr = np.add_run()
    nr.text = f"{page_num} / {total_pages}"
    nr.font.name = FONT_HEADING
    nr.font.size = Pt(9.5)
    nr.font.bold = True
    nr.font.color.rgb = NAVY


def add_bullet_list(slide, left, top, width, height, items, font_size=14.5, space_after=12):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.22
        lead, body = item
        r_dot = p.add_run()
        r_dot.text = "▪  "
        r_dot.font.name = FONT_HEADING
        r_dot.font.size = Pt(font_size)
        r_dot.font.bold = True
        r_dot.font.color.rgb = MAROON

        r_lead = p.add_run()
        r_lead.text = f"{lead} – "
        r_lead.font.name = FONT_HEADING
        r_lead.font.size = Pt(font_size)
        r_lead.font.bold = True
        r_lead.font.color.rgb = NAVY

        r_body = p.add_run()
        r_body.text = body
        r_body.font.name = FONT_BODY
        r_body.font.size = Pt(font_size)
        r_body.font.color.rgb = DARK_TEXT


def add_banner(slide, left, top, width, height, label, text, bg_color=NAVY):
    rect = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    rect.adjustments[0] = 0.12
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg_color
    rect.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.24), Inches(top + 0.14), Inches(width - 0.48), Inches(height - 0.24)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.line_spacing = 1.2
    if label:
        r1 = p.add_run()
        r1.text = f"{label}: "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = WHITE
    r2 = p.add_run()
    r2.text = text
    r2.font.name = FONT_BODY
    r2.font.size = Pt(13.5)
    r2.font.color.rgb = WHITE


def add_card(slide, left, top, width, height, title, items, accent_color=NAVY, bg_color=CARD_BG):
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.adjustments[0] = 0.04
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = CARD_BORDER
    box.line.width = Pt(1.0)

    strip = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left + 0.08), Inches(top), Inches(width - 0.16), Inches(0.06)
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.18), Inches(top + 0.16), Inches(width - 0.36), Inches(height - 0.24)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    p0.space_after = Pt(8)
    r0 = p0.add_run()
    r0.text = title
    r0.font.name = FONT_HEADING
    r0.font.size = Pt(14)
    r0.font.bold = True
    r0.font.color.rgb = accent_color

    for item in items:
        p = tf.add_paragraph()
        p.space_after = Pt(6)
        p.line_spacing = 1.18
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run()
            r1.text = f"• {lead}: "
            r1.font.name = FONT_HEADING
            r1.font.size = Pt(11.5)
            r1.font.bold = True
            r1.font.color.rgb = DARK_TEXT
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_BODY
            r2.font.size = Pt(11.5)
            r2.font.color.rgb = MUTED_TEXT
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.name = FONT_BODY
            r.font.size = Pt(11.5)
            r.font.color.rgb = DARK_TEXT


def build_presentation():
    print(f"Loading Zetech University 6-slide template: {TEMPLATE_PATH}")
    prs = Presentation(TEMPLATE_PATH)

    # Exact 6 slides from the official template:
    # 0 = Title, 1 = Problem Statement, 2 = Justification, 3 = Objectives,
    # 4 = Features/Project Details/Project Execution Steps, 5 = THANK YOU
    s_title, s_problem, s_justif, s_obj, s_features, _s_thanks = list(prs.slides)
    total = len(prs.slides)  # 6 slides

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    for shape in s_title.shapes:
        if shape.shape_id == 45:
            shape.text_frame.clear()  # clear template typo 'v'
        elif shape.shape_id == 46:
            shape.top = Inches(3.32)
            shape.height = Inches(1.08)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.line_spacing = 1.12
            r = p.add_run()
            r.text = "VIRTUAL MACHINE INSTABILITY MANAGEMENT SYSTEM FOR IT TRAINING LABS"
            r.font.name = FONT_HEADING
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = WHITE
        elif shape.shape_id == 47:
            shape.top = Inches(4.44)
            shape.height = Inches(0.42)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "Automated Crash Recovery, Snapshot Scheduling & Lab Management (VMRecovery)"
            r.font.name = FONT_BODY
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        elif shape.shape_id == 48:
            shape.top = Inches(4.92)
            shape.height = Inches(0.36)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "23/11/2026"
            r.font.name = FONT_BODY
            r.font.size = Pt(12.5)
            r.font.color.rgb = WHITE
        elif shape.shape_id == 49:
            shape.top = Inches(5.30)
            shape.height = Inches(0.55)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "SIMON NDONGA  |  DCS-02-0200/2025  |  Diploma in Computer Science"
            r.font.name = FONT_HEADING
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = WHITE

    set_notes(
        s_title,
        "Good morning/afternoon panel. My name is Simon Ndonga, DCS-02-0200/2025, Diploma in Computer Science. "
        "My project is VMRecovery — a Virtual Machine Instability Management System built to automatically monitor, "
        "snapshot, and recover VirtualBox machines in IT training labs."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    style_slide_title(s_problem, "Problem Statement")
    clear_body_placeholder(s_problem)
    add_footer(s_problem, 2, total)

    add_bullet_list(
        s_problem, 0.85, 1.50, 11.65, 4.30,
        [
            ("Frequent VM Crashes & Freezes", "Student misconfigurations, experimental commands, and memory exhaustion frequently crash or hang VirtualBox VMs during practicals."),
            ("Slow Manual Recovery", "Lab technicians manually inspect and rebuild broken VMs, wasting 20–45 minutes of instructional time per class."),
            ("Inconsistent Snapshots", "Manual pre-session snapshots are easily forgotten, leaving no clean rollback point when a guest OS breaks."),
            ("No Centralized Visibility", "Trainers lack a single dashboard to monitor classroom VM health, manage sessions, or handle student VM requests."),
            ("Poor Audit Accountability", "Manual VirtualBox GUI fixes leave no structured logs of crash frequency, recovery speed, or user actions."),
        ],
        font_size=14.5, space_after=13
    )

    add_banner(
        s_problem, 0.85, 5.95, 11.65, 0.82,
        "CORE PROBLEM",
        "IT training labs lack automated crash detection, scheduled snapshot protection, and fast self-healing for VirtualBox VMs.",
        bg_color=MAROON
    )

    set_notes(
        s_problem,
        "In IT training labs, students regularly break VirtualBox VMs while practicing Linux, networking, or security commands. "
        "Because recovery is manual, classes stall for 20 to 45 minutes while technicians reset machines. There is no automated "
        "monitoring, no scheduled snapshots, and no audit trail."
    )

    # =========================================================================
    # SLIDE 3: JUSTIFICATION
    # =========================================================================
    style_slide_title(s_justif, "Justification")
    clear_body_placeholder(s_justif)
    add_footer(s_justif, 3, total)

    add_bullet_list(
        s_justif, 0.85, 1.55, 11.65, 4.40,
        [
            ("Zero-Touch Sub-10s Recovery", "Detects crashed or frozen VMs automatically and rolls back to the latest clean snapshot in under 10 seconds."),
            ("Uninterrupted Practical Learning", "Keeps lab sessions running smoothly and lets students experiment safely with pre-session snapshot baselines."),
            ("Reduced Technician Workload", "Automates health polling, snapshot retention pruning, class session startups, and Golden Master VM cloning."),
            ("Full Accountability & Reporting", "Records every crash, restore, and action in an immutable audit log with MTTR reports and email/webhook alerts."),
            ("Cost-Effective & Secure", "Built on an open-source stack for existing lab hosts with RBAC (Admin/Trainer/Student), CSRF protection, and Cloudflare Zero-Trust HTTPS."),
        ],
        font_size=14.5, space_after=14
    )

    add_banner(
        s_justif, 0.85, 5.98, 11.65, 0.78,
        "IMPACT",
        "Verified with 154/154 passing automated tests (100% pass rate) and measured 8.4s crash-to-boot recovery.",
        bg_color=NAVY
    )

    set_notes(
        s_justif,
        "VMRecovery solves this by recovering crashed or frozen VMs automatically in under 10 seconds, keeping classes on schedule, "
        "reducing technician workload, providing full audit logs, and running on existing lab hardware with zero licensing costs."
    )

    # =========================================================================
    # SLIDE 4: OBJECTIVES
    # =========================================================================
    style_slide_title(s_obj, "Objectives")
    clear_body_placeholder(s_obj)
    add_footer(s_obj, 4, total)

    add_banner(
        s_obj, 0.85, 1.42, 11.65, 0.92,
        "GENERAL OBJECTIVE",
        "To design, develop, test, and deploy an automated Virtual Machine Instability Management System that monitors lab VMs, enforces snapshot schedules, and autonomously restores failed machines.",
        bg_color=NAVY
    )

    # Section label
    lbl = s_obj.shapes.add_textbox(Inches(0.85), Inches(2.52), Inches(6.0), Inches(0.38))
    p = lbl.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Specific Objectives"
    r.font.name = FONT_HEADING
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = MAROON

    add_bullet_list(
        s_obj, 0.85, 3.00, 11.65, 3.85,
        [
            ("Centralized VM Registry & Class Sessions", "Map VirtualBox VMs to class groups, snapshot policies, and student accounts with bulk session controls."),
            ("Automated Snapshot & Backup Engine", "Take scheduled, pre-session, and post-session snapshots with retention pruning and portable .ova disaster backups."),
            ("Autonomous Zero-Touch Recovery", "Monitor VM states and guest heartbeats every 10s with 2-cycle debouncing and anti-thrashing protection."),
            ("Student Provisioning & Role-Based Security", "Provide Golden Master VM cloning requests, Admin/Trainer/Student RBAC, alerting, and a live cloud demo."),
        ],
        font_size=14, space_after=14
    )

    set_notes(
        s_obj,
        "Our general objective was to build an automated VM recovery and lab management platform. "
        "We achieved this through four specific objectives: centralized VM registry, automated snapshotting and OVA backups, "
        "10-second autonomous crash/freeze recovery, and a role-based student provisioning portal."
    )

    # =========================================================================
    # SLIDE 5: FEATURES / PROJECT DETAILS / PROJECT EXECUTION STEPS
    # =========================================================================
    style_slide_title(s_features, "Features, Project Details & Execution Steps")
    clear_body_placeholder(s_features)
    add_footer(s_features, 5, total)

    add_card(
        s_features, 0.75, 1.42, 3.80, 5.40,
        "Core System Features",
        [
            ("Admin & Trainer Portal", "Live VM status, bulk power controls, class sessions, snapshots, and MTTR reports."),
            ("Student Portal", "Personal status cards, Last Checked telemetry, restore requests, and Golden Master VM cloning."),
            ("Autonomous Worker", "10s polling, 2-cycle debouncing, auto-rollback on crash/freeze/pause, and 3/hr circuit breaker."),
            ("Backups & Alerting", "Standalone .ova exports, hourly DB hot-backups, SMTP email, HMAC webhooks, and REST API."),
        ],
        accent_color=NAVY
    )

    add_card(
        s_features, 4.77, 1.42, 3.80, 5.40,
        "Architecture & Technologies",
        [
            ("Backend & Web", "Python 3.14, Flask 3.x Blueprints, Jinja2, Waitress multi-threaded WSGI."),
            ("Hypervisor Layer", "Oracle VirtualBox 7.2 (VBoxManage CLI) + SimulatedVBox cloud demo engine."),
            ("Dual Database", "SQLite 3 (WAL mode) on local lab hosts; Supabase Managed PostgreSQL in the cloud."),
            ("Security", "Werkzeug PBKDF2 password hashing, CSRF tokens, RBAC, CSP headers, and systemd hardening."),
        ],
        accent_color=MAROON
    )

    add_card(
        s_features, 8.79, 1.42, 3.80, 5.40,
        "Execution Steps & Hosting",
        [
            ("1. Analysis & Design", "DFDs (Level 0 & 1), 10-table ERD, UML Use Case & Class Diagrams."),
            ("2. Build & Testing", "Iterative development validated by 154/154 passing automated pytest cases."),
            ("3. On-Premise Host", "Linux systemd service (vmrecovery.service) + Cloudflare Zero-Trust HTTPS tunnel."),
            ("4. Live Cloud Demo", "Render PaaS (vmrecovery-demo.onrender.com) + Supabase PostgreSQL for 24/7 live evaluation."),
        ],
        accent_color=NAVY, bg_color=SOFT_NAVY_BG
    )

    set_notes(
        s_features,
        "Here is an overview of the entire system in three columns: First, the core features — Admin/Trainer dashboard, Student portal "
        "with live status and VM requests, 10-second autonomous recovery worker, and OVA backups with alerts. "
        "Second, our stack — Python/Flask/Waitress, VirtualBox CLI plus simulation mode, SQLite WAL locally and Supabase PostgreSQL in the cloud. "
        "Third, our execution — from design diagrams to 154 passing tests and live deployment on both the local lab host and Render at "
        "vmrecovery-demo.onrender.com. I am now ready to show the live demo and take your questions."
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print(f"SUCCESS: Created concise {total}-slide presentation at {OUTPUT_PATH}")


if __name__ == "__main__":
    build_presentation()
