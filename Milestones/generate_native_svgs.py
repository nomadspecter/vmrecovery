import os
import subprocess

os.makedirs('Milestones/figures', exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Level 0 DFD (Context Diagram) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_dfd_level0_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 750" width="100%" height="100%">
  <defs>
    <filter id="drop-shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#EA580C"/>
    </marker>
    <linearGradient id="procGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB"/>
      <stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <linearGradient id="entGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </linearGradient>
    <linearGradient id="sysGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFBEB"/>
      <stop offset="100%" stop-color="#FEF3C7"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1100" height="750" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="550" y="38" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.3a: Level 0 Data Flow Diagram (Context Diagram)</text>
  <text x="550" y="60" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Automated Virtual Machine Instability Management System (VMRecovery)</text>

  <!-- CENTER PROCESS: 0.0 -->
  <g transform="translate(430, 260)" filter="url(#drop-shadow)">
    <rect width="240" height="150" rx="75" fill="url(#procGrad)" stroke="#1E40AF" stroke-width="3"/>
    <line x1="20" y1="50" x2="220" y2="50" stroke="#93C5FD" stroke-width="1.5" stroke-dasharray="4,3"/>
    <text x="120" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="15" font-weight="800" fill="#DBEAFE" text-anchor="middle">0.0</text>
    <text x="120" y="80" font-family="'Segoe UI', Roboto, sans-serif" font-size="15" font-weight="700" fill="#FFFFFF" text-anchor="middle">VM INSTABILITY</text>
    <text x="120" y="102" font-family="'Segoe UI', Roboto, sans-serif" font-size="15" font-weight="700" fill="#FFFFFF" text-anchor="middle">MANAGEMENT SYSTEM</text>
    <text x="120" y="124" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#BFDBFE" text-anchor="middle">(Core Engine &amp; Daemon)</text>
  </g>

  <!-- EXTERNAL ENTITIES: Left Side -->
  <!-- Admin -->
  <g transform="translate(40, 110)" filter="url(#drop-shadow)">
    <rect width="180" height="85" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="180" height="26" rx="6" fill="#334155"/>
    <text x="90" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="90" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Lab Administrator</text>
    <text x="90" y="70" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(System &amp; Policies)</text>
  </g>

  <!-- Trainer -->
  <g transform="translate(40, 290)" filter="url(#drop-shadow)">
    <rect width="180" height="85" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="180" height="26" rx="6" fill="#334155"/>
    <text x="90" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="90" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Trainer</text>
    <text x="90" y="70" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(Class Sessions &amp; Labs)</text>
  </g>

  <!-- Student -->
  <g transform="translate(40, 480)" filter="url(#drop-shadow)">
    <rect width="180" height="85" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="180" height="26" rx="6" fill="#334155"/>
    <text x="90" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="90" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Student</text>
    <text x="90" y="70" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(Learner / Workstation)</text>
  </g>

  <!-- EXTERNAL ENTITIES: Right Side -->
  <!-- VirtualBox Hypervisor -->
  <g transform="translate(870, 160)" filter="url(#drop-shadow)">
    <rect width="190" height="95" rx="6" fill="url(#sysGrad)" stroke="#D97706" stroke-width="2"/>
    <rect x="0" y="0" width="190" height="26" rx="6" fill="#D97706"/>
    <text x="95" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">HARDWARE HYPERVISOR</text>
    <text x="95" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#78350F" text-anchor="middle">Oracle VirtualBox</text>
    <text x="95" y="72" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#92400E" text-anchor="middle">VBoxManage CLI &amp; IPC</text>
    <text x="95" y="86" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#B45309" text-anchor="middle">(/tmp/.vbox-nomad-ipc)</text>
  </g>

  <!-- Notification Gateways -->
  <g transform="translate(870, 420)" filter="url(#drop-shadow)">
    <rect width="190" height="90" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <rect x="0" y="0" width="190" height="26" rx="6" fill="#DC2626"/>
    <text x="95" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL GATEWAY</text>
    <text x="95" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#991B1B" text-anchor="middle">Alert Gateways</text>
    <text x="95" y="72" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#B91C1C" text-anchor="middle">SMTP &amp; Signed Webhooks</text>
  </g>

  <!-- FLOWS: Administrator -->
  <!-- Admin -> System -->
  <path d="M 220 135 L 435 285" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <rect x="235" y="185" width="170" height="28" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="320" y="203" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">VM Config, Policies, Settings</text>

  <!-- System -> Admin -->
  <path d="M 430 310 L 220 170" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <rect x="230" y="235" width="175" height="28" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="317" y="253" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Dashboard, Logs, Health Alerts</text>

  <!-- FLOWS: Trainer -->
  <!-- Trainer -> System -->
  <path d="M 220 320 L 430 320" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="325" y="312" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#0F172A" text-anchor="middle">Session Start/End, Restore Reqs</text>

  <!-- System -> Trainer -->
  <path d="M 430 350 L 220 350" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="325" y="366" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#0F172A" text-anchor="middle">VM Status, Session Telemetry</text>

  <!-- FLOWS: Student -->
  <!-- Student -> System -->
  <path d="M 220 495 L 435 385" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <rect x="230" y="445" width="180" height="28" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="320" y="463" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">VM Clone Request, Password</text>

  <!-- System -> Student -->
  <path d="M 435 415 L 220 525" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <rect x="230" y="495" width="180" height="28" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
  <text x="320" y="513" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Assigned VM Status, Approval</text>

  <!-- FLOWS: VirtualBox -->
  <!-- System -> VBox -->
  <path d="M 670 300 L 870 215" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#arrow-orange)"/>
  <rect x="685" y="235" width="170" height="28" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1"/>
  <text x="770" y="253" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#9A3412" text-anchor="middle">startvm, snapshot, restore</text>

  <!-- VBox -> System -->
  <path d="M 870 245 L 670 330" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#arrow-orange)"/>
  <rect x="685" y="295" width="170" height="28" rx="4" fill="#FFF7ED" stroke="#FED7AA" stroke-width="1"/>
  <text x="770" y="313" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#9A3412" text-anchor="middle">Guest Heartbeats, States</text>

  <!-- FLOWS: Notification Gateways -->
  <!-- System -> Notifications -->
  <path d="M 670 360 L 870 450" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="685" y="405" width="175" height="28" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="1"/>
  <text x="772" y="423" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#991B1B" text-anchor="middle">Incident Alert, HMAC Webhook</text>

  <!-- Notifications -> System -->
  <path d="M 870 480 L 670 390" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="685" y="460" width="175" height="28" rx="4" fill="#FEF2F2" stroke="#FECACA" stroke-width="1"/>
  <text x="772" y="478" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#991B1B" text-anchor="middle">Delivery Receipts, HTTP Status</text>

  <!-- Footer Note -->
  <rect x="50" y="670" width="1000" height="50" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
  <text x="550" y="692" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#334155" text-anchor="middle">
    Architecture Boundary: Local hypervisor engine controls physical VirtualBox VMs; management plane is accessible via LAN / Cloudflare Tunnel.
  </text>
  <text x="550" y="708" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#64748B" text-anchor="middle">
    Hands-on student guest OS execution is conducted over SSH (Port 22) and RDP/VRDP (Port 3389).
  </text>
</svg>'''
    with open('Milestones/figures/fig2_3_3a_dfd_level0.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_3a_dfd_level0.svg', '-o', 'Milestones/figures/fig2_3_3a_dfd_level0.png'], check=True)
    print("Generated Native SVG: fig2_3_3a_dfd_level0.svg -> PNG")

# -----------------------------------------------------------------------------
# 2. Level 1 DFD - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_dfd_level1_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 880" width="100%" height="100%">
  <defs>
    <filter id="shadow1" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="2" stdDeviation="2.5" flood-opacity="0.12"/>
    </filter>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#334155"/>
    </marker>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1200" height="880" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="600" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.3b: Level 1 Data Flow Diagram (Functional Decomposition)</text>
  <text x="600" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Decomposition of the 8 Subsystem Processes and 9 Relational Data Stores</text>

  <!-- 3 External Entities (Left) -->
  <g transform="translate(30, 110)" filter="url(#shadow1)">
    <rect width="130" height="60" rx="4" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <text x="65" y="35" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Administrator</text>
  </g>

  <g transform="translate(30, 360)" filter="url(#shadow1)">
    <rect width="130" height="60" rx="4" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <text x="65" y="35" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Trainer</text>
  </g>

  <g transform="translate(30, 620)" filter="url(#shadow1)">
    <rect width="130" height="60" rx="4" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <text x="65" y="35" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Student</text>
  </g>

  <!-- 2 External Entities (Right) -->
  <g transform="translate(1030, 260)" filter="url(#shadow1)">
    <rect width="140" height="70" rx="4" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
    <text x="70" y="34" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#78350F" text-anchor="middle">VirtualBox</text>
    <text x="70" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#92400E" text-anchor="middle">Hypervisor Host</text>
  </g>

  <g transform="translate(1030, 540)" filter="url(#shadow1)">
    <rect width="140" height="70" rx="4" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <text x="70" y="34" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#991B1B" text-anchor="middle">Notification</text>
    <text x="70" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#B91C1C" text-anchor="middle">Gateways</text>
  </g>

  <!-- 8 PROCESSES (Rounded Blue Cards) -->
  <!-- P1.0 -->
  <g transform="translate(250, 95)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">1.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">User Authentication &amp;</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">RBAC Role Enforcement</text>
  </g>

  <!-- P2.0 -->
  <g transform="translate(250, 195)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">2.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">VM Registry &amp; Policy</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">Configuration Management</text>
  </g>

  <!-- P3.0 -->
  <g transform="translate(250, 295)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">3.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Snapshot Automation &amp;</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">Pre-Session Baselines</text>
  </g>

  <!-- P4.0 -->
  <g transform="translate(250, 395)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">4.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Guest Heartbeat &amp;</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">State Interrogation Loop</text>
  </g>

  <!-- P5.0 -->
  <g transform="translate(250, 495)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">5.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Autonomous Recovery &amp;</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">Debounced Rollback</text>
  </g>

  <!-- P6.0 -->
  <g transform="translate(250, 595)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">6.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Student VM Provisioning</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">&amp; Template Cloning</text>
  </g>

  <!-- P7.0 -->
  <g transform="translate(250, 695)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">7.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Appliance Backup (.ova)</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">&amp; Database Hot-Backup</text>
  </g>

  <!-- P8.0 -->
  <g transform="translate(250, 790)" filter="url(#shadow1)">
    <rect width="250" height="65" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="28" cy="32" r="16" fill="#2563EB"/>
    <text x="28" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">8.0</text>
    <text x="56" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E3A8A">Multi-Channel Alerting</text>
    <text x="56" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="500" fill="#1D4ED8">&amp; Signed Webhooks</text>
  </g>

  <!-- 9 DATA STORES (Center-Right, Open Double-Line Store Boxes) -->
  <g transform="translate(680, 100)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D1</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">users (Auth &amp; Roles)</text>
  </g>

  <g transform="translate(680, 180)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D2</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">vms (Hardware Registry)</text>
  </g>

  <g transform="translate(680, 260)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D3</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">snapshots (Point-in-Time)</text>
  </g>

  <g transform="translate(680, 340)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D4</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">class_sessions (Classes)</text>
  </g>

  <g transform="translate(680, 420)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D5</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">vm_requests (Clones)</text>
  </g>

  <g transform="translate(680, 500)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D6</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">events (Audit Log)</text>
  </g>

  <g transform="translate(680, 580)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D7</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">backups (.ova Appliances)</text>
  </g>

  <g transform="translate(680, 660)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D8</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">app_settings (Overrides)</text>
  </g>

  <g transform="translate(680, 740)">
    <path d="M 0 0 L 220 0 M 0 45 L 220 45" stroke="#475569" stroke-width="2" fill="none"/>
    <rect x="0" y="2" width="220" height="41" fill="#F8FAFC"/>
    <text x="15" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#2563EB">D9</text>
    <text x="50" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">notifications (Dispatches)</text>
  </g>

  <!-- Connectors (Entities to Processes) -->
  <path d="M 160 135 L 250 135" stroke="#334155" stroke-width="1.8" marker-end="url(#arr)"/>
  <path d="M 160 150 L 210 150 L 210 225 L 250 225" stroke="#334155" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 160 380 L 250 325" stroke="#334155" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 160 400 L 250 525" stroke="#334155" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 160 650 L 250 625" stroke="#334155" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>

  <!-- Connectors (Processes to Data Stores) -->
  <path d="M 500 130 L 680 120" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 225 L 680 200" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 325 L 680 280" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 425 L 680 215" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 525 L 680 290" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 625 L 680 440" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 725 L 680 600" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>
  <path d="M 500 815 L 680 760" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>

  <!-- Connectors (Processes to VirtualBox / Notifications) -->
  <path d="M 500 335 L 1030 290" stroke="#D97706" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 1030 305 L 500 435" stroke="#D97706" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 500 535 L 1030 320" stroke="#D97706" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
  <path d="M 500 830 L 1030 575" stroke="#DC2626" stroke-width="1.8" marker-end="url(#arr)" fill="none"/>
</svg>'''
    with open('Milestones/figures/fig2_3_3b_dfd_level1.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_3b_dfd_level1.svg', '-o', 'Milestones/figures/fig2_3_3b_dfd_level1.png'], check=True)
    print("Generated Native SVG: fig2_3_3b_dfd_level1.svg -> PNG")

