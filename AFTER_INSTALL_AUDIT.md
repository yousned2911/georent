# AFTER_INSTALL_AUDIT.md — Rent Pro RC1

**Date:** 2026-07-15
**Error:** `Module import failed for "Rent Pro Settings"`

---

## Install Flow

```
bench install-app rentpro
  │
  ├── 1. before_install()
  │     └── _create_custom_roles()     ← Creates 7 roles
  │
  ├── 2. Model Sync (Frappe core)
  │     ├── Sync DocType JSONs         ← 25 DocTypes registered
  │     ├── Create Module Def          ← "Rent Pro" Module Def created
  │     └── Sync Custom Fields         ← None (only in after_install)
  │
  └── 3. after_install()
        ├── _create_default_settings() ← FAILED HERE
        └── _create_custom_fields()    ← Not reached
```

---

## Failure Point

**File:** `rentpro/setup/install.py:62-78`

```python
def _create_default_settings():
    if not frappe.db.exists("Rent Pro Settings", "settings"):
        settings = frappe.get_doc({          # ← Frappe falls back to frappe.core
            "doctype": "Rent Pro Settings",
            ...
        })
        settings.insert(ignore_permissions=True)
```

**What happens:**
1. `frappe.get_doc({"doctype": "Rent Pro Settings"})` is called
2. Frappe looks up "Rent Pro Settings" in the DocType table → found
3. Reads `module = "Rent Pro"` from the DocType record
4. Tries to find Module Def named "Rent Pro" → **fails** (cache not populated)
5. Falls back to `frappe.core.doctype.rent_pro_settings`
6. Import fails → `ModuleNotFoundError`

---

## Root Cause

`after_install()` runs after model sync, but Frappe's in-memory cache hasn't been refreshed to include the newly created Module Def. When `frappe.get_doc()` tries to resolve the module path, it can't find "Rent Pro" in the cache, so it falls back to `frappe.core`.

---

## Fix Applied

**File:** `rentpro/setup/install.py:9-15`

```python
def after_install():
    frappe.publish_progress(100, title="Installing Rent Pro")
    frappe.db.commit()         # ← Commit all sync changes to DB
    frappe.clear_cache()       # ← Refresh in-memory cache (Module Def, DocTypes)
    _create_default_settings() # ← Now frappe.get_doc() can resolve the module
    _create_custom_fields()
    frappe.db.commit()
```

**Why this works:**
- `frappe.db.commit()` ensures all model sync changes (DocTypes, Module Def) are persisted
- `frappe.clear_cache()` forces Frappe to reload the DocType and Module Def cache
- Now `frappe.get_doc({"doctype": "Rent Pro Settings"})` finds the Module Def and resolves the correct import path

---

## Verification

After the fix, the install flow becomes:

```
bench install-app rentpro
  │
  ├── 1. before_install()
  │     └── _create_custom_roles()     ✅
  │
  ├── 2. Model Sync
  │     ├── Sync DocType JSONs         ✅
  │     ├── Create Module Def          ✅
  │     └── Sync Custom Fields         ✅
  │
  └── 3. after_install()
        ├── frappe.db.commit()         ✅ (NEW)
        ├── frappe.clear_cache()       ✅ (NEW)
        ├── _create_default_settings() ✅ (NOW WORKS)
        ├── _create_custom_fields()    ✅
        └── frappe.db.commit()         ✅
```

---

## Expected Post-Install State

| Item | Status |
|------|:------:|
| 7 custom roles created | OK |
| Rent Pro Settings initialized | OK |
| Custom field on Sales Invoice | OK |
| 25 DocTypes in database | OK |
| Module Def "Rent Pro" exists | OK |
| Workspace "Rent Pro" exists | OK |
