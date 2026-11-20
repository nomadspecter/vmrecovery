import os
import subprocess

os.makedirs('Milestones/figures', exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Level 0 DFD (Context Diagram) - Native Clean Orthogonal SVG
# -----------------------------------------------------------------------------
def generate_dfd_level0_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" width="100%" height="100%">
  <defs>
    <filter id="drop-shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.14"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1E293B"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#EA580C"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#DC2626"/>
    </marker>
    <linearGradient id="procGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB"/>
      <stop offset="100%" stop-color="#1E40AF"/>
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
  <rect width="1200" height="760" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="600" y="38" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="21" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.3a: Level 0 Data Flow Diagram (Context Diagram)</text>
  <text x="600" y="60" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="12.5" fill="#64748B" text-anchor="middle">Automated Virtual Machine Instability Management System (VMRecovery)</text>

  <!-- ================================================================== -->
  <!-- LAYER 1: ORTHOGONAL FLOW ARROWS (Drawn FIRST so text never clips!) -->
  <!-- ================================================================== -->

  <!-- Admin <-> System (Top Left) -->
  <path d="M 225 140 H 545 V 275" fill="none" stroke="#2563EB" stroke-width="2.2" marker-end="url(#arrow-blue)"/>
  <path d="M 510 275 V 188 H 225" fill="none" stroke="#2563EB" stroke-width="2.2" marker-end="url(#arrow-blue)"/>

  <!-- Trainer <-> System (Middle Left) -->
  <path d="M 225 338 H 472" fill="none" stroke="#1E293B" stroke-width="2.2" marker-end="url(#arrow)"/>
  <path d="M 472 384 H 225" fill="none" stroke="#1E293B" stroke-width="2.2" marker-end="url(#arrow)"/>

  <!-- Student <-> System (Bottom Left) -->
  <path d="M 225 538 H 510 V 448" fill="none" stroke="#2563EB" stroke-width="2.2" marker-end="url(#arrow-blue)"/>
  <path d="M 545 448 V 586 H 225" fill="none" stroke="#2563EB" stroke-width="2.2" marker-end="url(#arrow-blue)"/>

  <!-- System <-> Oracle VirtualBox (Top Right) -->
  <path d="M 655 275 V 175 H 958" fill="none" stroke="#EA580C" stroke-width="2.2" marker-end="url(#arrow-orange)"/>
  <path d="M 958 228 H 690 V 275" fill="none" stroke="#EA580C" stroke-width="2.2" marker-end="url(#arrow-orange)"/>

  <!-- System <-> Alert Gateways (Bottom Right) -->
  <path d="M 690 448 V 495 H 958" fill="none" stroke="#DC2626" stroke-width="2.2" marker-end="url(#arrow-red)"/>
  <path d="M 958 548 H 655 V 448" fill="none" stroke="#DC2626" stroke-width="2.2" marker-end="url(#arrow-red)"/>

  <!-- ================================================================== -->
  <!-- LAYER 2: OPAQUE FLOW LABEL PILLS (Drawn OVER paths cleanly)        -->
  <!-- ================================================================== -->

  <!-- Admin Labels -->
  <rect x="262" y="125" width="216" height="28" rx="14" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.2"/>
  <text x="370" y="143" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#1E40AF" text-anchor="middle">VM Config, Policies &amp; Settings</text>

  <rect x="262" y="174" width="216" height="28" rx="14" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.2"/>
  <text x="370" y="192" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#1E40AF" text-anchor="middle">Dashboard, Audit Logs &amp; Alerts</text>

  <!-- Trainer Labels -->
  <rect x="252" y="324" width="194" height="26" rx="13" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
  <text x="349" y="341" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#0F172A" text-anchor="middle">Session Start/End, Approvals</text>

  <rect x="252" y="371" width="194" height="26" rx="13" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
  <text x="349" y="388" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#0F172A" text-anchor="middle">VM Status &amp; Class Telemetry</text>

  <!-- Student Labels -->
  <rect x="262" y="524" width="216" height="28" rx="14" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.2"/>
  <text x="370" y="542" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#1E40AF" text-anchor="middle">VM Clone &amp; Restore Requests</text>

  <rect x="262" y="572" width="216" height="28" rx="14" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.2"/>
  <text x="370" y="590" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#1E40AF" text-anchor="middle">Assigned VM Status &amp; Approvals</text>

  <!-- VirtualBox Labels -->
  <rect x="722" y="161" width="206" height="28" rx="14" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1.2"/>
  <text x="825" y="179" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#9A3412" text-anchor="middle">startvm, snapshot, restore, clone</text>

  <rect x="722" y="214" width="206" height="28" rx="14" fill="#FFFFFF" stroke="#FDBA74" stroke-width="1.2"/>
  <text x="825" y="232" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#9A3412" text-anchor="middle">Power States &amp; Guest Heartbeats</text>

  <!-- Alert Gateways Labels -->
  <rect x="722" y="481" width="206" height="28" rx="14" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="1.2"/>
  <text x="825" y="499" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#991B1B" text-anchor="middle">Incident Alerts &amp; HMAC Webhooks</text>

  <rect x="722" y="534" width="206" height="28" rx="14" fill="#FFFFFF" stroke="#FCA5A5" stroke-width="1.2"/>
  <text x="825" y="552" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#991B1B" text-anchor="middle">SMTP Receipts &amp; HTTP Status</text>

  <!-- ================================================================== -->
  <!-- LAYER 3: CENTER PROCESS & EXTERNAL ENTITIES                        -->
  <!-- ================================================================== -->

  <!-- CENTER PROCESS: 0.0 -->
  <g transform="translate(475, 278)" filter="url(#drop-shadow)">
    <rect width="250" height="166" rx="83" fill="url(#procGrad)" stroke="#1E3A8A" stroke-width="3"/>
    <line x1="28" y1="52" x2="222" y2="52" stroke="#93C5FD" stroke-width="1.5" stroke-dasharray="4,3"/>
    <text x="125" y="38" font-family="'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="800" fill="#DBEAFE" text-anchor="middle">0.0</text>
    <text x="125" y="84" font-family="'Segoe UI', Roboto, sans-serif" font-size="15.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">VM INSTABILITY</text>
    <text x="125" y="106" font-family="'Segoe UI', Roboto, sans-serif" font-size="15.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">MANAGEMENT SYSTEM</text>
    <text x="125" y="132" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="500" fill="#BFDBFE" text-anchor="middle">(Web Tier + Recovery Daemon)</text>
  </g>

  <!-- EXTERNAL ENTITIES: Left Side -->
  <g transform="translate(35, 118)" filter="url(#drop-shadow)">
    <rect width="190" height="90" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="190" height="26" rx="6" fill="#334155"/>
    <text x="95" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="95" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Lab Administrator</text>
    <text x="95" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(System &amp; Policies)</text>
  </g>

  <g transform="translate(35, 316)" filter="url(#drop-shadow)">
    <rect width="190" height="90" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="190" height="26" rx="6" fill="#334155"/>
    <text x="95" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="95" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Trainer</text>
    <text x="95" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(Class Sessions &amp; Labs)</text>
  </g>

  <g transform="translate(35, 514)" filter="url(#drop-shadow)">
    <rect width="190" height="90" rx="6" fill="url(#entGrad)" stroke="#334155" stroke-width="2"/>
    <rect x="0" y="0" width="190" height="26" rx="6" fill="#334155"/>
    <text x="95" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="95" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="700" fill="#0F172A" text-anchor="middle">Student</text>
    <text x="95" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">(Learner / Workstation)</text>
  </g>

  <!-- EXTERNAL ENTITIES: Right Side -->
  <g transform="translate(960, 150)" filter="url(#drop-shadow)">
    <rect width="205" height="102" rx="6" fill="url(#sysGrad)" stroke="#D97706" stroke-width="2"/>
    <rect x="0" y="0" width="205" height="26" rx="6" fill="#D97706"/>
    <text x="102" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">HARDWARE HYPERVISOR</text>
    <text x="102" y="54" font-family="'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700" fill="#78350F" text-anchor="middle">Oracle VirtualBox 7.2</text>
    <text x="102" y="74" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#92400E" text-anchor="middle">VBoxManage CLI &amp; IPC</text>
    <text x="102" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#B45309" text-anchor="middle">(/tmp/.vbox-nomad-ipc)</text>
  </g>

  <g transform="translate(960, 470)" filter="url(#drop-shadow)">
    <rect width="205" height="98" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <rect x="0" y="0" width="205" height="26" rx="6" fill="#DC2626"/>
    <text x="102" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL GATEWAY</text>
    <text x="102" y="56" font-family="'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700" fill="#991B1B" text-anchor="middle">Alert Gateways</text>
    <text x="102" y="76" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#B91C1C" text-anchor="middle">SMTP &amp; Signed Webhooks</text>
  </g>

  <!-- Footer Note -->
  <rect x="50" y="675" width="1100" height="54" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
  <text x="600" y="698" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="600" fill="#334155" text-anchor="middle">
    Architecture Boundary: Local hypervisor engine controls physical VirtualBox VMs; management plane is accessible via LAN / Cloudflare Tunnel / Render Cloud Demo.
  </text>
  <text x="600" y="716" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#64748B" text-anchor="middle">
    Hands-on student guest OS execution is conducted over SSH (Port 22) and RDP/VRDP (Port 3389).
  </text>
</svg>'''
    with open('Milestones/figures/fig2_3_3a_dfd_level0.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-z', '3.5', 'Milestones/figures/fig2_3_3a_dfd_level0.svg', '-o', 'Milestones/figures/fig2_3_3a_dfd_level0.png'], check=True)
    print("Generated Native SVG: fig2_3_3a_dfd_level0.svg -> PNG")

# -----------------------------------------------------------------------------
# 2. Level 1 DFD - Zero-Crossing 3-Column Labeled Native SVG
# -----------------------------------------------------------------------------
def generate_dfd_level1_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1360 960" width="100%" height="100%">
  <defs>
    <filter id="shadow1" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="1.5" dy="2" stdDeviation="2.5" flood-opacity="0.11"/>
    </filter>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#334155"/>
    </marker>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arr-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#D97706"/>
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#DC2626"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1360" height="960" fill="#FFFFFF"/>

  <!-- Title -->
  <text x="680" y="36" font-family="'Segoe UI', Roboto, sans-serif" font-size="21" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 2.3.3b: Level 1 Data Flow Diagram (Functional Decomposition)</text>
  <text x="680" y="58" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" fill="#64748B" text-anchor="middle">Zero-Crossing Decomposition of 5 External Interactors, 8 Core Processes &amp; 9 Connected Relational Data Stores</text>

  <!-- Column Headers -->
  <rect x="30" y="74" width="185" height="24" rx="4" fill="#F1F5F9" stroke="#CBD5E1"/>
  <text x="122" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="700" fill="#475569" text-anchor="middle">EXTERNAL INTERACTORS</text>

  <rect x="470" y="74" width="290" height="24" rx="4" fill="#EFF6FF" stroke="#BFDBFE"/>
  <text x="615" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="700" fill="#1E40AF" text-anchor="middle">SUBSYSTEM PROCESSES (1.0 – 8.0)</text>

  <rect x="1030" y="74" width="295" height="24" rx="4" fill="#F8FAFC" stroke="#CBD5E1"/>
  <text x="1177" y="90" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="700" fill="#334155" text-anchor="middle">RELATIONAL DATA STORES (D1 – D9)</text>

  <!-- ================================================================== -->
  <!-- LAYER 1: ALL ORTHOGONAL CONNECTORS (ZERO BOX CROSSINGS!)           -->
  <!-- ================================================================== -->

  <!-- LEFT CHANNEL: External Interactors -> Processes (x=215..470) -->
  <!-- Admin -> P1.0 & P2.0 -->
  <path d="M 215 142 H 468" fill="none" stroke="#334155" stroke-width="1.9" marker-end="url(#arr)"/>
  <path d="M 215 168 H 248 V 242 H 468" fill="none" stroke="#334155" stroke-width="1.9" marker-end="url(#arr)"/>

  <!-- Trainer -> P3.0 & P6.0 -->
  <path d="M 215 335 H 468" fill="none" stroke="#334155" stroke-width="1.9" marker-end="url(#arr)"/>
  <path d="M 215 362 H 235 V 632 H 468" fill="none" stroke="#334155" stroke-width="1.7" stroke-dasharray="4,3" marker-end="url(#arr)"/>

  <!-- VirtualBox <-> P3.0, P4.0, P5.0, P7.0 -->
  <path d="M 470 356 H 272 V 452 H 217" fill="none" stroke="#D97706" stroke-width="1.9" marker-end="url(#arr-orange)"/>
  <path d="M 215 462 H 468" fill="none" stroke="#D97706" stroke-width="1.9" marker-end="url(#arr-orange)"/>
  <path d="M 470 545 H 272 V 496 H 217" fill="none" stroke="#D97706" stroke-width="1.9" marker-end="url(#arr-orange)"/>
  <path d="M 470 742 H 255 V 514 H 217" fill="none" stroke="#D97706" stroke-width="1.7" stroke-dasharray="4,3" marker-end="url(#arr-orange)"/>

  <!-- Student -> P6.0 -->
  <path d="M 215 658 H 468" fill="none" stroke="#334155" stroke-width="1.9" marker-end="url(#arr)"/>

  <!-- P8.0 -> Notification Gateways -->
  <path d="M 470 842 H 217" fill="none" stroke="#DC2626" stroke-width="2.0" marker-end="url(#arr-red)"/>

  <!-- RIGHT CHANNEL: Processes -> Data Stores (x=760..1030) -->
  <!-- P1.0 -> D1 users -->
  <path d="M 760 142 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>

  <!-- P2.0 -> D2 vms & D8 app_settings -->
  <path d="M 760 228 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>
  <path d="M 760 254 H 795 V 314 H 1028" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>

  <!-- P3.0 -> D3 snapshots & D4 class_sessions -->
  <path d="M 760 336 H 782 V 398 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>
  <path d="M 760 358 H 772 V 478 H 1028" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>

  <!-- P4.0 -> D2 vms (status update) & D6 events -->
  <path d="M 760 436 H 808 V 242 H 1028" fill="none" stroke="#2563EB" stroke-width="1.7" stroke-dasharray="4,3" marker-end="url(#arr-blue)"/>
  <path d="M 760 462 H 795 V 558 H 1028" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arr-blue)"/>

  <!-- P5.0 -> D3 snapshots (read latest) & D6 events (audit log) -->
  <path d="M 1030 416 H 822 V 536 H 762" fill="none" stroke="#2563EB" stroke-width="1.7" stroke-dasharray="4,3" marker-end="url(#arr-blue)"/>
  <path d="M 760 558 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>

  <!-- P6.0 -> D5 vm_requests -->
  <path d="M 760 644 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>

  <!-- P7.0 -> D7 backups -->
  <path d="M 760 742 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>

  <!-- P8.0 -> D9 notifications -->
  <path d="M 760 842 H 1028" fill="none" stroke="#2563EB" stroke-width="1.9" marker-end="url(#arr-blue)"/>

  <!-- ================================================================== -->
  <!-- LAYER 2: FLOW LABELS (Crisp Opaque Pills on Horizontal Segments)   -->
  <!-- ================================================================== -->

  <!-- Left Labels -->
  <rect x="285" y="130" width="152" height="22" rx="11" fill="#FFFFFF" stroke="#CBD5E1"/>
  <text x="361" y="145" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E293B" text-anchor="middle">Login Credentials &amp; Roles</text>

  <rect x="285" y="230" width="152" height="22" rx="11" fill="#FFFFFF" stroke="#CBD5E1"/>
  <text x="361" y="245" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E293B" text-anchor="middle">VM Policies &amp; Settings</text>

  <rect x="285" y="323" width="152" height="22" rx="11" fill="#FFFFFF" stroke="#CBD5E1"/>
  <text x="361" y="338" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E293B" text-anchor="middle">Start/End Class Session</text>

  <rect x="292" y="346" width="146" height="20" rx="10" fill="#FFFBEB" stroke="#FDBA74"/>
  <text x="365" y="360" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" font-weight="600" fill="#9A3412" text-anchor="middle">snapshot take / delete</text>

  <rect x="285" y="451" width="152" height="22" rx="11" fill="#FFFBEB" stroke="#FDBA74"/>
  <text x="361" y="466" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#9A3412" text-anchor="middle">VMState &amp; Heartbeats</text>

  <rect x="285" y="534" width="152" height="22" rx="11" fill="#FFFBEB" stroke="#FDBA74"/>
  <text x="361" y="549" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#9A3412" text-anchor="middle">poweroff, restore, startvm</text>

  <rect x="285" y="621" width="152" height="20" rx="10" fill="#FFFFFF" stroke="#CBD5E1"/>
  <text x="361" y="635" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" font-weight="600" fill="#475569" text-anchor="middle">Approve / Reject Request</text>

  <rect x="285" y="647" width="152" height="22" rx="11" fill="#FFFFFF" stroke="#CBD5E1"/>
  <text x="361" y="662" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E293B" text-anchor="middle">Clone &amp; Restore Request</text>

  <rect x="285" y="731" width="152" height="22" rx="11" fill="#FFFBEB" stroke="#FDBA74"/>
  <text x="361" y="746" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#9A3412" text-anchor="middle">export / import .ova</text>

  <rect x="285" y="831" width="152" height="22" rx="11" fill="#FEF2F2" stroke="#FCA5A5"/>
  <text x="361" y="846" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#991B1B" text-anchor="middle">SMTP &amp; HMAC Webhook</text>

  <!-- Right Labels -->
  <rect x="838" y="131" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="146" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Verify PBKDF2 / Roles</text>

  <rect x="838" y="217" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="232" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Register UUID &amp; Policy</text>

  <rect x="838" y="303" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="318" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Runtime Overrides</text>

  <rect x="838" y="387" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="402" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Record / Prune Snapshots</text>

  <rect x="838" y="467" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="482" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Log Class Session State</text>

  <rect x="838" y="547" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="562" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Audit Incidents &amp; Rollback</text>

  <rect x="838" y="633" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="648" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Store &amp; Fulfill Clones</text>

  <rect x="838" y="731" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="746" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Archive Metadata &amp; Size</text>

  <rect x="838" y="831" width="156" height="22" rx="11" fill="#EFF6FF" stroke="#93C5FD"/>
  <text x="916" y="846" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#1E40AF" text-anchor="middle">Log Dispatch Status</text>

  <!-- ================================================================== -->
  <!-- LAYER 3: EXTERNAL INTERACTORS (Left Column)                        -->
  <!-- ================================================================== -->

  <g transform="translate(30, 120)" filter="url(#shadow1)">
    <rect width="185" height="68" rx="6" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <rect width="185" height="22" rx="6" fill="#334155"/>
    <text x="92" y="15" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="92" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700" fill="#0F172A" text-anchor="middle">Administrator</text>
  </g>

  <g transform="translate(30, 312)" filter="url(#shadow1)">
    <rect width="185" height="68" rx="6" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <rect width="185" height="22" rx="6" fill="#334155"/>
    <text x="92" y="15" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="92" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700" fill="#0F172A" text-anchor="middle">Trainer</text>
  </g>

  <g transform="translate(30, 442)" filter="url(#shadow1)">
    <rect width="185" height="84" rx="6" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
    <rect width="185" height="22" rx="6" fill="#D97706"/>
    <text x="92" y="15" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">HARDWARE HYPERVISOR</text>
    <text x="92" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#78350F" text-anchor="middle">Oracle VirtualBox</text>
    <text x="92" y="68" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#92400E" text-anchor="middle">VBoxManage CLI</text>
  </g>

  <g transform="translate(30, 622)" filter="url(#shadow1)">
    <rect width="185" height="68" rx="6" fill="#F1F5F9" stroke="#334155" stroke-width="2"/>
    <rect width="185" height="22" rx="6" fill="#334155"/>
    <text x="92" y="15" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL ENTITY</text>
    <text x="92" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="13.5" font-weight="700" fill="#0F172A" text-anchor="middle">Student</text>
  </g>

  <g transform="translate(30, 804)" filter="url(#shadow1)">
    <rect width="185" height="76" rx="6" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
    <rect width="185" height="22" rx="6" fill="#DC2626"/>
    <text x="92" y="15" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF" text-anchor="middle">EXTERNAL GATEWAY</text>
    <text x="92" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#991B1B" text-anchor="middle">Alert Gateways</text>
    <text x="92" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#B91C1C" text-anchor="middle">SMTP &amp; Webhooks</text>
  </g>

  <!-- ================================================================== -->
  <!-- LAYER 4: 8 PROCESSES (Center Column)                               -->
  <!-- ================================================================== -->

  <g transform="translate(470, 110)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">1.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">User Authentication &amp;</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">RBAC Role Enforcement</text>
  </g>

  <g transform="translate(470, 210)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">2.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">VM Registry &amp; Policy</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">Configuration Management</text>
  </g>

  <g transform="translate(470, 310)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">3.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Snapshot Automation &amp;</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">Pre-Session Baselines</text>
  </g>

  <g transform="translate(470, 410)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">4.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Guest Heartbeat &amp;</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">State Interrogation Loop</text>
  </g>

  <g transform="translate(470, 510)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">5.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Autonomous Recovery &amp;</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">Debounced Rollback Engine</text>
  </g>

  <g transform="translate(470, 610)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">6.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Student VM Provisioning</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">&amp; Golden Master Cloning</text>
  </g>

  <g transform="translate(470, 710)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">7.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Appliance Backup (.ova)</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">&amp; Database Hot-Backup</text>
  </g>

  <g transform="translate(470, 810)" filter="url(#shadow1)">
    <rect width="290" height="64" rx="12" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="30" cy="32" r="16" fill="#2563EB"/>
    <text x="30" y="37" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#FFFFFF" text-anchor="middle">8.0</text>
    <text x="58" y="28" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#1E3A8A">Multi-Channel Alerting</text>
    <text x="58" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#1D4ED8">&amp; Signed Webhooks</text>
  </g>

  <!-- ================================================================== -->
  <!-- LAYER 5: 9 DATA STORES (Right Column, Gane-Sarson Open-Right)      -->
  <!-- ================================================================== -->

  <g transform="translate(1030, 118)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D1</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">users (Auth &amp; Roles)</text>
  </g>

  <g transform="translate(1030, 204)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D2</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">vms (Hardware Registry)</text>
  </g>

  <g transform="translate(1030, 290)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D8</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">app_settings (Overrides)</text>
  </g>

  <g transform="translate(1030, 376)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D3</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">snapshots (Point-in-Time)</text>
  </g>

  <g transform="translate(1030, 454)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D4</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">class_sessions (Classes)</text>
  </g>

  <g transform="translate(1030, 534)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D6</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">events (Immutable Audit Log)</text>
  </g>

  <g transform="translate(1030, 620)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D5</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">vm_requests (Student Clones)</text>
  </g>

  <g transform="translate(1030, 718)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D7</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">backups (.ova Appliances)</text>
  </g>

  <g transform="translate(1030, 818)">
    <rect x="0" y="0" width="295" height="48" fill="#F8FAFC"/>
    <path d="M 295 0 H 0 V 48 H 295" stroke="#334155" stroke-width="2" fill="none"/>
    <line x1="48" y1="0" x2="48" y2="48" stroke="#334155" stroke-width="1.8"/>
    <text x="24" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="700" fill="#2563EB" text-anchor="middle">D9</text>
    <text x="62" y="29" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="600" fill="#0F172A">notifications (Dispatches)</text>
  </g>

  <!-- Legend Footer -->
  <rect x="30" y="902" width="1295" height="36" rx="6" fill="#F8FAFC" stroke="#CBD5E1"/>
  <text x="678" y="925" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">
    Notation: Gane-Sarson / Yourdon-DeMarco Standard — Rectangles: External Interactors | Rounded Cards: System Processes (1.0–8.0) | Open-Right Boxes: SQLite / Supabase Data Stores (D1–D9)
  </text>
</svg>'''
    with open('Milestones/figures/fig2_3_3b_dfd_level1.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-z', '3.5', 'Milestones/figures/fig2_3_3b_dfd_level1.svg', '-o', 'Milestones/figures/fig2_3_3b_dfd_level1.png'], check=True)
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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig2_3_5_use_case_complete.svg', '-o', 'Milestones/figures/fig2_3_5_use_case_complete.png'], check=True)
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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig2_3_4_erd_complete.svg', '-o', 'Milestones/figures/fig2_3_4_erd_complete.png'], check=True)
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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig2_3_6_class_diagram_complete.svg', '-o', 'Milestones/figures/fig2_3_6_class_diagram_complete.png'], check=True)
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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig3_1_architecture.svg', '-o', 'Milestones/figures/fig3_1_architecture.png'], check=True)
    print("Generated Native SVG: fig3_1_architecture.svg -> PNG (High-Res 300+ DPI)")


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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig3_2_database_wal.svg', '-o', 'Milestones/figures/fig3_2_database_wal.png'], check=True)
    print("Generated Native SVG: fig3_2_database_wal.svg -> PNG (High-Res 300+ DPI)")


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
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig3_6_worker_flowchart.svg', '-o', 'Milestones/figures/fig3_6_worker_flowchart.png'], check=True)
    print("Generated Native SVG: fig3_6_worker_flowchart.svg -> PNG (High-Res 300+ DPI)")


