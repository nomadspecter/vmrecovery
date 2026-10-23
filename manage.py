"""Command-line admin tasks.

    python manage.py create-user alice admin
    python manage.py list-vms
    python manage.py check                 # run one monitoring cycle now
    python manage.py start-session "Class A"
    python manage.py backup-db
    python manage.py set-setting check_seconds 45

Every command works against the same database and configuration as the web
service, so it can be used on a machine where the dashboard is not reachable.
"""
import argparse
import getpass
import os
import sqlite3
import sys

from werkzeug.security import generate_password_hash

from app import db, services
from app.config import Settings


def ask_password(prompt="Password (min 8 characters): ") -> str:
    while True:
        pw = getpass.getpass(prompt)
        if len(pw) < 8:
            print("Too short.")
            continue
        if pw != getpass.getpass("Repeat password: "):
            print("Passwords do not match.")
            continue
        return pw


def password_from(args) -> str:
    """Use the supplied password, or ask for one."""
    if getattr(args, "password", None):
        if len(args.password) < 8:
            raise SystemExit("The password must be at least 8 characters long.")
        return args.password
    return ask_password()


def main() -> int:
    parser = argparse.ArgumentParser(description="VM Recovery System admin tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db", help="create or upgrade the database tables")

    cu = sub.add_parser("create-user", help="add a user")
    cu.add_argument("username")
    cu.add_argument("role", choices=["admin", "trainer", "student"])
    cu.add_argument("--password", help="use this password instead of asking (8+ characters)")

    rp = sub.add_parser("reset-password", help="change a user's password")
    rp.add_argument("username")
    rp.add_argument("--password", help="use this password instead of asking (8+ characters)")

    du = sub.add_parser("delete-user", help="remove a user account")
    du.add_argument("username")

    sr = sub.add_parser("set-role", help="change a user's role")
    sr.add_argument("username")
    sr.add_argument("role", choices=["admin", "trainer", "student"])

    sub.add_parser("list-users", help="show all users")
    sub.add_parser("list-vms", help="show the registered virtual machines")
    sub.add_parser("list-settings", help="show the runtime overrides and their sources")

    ss = sub.add_parser("set-setting", help="change a runtime setting")
    ss.add_argument("key")
    ss.add_argument("value")

    sr2 = sub.add_parser("reset-setting", help="drop a runtime override")
    sr2.add_argument("key")

    sub.add_parser("check", help="run one monitoring cycle right now")

    sn = sub.add_parser("snapshot", help="take a snapshot of a machine")
    sn.add_argument("vm", help="machine name or UUID")

    rs = sub.add_parser("restore", help="restore a machine to its newest snapshot")
    rs.add_argument("vm", help="machine name or UUID")

    ssess = sub.add_parser("start-session", help="start a training session for a class group")
    ssess.add_argument("class_group")

    esess = sub.add_parser("end-session", help="end the training session for a class group")
    esess.add_argument("class_group")
    esess.add_argument("--no-power-off", action="store_true",
                       help="leave the machines running")

    bd = sub.add_parser("backup-db", help="back up the application database")
    bd.add_argument("--list", action="store_true", help="list existing backups instead")

    rd = sub.add_parser("restore-db", help="restore the application database from a backup")
    rd.add_argument("path")

    ex = sub.add_parser("export-events", help="write the event log to a CSV file")
    ex.add_argument("path")
    ex.add_argument("--days", type=int, default=0, help="only the last N days (0 = everything)")

    st = sub.add_parser("status", help="show the current state of the system")

    args = parser.parse_args()

    settings = Settings.from_env()
    version = db.init_db(settings.db_path)
    conn = db.connect(settings.db_path)
    services.set_runtime_settings(settings)

    try:
        return dispatch(args, settings, conn, version)
    finally:
        conn.close()