# -----------------------------------------------------------------------------
# 3. Complete Use Case Diagram - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_use_case_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1150 920" width="100%" height="100%">
  <defs>
    <filter id="ucShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.12"/>
    </filter>
  </defs>

  <rect width="1150" height="920" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="575" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.5: Complete UML Use Case Diagram</text>
  <text x="575" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">System Boundary and Interaction Model Across Roles</text>

  <!-- SYSTEM BOUNDARY BOX -->
  <rect x="260" y="85" width="630" height="805" rx="10" fill="#F8FAFC" stroke="#64748B" stroke-width="2" stroke-dasharray="6,4"/>
  <rect x="260" y="85" width="630" height="35" rx="10" fill="#E2E8F0"/>
  <text x="575" y="108" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#334155" text-anchor="middle">SYSTEM BOUNDARY: VM INSTABILITY MANAGEMENT PLATFORM (VMRECOVERY)</text>

  <!-- ACTORS: Left Side -->
  <!-- 1. Administrator -->
  <g transform="translate(100, 200)">
    <circle cx="25" cy="18" r="14" fill="#E2E8F0" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="32" x2="25" y2="70" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="0" y1="48" x2="50" y2="48" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="5" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="45" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <text x="25" y="125" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Administrator</text>
    <text x="25" y="140" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#64748B" text-anchor="middle">(Full System Admin)</text>
  </g>

  <!-- 2. Trainer -->
  <g transform="translate(100, 440)">
    <circle cx="25" cy="18" r="14" fill="#E2E8F0" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="32" x2="25" y2="70" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="0" y1="48" x2="50" y2="48" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="5" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="45" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <text x="25" y="125" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Trainer</text>
    <text x="25" y="140" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#64748B" text-anchor="middle">(Instructor / Labs)</text>
  </g>

  <!-- 3. Student -->
  <g transform="translate(100, 680)">
    <circle cx="25" cy="18" r="14" fill="#E2E8F0" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="32" x2="25" y2="70" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="0" y1="48" x2="50" y2="48" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="5" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <line x1="25" y1="70" x2="45" y2="105" stroke="#0F172A" stroke-width="2.5"/>
    <text x="25" y="125" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#0F172A" text-anchor="middle">Student</text>
    <text x="25" y="140" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#64748B" text-anchor="middle">(Learner / Workstation)</text>
  </g>

  <!-- ACTOR: Right Side (VirtualBox Supporting Actor) -->
  <g transform="translate(970, 440)">
    <rect x="0" y="0" width="130" height="85" rx="6" fill="#FFFBEB" stroke="#D97706" stroke-width="2" filter="url(#ucShadow)"/>
    <text x="65" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#B45309" text-anchor="middle">&lt;&lt;actor&gt;&gt;</text>
    <text x="65" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#78350F" text-anchor="middle">VirtualBox</text>
    <text x="65" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#92400E" text-anchor="middle">Hypervisor Host</text>
  </g>

  <!-- USE CASES (Ellipses) -->
  <g transform="translate(350, 140)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Authenticate &amp; Manage Account</text>
  </g>

  <g transform="translate(350, 195)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Register Lab VM &amp; Define Policies</text>
  </g>

  <g transform="translate(350, 250)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Start / End Class Training Session</text>
  </g>

  <g transform="translate(350, 305)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Trigger Pre-Session Snapshot Baseline</text>
  </g>

  <g transform="translate(350, 360)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#9A3412" text-anchor="middle">Interrogate Guest OS Heartbeats</text>
  </g>

  <g transform="translate(350, 415)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#C2410C" text-anchor="middle">Execute Autonomous Zero-Touch Recovery</text>
  </g>

  <g transform="translate(350, 470)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Request Emergency Snapshot Restore</text>
  </g>

  <g transform="translate(350, 525)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Provision VM from Golden Master Template</text>
  </g>

  <g transform="translate(350, 580)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Approve / Reject VM Provisioning Requests</text>
  </g>

  <g transform="translate(350, 635)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Export / Restore Standalone .ova Appliance</text>
  </g>

  <g transform="translate(350, 690)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">Perform SQLite WAL Hot Backup &amp; Migrations</text>
  </g>

  <g transform="translate(350, 745)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#FEF2F2" stroke="#DC2626" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#991B1B" text-anchor="middle">Dispatch Multi-Channel Alerts (SMTP / Webhook)</text>
  </g>

  <g transform="translate(350, 800)" filter="url(#ucShadow)">
    <ellipse cx="140" cy="24" rx="135" ry="22" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.8"/>
    <text x="140" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#1E3A8A" text-anchor="middle">View Health Dashboard &amp; Reliability Reports</text>
  </g>

  <!-- LINES: Admin Connections -->
  <line x1="160" y1="230" x2="360" y2="164" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="355" y2="219" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="360" y2="274" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="355" y2="604" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="355" y2="659" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="355" y2="714" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="230" x2="355" y2="824" stroke="#475569" stroke-width="1.5"/>

  <!-- LINES: Trainer Connections -->
  <line x1="160" y1="470" x2="355" y2="164" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="470" x2="360" y2="274" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="470" x2="355" y2="329" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="470" x2="355" y2="494" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="470" x2="355" y2="824" stroke="#475569" stroke-width="1.5"/>

  <!-- LINES: Student Connections -->
  <line x1="160" y1="710" x2="355" y2="164" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="710" x2="355" y2="494" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="710" x2="355" y2="549" stroke="#475569" stroke-width="1.5"/>

  <!-- LINES: VirtualBox Supporting Connections -->
  <line x1="970" y1="480" x2="625" y2="219" stroke="#D97706" stroke-width="1.5"/>
  <line x1="970" y1="480" x2="625" y2="329" stroke="#D97706" stroke-width="1.5"/>
  <line x1="970" y1="480" x2="625" y2="384" stroke="#D97706" stroke-width="1.5"/>
  <line x1="970" y1="480" x2="625" y2="439" stroke="#D97706" stroke-width="1.5"/>
  <line x1="970" y1="480" x2="625" y2="549" stroke="#D97706" stroke-width="1.5"/>
  <line x1="970" y1="480" x2="625" y2="659" stroke="#D97706" stroke-width="1.5"/>
