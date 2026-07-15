# Rent Pro v1.0 RC1 — Deployment Guide

**Version:** 1.0 RC1  
**Date:** 2026-07-15  
**Platform:** Frappe/ERPNext v15

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation Steps](#2-installation-steps)
3. [Post-Installation Configuration](#3-post-installation-configuration)
4. [Roles Reference](#4-roles-reference)
5. [Environment Variables](#5-environment-variables)
6. [Security Considerations](#6-security-considerations)
7. [Monitoring](#7-monitoring)
8. [Backup](#8-backup)
9. [Troubleshooting](#9-troubleshooting)
10. [Next Steps](#10-next-steps)

---

## 1. Prerequisites

Ensure the following components are installed and running before proceeding:

| Component       | Minimum Version | Notes                                    |
|-----------------|-----------------|------------------------------------------|
| Python          | 3.10+           | Recommended: 3.11                        |
| MariaDB         | 10.6+           | With `utf8mb4` and `utf8mb4_unicode_ci`  |
| Node.js         | 18+             | For bench asset building                 |
| Redis           | 6+              | Three instances: cache, queue, socketio  |
| Frappe Bench    | 5.x+            | CLI tool for managing Frappe deployments |
| ERPNext         | v15             | Required dependency for Rent Pro         |

**Verify your environment:**

```bash
python3 --version
mariadb --version
node --version
redis-server --version
bench --version
```

---

## 2. Installation Steps

All commands below assume you are operating as the `frappe` user within your bench directory.

### 2.1 Get the App

```bash
bench get-app https://github.com/your-org/rent_pro.git
```

Or from a local path:

```bash
bench get-app /path/to/rent_pro
```

### 2.2 Install the App

```bash
bench --site your-site.local install-app rent_pro
```

This registers all Rent Pro DocTypes, roles, and permissions with your site.

### 2.3 Run Database Migrations

```bash
bench --site your-site.local migrate
```

### 2.4 Build Frontend Assets

```bash
bench build --app rent_pro
```

### 2.5 Restart Workers

```bash
bench restart
```

### 2.6 Verify Installation

```bash
bench --site your-site.local console
```

```python
import rent_pro
print(rent_pro.__version__)
```

---

## 3. Post-Installation Configuration

### 3.1 Rent Pro Settings

Navigate to: **Rent Pro > Rent Pro Settings**

Configure the following:

- **Default Currency:** Set to MAD (Moroccan Dirham) for local operations
- **Company Name:** Link to your ERPNext Company record
- **Default Tax Template:** Configure applicable Moroccan VAT rates
- **Rental Number Prefix:** Set the prefix for auto-generated rental agreements (e.g., `RA-`)
- **Reservation Prefix:** Set the prefix for reservations (e.g., `RV-`)

### 3.2 Agency Setup

Create your agency record under **Rent Pro > Agency**:

- Agency name and legal entity details
- Address (physical location)
- Contact information
- Link to the ERPNext Company
- Operating hours

### 3.3 User Roles and Permissions

Create users and assign roles-based permissions as outlined in the table below. Assign roles via **Settings > User > User Role**.

At minimum, configure:

- **System Manager** for administrators (already exists in Frappe)
- **Rent Pro Manager** for operations leads
- **Rent Pro User** for front-desk staff

---

## 4. Roles Reference

Rent Pro introduces the following custom roles:

| Role                    | Scope / Description                                              |
|-------------------------|------------------------------------------------------------------|
| **Rent Pro Manager**    | Full access to all Rent Pro modules. Manages fleet, contracts, and financial records. |
| **Rent Pro User**       | Day-to-day operations: creates reservations, manages check-in/out, and views reports. |
| **Fleet Manager**       | Manages vehicles, maintenance schedules, insurance, and vehicle availability. |
| **Contract Manager**    | Creates and manages rental agreements, amends contracts, and handles extensions. |
| **Customer Service**    | Handles reservations, customer interactions, and basic reporting. |
| **Finance Manager**     | Manages invoicing, payments, and financial reconciliation within Rent Pro. |
| **Workshop Manager**    | Manages maintenance tasks, parts inventory, and service records. |

---

## 5. Environment Variables

Rent Pro requires **no environment variables**. All configuration is managed through the **Rent Pro Settings** DocType within the Frappe web interface.

If your Frappe/ERPNext instance already uses environment variables (e.g., `DB_HOST`, `REDIS_CACHE`), those apply as usual but are managed at the Frappe level, not Rent Pro.

---

## 6. Security Considerations

### 6.1 HTTPS

- **Enable HTTPS** on your Frappe site using a reverse proxy (e.g., Nginx) with a valid TLS certificate.
- Disable HTTP access entirely in production.

### 6.2 Role-Based Access Control

- Assign the **minimum required role** to each user.
- Avoid granting **Rent Pro Manager** to non-administrative users.
- Review role assignments periodically under **Settings > Role Profile**.

### 6.3 Audit Logging

- Rent Pro logs all critical actions (contract creation, amendments, payments) with timestamps and user attribution.
- Enable Frappe's standard **Activity Log** and **Document Version** tracking.
- Review logs under **Audit Trail** and **Activity Log** in the Frappe desk.

### 6.4 Additional Recommendations

- Enforce strong passwords via Frappe's **System Settings**.
- Enable **Two-Factor Authentication (2FA)** for administrative accounts.
- Restrict desk access for users who only need portal access.

---

## 7. Monitoring

### 7.1 System Health Check

```bash
bench doctor --site your-site.local
```

This checks database integrity, background worker status, and queued jobs.

### 7.2 Background Jobs

Monitor the background job queue via:

```bash
bench --site your-site.local console
```

```python
from frappe.utils.background_jobs import get_queue_list
from frappe import get_jobs
print(get_jobs())
```

Or view via the web desk: **Settings > Background Jobs**.

### 7.3 Site Health

```bash
bench --site your-site.local requests --limit 20
```

Check request logs for errors or performance issues.

### 7.4 Log Files

```bash
# Frappe logs
tail -f /home/frappe/frappe-bench/logs/web.log

# Worker logs
tail -f /home/frappe/frappe-bench/logs/worker.log

# Scheduler logs
tail -f /home/frappe/frappe-bench/logs/scheduler.log
```

---

## 8. Backup

Rent Pro uses standard Frappe backup mechanisms. No additional backup configuration is required.

### 8.1 Manual Backup

```bash
bench --site your-site.local backup --with-files
```

This creates:

- A database dump (`.sql.gz`)
- A site config backup
- Uploaded files and private files

### 8.2 Automated Backups

Frappe supports scheduled backups. Configure via:

- **Settings > System Settings > Backup** — set the backup interval
- Or use cron to run `bench --site your-site.local backup --with-files` on a schedule

### 8.3 Restore

```bash
bench --site your-site.local restore /path/to/backup.sql.gz --with-files
```

---

## 9. Troubleshooting

| Issue                                    | Solution                                                                 |
|------------------------------------------|--------------------------------------------------------------------------|
| `bench get-app` fails                    | Verify git is installed and the repository URL is correct.               |
| `install-app` throws import errors       | Ensure ERPNext v15 is installed before Rent Pro.                         |
| Assets not loading after `bench build`   | Run `bench clear-cache` then `bench build --app rent_pro` again.         |
| Roles not appearing in desk              | Run `bench --site your-site.local migrate` and restart.                  |
| DocType fields missing after update      | Run `bench --site your-site.local migrate` and `bench build --app rent_pro`. |
| Background jobs stuck                    | Restart workers: `bench restart`. Check `bench doctor` for issues.       |
| Permission errors on custom DocTypes     | Verify role assignments under **User > Role**. Reinstall if needed: `bench --site your-site.local reinstall`. |

---

## 10. Next Steps

After successful deployment:

1. **Seed initial data** — Import your vehicle fleet, customer records, and insurance providers.
2. **Configure templates** — Set up rental agreement templates and invoice templates under **Rent Pro Settings**.
3. **Train staff** — Provide desk walkthroughs for roles: Fleet Manager, Contract Manager, and Customer Service.
4. **Integrate payment gateways** — If applicable, configure Moroccan payment providers (e.g., CMI, M-Wallet) via ERPNext Payments.
5. **Schedule backups** — Set up automated daily backups with off-site storage.
6. **Monitor and iterate** — Review system logs weekly for the first month post-deployment.
7. **Report issues** — File bugs and feature requests via the project's GitHub Issues page.

---

*For questions or support, contact the development team or open an issue at the project repository.*