def dispatch(args, settings, conn, version) -> int:
    cmd = args.cmd

    if cmd == "init-db":
        print(f"Database ready at {settings.db_path} (schema version {version}).")

    elif cmd == "create-user":
        try:
            conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                         (args.username, generate_password_hash(password_from(args)), args.role))
            conn.commit()
            print(f"Created {args.role} '{args.username}'.")
        except sqlite3.IntegrityError:
            print("That username already exists.")
            return 1

    elif cmd == "reset-password":
        cur = conn.execute("UPDATE users SET password_hash=? WHERE username=?",
                           (generate_password_hash(password_from(args)), args.username))
        conn.commit()
        print("Password changed." if cur.rowcount else "No such user.")
        return 0 if cur.rowcount else 1

    elif cmd == "delete-user":
        row = conn.execute("SELECT * FROM users WHERE username=?", (args.username,)).fetchone()
        if not row:
            print("No such user.")
            return 1
        services.delete_user(conn, row["user_id"])
        print(f"Deleted user '{args.username}'.")

    elif cmd == "set-role":
        row = conn.execute("SELECT * FROM users WHERE username=?", (args.username,)).fetchone()
        if not row:
            print("No such user.")
            return 1
        if row["role"] == "admin" and args.role != "admin":
            admins = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='admin'").fetchone()["c"]
            if admins <= 1:
                print("Cannot remove the only administrator account.")
                return 1
        conn.execute("UPDATE users SET role=? WHERE username=?", (args.role, args.username))
        conn.commit()
        services.log_event(conn, "user_role_changed", None, None,
                           f"{args.username} is now {args.role}", "Success")
        print(f"'{args.username}' is now {args.role}.")

    elif cmd == "list-users":
        for row in services.list_users(conn):
            print(f"{row['username']:24} {row['role']:10} {row['assigned_vm_count']} VM(s)")

    elif cmd == "list-vms":
        for row in services.list_vms(conn):
            print(f"{row['vm_id']:>4}  {row['vm_name']:24} {row['status']:14} "
                  f"{row['class_group']:16} {row['student_username'] or '-'}")

    elif cmd == "list-settings":
        overrides = services.all_overrides(conn)
        print("Runtime overrides (these win over the environment):")
        if not overrides:
            print("  (none)")
        for key, value in sorted(overrides.items()):
            print(f"  {key:28} = {value}")
        print("\nEffective values:")
        for key in sorted(services.SETTING_TYPES):
            print(f"  {key:28} = {getattr(settings, key, '')}")

    elif cmd == "set-setting":
        try:
            services.set_override(conn, args.key, args.value)
        except ValueError as exc:
            print(str(exc))
            return 1
        services.apply_overrides(conn, settings)
        print(f"{args.key} = {args.value} (live).")

    elif cmd == "reset-setting":
        try:
            services.clear_override(conn, args.key)
        except ValueError as exc:
            print(str(exc))
            return 1
        services.apply_overrides(conn, settings)
        print(f"{args.key} reset to the configured default.")

    elif cmd == "check":
        from app.vbox import make_vbox
        vbox = make_vbox(settings)
        summary = services.run_cycle(conn, vbox, settings)
        print(f"Cycle complete: {summary}")

    elif cmd in ("snapshot", "restore"):
        from app.vbox import make_vbox
        vm = conn.execute("SELECT * FROM vms WHERE vm_name=? OR vbox_uuid=?",
                          (args.vm, args.vm)).fetchone()
        if not vm:
            print("No such virtual machine.")
            return 1
        vbox = make_vbox(settings)
        full = services.get_vm(conn, vm["vm_id"])
        if cmd == "snapshot":
            name = services.take_snapshot(conn, vbox, full, "manual")
            print(f"Snapshot {name} taken." if name else "The snapshot failed; see the event log.")
            return 0 if name else 1
        ok = services.recover(conn, vbox, full)
        print("Machine restored." if ok else "The restore failed; see the event log.")
        return 0 if ok else 1

    elif cmd in ("start-session", "end-session"):
        from app.vbox import make_vbox
        vbox = make_vbox(settings)
        if cmd == "start-session":
            result = services.start_session(conn, vbox, args.class_group)
            print(f"Session for {args.class_group}: {result['started']} started, "
                  f"{result['already_running']} already running, "
                  f"{result['snapshots']} snapshot(s) taken.")
        else:
            result = services.end_session(conn, vbox, args.class_group,
                                          power_off=not args.no_power_off)
            print(f"Session ended: {result['snapshots']} post-session snapshot(s), "
                  f"{result['powered_off']} VM(s) powered off.")
        for name, err in result.get("failed", []):
            print(f"  failed: {name}: {err}")
        return 1 if result.get("failed") else 0

    elif cmd == "backup-db":
        if args.list:
            out_dir = settings.db_backup_dir
            if os.path.isdir(out_dir):
                for name in sorted(os.listdir(out_dir)):
                    if name.endswith(".db"):
                        size = os.path.getsize(os.path.join(out_dir, name))
                        print(f"  {name}  {size / (1024 * 1024):.1f} MB")
            else:
                print(f"No backup directory at {out_dir}.")
            return 0
        path = db.backup_database(settings.db_path, settings.db_backup_dir,
                                  settings.db_backup_keep)
        print(f"Database backed up to {path}")

    elif cmd == "restore-db":
        try:
            db.restore_database(settings.db_path, args.path)
        except FileNotFoundError as exc:
            print(str(exc))
            return 1
        print(f"Database restored from {args.path}. Restart the service to use it.")

    elif cmd == "export-events":
        import csv
        since = None
        if args.days:
            from datetime import timedelta
            since = services.ts(services.now_local() - timedelta(days=args.days))
        rows = services.list_events(conn, limit=1_000_000)
        with open(args.path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["event_id", "created_at", "event_type", "vm", "details", "result",
                             "duration_seconds", "user"])
            for r in rows:
                if since and r["created_at"] < since:
                    continue
                writer.writerow([r["event_id"], r["created_at"], r["event_type"],
                                 r["vm_name"] or "", r["details"], r["result"],
                                 r["duration_seconds"] or "", r["username"] or "system"])
        print(f"Wrote {args.path}")

    elif cmd == "status":
        print(f"Database        : {settings.db_path}")
        print(f"Schema version  : {version}")
        print(f"VirtualBox      : {settings.vboxmanage}")
        print(f"Worker          : {'enabled' if settings.run_worker else 'disabled'}")
        print(f"Check interval  : {settings.check_seconds}s")
        print(f"Simulation      : {'on' if settings.simulate else 'off'}")
        vms = services.list_vms(conn)
        print(f"Registered VMs  : {len(vms)}")
        for row in vms:
            print(f"  {row['vm_name']:24} {row['status']}")
        pending = conn.execute("SELECT COUNT(*) AS n FROM vm_requests WHERE status='pending'").fetchone()["n"]
        print(f"Pending requests: {pending}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
