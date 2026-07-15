# Rent Pro v1.0 — Backup & Restore Guide

**Version:** 1.0.0-rc1

---

## Backup Strategy

### What to Back Up

| Component | Location | Priority |
|-----------|----------|----------|
| Database | MariaDB | CRITICAL |
| Site Config | `sites/site-name.local/site_config.json` | CRITICAL |
| Apps | `apps.txt` | HIGH |
| Private Files | `sites/site-name.local/private/files/` | HIGH |
| Public Files | `sites/site-name.local/public/files/` | MEDIUM |
| Logs | `sites/site-name.local/logs/` | LOW |

### Frappe Cloud

Frappe Cloud provides automatic daily backups. Manual backups available via:
- **Bench Dashboard** → Backups → Create Backup
- **API**: `GET /api/method/frappe.core.doctype.backup.backup.get_backup`

### Self-Hosted

```bash
# Full backup (database + files)
bench --site site-name.local backup --with-files

# Database only
bench --site site-name.local backup

# Database + private files
bench --site site-name.local backup --with-private-files

# Database + public files
bench --site site-name.local backup --with-public-files
```

### Automated Backup Script

```bash
#!/bin/bash
# /etc/cron.d/rentpro-backup
# Runs daily at 2 AM

SITE="site-name.local"
BACKUP_DIR="/backups/rentpro"
DATE=$(date +%Y%m%d_%H%M%S)

cd /home/frappe/bench-root

# Create backup
bench --site $SITE backup --with-files

# Move to backup directory
mkdir -p $BACKUP_DIR
mv sites/$SITE/private/backups/* $BACKUP_DIR/ 2>/dev/null

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar" -mtime +30 -delete
```

---

## Restore Procedures

### Full Restore (Frappe Cloud)

1. Go to Bench Dashboard → Backups
2. Select backup date
3. Click "Restore"
4. Confirm restoration

### Full Restore (Self-Hosted)

```bash
# Stop scheduler
bench --site site-name.local scheduler stop

# Restore database
bench --site site-name.local restore /path/to/backup.sql.gz

# Restore with files
bench --site site-name.local restore \
    /path/to/backup.sql.gz \
    --with-private-files /path/to/private-files.tar \
    --with-public-files /path/to/public-files.tar

# Restart
bench --site site-name.local scheduler start
bench restart
```

### Database-Only Restore

```bash
bench --site site-name.local restore /path/to/database.sql.gz
bench --site site-name.local migrate
bench restart
```

---

## Site Migration

### Moving to New Server

```bash
# On old server
bench --site site-name.local backup --with-files
tar -czf site-name.local.tar.gz \
    sites/site-name.local/private/backups/ \
    sites/site-name.local/site_config.json

# Copy to new server
scp site-name.local.tar.gz user@new-server:/path/to/

# On new server
cd bench-root
bench new-site site-name.local
bench --site site-name.local restore /path/to/backup.sql.gz \
    --with-private-files /path/to/private-files.tar \
    --with-public-files /path/to/public-files.tar
bench --site site-name.local install-app rentpro
bench --site site-name.local migrate
bench restart
```

---

## Rent Pro Specific Considerations

### Data Affected by Backup

| Data Type | DocType | Backup Impact |
|-----------|---------|---------------|
| Fleet data | Vehicle, Vehicle Category | Full backup |
| Reservations | Reservation | Full backup |
| Contracts | Rental Contract | Full backup |
| Payments | Payment Transaction | Full backup |
| Expenses | Expense Entry | Full backup |
| Documents | Document Record | Database + files |
| GPS Data | GPS Position | Database only (high volume) |
| Geofences | Geofence Zone, Geofence Alert | Full backup |
| Subscriptions | Agency Subscription, Subscription Plan | Full backup |
| Settings | All Single DocTypes | Full backup |
| Audit Logs | Super Admin Audit Log | Full backup |

### GPS Data Volume

GPS Position records can accumulate rapidly (thousands per vehicle per day). Consider:

```sql
-- Archive old GPS data before backup
DELETE FROM `tabGPS Position`
WHERE creation < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

### License Keys

License Key data includes encrypted payloads. Ensure backups are encrypted at rest for production.

---

## Disaster Recovery

### Recovery Time Objective (RTO)
- **Frappe Cloud:** < 1 hour (managed)
- **Self-hosted:** < 4 hours (depends on data size)

### Recovery Point Objective (RPO)
- **Frappe Cloud:** < 24 hours (daily backups)
- **Self-hosted:** Depends on backup frequency (recommend hourly for production)

### Recovery Steps

1. Provision new server
2. Install Frappe Bench
3. Restore from backup
4. Install Rent Pro app
5. Run migrations
6. Verify all data
7. Update DNS
8. Monitor for 24 hours
