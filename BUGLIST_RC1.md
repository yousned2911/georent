# BUGLIST_RC1.md — Rent Pro RC1

**Version:** 0.1.0-rc1
**Date:** 2026-07-15
**Total Bugs Found:** 49

---

## Critical (8)

| ID | Module | Location | Title | Description |
|----|--------|----------|-------|-------------|
| BUG-C01 | Finance | `payment_transaction.py:78` | **Refund does not reduce contract paid total** | When a payment is marked "Refunded", `_update_contract_payment_status` queries `SUM(amount) WHERE status='Completed'`. Refunded transactions are excluded from the sum, so `total_paid` never decreases. Contract payment_status remains "Paid" even after full refund. |
| BUG-C02 | Reservations | `reservation.py:130-165` | **Double-booking race condition** | Overlap detection uses a read-then-write pattern with no row-level locking. Two concurrent reservation requests for the same vehicle can both pass validation before either commits, creating overlapping reservations. |
| BUG-C03 | Contracts | `rental_contract.py` | **No date overlap check on contracts** | Reservations validate date overlap but rental contracts do not. Two active contracts can exist for the same vehicle on overlapping dates. This is a fundamental business logic gap. |
| BUG-C04 | Permissions | `gps/api.py` (all endpoints) | **GPS API has no authorization checks** | All 7 GPS API endpoints are `@frappe.whitelist()` with zero role validation. Any authenticated user can view all vehicle GPS positions, acknowledge security alerts, and trigger fleet simulation (`simulate_fleet_movement`). |
| BUG-C05 | Permissions | `super_admin.js:6-89` | **Super Admin JS bypasses auth checks** | 10 of 12 client-side API calls invoke `dashboard.*` and `support_tools.*` methods directly instead of going through `api.py`. The `api.py` wrapper has `_require_super_admin()` checks, but the direct calls skip them entirely. A non-admin user can suspend agencies, extend trials, and toggle feature flags from the browser console. |
| BUG-C06 | Security | `support_tools.py:107-124` | **Impersonation has no safeguards** | `impersonate_user()` sets `frappe.session.user = target_user` with no reversal mechanism, no timeout, no audit trail of actions performed while impersonating, and no limit on duration. After impersonation, ALL subsequent requests execute as the target user for the remainder of the session. |
| BUG-C07 | Security | `license_key.py:28` | **License signature is forgeable** | License data is signed with `hashlib.sha256(raw.encode()).hexdigest()[:32]` — a plain hash without an HMAC secret key. The raw payload is also stored in plaintext in `license_data`. Anyone can recompute a valid signature by reading the stored data. |
| BUG-C08 | Reports | `fleet_utilization_report.py:71` | **Fleet utilization counts contracts, not days** | `COUNT(DISTINCT rc.name) AS days_rented` counts the number of distinct rental contracts overlapping a month, NOT the actual number of days the vehicle was rented. A vehicle rented for 30 days under 1 contract shows `days_rented=1`. Utilization percentage is fundamentally wrong. |

---

## Major (17)

