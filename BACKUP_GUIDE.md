# Backup Guide — Rent Pro v1.0 RC1 (Frappe Cloud)

**Last updated:** 2026-07-15

---

## Why Backup Is Critical

Rent Pro manages your entire rental lifecycle — property records, tenant contracts, payment schedules, invoices, and OCR-processed documents. Losing this data means:

- **Contract history** — Lease agreements, renewal records, and tenant correspondence become unrecoverable
- **Financial records** — Outstanding balances, payment history, and invoice logs are lost
- **Compliance risk** — Tax-relevant documents and audit trails disappear
- **Operational disruption** — Manual reconstruction of rental data costs significant time and money

Regular backups are the only safety net for production data.

---

## Frappe's Built-In Backup

Frappe Cloud provides the `bench backup` command via the web terminal or SSH.

### Manual backup

```bash
bench backup
```

### Verbose (includes progress)

```bash
bench --site [sitename].frappe.cloud backup --verbose
```

### Backup to a specific directory

```bash
bench backup --backup-path /tmp/backups
```

On Frappe Cloud, backups are accessible via the **Backups** tab in your site dashboard.

---

## What Gets Backed Up

A full Frappe backup includes three components:

| Component | Content | File type |
|-----------|---------|-----------|
| **Database** | All doctype data, fixtures, and metadata | `.sql.gz` |
| **Public files** | Attachments served publicly, templates, static assets | `.tar.gz` |
| **Private files** | Private attachments, uploaded documents, OCR scans | `.tar.gz` |

All three must be restored together for a complete recovery.

---

## Backup Schedule Recommendations

| Environment | Frequency | Method |
|-------------|-----------|--------|
| Production | **Daily** | Frappe Cloud scheduled backups (automatic) |
| Production | Weekly manual | `bench backup` via web terminal |
| Staging | Weekly | Scheduled or manual |
| Development | Before changes | Manual `bench backup` |

### Frappe Cloud automatic backups

Frappe Cloud runs automatic backups by default. Confirm the schedule under **Site Dashboard → Backups → Backup Schedule**.

### Manual safety net

Even with automatic backups, perform a manual backup before:

- Deploying custom apps or updates
- Migrating fixtures or data
- Major configuration changes

---

## Restore Procedure (Step by Step)

### Prerequisites

- The backup files (`.sql.gz` and `.tar.gz` archives)
- SSH access or web terminal access to the target bench
- A site that is in maintenance mode

### Step 1 — Put the site in maintenance mode

```bash
bench --site [sitename] set-maintenance-mode on
```

### Step 2 — Stop background workers

```bash
bench --site [sitename] ready-for-production
```

### Step 3 — Restore the database

```bash
bench --site [sitename] restore [database_file.sql.gz]
```

### Step 4 — Restore public files

```bash
bench --site [sitename] restore --with-public-files [public_files.tar.gz]
```

### Step 5 — Restore private files

```bash
bench --site [sitename] restore --with-private-files [private_files.tar.gz]
```

### Step 6 — Run migrations

```bash
bench --site [sitename] migrate
bench build
```

### Step 7 — Bring the site out of maintenance mode

```bash
bench --site [sitename] set-maintenance-mode off
```

### Step 8 — Verify

- Log in to the site
- Check that contracts, payments, and property records are intact
- Confirm file attachments (OCR scans, uploaded documents) are accessible

---

## Data Recovery Considerations — Rent Pro Specifics

### Contracts and agreements

Contract doctypes link tenants, properties, and payment schedules. After a restore, verify:

- All active lease contracts are present and correctly linked
- Recurring payment entries are generated
- Contract start/end dates are accurate

### Payments and invoices

Financial data depends on correct database integrity:

- Check outstanding invoices against payment entries
- Reconcile any scheduled payments that may have missed a generation cycle
- Verify chart of accounts and cost centers if applicable

### OCR-processed documents

OCR uploads are stored as private file attachments. After restore:

- Confirm the `private/files` directory contains all expected documents
- Check that any OCR-linked doctypes (e.g., scanned receipts, signed contracts) resolve correctly
- If attachments are broken, re-link them via the file manager

### Custom doctypes and fixtures

If Rent Pro uses custom fixtures:

- Ensure fixture data was included in the backup
- Run `bench --site [sitename] migrate` to sync schema changes
- Verify custom fields and workflows

---

## Testing Backups Regularly

A backup is only reliable if it has been tested.

### Recommended testing schedule

| Action | Frequency |
|--------|-----------|
| Full restore test (to a staging site) | Monthly |
| Spot-check critical data | After every manual backup |
| Verify file attachment integrity | After every restore |

### How to test

1. Restore the backup to a staging or development site using the steps above
2. Log in and walk through key workflows:
   - View property list and tenant records
   - Open an active contract
   - Check payment schedule and invoice history
   - Download an uploaded document (OCR scan or attachment)
3. Confirm all data is present and relationships are intact

### What to watch for

- Missing or broken file attachments (indicates incomplete private file backup)
- Orphaned records (database restored but links not re-established)
- Schema mismatches (backup from a different app version)

---

## Quick Reference

```bash
# Backup
bench backup

# Restore database only
bench --site sitename restore backup.sql.gz

# Restore with files
bench --site sitename restore backup.sql.gz --with-public-files public.tar.gz --with-private-files private.tar.gz

# Maintenance mode
bench --site sitename set-maintenance-mode on
bench --site sitename set-maintenance-mode off

# Migrate after restore
bench --site sitename migrate
bench build
```

---

*For Frappe Cloud-specific documentation, see: https://frappecloud.com/docs*