</svg>'''
    with open('Milestones/figures/fig2_3_5_use_case_complete.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_5_use_case_complete.svg', '-o', 'Milestones/figures/fig2_3_5_use_case_complete.png'], check=True)
    print("Generated Native SVG: fig2_3_5_use_case_complete.svg -> PNG")

# -----------------------------------------------------------------------------
# 4. Complete 10-Table ERD - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_erd_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1350 960" width="100%" height="100%">
  <defs>
    <filter id="erdShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="erdArr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#DC2626"/>
    </marker>
  </defs>

  <rect width="1350" height="960" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="675" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.4: Complete Entity Relationship Diagram (10 Relational Tables)</text>
  <text x="675" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">SQLite Relational Database Architecture in WAL Mode (Schema Version 8)</text>

  <!-- TABLE 1: users -->
  <g transform="translate(40, 100)" filter="url(#erdShadow)">
    <rect width="210" height="150" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="210" height="30" rx="6" fill="#2563EB"/>
    <text x="105" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">USERS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] user_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" fill="#334155">     username</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     password_hash</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     role</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     created_at</text>
  </g>

  <!-- TABLE 2: vms -->
  <g transform="translate(360, 100)" filter="url(#erdShadow)">
    <rect width="240" height="280" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="240" height="30" rx="6" fill="#2563EB"/>
    <text x="120" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">VMS (REGISTRY)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] vm_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" fill="#334155">     vm_name</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     vbox_uuid</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     class_group</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#334155">     interval_minutes</text>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="11" fill="#334155">     retention_count</text>
    <text x="12" y="172" font-family="'Courier New', monospace" font-size="11" fill="#334155">     pre_session_snapshot</text>
    <text x="12" y="192" font-family="'Courier New', monospace" font-size="11" fill="#334155">     heartbeat_property</text>
    <text x="12" y="212" font-family="'Courier New', monospace" font-size="11" fill="#334155">     is_template</text>
    <text x="12" y="232" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] user_id (Student)</text>
    <text x="12" y="252" font-family="'Courier New', monospace" font-size="11" fill="#334155">     status, last_checked</text>
    <text x="12" y="272" font-family="'Courier New', monospace" font-size="11" fill="#059669">     admin_paused</text>
  </g>

  <!-- TABLE 3: snapshots -->
  <g transform="translate(710, 100)" filter="url(#erdShadow)">
    <rect width="220" height="150" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="220" height="30" rx="6" fill="#2563EB"/>
    <text x="110" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">SNAPSHOTS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] snapshot_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] vm_id</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     snapshot_name</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     snapshot_type</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     created_at</text>
  </g>

  <!-- TABLE 4: backups -->
  <g transform="translate(1040, 100)" filter="url(#erdShadow)">
    <rect width="230" height="150" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="230" height="30" rx="6" fill="#2563EB"/>
    <text x="115" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">BACKUPS (.OVA)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] backup_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] vm_id</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     backup_name</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     file_path, size_bytes</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     created_at</text>
  </g>

  <!-- TABLE 5: vm_requests -->
  <g transform="translate(40, 440)" filter="url(#erdShadow)">
    <rect width="250" height="230" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="250" height="30" rx="6" fill="#2563EB"/>
    <text x="125" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">VM_REQUESTS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] request_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] user_id (Student)</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     template_vbox_uuid</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     template_name</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#334155">     requested_name</text>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="11" fill="#334155">     class_group, clone_type</text>
    <text x="12" y="172" font-family="'Courier New', monospace" font-size="11" fill="#059669">     status, rejection_reason</text>
    <text x="12" y="192" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] created_vm_id</text>
    <text x="12" y="212" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     created_at, updated_at</text>
  </g>

  <!-- TABLE 6: class_sessions -->
  <g transform="translate(360, 440)" filter="url(#erdShadow)">
    <rect width="240" height="170" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="240" height="30" rx="6" fill="#2563EB"/>
    <text x="120" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">CLASS_SESSIONS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] session_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" fill="#334155">     class_group</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     status (active/ended)</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] started_by (Trainer)</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#334155">     started_at</text>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="11" fill="#334155">     ended_at</text>
  </g>

  <!-- TABLE 7: events -->
  <g transform="translate(710, 440)" filter="url(#erdShadow)">
    <rect width="250" height="190" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="250" height="30" rx="6" fill="#2563EB"/>
    <text x="125" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EVENTS (AUDIT LOG)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] event_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] vm_id (nullable)</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] user_id (nullable)</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     event_type</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#334155">     details, result</text>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="11" fill="#059669">     duration_seconds</text>
    <text x="12" y="172" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     created_at</text>
  </g>

  <!-- TABLE 8: notifications -->
  <g transform="translate(1040, 440)" filter="url(#erdShadow)">
    <rect width="240" height="190" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="240" height="30" rx="6" fill="#2563EB"/>
    <text x="120" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">NOTIFICATIONS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] notification_id</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] vm_id (nullable)</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     channel (smtp/webhook)</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" fill="#334155">     recipient, subject</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="11" fill="#334155">     severity, status</text>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="11" fill="#64748B">     sent_at</text>
  </g>

  <!-- TABLE 9: app_settings -->
  <g transform="translate(200, 750)" filter="url(#erdShadow)">
    <rect width="230" height="130" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="230" height="30" rx="6" fill="#2563EB"/>
    <text x="115" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">APP_SETTINGS</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] key</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" fill="#334155">     value</text>
    <text x="12" y="92" font-family="'Courier New', monospace" font-size="11" fill="#334155">     updated_at</text>
    <text x="12" y="112" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#2563EB">[FK] updated_by</text>
  </g>

  <!-- TABLE 10: schema_meta -->
  <g transform="translate(560, 750)" filter="url(#erdShadow)">
    <rect width="210" height="110" rx="6" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <rect width="210" height="30" rx="6" fill="#2563EB"/>
    <text x="105" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">SCHEMA_META</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#D97706">[PK] key</text>
    <text x="12" y="72" font-family="'Courier New', monospace" font-size="11" fill="#334155">     value ('8')</text>
    <text x="12" y="92" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#64748B">(Auto-migration tracker)</text>
  </g>

  <!-- RELATIONSHIP LINES (Red dashed arrows) -->
  <!-- users -> vms -->
  <path d="M 250 170 L 360 170" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- vms -> snapshots -->
  <path d="M 600 170 L 710 170" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- vms -> backups -->
  <path d="M 930 170 L 1040 170" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- users -> vm_requests -->
  <path d="M 140 250 L 140 440" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- vms -> vm_requests (created_vm_id) -->
  <path d="M 380 380 L 380 410 L 290 470" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- users -> class_sessions (started_by) -->
  <path d="M 210 250 L 210 390 L 360 480" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- vms -> events -->
  <path d="M 600 240 L 710 470" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
  <!-- vms -> notifications -->
  <path d="M 600 300 L 980 300 L 980 470 L 1040 470" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#erdArr)"/>
</svg>'''
    with open('Milestones/figures/fig2_3_4_erd_complete.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_4_erd_complete.svg', '-o', 'Milestones/figures/fig2_3_4_erd_complete.png'], check=True)
    print("Generated Native SVG: fig2_3_4_erd_complete.svg -> PNG")

