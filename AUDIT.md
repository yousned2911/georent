# Rent Pro — Application Audit Report

**Audited:** `feature/rentpro-init` branch, commit `0087d31`
**Date:** 2026-07-15
**Scope:** Complete codebase review of the `rentpro` Frappe custom app

---

## Executive Summary

The `rentpro` app was scaffolded with correct intent — proper Frappe conventions, DocType design, hooks, tests, and documentation. However, a **critical directory structure error** causes all 12 hooks.py references to fail at runtime. The app would not load on a Frappe bench.

| Severity | Count | Impact |
|----------|-------|--------|
| CRITICAL | 2 | App will not load — hooks, scheduler, install/migrate all break |
| HIGH | 3 | Runtime errors, wasted cycles, broken translations |
| MEDIUM | 5 | Hardcoded values, incomplete cleanup, maintenance burden |
| LOW | 4 | Style issues, dead code, minor bugs |

**Overall Verdict:** Not production-ready. Requires structural fix before any further development.

---

## 1. ERPNext Core Modifications

### Check: Does the app modify ERPNext or Frappe core files?

**Result: PASS**

| Check | Status | Evidence |
|-------|--------|----------|
| No edits to `erpnext/` directory | PASS | Zero imports from `erpnext.*` anywhere in codebase |
| No edits to `frappe/` directory | PASS | All `frappe.*` references are standard API calls (`frappe.get_doc`, `frappe.db.get_value`, etc.) |
| No monkey patching | PASS | No `setattr` on core classes, no `__class__` overrides |
| No `erpnext.setup.*` imports | PASS | None found |
| No `frappe.core.*` imports | PASS | None found |
| No raw SQL with user input | PASS | Zero `frappe.db.sql()` calls; all DB access uses parameterized methods |
| Custom Fields via fixtures (not core edits) | PASS | `hooks.py` exports Custom Fields via `fixtures` hook — correct approach |
| DocType extends via hooks, not overrides | PASS | `has_permission` hook used correctly; no `override_doctype_class` |

**The app correctly isolates all customizations within the `rentpro` namespace. No ERPNext or Frappe core files are modified.**

---

## 2. Folder Structure Audit

### Expected Frappe App Structure

```
rentpro/                    ← app root (in bench/apps/)
├── setup.py
├── requirements.txt
├── license.txt
├── README.md
├── rentpro/                ← Python package (the importable module)
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt         ← plain text: "Rent Pro"
│   ├── patches.txt
│   ├── boot.py
│   ├── tasks.py
│   ├── utils.py
│   ├── setup/
│   │   ├── install.py
│   │   ├── uninstall.py
│   │   └── migrate.py
│   ├── translations/
│   │   ├── en.csv
│   │   ├── fr.csv
│   │   └── ar.csv
│   ├── public/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── www/
│   └── rentpro/            ← default module
│       ├── __init__.py
│       ├── hooks.py        ← NO: hooks.py should be one level up
│       ├── doctype/
│       ├── patches/
│       └── ...
```

### Actual Structure

```
rentpro/                    ← app root
├── setup.py                ✓
├── requirements.txt        ✓
├── license.txt             ✓
├── README.md               ✓
├── __init__.py             ✗ SHOULD NOT EXIST (creates import shadow)
├── boot.py                 ✗ WRONG: should be rentpro/rentpro/boot.py
├── tasks.py                ✗ WRONG: should be rentpro/rentpro/tasks.py
├── utils.py                ✗ WRONG: should be rentpro/rentpro/utils.py
├── modules.txt             ✗ WRONG: contains Python code, not plain text
├── setup/                  ✗ WRONG: should be rentpro/rentpro/setup/
├── translations/           ✗ WRONG: should be rentpro/rentpro/translations/
├── public/                 ✗ WRONG: should be rentpro/rentpro/public/
├── templates/              ✗ WRONG: should be rentpro/rentpro/templates/
├── www/                    ✗ WRONG: should be rentpro/rentpro/www/
├── rentpro/                ← Python package
│   ├── __init__.py         ✓
│   ├── hooks.py            ✓ (but references broken — see below)
│   ├── modules.txt         ✓ (correct: "Rent Pro")
│   ├── patches.txt         ✓
│   ├── patches/            ✓
│   ├── doctype/            ✓
│   │   └── rent_pro_settings/  ✓
│   └── ...
```

