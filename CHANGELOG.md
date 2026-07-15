# Changelog

All notable changes to Rent Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-15

### Release Candidate 1

First production release of Rent Pro — a paperless ERP for Moroccan car rental agencies.

### Summary

- **26 DocTypes** (18 documents, 5 singles, 3 child tables)
- **559 total fields** across all DocTypes
- **229 test methods** in 26 test files
- **35 number cards** across all modules
- **8 financial reports**
- **27 hook handlers** (all resolve)
- **7 custom roles**
- **3 languages** (EN, FR, AR)

### Modules Included

- **Vehicles** — Fleet management, status workflow, categories
- **Reservations** — Booking system, overlap detection, 6-state workflow
- **Contracts** — Digital rental agreements, Moroccan TVA, invoice generation
- **OCR** — Document scanning, field extraction, audit trail
- **Finance** — Payments, expenses, 8 financial reports
- **GeoFleete** — GPS tracking, geofencing, alerts, 6 UI pages
- **SaaS** — Multi-tenant subscriptions, billing, plan enforcement
- **Super Admin** — Platform dashboard, feature flags, audit center

### Known Issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for complete list.

### Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Backup Guide](BACKUP_GUIDE.md)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Security Audit](SECURITY_AUDIT.md)
- [Performance Report](PERFORMANCE_REPORT.md)
- [Marketplace Checklist](MARKETPLACE_CHECKLIST.md)

---

## [0.9.0] - 2026-07-15

### Added

- **Feature Flag DocType** — Platform-wide feature toggling
  - Fields: flag_name, flag_label, enabled, category, scope, flag_type, flag_value
  - Categories: Core, Feature, Integration, Beta, Enterprise
  - Scopes: Global (all agencies), Per Agency (individual toggle)
  - Activation rules: min_plan_type, rollout_percentage
  - Metadata: last_toggled_by, last_toggled_on
  - API: is_enabled(), get_all_flags()
- **Super Admin Audit Log DocType** — Complete audit trail
  - 15 action types: Agency Creation, Suspension, Reactivation, Subscription Change, Trial Extension, Plan Upgrade/Downgrade, Feature Flag Toggle, Login Activity, Permission Change, Failed Payment, Support Action, System Event, Data Export, Tenant Isolation Check
  - Severity levels: Info, Warning, Critical
  - Tracks: actor, target, old/new values, IP address, metadata
  - create_audit_log() helper function
- **System Health Settings DocType** (Single) — Health monitoring configuration
  - Thresholds: CPU (80%), Memory (85%), Disk (90%), Queue (100), Failed Jobs (10), API Response (2000ms)
  - Alert settings: enable/disable, alert email
  - Last check status tracking: API, Database, Redis, Queue
- **Super Admin Settings DocType** (Single) — Platform admin configuration
  - Impersonation control: allow_impersonation, require_reason
  - Audit settings: audit_all_actions, retention_days, log_api_access
  - Support limits: max_trial_extension_days, max_extensions_per_agency, allow_subscription_reset
- **Super Admin Engine** (`super_admin/` module)
  - Dashboard: get_platform_summary(), get_agency_list_data(), get_subscription_monitoring(), get_revenue_dashboard()
  - Support Tools: extend_trial(), suspend_agency(), reactivate_agency(), reset_subscription(), impersonate_user(), export_agency_diagnostics()
  - System Health: run_health_check(), get_health_status(), get_background_job_stats()
  - Tenant Management: verify_tenant_isolation(), get_tenant_metrics(), get_tenant_quota_usage(), generate_usage_report()
  - Feature Flags: toggle_flag(), get_flag_status(), get_flags_for_agency(), bulk_toggle()
- **Super Admin API** — 18 whitelisted endpoints with role-based access
  - Platform summary, agency list, subscription monitoring, revenue dashboard
  - Health checks, background jobs
  - Audit logs, feature flags
  - Support actions: extend trial, suspend, reactivate, reset subscription
  - Tenant metrics, isolation verification
  - Agency diagnostics export
- **Super Admin Dashboard JS** — Client-side API wrapper for all endpoints
- **8 Tests** — Feature Flag (6), Audit Log (3), System Health Settings (2), Super Admin Settings (2), Dashboard (4), System Health (3), Support Tools (2), Tenant Management (5), Feature Flag Management (3)
- **Scheduled Job** — Daily health check via `scheduled_health_check()`

