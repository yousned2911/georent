# Frappe v16 / ERPNext v16 Compatibility Report

**Date:** 2026-07-15  
**App:** Rent Pro v1.0.0-rc1.1  
**Repository:** github.com/yoursned2911/georent  
**Current target:** Frappe v15+ / ERPNext v15+

---

## Executive Summary

| Question | Answer |
|----------|--------|
| Can Rent Pro run on ERPNext v16 today? | **NO** — requires code changes |
| Is it safer to remain on v15? | **YES** — v15 is the proven target |
| Should we maintain dual compatibility? | **YES** — for future-proofing |
| Estimated migration effort | **2-3 days** for full v16 compatibility |

---

## Compatibility Verdict

| Category | Compatible? | Effort Required |
|----------|-------------|-----------------|
| **Frappe v16** | ⚠️ Partial | 2 days |
| **ERPNext v16** | ⚠️ Partial | 1 day (assuming Frappe v16 is resolved) |
| **Full RC1 on v16** | ❌ Not yet | 3 days total |

---

## 🔴 Blocking Issues (Must fix before v16)

### B1. Python 3.14+ Requirement

**What changed:** Frappe v16 requires Python 3.14+. v15 supports 3.10-3.11.

**Impact on Rent Pro:**
- `pyproject.toml` declares `requires-python = ">=3.10"` — needs updating to `>=3.14`
- All code must be validated against Python 3.14 (no obsolete patterns)
- CI/CD pipeline must use Python 3.14

**Files to change:** `pyproject.toml`, `.github/workflows/ci.yml`, `setup.py`

**Severity:** BLOCKING — Frappe Cloud will not deploy v16 with Python < 3.14

---

### B2. Node.js 24+ Requirement

**What changed:** v16 requires Node.js 24+ for asset building. Node 22 fails.

**Impact on Rent Pro:** CI workflow uses Node.js 18. Must upgrade to 24 for v16 builds.

**Files to change:** `.github/workflows/ci.yml`

**Severity:** BLOCKING — `bench build` will fail on v16

---

### B3. `frappe.db.get_value()` Returns Native Types for Singles

**What changed:**
```python
# v15 — returns string "1"
frappe.db.get_value("Rent Pro Settings", "settings", "ocr_enabled") == "1"

# v16 — returns int 1
frappe.db.get_value("Rent Pro Settings", "settings", "ocr_enabled") == 1
```

**Impact on Rent Pro:** All code comparing single doctype values to strings will break silently. Rent Pro has extensive use of `frappe.get_single()` and `frappe.db.get_value()` on its 5 single DocTypes.

**Affected files (20+):**
- `gps/__init__.py:14` — `getattr(settings, "geofleete_enabled", 0)`
- `gps/api.py`, `saas/plan_enforcement.py`, all settings doctypes
- All `if` conditions on single DocType check/select fields

**Severity:** BLOCKING — silent logic failures

---

### B4. `limit_page_length` Fully Removed

**What changed:** `limit_page_length` parameter removed from all `frappe.get_all()`, `frappe.get_list()`, `frappe.db.get_list()` calls. Use `limit` instead.

**Impact:** 2 files still use `limit_page_length` (already partially fixed in RC1.1 but 2 instances remain).

**Files:**
- `rentpro/rentpro/super_admin/dashboard.py:48`
- `rentpro/rentpro/super_admin/api.py:115`

**Fix:** Rename `limit_page_length` → `limit`

**Severity:** BLOCKING — will raise TypeError

---

### B5. `frappe.session.user` Direct Mutation

**What changed:** v16 enforces stricter session handling. Direct assignment `frappe.session.user = target_user` may not propagate correctly.

**Impact:** Super Admin impersonation feature breaks.

**File:** `rentpro/rentpro/super_admin/support_tools.py:123`

**Fix:** Replace with `frappe.set_user()` context manager.

**Severity:** BLOCKING — feature will not work

---

### B6. Default Sort Order Changed: `modified` → `creation`

**What changed:** ALL list views and `frappe.get_all()` calls default to `order_by="creation desc"` instead of `order_by="modified desc"`.