# -----------------------------------------------------------------------------
# 5. Complete UML Class Diagram - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_class_diagram_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1350 960" width="100%" height="100%">
  <defs>
    <filter id="clsShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="clsArr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#166534"/>
    </marker>
  </defs>

  <rect width="1350" height="960" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="675" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.6: Complete UML Architectural Class Diagram</text>
  <text x="675" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Object-Oriented Domain Entities and Service Controller Abstractions</text>

  <!-- CONTROLLER 1: VBoxController -->
  <g transform="translate(40, 100)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#047857" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#047857"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;controller&gt;&gt; VBoxController</text>
    <!-- Attributes -->
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- vboxmanage_bin: str</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- action_timeout: int</text>
    <line x1="0" y1="80" x2="280" y2="80" stroke="#CBD5E1" stroke-width="1"/>
    <!-- Methods -->
    <text x="12" y="98" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ list_vms(): list</text>
    <text x="12" y="114" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ get_state(uuid): str</text>
    <text x="12" y="130" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ start_vm(uuid, type)</text>
    <text x="12" y="146" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ power_off_vm(uuid)</text>
    <text x="12" y="162" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ take_snapshot(uuid, name)</text>
    <text x="12" y="178" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ restore_snapshot(uuid, name)</text>
    <text x="12" y="194" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ clone_vm(src, new, mode)</text>
    <text x="12" y="210" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ get_guest_property(uuid, prop)</text>
  </g>

  <!-- CONTROLLER 2: Worker Daemon -->
  <g transform="translate(370, 100)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#047857" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#047857"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;service&gt;&gt; Worker (Daemon)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- interval_seconds: int = 10</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- thread: Thread</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- stop_event: Event</text>
    <line x1="0" y1="95" x2="280" y2="95" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="115" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ start()</text>
    <text x="12" y="133" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ stop()</text>
    <text x="12" y="151" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ run_cycle(conn, vbox)</text>
    <text x="12" y="169" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ check_heartbeat(vm, vbox)</text>
    <text x="12" y="187" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ trigger_recovery(vm, vbox)</text>
    <text x="12" y="205" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ prune_snapshots(vm, vbox)</text>
  </g>

  <!-- CONTROLLER 3: Notifier Engine -->
  <g transform="translate(700, 100)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#047857" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#047857"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;service&gt;&gt; Notifier</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- smtp_host: str</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- webhook_url: str</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- webhook_secret: str</text>
    <line x1="0" y1="95" x2="280" y2="95" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="115" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ notify(subject, body, sev)</text>
    <text x="12" y="133" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ send_smtp(to, subject, body)</text>
    <text x="12" y="151" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ send_webhook(payload, url)</text>
    <text x="12" y="169" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ sign_hmac_sha256(data)</text>
    <text x="12" y="187" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ test_channels()</text>
  </g>

  <!-- CONTROLLER 4: Settings Layer -->
  <g transform="translate(1030, 100)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#047857" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#047857"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;config&gt;&gt; Settings</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- host, port: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- fail_threshold: int = 2</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">- heartbeat_timeout: int = 90</text>
    <line x1="0" y1="95" x2="280" y2="95" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="115" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ from_env(): Settings</text>
    <text x="12" y="133" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ apply_db_overrides(conn)</text>
    <text x="12" y="151" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ get_effective(key): val</text>
    <text x="12" y="169" font-family="'Courier New', monospace" font-size="10.5" fill="#047857">+ is_production(): bool</text>
  </g>

  <!-- DOMAIN ENTITY 1: VirtualMachine -->
  <g transform="translate(40, 420)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; VirtualMachine</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ vm_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ vm_name: str</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ vbox_uuid: str</text>
    <text x="12" y="100" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ class_group: str</text>
    <text x="12" y="116" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ is_template: bool</text>
    <text x="12" y="132" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ admin_paused: bool</text>
    <line x1="0" y1="142" x2="280" y2="142" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="162" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ start(type='headless')</text>
    <text x="12" y="180" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ power_off()</text>
    <text x="12" y="198" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ pause() / resume()</text>
    <text x="12" y="216" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ update_policy(interval, keep)</text>
  </g>

  <!-- DOMAIN ENTITY 2: Snapshot -->
  <g transform="translate(370, 420)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; Snapshot</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ snapshot_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ vm_id: int</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ snapshot_name: str</text>
    <text x="12" y="100" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ snapshot_type: str</text>
    <text x="12" y="116" font-family="'Courier New', monospace" font-size="10.5" fill="#64748B">+ created_at: str</text>
    <line x1="0" y1="130" x2="280" y2="130" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ take(conn, vbox, type): str</text>
    <text x="12" y="172" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ restore(conn, vbox): bool</text>
    <text x="12" y="192" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ delete(conn, vbox): bool</text>
    <text x="12" y="212" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ prune_oldest(conn, keep)</text>
  </g>

  <!-- DOMAIN ENTITY 3: VMRequest (Provisioning) -->
  <g transform="translate(700, 420)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; VMRequest</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ request_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ user_id: int (Student)</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ requested_name: str</text>
    <text x="12" y="100" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ clone_type: str</text>
    <text x="12" y="116" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ status: str</text>
    <line x1="0" y1="130" x2="280" y2="130" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="152" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ submit(template, name)</text>
    <text x="12" y="172" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ approve(admin_id): int</text>
    <text x="12" y="192" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ reject(admin_id, reason)</text>
    <text x="12" y="212" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ list_pending(user_id)</text>
  </g>

  <!-- DOMAIN ENTITY 4: User & RBAC -->
  <g transform="translate(1030, 420)" filter="url(#clsShadow)">
    <rect width="280" height="230" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; User (RBAC)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ user_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ username: str</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ role: str</text>
    <text x="12" y="100" font-family="'Courier New', monospace" font-size="10.5" fill="#64748B">+ created_at: str</text>
    <line x1="0" y1="120" x2="280" y2="120" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="145" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ authenticate(password): bool</text>
    <text x="12" y="165" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ change_password(new_pass)</text>
    <text x="12" y="185" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ has_permission(role): bool</text>
    <text x="12" y="205" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ list_assigned_vms(): list</text>
  </g>

  <!-- ENTITIES: Bottom Row -->
  <!-- ClassSession -->
  <g transform="translate(180, 720)" filter="url(#clsShadow)">
    <rect width="280" height="180" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; ClassSession</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ session_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ class_group: str, status: str</text>
    <line x1="0" y1="80" x2="280" y2="80" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="105" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ start(class_group, trainer_id)</text>
    <text x="12" y="125" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ end(power_off=True)</text>
    <text x="12" y="145" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ is_active(class_group): bool</text>
  </g>

  <!-- EventLog -->
  <g transform="translate(530, 720)" filter="url(#clsShadow)">
    <rect width="280" height="180" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; EventLog</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ event_id: int, vm_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ event_type: str, result: str</text>
    <text x="12" y="84" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ duration_seconds: float</text>
    <line x1="0" y1="95" x2="280" y2="95" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="120" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ log(event_type, details)</text>
    <text x="12" y="140" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ export_csv(): bytes</text>
    <text x="12" y="160" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ prune_older_than(days)</text>
  </g>

  <!-- Backup -->
  <g transform="translate(880, 720)" filter="url(#clsShadow)">
    <rect width="280" height="180" rx="4" fill="#FFFFFF" stroke="#1E40AF" stroke-width="2"/>
    <rect width="280" height="30" rx="4" fill="#1E40AF"/>
    <text x="140" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">&lt;&lt;entity&gt;&gt; Backup (.ova)</text>
    <text x="12" y="52" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ backup_id: int, vm_id: int</text>
    <text x="12" y="68" font-family="'Courier New', monospace" font-size="10.5" fill="#334155">+ file_path: str, size: int</text>
    <line x1="0" y1="80" x2="280" y2="80" stroke="#CBD5E1" stroke-width="1"/>
    <text x="12" y="105" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ create(vbox, backup_dir)</text>
    <text x="12" y="125" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ restore(vbox): bool</text>
    <text x="12" y="145" font-family="'Courier New', monospace" font-size="10.5" fill="#1E40AF">+ delete(): bool</text>
  </g>

  <!-- Arrows (Controllers to Entities) -->
  <path d="M 180 330 L 180 420" fill="none" stroke="#166534" stroke-width="1.8" marker-end="url(#clsArr)"/>
  <path d="M 510 330 L 510 420" fill="none" stroke="#166534" stroke-width="1.8" marker-end="url(#clsArr)"/>
  <path d="M 840 330 L 840 420" fill="none" stroke="#166534" stroke-width="1.8" marker-end="url(#clsArr)"/>