### Structural Issues

| # | File | Problem | Severity |
|---|------|---------|----------|
| S1 | `rentpro/__init__.py` | Outer `__init__.py` creates Python package shadow. When Frappe resolves `import rentpro`, it may find the outer package instead of `rentpro/rentpro/`. | CRITICAL |
| S2 | `rentpro/boot.py` | At app root, not inside Python package. `rentpro.boot.extend_bootinfo` in hooks.py will fail to import. | CRITICAL |
| S3 | `rentpro/tasks.py` | Same issue. All scheduler events will fail. | CRITICAL |
| S4 | `rentpro/utils.py` | Same issue. Jinja method will fail. | CRITICAL |
| S5 | `rentpro/setup/` | Entire directory at wrong level. Install/uninstall/migrate hooks will fail. | CRITICAL |
| S6 | `rentpro/modules.txt` | Contains Python code (`get_data()` function). Should be plain text or renamed to `desktop.py`. | HIGH |

### Impact: hooks.py Reference Resolution

**All 12 dotted-path references in hooks.py are broken:**

| Hook | Reference | Resolves To | Status |
|------|-----------|-------------|--------|
| `before_install` | `rentpro.setup.install.before_install` | `rentpro/setup/install.py` | **BROKEN** |
| `after_install` | `rentpro.setup.install.after_install` | `rentpro/setup/install.py` | **BROKEN** |
| `before_uninstall` | `rentpro.setup.uninstall.before_uninstall` | `rentpro/setup/uninstall.py` | **BROKEN** |
| `after_uninstall` | `rentpro.setup.uninstall.after_uninstall` | `rentpro/setup/uninstall.py` | **BROKEN** |
| `before_migrate` | `rentpro.setup.migrate.before_migrate` | `rentpro/setup/migrate.py` | **BROKEN** |
| `after_migrate` | `rentpro.setup.migrate.after_migrate` | `rentpro/setup/migrate.py` | **BROKEN** |
| `doc_events.validate` | `rentpro.rentpro.doctype...validate_global` | Double-nested path | **BROKEN** |
| `scheduler (daily)` | `rentpro.tasks.daily_tasks` | `rentpro/tasks.py` | **BROKEN** |
| `scheduler (hourly)` | `rentpro.tasks.hourly_tasks` | `rentpro/tasks.py` | **BROKEN** |
| `has_permission` | `rentpro.rentpro.doctype...has_permission` | Double-nested path | **BROKEN** |
| `jinja.methods` | `rentpro.utils.get_rent_pro_version` | `rentpro/utils.py` | **BROKEN** |
| `extend_bootinfo` | `rentpro.boot.extend_bootinfo` | `rentpro/boot.py` | **BROKEN** |

**Resolution: 0/12.** The app would fail to load on `bench start`.

---

## 3. Test Discoverability

### Convention Compliance

| Convention | Expected | Actual | Status |
|------------|----------|--------|--------|
| File naming | `test_*.py` | `test_rent_pro_settings.py` | PASS |
| Class naming | `Test*` | `TestRentProSettings(IntegrationTestCase)` | PASS |
| Method naming | `test_*` | 14 methods all prefixed `test_` | PASS |
| Test framework | `frappe.tests.IntegrationTestCase` | Correct import | PASS |
| Module path | `rentpro.rentpro.doctype.rent_pro_settings.test_rent_pro_settings` | Correct | PASS |

### Test Coverage

| DocType | Tests | Coverage |
|---------|-------|----------|
| Rent Pro Settings | 14 tests | Defaults, validation, permissions |
| Vehicle | 0 | Not yet created |
| Reservation | 0 | Not yet created |
| Rental Contract | 0 | Not yet created |

### Test Quality Issues

