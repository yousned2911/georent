# Rent Pro v1.0 — Upgrade Guide

**Version:** 1.0.0-rc1

---

## Upgrade Prerequisites

- Frappe Bench CLI updated
- All apps compatible with target Frappe/ERPNext version
- Database backup completed
- Maintenance window scheduled

---

## Standard Upgrade Procedure

### Step 1: Backup

```bash
bench --site site-name.local backup --with-files
```

### Step 2: Update Apps

```bash
# Update all apps
bench update --pull

# Or update specific app
cd apps/rentpro
git pull origin main
```

### Step 3: Run Migrations

```bash
bench --site site-name.local migrate
bench build
bench restart
```

### Step 4: Verify

```bash
bench --site site-name.local console
>>> import rentpro
>>> print(rentpro.__version__)
```

---

## Version History

### v0.1.0 → v0.2.0 (Vehicle Module)
- New DocType: Vehicle (22 fields)
- New DocType: Vehicle Category
- New Child: Vehicle Document
- No breaking changes

### v0.2.0 → v0.3.0 (Reservation Module)
- New DocType: Reservation (17 fields)
- New Role: Reservation Agent
- No breaking changes

### v0.3.0 → v0.4.0 (Contract Module)
- New DocType: Rental Contract (30+ fields)
- New Role: Rental Agent
- New Print Format: Rent Pro Standard Contract
- Custom Field: Sales Invoice.rental_contract

### v0.4.0 → v0.5.0 (Finance Module)
- New DocType: Payment Transaction (14 fields)
- New DocType: Expense Entry (11 fields)
- 8 new Reports
- No breaking changes

### v0.5.0 → v0.6.0 (OCR Module)
- New DocType: Document Record (39 fields)
- New Child: Document Audit Log
- New Module: OCR Service
- No breaking changes

### v0.6.0 → v0.7.0 (GeoFleete Module)
- New DocType: GPS Position, Geofence Zone, Geofence Alert, Vehicle Tracking
- New Single: GeoFleete Settings
- New Module: GPS Provider
- 6 new UI pages
- No breaking changes

### v0.7.0 → v0.8.0 (SaaS Module)
- New DocType: Agency (40 fields)
- New DocType: Subscription Plan (34 fields)
- New DocType: Agency Subscription (20 fields)
- New DocType: License Key (15 fields)
- New Child: Subscription Usage
- New Single: SaaS Settings
- New Module: SaaS
- No breaking changes

### v0.8.0 → v0.9.0 (Super Admin)
- New DocType: Feature Flag (20 fields)
- New DocType: Super Admin Audit Log (17 fields)
- New Single: System Health Settings (22 fields)
- New Single: Super Admin Settings (18 fields)
- New Module: Super Admin
- No breaking changes

### v0.9.0 → v1.0.0 (Release Candidate)
- Security hardening (permission checks, tenant isolation)
- XSS fixes in GeoFleete JS
- Translation expansion
- No breaking changes

---

## Schema Changes

### v1.0.0-rc1 Schema

| DocType | Fields | Type |
|---------|--------|------|
| Vehicle | 35 | Document |
| Vehicle Category | 8 | Document |
| Vehicle Document | 7 | Child |
| Reservation | 23 | Document |
| Rental Contract | 48 | Document |
| Payment Transaction | 14 | Document |
| Expense Entry | 11 | Document |
| Document Record | 39 | Document |
| Document Audit Log | 4 | Child |
| GPS Position | 22 | Document |
| Geofence Zone | 19 | Document |
| Geofence Alert | 20 | Document |
| Vehicle Tracking | 18 | Document |
| Agency | 40 | Document |
| Subscription Plan | 34 | Document |
| Agency Subscription | 20 | Document |
| Subscription Usage | 6 | Child |
| License Key | 15 | Document |
| Feature Flag | 20 | Document |
| Super Admin Audit Log | 17 | Document |
| Rent Pro Settings | 27 | Single |
| GeoFleete Settings | 21 | Single |
| SaaS Settings | 16 | Single |
| Super Admin Settings | 18 | Single |
| System Health Settings | 22 | Single |

**Total: 559 fields across 26 DocTypes**

---

## Breaking Changes Policy

Rent Pro follows semantic versioning:
- **Major (X.0.0):** Breaking changes with migration path
- **Minor (0.X.0):** New features, backward compatible
- **Patch (0.0.X):** Bug fixes only

---

## Rollback Procedure

If upgrade fails:

```bash
# Stop the site
bench --site site-name.local set-maintenance-mode on

# Restore from backup
bench --site site-name.local restore /path/to/backup.sql.gz \
    --with-private-files /path/to/private-files.tar

# Restart
bench --site site-name.local set-maintenance-mode off
bench restart
```

---

## Frappe Cloud Upgrades

Frappe Cloud handles most upgrades automatically:
1. Updates are applied during maintenance windows
2. Backups are created automatically
3. Migrations run automatically
4. Rollback available if issues detected

For custom apps like Rent Pro:
1. Push new version to GitHub
2. Frappe Cloud detects update
3. Review changelog
4. Schedule update in maintenance window
5. Monitor after deployment