</svg>'''
    with open('Milestones/figures/fig2_3_6_class_diagram_complete.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig2_3_6_class_diagram_complete.svg', '-o', 'Milestones/figures/fig2_3_6_class_diagram_complete.png'], check=True)
    print("Generated Native SVG: fig2_3_6_class_diagram_complete.svg -> PNG")

# -----------------------------------------------------------------------------
# 6. Modular System Architecture (Figure 3.1) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_fig3_1_architecture_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 750" width="100%" height="100%">
  <defs>
    <filter id="archShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="arrArch" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrArchBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
  </defs>

  <rect width="1100" height="750" fill="#FFFFFF"/>
  <text x="550" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 3.1: Modular System Architecture and Process Interaction Model</text>
  <text x="550" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Concurrent Dual-Flow Architecture: Synchronous WSGI Web Tier &amp; Autonomous Worker Daemon</text>

  <!-- Ingress Clients (Left) -->
  <g transform="translate(30, 110)" filter="url(#archShadow)">
    <rect width="180" height="110" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>
    <rect width="180" height="28" rx="8" fill="#475569"/>
    <text x="90" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WEB BROWSERS</text>
    <text x="90" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#1E293B" text-anchor="middle">Lab Stakeholders</text>
    <text x="90" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">• Lab Administrator</text>
    <text x="90" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">• Course Trainers &amp; Students</text>
  </g>

  <g transform="translate(30, 480)" filter="url(#archShadow)">
    <rect width="180" height="100" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>
    <rect width="180" height="28" rx="8" fill="#475569"/>
    <text x="90" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL SYSTEMS</text>
    <text x="90" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#1E293B" text-anchor="middle">REST API Ingress</text>
    <text x="90" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">• Campus SIEM Dashboards</text>
    <text x="90" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">• Token Authenticated Clients</text>
  </g>

  <!-- SINGLE PROCESS BOUNDARY -->
  <rect x="250" y="90" width="560" height="630" rx="12" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" stroke-dasharray="6,4"/>
  <rect x="270" y="76" width="360" height="26" rx="4" fill="#E2E8F0"/>
  <text x="450" y="94" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="800" fill="#334155" text-anchor="middle">SINGLE PROCESS EXECUTION BOUNDARY (app/)</text>

  <!-- Web Tier -->
  <g transform="translate(280, 120)" filter="url(#archShadow)">
    <rect width="230" height="140" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <rect width="230" height="30" rx="8" fill="#2563EB"/>
    <text x="115" y="20" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WEB TIER (Flask + WSGI)</text>
    <text x="15" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#1E40AF">app/views.py (UI Blueprints)</text>
    <text x="15" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Dashboard, VMs, Snapshots</text>
    <text x="15" y="92" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Student Self-Service Portal</text>
    <text x="15" y="112" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#1E40AF">app/api.py (JSON REST API)</text>
    <text x="15" y="128" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Bearer Token Verified Endpoints</text>
  </g>

  <!-- Worker Tier -->
  <g transform="translate(280, 460)" filter="url(#archShadow)">
    <rect width="230" height="140" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>
    <rect width="230" height="30" rx="8" fill="#EA580C"/>
    <text x="115" y="20" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WORKER DAEMON (Daemon)</text>
    <text x="15" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#C2410C">app/worker.py (Background)</text>
    <text x="15" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• 10s Continuous Polling Loop</text>
    <text x="15" y="92" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• 2-Cycle Failure Debouncer</text>
    <text x="15" y="110" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Hourly SQLite Online Backup</text>
    <text x="15" y="128" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Retention &amp; Log Pruning</text>
  </g>

  <!-- Core Services -->
  <g transform="translate(560, 240)" filter="url(#archShadow)">
    <rect width="220" height="240" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
    <rect width="220" height="30" rx="8" fill="#16A34A"/>
    <text x="110" y="20" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">CORE SERVICES LAYER</text>
    <text x="15" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#15803D">app/services.py</text>
    <text x="15" y="78" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• VM Registry &amp; Policies</text>
    <text x="15" y="98" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Snapshot Scheduling</text>
    <text x="15" y="118" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Autonomous Crash Healing</text>
    <text x="15" y="138" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Circuit-Breaker Guard</text>
    <text x="15" y="158" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Student Request Cloner</text>
    <text x="15" y="178" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Disaster Recovery (.ova)</text>
    <text x="15" y="198" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Role-Based Access Control</text>
    <text x="15" y="218" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Runtime Configuration</text>
  </g>

  <!-- Subsystems (Right Inside Boundary) -->
  <g transform="translate(560, 120)" filter="url(#archShadow)">
    <rect width="220" height="95" rx="6" fill="#FAF5FF" stroke="#9333EA" stroke-width="2"/>
    <rect width="220" height="24" rx="6" fill="#9333EA"/>
    <text x="110" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">HYPERVISOR DRIVER</text>
    <text x="15" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#7E22CE">app/vbox.py</text>
    <text x="15" y="63" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• VBoxManage CLI Adapter</text>
    <text x="15" y="80" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Guest Property Telemetry</text>
  </g>

  <g transform="translate(560, 510)" filter="url(#archShadow)">
    <rect width="220" height="95" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <rect width="220" height="24" rx="6" fill="#DC2626"/>
    <text x="110" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">PERSISTENCE SUBSYSTEM</text>
    <text x="15" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#B91C1C">app/db.py</text>
    <text x="15" y="63" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• SQLite in WAL Mode</text>
    <text x="15" y="80" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• 8 Numbered Schema Migrations</text>
  </g>

  <g transform="translate(280, 620)" filter="url(#archShadow)">
    <rect width="500" height="80" rx="6" fill="#FFFBEB" stroke="#D97706" stroke-width="1.8"/>
    <text x="250" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#B45309" text-anchor="middle">NOTIFICATION SUBSYSTEM (app/notifier.py)</text>
    <text x="250" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#78350F" text-anchor="middle">SMTP Dispatch with STARTTLS Encryption &amp; Real-Time HMAC-SHA256 Signed JSON Webhooks</text>
    <text x="250" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#92400E" text-anchor="middle">(Non-blocking asynchronous delivery with automated retry &amp; audit logging in notifications table)</text>
  </g>

  <!-- External Physical Hypervisor (Far Right) -->
  <g transform="translate(860, 180)" filter="url(#archShadow)">
    <rect width="210" height="180" rx="8" fill="#FFFBEB" stroke="#D97706" stroke-width="2"/>
    <rect width="210" height="28" rx="8" fill="#D97706"/>
    <text x="105" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">ORACLE VIRTUALBOX 7.2</text>
    <text x="15" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#92400E">Hardware Hypervisor Layer</text>
    <text x="15" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• VT-x/AMD-V Hardware Accel</text>
    <text x="15" y="94" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Differencing VDI Disks</text>
    <text x="15" y="114" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Headless Execution Engine</text>
    <text x="15" y="134" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E293B">• Guest Properties Engine</text>
    <text x="15" y="156" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#B45309">Registered: agnes, debian, etc.</text>
  </g>

  <!-- Storage Database (Far Right Bottom) -->
  <g transform="translate(860, 480)" filter="url(#archShadow)">
    <rect width="210" height="130" rx="8" fill="#F8FAFC" stroke="#0284C7" stroke-width="2"/>
    <rect width="210" height="28" rx="8" fill="#0284C7"/>
    <text x="105" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">PHYSICAL STORAGE</text>
    <text x="15" y="52" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#0369A1">instance/vmrecovery.db</text>
    <text x="15" y="70" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• WAL Journal File (-wal)</text>
    <text x="15" y="88" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Shared Memory Index (-shm)</text>
    <text x="15" y="108" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#0369A1">backups/ (OVA &amp; Hot DBs)</text>
  </g>

  <!-- Arrows -->
  <path d="M 210 165 L 280 165" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrArchBlue)"/>
  <path d="M 210 530 L 280 530" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrArchBlue)"/>
  <path d="M 510 190 L 560 260" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrArch)"/>
  <path d="M 510 520 L 560 450" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrArch)"/>
  <path d="M 670 240 L 670 215" fill="none" stroke="#9333EA" stroke-width="2" marker-end="url(#arrArch)"/>
  <path d="M 670 480 L 670 510" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrArch)"/>
  <path d="M 780 165 L 860 230" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arrArch)"/>
  <path d="M 780 560 L 860 540" fill="none" stroke="#0284C7" stroke-width="2" marker-end="url(#arrArch)"/>
</svg>'''
    with open('Milestones/figures/fig3_1_architecture.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_1_architecture.svg', '-o', 'Milestones/figures/fig3_1_architecture.png'], check=True)
    print("Generated Native SVG: fig3_1_architecture.svg -> PNG")