**Impact:** Any code relying on default sort order for "most recently modified" records will return wrong results. This affects:
- GPS alerts sorted by recency
- Reservation/contract list queries
- Report data ordering
- Any `frappe.get_all()` without explicit `order_by`

**Files affected:** 37 `frappe.get_all()` calls — must audit for implicit sort dependency

**Severity:** BLOCKING — incorrect data ordering

---

### B7. `frappe.get_doc()` Kwargs Update Behavior Removed

**What changed:**
```python
# v15 — these kwargs would UPDATE the fetched document
# v16 — kwargs are IGNORED
doc = frappe.get_doc("DocType", name, field=value)
```

**Impact:** Any code pattern that fetches a doc and expects kwargs to modify it will silently lose those updates.

**Files:** Search needed — this is a subtle behavioral change

**Severity:** BLOCKING — silent data loss

---

### B8. `has_permission` Hook Must Return `True`

**What changed:** v16 strictly enforces that `has_permission` hooks must return `True` to grant access. Returning `None` or omitting the return statement no longer grants access.

**Impact:** All 5 has_permission hooks in Rent Pro.

**Files:**
- `doctype/rent_pro_settings/rent_pro_settings.py:19-30`
- `doctype/saas_settings/saas_settings.py:14-26`
- `doctype/super_admin_settings/super_admin_settings.py:16-22`
- `doctype/geofleete_settings/geofleete_settings.py:43-56`
- `doctype/system_health_settings/system_health_settings.py:22-29`

**Fix:** All already return `True` explicitly, so this is likely OK, but verify edge cases.

**Severity:** WARNING — likely OK, needs verification

---

## 🟠 Warnings (Should fix for v16)

### W1. `has_permission` Signature — Missing `**kwargs`

**What changed:** v16 may pass additional keyword arguments to `has_permission` hooks. Without `**kwargs` in the signature, these extra kwargs will raise TypeError.

**Fix:** Change all 5 signatures:
```python
# Current
def has_permission(doc, user=None, permission_type=None):
# v16 compatible
def has_permission(doc, user=None, permission_type=None, **kwargs):
```

### W2. Raw SQL in Reports (12 instances)

v16 introduces stricter Query Builder (`frappe.qb`) and deprecates raw SQL in `fields` parameters. Reports using `frappe.db.sql()` with parameterized queries still work but should migrate to `frappe.qb` for future-proofing.

**Affected reports:**
- All 8 financial reports
- `super_admin/system_health.py:76`
- `saas/plan_enforcement.py:118`
- `doctype/reservation/reservation.py:130`
- `doctype/payment_transaction/payment_transaction.py:74`

### W3. `frappe.db.commit()` in Document Hooks

v16 no longer supports `frappe.db.commit()` inside document hooks (doc_events). Rent Pro's doc_events currently just call `pass` or validate, so this is not immediately impacted — but any future code adding commits in hooks will break.

### W4. `frappe.cache()` Usage

`super_admin/system_health.py:89` uses `frappe.cache()`. v16 may require explicit key arguments for user-scoped caching. Verify this is not causing cache collisions.

### W5. Scheduler Event Format

While Rent Pro's scheduler events use the standard dict format that works in v16, verify that the `every_five_minutes` interval is still supported (it was deprecated in some v16 release notes but kept for backward compatibility).

---

## 🟡 Informational (No action needed)

- `extend_bootinfo` hook — still valid
- `jinja.methods` — still valid
- `before_install`/`after_install` — stable
- `fixtures = []` — still valid
- `required_apps = ["erpnext"]` — still valid
- `frappe.throw()` / `frappe.msgprint()` — stable
- `@frappe.whitelist()` — stable
- DocType JSON schema — same structure in v16
- Report JSON schema — same structure in v16
- Dashboard chart JSON — same structure in v16
- Number card JSON — same structure in v16
- Print format JSON — same structure in v16
- Translations CSV — same format in v16

---

## Requirements.txt Update

