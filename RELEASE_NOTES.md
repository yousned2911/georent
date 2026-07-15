# Rent Pro v1.0 — Release Notes

**Version:** 1.0.0-rc1
**Date:** 2026-07-15
**Status:** RELEASE CANDIDATE — NOT PRODUCTION READY

---

## Overview

Rent Pro is a paperless ERPNext custom app (`rentpro`) for Moroccan car rental agencies. Built on Frappe Framework v15+ and ERPNext v15+, it provides vehicle management, reservations, contracts, OCR document processing, GPS fleet tracking (GeoFleete), financial reporting, and SaaS multi-tenant capabilities.

---

## What's Included

### Core Modules (9)
| Module | Components |
|--------|------------|
| **Vehicles** | Vehicle DocType (35 fields), Vehicle Category, status workflow, 4 number cards |
| **Reservations** | Reservation DocType (23 fields), overlap detection, 6-state workflow, 5 number cards |
| **Contracts** | Rental Contract (48 fields), TVA engine (20%/14%/10%/7%), Sales Invoice integration, print format |
| **OCR** | Document Record (39 fields), Document Audit Log, OCR service abstraction (Tesseract/Google Vision/Azure) |
| **Finance** | Payment Transaction (14 fields), Expense Entry (11 fields), 8 financial reports |
| **GeoFleete** | GPS Position, Geofence Zone, Geofence Alert, Vehicle Tracking, GPS provider interface, 6 UI pages |
| **Reports** | 8 reports: Revenue by Month/Vehicle/Agency, TVA Summary, Expenses, Profitability, Fleet Utilization, Outstanding |
| **Dashboard** | 35 number cards across all modules |
| **SaaS** | Agency, Subscription Plan, Agency Subscription, License Key, Plan Enforcement, Billing Engine |

### Super Admin Platform
- Feature Flag system (Global/Per-Agency)
- Audit Center (15 action types)
- System Health monitoring (7 checks)
- Support Tools (impersonate, extend trial, suspend, reactivate, reset, export)
- Tenant Management (isolation verification, metrics, quotas)
- 18 whitelisted API endpoints

### Technical Specifications
| Metric | Count |
|--------|-------|
| DocTypes | 26 (18 documents, 5 singles, 3 child tables) |
| Total Fields | 559 |
| Python Controllers | 26 |
| Test Methods | 229 |
| Number Cards | 35 |
| Reports | 8 |
| JS Files | 29 |
| Whitelisted APIs | 26 (18 super admin + 8 GPS) |
| Scheduled Jobs | 6 (4 daily, 1 hourly, 1 every-5min) |
| Custom Roles | 7 |
| Hook Handlers | 27 |

### Languages
- English (en)
- French (fr)
- Arabic (ar) — partial RTL support

---

## Installation

```bash
bench get-app https://github.com/your-org/rentpro.git
bench --site your-site.local install-app rentpro
bench --site your-site.local migrate
bench build
bench restart
```

---

## Upgrade Path

From v0.x to v1.0: Run `bench migrate` after installation. No data migration required for fresh installs.

---

## Known Limitations (see KNOWN_ISSUES.md)

1. Multi-tenancy has critical isolation gaps (GPS API, reports, 3 DocTypes missing agency field)
2. Translation coverage is incomplete (49 keys vs 136+ needed)
3. Print format is English-only (no Arabic/RTL)
4. 2 DocType name collisions with ERPNext core (Vehicle, Expense Entry)
5. 8 GPS API endpoints have no permission checks
6. XSS vulnerabilities in GeoFleete JS pages

---

## Breaking Changes

- None (initial release)

---

## Contributors

- Rent Pro Development Team

---

## License

MIT License