# -----------------------------------------------------------------------------
# 7. SQLite WAL Concurrency Model (Figure 3.2) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_fig3_2_database_wal_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 700" width="100%" height="100%">
  <defs>
    <filter id="walShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="arrWal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrWalBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
  </defs>

  <rect width="1100" height="700" fill="#FFFFFF"/>
  <text x="550" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 3.2: SQLite Concurrency Model (WAL Mode) &amp; Schema Evolution</text>
  <text x="550" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Non-Blocking Concurrent Operations: Multiple Simultaneous Readers and Zero-Delay Writers</text>

  <!-- Top: Dual Ingress Threads -->
  <g transform="translate(100, 100)" filter="url(#walShadow)">
    <rect width="380" height="120" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <rect width="380" height="30" rx="8" fill="#2563EB"/>
    <text x="190" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WEB TIER CONCURRENCY (Waitress WSGI)</text>
    <text x="20" y="58" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#1E40AF">• Dedicated Connection per HTTP Request Thread</text>
    <text x="20" y="78" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Rapid Read Operations: Dashboard &amp; VM Status Queries</text>
    <text x="20" y="98" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Instant Writes: Student VM Requests &amp; Password Changes</text>
  </g>

  <g transform="translate(620, 100)" filter="url(#walShadow)">
    <rect width="380" height="120" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>
    <rect width="380" height="30" rx="8" fill="#EA580C"/>
    <text x="190" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WORKER DAEMON CONCURRENCY (app/worker.py)</text>
    <text x="20" y="58" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#C2410C">• Independent DB Connection per 10s Monitoring Cycle</text>
    <text x="20" y="78" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Continuous Telemetry Writes: State &amp; Heartbeat Timestamps</text>
    <text x="20" y="98" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">• Atomic Recovery Logging: Event Trails &amp; MTTR Durations</text>
  </g>

  <!-- Center: SQLite Engine -->
  <g transform="translate(250, 260)" filter="url(#walShadow)">
    <rect width="600" height="140" rx="10" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2.5"/>
    <rect width="600" height="32" rx="10" fill="#CA8A04"/>
    <text x="300" y="22" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle">SQLITE 3 EMBEDDED DATABASE ENGINE (app/db.py)</text>
    <text x="30" y="60" font-family="'Courier New', monospace" font-size="12" font-weight="700" fill="#854D0E">PRAGMA journal_mode = WAL;</text>
    <text x="320" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#713F12">Writes append to log without blocking concurrent reads</text>
    <text x="30" y="85" font-family="'Courier New', monospace" font-size="12" font-weight="700" fill="#854D0E">PRAGMA busy_timeout = 15000;</text>
    <text x="320" y="85" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#713F12">15-second busy handler completely eliminates locked errors</text>
    <text x="30" y="110" font-family="'Courier New', monospace" font-size="12" font-weight="700" fill="#854D0E">PRAGMA foreign_keys = ON;</text>
    <text x="320" y="110" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#713F12">Enforces referential integrity on VM deletions &amp; cascades</text>
  </g>

  <!-- Bottom: Physical Disk Files -->
  <g transform="translate(100, 460)" filter="url(#walShadow)">
    <rect width="260" height="190" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
    <rect width="260" height="28" rx="8" fill="#16A34A"/>
    <text x="130" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">MAIN DATABASE FILE</text>
    <text x="20" y="55" font-family="'Courier New', monospace" font-size="12" font-weight="700" fill="#166534">instance/vmrecovery.db</text>
    <text x="20" y="80" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• B-Tree Structured Tables</text>
    <text x="20" y="100" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Primary relational data</text>
    <text x="20" y="120" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Updated via Checkpoints</text>
    <text x="20" y="150" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-style="italic" fill="#16A34A">Non-destructive checkpoints</text>
  </g>

  <g transform="translate(420, 460)" filter="url(#walShadow)">
    <rect width="260" height="190" rx="8" fill="#FAF5FF" stroke="#9333EA" stroke-width="2"/>
    <rect width="260" height="28" rx="8" fill="#9333EA"/>
    <text x="130" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">WRITE-AHEAD LOG &amp; SHM</text>
    <text x="20" y="55" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#7E22CE">vmrecovery.db-wal</text>
    <text x="20" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Append-only transactions</text>
    <text x="20" y="95" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Fast sequential I/O write</text>
    <text x="20" y="125" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#7E22CE">vmrecovery.db-shm</text>
    <text x="20" y="145" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Shared-memory index</text>
    <text x="20" y="165" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Coordinates multi-threads</text>
  </g>

  <g transform="translate(740, 460)" filter="url(#walShadow)">
    <rect width="260" height="190" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <rect width="260" height="28" rx="8" fill="#DC2626"/>
    <text x="130" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">DYNAMIC SCHEMA &amp; BACKUP</text>
    <text x="20" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#991B1B">schema_meta (Migrations 1-8)</text>
    <text x="20" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Safe programmatic upgrades</text>
    <text x="20" y="95" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Table recreation pattern</text>
    <text x="20" y="125" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#991B1B">Online Hot Backup API</text>
    <text x="20" y="145" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Non-blocking backup API</text>
    <text x="20" y="165" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Hourly automated retention</text>
  </g>

  <!-- Connectors -->
  <path d="M 290 220 L 450 260" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrWalBlue)"/>
  <path d="M 810 220 L 650 260" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#arrWal)"/>
  <path d="M 400 400 L 230 460" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrWal)"/>
  <path d="M 550 400 L 550 460" fill="none" stroke="#9333EA" stroke-width="2" marker-end="url(#arrWal)"/>
  <path d="M 700 400 L 870 460" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrWal)"/>
