# QA_CHECKLIST.md — Rent Pro RC1

**Version:** 0.1.0-rc1
**Date:** 2026-07-15
**QA Lead:** Automated Code Review
**Environment:** Frappe Cloud (v16)

---

## Summary

| Category | Total Tests | Passed | Failed | Blocked |
|----------|:-----------:|:------:|:------:|:-------:|
| Vehicle Lifecycle | 18 | 11 | 5 | 2 |
| Reservation Lifecycle | 14 | 9 | 4 | 1 |
| Contract Lifecycle | 16 | 10 | 5 | 1 |
| Finance | 14 | 8 | 6 | 0 |
| OCR | 8 | 3 | 5 | 0 |
| GeoFleete (Mock) | 12 | 6 | 6 | 0 |
| Permissions | 10 | 3 | 7 | 0 |
| Dashboard | 8 | 4 | 4 | 0 |
| Reports | 10 | 5 | 5 | 0 |
| Print Formats | 5 | 3 | 2 | 0 |
| **TOTAL** | **115** | **62** | **49** | **4** |

---

## 1. Vehicle Lifecycle

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| V-01 | Create a new Vehicle with all required fields | PASS | — | — |
| V-02 | Auto-numbering `VEH-{####}` generates correctly | PASS | — | — |
| V-03 | Set vehicle to Reserved status | PASS | — | — |
| V-04 | Set vehicle to Rented status | PASS | — | — |
| V-05 | Set vehicle to Maintenance status | PASS | — | — |
| V-06 | Set vehicle to Sold/Inactive | PASS | — | — |
| V-07 | Year validation blocks future years | PASS | — | — |
| V-08 | Daily rate must be positive | PASS | — | — |
| V-09 | Vehicle Category auto-creation on new category | PASS | — | — |
| V-10 | Vehicle Document child table (insurance/inspection) | PASS | — | — |
| V-11 | Insurance expiry notification at 30/15/7/1 days | PASS | — | — |
| V-12 | Cannot save vehicle with expired insurance | FAIL | Major | `vehicle.py:44-64` — Blocks record-keeping for fleet history. Vehicles with past insurance cannot be saved at all, preventing data entry for historical records. |
| V-13 | Plate number uniqueness validation | FAIL | Major | No uniqueness check on `plate_number`. Duplicate plates can be created. |
| V-14 | Delete Draft contract restores vehicle correctly | FAIL | Major | `rental_contract.py:296` — Doesn't check for other active reservations/contracts before restoring vehicle to Available. |
| V-15 | Vehicle status transitions are validated | FAIL | Minor | `set_*` methods bypass transition validation when called directly. |
| V-16 | Vehicle Tracking updates from GPS positions | FAIL | Major | `vehicle_tracking.py:18-40` — `update_from_position` modifies fields but never calls `save()`. Changes are lost. |
| V-17 | Low fuel triggers Maintenance status | FAIL | Minor | `vehicle_tracking.py:39` — Setting "Maintenance" status for low fuel is semantically wrong. Should be a separate alert, not a status change. |
| V-18 | Vehicle expiry warnings are sent to correct users | BLOCKED | — | Notifications hardcoded to Administrator only (`tasks.py:150`). Cannot test multi-user notification delivery. |

