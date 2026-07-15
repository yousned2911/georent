# Rent Pro v1.0 RC1 — Frappe Cloud Deployment Guide

**Date:** 2026-07-15  
**App Version:** 1.0.0-rc1

---

## Prerequisites

- A **Frappe Cloud** account ([dashboard.frappe.cloud](https://dashboard.frappe.cloud))
- A **GitHub** account with access to the Rent Pro repository
- A verified Frappe Cloud SSH key linked to your GitHub account (Settings → SSH Keys on Frappe Cloud)

---

## Step 1: Create a New Frappe Cloud Site

1. Log in to [dashboard.frappe.cloud](https://dashboard.frappe.cloud).
2. Click **"New Site"**.
3. Choose a **site name** (e.g., `rentpro-demo.frappe.cloud`).
4. Select the **database plan** appropriate for your workload (Basic is fine for a demo).
5. Click **"Create Site"** and wait for the initial provisioning to finish.

---

## Step 2: Select Frappe Framework v15 and ERPNext v15

1. From the site dashboard, navigate to **"App"**.
2. Under **Frappe Framework**, select version **v15**.
3. Under **ERPNext**, select version **v15**.
4. Click **"Install"** for both apps and confirm.

> **Note:** Frappe v15 and ERPNext v15 are the minimum supported versions for Rent Pro v1.0 RC1.

---

## Step 3: Connect GitHub Repository

1. Go to **Settings → SSH/Git Access** on the Frappe Cloud dashboard.
2. Add your **GitHub repository URL** (e.g., `git@github.com:your-org/rent_pro.git`).
3. Ensure the **branch** is set to the release tag or commit for v1.0 RC1.
4. Verify the connection by clicking **"Test"** — a green checkmark confirms success.

---

## Step 4: Install Rent Pro App

1. On your site's dashboard, navigate to **"App" → "Install from Git"**.
2. Enter the repository details:
   - **Repository URL:** `git@github.com:your-org/rent_pro.git`
   - **Branch/Tag:** `v1.0.0-rc1` (or the appropriate branch)
3. Click **"Install"**.
4. Wait for the app to be cloned and installed. The status will change to **"Installed"** once complete.

---

## Step 5: Run Migrations

1. From the site dashboard, go to **"Actions" → "Run Bench Migrate"**.
2. Confirm the migration prompt.
3. Monitor the logs — all migrations should complete without errors.
4. If any migration fails, check the error log and resolve before proceeding.

> **Tip:** You can also trigger migrations via SSH:
> ```bash
> bench --site your-site.frappe.cloud migrate
> ```

---

## Step 6: Configure Site via UI (Rent Pro Settings)

1. Log in to your site as **Administrator**.
2. Search for **"Rent Pro Settings"** in the awesome bar.
3. Open **Rent Pro Settings** and configure the following:
   - **Company** — Select or create the default company.
   - **Currency** — Set the operating currency.
   - **Default Rent Agreement Template** — Upload or select a template.
   - **Payment Gateway** — Configure if online payments are required.
   - **Notification Preferences** — Set email/SMS notification defaults.
4. Click **"Save"**.

---

## Step 7: Verify Deployment

Perform the following checks to confirm a healthy deployment:

| # | Check | Expected Result |
|---|-------|-----------------|
| 1 | **Doctypes exist** — Search for "Rent Agreement", "Rent Invoice", "Tenant" in the awesome bar. | All doctypes are listed and open without error. |
| 2 | **Scheduler active** — Go to **Settings → System Info** and verify the scheduler status. | Scheduler shows as **"Active"**. |
| 3 | **Smoke test** — Create a test Tenant record and a test Rent Agreement. | Records save successfully and appear in the respective list views. |
| 4 | **Error logs** — Check **Settings → Error Log** for any critical errors. | No Rent Pro-related critical errors. |

If all checks pass, your deployment is ready.

---

## Common Issues & Resolutions

| Issue | Resolution |
|-------|-----------|
| **App not appearing after install** | Run `bench --site <site> clear-cache` and refresh. |
| **Migration fails with "App not found"** | Verify the app is installed: `bench --site <site> list-apps`. Reinstall if missing. |
| **Scheduler not running** | Trigger manually: `bench --site <site> scheduler enable`. Check Frappe Cloud background workers status. |
| **Permission error on Rent Pro Settings** | Ensure your user has the **"Rent Pro Manager"** role assigned. |
| **GitHub clone fails during install** | Verify the SSH key on Frappe Cloud matches your GitHub account and the repository is accessible. |
| **Site goes into maintenance mode** | Check the site's **"Jobs"** tab for stuck jobs. Cancel or retry as needed. |

---

## Support Contact

For issues, questions, or contributions:

- **GitHub Issues:** [https://github.com/your-org/rent_pro/issues](https://github.com/your-org/rent_pro/issues)
- **Email:** support@your-org.com
- **Frappe Community Forum:** [https://discuss.frappe.io](https://discuss.frappe.io) (tag: `rent-pro`)

---

*This guide is specific to Rent Pro v1.0 RC1 on Frappe Cloud. For local development setup, refer to the main project README.*