</svg>'''
    with open('Milestones/figures/fig3_2_database_wal.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_2_database_wal.svg', '-o', 'Milestones/figures/fig3_2_database_wal.png'], check=True)
    print("Generated Native SVG: fig3_2_database_wal.svg -> PNG")


# -----------------------------------------------------------------------------
# 8. Worker Monitoring & Self-Healing Flowchart (Figure 3.6) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_fig3_6_worker_flowchart_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 1150" width="100%" height="100%">
  <defs>
    <filter id="fcShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="2" stdDeviation="2.5" flood-opacity="0.12"/>
    </filter>
    <marker id="arrFc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrFcRed" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#DC2626"/>
    </marker>
    <marker id="arrFcGreen" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#16A34A"/>
    </marker>
  </defs>

  <rect width="950" height="1150" fill="#FFFFFF"/>
  <text x="475" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="19" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 3.6: Autonomous Recovery Engine Decision Logic &amp; Failure Debouncing</text>
  <text x="475" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Zero-Touch Self-Healing Loop Executing Every 10 Seconds (app/worker.py &amp; app/services.py)</text>

  <!-- 1. Start Pill -->
  <g transform="translate(350, 90)" filter="url(#fcShadow)">
    <rect width="250" height="45" rx="22.5" fill="#334155"/>
    <text x="125" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle">START WORKER CYCLE (10s)</text>
  </g>

  <!-- 2. Process: Query VBox -->
  <g transform="translate(330, 175)" filter="url(#fcShadow)">
    <rect width="290" height="60" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <text x="145" y="27" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E40AF" text-anchor="middle">Query Oracle VirtualBox</text>
    <text x="145" y="47" font-family="'Courier New', monospace" font-size="11" fill="#334155" text-anchor="middle">VBoxManage list runningvms</text>
  </g>

  <!-- 3. Decision 1: Registered & In Session? -->
  <g transform="translate(475, 290)" filter="url(#fcShadow)">
    <polygon points="0,-45 130,0 0,45 -130,0" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2"/>
    <text x="0" y="-8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Registered VM &amp;</text>
    <text x="0" y="12" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Active Session?</text>
  </g>

  <!-- Branch: Not in session -> Skip -->
  <g transform="translate(110, 268)" filter="url(#fcShadow)">
    <rect width="180" height="45" rx="6" fill="#F1F5F9" stroke="#94A3B8" stroke-width="1.5"/>
    <text x="90" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Skip / Wait Next Cycle</text>
  </g>

  <!-- 4. Decision 2: Admin Paused? -->
  <g transform="translate(475, 420)" filter="url(#fcShadow)">
    <polygon points="0,-42 125,0 0,42 -125,0" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2"/>
    <text x="0" y="-6" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Is Machine</text>
    <text x="0" y="14" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">admin_paused == 1?</text>
  </g>

  <!-- Branch: Paused -> Maintain -->
  <g transform="translate(110, 400)" filter="url(#fcShadow)">
    <rect width="180" height="45" rx="6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.5"/>
    <text x="90" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1E40AF" text-anchor="middle">Maintain Paused State (OK)</text>
  </g>

  <!-- 5. Process: Query Heartbeat -->
  <g transform="translate(320, 500)" filter="url(#fcShadow)">
    <rect width="310" height="60" rx="6" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
    <text x="155" y="26" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#15803D" text-anchor="middle">Poll Guest Heartbeat Property</text>
    <text x="155" y="46" font-family="'Courier New', monospace" font-size="10.5" fill="#334155" text-anchor="middle">/VirtualBox/.../VBoxService/heartbeat</text>
  </g>

  <!-- 6. Decision 3: Fresh & Running? -->
  <g transform="translate(475, 630)" filter="url(#fcShadow)">
    <polygon points="0,-45 130,0 0,45 -130,0" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2"/>
    <text x="0" y="-8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">State == 'running' &amp;</text>
    <text x="0" y="12" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Heartbeat &lt; 90s?</text>
  </g>

  <!-- Branch: Healthy (Yes) -->
  <g transform="translate(110, 608)" filter="url(#fcShadow)">
    <rect width="190" height="50" rx="6" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
    <text x="95" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#166534" text-anchor="middle">Reset fail_count = 0</text>
    <text x="95" y="42" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#15803D" text-anchor="middle">Status = 'running'</text>
  </g>

  <!-- Branch: Unhealthy (No) -> Increment fail_count -->
  <g transform="translate(680, 605)" filter="url(#fcShadow)">
    <rect width="220" height="55" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <text x="110" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#991B1B" text-anchor="middle">Increment fail_count (+1)</text>
    <text x="110" y="44" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#7F1D1D" text-anchor="middle">Log Transient Warning</text>
  </g>

  <!-- 7. Decision 4: Debounce Check -->
  <g transform="translate(790, 750)" filter="url(#fcShadow)">
    <polygon points="0,-45 125,0 0,45 -125,0" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2"/>
    <text x="0" y="-8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Is fail_count &gt;=</text>
    <text x="0" y="12" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">fail_threshold (2)?</text>
  </g>

  <!-- Debounce Branch: No -> Wait next cycle -->
  <g transform="translate(520, 730)" filter="url(#fcShadow)">
    <rect width="180" height="42" rx="6" fill="#F8FAFC" stroke="#64748B" stroke-width="1.5"/>
    <text x="90" y="26" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569" text-anchor="middle">Debounce (Wait next 10s)</text>
  </g>

  <!-- 8. Decision 5: Circuit Breaker Check -->
  <g transform="translate(790, 890)" filter="url(#fcShadow)">
    <polygon points="0,-45 125,0 0,45 -125,0" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2"/>
    <text x="0" y="-8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">Past Hour Restores</text>
    <text x="0" y="12" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#854D0E" text-anchor="middle">&gt;= max (3)?</text>
  </g>

  <!-- Circuit Breaker Tripped (Yes) -->
  <g transform="translate(480, 868)" filter="url(#fcShadow)">
    <rect width="220" height="50" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <text x="110" y="22" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#991B1B" text-anchor="middle">CIRCUIT BREAKER TRIPPED</text>
    <text x="110" y="40" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#7F1D1D" text-anchor="middle">Status='needs_admin', Send Alert</text>
  </g>

  <!-- Confirmed Autonomous Recovery (No) -->
  <g transform="translate(670, 990)" filter="url(#fcShadow)">
    <rect width="240" height="90" rx="8" fill="#FEE2E2" stroke="#B91C1C" stroke-width="2.5"/>
    <text x="120" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="800" fill="#991B1B" text-anchor="middle">EXECUTE ZERO-TOUCH ROLLBACK</text>
    <text x="12" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">1. Discard unstable saved state</text>
    <text x="12" y="62" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">2. Restore newest valid snapshot</text>
    <text x="12" y="78" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">3. Headless boot &amp; reset fail_count</text>
  </g>

  <!-- Arrows -->
  <path d="M 475 135 L 475 175" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrFc)"/>
  <path d="M 475 235 L 475 245" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrFc)"/>
  
  <path d="M 345 290 L 290 290" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrFc)"/>
  <text x="320" y="282" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#64748B">No</text>

  <path d="M 475 335 L 475 378" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrFcGreen)"/>
  <text x="485" y="355" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#16A34A">Yes</text>

  <path d="M 350 420 L 290 420" fill="none" stroke="#3B82F6" stroke-width="2" marker-end="url(#arrFc)"/>
  <text x="320" y="412" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#3B82F6">Yes</text>

  <path d="M 475 462 L 475 500" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrFc)"/>
  <text x="485" y="482" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#1E293B">No</text>

  <path d="M 475 560 L 475 585" fill="none" stroke="#1E293B" stroke-width="2" marker-end="url(#arrFc)"/>

  <path d="M 345 630 L 300 630" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrFcGreen)"/>
  <text x="325" y="622" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#16A34A">Yes</text>

  <path d="M 605 630 L 680 630" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrFcRed)"/>
  <text x="635" y="622" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#DC2626">No</text>

  <path d="M 790 660 L 790 705" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrFcRed)"/>

  <path d="M 665 750 L 700 750" fill="none" stroke="#64748B" stroke-width="2" marker-end="url(#arrFc)"/>
  <text x="730" y="742" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#64748B">No</text>

  <path d="M 790 795 L 790 845" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrFcRed)"/>
  <text x="800" y="820" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#DC2626">Yes</text>

  <path d="M 665 890 L 700 890" fill="none" stroke="#DC2626" stroke-width="2" marker-end="url(#arrFcRed)"/>
  <text x="725" y="882" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#DC2626">Yes</text>

  <path d="M 790 935 L 790 990" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrFcGreen)"/>
  <text x="800" y="960" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#16A34A">No</text>
</svg>'''
    with open('Milestones/figures/fig3_6_worker_flowchart.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_6_worker_flowchart.svg', '-o', 'Milestones/figures/fig3_6_worker_flowchart.png'], check=True)
    print("Generated Native SVG: fig3_6_worker_flowchart.svg -> PNG")


