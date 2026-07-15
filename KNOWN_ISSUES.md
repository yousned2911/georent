# Rent Pro v1.0 — Known Issues

**Last Updated:** 2026-07-15
**Severity Legend:** CRITICAL | HIGH | MEDIUM | LOW

---

## CRITICAL Issues (Must Fix Before Production)

### KI-001: DocType Name Collision — Vehicle
**Severity:** CRITICAL
**Module:** Vehicles
**Description:** `Vehicle` DocType collides with ERPNext's built-in `Vehicle` DocType. Installing rentpro will override/overwrite the core DocType, breaking ERPNext Fleet module functionality.
**Impact:** ERPNext core Fleet module will not function. Marketplace submission will be rejected.
**Fix:** Rename to `Rent Pro Vehicle` or convert to Custom Fields on ERPNext's existing Vehicle DocType.

### KI-002: DocType Name Collision — Expense Entry
**Severity:** CRITICAL
**Module:** Finance
**Description:** `Expense Entry` DocType collides with ERPNext's built-in `Expense Entry` DocType.
**Impact:** ERPNext core expense functionality will be overridden.
**Fix:** Rename to `Rent Pro Expense Entry` or `Fleet Expense Entry`.

### KI-003: Multi-Tenancy — GPS API Cross-Tenant Data Leak
**Severity:** CRITICAL
**Module:** GeoFleete
**Description:** All 8 GPS API whitelisted endpoints in `gps/api.py` have zero permission checks and no agency filtering. Any logged-in user can access all agencies' vehicle positions, geofences, and alerts.
**Impact:** Complete tenant data exposure for fleet tracking data.
**Files:** `gps/api.py:7-193`
**Fix:** Add agency filtering to all GPS queries and permission checks to all whitelisted endpoints.

### KI-004: Multi-Tenancy — 8 Reports Expose Cross-Tenant Data
**Severity:** CRITICAL
**Module:** Reports
**Description:** 7 of 8 financial reports query data without agency filtering. Expense Entry and Payment Transaction DocTypes lack agency fields entirely.
**Impact:** Agency A can see Agency B's revenue, expenses, TVA, and profitability data.
**Files:** All 8 report `.py` files
**Fix:** Add agency WHERE clauses to all report queries, or restrict report access to super admin only.

### KI-005: Multi-Tenancy — Missing agency Field on 3 DocTypes
**Severity:** CRITICAL
**Module:** Finance/GeoFleete
**Description:** `Expense Entry`, `Payment Transaction`, and `Vehicle Tracking` lack an `agency` field, making per-tenant data isolation impossible.
**Impact:** Financial and tracking data cannot be scoped to tenants.
**Fix:** Add `agency` Link field to all three DocTypes with proper default values and mandatory constraints.

### KI-006: GPS API Write Endpoint Without Permission Check
**Severity:** CRITICAL
**Module:** GeoFleete
**Description:** `simulate_fleet_movement()` in `gps/api.py:175` is a whitelisted write endpoint with no permission check. Any user can create GPS positions and geofence alerts.
**Impact:** Arbitrary data creation in production systems.
**Fix:** Add role-based permission check (Rent Pro Fleet Manager or System Manager).

### KI-007: Impersonation Without Session Restoration
**Severity:** CRITICAL
**Module:** Super Admin
**Description:** `impersonate_user()` in `super_admin/support_tools.py:123` sets `frappe.session.user` directly without session restoration. If called from non-API code path, it causes full privilege escalation.
**Impact:** Potential privilege escalation.
**Fix:** Implement session context manager with automatic restoration.

---

## HIGH Issues (Fix Before Production)

### KI-008: Translation Coverage — Only 49 Keys
**Severity:** HIGH
**Module:** i18n
**Description:** Translation CSVs contain only 49 keys. The codebase has 86+ `frappe._()` calls and 50+ `__()` calls, none of which have translations.
**Impact:** French and Arabic users see English fallback text for all validation messages, toasts, and labels.
**Fix:** Extract all translatable strings and add to en.csv, fr.csv, ar.csv.

### KI-009: Print Format — English Only
**Severity:** HIGH
**Module:** Contracts
**Description:** The rental contract print format is hardcoded in English with LTR layout. No Arabic/RTL support.
**Impact:** Moroccan agencies cannot generate bilingual or Arabic contracts.
**Fix:** Add Jinja language conditionals and RTL CSS support.

### KI-010: RTL CSS — Minimal
**Severity:** HIGH
**Module:** CSS
**Description:** Only one RTL CSS rule exists (`[dir="rtl"] .rent-pro-container`). Dashboard cards, tables, status badges, and map containers lack RTL support.
**Impact:** Arabic UI is misaligned and unreadable in many components.
**Fix:** Add comprehensive RTL CSS rules.

### KI-011: XSS Vulnerabilities in GeoFleete JS
**Severity:** HIGH
**Module:** GeoFleete
**Description:** All GeoFleete JS pages inject server data into DOM via `innerHTML` without escaping. `alerts.js:54` injects user-authored `resolution_notes` as raw HTML.
**Impact:** Stored XSS if a user enters malicious HTML in alert resolution notes.
**Files:** `public/js/geofleete/*.js`
**Fix:** Use `frappe.utils.escape_html()` or DOM text nodes.