### Changed

- Updated hooks.py: 27 handlers (all resolve)
  - Added daily scheduled job for health checks
  - Added permission handlers for Super Admin Settings and System Health Settings
- Updated tasks.py with scheduled_health_check()
- Updated ROADMAP.md Phase 5 Super Admin marked DONE

## [0.8.0] - 2026-07-15

### Added

- **Agency DocType** — Multi-tenant agency management
  - Fields: agency_name, agency_code, status, contact info, address, subscription details, white label branding, usage tracking
  - Statuses: Active, Trial, Suspended, Inactive, Cancelled
  - Trial management: trial_start_date, trial_end_date, is_trial_expired()
  - Suspension/reactivation methods for non-payment handling
- **Subscription Plan DocType** — Pricing plan definitions
  - Fields: plan_label, plan_type, plan_code, price_mad, billing_cycle
  - Limits: max_vehicles, max_users, max_storage_mb, max_ocr_per_month, max_api_calls_per_month
  - Feature flags: geo_fleete_enabled, white_label_enabled, priority_support, multi_branch
  - Plan types: Starter, Professional, Enterprise
  - Billing cycles: Monthly, Quarterly, Yearly
- **Agency Subscription DocType** — Subscription lifecycle management
  - Fields: agency, plan, status, start_date, next_billing_date, amount_mad, auto_renew
  - Statuses: Active, Suspended, Cancelled, Past Due, Expired
  - Methods: suspend(), reactivate(), cancel_subscription(), renew()
  - Billing cycle tracking and invoice count
- **Subscription Usage DocType** — Child table for usage tracking
  - Metrics: Vehicles, Users, Storage, OCR Scans, API Calls, Contracts, Reservations
  - Per-metric usage vs limit with percentage tracking
- **License Key DocType** — Software licensing management
  - Fields: license_key, agency, status, plan, validity dates, max_agencies, activation count
  - License data generation with SHA-256 signature
  - Activation counting and validation
  - Methods: activate_for_agency(), is_valid(), revoke()
- **SaaS Settings DocType** — Platform-wide configuration
  - SaaS mode toggle, enforcement settings, grace period
  - Billing email, payment terms, auto-invoice generation
  - White label defaults (allow_white_label, default_brand_color, platform_name)
- **SaaS Engine** — Core subscription logic
  - Plan Enforcement: get_agency_usage(), check_vehicle_limit(), check_user_limit(), check_ocr_limit(), check_api_limit(), enforce_all_limits()
  - Vehicle creation validation via doc_event hook
  - Billing: generate_invoice(), process_renewals(), check_and_suspend_overdue(), mark_past_due()
  - Dashboard: get_platform_summary(), get_monthly_revenue_data()
- **5 SaaS Number Cards**
  - Total Agencies, Active Agencies, Trial Agencies, Active Subscriptions, Suspended Agencies
- **24 Tests** — Agency (5), Subscription Plan (5), Agency Subscription (5), License Key (5), SaaS Settings (2), Plan Enforcement (6), Billing (2), Dashboard (2)
- **Scheduled Jobs** — Subscription renewal and overdue checking (daily)

### Changed

- Updated hooks.py: 24 hook handlers (all resolve)
  - Added Vehicle before_insert for plan enforcement
  - Added daily scheduled jobs for subscription renewal and overdue checks
  - Added SaaS Settings permission handler
- Updated tasks.py with scheduled_subscription_renewal() and scheduled_check_overdue_subscriptions()
- Updated ROADMAP.md Phase 5 SaaS marked IN PROGRESS

## [0.7.0] - 2026-07-15

### Added

- **GPS Provider Interface** — Abstract base class for GPS providers
  - GPSProviderInterface: 9 abstract methods (get_positions, get_vehicle_state, get_all_vehicle_states, simulate_movement, check_geofences, get_maintenance_status, is_available)
  - GPS Provider Factory: `rentpro.gps.get_provider()` — returns configured provider based on GeoFleete Settings
  - TraccarProvider placeholder ready for implementation
- **MockProvider** — Realistic fleet data simulation
  - Simulates vehicle movement with heading variation and speed changes
  - Fuel consumption, battery drain, GPS signal strength, accuracy
  - Geofence boundary detection (entry/exit events)
  - Maintenance reminders (oil change, tire rotation, low fuel)
  - In-memory position history cache (500 positions per vehicle)
  - Haversine distance calculation for geofence checks