# -------------------------------------------------------------
# 9. Production Deployment Architecture (Figure 4.8) - Native Clean SVG
# -----------------------------------------------------------------------------
def generate_fig3_deployment_architecture_svg():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1350 920" width="100%" height="100%">
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
    <marker id="arrDepIndigo" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#4F46E5"/>
    </marker>
    <marker id="arrDepTeal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#059669"/>
    </marker>
    <marker id="arrDepAmber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#D97706"/>
    </marker>
  </defs>

  <rect width="1350" height="920" fill="#FFFFFF"/>
  <text x="675" y="38" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="20" font-weight="700" fill="#0F172A" text-anchor="middle">Figure 4.8: Hybrid Edge-Cloud Production Deployment Architecture</text>
  <text x="675" y="60" font-family="'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">4-Pillar Architecture: Physical Hypervisor Host, Cloudflare Zero-Trust, Render Cloud PaaS &amp; Supabase Managed PostgreSQL</text>

  <!-- ON-PREMISES HYPERVISOR BOUNDARY (Left) -->
  <rect x="40" y="85" width="620" height="805" rx="12" fill="#F8FAFC" stroke="#1E40AF" stroke-width="2.5"/>
  <rect x="60" y="70" width="480" height="28" rx="4" fill="#1E40AF"/>
  <text x="300" y="89" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="800" fill="#FFFFFF" text-anchor="middle">ON-PREMISES LAB HYPERVISOR HOST (Ubuntu / Bare-Metal Linux Host)</text>

  <!-- Systemd Supervisor -->
  <g transform="translate(70, 115)" filter="url(#depShadow)">
    <rect width="560" height="60" rx="6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.8"/>
    <text x="280" y="24" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E40AF" text-anchor="middle">SYSTEMD SERVICE MANAGER (vmrecovery.service)</text>
    <text x="280" y="42" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Automatic Boot Startup, Restart-on-Failure (RestartSec=5s), StandardOutput=journal</text>
    <text x="280" y="55" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#2563EB" text-anchor="middle">Hardening: NoNewPrivileges=true, ProtectSystem=full, UMask=0077</text>
  </g>

  <!-- Waitress WSGI -->
  <g transform="translate(70, 190)" filter="url(#depShadow)">
    <rect width="560" height="80" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="2"/>
    <rect width="560" height="24" rx="6" fill="#2563EB"/>
    <text x="280" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">WAITRESS MULTI-THREADED WSGI SERVER</text>
    <text x="20" y="46" font-family="'Courier New', monospace" font-size="11" font-weight="700" fill="#1E40AF">Binding: http://127.0.0.1:5000 (Production threads=8)</text>
    <text x="20" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" fill="#475569">Handles simultaneous trainer sessions, student self-service provisioning, and REST API calls</text>
  </g>

  <!-- Middle Row: Worker & SQLite -->
  <g transform="translate(70, 285)" filter="url(#depShadow)">
    <rect width="265" height="145" rx="6" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.8"/>
    <rect width="265" height="24" rx="6" fill="#EA580C"/>
    <text x="132" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">BACKGROUND WORKER</text>
    <text x="12" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#9A3412">app/worker.py</text>
    <text x="12" y="68" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• 10s Continuous Polling</text>
    <text x="12" y="86" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Zero-Touch Auto-Healing</text>
    <text x="12" y="104" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Hourly Online Database Backup</text>
    <text x="12" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Automatic Retention Pruning</text>
    <text x="12" y="138" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#EA580C">• 2-Cycle Failure Debouncing</text>
  </g>

  <g transform="translate(365, 285)" filter="url(#depShadow)">
    <rect width="265" height="145" rx="6" fill="#FEFCE8" stroke="#CA8A04" stroke-width="1.8"/>
    <rect width="265" height="24" rx="6" fill="#CA8A04"/>
    <text x="132" y="17" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">SQLITE 3 DATABASE (WAL)</text>
    <text x="12" y="48" font-family="'Courier New', monospace" font-size="10.5" font-weight="700" fill="#854D0E">instance/vmrecovery.db</text>
    <text x="12" y="68" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• WAL Concurrency Journal</text>
    <text x="12" y="86" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• 8 Sequential Migrations</text>
    <text x="12" y="104" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Atomic Transaction Logs</text>
    <text x="12" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Hot Backup Storage (backups/)</text>
    <text x="12" y="138" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" fill="#A16207">• PRAGMA busy_timeout=15000</text>
  </g>

  <!-- Bottom: VirtualBox & Physical Machines -->
  <g transform="translate(70, 445)" filter="url(#depShadow)">
    <rect width="560" height="215" rx="8" fill="#FFFBEB" stroke="#D97706" stroke-width="2"/>
    <rect width="560" height="26" rx="8" fill="#D97706"/>
    <text x="280" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">ORACLE VIRTUALBOX 7.2 HYPERVISOR (VBoxManage)</text>
    <text x="20" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#78350F">Hardware Virtualization &amp; Differential Storage Control</text>
    <text x="20" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Fast Differencing Snapshots (&lt;10s Rollback) &amp; Golden Master Linked Clones</text>
    <text x="20" y="84" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Guest Property Heartbeat Telemetry &amp; Headless Process Execution</text>
    <text x="20" y="102" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Independent Appliance Export Engine (.ova compressed standalone packages)</text>

    <!-- Lab VMs Sub-boxes -->
    <rect x="20" y="115" width="115" height="85" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="77" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">debian</text>
    <text x="77" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Linux Server</text>
    <text x="77" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH Port 22</text>
    <text x="77" y="188" font-family="'Segoe UI', Roboto, sans-serif" font-size="8.5" fill="#475569" text-anchor="middle">Running (Active)</text>

    <rect x="155" y="115" width="115" height="85" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="212" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">LAB-CS-001</text>
    <text x="212" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Student Node 1</text>
    <text x="212" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH / VRDP</text>
    <text x="212" y="188" font-family="'Segoe UI', Roboto, sans-serif" font-size="8.5" fill="#475569" text-anchor="middle">Session Active</text>

    <rect x="290" y="115" width="115" height="85" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="347" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">LAB-CS-002</text>
    <text x="347" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Student Node 2</text>
    <text x="347" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">SSH / VRDP</text>
    <text x="347" y="188" font-family="'Segoe UI', Roboto, sans-serif" font-size="8.5" fill="#475569" text-anchor="middle">Auto-Protected</text>

    <rect x="425" y="115" width="115" height="85" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>
    <text x="482" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#0F172A" text-anchor="middle">agnes</text>
    <text x="482" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" fill="#64748B" text-anchor="middle">Lab Workstation</text>
    <text x="482" y="170" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#16A34A" text-anchor="middle">VRDP Port 3389</text>
    <text x="482" y="188" font-family="'Segoe UI', Roboto, sans-serif" font-size="8.5" fill="#475569" text-anchor="middle">Guest Telemetry</text>
  </g>

  <!-- Local Network Footnote -->
  <text x="350" y="682" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="600" fill="#1E40AF" text-anchor="middle">Local Area Network (LAN): Direct Student Access via SSH (22) &amp; VRDP (3389)</text>

  <!-- RIGHT COLUMN: 4 PILLARS & STAKEHOLDERS -->

  <!-- PILLAR 1: CLOUDFLARE ZERO-TRUST EDGE (Right Top) -->
  <g transform="translate(700, 85)" filter="url(#depShadow)">
    <rect width="610" height="120" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>
    <rect width="610" height="26" rx="8" fill="#EA580C"/>
    <text x="305" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">PILLAR 1: CLOUDFLARE ZERO-TRUST EDGE INGRESS (cloudflared)</text>
    <text x="18" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#C2410C">• Outbound Encrypted TLS Tunnel (No open router inbound ports / Zero NAT punching)</text>
    <text x="18" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Automated Wildcard SSL/TLS Certificate Termination with Edge CDN Caching</text>
    <text x="18" y="82" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Built-in DDoS Defense, Web Application Firewall (WAF) &amp; Secure Host Ingress</text>
    <text x="18" y="100" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#64748B">Enables University Staff &amp; Students to access on-premise dashboard remotely with zero router ports</text>
  </g>

  <!-- PILLAR 2: RENDER PAAS PUBLIC CLOUD APPLICATION -->
  <g transform="translate(700, 220)" filter="url(#depShadow)">
    <rect width="610" height="135" rx="8" fill="#EEF2FF" stroke="#4F46E5" stroke-width="2"/>
    <rect width="610" height="26" rx="8" fill="#4F46E5"/>
    <text x="305" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">PILLAR 2: RENDER PAAS CLOUD APPLICATION (vmrecovery-demo.onrender.com)</text>
    <text x="18" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#4338CA">• Public Cloud Live App: <tspan font-family="'Courier New', monospace" font-size="10.5">https://vmrecovery-demo.onrender.com</tspan></text>
    <text x="18" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Continuous Deployment CI/CD: Automated deployment directly from GitHub repository main branch</text>
    <text x="18" y="82" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Hypervisor Simulation Engine (VMRECOVERY_SIMULATED=true) for non-bare-metal cloud environments</text>
    <text x="18" y="100" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Multi-threaded Waitress WSGI server with continuous /healthz monitoring</text>
    <text x="18" y="118" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-style="italic" fill="#6366F1">Allows Examiners &amp; External Reviewers to test live platform anytime with zero hardware setup</text>
  </g>

  <!-- PILLAR 3: SUPABASE MANAGED POSTGRESQL DATABASE -->
  <g transform="translate(700, 370)" filter="url(#depShadow)">
    <rect width="610" height="135" rx="8" fill="#ECFDF5" stroke="#059669" stroke-width="2"/>
    <rect width="610" height="26" rx="8" fill="#059669"/>
    <text x="305" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">PILLAR 3: SUPABASE MANAGED CLOUD POSTGRESQL DATABASE</text>
    <text x="18" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#047857">• Dedicated Supabase PostgreSQL Instance: <tspan font-family="'Courier New', monospace" font-size="10">aws-0-eu-central-1.pooler.supabase.com:5432</tspan></text>
    <text x="18" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Automated Schema Migration Engine: Automatically provisioned tables on first startup (app/pg_db.py)</text>
    <text x="18" y="82" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Dual-Database Architecture: Native SQLite (Local host) &amp; PostgreSQL (Cloud Render deployment)</text>
    <text x="18" y="100" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• High Availability &amp; Point-in-time Recovery with TLS-encrypted connection pooling</text>
    <text x="18" y="118" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-style="italic" fill="#059669">Enterprise managed cloud persistence with zero host maintenance overhead</text>
  </g>

  <!-- PILLAR 4: INDEPENDENT APPLIANCE (.OVA) DISASTER RECOVERY & BACKUPS -->
  <g transform="translate(700, 520)" filter="url(#depShadow)">
    <rect width="610" height="135" rx="8" fill="#FFFBEB" stroke="#D97706" stroke-width="2"/>
    <rect width="610" height="26" rx="8" fill="#D97706"/>
    <text x="305" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">PILLAR 4: INDEPENDENT APPLIANCE (.OVA) DISASTER RECOVERY &amp; BACKUPS</text>
    <text x="18" y="46" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#B45309">• Open Virtualization Appliance (.ova) Standalone Portable Archives</text>
    <text x="18" y="64" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Hourly SQLite Online Hot Backups with SHA-256 integrity verification (backups/ directory)</text>
    <text x="18" y="82" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Automatic 7-day backup retention pruning policy managed by background worker</text>
    <text x="18" y="100" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#334155">• Zero-Dependency Hardware Portability: Fast import into any VirtualBox / VMware host</text>
    <text x="18" y="118" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-style="italic" fill="#D97706">Guarantees total system restoration even during catastrophic hardware or network failures</text>
  </g>

  <!-- UNIVERSITY STAKEHOLDERS (Right Bottom) -->
  <g transform="translate(700, 670)" filter="url(#depShadow)">
    <rect width="610" height="220" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>
    <rect width="610" height="26" rx="8" fill="#475569"/>
    <text x="305" y="18" font-family="'Segoe UI', Roboto, sans-serif" font-size="11.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">UNIVERSITY STAKEHOLDERS &amp; LAB CLIENTS</text>
    <text x="18" y="48" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#1E293B">1. Dashboard Management Access (Examiners, Admins, Trainers &amp; Students via Web HTTPS):</text>
    <text x="32" y="66" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">• Local Host: http://127.0.0.1:5000 (Waitress WSGI)</text>
    <text x="32" y="84" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#EA580C">• Cloudflare Ingress: https://vmrecovery.lab.domain (Encrypted Edge Tunnel)</text>
    <text x="32" y="102" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#4F46E5">• Live Cloud Demo: https://vmrecovery-demo.onrender.com (Render + Supabase PostgreSQL)</text>
    <text x="18" y="126" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#166534">2. Guest Operating System Access (Hands-on Technical Training):</text>
    <text x="32" y="144" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#475569">Students connect directly from laboratory workstations across campus LAN</text>
    <text x="32" y="162" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#166534">• SSH (Port 22) for Linux terminal administration and scripting</text>
    <text x="32" y="180" font-family="'Segoe UI', Roboto, sans-serif" font-size="10.5" fill="#166534">• RDP / VRDP (Port 3389) for interactive graphical desktop environments</text>
    <text x="18" y="202" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" font-style="italic" fill="#64748B">Instant snapshot rollback resets guest machine state without disrupting network configurations</text>
  </g>

  <!-- Connectors -->
  <path d="M 630 220 L 700 145" fill="none" stroke="#EA580C" stroke-width="2.2" marker-end="url(#arrDepOrange)"/>
  <path d="M 630 240 L 700 280" fill="none" stroke="#4F46E5" stroke-width="2.2" stroke-dasharray="5,4" marker-end="url(#arrDepIndigo)"/>
  <path d="M 630 350 L 700 435" fill="none" stroke="#059669" stroke-width="2.2" stroke-dasharray="5,4" marker-end="url(#arrDepTeal)"/>
  <path d="M 630 550 L 700 585" fill="none" stroke="#D97706" stroke-width="2.2" marker-end="url(#arrDepAmber)"/>
  <path d="M 350 430 L 700 780" fill="none" stroke="#166534" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrDep)"/>
  <path d="M 1005 205 L 1005 220" fill="none" stroke="#4F46E5" stroke-width="1.8" marker-end="url(#arrDepIndigo)"/>
  <path d="M 1005 355 L 1005 370" fill="none" stroke="#059669" stroke-width="1.8" marker-end="url(#arrDepTeal)"/>
  <path d="M 1005 505 L 1005 520" fill="none" stroke="#D97706" stroke-width="1.8" marker-end="url(#arrDepAmber)"/>
  <path d="M 1005 655 L 1005 670" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrDepBlue)"/>
</svg>'''
    with open('Milestones/figures/fig3_deployment_architecture.svg', 'w') as f:
        f.write(svg)
    subprocess.run(['rsvg-convert', '-z', '2.5', 'Milestones/figures/fig3_deployment_architecture.svg', '-o', 'Milestones/figures/fig3_deployment_architecture.png'], check=True)
    print("Generated Native SVG: fig3_deployment_architecture.svg -> PNG (High-Res 300+ DPI)")

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
