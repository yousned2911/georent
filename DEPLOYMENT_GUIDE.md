# Rent Pro v1.0 — Deployment Guide

**Version:** 1.0.0-rc1
**Target:** Frappe Cloud or Self-Hosted

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| MariaDB | 10.6+ |
| Node.js | 18+ |
| Frappe Framework | v15+ |
| ERPNext | v15+ |
| Redis | 6+ |
| bench CLI | Latest |

---

## Fresh Installation

### Step 1: Install Frappe Bench

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-dev python3-pip python3-venv \
    mariadb-server redis-server git curl

# Install bench
pip3 install frappe-bench

# Initialize bench
bench init --frappe-branch version-15 bench-root
cd bench-root
```

### Step 2: Create Site

```bash
bench new-site site-name.local \
    --mariadb-root-password your-password \
    --admin-password admin-password
bench --site site-name.local set-config developer_mode 1
bench use site-name.local
```

### Step 3: Install ERPNext

```bash
bench get-app erpnext --branch version-15
bench --site site-name.local install-app erpnext
```

### Step 4: Install Rent Pro

```bash
bench get-app /path/to/rentpro.git
# OR from GitHub:
# bench get-app https://github.com/your-org/rentpro.git

bench --site site-name.local install-app rentpro
bench --site site-name.local migrate
bench build
bench restart
```

### Step 5: Verify Installation

```bash
# Check hooks resolve
bench --site site-name.local console
>>> import rentpro
>>> print(rentpro.__version__)

# Check DocTypes exist
>>> frappe.get_doc("DocType", "Vehicle")
>>> frappe.get_doc("DocType", "Agency")

# Check roles created
>>> frappe.get_all("Role", filters={"role_name": ["like", "Rent Pro%"]})
```

### Step 6: Configure

1. Navigate to **Rent Pro Settings** in desk
2. Set agency name, currency (MAD), default TVA rate
3. Configure OCR settings (enable/disable, confidence threshold)
4. Configure GeoFleete (enable, select provider, set mock mode)
5. Configure SaaS Settings (enable SaaS mode, set billing parameters)
6. Configure System Health Settings (enable health checks)

---

## Production Configuration

### Environment Variables

```bash
# In site_config.json
{
    "db_name": "rentpro_db",
    "db_password": "secure-password",
    "secret_key": "auto-generated-key",
    "developer_mode": 0
}
```

### Recommended Settings

```json
// site_config.json additions
{
    "background_workers": 2,
    "scheduler_enabled": 1,
    "allow_login_using_mobile_number": 0,
    "allow_login_using_user_name": 1
}
```

### Redis Configuration

Ensure Redis is running for:
- Cache: `redis_cache` (default port 13000)
- Queue: `redis_queue` (default port 11000)
- Socketio: `redis_socketio` (default port 12000)

### MariaDB Configuration

Recommended for 1000+ agencies:

```ini
[mysqld]
innodb_buffer_pool_size = 4G
innodb_log_file_size = 1G
max_connections = 500
query_cache_type = 0
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

---

## Frappe Cloud Deployment

1. Push to GitHub repository
2. Connect repository to Frappe Cloud
3. Select branch and app
4. Install on target site
5. Frappe Cloud handles scaling, backups, and SSL

---

## Post-Installation Checklist

- [ ] Rent Pro Settings configured
- [ ] Default agency created
- [ ] Vehicle Categories set up
- [ ] TVA Rates configured (20%, 14%, 10%, 7%)
- [ ] OCR provider configured (if using)
- [ ] GeoFleete enabled (if using)
- [ ] SaaS Settings configured (if multi-tenant)
- [ ] Feature Flags reviewed
- [ ] System Health Settings configured
- [ ] Super Admin Settings reviewed
- [ ] Custom roles assigned to users
- [ ] Print format reviewed
- [ ] Test contract printed

---

## Monitoring

### Health Checks

Health checks run daily via `scheduled_health_check()`. Check status at:
- **System Health Settings** single DocType in desk
- Or call `rentpro.super_admin.system_health.get_health_status()`

### Scheduled Jobs

| Job | Frequency | Purpose |
|-----|-----------|---------|
| `daily_tasks` | Daily | Document expiry warnings, vehicle compliance |
| `scheduled_subscription_renewal` | Daily | Process subscription renewals |
| `scheduled_check_overdue_subscriptions` | Daily | Mark past due, suspend overdue |
| `scheduled_health_check` | Daily | System health monitoring |
| `hourly_tasks` | Hourly | Document expiration monitoring |
| `geofleete_heartbeat` | Every 5 min | GPS simulation (mock mode) |

---

## Troubleshooting

### Common Issues

1. **Hooks not resolving**: Run `bench build` and `bench restart`
2. **Missing DocTypes**: Run `bench migrate`
3. **Permission errors**: Check custom roles are assigned to users
4. **GPS not working**: Verify GeoFleete Settings is enabled and mock mode is on
5. **OCR failing**: Check Tesseract installation (`tesseract --version`)

### Logs

```bash
# Frappe logs
tail -f sites/site-name.local/logs/frappe.log

# Scheduler logs
bench --site site-name.local scheduler status
```