### KI-012: Tenant Isolation Check — Broken Orphan Detection
**Severity:** HIGH
**Module:** Super Admin
**Description:** `_find_orphan_records()` in `super_admin/tenant_management.py:125` has `pass` instead of appending violations. Always returns empty.
**Impact:** Tenant isolation verification silently gives false positives.
**Fix:** Replace `pass` with violation append logic.

### KI-013: 7 Missing __init__.py Files
**Severity:** HIGH
**Module:** Various
**Description:** 7 DocType directories are missing `__init__.py`: expense_entry, feature_flag, payment_transaction, reservation, super_admin_audit_log, super_admin_settings, system_health_settings.
**Impact:** May cause import errors in some Frappe configurations.
**Fix:** Add empty `__init__.py` to all 7 directories.

### KI-014: No App Icon
**Severity:** HIGH
**Module:** Marketplace
**Description:** No app icon exists in `public/images/`. Required for ERPNext Marketplace listing.
**Fix:** Add 512x512 PNG icon.

### KI-015: setup.py Not in App Directory
**Severity:** HIGH
**Module:** Installation
**Description:** `setup.py` and `requirements.txt` are at repo root, not inside `rentpro/`. `bench get-app` may fail.
**Fix:** Move into `rentpro/` package directory.

---

## MEDIUM Issues

### KI-016: Scheduled Tasks Lack Agency Filtering
**Severity:** MEDIUM
**Module:** Tasks
**Description:** Background tasks (`_check_document_expiries_job`, `_check_vehicle_expiry_warnings`, `_check_document_expirations`, `_geofleete_simulation_job`) query ALL records without agency filtering.
**Impact:** Performance issues at scale; cross-tenant data processing.
**Fix:** Iterate over agencies and scope each query.

### KI-017: Notification Targeting in Background Jobs
**Severity:** MEDIUM
**Module:** Tasks
**Description:** `_create_notification()` targets `frappe.session.user` which is Administrator in background scheduler context. Notifications never reach agency users.
**Impact:** Users don't receive expiry warnings or alerts.
**Fix:** Store user reference per record and notify that user directly.

### KI-018: 9+ Hardcoded Python Strings
**Severity:** MEDIUM
**Module:** Various
**Description:** Multiple user-facing strings not wrapped in `frappe._()`.
**Impact:** Cannot be translated.
**Files:** `gps/api.py:181`, `super_admin/system_health.py:93-146`, `gps/mock_provider.py:257`

### KI-019: 10+ Hardcoded JS Strings
**Severity:** MEDIUM
**Module:** GeoFleete
**Description:** Dashboard labels, status text, and zone types hardcoded in English.
**Impact:** Cannot be translated.
**Files:** `public/js/geofleete/dashboard.js:29-63`, `alerts.js:28`, etc.

### KI-020: 88 Uses of ignore_permissions=True
**Severity:** MEDIUM
**Module:** Various
**Description:** Excessive use of `ignore_permissions=True` across the codebase, including production code.
**Impact:** Bypasses Frappe's permission system. Marketplace reviewers may flag.
**Fix:** Replace with proper permission checks where possible.

### KI-021: No File Upload Validation
**Severity:** MEDIUM
**Module:** OCR/Various
**Description:** No application-level file type or size validation on Attach fields.
**Impact:** Users could upload malicious files.
**Fix:** Add file type whitelist and size limits.

### KI-022: Vehicle Category Permission Too Open
**Severity:** MEDIUM
**Module:** Vehicles
**Description:** `Rent Pro User` role can create/modify Vehicle Categories. Should be Manager+ only.
**Fix:** Remove write/create from Rent Pro User role.

### KI-023: No Form.js Files
**Severity:** MEDIUM
**Module:** All
**Description:** No `_form.js` files exist for any DocType. All JS customizations are list-only.
**Impact:** No client-side validation or form UX enhancements.

---

## LOW Issues

### KI-024: Empty www/ and templates/ Directories
**Severity:** LOW
**Module:** Web
**Description:** Empty web template directories exist but contain no pages.
**Fix:** Remove or populate.

### KI-025: migrate.py Stubs
**Severity:** LOW
**Module:** Setup
**Description:** `before_migrate()` and `after_migrate()` are empty pass-throughs.
**Fix:** Implement or document as intentional.

### KI-026: patches.txt Empty
**Severity:** LOW
**Module:** Setup
**Description:** No migration patches defined.
**Fix:** Acceptable for v1.0; add patches for future schema changes.

### KI-027: uninstall.py Stale References
**Severity:** LOW
**Module:** Setup
**Description:** Uninstall references 2 custom fields (`Customer_rent_pro_customer_id`, `Employee_rent_pro_employee_id`) not created by install.py.
**Fix:** Remove stale references or add to install.py.

### KI-028: public/images/ Empty
**Severity:** LOW
**Module:** Assets
**Description:** No image assets.
**Fix:** Add app icon and any required images.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 7 |
| HIGH | 8 |
| MEDIUM | 8 |
| LOW | 5 |
| **Total** | **28** |
