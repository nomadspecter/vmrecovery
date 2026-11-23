"""Build a clean, easy-to-follow 8-slide Zetech University Project Defense Presentation (.pptx)
built directly on the official school template:
  /home/nomad/Downloads/4. Project presentation Template.pptx

Outputs:
  Milestones/Project_Presentation_8Slides_SimonNdonga.pptx
"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = "/home/nomad/Downloads/4. Project presentation Template.pptx"
OUTPUT_PATH = "Milestones/Project_Presentation_8Slides_SimonNdonga.pptx"

NAVY = RGBColor(0x00, 0x1C, 0x54)
MAROON = RGBColor(0x98, 0x00, 0x00)
DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
MUTED_TEXT = RGBColor(0x47, 0x55, 0x69)
CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)
CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
SOFT_NAVY_BG = RGBColor(0xEF, 0xF6, 0xFF)
GREEN_TEXT = RGBColor(0x15, 0x80, 0x3D)
GREEN_BG = RGBColor(0xF0, 0xFD, 0xF4)
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
            r.font.size = Pt(27)
            r.font.bold = True
            r.font.color.rgb = NAVY
            break


def clear_body_placeholder(slide):
    for shape in list(slide.placeholders):
        if shape.placeholder_format.idx == 1:
            sp = shape._element
            sp.getparent().remove(sp)


def add_top_accent_bar(slide):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.43), Inches(0.25), Inches(6.63), Inches(0.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.10), Inches(0.25), Inches(1.20), Inches(0.05))
    accent.fill.solid()
    accent.fill.fore_color.rgb = MAROON
    accent.line.fill.background()


def add_footer(slide, page_num: int, total_pages: int = 8):
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
    for idx, (lead, body) in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.20
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
    rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    rect.adjustments[0] = 0.12
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg_color
    rect.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(left + 0.24), Inches(top + 0.14), Inches(width - 0.48), Inches(height - 0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = 1.18
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


def add_card(slide, left, top, width, height, title, items, accent_color=NAVY, bg_color=CARD_BG, body_size=12):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    box.adjustments[0] = 0.04
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = CARD_BORDER
    box.line.width = Pt(1.0)
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left + 0.08), Inches(top), Inches(width - 0.16), Inches(0.06))
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.16), Inches(width - 0.36), Inches(height - 0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p0 = tf.paragraphs[0]
    p0.space_after = Pt(8)
    r0 = p0.add_run()
    r0.text = title
    r0.font.name = FONT_HEADING
    r0.font.size = Pt(14.5)
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


def add_kpi_tile(slide, left, top, width, height, value, label, accent=NAVY, bg=SOFT_NAVY_BG):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    box.adjustments[0] = 0.08
    box.fill.solid()
    box.fill.fore_color.rgb = bg
    box.line.color.rgb = accent
    box.line.width = Pt(1.2)
    tb = slide.shapes.add_textbox(Inches(left + 0.10), Inches(top + 0.12), Inches(width - 0.20), Inches(height - 0.20))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = value
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(22)
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


def add_picture_fit(slide, img_path, left, top, max_w, max_h):
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
    frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x - 0.04), Inches(y - 0.04), Inches(w + 0.08), Inches(h + 0.08))
    frame.fill.solid()
    frame.fill.fore_color.rgb = WHITE
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = Pt(1.0)
    slide.shapes.add_picture(img_path, Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def move_slide(prs, old_index, new_index):
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    el = slides[old_index]
    xml_slides.remove(el)
    xml_slides.insert(new_index, el)


def build_8slide_presentation():
    prs = Presentation(TEMPLATE_PATH)
    s_title, s_problem, s_justif, s_obj, s_arch, _s_thanks = list(prs.slides)
    obj_layout = prs.slide_layouts[1]
    s_features = prs.slides.add_slide(obj_layout)
    s_results = prs.slides.add_slide(obj_layout)
    move_slide(prs, 5, len(prs.slides) - 1)  # THANK YOU -> Slide 8
    total = len(prs.slides)  # 8 slides

    # SLIDE 1: TITLE SLIDE
    for shape in s_title.shapes:
        if shape.shape_id == 45:
            shape.text_frame.clear()
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
            r.text = "Automated Crash Recovery, Snapshot Scheduling & Hybrid Lab Management"
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
    set_notes(s_title, "Introduce yourself (Simon Ndonga, DCS-02-0200/2025) and the project: VMRecovery, an automated VirtualBox recovery and management system for IT training labs.")

    # SLIDE 2: PROBLEM STATEMENT
    style_slide_title(s_problem, "Problem Statement")
    clear_body_placeholder(s_problem)
    add_footer(s_problem, 2, total)
    add_bullet_list(s_problem, 0.85, 1.50, 11.65, 4.30, [
        ("Frequent VM Crashes & Freezes", "Student misconfigurations and experimental commands frequently crash or hang VirtualBox VMs during practicals."),
        ("Slow Manual Recovery", "Lab technicians spend 20–45 minutes manually rebuilding or resetting broken VMs, stalling lessons."),
        ("Inconsistent Snapshots", "Manual pre-session snapshots are easily forgotten, leaving no clean rollback point when a guest OS breaks."),
        ("No Centralized Visibility", "Instructors lack a single dashboard to monitor lab VM health, manage sessions, or approve student VM requests."),
        ("Poor Audit Accountability", "Manual VirtualBox GUI fixes leave no structured logs of crash frequency or recovery speed."),
    ])
    add_banner(s_problem, 0.85, 5.95, 11.65, 0.82, "CORE PROBLEM",
               "IT training labs lack automated crash detection, scheduled snapshot protection, and fast self-healing for VirtualBox VMs.", bg_color=MAROON)
    set_notes(s_problem, "Walk through the 5 pain points in IT labs — emphasize the 20–45 minutes lost per broken machine.")

    # SLIDE 3: JUSTIFICATION
    style_slide_title(s_justif, "Justification")
    clear_body_placeholder(s_justif)
    add_footer(s_justif, 3, total)
    add_bullet_list(s_justif, 0.85, 1.50, 11.65, 4.30, [
        ("Zero-Touch Sub-10s Recovery", "Automatically detects crashed, frozen, or paused VMs and restores the latest clean snapshot in under 10 seconds."),
        ("Uninterrupted Learning", "Eliminates practical downtime and lets students experiment safely with pre-session snapshot baselines."),
        ("Reduced Technician Workload", "Automates 10s health polling, snapshot retention pruning, class sessions, and Golden Master VM cloning."),
        ("Full Accountability & Reporting", "Immutable audit trail, MTTR reliability reports, CSV exports, and real-time SMTP/webhook incident alerts."),
        ("Cost-Effective & Secure", "100% open-source stack on existing lab hosts with RBAC, PBKDF2 hashing, CSRF protection, and HTTPS cloud hosting."),
    ])
    add_banner(s_justif, 0.85, 5.95, 11.65, 0.82, "PROVEN VALUE",
               "Verified with 154/154 automated tests passing (100% pass rate) and 8.4s measured crash-to-boot recovery.", bg_color=NAVY)
    set_notes(s_justif, "Highlight speed (<10s recovery), zero software licensing cost, and 154/154 passing tests.")

    # SLIDE 4: OBJECTIVES
    style_slide_title(s_obj, "Objectives")
    clear_body_placeholder(s_obj)
    add_footer(s_obj, 4, total)
    add_banner(s_obj, 0.85, 1.42, 11.65, 0.92, "GENERAL OBJECTIVE",
               "To design, develop, test, and deploy an automated Virtual Machine Instability Management System that monitors lab VMs, schedules snapshots, and autonomously recovers failed machines.", bg_color=NAVY)
    lbl = s_obj.shapes.add_textbox(Inches(0.85), Inches(2.50), Inches(6.0), Inches(0.38))
    r = lbl.text_frame.paragraphs[0].add_run()
    r.text = "Specific Objectives"
    r.font.name = FONT_HEADING
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = MAROON
    add_bullet_list(s_obj, 0.85, 2.98, 11.65, 3.85, [
        ("Centralized VM Registry & Sessions", "Map VirtualBox UUIDs to class groups, snapshot policies, and student accounts with one-click session controls."),
        ("Automated Snapshot & .OVA Backups", "Enforce scheduled, pre-session, and post-session snapshots with retention pruning and portable .ova exports."),
        ("Zero-Touch Autonomous Recovery", "Poll VM states and guest heartbeats every 10s with 2-cycle debouncing and a 3/hr anti-thrashing circuit breaker."),
        ("Student Self-Service & RBAC Security", "Provide Golden Master VM cloning requests, Admin/Trainer/Student roles, alerts, and a live cloud demo."),
    ], font_size=14, space_after=13)
    set_notes(s_obj, "Read the General Objective briefly, then summarize the 4 specific objectives.")

    # SLIDE 5: SYSTEM ARCHITECTURE & TECH STACK
    style_slide_title(s_arch, "System Architecture & Technology Stack")
    clear_body_placeholder(s_arch)
    add_footer(s_arch, 5, total)
    add_picture_fit(s_arch, "Milestones/figures/fig3_1_architecture.png", 0.75, 1.42, 7.55, 5.35)
    add_card(s_arch, 8.55, 1.42, 4.03, 5.35, "Technology Stack", [
        ("Web & Backend", "Python 3.14, Flask 3.x Blueprints, Waitress WSGI (systemd)"),
        ("Hypervisor Layer", "Oracle VirtualBox 7.2 (VBoxManage CLI) + Simulation Engine"),
        ("Dual Database", "SQLite 3 (WAL mode) locally & Supabase PostgreSQL in cloud"),
        ("Security", "PBKDF2 hashing, CSRF tokens, RBAC, HMAC-SHA256 webhooks"),
        ("Cloud Demo", "Render PaaS (vmrecovery-demo.onrender.com) + Supabase PostgreSQL"),
    ], accent_color=NAVY, body_size=11.5)
    set_notes(s_arch, "Point to the layered diagram: Web UI & REST API -> Services -> VBoxManage / SQLite WAL / Supabase PostgreSQL.")

    # SLIDE 6: CORE FEATURES & LIVE SYSTEM WALKTHROUGH
    add_top_accent_bar(s_features)
    style_slide_title(s_features, "Core Features & System Walkthrough")
    clear_body_placeholder(s_features)
    add_footer(s_features, 6, total)
    add_picture_fit(s_features, "Milestones/figures/screen_dashboard.png", 0.75, 1.42, 6.20, 3.95)
    add_banner(s_features, 0.75, 5.52, 6.20, 1.25, "LIVE DASHBOARD",
               "Real-time VM status cards, bulk Start/Stop/Pause controls, class session triggers, and instant Sim. Crash / Sim. Freeze demo buttons.", bg_color=NAVY)
    add_card(s_features, 7.20, 1.42, 5.38, 5.35, "What I Will Demonstrate Live", [
        ("1. Role-Based Portals", "Admin/Trainer operations dashboard + dedicated Student Portal with personal status cards & Last Checked telemetry."),
        ("2. Class Session Snapshots", "One-click Start Session boots lab VMs and captures pre-session baselines automatically."),
        ("3. Autonomous Self-Healing", "Triggering a Crash, Freeze, or Pause -> 10s worker detects fault -> auto-restores clean snapshot & reboots."),
        ("4. Student VM Provisioning", "Student requests a VM from a Golden Master template -> Admin approves -> clone provisioned & assigned."),
        ("5. Backups & Audit Trail", "Standalone .ova disaster exports, MTTR reports, and immutable event logs."),
    ], accent_color=MAROON, body_size=11.5)
    set_notes(s_features, "Use this slide to preview your live demo steps so the panel knows exactly what you are about to show them.")

    # SLIDE 7: TESTING, HYBRID DEPLOYMENT & LIVE ACCESS
    add_top_accent_bar(s_results)
    style_slide_title(s_results, "Testing, Hybrid Deployment & Live Demo Access")
    clear_body_placeholder(s_results)
    add_footer(s_results, 7, total)
    add_kpi_tile(s_results, 0.75, 1.40, 2.78, 1.12, "154 / 154", "Pytest Cases Passing (100%)", GREEN_TEXT, GREEN_BG)
    add_kpi_tile(s_results, 3.77, 1.40, 2.78, 1.12, "8.4 sec", "Measured Crash Recovery", NAVY, SOFT_NAVY_BG)
    add_kpi_tile(s_results, 6.79, 1.40, 2.78, 1.12, "3 Roles", "Admin, Trainer & Student RBAC", MAROON, RGBColor(0xFE, 0xF2, 0xF2))
    add_kpi_tile(s_results, 9.81, 1.40, 2.77, 1.12, "24/7 Live", "Render + Supabase Cloud Demo", NAVY, SOFT_NAVY_BG)

    add_card(s_results, 0.75, 2.76, 5.75, 4.02, "Hybrid Edge-Cloud Deployment", [
        ("On-Premises Lab Host", "Linux systemd (vmrecovery.service) + Waitress WSGI + Oracle VirtualBox 7.2 + SQLite WAL."),
        ("Independent Backups", "Standalone .ova appliance exports & hourly online SQLite hot backups with 7-day retention."),
        ("Render Cloud PaaS", "Public live demo at https://vmrecovery-demo.onrender.com (Simulation Mode active)."),
        ("Supabase PostgreSQL", "Managed cloud database (EU Central 1) with TLS pooling & automatic schema migration."),
    ], accent_color=NAVY, body_size=11.8)

    add_card(s_results, 6.83, 2.76, 5.75, 4.02, "Key Achievements & Future Work", [
        ("100% Objectives Met", "All 4 specific objectives implemented, tested across 7 pytest suites, and deployed live."),
        ("Solved Real Faults", "SQLite WAL concurrency, VirtualBox live-snapshot locks, systemd setuid access, and cloud DB hydration."),
        ("Future: Multi-Hypervisor", "Extend controller layer to support Proxmox VE, KVM/QEMU, and VMware ESXi clusters."),
        ("Future: Embedded Console", "Add HTML5 noVNC/RDP directly inside the Student Portal and university SSO login."),
    ], accent_color=MAROON, bg_color=SOFT_NAVY_BG, body_size=11.8)
    set_notes(s_results, "Summarize your test results (154/154 tests, 8.4s recovery), show the live Render URL vmrecovery-demo.onrender.com, and invite questions / begin the live demo.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print(f"SUCCESS: Created 8-slide walkthrough presentation at {OUTPUT_PATH}")


if __name__ == "__main__":
    build_8slide_presentation()
