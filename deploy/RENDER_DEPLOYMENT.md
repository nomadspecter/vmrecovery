# Deploying VMRecovery to Render (Simulated Cloud Mode)

This guide explains how to deploy the **Virtual Machine Recovery System (VMRecovery)** to [Render.com](https://render.com) using its free tier.

Because Render containers run in cloud sandboxes without bare-metal hypervisor access (Intel VT-x / AMD-V), the application is configured to run in **Simulated Hypervisor Mode (`VMR_SIMULATE=true`)**. In this mode:
- All core features (autonomous recovery, debouncing, snapshot policies, student self-service provisioning, user authentication) operate live.
- Five virtual training machines (`DEV-LAB-01`, `DEV-LAB-02`, `NET-LAB-03`, `NET-LAB-04`, `SEC-LAB-05`) are simulated in memory.
- Examiners, supervisors, and students can access the live public URL from any browser or smartphone.

---

## Quick 3-Step Deployment via Render Dashboard

### Step 1: Push Code to GitHub
Ensure your repository is pushed to your GitHub account:
```bash
git add .
git commit -m "Configure Render cloud deployment in simulated mode"
git push origin main
```

### Step 2: Create a Web Service on Render
1. Log in to your free account at [https://dashboard.render.com](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository (`vmrecovery`).
4. Set the following deployment parameters:
   - **Name:** `vmrecovery` (or `vmrecovery-demo`)
   - **Region:** Frankfurt (EU) or Oregon (US)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
   - **Instance Type:** `Free`

### Step 3: Add Environment Variables
Under the **Environment Variables** section on Render, add:

| Key | Value | Purpose |
| :--- | :--- | :--- |
| `VMR_SIMULATE` | `true` | Enables simulated VirtualBox for cloud hosting |
| `VMR_WORKER` | `true` | Runs the 10-second background self-healing daemon |
| `PYTHON_VERSION` | `3.11.9` | Sets the Python runtime version |
| `DATABASE_URL` | `postgresql://postgres...` | **Supabase PostgreSQL Connection URI** (see below) |

Click **Create Web Service**. Render will install dependencies and launch your application!

---

## Connecting Supabase PostgreSQL

To persist users, VM records, and recovery metrics permanently across Render restarts:

1. In your **Supabase Dashboard**, click the green **Connect** button at the top (or go to **Project Settings > Database > Connection String**).
2. Choose **URI** under **Connection Pooling** (Port 6543) or **Direct** (Port 5432).
3. Copy the URI string:
   ```text
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
   ```
4. Replace `[YOUR-PASSWORD]` with the database password you chose during Supabase project creation.
5. In Render's **Environment Variables**, paste this string into `DATABASE_URL`.
6. On startup, the application detects the PostgreSQL connection, automatically creates all necessary tables using [`app/schema_pg.sql`](file:///home/nomad/vmrecovery/app/schema_pg.sql), and seeds the initial admin and demo data.

---

## Default Seed Credentials (On Fresh Deploy)

When the application boots for the first time in simulated mode, it automatically initializes the database and creates these default accounts:

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin1234!` | Full system management, VM registry, failure simulations |
| **Course Trainer** | `trainer` | `Trainer1234!` | Class session management, pre-session snapshot triggers |
| **Student** | `student` | `Student1234!` | Personal assigned VM dashboard, self-service VM requests |

*Note: New students can also click **"Register as Student"** on the login page to create personal accounts directly.*

---

## How to Illustrate VM Failures & Autonomous Recovery on Render

1. Log in as `admin` (`Admin1234!`).
2. On the **Dashboard**, locate any active VM (e.g., `DEV-LAB-01`).
3. Under the **Actions** column, click **Sim. crash** (abrupt crash) or **Sim. freeze** (hung guest kernel).
4. Watch the demonstration:
   - **Immediate State:** VM status turns red (**Crashed**) or yellow (**Frozen**).
   - **Debouncing:** The fault counter displays `Debounce: 1/2` on the next 10-second check.
   - **Rollback:** Once confirmed (cycle 2), the daemon automatically rolls back the VM to its clean baseline snapshot and headlessly restarts it.
   - **Restored:** VM status returns to green (**Running**) with `Debounce: 0`.
   - **Audit Trail:** Check the **Event Log** to see the full MTTR (Mean Time to Recover) duration logged in seconds.
