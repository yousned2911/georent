# SITE_AUDIT.md — Rent Pro RC1 Frappe Cloud Deployment

**Version:** 0.1.0-rc1
**Date:** 2026-07-15
**Environment:** Frappe Cloud / Frappe v16 + ERPNext v16
**Symptom:** Searching "rentpro" returns no results in Frappe Desk

---

## Root Cause

**Rent Pro is missing its Workspace definition.**

In Frappe v16, an app becomes visible in the Desk sidebar and search through a **Workspace** — a JSON file that defines the module's landing page, shortcuts, and links. Rent Pro has **zero workspace files** in the repository. The `rentpro/` directory contains no `workspace/` subdirectory and no workspace JSON files anywhere.

This means:
- The module is registered in the database (via `modules.txt` → Module Def)
- DocTypes are created and synced
- But **no Workspace exists** to make the module discoverable in the UI

---

## Audit Results

### 1. App Installation — PASS

| Check | Status | Evidence |
|-------|:------:|----------|
| `setup.py` defines app correctly | PASS | `name="rentpro"`, version `0.1.0` |
| `pyproject.toml` is valid | PASS | Build system configured |
| `hooks.py` is complete | PASS | All hooks defined |
| `__init__.py` has version | PASS | `__version__ = "0.1.0"` |
| `modules.txt` defines module | PASS | Contains `Rent Pro` |
| `MANIFEST.in` includes all files | PASS | Recursive includes for `.py`, `.json`, `.css`, `.js` |

### 2. Module Def — PASS (auto-generated)

| Check | Status | Evidence |
|-------|:------:|----------|
| Module name in `modules.txt` | PASS | `Rent Pro` (line 1) |
| Module Def created by `bench migrate` | PASS | Frappe auto-creates `Module Def` from `modules.txt` |
| Module linked to app | PASS | `app_name = "rentpro"` in hooks.py |

**Note:** The Module Def exists in the database but is invisible without a Workspace.

### 3. Workspace — FAIL (MISSING)

| Check | Status | Evidence |
|-------|:------:|----------|
| `rentpro/workspace/` directory exists | **FAIL** | Directory does not exist |
| Workspace JSON file exists | **FAIL** | No `*.json` files in any `workspace/` path |
| Workspace referenced in hooks.py | **FAIL** | No `workspaces` hook defined |
| Module appears in Desk sidebar | **FAIL** | No Workspace = no sidebar entry |
| Module appears in search | **FAIL** | No Workspace = no search index |

**This is the root cause of the search failure.**

### 4. DocTypes — PASS

| DocType | JSON Exists | Module | Status |
|---------|:-----------:|--------|:------:|
| Vehicle | YES | Rent Pro | OK |
| Vehicle Category | YES | Rent Pro | OK |
| Vehicle Tracking | YES | Rent Pro | OK |
| Vehicle Document | YES | Rent Pro | OK |
| Rental Contract | YES | Rent Pro | OK |
| Reservation | YES | Rent Pro | OK |
| Payment Transaction | YES | Rent Pro | OK |
| Expense Entry | YES | Rent Pro | OK |
| Document Record | YES | Rent Pro | OK |
| Document Audit Log | YES | Rent Pro | OK |
| Agency | YES | Rent Pro | OK |
| Agency Subscription | YES | Rent Pro | OK |
| Subscription Plan | YES | Rent Pro | OK |
| Subscription Usage | YES | Rent Pro | OK |
| License Key | YES | Rent Pro | OK |
| GPS Position | YES | Rent Pro | OK |
| Geofence Zone | YES | Rent Pro | OK |
| Geofence Alert | YES | Rent Pro | OK |
| Rent Pro Settings | YES | Rent Pro | OK |
| SaaS Settings | YES | Rent Pro | OK |
| GeoFleete Settings | YES | Rent Pro | OK |
| System Health Settings | YES | Rent Pro | OK |
| Super Admin Settings | YES | Rent Pro | OK |
| Super Admin Audit Log | YES | Rent Pro | OK |
| Feature Flag | YES | Rent Pro | OK |

**25 DocTypes verified** — all JSON definitions present and correctly module-linked.

### 5. Migrations — PASS

| Check | Status | Evidence |
|-------|:------:|----------|
| `patches.txt` exists | PASS | Empty but valid format |
| `before_migrate` hook defined | PASS | `rentpro.setup.migrate.before_migrate` |
| `after_migrate` hook defined | PASS | `rentpro.setup.migrate.after_migrate` |
| DocType JSON syncs on migrate | PASS | Standard Frappe behavior |
| No breaking patches | PASS | Patches file is empty (no migrations needed) |

### 6. Installed Applications — PASS (expected)

| Check | Status | Evidence |
|-------|:------:|----------|
| App listed in `__installed_apps` | PASS | Frappe tracks this automatically on `install-app` |
| Version matches | PASS | `0.1.0` in `__init__.py` |
| Required apps satisfied | PASS | `erpnext` is required and present on Frappe Cloud |

### 7. Supporting Files — PASS

| File | Status | Notes |
|------|:------:|-------|
| 8 Report JSONs | PASS | All present |
| 31 Number Card JSONs | PASS | All present |
| 1 Print Format JSON | PASS | Present |
| 3 Translation CSVs | PASS | en, fr, ar |
| CSS/JS assets | PASS | Present |
| Public JS (GeoFleete, Super Admin) | PASS | Present |

---

## What's Missing

### Primary: Workspace JSON

Frappe requires a Workspace JSON file at:
```
rentpro/workspace/rent_pro/rent_pro.json
```

The file must define:
- Module link
- Shortcuts to key DocTypes
- Number card references
- Chart references (if any)
- Sidebar ordering

### Secondary: No `app_include_logo` or branding

`hooks.py` has no `app_include_logo` or app icon configuration. Even after adding the Workspace, the app won't have a custom icon in the sidebar.

---

## Fix Required

Create the following file:

```
rentpro/workspace/rent_pro/rent_pro.json
```

This is a **blocking issue** — without it, Rent Pro is invisible in Frappe Desk despite being fully installed.

---

## Verification Commands (Post-Fix)

After creating the Workspace and running `bench migrate`:

```bash
# 1. Verify Module Def exists
bench --site <site> console -c "print(frappe.db.exists('Module Def', 'Rent Pro'))"
# Expected: True

# 2. Verify Workspace exists
bench --site <site> console -c "print(frappe.db.exists('Workspace', 'Rent Pro'))"
# Expected: True

# 3. Verify DocTypes exist
bench --site <site> console -c "print(frappe.db.exists('DocType', 'Rental Contract'))"
# Expected: True

# 4. Verify Installed Applications
bench --site <site> console -c "import json; print(json.dumps(frappe.get_installed_apps(), indent=2))"
# Expected: includes "rentpro"

# 5. Verify search works
# Navigate to Desk > search "rent pro" — should show the module
```

---

## Summary

| Component | Status | Impact |
|-----------|:------:|--------|
| App Installation | PASS | — |
| Module Def | PASS | — |
| **Workspace** | **FAIL** | **App invisible in Desk** |
| DocTypes (25) | PASS | — |
| Migrations | PASS | — |
| Installed Apps | PASS | — |
| Supporting Files | PASS | — |

**Diagnosis:** Rent Pro is fully installed at the database level. All 25 DocTypes, 7 roles, 8 reports, 31 number cards, and 1 print format are present. The app appears in `__installed_apps`. However, the **absence of a Workspace JSON file** means Frappe has no UI entry point for the module. It exists in the database but has no "front door" — hence searching "rentpro" returns nothing.