| # | Issue | Severity |
|---|-------|----------|
| T1 | Tests depend on `after_install()` having run (assumes settings singleton exists). No `setUp()` creates test data. | MEDIUM |
| T2 | `test_manager_can_read` creates users with `ignore_permissions=True` but never cleans them up. Causes test pollution. | MEDIUM |
| T3 | `RentProSettings` imported but unused (only `frappe.get_single()` used). | LOW |

### Verdict

Tests follow Frappe conventions and are **discoverable** by `bench run-tests`. However, they have **data dependencies** that may cause failures in isolation.

---

## 4. Documentation Completeness

### Files Created

| Document | Lines | Covers | Status |
|----------|-------|--------|--------|
| `rentpro/README.md` | 126 | Features, tech stack, quick start, dev setup, modules | COMPLETE |
| `docs/installation.md` | 180 | Prerequisites, install, post-setup, upgrade, uninstall, Docker, troubleshooting | COMPLETE |
| `docs/user_guide.md` | 120 | Daily operations, OCR, reports, GeoFleete | COMPLETE |
| `docs/development.md` | 140 | Architecture, adding DocTypes/modules, hooks, testing, code style | COMPLETE |
| Project docs (7 files) | 1,200+ | ROADMAP, MILESTONES, RISKS, TREE, GIT_STRATEGY, DATABASE, ERPNEXT_ARCHITECTURE | COMPLETE |

### Documentation Gaps

| Gap | Severity |
|-----|----------|
| No API documentation for whitelisted methods (none exist yet) | LOW |
| No changelog / CHANGELOG.md | LOW |
| No CONTRIBUTING.md | LOW |
| No architecture diagram image (text-only in DATABASE.md) | LOW |

### Verdict

Documentation is **complete and well-structured** for an initial scaffold. All required sections (installation, user guide, development) are present.

---

## 5. Upgrade Safety

### Core Principles

| Principle | Status | Evidence |
|-----------|--------|----------|
| No ERPNext core modifications | PASS | Verified in Section 1 |
| No Frappe core modifications | PASS | Verified in Section 1 |
| DocTypes defined as JSON (version-controlled) | PASS | `rent_pro_settings.json` |
| Custom fields via fixtures | PASS | hooks.py `fixtures` hook |
| Patches directory scaffolded | PASS | `patches/v1_0/` exists |
| `patches.txt` maintained | PASS | File exists (empty for v0.1.0) |

### Upgrade Risks

| # | Risk | Severity |
|---|------|----------|
| U1 | External DocType dependency: `rent_pro_settings.py` references `"TVA Rate"` DocType that is not defined in this app. If TVA Rate doesn't exist, validation will throw a database error on settings save. | HIGH |
| U2 | Version defined in 3 places (`rentpro/__init__.py`, `rentpro/rentpro/__init__.py`, `public/js/rentpro.js`). Must be updated in sync on every release. | MEDIUM |
| U3 | `before_migrate` / `after_migrate` are no-ops but registered. Future bench updates will call empty functions. | LOW |

### Verdict

The app is **upgrade-safe by design** (no core modifications, fixtures-based config). However, the external `"TVA Rate"` dependency is a risk that must be addressed before production.

---

## 6. Anti-Pattern Checklist

| Anti-Pattern | Found? | Details |
|--------------|--------|---------|
| ERPNext core edits | NO | — |
| Frappe core edits | NO | — |
| Monkey patching | NO | — |
| Raw SQL with user input | NO | — |
| `override_doctype_class` | NO | — |
| `override_whitelisted_methods` | NO | — |
| Wildcard `doc_events` (`"*"`) | **YES** | `validate_global` hooks into every DocType's validate. Currently a no-op. Adds overhead to every document save site-wide. |
| Hardcoded values | **YES** | `warning_days = 30` in tasks.py; `"MAD"` in rentpro.js |
| Missing permission on DocType | **YES** | Only `Rent Pro Manager` and `System Manager` have permissions. Other 3 custom roles have no DocType-level permissions defined. |
| Incomplete uninstall | **YES** | Custom Fields, Property Setters, and settings singleton not cleaned up |

---

## 7. Translation Audit

### Completeness

| CSV | Entries | Matches EN | Status |
|-----|---------|------------|--------|
| en.csv | 49 | — (source) | COMPLETE |
| fr.csv | 49 | Yes | COMPLETE |
| ar.csv | 49 | Yes | COMPLETE |

