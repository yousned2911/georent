# Rent Pro v1.0 — ERPNext Marketplace Checklist

**Version:** 1.0.0-rc1
**Status:** NOT READY FOR SUBMISSION

---

## Mandatory Requirements

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | App structure follows Frappe conventions | ✅ PASS | hooks.py, modules.txt, setup.py pattern |
| 2 | `__init__.py` with version, metadata | ✅ PASS | v0.1.0, all metadata present |
| 3 | `hooks.py` with all hook categories | ✅ PASS | 27 handlers, all resolve |
| 4 | `required_apps` set correctly | ✅ PASS | `["erpnext"]` |
| 5 | No monkey patching of core | ✅ PASS | No overrides found |
| 6 | No raw SQL injection vulnerabilities | ✅ PASS | All queries parameterized |
| 7 | MIT or compatible license | ✅ PASS | MIT License present |
| 8 | README.md with description | ✅ PASS | Comprehensive documentation |
| 9 | `setup.py` in app directory | ❌ FAIL | At repo root, not in `rentpro/` |
| 10 | `requirements.txt` in app directory | ❌ FAIL | At repo root, not in `rentpro/` |
| 11 | App icon (512x512 PNG) | ❌ FAIL | No icon file exists |
| 12 | No DocType name collisions | ❌ FAIL | `Vehicle` and `Expense Entry` collide with ERPNext core |
| 13 | Proper DocType permissions | ⚠️ WARN | Vehicle Category has overly permissive access |
| 14 | Translation files (en + 1 more) | ✅ PASS | en, fr, ar CSVs present |
| 15 | No hardcoded secrets | ✅ PASS | Clean scan |
| 16 | Works with bench install | ⚠️ WARN | setup.py location may cause issues |

---

## Code Quality

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 17 | Black formatting | ✅ PASS | 109 files, all clean |
| 18 | isort import sorting | ✅ PASS | Clean |
| 19 | Flake8 lint | ✅ PASS | Zero violations |
| 20 | Test coverage | ⚠️ WARN | 229 tests, no runtime coverage data |
| 21 | No deprecated API usage | ✅ PASS | Uses current Frappe v15 patterns |
| 22 | DocType JSON valid | ✅ PASS | All 26 DocTypes have valid JSON |
| 23 | Controller files present | ✅ PASS | All 26 DocTypes have controllers |

---

## Security

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 24 | No XSS vulnerabilities | ❌ FAIL | 8 JS files use innerHTML unsafely |
| 25 | Permission checks on APIs | ❌ FAIL | 8 GPS API endpoints unguarded |
| 26 | CSRF protection | ✅ PASS | Standard Frappe patterns |
| 27 | No privilege escalation | ❌ FAIL | Session user manipulation without context manager |
| 28 | File upload validation | ❌ FAIL | No type/size restrictions |
| 29 | Rate limiting | ❌ FAIL | Not implemented |

---

## Multi-Tenancy (SaaS)

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 30 | Agency field on all data DocTypes | ❌ FAIL | Missing on 3 DocTypes |
| 31 | Agency filtering on all queries | ❌ FAIL | GPS API and reports leak data |
| 32 | Tenant isolation verification | ⚠️ WARN | Orphan detection broken |
| 33 | Per-agency settings | ❌ FAIL | Rent Pro Settings is global single |

---

## Documentation

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 34 | Installation guide | ✅ PASS | DEPLOYMENT_GUIDE.md |
| 35 | API documentation | ⚠️ WARN | No OpenAPI/Swagger spec |
| 36 | Changelog | ✅ PASS | CHANGELOG.md with all versions |
| 37 | Known issues documented | ✅ PASS | KNOWN_ISSUES.md |
| 38 | Upgrade guide | ✅ PASS | UPGRADE_GUIDE.md |
| 39 | Backup guide | ✅ PASS | BACKUP_GUIDE.md |

---

## Frappe Cloud Specific

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 40 | Works with bench manager | ✅ PASS | Standard structure |
| 41 | Migration hooks implemented | ⚠️ WARN | Stubs only |
| 42 | No hardcoded paths | ✅ PASS | Uses Frappe conventions |
| 43 | Compatible with MariaDB 10.6+ | ✅ PASS | Standard SQL used |
| 44 | Compatible with Python 3.10+ | ✅ PASS | No deprecated syntax |
| 45 | Compatible with Node.js 18+ | ✅ PASS | Standard JS |

---

## Score Card

| Category | Pass | Fail | Warn | Score |
|----------|------|------|------|-------|
| Mandatory (16) | 11 | 4 | 1 | 69% |
| Code Quality (7) | 7 | 0 | 0 | 100% |
| Security (6) | 2 | 4 | 0 | 33% |
| Multi-Tenancy (4) | 0 | 3 | 1 | 13% |
| Documentation (6) | 5 | 0 | 1 | 83% |
| Frappe Cloud (6) | 5 | 0 | 1 | 83% |
| **TOTAL (45)** | **30** | **11** | **4** | **67%** |

---

## Required Fixes Before Submission

### P0 — Must Fix (Marketplace Will Reject)

1. **Rename `Vehicle` DocType** → `Rent Pro Vehicle` or extend ERPNext's Vehicle
2. **Rename `Expense Entry` DocType** → `Rent Pro Expense Entry`
3. **Move `setup.py` and `requirements.txt`** into `rentpro/` directory
4. **Add app icon** (512x512 PNG) to `rentpro/public/images/`

### P1 — Should Fix (Reviewer May Flag)

5. Add permission checks to all GPS API endpoints
6. Add agency field to Expense Entry, Payment Transaction, Vehicle Tracking
7. Fix XSS vulnerabilities in GeoFleete JS files
8. Implement session context manager for impersonation
9. Add file upload validation
10. Reduce `ignore_permissions` usage

### P2 — Recommended

11. Add OpenAPI documentation for API endpoints
12. Add comprehensive translation keys
13. Add Arabic/RTL print format support
14. Add rate limiting
15. Implement proper migration hooks

---

## Conclusion

**Status: NOT READY FOR MARKETPLACE SUBMISSION**

The app has strong code quality (100% on lint/formatting) and good documentation (83%). However, critical issues remain:

- **2 DocType name collisions** with ERPNext core will cause immediate rejection
- **4 security vulnerabilities** (unguarded APIs, XSS, privilege escalation)
- **3 multi-tenancy failures** (missing agency fields, cross-tenant data leaks)
- **4 missing mandatory files** (setup.py location, app icon)

**Estimated effort to reach submission readiness: 3-5 days of focused development.**