- **GeoFleete Settings DocType** (Single) — Configuration hub
  - Enable/disable GeoFleete, select GPS provider (Mock/Traccar)
  - Mock mode with simulation parameters (lat/lng, speed factor, fuel consumption)
  - Alert thresholds (low fuel, speed limit, idle time, low battery)
  - "Coming Soon" banner for external integrations
- **GPS Position DocType** — Vehicle position tracking
  - 16 fields: vehicle, coordinates, speed, heading, altitude, accuracy, ignition, fuel, battery, GPS signal
  - Coordinate validation (-90/90 lat, -180/180 lng)
  - Speed validation (0-300 km/h)
- **Geofence Zone DocType** — Geofence area definition
  - 12 fields: zone_name, zone_type, coordinates, radius, speed limit, alert settings
  - 5 zone types: Depot, Customer Zone, Restricted, Speed Limit, Airport
  - Circle and Polygon boundary types
- **Geofence Alert DocType** — Geofence event records
  - 15 fields: vehicle, zone, alert_type, position, speed, severity, acknowledgement
  - 5 alert types: Entry, Exit, Speed Violation, Unauthorized Use, Prolonged Stay
  - Auto-severity based on alert type
  - Acknowledge method with notes
- **Vehicle Tracking DocType** — Current vehicle state snapshot
  - 12 fields: vehicle, status, position, telemetry, mileage, provider
  - Statuses: Online, Offline, Idle, Moving, Maintenance
  - update_from_position() method for real-time updates
- **GeoFleete UI Pages** — 6 complete pages
  - Map View: Leaflet.js map with vehicle markers and geofence circles
  - Vehicle Status: Real-time telemetry table (speed, fuel, battery, ignition, GPS)
  - Alerts: View and acknowledge geofence alerts with severity indicators
  - Maintenance: Vehicle maintenance reminders with priority
  - Dashboard: Fleet KPIs (total, moving, idle, offline, fuel avg, alerts)
  - Geofences: Geofence zone listing with type indicators
- **GPS API Layer** — 8 whitelisted methods for UI consumption
  - get_fleet_positions, get_all_vehicle_states, get_active_geofences
  - get_recent_alerts, acknowledge_alert, get_maintenance_alerts
  - get_fleet_summary, simulate_fleet_movement
- **6 Dashboard Number Cards**
  - Tracked Vehicles, Moving Vehicles, Active Geofence Alerts
  - Active Geofence Zones, Fleet Fuel Average
- **22 Tests** — GPS position, geofence zone, geofence alert, vehicle tracking, MockProvider, settings, provider factory
- **Scheduled Job** — geofleete_heartbeat runs every 5 minutes (mock mode only)

### Changed

- Updated hooks.py with Geofence Alert doc_events and every_five_minutes scheduled job
- Updated tasks.py with geofleete_heartbeat and _geofleete_simulation_job
- Updated ROADMAP.md Phase 4 GeoFleete marked DONE

## [0.6.0] - 2026-07-15

### Added

- **Document Record DocType** — Complete paperless document management
  - Fields: document_number, customer, vehicle, contract, document_type, document_name, issuing_country, issuing_authority, issue_date, expiry_date, ocr_enabled, ocr_status, extracted fields, attachment, thumbnail, status, notes, uploaded_by, uploaded_at
  - 8 document types: National ID, Passport, Driver License, Residence Permit, Registration Card, Insurance Certificate, Technical Inspection, Ownership Document
  - Statuses: Active, Expired, Archived (with enforced transitions)
  - Automatic status detection on expiry date
- **Document Audit Log** — Child table tracking all document actions
  - Actions tracked: Upload, Modification, OCR Execution, Manual Correction, Download, Archive, Deletion Request, Status Change
  - Records performer and timestamp for each action
- **OCR Service Abstraction** — Pluggable OCR provider layer
  - Built-in: Tesseract (with pytesseract)
  - Optional: Google Vision (google-cloud-vision), Azure OCR (azure-ai-documentintelligence)
  - Extracts: Full Name, Document Number, Expiry Date, Date of Birth, License Number, Country
  - Regex-based field parsing from raw OCR text
  - Graceful fallback: provider unavailable → mock result (no upload blocking)
- **OCR Manual Correction** — correct_ocr_field() method for human review
  - Sets ocr_status to "Manual Review"
  - Logs correction in audit trail
