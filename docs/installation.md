# Installation Guide

## Prerequisites

### System Requirements

| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| MariaDB | 10.6+ |
| Redis | 6+ |
| wkhtmltopdf | 0.12.6+ (for PDF generation) |
| Nginx | 1.18+ |

### Frappe Bench

Frappe Bench must be installed. Follow the [official guide](https://frappeframework.com/docs/user/en/installation):

```bash
# Install bench
pip3 install frappe-bench

# Initialize a new bench
bench init frappe-bench
cd frappe-bench

# Create a new site
bench new-site dev.rentpro.local

# Install ERPNext
bench get-app erpnext
bench --site dev.rentpro.local install-app erpnext
```

## Installing Rent Pro

### From Source (Recommended)

```bash
# Navigate to your bench directory
cd /path/to/frappe-bench

# Clone the repository into apps/
bench get-app /path/to/georent

# Install the app on your site
bench --site dev.rentpro.local install-app rentpro

# Run migrations
bench --site dev.rentpro.local migrate

# Build frontend assets
bench build --app rentpro

# Restart bench
bench restart
```

### Verify Installation

```bash
# Check app is installed
bench --site dev.rentpro.local console

>>> import rentpro
>>> rentpro.__version__
'0.1.0'

>>> frappe.db.exists("Rent Pro Settings", "settings")
'settings'
```

Or navigate to `http://dev.rentpro.local/app/rent-pro-settings` in your browser.

## Post-Installation Setup

### 1. Configure Rent Pro Settings

Navigate to **Rent Pro > Settings** and configure:

- **Agency Name** — Your rental agency name
- **Default Currency** — Defaults to MAD (Moroccan Dirham)
- **Default TVA Rate** — Select from 20%, 14%, 10%, 7%
- **OCR Settings** — Enable/disable and configure confidence threshold
- **GeoFleete** — Enable GPS tracking if available

### 2. Create User Roles

The following roles are created during installation:

| Role | Description |
|------|-------------|
| Rent Pro Manager | Full access to all modules |
| Rent Pro User | Day-to-day operations |
| Rent Pro Fleet Manager | Vehicle and maintenance management |
| Rent Pro Finance | Invoicing and payment processing |
| Rent Pro Read Only | View-only access |

Assign roles to users via **User > Roles** tab.

### 3. Create Vehicle Categories

Navigate to **Rent Pro > Vehicle Category** and create categories:

| Category | Description |
|----------|-------------|
| Economy | Small, fuel-efficient vehicles |
| Compact | Mid-size sedans |
| SUV | Sport utility vehicles |
| Luxury | Premium vehicles |
| Van | Passenger and cargo vans |

### 4. Add Vehicles

Navigate to **Rent Pro > Vehicle > New** and add your fleet with:

- Vehicle number (license plate)
- Make, model, year
- VIN
- Daily rental rate
- Insurance and inspection expiry dates

### 5. Create TVA Rates

Navigate to **Setup > Data > Naming Series** and ensure TVA rates exist:

| Rate | Percentage |
|------|------------|
| 20% | Standard rate |
| 14% | Reduced rate |
| 10% | Super-reduced rate |
| 7% | Preferential rate |

## Upgrade

```bash
# Pull latest changes
cd /path/to/georent
git pull origin develop

# Navigate to bench
cd /path/to/frappe-bench

# Update dependencies
bench update --app rentpro

# Or manually
bench --site dev.rentpro.local migrate
bench build --app rentpro
bench restart
```

## Uninstallation

```bash
bench --site dev.rentpro.local uninstall-app rentpro
bench --site dev.rentpro.local migrate
bench restart
```

## Troubleshooting

### Common Issues

**"App not found" error:**
```bash
bench --site dev.rentpro.local installed-apps
# If not listed, reinstall:
bench --site dev.rentpro.local install-app rentpro
```

**Build fails:**
```bash
# Clear cache and rebuild
bench --site dev.rentpro.local clear-cache
bench build --app rentpro --force
bench restart
```

**Permission errors:**
```bash
# Ensure correct ownership
sudo chown -R $USER:$USER /path/to/frappe-bench
```

### Logs

Check bench logs for errors:

```bash
tail -f /path/to/frappe-bench/logs/frappe.log
tail -f /path/to/frappe-bench/logs/worker.error.log
```

## Docker Development

For Docker-based development:

```bash
# Clone the repository
git clone https://github.com/your-org/georent.git

# Use the provided Docker setup
cd docker
cp .env.example .env
docker-compose up -d

# Access the site
open http://localhost:8000
```

## Support

- Documentation: See `docs/` directory
- Issues: GitHub Issues
- Forum: Frappe Discuss