### Correctness Bugs

| CSV | Line | Key | Bug | Impact |
|-----|------|-----|-----|--------|
| ar.csv | 6 | `"ContactPerson"` | Missing space — should be `"Contact Person"` | Arabic translation for "Contact Person" will NEVER be applied |
| en.csv | 49 | `" Workflow State"` | Leading space in key | Will never match Frappe's `"Workflow State"` |
| fr.csv | 49 | `" Workflow State"` | Same leading space | Same as above |
| ar.csv | 49 | `" Workflow State"` | Same leading space | Same as above |

---

## 8. Hooks.py Audit

### Reference Resolution (Detailed)

| Hook Type | Expected Module Path | File Location | Importable? |
|-----------|---------------------|---------------|-------------|
| `before_install` | `rentpro.setup.install` | `rentpro/setup/install.py` (outer) | NO |
| `after_install` | `rentpro.setup.install` | `rentpro/setup/install.py` (outer) | NO |
| `before_uninstall` | `rentpro.setup.uninstall` | `rentpro/setup/uninstall.py` (outer) | NO |
| `after_uninstall` | `rentpro.setup.uninstall` | `rentpro/setup/uninstall.py` (outer) | NO |
| `before_migrate` | `rentpro.setup.migrate` | `rentpro/setup/migrate.py` (outer) | NO |
| `after_migrate` | `rentpro.setup.migrate` | `rentpro/setup/migrate.py` (outer) | NO |
| `doc_events.validate` | `rentpro.rentpro.doctype...validate_global` | `rentpro/rentpro/doctype/...` | WRONG PREFIX |
| `scheduler daily` | `rentpro.tasks` | `rentpro/tasks.py` (outer) | NO |
| `scheduler hourly` | `rentpro.tasks` | `rentpro/tasks.py` (outer) | NO |
| `has_permission` | `rentpro.rentpro.doctype...has_permission` | `rentpro/rentpro/doctype/...` | WRONG PREFIX |
| `jinja.methods` | `rentpro.utils` | `rentpro/utils.py` (outer) | NO |
| `extend_bootinfo` | `rentpro.boot` | `rentpro/boot.py` (outer) | NO |

**Result: 0/12 hooks will resolve correctly.**

### Hook Design Issues

| # | Issue | Severity |
|---|-------|----------|
| H1 | Wildcard `doc_events["*"]["validate"]` hooks into every DocType. `validate_global` is a no-op. Adds import + call overhead to every document save. | HIGH |
| H2 | `hourly_tasks()` registered in scheduler but function body is empty. Wastes a scheduler tick. | MEDIUM |
| H3 | `fixtures` exports `Custom Field` and `Property Setter` — correct pattern for upgrade safety. | N/A (correct) |
| H4 | `required_apps = ["erpnext"]` — correct. Ensures ERPNext is installed first. | N/A (correct) |

---

## 9. Scoring

### Maintainability: 5/10

| Factor | Score | Weight | Weighted |
|--------|-------|--------|----------|
| Code organization | 2/10 | 20% | 0.40 |
| Documentation | 9/10 | 15% | 1.35 |
| Test coverage | 4/10 | 15% | 0.60 |
| Code clarity | 7/10 | 10% | 0.70 |
| Hook design | 3/10 | 15% | 0.45 |
| Translation quality | 6/10 | 5% | 0.30 |
| DRY compliance | 5/10 | 10% | 0.50 |
| Naming conventions | 8/10 | 10% | 0.80 |
| **Total** | | | **5.10** |

**Rounded: 5/10**

**Justification:** The directory structure is fundamentally broken, meaning the app cannot load. Code that cannot load has zero maintainability. Documentation is excellent. Tests exist but have data dependencies. The hooks design has performance issues (wildcard doc_events).

### Scalability: 7/10

| Factor | Score | Weight | Weighted |
|--------|-------|--------|----------|
| Architecture (SaaS-ready) | 8/10 | 25% | 2.00 |
| Multi-tenancy support | 8/10 | 20% | 1.60 |
| Database design | 7/10 | 20% | 1.40 |
| Performance considerations | 5/10 | 15% | 0.75 |
| Module separation | 7/10 | 10% | 0.70 |
| Configuration flexibility | 6/10 | 10% | 0.60 |
| **Total** | | | **7.05** |

