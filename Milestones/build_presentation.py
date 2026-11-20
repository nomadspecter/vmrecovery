"""Build the official Zetech University Project Defense Presentation (.pptx)
using the exact school template:
  /home/nomad/Downloads/4. Project presentation Template.pptx

Outputs:
  Milestones/Project_Presentation_SimonNdonga.pptx
"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = "/home/nomad/Downloads/4. Project presentation Template.pptx"
OUTPUT_PATH = "Milestones/Project_Presentation_SimonNdonga.pptx"

# Zetech University Brand Palette (extracted directly from the school template)
NAVY = RGBColor(0x00, 0x1C, 0x54)
MAROON = RGBColor(0x98, 0x00, 0x00)
DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
MUTED_TEXT = RGBColor(0x47, 0x55, 0x69)
CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)
CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
SOFT_NAVY_BG = RGBColor(0xEF, 0xF6, 0xFF)
SOFT_MAROON_BG = RGBColor(0xFE, 0xF2, 0xF2)
GREEN_TEXT = RGBColor(0x15, 0x80, 0x3D)
GREEN_BG = RGBColor(0xF0, 0xFD, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT_HEADING = "Montserrat"
FONT_BODY = "Montserrat Medium"


def set_notes(slide, text: str):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.clear()
    tf.text = text


def style_slide_title(slide, title_text: str):
    """Style the title placeholder consistently with Zetech branding."""
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == 0:
            shape.left = Inches(0.75)
            shape.top = Inches(0.42)
            shape.width = Inches(11.83)
            shape.height = Inches(0.85)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = title_text
            r.font.name = FONT_HEADING
            r.font.size = Pt(26)
            r.font.bold = True
            r.font.color.rgb = NAVY
            break


def clear_body_placeholder(slide):
    """Remove unused empty body placeholder so custom structured layouts stay clean."""
    for shape in list(slide.placeholders):
        if shape.placeholder_format.idx == 1:
            sp = shape._element
            sp.getparent().remove(sp)


def add_top_accent_bar(slide):
    """Add Zetech's signature top navy accent line + small maroon highlight."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.43), Inches(0.25), Inches(6.63), Inches(0.05)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()

    accent = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(7.10), Inches(0.25), Inches(1.20), Inches(0.05)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = MAROON
    accent.line.fill.background()


def add_footer(slide, page_num: int, total_pages: int):
    """Subtle academic footer on content slides."""
    tb = slide.shapes.add_textbox(Inches(0.75), Inches(7.05), Inches(9.5), Inches(0.32))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Zetech University  |  Simon Ndonga (DCS-02-0200/2025)  |  VM Instability Management System"
    r.font.name = FONT_BODY
    r.font.size = Pt(9.5)
    r.font.color.rgb = MUTED_TEXT

    nb = slide.shapes.add_textbox(Inches(11.3), Inches(7.05), Inches(1.3), Inches(0.32))
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


def add_card(slide, left, top, width, height, title, bullets,
             accent_color=NAVY, bg_color=CARD_BG, title_size=14, body_size=11.5):
    """Add a clean bordered card with a top accent bar, title, and bullet points."""
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.adjustments[0] = 0.04
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = CARD_BORDER
    box.line.width = Pt(1.0)

    # Top accent strip
    strip = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left + 0.08), Inches(top), Inches(width - 0.16), Inches(0.06)
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.18), Inches(top + 0.14), Inches(width - 0.36), Inches(height - 0.22)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    p0.space_after = Pt(6)
    r0 = p0.add_run()
    r0.text = title
    r0.font.name = FONT_HEADING
    r0.font.size = Pt(title_size)
    r0.font.bold = True
    r0.font.color.rgb = accent_color

    for item in bullets:
        p = tf.add_paragraph()
        p.space_after = Pt(4)
        p.line_spacing = 1.15
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run()
            r1.text = f"• {lead}: "
            r1.font.name = FONT_HEADING
            r1.font.size = Pt(body_size)
            r1.font.bold = True
            r1.font.color.rgb = DARK_TEXT
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_BODY
            r2.font.size = Pt(body_size)
            r2.font.color.rgb = MUTED_TEXT
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.name = FONT_BODY
            r.font.size = Pt(body_size)
            r.font.color.rgb = DARK_TEXT