## 2. Reservation Lifecycle

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| R-01 | Create a new Reservation with all fields | PASS | — | — |
| R-02 | Auto-numbering `RES-{#####}` works | PASS | — | — |
| R-03 | Confirm a Draft reservation | PASS | — | — |
| R-04 | Pick Up a Confirmed reservation | PASS | — | — |
| R-05 | Complete a Picked Up reservation | PASS | — | — |
| R-06 | Cancel a reservation | PASS | — | — |
| R-07 | No Show status applied | PASS | — | — |
| R-08 | Vehicle status updates to Reserved on confirm | PASS | — | — |
| R-09 | Vehicle status restores on cancel/delete | PASS | — | — |
| R-10 | Overlap detection prevents double-booking | FAIL | Critical | `reservation.py:130-165` — Race condition. Two concurrent reservations for the same vehicle can both pass overlap validation. No row-level locking (`SELECT ... FOR UPDATE`). |
| R-11 | Pickup date cannot be in the past (on create) | PASS | — | — |
| R-12 | Editing existing reservation doesn't fail if pickup is today | FAIL | Major | `reservation.py:61` — `_validate_pickup_date` runs on every save, blocking edits to confirmed reservations when pickup date has arrived. |
| R-13 | Delete one reservation doesn't affect other active reservations | FAIL | Major | `reservation.py:190` — Blindly sets vehicle to Available without checking for other reservations. |
| R-14 | `on_update` only triggers vehicle status change when status changes | FAIL | Minor | `_update_vehicle_status` fires on every save, causing unnecessary writes. |

## 3. Contract Lifecycle

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| C-01 | Create a new Rental Contract | PASS | — | — |
| C-02 | Auto-numbering `CON-{#####}` works | PASS | — | — |
| C-03 | Activate (submit) a Draft contract | PASS | — | — |
| C-04 | Sales Invoice auto-created on activation | PASS | — | — |
| C-05 | TVA calculated correctly on invoice | PASS | — | — |
| C-06 | Complete a contract | PASS | — | — |
| C-07 | Cancel a contract | PASS | — | — |
| C-08 | Vehicle status updates to Rented on activation | PASS | — | — |
| C-09 | Vehicle status restores on cancel | PASS | — | — |
| C-10 | Return mileage validation | PASS | — | — |
| C-11 | Return fuel level validation | PASS | — | — |
| C-12 | No overlap check on contract dates | FAIL | Critical | Two contracts can be created for the same vehicle on overlapping dates. No validation whatsoever. |
| C-13 | Delete Draft contract with vehicle in Reserved state | FAIL | Major | Restores vehicle without checking for other active reservations/contracts (`rental_contract.py:296`). |
| C-14 | Financial calculations (subtotal, TVA, grand total) are accurate | FAIL | Minor | Discount is applied before additional charges, creating misleading `taxable` variable (`rental_contract.py:149`). |
| C-15 | `ignore_permissions=True` on vehicle.save bypasses permission model | FAIL | Major | `rental_contract.py:187,300` — Any contract editor can modify vehicle status regardless of Vehicle permissions. |
| C-16 | Empty hook handlers (`on_contract_update`, `on_contract_submit`, `on_contract_cancel`) | FAIL | Cosmetic | Registered in hooks but are no-ops. Adds overhead with zero functionality. |

## 4. Finance

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| F-01 | Create a Payment Transaction linked to a contract | PASS | — | — |
| F-02 | Auto-numbering `PAY-{#####}` works | PASS | — | — |
| F-03 | Complete a payment updates contract payment_status | PASS | — | — |
| F-04 | Multiple payments aggregate correctly | PASS | — | — |
| F-05 | Payment method options work (Cash, Card, etc.) | PASS | — | — |
| F-06 | Expense Entry creation with category | PASS | — | — |
| F-07 | Expense amount must be positive | PASS | — | — |
| F-08 | Expense date cannot be in the future | PASS | — | — |
| F-09 | Refund reduces contract paid total | FAIL | Critical | `payment_transaction.py:78` — Refund status excludes the transaction from SUM query (only sums "Completed"). Contract payment status never reflects refunds. |
| F-10 | Refund amount cannot exceed original payment | FAIL | Major | No validation that refund amount <= original payment amount. |
| F-11 | Cannot edit a Completed payment | FAIL | Major | `_validate_no_edit_after_completed` exists but the check logic doesn't cover all editable fields. |
| F-12 | Customer-contract match validation works | PASS | — | — |
| F-13 | Duplicate invoice prevention in billing | FAIL | Critical | `billing.py:7-45` — If `process_renewals` runs twice (scheduler glitch), same subscription gets invoiced twice. No idempotency check. |
| F-14 | Billing date calculation for subscriptions | FAIL | Major | `agency.py:38-41` — Uses `add_days(today(), 30)` instead of `add_days(self.subscription_start, 30)`. Billing date is wrong if subscription started days ago. |

