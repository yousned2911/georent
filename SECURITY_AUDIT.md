# Rent Pro v1.0 — Security Audit Report

**Audit Date:** 2026-07-15
**Auditor:** Lead QA Engineer
**Severity:** CRITICAL overall — multiple vulnerabilities identified

---

## Executive Summary

The Rent Pro codebase has **7 CRITICAL**, **5 HIGH**, and **4 MEDIUM** security findings. The most severe issues involve cross-tenant data exposure in the GPS API and financial reports, unguarded write endpoints, and XSS vulnerabilities. The app is **NOT production-ready** from a security standpoint.

---

## Findings

### CRITICAL

#### SEC-001: Unguarded GPS API Write Endpoint
- **File:** `gps/api.py:175`
- **Function:** `simulate_fleet_movement()`
- **Issue:** Whitelisted write endpoint with zero permission checks. Any authenticated user can create GPS positions and geofence alerts for any vehicle.
- **CVSS:** 9.1 (Critical)
- **Fix:** Add `frappe.has_permission("Vehicle", "write")` check or restrict to Fleet Manager role.

#### SEC-002: Cross-Tenant GPS Data Exposure
- **File:** `gps/api.py:7-193`
- **Functions:** All 8 whitelisted endpoints
- **Issue:** No agency filtering on any GPS query. Agency A can see all vehicles, positions, geofences, and alerts for Agency B.
- **CVSS:** 8.6 (High)
- **Fix:** Add `agency` parameter and filter all queries by current user's agency.

#### SEC-003: Cross-Tenant Financial Data Exposure
- **Files:** All 8 report `.py` files
- **Issue:** Financial reports query data without agency filtering. Expense Entry and Payment Transaction lack agency fields.
- **CVSS:** 8.6 (High)
- **Fix:** Add agency WHERE clauses or restrict reports to super admin.

#### SEC-004: Session User Direct Manipulation
- **File:** `super_admin/support_tools.py:123`
- **Code:** `frappe.session.user = target_user`
- **Issue:** Direct session manipulation without context manager. If called from any non-API path, causes full privilege escalation.
- **CVSS:** 9.0 (Critical)
- **Fix:** Implement session context manager:
  ```python
  from contextlib import contextmanager
  @contextmanager
  def impersonate(user):
      old_user = frappe.session.user
      frappe.session.user = user
      try:
          yield
      finally:
          frappe.session.user = old_user
  ```

#### SEC-005: Unescaped User Input in DOM (XSS)
- **Files:** `public/js/geofleete/alerts.js:54`, `dashboard.js:102-118`, `map_view.js:91-98`
- **Issue:** Server data injected via `innerHTML` without sanitization. `resolution_notes` (free-form user text) is injected as raw HTML.
- **CVSS:** 7.5 (High)
- **Fix:** Use `frappe.utils.escape_html()` or DOM text nodes:
  ```javascript
  // Before (unsafe)
  container.innerHTML = `<p>${data.resolution_notes}</p>`;
  // After (safe)
  const p = document.createElement('p');
  p.textContent = data.resolution_notes;
  container.appendChild(p);
  ```

#### SEC-006: Alert Acknowledgement Without Authorization
- **File:** `gps/api.py:123`
- **Function:** `acknowledge_alert()`
- **Issue:** Any user can acknowledge any geofence alert across all agencies.
- **CVSS:** 7.5 (High)
- **Fix:** Add agency check: verify alert belongs to user's agency.

#### SEC-007: ignore_permissions=True Overuse
- **Files:** 88 instances across codebase
- **Issue:** Bypasses Frappe's permission system. Production code uses `ignore_permissions=True` for vehicle status updates, invoice creation, GPS saves, etc.
- **CVSS:** 6.5 (Medium-High)
- **Fix:** Replace with proper permission checks. Reserve `ignore_permissions` for install/uninstall only.

---

### HIGH

#### SEC-008: No File Upload Validation
- **Files:** All `Attach` fields (6 DocTypes)
- **Issue:** No file type whitelist or size limits. Users can upload executables, scripts, or oversized files.
- **Fix:** Add `before_insert` validation:
  ```python
  ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
  MAX_SIZE = 10 * 1024 * 1024  # 10MB
  ```

#### SEC-009: SQL Injection — SAFE
- **Files:** 12 `frappe.db.sql()` calls checked
- **Issue:** None. All queries use parameterized `%s` or `%(key)s` placeholders.
- **Status:** ✅ PASS

#### SEC-010: Hardcoded Secrets — SAFE
- **Files:** Full codebase scan
- **Issue:** None found. No passwords, API keys, or tokens hardcoded.
- **Status:** ✅ PASS

#### SEC-011: CSRF Protection — SAFE
- **Files:** All write operations
- **Issue:** None. All mutations use `@frappe.whitelist()` or `frappe.call()`, which enforce CSRF tokens.
- **Status:** ✅ PASS

#### SEC-012: Missing Role-Based Access on Super Admin
- **Files:** `super_admin/api.py`
- **Issue:** All 18 endpoints check for `System Manager` role. However, the role check logic could be stricter (e.g., dedicated `Rent Pro Super Admin` role).
- **Fix:** Consider creating a dedicated role.

---

### MEDIUM

#### SEC-013: Vehicle Category Permission Too Open
- **File:** `vehicle_category.json:70-74`
- **Issue:** `Rent Pro User` role has write/create permissions on Vehicle Categories.
- **Fix:** Remove from `Rent Pro User`, keep only `Rent Pro Manager`+.

#### SEC-014: No Rate Limiting on API Endpoints
- **Issue:** No rate limiting on whitelisted endpoints. Could enable brute-force or DoS attacks.
- **Fix:** Implement rate limiting via Frappe or nginx.

#### SEC-015: Background Job Notification Targeting
- **File:** `tasks.py:152`
- **Issue:** Notifications target `frappe.session.user` which is Administrator in background context.
- **Fix:** Store and use target user per record.

#### SEC-016: No Content Security Policy Headers
- **Issue:** No CSP headers configured for the app's web pages.
- **Fix:** Configure CSP in nginx or Frappe middleware.

---

## Compliance

| Standard | Status |
|----------|--------|
| OWASP Top 10 | 4 of 10 categories have findings |
| Frappe Security Guidelines | Partial compliance |
| GDPR (data isolation) | FAIL — cross-tenant data exposure |
| Moroccan Data Protection | FAIL — no data isolation |

---

## Recommendations

### Immediate (Before Production)
1. Fix SEC-001 through SEC-007 (CRITICAL)
2. Add agency filtering to all GPS API endpoints
3. Add agency field to Expense Entry, Payment Transaction, Vehicle Tracking
4. Implement XSS sanitization in all JS files
5. Add permission checks to all whitelisted endpoints

### Short-Term (v1.1)
6. Add file upload validation
7. Implement rate limiting
8. Create dedicated `Rent Pro Super Admin` role
9. Add CSP headers
10. Reduce `ignore_permissions` usage

### Long-Term (v2.0)
11. Security penetration testing
12. Implement audit logging for all API access
13. Add encryption at rest for sensitive data
14. Implement data retention policies