def add_banner(slide, left, top, width, height, label, text, bg_color=NAVY):
    """Add a solid branded banner (e.g., General Objective or Key Metric)."""
    rect = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    rect.adjustments[0] = 0.08
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg_color
    rect.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.22), Inches(top + 0.12), Inches(width - 0.44), Inches(height - 0.20)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.line_spacing = 1.15
    r1 = p.add_run()
    r1.text = f"{label}: "
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = WHITE

    r2 = p.add_run()
    r2.text = text
    r2.font.name = FONT_BODY
    r2.font.size = Pt(12.5)
    r2.font.color.rgb = WHITE


def add_picture_fit(slide, img_path, left, top, max_w, max_h, border=True):
    """Insert an image scaled proportionally to fit inside (max_w, max_h), centered."""
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Missing image: {img_path}")
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = iw / ih
    if max_w / max_h > ratio:
        h = max_h
        w = h * ratio
    else:
        w = max_w
        h = w / ratio
    x = left + (max_w - w) / 2
    y = top + (max_h - h) / 2

    if border:
        frame = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(x - 0.04), Inches(y - 0.04), Inches(w + 0.08), Inches(h + 0.08)
        )
        frame.fill.solid()
        frame.fill.fore_color.rgb = WHITE
        frame.line.color.rgb = CARD_BORDER
        frame.line.width = Pt(1.0)

    slide.shapes.add_picture(img_path, Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def add_kpi_tile(slide, left, top, width, height, value, label, accent=NAVY, bg=SOFT_NAVY_BG):
    """Add a clean KPI stat tile."""
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.adjustments[0] = 0.08
    box.fill.solid()
    box.fill.fore_color.rgb = bg
    box.line.color.rgb = accent
    box.line.width = Pt(1.2)

    tb = slide.shapes.add_textbox(
        Inches(left + 0.12), Inches(top + 0.12), Inches(width - 0.24), Inches(height - 0.20)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = value
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(24)
    r1.font.bold = True
    r1.font.color.rgb = accent

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(3)
    r2 = p2.add_run()
    r2.text = label
    r2.font.name = FONT_BODY
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = DARK_TEXT


def move_slide(prs, old_index, new_index):
    """Reorder slide in presentation XML."""
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    el = slides[old_index]
    xml_slides.remove(el)
    xml_slides.insert(new_index, el)


def build_presentation():
    print(f"Loading Zetech University template: {TEMPLATE_PATH}")
    prs = Presentation(TEMPLATE_PATH)

    # Keep references to existing template slides:
    # 0 = Title, 1 = Problem Statement, 2 = Justification, 3 = Objectives,
    # 4 = Features/Project Details, 5 = THANK YOU (will be moved to end)
    s_title = prs.slides[0]
    s_problem = prs.slides[1]
    s_justif = prs.slides[2]
    s_obj = prs.slides[3]
    s_features = prs.slides[4]
    # s_thanks = prs.slides[5]  -> preserved untouched and moved to final slide!

    # Add 6 additional content slides using the template's 'OBJECT' layout (index 1)
    obj_layout = prs.slide_layouts[1]
    s_arch = prs.slides.add_slide(obj_layout)
    s_recovery = prs.slides.add_slide(obj_layout)
    s_ui = prs.slides.add_slide(obj_layout)
    s_testing = prs.slides.add_slide(obj_layout)
    s_deploy = prs.slides.add_slide(obj_layout)
    s_conc = prs.slides.add_slide(obj_layout)

    # Move THANK YOU slide (originally index 5) to the very end (index 11)
    move_slide(prs, 5, len(prs.slides) - 1)
    total_slides = len(prs.slides)  # 12 slides

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Zetech University Branded Cover)
    # =========================================================================
    for shape in s_title.shapes:
        if shape.shape_id == 45:
            # Remove the stray 'v' typo present in the school template's navy box
            shape.text_frame.clear()
        elif shape.shape_id == 46:
            shape.top = Inches(3.32)
            shape.height = Inches(1.05)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.line_spacing = 1.1
            r = p.add_run()
            r.text = "VIRTUAL MACHINE INSTABILITY MANAGEMENT SYSTEM FOR IT TRAINING LABS"
            r.font.name = FONT_HEADING
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = WHITE
        elif shape.shape_id == 47:
            shape.top = Inches(4.42)
            shape.height = Inches(0.45)
            tf = shape.text_frame
            tf.clear()
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "Zero-Touch Crash Detection, Snapshot Orchestration & Hybrid Lab Management"
            r.font.name = FONT_BODY
            r.font.size = Pt(12.5)
            r.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        elif shape.shape_id == 48:
            shape.top = Inches(4.92)
            shape.height = Inches(0.38)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "November 2026  |  Department of ICT & Computer Science"
            r.font.name = FONT_BODY
            r.font.size = Pt(12)
            r.font.color.rgb = WHITE
        elif shape.shape_id == 49:
            shape.top = Inches(5.32)
            shape.height = Inches(0.55)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "Simon Ndonga  |  DCS-02-0200/2025  |  Diploma in Computer Science"
            r.font.name = FONT_HEADING
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = WHITE

    set_notes(
        s_title,
        "Good morning/afternoon panel members. My name is Simon Ndonga, Admission Number DCS-02-0200/2025, "
        "pursuing a Diploma in Computer Science at Zetech University. Today I am presenting my project: "
        "The Virtual Machine Instability Management System for IT Training Labs (VMRecovery) — an automated "
        "platform for zero-touch crash detection, snapshot orchestration, and hybrid lab management."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    style_slide_title(s_problem, "Problem Statement")
    clear_body_placeholder(s_problem)
    add_footer(s_problem, 2, total_slides)

    add_banner(
        s_problem, 0.75, 1.38, 11.83, 0.92,
        "CORE CHALLENGE",
        "IT training laboratories rely heavily on VirtualBox VMs for hands-on networking, OS, and cybersecurity practicals, "
        "yet frequent student misconfigurations, kernel panics, and OS freezes disrupt classes and require slow manual recovery.",
        bg_color=MAROON
    )

    add_card(
        s_problem, 0.75, 2.52, 5.75, 4.25,
        "Operational Bottlenecks in Training Labs",
        [
            ("Frequent VM Instability", "Experimental commands, corrupted configs, and memory exhaustion cause sudden crashes and frozen guest OS states."),
            ("Manual Recovery Delays", "Lab technicians manually inspect, power-cycle, and rebuild broken VMs—losing 20–45 minutes per practical session."),
            ("Inconsistent Snapshots", "Ad-hoc manual snapshots are easily forgotten before lab sessions, leaving no clean rollback point."),
            ("No Centralized Visibility", "Instructors lack a real-time dashboard to monitor VM health across an entire classroom.")
        ],
        accent_color=NAVY
    )

    add_card(
        s_problem, 6.83, 2.52, 5.75, 4.25,
        "Impact on Students & Institutions",
        [
            ("Lost Instructional Time", "Practical lessons stall while instructors troubleshoot individual broken student machines."),
            ("High Technician Workload", "Repetitive VM cloning, resetting, and provisioning consume valuable IT support hours."),
            ("Zero Audit Accountability", "Manual VirtualBox GUI interventions leave no structured logs of crash frequency or recovery duration."),
            ("Risk of Data & Lab Loss", "Without automated `.ova` backups and retention pruning, host disk exhaustion or corruption breaks entire lab setups.")
        ],
        accent_color=MAROON,
        bg_color=SOFT_MAROON_BG
    )

    set_notes(
        s_problem,
        "In university IT training labs, students regularly run destructive or experimental commands inside VirtualBox VMs. "
        "When a VM crashes or freezes, lab technicians have to manually rebuild or reset it, wasting 20 to 45 minutes of class time. "
        "There is no automated heartbeat monitoring, no scheduled pre-session snapshotting, and no centralized audit trail."
    )

    # =========================================================================
    # SLIDE 3: JUSTIFICATION
    # =========================================================================
    style_slide_title(s_justif, "Justification")
    clear_body_placeholder(s_justif)
    add_footer(s_justif, 3, total_slides)

    # Top KPI impact strip
    add_kpi_tile(s_justif, 0.75, 1.42, 2.75, 1.15, "< 10 sec", "Autonomous Snapshot Rollback", NAVY, SOFT_NAVY_BG)
    add_kpi_tile(s_justif, 3.78, 1.42, 2.75, 1.15, "Zero-Touch", "Unattended Crash & Freeze Healing", GREEN_TEXT, GREEN_BG)
    add_kpi_tile(s_justif, 6.81, 1.42, 2.75, 1.15, "100%", "Open-Source Zero-License Stack", MAROON, SOFT_MAROON_BG)
    add_kpi_tile(s_justif, 9.83, 1.42, 2.75, 1.15, "24/7", "Remote Access & Cloud Demo Tier", NAVY, SOFT_NAVY_BG)

    add_card(
        s_justif, 0.75, 2.82, 3.75, 3.95,
        "Academic Value",
        [
            ("Uninterrupted Learning", "Students resume practicals within seconds after a crash instead of waiting for manual rebuilds."),
            ("Safe Experimentation", "Pre-session baselines encourage hands-on exploration without fear of permanently breaking lab VMs."),
            ("Self-Service Portal", "Students can request lab VMs and restores transparently.")
        ],
        accent_color=NAVY
    )

    add_card(
        s_justif, 4.79, 2.82, 3.75, 3.95,
        "Operational Efficiency",
        [
            ("Automated Governance", "Replaces manual VBoxManage CLI work with a 10-second background monitoring daemon."),
            ("Anti-Thrashing Safety", "2-cycle failure debouncing and a 3-restores/hour circuit breaker prevent endless boot loops."),
            ("Audit & Reporting", "Immutable event logs and CSV exports support institutional IT reporting.")
        ],
        accent_color=MAROON
    )

    add_card(
        s_justif, 8.83, 2.82, 3.75, 3.95,
        "Economic & Security Fit",
        [
            ("Budget-Friendly", "Runs on existing university VirtualBox hosts using Python, Flask, SQLite, and Waitress—avoiding costly VMware/bare-metal cloud fees."),
            ("Zero-Trust Ingress", "Cloudflare Tunnels expose dashboards securely over HTTPS without opening campus firewall ports."),
            ("RBAC Hardening", "PBKDF2 password hashing, CSRF tokens, and role-based isolation.")
        ],
        accent_color=GREEN_TEXT
    )

    set_notes(
        s_justif,
        "Why is this system justified? First, academically, it recovers crashed VMs in under 10 seconds so class time is never lost. "
        "Second, operationally, it eliminates repetitive manual intervention using debounced zero-touch recovery. "
        "Third, financially, it runs on existing lab hardware using open-source software, avoiding expensive enterprise hypervisor licenses."
    )

    # =========================================================================
    # SLIDE 4: OBJECTIVES
    # =========================================================================
    style_slide_title(s_obj, "Objectives")
    clear_body_placeholder(s_obj)
    add_footer(s_obj, 4, total_slides)

    add_banner(
        s_obj, 0.75, 1.38, 11.83, 0.95,
        "GENERAL OBJECTIVE",
        "To design, develop, test, and deploy an automated Virtual Machine Instability Management System that continuously "
        "monitors lab VMs, enforces scheduled snapshot policies, and autonomously restores failed machines in under 10 seconds.",
        bg_color=NAVY
    )

    add_card(
        s_obj, 0.75, 2.55, 5.75, 1.98,
        "Specific Objective 1: Centralized VM Registry",
        [
            "Build a centralized registry mapping Oracle VirtualBox hardware UUIDs to academic class groups, snapshot policies, and student assignments.",
            "Support direct VBoxManage CLI discovery and bulk class session controls."
        ],
        accent_color=NAVY, title_size=13.5, body_size=11
    )

    add_card(
        s_obj, 6.83, 2.55, 5.75, 1.98,
        "Specific Objective 2: Automated Snapshot Orchestration",
        [
            "Implement interval-based automatic snapshots, pre-session/post-session baselines, and manual snapshot capture.",
            "Enforce automated retention pruning and host low-disk-space protection."
        ],
        accent_color=MAROON, title_size=13.5, body_size=11
    )

    add_card(
        s_obj, 0.75, 4.75, 5.75, 1.98,
        "Specific Objective 3: Zero-Touch Autonomous Recovery",
        [
            "Develop a background worker daemon polling VM power states and guest heartbeats every 10 seconds.",
            "Apply 2-cycle failure debouncing, admin-pause awareness, and automated rollback upon confirmed crashes or freezes."
        ],
        accent_color=GREEN_TEXT, title_size=13.5, body_size=11
    )

    add_card(
        s_obj, 6.83, 4.75, 5.75, 1.98,
        "Specific Objective 4: Provisioning, Security & Hybrid Access",
        [
            "Provide a Golden Master student VM provisioning workflow, SMTP/HMAC webhook alerting, and `.ova` appliance exports.",
            "Enforce Admin/Trainer/Student RBAC and deploy a verifiable hybrid edge-cloud architecture."
        ],
        accent_color=NAVY, title_size=13.5, body_size=11
    )

    set_notes(
        s_obj,
        "Our general objective was to build and deploy a complete zero-touch VM recovery system for IT training labs. "
        "We broke this down into four specific objectives: centralized VM registry, automated snapshot orchestration with retention pruning, "
        "autonomous crash and freeze recovery, and secure multi-role provisioning with hybrid deployment."
    )

    # =========================================================================
    # SLIDE 5: FEATURES / PROJECT DETAILS / PROJECT EXECUTION STEPS
    # =========================================================================
    style_slide_title(s_features, "Features, Project Details & Execution Steps")
    clear_body_placeholder(s_features)
    add_footer(s_features, 5, total_slides)

    add_card(
        s_features, 0.75, 1.40, 5.80, 5.35,
        "Core System Modules Implemented",
        [
            ("VM Registry & Class Sessions", "Groups VMs by class; triggers pre-session baselines and post-session cleanups in one click."),
            ("Autonomous Worker Daemon", "10s polling loop with 2-cycle debouncing, admin_paused flag, and 3/hr anti-thrashing circuit breaker."),
            ("Snapshot & .OVA Backup Engine", "Crash-consistent sub-second snapshots, retention pruning, and portable `.ova` disaster recovery archives."),
            ("Student Provisioning Portal", "Students request VMs cloned from Golden Master templates (linked or full clone) pending Trainer/Admin approval."),
            ("Alerting & REST API", "SMTP email alerts, HMAC-SHA256 signed webhooks, and Bearer-token authenticated `/api/v1` telemetry endpoints."),
            ("Dual-Database Persistence", "SQLite (WAL mode) on bare-metal lab hosts + Supabase Managed PostgreSQL (`app/pg_db.py`) for cloud deployment.")
        ],
        accent_color=NAVY, body_size=11
    )

    add_card(
        s_features, 6.83, 1.40, 5.75, 5.35,
        "Project Execution Steps (Iterative SDLC)",
        [
            ("Phase 1: Requirements & Analysis", "Identified lab bottlenecks; designed Level 0/1 DFDs, ERD (10 tables), UML Use Cases, and Class Diagrams."),
            ("Phase 2: Core Backend & Hypervisor Layer", "Built `VBoxController` CLI wrapper, `SimulatedVBox` test harness, SQLite WAL engine, and 8 sequential migrations."),
            ("Phase 3: Autonomous Recovery & RBAC UI", "Implemented `app/worker.py`, debounced rollback engine, Flask blueprints, and Admin/Trainer/Student dashboards."),
            ("Phase 4: Comprehensive Verification", "Authored 154 automated tests (`pytest`) covering unit logic, failure modes, VirtualBox integration, and security."),
            ("Phase 5: Hybrid Production Deployment", "Hardened `vmrecovery.service` (systemd + Waitress), configured Cloudflare Zero-Trust tunnel, and launched live Render + Supabase demo.")
        ],
        accent_color=MAROON, bg_color=SOFT_NAVY_BG, body_size=11
    )

    set_notes(
        s_features,
        "On the left are the six core modules we engineered—covering VM registry, autonomous healing, snapshotting and OVA backups, "
        "student self-service provisioning, multi-channel alerting, and dual-database persistence. "
        "On the right is our 5-phase iterative execution path from requirements analysis all the way to hardened production deployment."
    )

    # =========================================================================
    # SLIDE 6: SYSTEM ARCHITECTURE & TECHNOLOGY STACK
    # =========================================================================
    add_top_accent_bar(s_arch)
    style_slide_title(s_arch, "System Architecture & Technology Stack")
    clear_body_placeholder(s_arch)
    add_footer(s_arch, 6, total_slides)

    add_picture_fit(s_arch, "Milestones/figures/fig3_1_architecture.png", 0.75, 1.40, 7.65, 5.35, border=True)

    add_card(
        s_arch, 8.65, 1.40, 3.93, 5.35,
        "Technology Stack",
        [
            ("Language & Web", "Python 3.14, Flask 3.x Blueprints, Jinja2 templates"),
            ("WSGI Server", "Waitress multi-threaded WSGI (8 threads, systemd supervised)"),
            ("Hypervisor Layer", "Oracle VirtualBox 7.2 (`VBoxManage` CLI + `SimulatedVBox`)"),
            ("Database Layer", "SQLite 3 (WAL mode, 15s busy timeout) & Supabase PostgreSQL"),
            ("Security", "Werkzeug PBKDF2, CSRF tokens, RBAC, CSP headers, HMAC-SHA256"),
            ("Edge & Cloud", "Cloudflare Zero-Trust (`cloudflared`) & Render PaaS")
        ],
        accent_color=NAVY, body_size=10.8
    )

    set_notes(
        s_arch,
        "This layered architecture cleanly decouples the web interface, business rules in services.py, hypervisor commands in vbox.py, "
        "and persistence in db.py and pg_db.py. Because VBoxManage is isolated behind a controller interface, we can seamlessly swap "
        "between real VirtualBox hardware in the lab and SimulatedVBox for automated tests and cloud demonstrations."
    )

    # =========================================================================
    # SLIDE 7: AUTONOMOUS ZERO-TOUCH RECOVERY WORKFLOW
    # =========================================================================
    add_top_accent_bar(s_recovery)
    style_slide_title(s_recovery, "Autonomous Zero-Touch Recovery Workflow")
    clear_body_placeholder(s_recovery)
    add_footer(s_recovery, 7, total_slides)

    add_picture_fit(s_recovery, "Milestones/figures/fig3_6_worker_flowchart.png", 0.75, 1.38, 4.75, 5.45, border=True)

    add_card(
        s_recovery, 5.80, 1.38, 6.78, 2.55,
        "Intelligent Failure Detection & Safeguards",
        [
            ("State Classification", "Detects `aborted`, `gurumeditation`, `stuck` (Crashed) and unexpected `paused` or stale guest heartbeats (Frozen)."),
            ("2-Cycle Failure Debouncing", "Requires 2 consecutive failed polls (20s) before restoring—eliminating false positives from brief CPU spikes."),
            ("Admin-Pause Protection", "Migration #7 (`admin_paused` flag) distinguishes intentional instructor pauses from genuine OS freezes."),
            ("Anti-Thrashing Circuit Breaker", "Caps auto-restores at 3 per hour; escalates persistent hardware/OS faults to Admin alerts.")
        ],
        accent_color=NAVY, body_size=11
    )

    add_card(
        s_recovery, 5.80, 4.15, 6.78, 2.68,
        "Live Fault Demonstration Scenarios",
        [
            ("Scenario A — Simulated Freeze", "Running `VBoxManage controlvm debian pause` without admin flag -> Suspect (10s) -> Freeze Confirmed (20s) -> Auto-Restored in <10s."),
            ("Scenario B — Abrupt Crash", "Killing headless VM process (`pkill -9`) -> VirtualBox marks `aborted` -> Automatic rollback to latest clean snapshot & reboot."),
            ("Scenario C — Clean Shutdown Ignored", "Normal `powered off` states are respected; worker never undoes intentional student or trainer shutdowns.")
        ],
        accent_color=MAROON, bg_color=SOFT_MAROON_BG, body_size=11
    )

    set_notes(
        s_recovery,
        "Here is how our autonomous recovery worker operates every 10 seconds. It observes each VM's state, debounces transient stalls "
        "over 2 cycles, checks whether an administrator intentionally paused the VM, verifies the anti-thrashing limit of 3 restores per hour, "
        "and then autonomously powers off, rolls back to the latest clean snapshot, and reboots the machine in under 10 seconds."
    )

    # =========================================================================
    # SLIDE 8: LIVE SYSTEM INTERFACE SHOWCASE
    # =========================================================================
    add_top_accent_bar(s_ui)
    style_slide_title(s_ui, "Live System Interface Showcase")
    clear_body_placeholder(s_ui)
    add_footer(s_ui, 8, total_slides)

    # Left screenshot: Admin/Trainer Dashboard
    add_picture_fit(s_ui, "Milestones/figures/screen_dashboard.png", 0.75, 1.45, 5.75, 3.80, border=True)
    add_card(
        s_ui, 0.75, 5.42, 5.75, 1.40,
        "Administrator & Trainer Operations Dashboard",
        [
            "Real-time VM health badges, bulk class session triggers, one-click snapshot/restore controls, and live audit trail telemetry."
        ],
        accent_color=NAVY, title_size=12.5, body_size=10.5
    )

    # Right screenshot: Student Self-Service Portal
    add_picture_fit(s_ui, "Milestones/figures/screen_student_dashboard.png", 6.83, 1.45, 5.75, 3.80, border=True)
    add_card(
        s_ui, 6.83, 5.42, 5.75, 1.40,
        "Student Self-Service Portal (RBAC-Scoped)",
        [
            "Role-isolated view allowing students to monitor assigned lab VMs, request emergency snapshot restores, and request Golden Master clones."
        ],
        accent_color=MAROON, title_size=12.5, body_size=10.5
    )

    set_notes(
        s_ui,
        "These are live screenshots of the running application. On the left is the Administrator and Trainer dashboard showing real-time VM "
        "status, session controls, and snapshot management. On the right is the Student self-service portal, strictly scoped by RBAC so "
        "students only interact with their assigned machines and submit provisioning or restore requests."
    )

    # =========================================================================
    # SLIDE 9: TESTING, VALIDATION & EMPIRICAL RESULTS
    # =========================================================================
    add_top_accent_bar(s_testing)
    style_slide_title(s_testing, "Testing, Validation & Empirical Results")
    clear_body_placeholder(s_testing)
    add_footer(s_testing, 9, total_slides)

    # Top KPI row
    add_kpi_tile(s_testing, 0.75, 1.40, 2.75, 1.15, "154 / 154", "Automated Pytest Cases Passing", GREEN_TEXT, GREEN_BG)
    add_kpi_tile(s_testing, 3.78, 1.40, 2.75, 1.15, "100%", "Verification Pass Rate (0 Defects)", GREEN_TEXT, GREEN_BG)
    add_kpi_tile(s_testing, 6.81, 1.40, 2.75, 1.15, "8.4 sec", "Measured Crash-to-Boot Rollback", NAVY, SOFT_NAVY_BG)
    add_kpi_tile(s_testing, 9.83, 1.40, 2.75, 1.15, "17.2 sec", "Full Test Suite Execution Time", MAROON, SOFT_MAROON_BG)

    # Test Matrix Table
    rows, cols = 8, 4
    tbl_shape = s_testing.shapes.add_table(rows, cols, Inches(0.75), Inches(2.80), Inches(11.83), Inches(3.95))
    tbl = tbl_shape.table
    col_widths = [Inches(2.85), Inches(1.25), Inches(6.43), Inches(1.30)]
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = w

    headers = ["Test Suite Module", "Tests", "Scope Verified", "Status"]
    data = [
        ("test_enterprise.py", "37", "RBAC enforcement, CSRF, rate limiting, HMAC webhooks, REST API, DB backup/restore", "PASS"),
        ("test_services.py", "32", "VM registry, snapshot scheduling, retention pruning, class sessions, reporting", "PASS"),
        ("test_recovery_failure_modes.py", "24", "2-cycle debouncing, admin_paused flag, anti-thrashing circuit breaker, busy timeouts", "PASS"),
        ("test_web.py", "19", "Auth flows, login audit, route protection, template rendering, error handlers", "PASS"),
        ("test_vbox_controller.py", "18", "VBoxManage CLI parsing, command timeouts, state mapping, error resilience", "PASS"),
        ("test_vbox_integration.py", "12", "End-to-end VirtualBox lifecycle, snapshot trees, linked/full clone operations", "PASS"),
        ("test_new_features.py", "12", "Student VM request workflow, Golden Master templates, `.ova` appliance export", "PASS"),
    ]

    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx in (1, 3) else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = h_text
        r.font.name = FONT_HEADING
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = WHITE

    for r_idx, row_vals in enumerate(data, start=1):
        bg = CARD_BG if r_idx % 2 == 1 else WHITE
        for c_idx, val in enumerate(row_vals):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = GREEN_BG if c_idx == 3 else bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c_idx in (1, 3) else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = val
            r.font.name = FONT_HEADING if c_idx in (0, 1, 3) else FONT_BODY
            r.font.size = Pt(10.5)
            r.font.bold = c_idx in (0, 3)
            r.font.color.rgb = GREEN_TEXT if c_idx == 3 else DARK_TEXT

    set_notes(
        s_testing,
        "We validated the entire platform with an automated pytest suite of 154 tests across 7 modules. "
        "All 154 tests pass in 17.2 seconds with zero defects. Notably, our live crash-to-boot recovery test confirmed "
        "end-to-end restoration in 8.4 seconds, well within our 10-second performance target."
    )

    # =========================================================================
    # SLIDE 10: HYBRID EDGE-CLOUD PRODUCTION DEPLOYMENT
    # =========================================================================
    add_top_accent_bar(s_deploy)
    style_slide_title(s_deploy, "Hybrid Edge-Cloud Production Deployment")
    clear_body_placeholder(s_deploy)
    add_footer(s_deploy, 10, total_slides)

    add_picture_fit(s_deploy, "Milestones/figures/fig3_deployment_architecture.png", 0.75, 1.38, 7.65, 5.40, border=True)

    add_card(
        s_deploy, 8.65, 1.38, 3.93, 5.40,
        "4-Pillar Verified Stack",
        [
            ("1. Physical Lab Host", "systemd (`vmrecovery.service`) + Waitress WSGI + SQLite WAL + Oracle VirtualBox 7.2."),
            ("2. Cloudflare Zero-Trust", "Outbound-only encrypted `cloudflared` tunnel for secure remote HTTPS with zero open router ports."),
            ("3. Render Cloud PaaS", "Live public demo at `vmrecovery-demo.onrender.com` with `VMRECOVERY_SIMULATED=true`."),
            ("4. Supabase PostgreSQL", "Managed cloud DB (`aws-0-eu-central-1.pooler.supabase.com:5432`) with TLS & auto-migrations."),
            ("Disaster Recovery", "Portable `.ova` appliance exports & hourly hot SQLite backups with 7-day retention pruning.")
        ],
        accent_color=NAVY, body_size=10.5
    )

    set_notes(
        s_deploy,
        "Because standard cloud containers do not support bare-metal VT-x/AMD-V hardware virtualization, we engineered a 4-Pillar Hybrid "
        "Deployment. VirtualBox runs on the physical lab host under systemd and Waitress; Cloudflare Zero-Trust provides encrypted remote HTTPS; "
        "and our live public demonstration runs on Render PaaS backed by Supabase Managed PostgreSQL so examiners can test it anytime."
    )

    # =========================================================================
    # SLIDE 11: CHALLENGES, MITIGATIONS & RECOMMENDATIONS
    # =========================================================================
    add_top_accent_bar(s_conc)
    style_slide_title(s_conc, "Challenges, Mitigations & Recommendations")
    clear_body_placeholder(s_conc)
    add_footer(s_conc, 11, total_slides)

    add_card(
        s_conc, 0.75, 1.40, 5.80, 5.35,
        "Technical Challenges & Engineering Mitigations",
        [
            ("SQLite Lock Contention", "Default rollback journal caused lock errors under concurrent worker + web writes -> Solved with WAL mode & 15s busy timeout."),
            ("Live Snapshot Hang Locks", "`VBoxManage --live` wedged unresponsive guests in `LiveSnapshotting` -> Made crash-consistent snapshots default & added `wait_until_ready()`."),
            ("Intentional Pause Conflicts", "Worker mistook instructor pauses for freezes -> Added Migration #7 (`admin_paused` flag) to suppress rollback during deliberate pauses."),
            ("Systemd IPC Isolation", "`PrivateTmp=true` broke VirtualBox `/tmp/.vbox-ipc` sockets -> Explicitly set `PrivateTmp=false` while keeping `NoNewPrivileges` & `ProtectSystem=full`."),
            ("Cloud Virtualization Limits", "PaaS containers lack VT-x -> Built `SimulatedVBox` mode so Render + Supabase provides a live verifiable evaluation environment.")
        ],
        accent_color=MAROON, body_size=10.8
    )

    add_card(
        s_conc, 6.83, 1.40, 5.75, 5.35,
        "Conclusions & Future Recommendations",
        [
            ("Project Conclusion", "All 4 specific objectives were fully achieved and verified with 154 passing automated tests and live hybrid deployment."),
            ("Multi-Hypervisor Support", "Extend the controller interface to support KVM/QEMU, Proxmox VE, and VMware ESXi clusters."),
            ("Multi-Host Lab Federation", "Add lightweight host agents so a single central dashboard can manage multiple physical computer labs simultaneously."),
            ("Browser-Based Console (noVNC)", "Embed HTML5 VNC/RDP sessions directly inside the Student Portal for zero-client lab access."),
            ("Institutional SSO Integration", "Integrate university LDAP / Active Directory or Google Workspace OAuth for seamless student onboarding.")
        ],
        accent_color=NAVY, bg_color=SOFT_NAVY_BG, body_size=10.8
    )

    set_notes(
        s_conc,
        "During implementation we overcame five real systems-engineering challenges, including SQLite WAL concurrency, VirtualBox live-snapshot "
        "locks, intentional admin pauses, and systemd IPC isolation. In conclusion, all objectives were met and verified. For future work, "
        "we recommend multi-hypervisor support (Proxmox/KVM), multi-lab federation, embedded browser consoles, and university SSO integration. "
        "Thank you — I am now ready for your questions and live demonstration."
    )

    # Save presentation
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print(f"SUCCESS: Created {OUTPUT_PATH} ({total_slides} slides)")


if __name__ == "__main__":
    build_presentation()