- **Expiration Monitoring** — Multi-threshold alert system
  - Alerts at 30, 15, 7, and 1 day(s) before expiry
  - Covers: customer documents, vehicle insurance, technical inspection
  - Creates Notification Log entries
  - Hourly check for document records, daily check for vehicle expiry
- **5 Dashboard Number Cards**
  - Total Documents, Expiring in 30 Days, Expired Documents, OCR Success Rate, Documents Uploaded Today
- **19 Tests** — Creation, autoname, date validation, status transitions, OCR correction, audit trail, document types, archive method

### Changed

- Updated hooks.py with Document Record doc_events and hourly scheduled job
- Updated tasks.py with document expiration monitoring (_check_document_expirations, _check_vehicle_expiry_warnings)
- Updated ROADMAP.md Phase 3 OCR and Document Management marked DONE

## [0.5.0] - 2026-07-15

### Added

- **Payment Transaction DocType** — Cash receipt tracking with contract linkage
  - Fields: transaction_number, contract, customer, amount, currency (MAD), payment_method, transaction_date, reference_number, status, notes
  - 7 payment methods: Cash, Credit Card, Bank Transfer, Mobile Payment, Payzone, Cash Plus, Check
  - Statuses: Pending, Completed, Refunded, Cancelled
  - Contract payment status auto-updates on completion/refund
  - Cannot edit amount after completion
- **Expense Entry DocType** — Fleet expense tracking with category breakdown
  - Fields: entry_number, expense_date, category, vehicle, contract, amount, currency (MAD), vendor, reference_number, status, notes, attachments
  - 10 expense categories: Fuel, Maintenance, Insurance, Tolls, Parking, Cleaning, Tires, Battery, Body Work, Other
  - Statuses: Draft, Approved, Rejected, Paid
  - Vehicle or contract linkage optional
- **8 Financial Reports**
  - Revenue by Month, Revenue by Vehicle, Revenue by Agency
  - Outstanding Payments Report, Expenses by Category
  - Profitability Report, TVA Summary, Fleet Utilization Report
- **6 Finance Dashboard Number Cards**
  - Monthly Revenue, Monthly Expenses, Outstanding Balance, Net Profit
  - Contracts Paid Today, Fleet Utilization (Finance)
- **Payment Transaction List View** — 7 columns with status/method indicators
- **Expense Entry List View** — 7 columns with category/status indicators
- **14 New Tests** — Payment Transaction (14): creation, autoname, currency, amount validation, contract linkage, customer mismatch, status transitions, payment methods, read-only behavior. Expense Entry (14): creation, autoname, currency, amount validation, status transitions, category validation

### Changed

- Updated hooks.py with Payment Transaction and Expense Entry doc_events
- Added .flake8 configuration (max-line-length=110 to match black)

### Fixed

- All hooks resolve correctly (16/16)
- Full project lint passes (black, isort, flake8)

## [0.4.0] - 2026-07-15

### Added

- **Rental Contract DocType** — Complete implementation with 30+ fields
  - Identification: contract_number, reservation, customer, vehicle, agency
  - Dates: contract_date, pickup_datetime, expected_return_datetime, actual_return_datetime
  - Vehicle Condition: pickup/return mileage, fuel level, notes
  - Financial: daily_rate, number_of_days, subtotal, discount, tva_rate, tva_amount, additional_charges, late_return_fee, damage_fee, deposit_amount, grand_total
  - Payment: payment_status (Unpaid/Partial/Paid/Refunded)
  - Status: Draft, Active, Completed, Cancelled
  - Signatures: customer_signature, agency_signature, attachments
- **Moroccan TVA Support** — Built-in rates: 20%, 14%, 10%, 7%, 0%
- **TVA Calculation Engine** — Automatic taxable amount and TVA computation
- **Sales Invoice Integration** — Auto-creates invoice on contract activation
- **Vehicle Status Automation** — Draft→Reserved, Active→Rented, Completed/Cancelled→Available
- **Contract Status Workflow** — Draft → Active → Completed, with Cancelled path
- **5 Dashboard Number Cards** — Total Contracts, Active, Completed Today, Revenue This Month, Outstanding Payments
- **List View** — 7 columns with status indicators
- **Print Format** — "Rent Pro Standard Contract" with agency/customer info, vehicle details, financial summary, TVA breakdown, signatures, terms
- **Rental Agent Role** — New custom role for contract desk staff
- **33 Tests** — TVA calculations, financial calculations, status transitions, vehicle status updates, invoice creation, mileage/fuel validation, read-only behavior

