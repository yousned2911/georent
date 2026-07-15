# Rent Pro

**Paperless ERP for Moroccan Car Rental Agencies**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext: v15+](https://img.shields.io/badge/ERPNext-v15+-blue.svg)](https://erpnext.com)
[![Frappe: v15+](https://img.shields.io/badge/Frappe-v15+-green.svg)](https://frappeframework.com)

---

## Overview

Rent Pro is a comprehensive, paperless ERPNext custom app designed specifically for Moroccan car rental agencies. Built on Frappe Framework v15+ and ERPNext v15+, it provides end-to-end rental business management with multi-tenant SaaS capabilities.

### Key Features

- **Vehicle Management** — Fleet tracking, status workflow, maintenance, compliance
- **Reservations** — Availability calendar, overlap detection, 6-state workflow
- **Rental Contracts** — Digital contracts, Moroccan TVA (20%/14%/10%/7%), invoice generation
- **OCR Document Processing** — Automated CIN, license, and registration scanning
- **Finance & Accounting** — Payment tracking, expense management, 8 financial reports
- **GPS Fleet Tracking (GeoFleete)** — Real-time tracking, geofencing, route monitoring
- **SaaS Platform** — Multi-tenant architecture, subscription billing, agency management
- **Super Admin** — Platform dashboard, feature flags, audit center, support tools

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.10+, Frappe Framework v15+ |
| Frontend | JavaScript, Leaflet.js (maps) |
| Database | MariaDB 10.6+ |
| Cache | Redis 6+ |
| OCR | Tesseract, Google Vision, Azure OCR |
| Platform | ERPNext v15+ |

---

## Installation

### Prerequisites

- Python 3.10+
- MariaDB 10.6+
- Node.js 18+
- Redis 6+
- Frappe Bench CLI

### Quick Start

```bash
# Clone and install
bench get-app https://github.com/your-org/rentpro.git
bench --site your-site.local install-app rentpro
bench --site your-site.local migrate
bench build
bench restart
```

### Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Backup Guide](BACKUP_GUIDE.md)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## Modules

| Module | Description |
|--------|-------------|
| Vehicles | Fleet management, categories, status tracking |
| Reservations | Booking system, availability, conflict resolution |
| Contracts | Digital rental agreements, TVA calculation |
| OCR | Document scanning, field extraction |
| Finance | Payments, expenses, financial reports |
| GeoFleete | GPS tracking, geofencing, alerts |
| Reports | 8 built-in financial and operational reports |
| SaaS | Multi-tenant subscription management |
| Super Admin | Platform administration and monitoring |

---

## Configuration

After installation, configure Rent Pro via:

1. **Rent Pro Settings** — Agency name, currency, OCR, GeoFleete
2. **SaaS Settings** — Multi-tenant configuration
3. **System Health Settings** — Monitoring thresholds
4. **Super Admin Settings** — Platform administration

---

## Testing

```bash
cd rentpro
bench --site your-site.local run-tests --app rentpro
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## Security

Report security vulnerabilities via [SECURITY.md](SECURITY.md).

---

## License

MIT License — see [license.txt](license.txt)

---

## Support

- **Documentation:** [docs.rentpro.ma](https://docs.rentpro.ma)
- **Issues:** [GitHub Issues](https://github.com/your-org/rentpro/issues)
- **Email:** dev@rentpro.ma