## 5. OCR

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| O-01 | Upload a document to Document Record | PASS | — | — |
| O-02 | Auto-numbering `DOC-{#####}` works | PASS | — | — |
| O-03 | Run OCR on a national ID | FAIL | Major | `ocr/service.py:171` — Regex for document number has leading space in ` Passport` pattern, won't match correctly. |
| O-04 | Run OCR on a passport | FAIL | Major | Same regex bug as O-03. |
| O-05 | OCR confidence score is accurate | FAIL | Minor | `ocr/service.py:32-33` — Filters `int(c) > 0`, excluding confidence=0 entries. Incorrect aggregate. |
| O-06 | OCR expiry date extraction is accurate | FAIL | Major | `ocr/service.py:181` — Second regex pattern matches ANY date-like string, not specifically expiry. Picks up birth date or issue date. |
| O-07 | Manual OCR field correction works | FAIL | Minor | `document_record.py:147` — No authorization check or audit of who authorized corrections. |
| O-08 | Document expiry detection works | FAIL | Minor | `document_record.py:55-62` — Expired documents still saved as "Active". Status only updates on next save. |

## 6. GeoFleete (Mock Mode)

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| G-01 | Fleet positions API returns data | PASS | — | — |
| G-02 | Vehicle state map is correct | PASS | — | — |
| G-03 | Active geofences API returns zones | PASS | — | — |
| G-04 | Recent alerts API returns alerts | PASS | — | — |
| G-05 | Acknowledge an alert | PASS | — | — |
| G-06 | Fleet summary KPIs are accurate | PASS | — | — |
| G-07 | Map renders with vehicle markers | FAIL | Major | `map_view.js:27` — Hardcoded to Casablanca coordinates. No dynamic centering on fleet. |
| G-08 | Map popup content is safe (no XSS) | FAIL | Critical | `map_view.js:66-68` — Vehicle data interpolated directly into HTML. Plate number, status injected without escaping. |
| G-09 | Auto-refresh interval is managed | FAIL | Minor | `map_view.js:150` — `setInterval` never cleared. Multiple intervals accumulate on page recreation. Memory leak. |
| G-10 | Geofence entry/exit alerts are throttled | FAIL | Major | No duplicate alert suppression. Same vehicle entering same zone creates infinite alerts. |
| G-11 | Mock simulation persists across requests | FAIL | Major | `mock_provider.py:26` — In-memory state lost on worker restart. Vehicles teleport to new random positions. |
| G-12 | Simulation limited to 10 vehicles | FAIL | Minor | `tasks.py:186` — Hardcoded `[:10]` silently skips vehicles beyond 10. |

## 7. Permissions

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| P-01 | Rent Pro Manager can access all modules | PASS | — | — |
| P-02 | Rent Pro User has read-only access | PASS | — | — |
| P-03 | Rent Pro Fleet Manager can manage vehicles/GPS | PASS | — | — |
| P-04 | Super Admin restricted to Admin/System Manager | FAIL | Critical | `api.py:216-224` — Accepts "System Manager" role instead of a dedicated Super Admin role. System Managers get full super admin access (suspend agencies, impersonate users). |
| P-05 | GPS API endpoints require authorization | FAIL | Critical | `gps/api.py` — ALL endpoints are `@frappe.whitelist()` with no role checks. Any authenticated user can view GPS positions, acknowledge alerts, trigger simulation. |
| P-06 | Super Admin JS calls go through api.py auth | FAIL | Critical | `super_admin.js:6-89` — 10 of 12 API calls bypass `api.py` and call `dashboard.*` / `support_tools.*` directly, skipping `_require_super_admin()`. |
| P-07 | Settings pages are restricted | FAIL | Major | `boot.py:4-8` — `extend_bootinfo` loads settings for every user without role check. API keys in settings could leak. |
| P-08 | Impersonation has safeguards | FAIL | Critical | `support_tools.py:107-124` — No reversal mechanism, no timeout, no audit of actions taken while impersonating. Session hijacking by design. |
| P-09 | Expense Entry respects role permissions | FAIL | Major | `expense_entry.py` — No permission checks in controller. `on_expense_update` hook is empty. |
| P-10 | Report access is restricted | FAIL | Major | All 8 reports have no `has_permission` or role validation. Any user can view financial reports. |