| ID | Module | Location | Title | Description |
|----|--------|----------|-------|-------------|
| BUG-M01 | Vehicles | `vehicle.py:44-64` | **Cannot save vehicle with expired insurance** | `_validate_dates` rejects saving a vehicle whose insurance has expired. This prevents record-keeping for fleet history — you cannot enter a vehicle into the system if its insurance documents are past expiry. |
| BUG-M02 | Vehicles | `vehicle.py` | **No plate number uniqueness check** | Multiple vehicles can be created with the same plate number. No uniqueness validation exists. |
| BUG-M03 | Contracts | `rental_contract.py:296` | **Deleting contract doesn't check other active records** | Deleting a Draft contract blindly restores the vehicle to "Available" without checking for other active reservations or contracts for the same vehicle. |
| BUG-M04 | Vehicles | `vehicle_tracking.py:18-40` | **update_from_position never saves** | `update_from_position` modifies `self` fields (status, fuel, odometer) but never calls `save()`. All telemetry updates are silently lost unless the caller explicitly saves. |
| BUG-M05 | Reservations | `reservation.py:61` | **Editing existing reservation fails when pickup is today** | `_validate_pickup_date` runs on every save (not just insert). A Confirmed reservation whose pickup date has arrived cannot be edited — any field change triggers the "pickup date in the past" validation error. |
| BUG-M06 | Reservations | `reservation.py:190` | **Deleting reservation doesn't check other active records** | Same as BUG-M03 — blindly restores vehicle to Available without checking for overlapping reservations. |
| BUG-M07 | Billing | `billing.py:7-45` | **No duplicate invoice prevention** | If `process_renewals` runs twice (scheduler glitch, manual trigger), the same subscription gets invoiced twice. No idempotency check on invoice generation. |
| BUG-M08 | Billing | `billing.py:67` | **Exception swallowed, renewal proceeds on failure** | `process_renewals` catches all exceptions and logs them, but still calls `subscription.renew()` even if invoice generation failed. Subscription renews without payment. |
| BUG-M09 | Finance | `payment_transaction.py` | **No refund amount validation** | No check that refund amount <= original payment amount. A user can refund more than was paid. |
| BUG-M10 | Finance | `agency.py:38-41` | **Billing date calculation uses today() instead of subscription start** | `_validate_trial_to_active` sets billing date as `add_days(today(), 30)` instead of `add_days(self.subscription_start, 30)`. If subscription started 5 days ago, billing is 30 days from now instead of 25. |
| BUG-M11 | OCR | `ocr/service.py:171` | **Passport regex pattern has leading space** | `r"(?:CIN\| Passport\|License)[.\s]*(\w{6,})"` has a space before "Passport". The pattern won't match "Passport" at a word boundary. |
| BUG-M12 | OCR | `ocr/service.py:181` | **Expiry date regex matches any date in document** | The second expiry pattern `r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"` matches ANY date-like string, not specifically the expiry date. It picks up birth dates, issue dates, etc. |
| BUG-M13 | Super Admin | `system_health.py:167,187,207` | **Health check exceptions treated as OK** | `_check_storage`, `_check_system_resources`, and `_check_failed_jobs` all return `{"status": "OK"}` on exception. Failures are silently treated as healthy. |
| BUG-M14 | GeoFleete | `map_view.js:27` | **Map hardcoded to Casablanca** | Leaflet map `setView([33.5731, -7.5898], 12)` is hardcoded. Should center on the fleet's centroid or be configurable. |
| BUG-M15 | GeoFleete | `geofence_alert.py` | **No duplicate alert suppression** | The same vehicle entering the same geofence zone creates infinite alerts with no throttling or deduplication. |
| BUG-M16 | SaaS | `agency_subscription.py:49` | **Renewal billing date uses missed date** | `renew()` sets `next_billing_date = add_days(self.next_billing_date, 30)`. If the billing date was missed, the next date is 30 days from the missed date, not from today. Creates perpetual catch-up loops. |
| BUG-M17 | Security | `super_admin/api.py:216-224` | **Super Admin accepts System Manager role** | `_require_super_admin()` grants access to any user with "System Manager" role, not a dedicated Super Admin role. System Managers get full super admin capabilities (suspend, impersonate, export). |

---

## Minor (14)

