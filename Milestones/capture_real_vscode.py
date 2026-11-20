"""Capture 100% genuine screenshots directly from the user's running VS Code (code-oss)
window on Hyprland using `code --reuse-window --goto` and `grim`.
"""
import json
import os
import subprocess
import time

REPO = "/home/nomad/vmrecovery"
TARGETS = [
    ("code_3_3_db_wal.png",        "app/db.py",                 36),
    ("code_3_4_auth.png",          "app/views.py",             171),
    ("code_3_5_vbox.png",          "app/vbox.py",               78),
    ("code_3_6_worker.png",        "app/worker.py",             56),
    ("code_4_1_snapshot.png",      "app/services.py",          462),
    ("code_4_2_recovery.png",      "app/services.py",         1354),
    ("code_4_3_backup.png",        "app/services.py",          736),
    ("code_4_4_provisioning.png",  "app/services.py",         1095),
    ("code_4_5_notifier.png",      "app/notifier.py",          112),
    ("code_4_6_api.png",           "app/api.py",                44),
    ("code_4_11_systemd.png",      "deploy/vmrecovery.service", 15),
    ("code_4_13_supabase_pg.png",  "app/pg_db.py",             198),
]


def get_json(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def find_vscode_client():
    for c in get_json(["hyprctl", "clients", "-j"]):
        if "code" in c.get("class", "").lower():
            return c
    raise RuntimeError("No running VS Code (code-oss) window found in Hyprland.")


def main():
    orig_ws = get_json(["hyprctl", "activeworkspace", "-j"])["id"]
    client = find_vscode_client()
    vs_ws = client["workspace"]["id"]
    x, y = client["at"]
    w, h = client["size"]
    geom = f"{x},{y} {w}x{h}"
    print(f"Found VS Code ({client['class']}) on workspace {vs_ws}, geom={geom} (original ws={orig_ws})")

    os.makedirs("Milestones/figures", exist_ok=True)
    subprocess.run(["hyprctl", "dispatch", f'hl.dsp.focus({{ workspace = "{vs_ws}" }})'], check=True, stdout=subprocess.DEVNULL)
    time.sleep(0.6)

    try:
        for out_name, rel_path, line_no in TARGETS:
            abs_path = os.path.join(REPO, rel_path)
            subprocess.run(
                ["code", "--reuse-window", "--goto", f"{abs_path}:{line_no}:1"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.1)
            out_path = os.path.join("Milestones/figures", out_name)
            subprocess.run(["grim", "-g", geom, out_path], check=True)
            print(f"  -> Captured REAL VS Code screenshot: {out_path} ({rel_path}:{line_no})")
    finally:
        subprocess.run(["hyprctl", "dispatch", f'hl.dsp.focus({{ workspace = "{orig_ws}" }})'], check=False, stdout=subprocess.DEVNULL)
        print(f"Restored original workspace {orig_ws}.")


if __name__ == "__main__":
    main()