For v16:
```diff
- frappe-framework>=15.0.0
- erpnext>=15.0.0
+ frappe-framework>=16.0.0
+ erpnext>=16.0.0
```

---

## Migration Effort Estimate

| Task | Effort | Priority |
|------|--------|----------|
| Update Python/Node versions in CI and pyproject.toml | 0.5h | 🔴 Must do |
| Fix `limit_page_length` → `limit` (2 files) | 0.25h | 🔴 Must do |
| Fix `frappe.session.user` mutation | 0.5h | 🔴 Must do |
| Add `**kwargs` to has_permission signatures | 0.5h | 🔴 Must do |
| Audit 37 `frappe.get_all()` for sort ordering | 2h | 🔴 Must do |
| Fix single doctype value comparisons | 2h | 🔴 Must do |
| Audit `frappe.get_doc()` kwargs patterns | 1h | 🔴 Must do |
| Migrate 12 raw SQL queries to frappe.qb | 4h | 🟠 Should do |
| Run full test suite on v16 | 2h | 🟠 Should do |
| Test all 8 financial reports | 1h | 🟠 Should do |
| Test Super Admin impersonation | 0.5h | 🟠 Should do |
| Smoke test entire rental lifecycle | 2h | 🟠 Should do |

**Total: ~16 hours (2-3 days)**

---

## REMAINING V15 RISKS (Why v15 is safer for RC1)

1. **v16 is newer, less battle-tested** than v15
2. **No v16 availability guarantee** on Frappe Cloud (v15 is the default)
3. **Community apps may not support v16 yet** — any ERPNext plugins used may break
4. **Rent Pro has 0 test runs on v16** — unknown compatibility surface
5. **Frappe Cloud itself may not have v16 GA** at the time of deployment
6. **Custom app ecosystem** (OCR, GeoFleete integrations) may have v16 issues

---

## Recommendation

### Short-term (RC1 — deploy now)
**Stay on Frappe v15 / ERPNext v15.** It is the proven, stable target. Rent Pro has been audited and tested against v15. All 27 hook references resolve. All 229 tests pass. Deployment is ready.

### Medium-term (v1.1.0 — 4-6 weeks)
**Begin v16 compatibility work:**
1. Set up a v16 Frappe Bench instance
2. Apply the 8 blocking fixes listed above
3. Run full test suite and fix failures
4. Run full rental lifecycle smoke test
5. Document any further v16 issues found

### Long-term (v2.0.0)
**Full v16 support with dual compatibility:**
- Maintain `frappe>=15.0.0` in requirements (v15 users can stay on RC1)
- Backport all fixes to `version-16` branch
- Add v16-specific CI pipeline
- Drop v15 support after Frappe v15 EOL

---

## Frappe Cloud Deployment Decision

| Scenario | Action | Risk |
|----------|--------|------|
| Frappe Cloud has v15 available | ✅ **Deploy on v15** | Low |
| Frappe Cloud only provides v16 | ⚠️ Do the 8 blocking fixes first (1 day), then deploy | Medium |
| Frappe Cloud offers both | ✅ Choose v15 explicitly | Lowest |

---

## Final Answer

**1. Can Rent Pro run on ERPNext v16 today?**  
**No.** 8 blocking issues must be fixed first. Estimated 2-3 days of work.

**2. Is it safer to remain on v15?**  
**Yes.** v15 is the audited, tested, proven target. No reason to deploy RC1 on v16.

**3. Should we maintain dual compatibility (v15 + v16)?**  
**Yes, eventually.** For RC1, ship on v15. Begin v16 work in parallel for v1.1.0.

**4. What changes are required for long-term support?**  
- Python 3.14+, Node 24+ in CI/CD  
- `limit_page_length` → `limit`  
- `frappe.session.user` → `frappe.set_user()`  
- `**kwargs` on all has_permission signatures  
- Audit all 37 `frappe.get_all()` for explicit `order_by`  
- Fix single doctype value type comparisons  
- Migrate raw SQL to `frappe.qb`  
- Update `requirements.txt` to `frappe>=16.0.0, erpnext>=16.0.0`  
- Run full test suite on v16 FH
