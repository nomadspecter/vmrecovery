"""Command-line admin tasks:  python manage.py create-user alice admin"""
import argparse
import getpass
import sqlite3
import sys

from werkzeug.security import generate_password_hash

from app import db
from app.config import Settings


def ask_password() -> str:
    while True:
        pw = getpass.getpass("Password (min 8 characters): ")
        if len(pw) < 8:
            print("Too short.")
            continue
        if pw != getpass.getpass("Repeat password: "):
            print("Passwords do not match.")
            continue
        return pw


def main() -> int:
    parser = argparse.ArgumentParser(description="VM Recovery System admin tool")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db", help="create the database tables")
    cu = sub.add_parser("create-user", help="add a user")
    cu.add_argument("username")
    cu.add_argument("role", choices=["admin", "trainer", "student"])
    rp = sub.add_parser("reset-password", help="change a user's password")
    rp.add_argument("username")
    sub.add_parser("list-users", help="show all users")
    args = parser.parse_args()

    settings = Settings.from_env()
    db.init_db(settings.db_path)
    conn = db.connect(settings.db_path)

    if args.cmd == "init-db":
        print(f"Database ready at {settings.db_path}")
    elif args.cmd == "create-user":
        try:
            conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                         (args.username, generate_password_hash(ask_password()), args.role))
            conn.commit()
            print(f"Created {args.role} '{args.username}'.")
        except sqlite3.IntegrityError:
            print("That username already exists.")
            return 1
    elif args.cmd == "reset-password":
        cur = conn.execute("UPDATE users SET password_hash=? WHERE username=?",
                           (generate_password_hash(ask_password()), args.username))
        conn.commit()
        print("Password changed." if cur.rowcount else "No such user.")
        return 0 if cur.rowcount else 1
    elif args.cmd == "list-users":
        for row in conn.execute("SELECT username, role FROM users ORDER BY username"):
            print(f"{row['username']:20} {row['role']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