# -----------------------------------------------------------------------------
# 9. Production Deployment Architecture (Figure 3.16) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_fig3_deployment_architecture_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <filter id="depShadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="arrDep" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrDepBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arrDepOrange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#EA580C"/>
    </marker>
  </defs>

  <rect width="1200" height="800" fill="#FFFFFF"/>
  <text x="600" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 3.16: Production Deployment Architecture with Cloudflare Zero-Trust &amp; AWS S3</text>
  <text x="600" y="60" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Hybrid On-Premises Hypervisor Host with Cloud Edge Ingress and Offsite Disaster Recovery Storage</text>

  <!-- ON-PREMISES HYPERVISOR BOUNDARY (Left) -->
  <rect x="40" y="90" width="620" height="680" rx="12" fill="#F8FAFC" stroke="#1E40AF" stroke-width="2.5"/>
  <rect x="60" y="75" width="450" height="28" rx="4" fill="#1E40AF"/>
  <text x="285" y="94" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="800" fill="#FFFFFF" text-anchor="middle">ON-PREMISES LAB HYPERVISOR HOST (Ubuntu 22.04 LTS / Debian)</text>

  <!-- Systemd Supervisor -->
  <g transform="translate(70, 120)" filter="url(#depShadow)">
    <rect width="560" height="50" rx="6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.8"/>
    <text x="280" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E40AF" text-anchor="middle">SYSTEMD SERVICE MANAGER (vmrecovery.service)</text>
    <text x="280" y="42" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Automatic Boot Startup, Restart-on-Failure (RestartSec=5s), StandardOutput=journal</text>
  </g>

  <!-- Waitress WSGI -->
  <g transform="translate(70, 190)" filter="url(#depShadow)">
    <rect width="560" height="75" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <rect width="560" height="24" rx="6" fill="#2563EB"/>
    <text x="280" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">WAITRESS MULTI-THREADED WSGI SERVER</text>
    <text x="20" y="46" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#1E40AF">Binding: http://127.0.0.1:5000 (Production threads=8)</text>
    <text x="20" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">Handles simultaneous trainer sessions, student self-service provisioning, and REST API calls</text>
  </g>

  <!-- Middle Row: Worker & SQLite -->
  <g transform="translate(70, 285)" filter="url(#depShadow)">
    <rect width="265" height="135" rx="6" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.8"/>
    <rect width="265" height="24" rx="6" fill="#EA580C"/>
    <text x="132" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">BACKGROUND WORKER</text>
    <text x="12" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#9A3412">app/worker.py</text>
    <text x="12" y="68" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• 10s Continuous Polling</text>
    <text x="12" y="86" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Zero-Touch Auto-Healing</text>
    <text x="12" y="104" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Hourly Online Database Backup</text>
    <text x="12" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Automatic Retention Pruning</text>
  </g>

  <g transform="translate(365, 285)" filter="url(#depShadow)">
    <rect width="265" height="135" rx="6" fill="#FEFCE8" stroke="#CA8A04" stroke-width="1.8"/>
    <rect width="265" height="24" rx="6" fill="#CA8A04"/>
    <text x="132" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">SQLITE 3 DATABASE (WAL)</text>
    <text x="12" y="48" font-family="'Courier New', monospace" font-size="10.5" font-weight="700" fill="#854D0E">instance/vmrecovery.db</text>
    <text x="12" y="68" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• WAL Concurrency Journal</text>
    <text x="12" y="86" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• 8 Sequential Migrations</text>
    <text x="12" y="104" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Atomic Transaction Logs</text>
    <text x="12" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Hot Backup Storage (backups/)</text>
  </g>

  <!-- Bottom: VirtualBox & Physical Machines -->
  <g transform="translate(70, 440)" filter="url(#depShadow)">
    <rect width="560" height="205" rx="8" fill="#FFFBEB" stroke="#D97706" stroke-width="2"/>
    <rect width="560" height="26" rx="8" fill="#D97706"/>
    <text x="280" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">ORACLE VIRTUALBOX 7.2 HYPERVISOR (VBoxManage)</text>
    <text x="20" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#78350F">Hardware Virtualization &amp; Differential Storage Control</text>
    <text x="20" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Fast Differencing Snapshots (&lt;10s Rollback) &amp; Golden Master Linked Clones</text>
    <text x="20" y="84" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Guest Property Heartbeat Telemetry &amp; Headless Process Execution</text>
    <text x="20" y="102" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Independent Appliance Export Engine (.ova compressed standalone packages)</text>

    <!-- Lab VMs Sub-boxes -->
    <rect x="20" y="115" width="115" height="75" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="77" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">debian</text>
    <text x="77" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Linux Server</text>
    <text x="77" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH Port 22</text>

    <rect x="155" y="115" width="115" height="75" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="212" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">LAB-CS-001</text>
    <text x="212" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Student Node 1</text>
    <text x="212" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH / VRDP</text>

    <rect x="290" y="115" width="115" height="75" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="347" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">LAB-CS-002</text>
    <text x="347" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Student Node 2</text>
    <text x="347" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH / VRDP</text>

    <rect x="425" y="115" width="115" height="75" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="482" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">agnes</text>
    <text x="482" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Lab Workstation</text>
    <text x="482" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">VRDP Port 3389</text>
  </g>

  <!-- Local Network Footnote -->
  <text x="350" y="665" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#1E40AF" text-anchor="middle">Local Area Network (LAN): Direct Student Access via SSH (22) &amp; VRDP (3389)</text>

  <!-- CLOUDFLARE ZERO-TRUST EDGE (Right Top) -->
  <g transform="translate(720, 100)" filter="url(#depShadow)">
    <rect width="440" height="150" rx="10" fill="#FFF7ED" stroke="#EA580C" stroke-width="2.5"/>
    <rect width="440" height="30" rx="10" fill="#EA580C"/>
    <text x="220" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">CLOUDFLARE ZERO-TRUST EDGE NETWORK (cloudflared)</text>
    <text x="20" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#C2410C">• Outbound Encrypted TLS Tunnel (No open router inbound ports)</text>
    <text x="20" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Automated Wildcard SSL/TLS Certificate Termination</text>
    <text x="20" y="95" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• DDoS Defense, Web Application Firewall (WAF) &amp; Global CDN</text>
    <text x="20" y="115" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">• Public Endpoint: <tspan font-family="'Courier New', monospace" font-weight="700" fill="#EA580C">https://vmrecovery.lab.domain</tspan></text>
    <text x="20" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">Enables University Examiners &amp; Remote Students to inspect dashboard safely</text>
  </g>

  <!-- UNIVERSITY STAKEHOLDERS (Right Middle) -->
  <g transform="translate(720, 290)" filter="url(#depShadow)">
    <rect width="440" height="140" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>
    <rect width="440" height="28" rx="8" fill="#475569"/>
    <text x="220" y="19" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">END USERS &amp; LAB CLIENTS</text>
    <text x="20" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#1E293B">1. Web Browser Access (Dashboard Management):</text>
    <text x="35" y="73" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">Examiners, Administrators, Trainers &amp; Students (HTTP/HTTPS)</text>
    <text x="20" y="98" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#166534">2. Guest Operating System Access (Hands-on Labs):</text>
    <text x="35" y="116" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">Direct LAN connection via SSH (port 22) and RDP/VRDP (port 3389)</text>
  </g>

  <!-- AWS CLOUD STORAGE (Right Bottom) -->
  <g transform="translate(720, 470)" filter="url(#depShadow)">
    <rect width="440" height="195" rx="10" fill="#F0FDF4" stroke="#16A34A" stroke-width="2.5"/>
    <rect width="440" height="30" rx="10" fill="#16A34A"/>
    <text x="220" y="21" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">AMAZON WEB SERVICES (AWS CLOUD 3-2-1 BACKUP)</text>
    <text x="20" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#15803D">• AWS S3 Bucket: Offsite Disaster Recovery Storage</text>
    <text x="20" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">  - Independent Open Virtualization Appliance (.ova) archives</text>
    <text x="20" y="95" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#334155">  - Hourly SQLite Online Hot Backups with SHA-256 Checksums</text>
    <text x="20" y="118" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#15803D">• Automated Synchronization Script:</text>
    <text x="35" y="136" font-family="'Courier New', monospace" font-size="10.5" fill="#1E293B">deploy/sync_s3_backups.sh (S3 Lifecycle Glacier)</text>
    <text x="20" y="160" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#15803D">• External Health Sentinel (AWS EC2 / Cloud Sentry):</text>
    <text x="35" y="178" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">Independent probe pinging /api/health to alert if host loses power</text>
  </g>

  <!-- Connectors -->
  <path d="M 630 220 L 720 175" fill="none" stroke="#EA580C" stroke-width="2.2" marker-end="url(#arrDepOrange)"/>
  <path d="M 940 250 L 940 290" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrDepBlue)"/>
  <path d="M 495 420 L 720 540" fill="none" stroke="#16A34A" stroke-width="2.2" marker-end="url(#arrDep)"/>
  <path d="M 350 440 L 720 370" fill="none" stroke="#166534" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrDep)"/>
</svg>'''
    with open('Milestones/figures/fig3_deployment_architecture.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-d', '300', '-p', '300', 'Milestones/figures/fig3_deployment_architecture.svg', '-o', 'Milestones/figures/fig3_deployment_architecture.png'], check=True)
    print("Generated Native SVG: fig3_deployment_architecture.svg -> PNG")

if __name__ == '__main__':
    generate_dfd_level0_svg()
    generate_dfd_level1_svg()
    generate_use_case_svg()
    generate_erd_svg()
    generate_class_diagram_svg()
    generate_fig3_1_architecture_svg()
    generate_fig3_2_database_wal_svg()
    generate_fig3_6_worker_flowchart_svg()
    generate_fig3_deployment_architecture_svg()