| ID | Module | Location | Title | Description |
|----|--------|----------|-------|-------------|
| BUG-N01 | Vehicles | `vehicle.py:90-113` | **set_* methods bypass status transition validation** | `set_reserved()`, `set_rented()`, etc. set status directly. The `_validate_status_transition` check relies on `get_doc_before_save()` which may return the same status if the doc was fetched fresh, causing a false pass. |
| BUG-N02 | Contracts | `rental_contract.py:149` | **Discount calculation is misleading** | Discount is applied before additional charges, and the `taxable` variable semantics are unclear. The double-count risk exists if SI items already reflect discounted rates. |
| BUG-N03 | GeoFleete | `vehicle_tracking.py:39` | **Low fuel sets "Maintenance" status** | Setting vehicle tracking status to "Maintenance" when fuel < 10% is semantically wrong. Low fuel should trigger an alert, not change the vehicle's operational status. |
| BUG-N04 | GeoFleete | `mock_provider.py:26` | **In-memory state lost on worker restart** | `_simulation_state = {}` is module-level. On Gunicorn worker restart, all state resets. Vehicles teleport to new random positions. |
| BUG-N05 | GeoFleete | `tasks.py:186` | **Simulation limited to 10 vehicles** | `list(states.keys())[:10]` silently skips vehicles beyond 10. No warning logged. |
| BUG-N06 | OCR | `ocr/service.py:32-33` | **Confidence calculation excludes 0-value entries** | Filters `int(c) > 0` which excludes confidence=0 entries from the average. Incorrect aggregate score. |
| BUG-N07 | OCR | `document_record.py:147` | **OCR correction has no authorization check** | Any user with write permission can modify OCR-extracted fields. No role check or audit of who authorized corrections. |
| BUG-N08 | SaaS | `feature_flag.py:39` | **Per-Agency flags return True when no agency specified** | When `scope` is "Per Agency" and no `agency_name` is provided, falls through to `return flag.enabled` which is always `True`. Defeats per-agency scoping. |
| BUG-N09 | Tasks | `tasks.py:150` | **Notifications hardcoded to Administrator** | `_create_notification` creates Notification Log entries only for "Administrator". No per-agency or per-role notification delivery. |
| BUG-N10 | Tasks | `tasks.py:83` | **Expiry warnings missed if task doesn't run on exact day** | Uses exact-match `[30, 15, 7, 1]` thresholds. If server downtime causes the daily task to skip a day, warnings for that threshold are permanently lost. |
| BUG-N11 | Dashboard | `dashboard.py:175-194` | **Monthly revenue misattributes to wrong months** | Uses `add_days(today(), -30*i)` instead of calendar month boundaries. February is treated as 30 days. Revenue is misattributed to wrong months. |
| BUG-N12 | GeoFleete | `map_view.js:150` | **Auto-refresh interval never cleared** | `setInterval` in `start_auto_refresh()` is never cleared on page destroy. Multiple intervals accumulate, causing memory leaks and duplicate API calls. |
| BUG-N13 | Settings | `rent_pro_settings.json` + `geofleete_settings.json` | **Duplicate GPS config fields** | `gps_update_interval` and `gps_retention_days` exist in both Rent Pro Settings and GeoFleete Settings. Values can diverge. No single source of truth. |
| BUG-N14 | Setup | `tasks.py:24` vs `rent_pro_settings.json` | **expiry_warning_days field read but never defined** | `getattr(settings, "expiry_warning_days", 30)` reads a field that doesn't exist in the settings JSON. Always falls back to default. |

---

## Cosmetic (4)

| ID | Module | Location | Title | Description |
|----|--------|----------|-------|-------------|
| BUG-X01 | Contracts | `rental_contract.py:303-315` | **Empty hook handlers registered** | `on_contract_update`, `on_contract_submit`, `on_contract_cancel` are registered in hooks but contain only `pass`. Adds overhead with zero functionality. |
| BUG-X02 | Reports | All 8 reports | **SQL fragment .format() pattern** | All reports use `.format(where_clause=...)` for SQL fragments. Values are parameterized and safe, but the pattern is fragile and inconsistent with best practices. |
| BUG-X03 | Print Format | `rent_pro_standard_contract.json` | **Hardcoded currency MAD** | All `fmt_money()` calls hardcode `currency="MAD"`. Not configurable for multi-currency deployments. |
| BUG-X04 | Print Format | `rent_pro_standard_contract.json` | **Hardcoded Terms & Conditions** | T&C are hardcoded in English. Not translated and not configurable per agency. |

---

## Summary

| Severity | Count | % |
|----------|:-----:|:-:|
| Critical | 8 | 16.3% |
| Major | 17 | 34.7% |
| Minor | 14 | 28.6% |
| Cosmetic | 4 | 8.2% |
| **Total** | **49** | **100%** |

---

## Top 5 Bugs Blocking Production Readiness

1. **BUG-C05** — Super Admin JS bypasses auth (any user can admin)
2. **BUG-C04** — GPS API has no authorization (location data exposed)
3. **BUG-C06** — Impersonation has no safeguards (session hijacking)
4. **BUG-C01** — Refunds don't reduce contract totals (financial inaccuracy)
5. **BUG-C08** — Fleet utilization report is fundamentally wrong