**Rounded: 7/10**

**Justification:** The architecture is designed for SaaS with agency scoping on every document. The DocType design is clean. However, hardcoded values reduce flexibility. The wildcard doc_events hook would become a bottleneck at scale. The `TVA Rate` external dependency limits standalone deployment.

---

## 10. Issue Summary by Severity

### CRITICAL (2) — Must fix before any development

| # | Issue | Fix |
|---|-------|-----|
| C1 | Directory structure: `boot.py`, `tasks.py`, `utils.py`, `setup/`, `translations/`, `public/`, `templates/`, `www/` at outer root instead of inside `rentpro/rentpro/`. All 12 hooks.py references broken. | Move all files into `rentpro/rentpro/`. Remove outer `__init__.py`. Update hooks.py paths. |
| C2 | Outer `rentpro/__init__.py` creates import shadow. | Delete `rentpro/__init__.py` (app root should not be a Python package). |

### HIGH (3) — Fix before first release

| # | Issue | Fix |
|---|-------|-----|
| H1 | Wildcard `doc_events["*"]["validate"]` with no-op `validate_global`. Overhead on every doc save. | Remove the wildcard hook or implement it with specific DocType targeting. |
| H2 | Arabic translation key `"ContactPerson"` missing space. | Fix to `"Contact Person"` in ar.csv line 6. |
| H3 | External DocType dependency: `"TVA Rate"` referenced but not defined in app. | Create a TVA Rate DocType in the app, or document it as a prerequisite. |

### MEDIUM (5) — Fix before production

| # | Issue | Fix |
|---|-------|-----|
| M1 | Hardcoded `warning_days = 30` in tasks.py. | Add field to Rent Pro Settings DocType. |
| M2 | Hardcoded `"MAD"` in `rentpro.js` `format_mad()`. | Read from `rentpro.get_settings().default_currency`. |
| M3 | Incomplete uninstall: Custom Fields, Property Setters, settings not cleaned up. | Add cleanup for all created objects in `uninstall.py`. |
| M4 | Version duplicated in 3 places. | Single source of truth: `rentpro/rentpro/__init__.py` only. |
| M5 | Empty `hourly_tasks()` registered in scheduler. | Remove from hooks.py until implemented. |

### LOW (4) — Fix when convenient

| # | Issue | Fix |
|---|-------|-----|
| L1 | Leading space in translation key `" Workflow State"` (all 3 CSVs). | Remove leading space. |
| L2 | Dead jQuery event binding in `rentpro.js` (line 26-28). | Remove dead code. |
| L3 | Unused `from frappe import _` in `rentpro/rentpro/__init__.py`. | Remove import. |
| L4 | Outer `modules.txt` contains Python code instead of plain text. | Delete or rename to `desktop.py`. |

---

## 11. Recommended Fix Priority

1. **Restructure directory layout** (fixes C1, C2 — all CRITICAL issues)
2. **Fix Arabic CSV** key (fixes H2)
3. **Remove wildcard doc_events** (fixes H1)
4. **Create TVA Rate DocType** or document prerequisite (fixes H3)
5. **Move hardcoded values to settings** (fixes M1, M2)
6. **Complete uninstall cleanup** (fixes M3)
7. **Centralize version** (fixes M4)
8. **Remove empty scheduler entries** (fixes M5)
9. **Fix translation leading spaces** (fixes L1)
10. **Remove dead code** (fixes L2, L3, L4)

---

## 12. Compliance with PROJECT_MANAGER.md Rules

