import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>\n'
                      f'  <w:top w:w="{top}" w:type="dxa"/>\n'
                      f'  <w:bottom w:w="{bottom}" w:type="dxa"/>\n'
                      f'  <w:left w:w="{left}" w:type="dxa"/>\n'
                      f'  <w:right w:w="{right}" w:type="dxa"/>\n'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, color="D9D9D9"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}" w:color="auto" w:val="clear"/>')
    tcPr.append(shd)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>\n'
                        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>\n'
                        f'</w:tblBorders>')
    tblPr.append(borders)

def add_p(doc, text, style=None, bold_prefix="", italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=10, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Montserrat Medium'
        r_pre.font.size = Pt(12)
        r_pre.bold = True
        
    if text:
        r = p.add_run(text)
        r.font.name = 'Montserrat Medium'
        r.font.size = Pt(12)
        r.italic = italic
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.style = 'Heading 1'
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    r.font.name = 'Montserrat Medium'
    r.font.size = Pt(15)
    r.bold = True
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.style = 'Heading 2'
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.font.name = 'Montserrat Medium'
    r.font.size = Pt(13)
    r.bold = True
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.style = 'Heading 3'
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.name = 'Montserrat Medium'
    r.font.size = Pt(12)
    r.bold = True
    return p

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.font.name = 'Montserrat Medium'
    r.font.size = Pt(11)
    r.bold = True
    return p

def add_image_box(doc, img_path, caption_text, width=Inches(6.0)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(img_path, width=width)
        add_caption(doc, caption_text)
    else:
        print(f"Warning: image path not found: {img_path}")

def add_code_snippet(doc, code_str, caption_title, img_path=None):
    # Auto-map to VS Code screenshots if not explicitly provided
    if not img_path:
        mapping = {
            'Listing 3.3.1': 'Milestones/figures/code_3_3_db_wal.png',
            'Listing 3.4.1': 'Milestones/figures/code_3_4_auth.png',
            'Listing 3.5.1': 'Milestones/figures/code_3_5_vbox.png',
            'Listing 3.6.1': 'Milestones/figures/code_3_6_worker.png',
            'Listing 4.1.1': 'Milestones/figures/code_4_1_snapshot.png',
            'Listing 4.2.1': 'Milestones/figures/code_4_2_recovery.png',
            'Listing 4.3.1': 'Milestones/figures/code_4_3_backup.png',
            'Listing 4.4.1': 'Milestones/figures/code_4_4_provisioning.png',
            'Listing 4.5.1': 'Milestones/figures/code_4_5_notifier.png',
            'Listing 4.6.1': 'Milestones/figures/code_4_6_api.png',
            'Listing 4.11.1': 'Milestones/figures/code_4_11_systemd.png',
            'Listing 4.13.1': 'Milestones/figures/code_4_13_supabase_pg.png',
        }
        for prefix, path in mapping.items():
            if prefix in caption_title:
                img_path = path
                break

    if img_path and os.path.exists(img_path):
        add_image_box(doc, img_path, caption_title, width=Inches(6.2))
        return

    add_caption(doc, caption_title)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
    set_cell_shading(cell, color="F8FAFC")
    set_table_borders(tbl)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    
    r = p.add_run(code_str.strip())
    r.font.name = 'Consolas'
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(30, 41, 59)
    
    # Trailing spacer paragraph
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(6)

def update_milestone2(doc):
    # 0. Update Section 1.5.4 paragraph 44 (Client devices) with guest access clarification
    for p in doc.paragraphs:
        if p.text.strip().startswith("Client devices:"):
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
            break

    # 1. Update Table 0 (Functional requirements) to include Student & Administration
    t = doc.tables[0]
    
    # Check if student already in table
    existing_texts = [cell.text for row in t.rows for cell in row.cells]
    if "Student" not in existing_texts:
        # Add Student rows
        row1 = t.add_row()
        row1.cells[0].paragraphs[0].text = "Student"
        row1.cells[1].paragraphs[0].text = "Request a training virtual machine from approved golden templates (linked or full clone)"
        row1.cells[2].paragraphs[0].text = "Self-service VM provisioning portal"
        
        row2 = t.add_row()
        row2.cells[0].paragraphs[0].text = ""
        row2.cells[1].paragraphs[0].text = "Monitor assigned personal VM status and training session progress"
        row2.cells[2].paragraphs[0].text = "Student dashboard view"
        
        row3 = t.add_row()
        row3.cells[0].paragraphs[0].text = ""
        row3.cells[1].paragraphs[0].text = "Update personal login password securely"
        row3.cells[2].paragraphs[0].text = "Self-service Account Settings"

        row4 = t.add_row()
        row4.cells[0].paragraphs[0].text = "Lab administrator"
        row4.cells[1].paragraphs[0].text = "Configure runtime timeouts and monitoring thresholds without restarting the daemon; manage multi-channel alerts and independent backups"
        row4.cells[2].paragraphs[0].text = "Runtime Settings & Multi-Channel Alerting"

        # Format new rows
        for row in [row1, row2, row3, row4]:
            for i, c in enumerate(row.cells):
                set_cell_margins(c, top=80, bottom=80, left=100, right=100)
                for p in c.paragraphs:
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.0
                    for r in p.runs:
                        r.font.name = 'Montserrat Medium'
                        r.font.size = Pt(11)
                        if i == 0:
                            r.bold = True

    # 2. Update Paragraph 107 (ERD description)
    for p in doc.paragraphs:
        if "The entity relationship diagram shows the SQLite database design." in p.text:
            p.text = (
                "The entity relationship diagram shows the SQLite database design. The users table stores login details, "
                "role-based permissions ('admin', 'trainer', 'student'), account creation timestamps and last-login tracking. "
                "The snapshot_policies table holds the snapshot interval, the number of snapshots to keep and whether a pre-session "
                "snapshot is required. The vms table stores each registered machine with its VirtualBox identifier, class group, status, "
                "heartbeat property, failure count, template designation, assigned student identifier and administrator pause lock. "
                "The snapshots table maintains the record of automatic and manual snapshots for each machine, while the backups table stores "
                "independent .ova appliance exports. The vm_requests table tracks student provisioning requests from templates, and the "
                "class_sessions table tracks active and ended class training sessions per group. The events table provides an audit trail "
                "of all system operations, including recovery execution durations. The app_settings table allows administrators to override "
                "configuration parameters at runtime, and the notifications table records email and webhook dispatch attempts. The schema_meta "
                "table records the applied numbered schema migrations (1 through 8), ensuring non-destructive schema evolution. Foreign keys "
                "with cascading rules maintain referential consistency across all entities."
            )
            # Reformat runs
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(10)
            p.paragraph_format.line_spacing = 1.15
            break

print("Helper definitions loaded successfully.")