### Changed

- Updated hooks.py with Rental Contract doc_events (on_update, on_submit, on_cancel)
- Updated install.py with Rental Agent role and Sales Invoice custom field
- Updated uninstall.py with Rental Agent role and custom field cleanup
- Updated DATABASE.md Rental Contract section to match implementation
- Updated ROADMAP.md Phase 2 Contracts marked DONE

## [0.3.0] - 2026-07-15

### Added

- **Reservation DocType** — Complete implementation with 17 fields
  - Core: reservation_number, customer, vehicle, agency
  - Dates: reservation_date, pickup_date, expected_return_date
  - Financial: daily_rate, number_of_days, discount, deposit_amount, estimated_total
  - Status: Draft, Confirmed, Picked Up, Completed, Cancelled, No Show
  - Metadata: notes, created_by, active
- **Reservation Status Workflow** — Draft → Confirmed → Picked Up → Completed, with Cancelled and No Show paths
- **Reservation Controller Validations** — Vehicle/customer existence, date validation, overlap detection, deposit limits, status transitions, terminal state protection
- **Overlap Detection** — SQL-based double-booking prevention for Confirmed/Picked Up reservations
- **Vehicle Status Integration** — Confirmed→Reserved, Picked Up→Rented, Completed→Available, Cancelled→Available, No Show→Available
- **5 Dashboard Number Cards** — Total Reservations, Active, Upcoming Pickups, Today's Returns, Cancelled
- **Reservation List View** — 7 columns with status indicators
- **Reservation Agent Role** — New custom role for reservation desk staff
- **25 Tests** — CRUD, date validation, overlap detection, status transitions, financial calculations, vehicle status updates, terminal state protection

### Changed

- Updated hooks.py with Reservation doc_events
- Updated install.py with Reservation Agent role creation
- Updated uninstall.py with Reservation Agent role cleanup
- Updated DATABASE.md Reservation section to match implementation
- Updated ROADMAP.md Phase 2 Reservations marked DONE

## [0.2.0] - 2026-07-15

### Added

- **Vehicle DocType** — Complete implementation with 22 fields
  - Core: plate_number, vin, make, model, year, color, category
  - Operations: status, current_mileage, fuel_type, transmission, seats, agency
  - Financial: daily_rate, weekly_rate, monthly_rate, deposit_amount
  - Compliance: insurance_expiry, technical_inspection_expiry, registration_expiry
  - Metadata: active, notes
- **Vehicle Status Workflow** — Available → Reserved → Rented → Available, with Maintenance, Sold (terminal), Inactive
- **Vehicle Controller Validations** — Year ≤ current year, daily rate ≥ 0, mileage ≥ 0, expiry dates ≥ today, status transitions enforced
- **Vehicle Category DocType** — Categories with daily rate multiplier and security deposit
- **Vehicle Document Child Table** — Document tracking for vehicle files
- **4 Dashboard Number Cards** — Total Vehicles, Available, Rented, In Maintenance
- **Vehicle List View** — Status, daily rate, insurance expiry display
- **35 Tests** — CRUD, uniqueness, status transitions, validations, edge cases

### Changed

- Removed phantom fixture references from hooks.py
- Updated DATABASE.md with Vehicle field definitions and status workflow
- Updated ROADMAP.md to mark Phase 1 Vehicles as DONE

### Fixed

- All 14 hooks resolve correctly
- Lint compliance: black, isort, flake8 all pass

## [0.1.0] - 2026-07-14

### Added

- Initial app scaffold
- Rent Pro Settings DocType with validation and permissions
- Custom roles: Manager, User, Fleet Manager, Finance, Read Only
- Setup module: install, uninstall, migrate lifecycle
- Scheduled tasks: document expiry checks
- Boot session extension
- Translations: EN, FR, AR
- Public assets: CSS, JS
- Documentation: installation, user guide, development guide
- Project docs: ROADMAP, MILESTONES, RISKS, TREE, GIT_STRATEGY, DATABASE, ERPNEXT_ARCHITECTURE
- CI pipeline: lint, test, build
- Pre-commit hooks: black, isort, flake8
