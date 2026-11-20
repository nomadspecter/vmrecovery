import os
import pygments
from pygments.lexers import PythonLexer, BashLexer, IniLexer
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

os.makedirs('Milestones/figures', exist_ok=True)

def render_vscode_screenshot(page, code_text, filepath, start_line=1, lexer=PythonLexer(), out_png=''):
    lines = code_text.strip().split('\n')
    line_nums_html = '<br>'.join(str(start_line + i) for i in range(len(lines)))
    
    formatter = HtmlFormatter(nowrap=True)
    highlighted_code = pygments.highlight(code_text.strip(), lexer, formatter)
    
    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath) or 'vmrecovery'
    
    # Choose file icon
    if filename.endswith('.py'):
        icon = '🐍'
        lang_label = 'Python 3.14.1'
    elif filename.endswith('.sh'):
        icon = '🐚'
        lang_label = 'Bash / Shell'
    elif filename.endswith('.service'):
        icon = '⚙️'
        lang_label = 'systemd unit'
    elif filename.endswith('.sql'):
        icon = '🗄️'
        lang_label = 'SQL'
    else:
        icon = '📄'
        lang_label = 'Plain Text'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 20px;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: inline-block;
  }}
  .vscode-window {{
    width: 960px;
    background: #1E1E1E;
    border-radius: 10px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.12);
    overflow: hidden;
    font-family: 'Consolas', 'Fira Code', 'DejaVu Sans Mono', 'Courier New', monospace;
  }}
  .title-bar {{
    background: #2D2D2D;
    height: 38px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    user-select: none;
    border-bottom: 1px solid #181818;
  }}
  .traffic-lights {{
    display: flex;
    gap: 8px;
    margin-right: 18px;
  }}
  .traffic-light {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .tl-red {{ background: #FF5F56; border: 1px solid #E0443E; }}
  .tl-yellow {{ background: #FFBD2E; border: 1px solid #DEA123; }}
  .tl-green {{ background: #27C93F; border: 1px solid #1AAB29; }}
  .title-text {{
    flex: 1;
    text-align: center;
    color: #CCCCCC;
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    letter-spacing: 0.3px;
  }}
  .tabs-bar {{
    background: #252526;
    display: flex;
    height: 36px;
    align-items: flex-end;
    border-bottom: 1px solid #1E1E1E;
  }}
  .tab {{
    background: #1E1E1E;
    color: #FFFFFF;
    padding: 0 18px;
    height: 36px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-top: 2px solid #007ACC;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  .tab-icon {{
    font-size: 14px;
  }}
  .breadcrumbs {{
    background: #1E1E1E;
    color: #8C8C8C;
    font-size: 12px;
    padding: 6px 18px;
    border-bottom: 1px solid #282828;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  .editor-content {{
    display: flex;
    padding: 14px 0 18px 0;
    font-size: 13.5px;
    line-height: 1.55;
    background: #1E1E1E;
  }}
  .gutter {{
    padding: 0 16px 0 14px;
    color: #6E7681;
    text-align: right;
    user-select: none;
    border-right: 1px solid #2D2D2D;
    font-family: 'Consolas', 'DejaVu Sans Mono', monospace;
    font-size: 13px;
    line-height: 1.55;
    min-width: 45px;
  }}
  .code-area {{
    padding: 0 20px;
    flex: 1;
    color: #D4D4D4;
    white-space: pre;
    font-family: 'Consolas', 'DejaVu Sans Mono', 'Fira Code', monospace;
    font-size: 13.5px;
    line-height: 1.55;
  }}
  /* VS Code Dark+ Colors */
  .c, .c1, .ch, .cm, .cs {{ color: #6A9955; font-style: italic; }} /* comments */
  .k, .kd, .kn, .kp, .kr {{ color: #C586C0; }} /* keywords */
  .ow {{ color: #569CD6; }}
  .nb, .bp {{ color: #569CD6; }} /* builtins */
  .nf, .fm {{ color: #DCDCAA; font-weight: 600; }} /* functions */
  .nc, .nn {{ color: #4EC9B0; font-weight: 600; }} /* classes/modules */
  .s, .s1, .s2, .sa, .sb, .sc, .sd, .se, .sh, .si, .sx, .sr, .ss {{ color: #CE9178; }} /* strings */
  .m, .mi, .mf, .mh, .mo, .il {{ color: #B5CEA8; }} /* numbers */
  .o {{ color: #D4D4D4; }} /* operators */
  .nd {{ color: #DCDCAA; }} /* decorators */
  .na {{ color: #9CDCFE; }} /* attribute / ini key */
  .nv {{ color: #9CDCFE; }} /* variable */
  .status-bar {{
    background: #007ACC;
    color: #FFFFFF;
    font-size: 11.5px;
    padding: 4px 16px;
    display: flex;
    justify-content: space-between;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  .status-left, .status-right {{
    display: flex;
    gap: 16px;
  }}
</style>
</head>
<body>
  <div class="vscode-window">
    <div class="title-bar">
      <div class="traffic-lights">
        <div class="traffic-light tl-red"></div>
        <div class="traffic-light tl-yellow"></div>
        <div class="traffic-light tl-green"></div>
      </div>
      <div class="title-text">{filename} — vmrecovery [Visual Studio Code]</div>
    </div>
    <div class="tabs-bar">
      <div class="tab">
        <span class="tab-icon">{icon}</span>
        <span>{filename}</span>
      </div>
    </div>
    <div class="breadcrumbs">
      vmrecovery &gt; {folder} &gt; {filename}
    </div>
    <div class="editor-content">
      <div class="gutter">{line_nums_html}</div>
      <div class="code-area">{highlighted_code}</div>
    </div>
    <div class="status-bar">
      <div class="status-left">
        <span>⎇ main*</span>
        <span>⊗ 0  ⚠ 0</span>
      </div>
      <div class="status-right">
        <span>Ln {start_line}, Col 1</span>
        <span>Spaces: 4</span>
        <span>UTF-8</span>
        <span>{lang_label}</span>
      </div>
    </div>
  </div>
</body>
</html>'''

    page.set_content(html)
    window_elem = page.query_selector('.vscode-window')
    window_elem.screenshot(path=out_png)
    print(f"  -> Generated VS Code screenshot: {out_png}")


def generate_all_snippets():
    print("Initializing Playwright to capture VS Code code screenshots...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        
        # 1. Listing 3.3.1: SQLite Concurrency and WAL Journal Configuration
        code_3_3 = '''def connect(path: str):
    """Open a connection to the application database (SQLite or PostgreSQL)."""
    if is_postgres_url(path):
        return connect_pg(path)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    if conn.execute("PRAGMA journal_mode").fetchone()[0].lower() != "wal":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn'''
        render_vscode_screenshot(page, code_3_3, 'app/db.py', start_line=28, 
                                 out_png='Milestones/figures/code_3_3_db_wal.png')

        # 2. Listing 3.4.1: Password Hashing Verification and Login Audit
        code_3_4 = '''@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr or "?"
        now = time.time()
        # Rate limiting: debounce repeated brute-force attempts
        if len(_failed_logins[ip]) >= settings().login_max_failures:
            flash_error("Too many failed attempts. Wait a few minutes and try again.")
            return render_template("login.html"), 429
            
        row = get_db().execute("SELECT * FROM users WHERE username=?",
                               (request.form.get("username", "").strip(),)).fetchone()
        if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = row["user_id"]
            session["csrf"] = secrets.token_hex(16)
            session.permanent = True
            get_db().execute("UPDATE users SET last_login_at=? WHERE user_id=?",
                             (services.ts(services.now_local()), row["user_id"]))
            get_db().commit()
            return redirect(url_for("main.dashboard"))'''
        render_vscode_screenshot(page, code_3_4, 'app/views.py', start_line=156, 
                                 out_png='Milestones/figures/code_3_4_auth.png')

        # 3. Listing 3.5.1: Safe Subprocess Execution of VBoxManage CLI
        code_3_5 = '''def _run(self, *args: str, check: bool = True, timeout: float | None = None) -> str:
    """Safe command execution wrapper around Oracle VirtualBox VBoxManage CLI."""
    log.debug("VBoxManage %s", " ".join(args))
    try:
        proc = subprocess.run([self.exe, *args], capture_output=True, text=True,
                              timeout=timeout or self.timeout)
    except FileNotFoundError:
        raise VBoxError(f"VBoxManage not found ('{self.exe}'). Is VirtualBox installed?")
    except subprocess.TimeoutExpired:
        raise VBoxError(f"VBoxManage timed out: {' '.join(args[:3])}")
    if check and proc.returncode != 0:
        raise VBoxError(self._error_message(proc))
    return proc.stdout'''
        render_vscode_screenshot(page, code_3_5, 'app/vbox.py', start_line=65, 
                                 out_png='Milestones/figures/code_3_5_vbox.png')

        # 4. Listing 3.6.1: Autonomous Background Monitoring Daemon Thread
        code_3_6 = '''def run(self):
    """Uninterrupted background monitoring thread loop executing every check_seconds."""
    self.started_at = services.ts(services.now_local())
    log.info("Worker started (every %ss)", self.settings.check_seconds)
    while not self._stop_event.is_set():
        try:
            conn = db.connect(self.settings.db_path)
            try:
                summary = services.run_cycle(conn, self.vbox, self.settings, lock=self.lock)
                self._housekeeping(conn)
            finally:
                conn.close()
            self.last_cycle = services.ts(services.now_local())
            self.last_summary = summary
            self.cycles += 1
        except Exception as exc:
            self.last_error = str(exc) or exc.__class__.__name__
            log.exception("Worker cycle failed")
        self._stop_event.wait(self.settings.check_seconds)'''
        render_vscode_screenshot(page, code_3_6, 'app/worker.py', start_line=44, 
                                 out_png='Milestones/figures/code_3_6_worker.png')

        # 5. Listing 4.1.1: Snapshot Due Verification and Retention Pruning Algorithm
        code_4_1 = '''def due_for_snapshot(conn, vm, now) -> bool:
    """Check if the VM is overdue for an interval snapshot."""
    last = conn.execute("SELECT MAX(created_at) AS t FROM snapshots WHERE vm_id=?",
                        (vm["vm_id"],)).fetchone()["t"]
    return last is None or now - parse_ts(last) >= timedelta(minutes=vm["interval_minutes"])

def apply_retention(conn, vbox, vm, now):
    """Enforce retention policy: prune oldest snapshots exceeding retention_count."""
    rows = list_snapshots(conn, vm["vm_id"])
    if not rows[vm["retention_count"]:]:
        return
    vbox.wait_until_ready(vm["vbox_uuid"])
    for old in rows[vm["retention_count"]:]:
        try:
            vbox.delete_snapshot(vm["vbox_uuid"], old["snapshot_name"])
            conn.execute("DELETE FROM snapshots WHERE snapshot_id=?", (old["snapshot_id"],))
            conn.commit()
        except VBoxError as exc:
            log_event(conn, "snapshot_failed", vm["vm_id"], None,
                      f"Could not delete old snapshot {old['snapshot_name']}", str(exc), now)'''
        render_vscode_screenshot(page, code_4_1, 'app/services.py', start_line=431, 
                                 out_png='Milestones/figures/code_4_1_snapshot.png')

        # 6. Listing 4.2.1: Autonomous Crash Observation, Heartbeat Polling & Debounced Recovery
        code_4_2 = '''def recover(conn, vbox, vm, now=None, snapshot=None, user_id=None) -> bool:
    """Zero-touch crash recovery: power off, restore latest snapshot, and restart VM."""
    now = now or now_local()
    snap = snapshot or latest_valid_snapshot(conn, vbox, vm)
    if snap is None:
        alert_once(conn, vm, "No usable snapshot exists. Manual recovery needed.", now)
        return False
    conn.execute("UPDATE vms SET status='restoring' WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    t0 = time.monotonic()
    try:
        state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
        if state not in ("poweroff", "aborted"):
            vbox.power_off(vm["vbox_uuid"])
            vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted"))
        vbox.restore_snapshot(vm["vbox_uuid"], snap["snapshot_name"])
        vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted", "saved"))
        vbox.start_vm(vm["vbox_uuid"])
    except VBoxError as exc:
        conn.execute("UPDATE vms SET status='crashed' WHERE vm_id=?", (vm["vm_id"],))
        conn.commit()
        return False
    conn.execute("UPDATE vms SET status='running', fail_count=0 WHERE vm_id=?", (vm["vm_id"],))
    conn.commit()
    dur = round(time.monotonic() - t0, 2)
    log_event(conn, "restore_success", vm["vm_id"], user_id,
              f"Automatic restore ({snap['snapshot_name']}) in {dur}s", "Success", now, dur)
    return True'''
        render_vscode_screenshot(page, code_4_2, 'app/services.py', start_line=1294, 
                                 out_png='Milestones/figures/code_4_2_recovery.png')

        # 7. Listing 4.3.1: Standalone Open Virtualization Appliance (.ova) Export Engine
        code_4_3 = '''def create_backup(conn, vbox, vm, backup_dir: str, user_id=None, now=None):
    """Export the VM to an independent compressed .ova appliance archive."""
    now = now or now_local()
    b_path = Path(backup_dir)
    b_path.mkdir(parents=True, exist_ok=True)
    suffix = secrets.token_hex(4)
    filename = f"backup-{vm['vm_name']}-{now:%Y%m%d-%H%M%S}-{suffix}.ova"
    dest = b_path / filename

    state = vbox.wait_until_ready(vm["vbox_uuid"]).lower()
    was_active = state in ("running", "paused")
    if was_active:
        vbox.save_state(vm["vbox_uuid"])
        vbox.wait_for_state(vm["vbox_uuid"], ("saved", "aborted-saved"), timeout=1800)
    try:
        vbox.export_vm(vm["vbox_uuid"], str(dest))
    finally:
        if was_active:
            vbox.discard_state(vm["vbox_uuid"])
            vbox.wait_for_state(vm["vbox_uuid"], ("poweroff", "aborted"))
            vbox.start_vm(vm["vbox_uuid"])

    size = dest.stat().st_size if dest.exists() else 0
    conn.execute("INSERT INTO backups (vm_id, backup_name, file_path, size_bytes, created_at) "
                 "VALUES (?, ?, ?, ?, ?)", (vm["vm_id"], filename, str(dest), size, ts(now)))
    conn.commit()'''
        render_vscode_screenshot(page, code_4_3, 'app/services.py', start_line=718, 
                                 out_png='Milestones/figures/code_4_3_backup.png')

        # 8. Listing 4.4.1: Golden Master Linked/Full Clone Provisioning Routine
        code_4_4 = '''def approve_vm_request(conn, vbox, request_id, admin_user_id, interval=30, keep=5,
                       pre_session=True, now=None):
    """Approve request and autonomously provision linked or full clone from Golden Master."""
    now = now or now_local()
    req = conn.execute("SELECT * FROM vm_requests WHERE request_id=?", (request_id,)).fetchone()
    conn.execute("UPDATE vm_requests SET status='creating', updated_at=? WHERE request_id=?",
                 (ts(now), request_id))
    conn.commit()
    
    snap_name = _template_snapshot(conn, vbox, req["template_vbox_uuid"]) \\
        if req["clone_type"] == "linked" else None
    new_name, new_uuid = _clone_from_template(
        vbox, req["template_vbox_uuid"], req["requested_name"],
        linked=(req["clone_type"] == "linked"), snapshot=snap_name, conn=conn)
        
    vm_id = register_vm(conn, new_name, new_uuid, req["class_group"], interval, keep,
                        pre_session=pre_session, user_id=req["user_id"], now=now)
    take_snapshot(conn, vbox, get_vm(conn, vm_id), "baseline", now=now, user_id=admin_user_id)
    conn.execute("UPDATE vm_requests SET status='ready', created_vm_id=?, updated_at=? "
                 "WHERE request_id=?", (vm_id, ts(now), request_id))
    conn.commit()
    log_event(conn, "vm_request_approved", vm_id, admin_user_id,
              f"Approved and created '{new_name}' for student", "Success", now)
    return vm_id'''
        render_vscode_screenshot(page, code_4_4, 'app/services.py', start_line=1077, 
                                 out_png='Milestones/figures/code_4_4_provisioning.png')

        # 9. Listing 4.5.1: Multi-Channel Alert Dispatcher with HMAC-SHA256 Webhook Signing
        code_4_5 = '''def _send_webhook(settings, subject, body, severity="info", vm_id=None):
    """Format JSON payload and dispatch over HTTP POST with HMAC-SHA256 signature."""
    payload = {
        "event": "alert", "severity": severity, "subject": subject,
        "body": body, "vm_id": vm_id, "timestamp": ts(now_local())
    }
    raw = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "VMRecovery/1.0"}
    if settings.webhook_secret:
        signature = hmac.new(settings.webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
        headers["X-VMRecovery-Signature"] = f"sha256={signature}"
        
    request = urllib.request.Request(settings.webhook_url, data=raw, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status >= 300:
            raise RuntimeError(f"webhook returned HTTP {response.status}")'''
        render_vscode_screenshot(page, code_4_5, 'app/notifier.py', start_line=103, 
                                 out_png='Milestones/figures/code_4_5_notifier.png')

        # 10. Listing 4.6.1: Token-Authenticated REST API Endpoint Guard with Constant-Time Verification
        code_4_6 = '''@bp.before_request
def require_token():
    """Enforce constant-time HMAC bearer token validation on all API endpoints."""
    if request.endpoint == "api.health":      # the liveness probe stays open
        return None
    expected = _token()
    if not expected:
        return jsonify(error="The API is disabled. Set VMR_API_TOKEN on Settings page."), 503
        
    presented = _presented_token()
    # hmac.compare_digest prevents timing side-channel attacks
    if not hmac.compare_digest(presented, expected):
        return jsonify(error="A valid API token is required."), 401
    return None'''
        render_vscode_screenshot(page, code_4_6, 'app/api.py', start_line=38, 
                                 out_png='Milestones/figures/code_4_6_api.png')

        # 11. Listing 4.11.1: Managed Systemd Service Supervisor Configuration
        code_4_11 = '''[Unit]
Description=Automated Virtual Machine Recovery System (VMRecovery)
After=network.target virtualbox.service
Wants=virtualbox.service

[Service]
Type=simple
User=nomad
Group=nomad
SupplementaryGroups=vboxusers
WorkingDirectory=/home/nomad/vmrecovery
ExecStart=/home/nomad/vmrecovery/.venv/bin/python run.py
Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal

# Security hardening directives
NoNewPrivileges=false
ProtectSystem=full
UMask=0077

[Install]
WantedBy=multi-user.target'''
        render_vscode_screenshot(page, code_4_11, 'deploy/vmrecovery.service', start_line=1, 
                                 lexer=IniLexer(), out_png='Milestones/figures/code_4_11_systemd.png')

        # 12. Listing 4.13.1: Supabase Managed Cloud PostgreSQL Adapter & Auto-Migration
        code_4_13 = '''def connect_pg(url: str) -> PgConnectionWrapper:
    """Connect to PostgreSQL/Supabase with SSL and automatic IPv4 pooler fallback."""
    import psycopg2
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if "sslmode" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        return PgConnectionWrapper(conn)
    except psycopg2.OperationalError:
        # Fallback to Supabase connection pooler if IPv6 direct access is unreachable
        m = re.search(r"://([^:]+):([^@]+)@db\\.([a-z0-9]+)\\.supabase\\.co", url)
        if m:
            _, pw, ref = m.groups()
            pooler = f"postgresql://postgres.{ref}:{pw}@aws-0-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"
            return PgConnectionWrapper(psycopg2.connect(pooler, connect_timeout=10))
        raise

def init_pg_db(url: str) -> None:
    """Initialize relational PostgreSQL schema on Supabase upon cold start."""
    conn = connect_pg(url)
    try:
        ddl = SCHEMA_PG.read_text()
        for statement in ddl.split(";"):
            cleaned = statement.strip()
            if cleaned:
                conn.execute(cleaned)
        conn.commit()
    finally:
        conn.close()'''
        render_vscode_screenshot(page, code_4_13, 'app/pg_db.py', start_line=180, 
                                 lexer=PythonLexer(), out_png='Milestones/figures/code_4_13_supabase_pg.png')

        browser.close()
    print("SUCCESS: All 12 VS Code code screenshots generated successfully!")

if __name__ == '__main__':
    generate_all_snippets()
