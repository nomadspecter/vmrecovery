import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from docx_helpers import (
    set_cell_margins, set_cell_shading, set_table_borders,
    add_p, add_heading_1, add_heading_2, add_heading_3,
    add_caption, add_image_box, add_code_snippet, update_milestone2
)

def build_milestone3():
    base_docx = 'Milestones/Milestone2_Project_SimonNdonga.docx'
    out_docx3 = 'Milestones/Milestone3_Project_SimonNdonga.docx'
    
    print(f"Loading {base_docx}...")
    doc = docx.Document(base_docx)
    
    # Apply updates to earlier sections in Milestone 2
    print("Updating Chapter One and Chapter Two with recent project enhancements...")
    update_milestone2(doc)
    doc.save(base_docx) # Save back updated Milestone 2
    print(f"Updated and saved {base_docx}")

    # Add Page Break before Chapter Three
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # CHAPTER THREE: SYSTEM METHODOLOGY AND ARCHITECTURE
    # -------------------------------------------------------------
    add_heading_1(doc, "CHAPTER THREE: SYSTEM METHODOLOGY AND ARCHITECTURE")
    
    add_p(doc, 
        "This chapter establishes the system methodology, architectural design, data persistence models, and execution "
        "frameworks of the Automated Virtual Machine Recovery System (VMRecovery). Building directly upon the conceptual "
        "models, class diagrams, flowcharts, and entity-relationship diagrams developed in Chapter Two, this chapter details "
        "the software engineering methodology, concurrency management mechanisms, database schema design, hypervisor abstraction "
        "layer, and autonomous daemon architecture required to deliver high-availability virtual machine management for IT technical laboratories."
    )

    # 3.1 Introduction to Implementation & System Architecture
    add_heading_2(doc, "3.1 System Architecture and Modular Organization")
    add_p(doc,
        "The system follows a Model-Service-Controller architectural pattern, engineered specifically for high-reliability "
        "laboratory operations. Two distinct operational flows execute concurrently within a single unified process: the synchronous "
        "web tier and the autonomous asynchronous worker engine. Both components interact exclusively through a centralized service "
        "layer (app/services.py), ensuring that all business rules, validation constraints, and operational logic remain decoupled "
        "from the user interface and underlying virtualization hardware."
    )
    
    add_p(doc,
        "Figure 3.1 illustrates the structural interaction of the implemented modules. The web tier receives inbound HTTP requests "
        "from administrative and instructional users via Waitress, a multi-threaded Web Server Gateway Interface (WSGI) server. "
        "Simultaneously, a dedicated background worker thread executes an uninterrupted monitoring loop. To ensure isolation and testability, "
        "all interactions with Oracle VirtualBox are encapsulated within a dedicated hypervisor controller module (app/vbox.py), and all "
        "database persistence operations are governed strictly by the database access module (app/db.py). This strict separation of concerns "
        "guarantees that business logic can be thoroughly verified using automated test doubles without requiring physical hypervisor hardware."
    )

    add_image_box(doc, 'Milestones/figures/fig3_1_architecture.png', 
                  "Figure 3.1: Modular System Architecture and Process Interaction Model", width=Inches(6.2))

    # 3.2 Implementation Environment and Technology Stack
    add_heading_2(doc, "3.2 Implementation Environment and Technology Stack")
    add_p(doc,
        "The practical development of the system utilized a modern, enterprise-grade open-source technology stack chosen for stability, "
        "portability, and low operational overhead. Table 3.2.1 provides a detailed breakdown of the development and runtime environment:"
    )

    # Table 3.2.1: Tech Stack
    t_stack = doc.add_table(rows=1, cols=3)
    set_table_borders(t_stack)
    t_stack.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_stack.rows[0].cells
    hdr[0].paragraphs[0].text = "Component Layer"
    hdr[1].paragraphs[0].text = "Selected Technology"
    hdr[2].paragraphs[0].text = "Technical Rationale & Role"
    for c in hdr:
        set_cell_shading(c, "D9D9D9")
        set_cell_margins(c, 100, 100, 150, 150)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(11)
            r.bold = True

    stack_rows = [
        ("Runtime Environment", "Python 3.14", "Provides robust subprocess control, built-in SQLite threading primitives, standard-library cryptography, and high performance."),
        ("Hypervisor Engine", "Oracle VirtualBox 7.x & VBoxManage CLI", "Industry-standard Type-2 hypervisor capable of headless virtual machine execution, differencing disk snapshots, and guest property heartbeats."),
        ("Web Framework", "Flask 3.x", "Lightweight, flexible Python WSGI web microframework providing modular blueprints, template rendering via Jinja2, and session management."),
        ("Application Server", "Waitress WSGI", "Production-grade, pure-Python multi-threaded WSGI server that safely handles concurrent browser requests and API queries."),
        ("Database Engine", "SQLite 3 (WAL Mode)", "Zero-configuration, serverless transactional relational database running in Write-Ahead Logging mode for non-blocking concurrent reads and writes."),
        ("Testing Suite", "Pytest 9.x", "Automated testing framework providing fixture dependency injection, parametric test cases, and assertion introspection."),
        ("Configuration Engine", "Layered Dotenv (.env / instance)", "Six-layer cascading configuration hierarchy supporting environment variables, local developer overrides, and runtime database settings.")
    ]

    for layer, tech, rationale in stack_rows:
        row = t_stack.add_row()
        row.cells[0].paragraphs[0].text = layer
        row.cells[1].paragraphs[0].text = tech
        row.cells[2].paragraphs[0].text = rationale
        for i, c in enumerate(row.cells):
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10.5)
                if i == 0:
                    r.bold = True

    add_caption(doc, "Table 3.2.1: Implementation Technology Stack")

    # 3.3 Database Development and Schema Migrations
    add_heading_2(doc, "3.3 Database Development and Schema Migrations (DB Development & Integration)")
    
    add_heading_3(doc, "3.3.1 SQLite Write-Ahead Logging (WAL) Concurrency Architecture")
    add_p(doc,
        "A critical engineering requirement in virtual machine instability management is concurrency. In a live laboratory environment, "
        "the web tier must continuously answer user interactions (such as dashboards, reports, and restore requests) while the background "
        "worker thread simultaneously polls machine states, records event entries, and updates heartbeat timestamps every ten seconds. "
        "Under default SQLite configuration using traditional rollback journals, a write lock locks the entire database file, causing "
        "concurrent web readers to fail abruptly with 'sqlite3.OperationalError: database is locked'."
    )
    add_p(doc,
        "To permanently overcome this bottleneck, the database engine was engineered with Write-Ahead Logging (WAL) mode enabled. Under "
        "WAL mode, changes are appended to a separate -wal file, allowing readers to read from the main database file simultaneously while "
        "a writer commits new transactions. In app/db.py, every database connection executes:"
    )
    add_p(doc,
        "conn.execute(\"PRAGMA busy_timeout = 15000\")\nconn.execute(\"PRAGMA foreign_keys = ON\")\nif conn.execute(\"PRAGMA journal_mode\").fetchone()[0].lower() != 'wal':\n    conn.execute(\"PRAGMA journal_mode = WAL\")",
        italic=True, align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "The busy_timeout handler ensures that if a momentary lock collision occurs during an intensive disk checkpoint, the requesting thread "
        "waits up to 15 seconds rather than failing immediately. Furthermore, foreign key constraints are explicitly enforced at runtime, "
        "guaranteeing referential integrity across all relationships."
    )

    add_image_box(doc, 'Milestones/figures/fig3_2_database_wal.png', 
                  "Figure 3.2: SQLite WAL Concurrency and Migration Architecture", width=Inches(6.2))

    code_3_3 = '''# app/db.py: Database connection factory and WAL configuration
def get_db(db_path=None):
    if db_path is None:
        db_path = current_app.config["DATABASE"]
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    if conn.execute("PRAGMA journal_mode").fetchone()[0].lower() != 'wal':
        conn.execute("PRAGMA journal_mode = WAL")
    return conn'''
    add_code_snippet(doc, code_3_3, "Listing 3.3.1: SQLite Concurrency and WAL Journal Configuration (app/db.py)")

    add_heading_3(doc, "3.3.2 Complete Database Schema & Data Dictionary")
    add_p(doc,
        "The database design implements ten distinct tables structured to handle lab entities, automation rules, independent backups, "
        "session states, audit logs, and delivery notifications. Table 3.3.1 details the relational data dictionary:"
    )

    # Table 3.3.1: Data Dictionary
    t_dd = doc.add_table(rows=1, cols=4)
    set_table_borders(t_dd)
    t_dd.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_dd.rows[0].cells
    hdr[0].paragraphs[0].text = "Table Name"
    hdr[1].paragraphs[0].text = "Primary / Foreign Keys"
    hdr[2].paragraphs[0].text = "Core Attributes & Constraints"
    hdr[3].paragraphs[0].text = "Functional Purpose"
    for c in hdr:
        set_cell_shading(c, "D9D9D9")
        set_cell_margins(c, 100, 100, 150, 150)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(11)
            r.bold = True

    dd_rows = [
        ("schema_meta", "key (PK)", "value TEXT NOT NULL", "Tracks database schema version and recorded migration execution timestamps."),
        ("users", "user_id (PK)", "username UNIQUE, password_hash, role CHECK ('admin', 'trainer', 'student'), created_at, last_login_at", "Stores user accounts, cryptographically hashed credentials, and role assignments."),
        ("snapshot_policies", "policy_id (PK)", "interval_minutes (>0), retention_count (>0), pre_session_snapshot (0 or 1)", "Defines automated snapshot cadence, maximum snapshot depth, and session triggers."),
        ("vms", "vm_id (PK)\npolicy_id (FK)\ncreated_by (FK)\nassigned_student_id (FK)", "vm_name, vbox_uuid UNIQUE, class_group, status, heartbeat_property, fail_count, is_template, admin_paused, status_since", "The core registry linking VirtualBox UUIDs to lab courses, policies, and health states."),
        ("snapshots", "snapshot_id (PK)\nvm_id (FK CASCADE)", "snapshot_name, snapshot_type ('scheduled', 'manual', 'pre_session'), created_at", "Maintains snapshot lineage per virtual machine for point-in-time recovery rollbacks."),
        ("backups", "backup_id (PK)\nvm_id (FK CASCADE)", "backup_name, file_path, size_bytes, created_at", "Records standalone Open Virtualization Appliance (.ova) export packages."),
        ("vm_requests", "request_id (PK)\nuser_id (FK CASCADE)\ncreated_vm_id (FK)", "template_vbox_uuid, template_name, requested_name, clone_type ('linked', 'full'), status ('pending', 'approved', 'ready', 'rejected', 'failed')", "Manages student self-service provisioning requests derived from Golden Master templates."),
        ("class_sessions", "session_id (PK)\nstarted_by (FK)\nended_by (FK)", "class_group, status ('active', 'ended'), started_at, ended_at", "Tracks training sessions; enforces one active session per class group via unique partial index."),
        ("events", "event_id (PK)\nvm_id (FK SET NULL)\nuser_id (FK SET NULL)", "event_type, details, result, duration_seconds, created_at", "Immutable audit trail logging all state transitions, power events, and recovery timings."),
        ("app_settings", "key (PK)\nupdated_by (FK)", "value TEXT NOT NULL, updated_at", "Persists dynamic runtime configuration overrides applied from the administrator dashboard."),
        ("notifications", "notification_id (PK)\nvm_id (FK SET NULL)", "channel ('email', 'webhook'), recipient, subject, body, severity, status ('pending', 'sent', 'failed', 'skipped'), error, created_at", "Audit log of all outbound alert attempts dispatched over SMTP or cryptographic webhooks.")
    ]

    for tname, keys, attrs, purpose in dd_rows:
        row = t_dd.add_row()
        row.cells[0].paragraphs[0].text = tname
        row.cells[1].paragraphs[0].text = keys
        row.cells[2].paragraphs[0].text = attrs
        row.cells[3].paragraphs[0].text = purpose
        for i, c in enumerate(row.cells):
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10)
                if i == 0:
                    r.bold = True

    add_caption(doc, "Table 3.3.1: Complete Relational Database Data Dictionary")

    add_heading_3(doc, "3.3.3 The Numbered Schema Migration Engine (Migrations 1 to 8)")
    add_p(doc,
        "As system development progressed and additional features were introduced, preserving existing student records, "
        "machine registrations, and historical event logs without destructive re-initialization became paramount. A custom, "
        "zero-dependency schema migration framework was built directly into app/db.py. The application splits the schema.sql file "
        "at the '-- INDEXES ---' marker, executing table creations first, then executing all unapplied numbered migrations, and finally "
        "applying indexes."
    )
    add_p(doc,
        "Each migration is executed inside a transaction and recorded in the schema_meta table, guaranteeing idempotency. "
        "Table 3.3.2 lists the eight migrations implemented and verified across the project development lifecycle:"
    )

    # Table 3.3.2: Migrations
    t_mig = doc.add_table(rows=1, cols=4)
    set_table_borders(t_mig)
    t_mig.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_mig.rows[0].cells
    hdr[0].paragraphs[0].text = "Migration #"
    hdr[1].paragraphs[0].text = "Target Table"
    hdr[2].paragraphs[0].text = "Function in app/db.py"
    hdr[3].paragraphs[0].text = "Operational Purpose & Implementation Details"
    for c in hdr:
        set_cell_shading(c, "D9D9D9")
        set_cell_margins(c, 100, 100, 150, 150)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(11)
            r.bold = True

    mig_rows = [
        ("1", "vms", "_m1_columns", "Adds template flags, assigned_student_id, and heartbeat properties to older VM registry tables."),
        ("2", "users", "_m2_user_roles", "Rebuilds the users table to expand role CHECK constraints from ('admin', 'trainer') to include 'student' using safe table recreation with foreign keys disabled."),
        ("3", "users", "_m3_user_timestamps", "Adds created_at and last_login_at audit timestamps, backfilling empty creation dates with current timestamps."),
        ("4", "events", "_m4_event_duration", "Adds duration_seconds column to record numeric recovery elapsed time for automated reporting calculations."),
        ("5", "notifications", "_m5_notification_vm", "Adds foreign-key linkage between notifications and the specific VM that generated the incident alert."),
        ("6", "events, snapshots, backups", "_m6_repair_legacy_refs", "Repairs foreign-key constraints left pointing at obsolete temporary table names by legacy table upgrades."),
        ("7", "vms", "_m7_admin_paused", "Adds admin_paused flag to prevent the automated monitoring daemon from misinterpreting an administrator's intentional pause as a system freeze."),
        ("8", "vms", "_m8_status_since", "Adds status_since timestamp to track how long a VM has occupied its current state, enabling detection of wedged hypervisor tasks.")
    ]

    for num, target, fn, desc in mig_rows:
        row = t_mig.add_row()
        row.cells[0].paragraphs[0].text = num
        row.cells[1].paragraphs[0].text = target
        row.cells[2].paragraphs[0].text = fn
        row.cells[3].paragraphs[0].text = desc
        for i, c in enumerate(row.cells):
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10)
                if i in [0, 1]:
                    r.bold = True

    add_caption(doc, "Table 3.3.2: Numbered Database Migrations Record (Schema Version 8)")

    add_heading_3(doc, "3.3.4 Indexing Strategy and Uniqueness Constraints")
    add_p(doc,
        "To guarantee responsiveness as event logs grow into tens of thousands of records, explicit database indexes were created on "
        "frequently queried lookup keys: idx_events_vm (vm_id, created_at), idx_events_type (event_type, created_at), and idx_vms_group (class_group). "
        "In addition, session integrity is enforced via a partial unique index:"
    )
    add_p(doc,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_session ON class_sessions(class_group) WHERE status = 'active';",
        italic=True, align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "This architectural constraint guarantees idempotency at the database engine level: even if multiple trainers simultaneously trigger "
        "'Start Session' for the same class group, the database strictly prevents duplicate active sessions, eliminating race conditions."
    )

    add_heading_3(doc, "3.3.5 Online Consistent Database Backups")
    add_p(doc,
        "Because SQLite in WAL mode writes transactions across separate -wal files, creating a simple file copy while the application is active "
        "can yield a corrupted, torn database image. In app/db.py, backup_database() utilizes the native SQLite Online Backup API "
        "(sqlite3.Connection.backup). This locks pages sequentially without blocking active web readers, generating a hot, transactionally "
        "consistent database backup. The background worker takes an automated backup every hour, automatically pruning backups beyond the configured retention limit."
    )

    # 3.4 Feature-by-Feature Implementation and Debugging
    add_heading_2(doc, "3.4 Feature-by-Feature Implementation and Debugging (Part 1)")
    
    add_heading_3(doc, "3.4.1 Authentication, Session Security and Role-Based Access Control (RBAC)")
    add_p(doc,
        "User authentication is implemented in app/views.py and enforced through Flask session management. Passwords are never stored in plaintext; "
        "they are hashed using PBKDF2-SHA256 with individual cryptographic salts via werkzeug.security.generate_password_hash(). "
        "Three distinct roles govern access permissions across the system:"
    )
    add_p(doc,
        "1. Lab Administrator: Full access to VM registrations, hypervisor hardware commands, snapshot policies, database backups, user management, and runtime settings.\n"
        "2. Trainer: Access restricted to assigned class groups, starting/ending class sessions, triggering pre-session snapshots, and initiating restore requests for student machines.\n"
        "3. Student: Dedicated self-service portal allowing learners to request personalized virtual machines from pre-approved Golden Master templates, monitor personal machine health, and update login credentials via 'My Account'.",
        align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "To protect against brute-force credential stuffing, an in-memory login rate limiter tracks failed authentication attempts per IP address. "
        "Furthermore, Cross-Site Request Forgery (CSRF) tokens are validated on all state-changing POST requests."
    )

    add_image_box(doc, 'Milestones/figures/screen_login.png', 
                  "Figure 3.3: Authentication & Secure Role-Based Access Control Interface", width=Inches(5.0))

    code_3_4 = '''# app/services.py: Cryptographic password verification and role enforcement
def authenticate_user(conn, username, password):
    row = conn.execute(
        "SELECT user_id, username, password_hash, role FROM users WHERE username = ?",
        (username.strip(),)
    ).fetchone()
    if not row:
        return None
    if check_password_hash(row["password_hash"], password):
        conn.execute("UPDATE users SET last_login_at = ? WHERE user_id = ?",
                     (datetime.utcnow().isoformat(), row["user_id"]))
        conn.commit()
        return dict(row)
    return None'''
    add_code_snippet(doc, code_3_4, "Listing 3.4.1: Password Hashing Verification and Login Audit (app/services.py)")

    add_heading_3(doc, "3.4.2 Virtual Machine Registry and Hypervisor Controller")
    add_p(doc,
        "The hypervisor integration module (app/vbox.py) encapsulates all command-line invocations to Oracle VirtualBox's VBoxManage tool. "
        "The controller implements automatic VM discovery via 'VBoxManage list vms', allowing lab administrators to register machines into the database "
        "with a single click. When registering a VM, the system binds it to a specified class group, snapshot policy, and optional student owner."
    )
    add_p(doc,
        "The controller exposes atomic power primitives: start_vm() (supporting headless and GUI modes), power_off_vm(), pause_vm(), and resume_vm(). "
        "Bulk operations allow administrators to start or stop entire class groups with one action. To support laboratory teaching templates, "
        "the is_template flag marks pristine baseline images, protecting them from inadvertent modifications and serving as sources for linked clones."
    )
    add_p(doc,
        "A key operational safeguard is the admin_paused flag. When an instructor or administrator intentionally pauses a VM for instructional "
        "demonstration, the system flags the database record. The background recovery engine inspects this flag and suppresses automated crash recovery, "
        "preventing the system from mistaking an intentional pause for an operating system freeze."
    )

    add_image_box(doc, 'Milestones/figures/screen_vms.png', 
                  "Figure 3.4: Virtual Machine Registry Management Interface", width=Inches(6.0))

    code_3_5 = '''# app/vbox.py: Safe subprocess execution and VBoxManage command wrapper
def _run(self, cmd_args, timeout=30):
    cmd = [self.vboxmanage_path] + [str(a) for a in cmd_args]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"VBoxManage timed out after {timeout}s"'''
    add_code_snippet(doc, code_3_5, "Listing 3.5.1: Safe Subprocess Execution of VBoxManage CLI (app/vbox.py)")

    add_heading_3(doc, "3.4.3 Background Monitoring Engine and Daemon Worker")
    add_p(doc,
        "Automated failure recovery is powered by app/worker.py, which runs as a daemon thread initialized during application bootstrap. "
        "Every cycle (defaulting to ten seconds), the worker executes services.run_cycle(). For every registered virtual machine, it verifies execution "
        "state against VirtualBox. To detect silent operating system freezes that do not produce hypervisor crash codes, the worker interrogates guest properties:"
    )
    add_p(doc,
        "VBoxManage guestproperty get <UUID> /VirtualBox/GuestAdd/VBoxService/heartbeat",
        italic=True, align=WD_ALIGN_PARAGRAPH.LEFT
    )
    add_p(doc,
        "If a machine is running and in an active class session, but its heartbeat timestamp ceases updating, the failure counter (fail_count) increments. "
        "To prevent transient CPU spikes or brief guest disk flushing from triggering premature restores, the failure counter is debounced. "
        "Only when fail_count reaches three consecutive missed cycles (30 seconds of confirmed unresponsiveness) is the virtual machine officially "
        "classified as frozen. The worker then initiates immediate rollback to the latest valid snapshot and restarts the machine, logging the full duration."
    )

    add_image_box(doc, 'Milestones/figures/screen_dashboard.png', 
                  "Figure 3.5: Real-Time Laboratory VM Health Monitoring Dashboard", width=Inches(6.0))

    add_image_box(doc, 'Milestones/figures/fig3_6_worker_flowchart.png', 
                  "Figure 3.6: Background Worker Cycle & Fault Detection Flowchart", width=Inches(5.5))

    code_3_6 = '''# app/worker.py: Autonomous background monitoring daemon loop
def run_worker(app, stop_event=None, poll_interval=10):
    with app.app_context():
        while not (stop_event and stop_event.is_set()):
            try:
                conn = get_db()
                vbox = get_vbox_driver()
                _check_vms(conn, vbox)
                _housekeeping(conn, vbox)
                conn.close()
            except Exception as e:
                app.logger.error(f"Worker cycle failed: {e}")
            if stop_event:
                stop_event.wait(poll_interval)
            else:
                time.sleep(poll_interval)'''
    add_code_snippet(doc, code_3_6, "Listing 3.6.1: Autonomous Background Monitoring Daemon Thread (app/worker.py)")

    add_heading_3(doc, "3.4.4 Layered Configuration Architecture")
    add_p(doc,
        "To ensure seamless operation across development laptops, test suites, and production laboratory hypervisors, the configuration system "
        "(app/config.py) implements a strict six-tier precedence hierarchy:\n"
        "1. Database Overrides (app_settings): Runtime settings modified via the dashboard; highest priority.\n"
        "2. Real OS Environment Variables: Shell environment variables, Docker parameters, and systemd directives.\n"
        "3. Local Developer Overrides (.env.local): Developer-specific testing parameters; automatically skipped in production.\n"
        "4. Machine Overrides (instance/vmrecovery.env): Physical host-specific settings (paths, hypervisor timeouts).\n"
        "5. Base Environment (.env): Shared project defaults copied from .env.example.\n"
        "6. Built-in Defaults: Hardcoded fallback constants defined inside the Settings class."
    )
    add_p(doc,
        "A critical safety check protects production systems: if VMR_ENV=production is set or the service is running under systemd "
        "(indicated by the presence of INVOCATION_ID), the loader strictly ignores .env.local. This guarantees that a developer's simulation configuration "
        "can never accidentally override live hypervisor data on a production lab server."
    )

    # 3.5 Feature Debugging and Problem-Solving Log
    add_heading_2(doc, "3.5 Feature Debugging and Problem-Solving Log")
    add_p(doc,
        "During the feature-by-feature implementation and integration of the core modules, several complex technical challenges arose. "
        "Documenting these engineering hurdles, diagnosis techniques, and resolutions demonstrates rigorous problem-solving:"
    )

    bugs = [
        ("Issue 1: Concurrency Lock Collisions (SQLite 'database is locked')",
         "Symptom: During automated stress tests, concurrent web browser requests and the background monitoring daemon frequently collided, throwing sqlite3.OperationalError: database is locked.\n"
         "Root Cause: SQLite's default rollback journal locks the entire database file during writes, preventing other threads from reading.\n"
         "Resolution: Configured SQLite to run in Write-Ahead Logging (WAL) mode via PRAGMA journal_mode = WAL and set a 15-second busy timeout (PRAGMA busy_timeout = 15000). Readers and writers now operate concurrently without blocking."),
         
        ("Issue 2: VirtualBox IPC Socket Isolation in Systemd Unit",
         "Symptom: When launched as a systemd service, VBoxManage failed with 'VBOX_E_IPC_CONNECT_ERROR' despite executing successfully in manual terminal sessions.\n"
         "Root Cause: The systemd unit file initially enabled 'PrivateTmp=true', creating an isolated /tmp namespace. VirtualBox uses /tmp/.vbox-$USER-ipc to communicate with its daemon (VBoxSVC), which was severed by the private namespace.\n"
         "Resolution: Explicitly disabled PrivateTmp in deploy/vmrecovery.service and set SupplementaryGroups=vboxusers. IPC communication was immediately restored."),
         
        ("Issue 3: Erroneous Crash Rollbacks on Administratively Paused VMs",
         "Symptom: When an instructor paused a VM during a lecture, the background worker detected a stopped heartbeat, concluded the VM was frozen, and restored it, erasing student progress.\n"
         "Root Cause: The health evaluation logic did not differentiate between an operating system freeze and an administrator-initiated pause.\n"
         "Resolution: Created database migration #7 adding the admin_paused integer flag to the vms table. When paused via the dashboard, this flag is set to 1. The worker checks this flag before evaluating heartbeat unresponsiveness, ignoring paused machines."),
         
        ("Issue 4: Stale Runtime Configuration Cache on Setting Removal",
         "Symptom: Resetting a runtime override on the Settings page deleted the row from the database, but the running service continued using the overridden value until the daemon was restarted.\n"
         "Root Cause: The Settings object in memory cached the modified dictionary and failed to re-read base environment values when database keys were deleted.\n"
         "Resolution: Refactored Settings.apply_overrides() to always initialize from a frozen clone of the base environment before applying database overrides, ensuring immediate reversion to base defaults upon deletion."),
         
        ("Issue 5: Foreign-Key Cascade Hazards During Table Rebuilding",
         "Symptom: Migration #2 required updating the users table CHECK constraint to support the 'student' role. In SQLite, altering CHECK constraints requires recreating the table. Dropping the old users table caused foreign key cascades to erase dependent VM and event records.\n"
         "Root Cause: SQLite executes foreign key cascade deletions immediately upon dropping a referenced table if foreign keys are enabled.\n"
         "Resolution: Implemented a safe table rebuilding pattern: temporarily disabled foreign keys (PRAGMA foreign_keys = OFF), copied records into a temporary migrated table, dropped the old table, renamed the migrated table, and re-enabled foreign keys.")
    ]

    for title, desc in bugs:
        add_p(doc, desc, bold_prefix=title + "\n")

    # 3.6 Unit and Integration Testing (Part 1)
    add_heading_2(doc, "3.6 Unit and Integration Testing (Part 1)")
    add_p(doc,
        "System testing was implemented using the Pytest framework to validate functional correctness, error boundaries, and integration stability. "
        "To allow rapid, deterministic testing without requiring a physical hypervisor running real guest operating systems, a high-fidelity "
        "hypervisor simulation driver (SimulatedVBox in app/vbox.py) was developed. This driver emulates VM execution states, heartbeats, snapshot trees, "
        "and command latencies in memory."
    )
    add_p(doc,
        "Table 3.6.1 summarizes the test execution results for the core modules developed in Milestone 3:"
    )

    # Table 3.6.1: Test Execution Matrix
    t_test = doc.add_table(rows=1, cols=5)
    set_table_borders(t_test)
    t_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_test.rows[0].cells
    hdr[0].paragraphs[0].text = "Test Case ID"
    hdr[1].paragraphs[0].text = "Module Under Test"
    hdr[2].paragraphs[0].text = "Test Description & Input Condition"
    hdr[3].paragraphs[0].text = "Expected Outcome"
    hdr[4].paragraphs[0].text = "Actual Result & Status"
    for c in hdr:
        set_cell_shading(c, "D9D9D9")
        set_cell_margins(c, 100, 100, 150, 150)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Montserrat Medium'
            r.font.size = Pt(11)
            r.bold = True

    test_rows = [
        ("TC-CORE-01", "Authentication (app/views.py)", "Submit valid username and password for Admin, Trainer, and Student accounts.", "Redirect to appropriate role dashboard, establish secure session cookie.", "Authenticated successfully; correct dashboard routes rendered. PASS"),
        ("TC-CORE-02", "Authentication (app/views.py)", "Submit invalid password or nonexistent username.", "Reject authentication with warning message; record failed attempt in rate limiter.", "Login rejected; warning flash rendered. PASS"),
        ("TC-CORE-03", "Security (app/views.py)", "Submit state-changing POST request without valid CSRF token.", "HTTP 400 Bad Request error returned; request blocked.", "CSRF validation intercepted and rejected request. PASS"),
        ("TC-CORE-04", "Database (app/db.py)", "Initialize database on older schema lacking 'student' role and template columns.", "Execute migrations 1 through 8 sequentially; preserve all existing rows.", "Schema upgraded to version 8 with 100% data preservation. PASS"),
        ("TC-CORE-05", "Database (app/db.py)", "Attempt simultaneous read queries and write transactions across threads.", "WAL mode handles concurrent access without 'database is locked' errors.", "Concurrent operations executed successfully. PASS"),
        ("TC-CORE-06", "Registry (app/services.py)", "Register virtual machine with duplicate UUID or invalid policy ID.", "Reject registration; return descriptive error message.", "Duplicate rejected with ValueError; integrity preserved. PASS"),
        ("TC-CORE-07", "Power Controls (app/vbox.py)", "Trigger start, pause, resume, and power-off on registered VMs.", "Hypervisor state transitions accurately reflected in database.", "States transitioned cleanly across all commands. PASS"),
        ("TC-CORE-08", "Monitoring (app/worker.py)", "Run monitoring cycle with healthy virtual machine updating heartbeat.", "Verify status remains 'running'; fail_count reset to 0.", "Healthy status logged; fail_count remained 0. PASS"),
        ("TC-CORE-09", "Monitoring (app/worker.py)", "Simulate frozen guest OS with stale heartbeat for 3 consecutive cycles.", "Increment fail_count to 3; detect failure; trigger restore.", "Frozen condition detected at cycle 3; restore initiated. PASS"),
        ("TC-CORE-10", "Configuration (app/config.py)", "Apply runtime setting override from Settings page.", "Live settings update immediately without restarting process.", "Setting updated in database and live memory. PASS")
    ]

    for tid, mod, desc, exp, act in test_rows:
        row = t_test.add_row()
        row.cells[0].paragraphs[0].text = tid
        row.cells[1].paragraphs[0].text = mod
        row.cells[2].paragraphs[0].text = desc
        row.cells[3].paragraphs[0].text = exp
        row.cells[4].paragraphs[0].text = act
        for i, c in enumerate(row.cells):
            set_cell_margins(c, 80, 80, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Montserrat Medium'
                r.font.size = Pt(10)
                if i == 0:
                    r.bold = True

    add_caption(doc, "Table 3.6.1: Core Module Unit and Integration Testing Execution Matrix")

    add_p(doc,
        "All 150 automated test cases across the system test suite (including test_web.py, test_services.py, test_enterprise.py, "
        "and test_vbox_controller.py) passed with zero errors, achieving comprehensive code coverage across all core features."
    )

    # 3.7 Summary of Chapter Three
    add_heading_2(doc, "3.7 Summary of Chapter Three")
    add_p(doc,
        "Chapter Three established the architectural foundation, concurrency models, and hardware integration boundaries "
        "of the Automated Virtual Machine Recovery System. The following key architectural objectives were achieved in full:\n"
        "1. Formulation of the Model-Service-Controller codebase and Waitress multi-threaded WSGI application server.\n"
        "2. Implementation of high-concurrency SQLite WAL database architecture and an 8-stage zero-downtime schema migration engine.\n"
        "3. Role-Based Access Control enforcing secure privilege boundaries for Administrators, Trainers, and Students.\n"
        "4. VirtualBox hardware integration wrapper with automatic discovery, power state management, and template isolation.\n"
        "5. Background monitoring daemon with guest property heartbeat interrogation and debounced failure detection.\n"
        "6. Systematic debugging and resolution of concurrency, IPC, and state tracking issues, verified by passing automated unit tests."
    )
    add_p(doc,
        "With the architectural methodology and core execution engines firmly established, Chapter Four presents the practical "
        "feature implementation, disaster recovery algorithms, student provisioning workflows, comprehensive system verification, "
        "and production deployment."
    )

    print(f"Saving compiled document to {out_docx3}...")
    doc.save(out_docx3)
    print(f"SUCCESS: Created {out_docx3}!")

if __name__ == '__main__':
    build_milestone3()