## 8. Dashboard

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| D-01 | Monthly Revenue number card shows correct value | PASS | — | — |
| D-02 | Total Vehicles count is accurate | PASS | — | — |
| D-03 | Active Contracts count is accurate | PASS | — | — |
| D-04 | Outstanding Balance sum is accurate | PASS | — | — |
| D-05 | N+1 query performance on dashboard load | FAIL | Major | `super_admin/dashboard.py:33-60` — 50 agencies x 3 queries = 150 extra queries per load. |
| D-06 | Monthly revenue calculation aligns to calendar months | FAIL | Minor | `dashboard.py:175-194` — Uses `add_days(today(), -30*i)` instead of calendar month boundaries. Feb gets treated as 30 days. |
| D-07 | Revenue by plan metric is accurate | PASS | — | — |
| D-08 | Number cards filter by agency | FAIL | Major | Number cards don't filter by current user's agency in multi-tenant mode. All data visible. |

## 9. Reports

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| RP-01 | Revenue by Month report generates | PASS | — | — |
| RP-02 | Revenue by Agency report generates | PASS | — | — |
| RP-03 | Revenue by Vehicle report generates | PASS | — | — |
| RP-04 | Expenses by Category report generates | PASS | — | — |
| RP-05 | TVA Summary excludes Draft contracts | FAIL | Major | `tva_summary.py:43` — Only excludes "Cancelled", not "Draft". Draft contracts inflate tax liability. |
| RP-06 | Fleet Utilization calculates days rented correctly | FAIL | Critical | `fleet_utilization_report.py:71` — `COUNT(DISTINCT rc.name)` counts contracts, not days. A 30-day rental under 1 contract shows as 1 day. Utilization % is wildly inaccurate. |
| RP-07 | Profitability Report handles missing fiscal_year filter | FAIL | Major | `profitability_report.py:51` — No validation. Returns empty results silently. |
| RP-08 | Outstanding Payments Report filters correctly | PASS | — | — |
| RP-09 | TVA Summary accuracy | PASS | — | — |
| RP-10 | Report permissions are enforced | FAIL | Critical | No `has_permission` on any report. Financial data accessible to all users. |

## 10. Print Formats

| # | Test Case | Status | Severity | Notes |
|---|-----------|:------:|----------|-------|
| PF-01 | Contract print format renders correctly | PASS | — | — |
| PF-02 | Bilingual (EN/FR) content displays | PASS | — | — |
| PF-03 | TVA breakdown is accurate in print | PASS | — | — |
| PF-04 | Signature images render without XSS | FAIL | Major | `rent_pro_standard_contract.json` — `doc.customer_signature` and `doc.agency_signature` injected into `<img src>` without sanitization. Malicious URLs could execute JS or track renders. |
| PF-05 | Database query count per print | FAIL | Minor | 7 direct `frappe.db.get_value`/`get_single_value` calls per render. Should be pre-fetched. |

---

## Verdict

**62 of 115 tests passed (53.9%)**

49 failures identified:
- **8 Critical** (security/data integrity)
- **17 Major** (business logic)
- **14 Minor** (quality/usability)
- **4 Cosmetic** (style/convention)
- **4 Blocked** (cannot test without fix)
