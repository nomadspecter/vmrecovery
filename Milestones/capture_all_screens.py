import os
import time
import sqlite3
from playwright.sync_api import sync_playwright

def capture():
    os.makedirs('Milestones/figures', exist_ok=True)
    
    # Get first VM with snapshots
    conn = sqlite3.connect('instance/vmrecovery.db')
    row = conn.execute("SELECT vm_id FROM snapshots LIMIT 1").fetchone()
    vm_id = row[0] if row else 4
    conn.close()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/opt/google/chrome/chrome',
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 820},
            device_scale_factor=2
        )
        page = context.new_page()

        print("1. Capturing Login Page...")
        page.goto('http://127.0.0.1:5000/login')
        page.wait_for_selector('input[name="username"]')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_login.png')

        print("Logging in as admin...")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin123')
        page.click('button[type="submit"]')
        page.wait_for_selector('nav.side')
        time.sleep(0.5)

        print("2. Capturing Dashboard...")
        page.screenshot(path='Milestones/figures/screen_dashboard.png')

        print("3. Capturing Virtual Machines Registry...")
        page.goto('http://127.0.0.1:5000/vms')
        page.wait_for_selector('table')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_vms.png')

        print(f"4. Capturing Snapshots Page (VM {vm_id})...")
        page.goto(f'http://127.0.0.1:5000/vms/{vm_id}/snapshots')
        page.wait_for_selector('table')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_snapshots.png')

        print("5. Capturing Event Log...")
        page.goto('http://127.0.0.1:5000/events')
        page.wait_for_selector('table')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_events.png')

        print("6. Capturing Reports Page...")
        page.goto('http://127.0.0.1:5000/reports')
        page.wait_for_selector('.cards')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_reports.png')

        print("7. Capturing Provisioning Requests Page...")
        page.goto('http://127.0.0.1:5000/requests')
        page.wait_for_selector('table')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_requests.png')

        print("8. Capturing System Health Page...")
        page.goto('http://127.0.0.1:5000/system')
        page.wait_for_selector('.panel')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_system.png')

        # Log out
        print("Logging out...")
        page.click('nav.side form button[type="submit"]')
        page.wait_for_selector('input[name="username"]')
        time.sleep(0.5)

        print("Logging in as student...")
        page.fill('input[name="username"]', 'student')
        page.fill('input[name="password"]', 'student123')
        page.click('button[type="submit"]')
        page.wait_for_selector('nav.side')
        time.sleep(0.5)

        print("9. Capturing Student Workstation Dashboard...")
        page.screenshot(path='Milestones/figures/screen_student_dashboard.png')

        print("10. Capturing Student VM Requests...")
        page.goto('http://127.0.0.1:5000/requests')
        page.wait_for_selector('table')
        time.sleep(0.5)
        page.screenshot(path='Milestones/figures/screen_student_requests.png')

        browser.close()
        print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == '__main__':
    capture()