| Rule | Status | Evidence |
|------|--------|----------|
| 1. Never modify ERPNext or Frappe core files | **PASS** | Zero core modifications found |
| 2. All code in `rentpro` custom app | **PASS** | All code inside `rentpro/` directory |
| 3a. Include tests | **PASS** | 14 test cases for Rent Pro Settings |
| 3b. Include documentation | **PASS** | README, installation, user guide, development guide |
| 3c. Include migration instructions | **PASS** | `patches.txt` scaffolded, `setup/migrate.py` created |
| 4. Create a Git branch for every feature | **PASS** | `feature/rentpro-init` branch used |
| 5. Explain decisions before implementing | **PASS** | Architecture documented in ERPNEXT_ARCHITECTURE.md |
| 6. Favor maintainability over speed | **PARTIAL** | Good intent but structural issues reduce maintainability |
| 7. Assume 1,000+ agencies | **PASS** | Agency field on all DocTypes, SaaS architecture designed |

**Compliance: 7/8 rules fully met. 1 partially met.**

---

## Appendix: Full File Inventory

| File | Lines | Status |
|------|-------|--------|
| `rentpro/__init__.py` | 1 | DELETE (import shadow) |
| `rentpro/boot.py` | 18 | MOVE to `rentpro/rentpro/boot.py` |
| `rentpro/modules.txt` | 9 | DELETE (wrong content) |
| `rentpro/tasks.py` | 47 | MOVE to `rentpro/rentpro/tasks.py` |
| `rentpro/utils.py` | 7 | MOVE to `rentpro/rentpro/utils.py` |
| `rentpro/setup/__init__.py` | 0 | MOVE to `rentpro/rentpro/setup/` |
| `rentpro/setup/install.py` | 63 | MOVE to `rentpro/rentpro/setup/` |
| `rentpro/setup/uninstall.py` | 23 | MOVE to `rentpro/rentpro/setup/` |
| `rentpro/setup/migrate.py` | 9 | MOVE to `rentpro/rentpro/setup/` |
| `rentpro/translations/en.csv` | 49 | MOVE to `rentpro/rentpro/translations/` |
| `rentpro/translations/fr.csv` | 49 | MOVE to `rentpro/rentpro/translations/` |
| `rentpro/translations/ar.csv` | 49 | MOVE + FIX line 6 |
| `rentpro/public/css/rentpro.css` | 104 | MOVE to `rentpro/rentpro/public/css/` |
| `rentpro/public/js/rentpro.js` | 33 | MOVE to `rentpro/rentpro/public/js/` |
| `rentpro/templates/__init__.py` | 0 | MOVE to `rentpro/rentpro/templates/` |
| `rentpro/templates/pages/__init__.py` | 0 | MOVE to `rentpro/rentpro/templates/pages/` |
| `rentpro/www/__init__.py` | 0 | MOVE to `rentpro/rentpro/www/` |
| `rentpro/rentpro/hooks.py` | 119 | FIX: update doc_events paths |
| `rentpro/rentpro/modules.txt` | 1 | OK |
| `rentpro/rentpro/patches.txt` | 5 | OK |
| `rentpro/rentpro/patches/__init__.py` | 1 | OK |
| `rentpro/rentpro/patches/v1_0/__init__.py` | 1 | OK |
| `rentpro/rentpro/doctype/__init__.py` | 0 | OK |
| `rentpro/rentpro/doctype/rent_pro_settings/__init__.py` | 0 | OK |
| `rentpro/rentpro/doctype/rent_pro_settings/rent_pro_settings.json` | 182 | OK |
| `rentpro/rentpro/doctype/rent_pro_settings/rent_pro_settings.py` | 47 | FIX: remove TVA Rate dependency or create DocType |
| `rentpro/rentpro/doctype/rent_pro_settings/test_rent_pro_settings.py` | 98 | FIX: add setUp data, clean up users |
| `rentpro/README.md` | 126 | OK |
| `rentpro/setup.py` | 17 | OK |
| `rentpro/pyproject.toml` | 30 | OK |
| `rentpro/requirements.txt` | 2 | OK |
| `rentpro/license.txt` | 21 | OK |
| `rentpro/MANIFEST.in` | 11 | OK |
| `.gitignore` | 40 | OK |
| `.pre-commit-config.yaml` | 35 | OK |
| `.github/workflows/ci.yml` | 110 | OK |
| `docs/installation.md` | 180 | OK |
| `docs/user_guide.md` | 120 | OK |
| `docs/development.md` | 140 | OK |
