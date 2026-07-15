# Rent Pro — Repository Structure

```
georent/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Lint, test, build on every PR
│   │   └── deploy-staging.yml        # Auto-deploy to Frappe Cloud staging
│   └── pull_request_template.md
│
├── apps/
│   └── rentpro/                      # Custom Frappe app
│       ├── setup.py
│       ├── requirements.txt
│       ├── license.txt
│       ├── README.md
│       ├── __init__.py
│       ├── hooks.py                  # App hooks, overrides, fixtures
│       ├── patches.txt               # Migration patches
│       │
│       ├── rentpro/
│       │   ├── __init__.py
│       │   │
│       │   ├── vehicles/             # Module 1
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── vehicle/
│       │   │   │   │   ├── vehicle.json
│       │   │   │   │   ├── vehicle.py
│       │   │   │   │   ├── vehicle.js
│       │   │   │   │   └── test_vehicle.py
│       │   │   │   ├── vehicle_category/
│       │   │   │   ├── vehicle_document/
│       │   │   │   └── vehicle_maintenance/
│       │   │   └── report/
│       │   │       └── fleet_utilization/
│       │   │
│       │   ├── reservations/         # Module 2
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── reservation/
│       │   │   │   ├── reservation_availability/
│       │   │   │   └── reservation_conflict/
│       │   │   └── report/
│       │   │       └── reservation_summary/
│       │   │
│       │   ├── contracts/            # Module 3
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── rental_contract/
│       │   │   │   ├── contract_renewal/
│       │   │   │   └── contract_template/
│       │   │   ├── report/
│       │   │   │   └── contract_status/
│       │   │   └── template/
│       │   │       └── rental_contract.html
│       │   │
│       │   ├── ocr/                  # Module 4
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── ocr_document/
│       │   │   │   └── ocr_field_mapping/
│       │   │   ├── services/
│       │   │   │   ├── ocr_engine.py
│       │   │   │   ├── cin_extractor.py
│       │   │   │   ├── license_extractor.py
│       │   │   │   └── registration_extractor.py
│       │   │   └── api.py
│       │   │
│       │   ├── finance/              # Module 5
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── sales_invoice/
│       │   │   │   ├── payment_entry/
│       │   │   │   ├── tva_rate/
│       │   │   │   ├── deposit/
│       │   │   │   └── late_fee/
│       │   │   ├── services/
│       │   │   │   ├── tva_calculator.py
│       │   │   │   └── reconciliation.py
│       │   │   └── report/
│       │   │       ├── revenue_report/
│       │   │       └── tax_summary/
│       │   │
│       │   ├── geofleete/            # Module 6
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── gps_device/
│       │   │   │   ├── gps_position/
│       │   │   │   ├── geofence_zone/
│       │   │   │   └── geofence_alert/
│       │   │   ├── services/
│       │   │   │   ├── gps_tracker.py
│       │   │   │   ├── geofence_engine.py
│       │   │   │   └── route_history.py
│       │   │   └── api.py
│       │   │
│       │   ├── reports/              # Module 7
│       │   │   ├── __init__.py
│       │   │   ├── fleet_utilization_report/
│       │   │   ├── revenue_report/
│       │   │   ├── customer_history/
│       │   │   ├── maintenance_schedule/
│       │   │   └── tax_summary/
│       │   │
│       │   ├── dashboard/            # Module 8
│       │   │   ├── __init__.py
│       │   │   ├── page/
│       │   │   │   └── executive_dashboard/
│       │   │   ├── dashboard_chart/
│       │   │   │   ├── fleet_status/
│       │   │   │   ├── reservation_heatmap/
│       │   │   │   └── revenue_trend/
│       │   │   └── number_card/
│       │   │       ├── active_vehicles/
│       │   │       ├── today_revenue/
│       │   │       └── occupancy_rate/
│       │   │
│       │   ├── saas/                 # Module 9
│       │   │   ├── __init__.py
│       │   │   ├── doctype/
│       │   │   │   ├── agency/
│       │   │   │   ├── subscription_plan/
│       │   │   │   └── agency_onboarding/
│       │   │   ├── services/
│       │   │   │   ├── tenant_manager.py
│       │   │   │   └── billing.py
│       │   │   └── api.py
│       │   │
│       │   ├── public/               # Static assets
│       │   │   ├── css/
│       │   │   │   └── rentpro.css
│       │   │   ├── js/
│       │   │   │   └── rentpro.js
│       │   │   └── images/
│       │   │
│       │   ├── templates/            # Jinja templates
│       │   │   ├── pages/
│       │   │   └── includes/
│       │   │
│       │   └── translations/         # i18n
│       │       ├── fr.csv
│       │       ├── ar.csv
│       │       └── en.csv
│       │
│       └── patches/                  # Data migration patches
│           ├── v1_0/
│           └── v2_0/
│
├── docker/
│   ├── dev.dockerfile
│   ├── dev-compose.yml
│   └── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── development.md
│   ├── user/
│   │   ├── vehicles.md
│   │   ├── reservations.md
│   │   ├── contracts.md
│   │   └── finance.md
│   └── api/
│       └── ocr_api.md
│
├── PROJECT_MANAGER.md
├── ROADMAP.md
├── MILESTONES.md
├── RISKS.md
├── TREE.md
├── GIT_STRATEGY.md
└── README.md
```

## Key Conventions

- **Doctype naming**: `snake_case` matching Frappe convention
- **One doctype per directory**: contains `.json` (schema), `.py` (server), `.js` (client), `test_*.py`
- **Services layer**: business logic that spans multiple doctypes lives in `services/`
- **Translations**: CSV files per language, generated from Frappe's `build-for-app` command
- **Patches**: versioned under `patches/v{major}_{minor}/`, referenced in `patches.txt`
- **No core modifications**: all customizations use Frappe hooks, whitelisted APIs, and overrides
