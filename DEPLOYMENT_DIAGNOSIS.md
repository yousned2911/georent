# DEPLOYMENT_DIAGNOSIS.md — Rent Pro Deployment Failure

**Error:** `ModuleNotFoundError: No module named 'erpnext'`
**Date:** 2026-07-15
**Environment:** Frappe Cloud

---

## Error

```
ModuleNotFoundError: No module named 'erpnext'

installed_apps = ['frappe']
```

---

## Root Cause

**The Frappe Cloud site does not have ERPNext installed.**

`installed_apps = ['frappe']` confirms only Frappe is present. Rent Pro declares ERPNext as a required dependency (`required_apps = ["erpnext"]` in `hooks.py:12`). When Frappe attempts to load the app, it verifies all `required_apps` are installed. Since ERPNext is missing, the installation fails.

This is **not a code issue**. This is a **deployment environment issue**.

---

## Audit Results

### 1. hooks.py

```python
required_apps = ["erpnext"]  # Line 12
```

| Check | Status | Detail |
|-------|:------:|--------|
| `required_apps` declared | PASS | Correctly declares ERPNext dependency |
| Value is `["erpnext"]` | PASS | Matches the Frappe app name for ERPNext |
| No other hooks reference erpnext imports | PASS | All hooks point to `rentpro.*` modules |

### 2. pyproject.toml

```toml
dependencies = []  # Line 13
```

| Check | Status | Detail |
|-------|:------:|--------|
| No `erpnext` in pip dependencies | PASS | Correct — ERPNext is a bench app, not a pip package |
| `dependencies = []` | PASS | Frappe apps are installed via `bench`, not pip |

### 3. setup.py

```python
install_requires = install_requires  # From requirements.txt
```

| Check | Status | Detail |
|-------|:------:|--------|
| `requirements.txt` content | PASS | Contains only comment: `# Frappe and ERPNext are provided by the bench environment` |
| No pip-level erpnext dependency | PASS | Correct — erpnext is a bench app |

### 4. modules.txt

```
Rent Pro
```

| Check | Status | Detail |
|-------|:------:|--------|
| Module name defined | PASS | `Rent Pro` |
| No erpnext reference | PASS | Module is independent |

### 5. patches.txt

```
[pre_model_sync]
# Patches that run before model sync

[post_model_sync]
# Patches that run after model sync
```

| Check | Status | Detail |
|-------|:------:|--------|
| No erpnext patches | PASS | Clean |

### 6. Python Import Analysis

| Check | Status | Detail |
|-------|:------:|--------|
| `import erpnext` | PASS | Zero occurrences |
| `from erpnext import` | PASS | Zero occurrences |
| `from erpnext.*` | PASS | Zero occurrences |

**Rent Pro does NOT import any ERPNext Python modules directly.**

### 7. ERPNext DocType Usage (via frappe.get_doc / frappe.get_all)

| DocType | Used In | Access Pattern |
|---------|---------|----------------|
| `Sales Invoice` | `rental_contract.py:210,260` | `frappe.get_doc({"doctype": "Sales Invoice", ...})` |
| `Sales Invoice` | `billing.py:21` | `frappe.get_doc({"doctype": "Sales Invoice", ...})` |
| `Sales Invoice` | `saas/dashboard.py:52` | `frappe.get_all("Sales Invoice", ...)` |
| `Sales Invoice` | `super_admin/dashboard.py:183` | `frappe.get_all("Sales Invoice", ...)` |
| `Sales Invoice` | `install.py:82` | Custom field creation on `Sales Invoice` |
| `Customer` | `billing.py:99` | `frappe.get_doc({"doctype": "Customer", ...})` |
| `Customer` | `billing.py:88` | `frappe.db.get_value("Customer", ...)` |
| `Selling Settings` | `billing.py:95-96` | `frappe.db.get_single_value("Selling Settings", ...)` |

**These are all accessed via Frappe's document API — not via Python imports.** This is the correct pattern for Frappe apps that depend on other apps' DocTypes.

---

## Why ERPNext Is Required

Rent Pro creates and queries the following ERPNext DocTypes at runtime:

1. **Sales Invoice** — Auto-generated when a rental contract is activated (billing)
2. **Customer** — Created for agencies during SaaS subscription billing
3. **Selling Settings** — Read for default customer group and territory

These are not optional integrations. They are **core business functions**:
- A car rental agency needs invoices
- Invoices require the Sales Invoice DocType (ERPNext Accounts module)
- Sales Invoices require Customer records (ERPNext CRM module)
- Customer creation requires Selling Settings (ERPNext Selling module)

**Removing the ERPNext dependency would break billing, invoicing, and financial reporting.**

---

## Is This a Rent Pro Code Issue?

**No.**

The code is correct:
- `required_apps = ["erpnext"]` properly declares the dependency
- No direct Python imports from erpnext (uses Frappe's document API — correct pattern)
- All ERPNext DocType references are accessed via `frappe.get_doc()` / `frappe.get_all()` — runtime resolution, not import-time

## Is This a Frappe Cloud Environment Issue?

**Yes.**

The Frappe Cloud site was created as a **Frappe-only** site (no ERPNext). The deployment log confirms:
```
installed_apps = ['frappe']
```

Rent Pro requires an **ERPNext site**, not a Frappe-only site.

## Is the Deployment Target Missing ERPNext?

**Yes.**

The site needs ERPNext installed. On Frappe Cloud, this means:
- The site must be created with ERPNext enabled
- OR ERPNext must be installed after site creation via `bench --site <site> install-app erpnext`

## Is the Deployment Configuration Incorrect?

**Partially.**

The `required_apps` in `hooks.py` is correct. However, the **Frappe Cloud site configuration** is wrong — it should have ERPNext installed.

---

## Correct Deployment Procedure

### Option A: Frappe Cloud (Recommended)

1. Create a new site on Frappe Cloud **with ERPNext enabled**
   - During site creation, select "ERPNext" as an included app
   - This ensures `installed_apps` includes both `frappe` and `erpnext`

2. Install Rent Pro:
   ```
   bench get-app https://github.com/yousned2911/georent.git --branch feature/rentpro-init
   bench --site <site> install-app rentpro
   ```

3. Verify:
   ```
   bench --site <site> console -c "print(frappe.get_installed_apps())"
   # Expected: ['frappe', 'erpnext', 'rentpro']
   ```

### Option B: Self-Hosted Bench

1. Set up a bench with ERPNext:
   ```
   bench init --frappe-branch version-16 frappe-bench
   cd frappe-bench
   bench get-app erpnext --branch version-16
   bench new-site <site-name>
   bench --site <site-name> install-app erpnext
   ```

2. Install Rent Pro:
   ```
   bench get-app https://github.com/yousned2911/georent.git --branch feature/rentpro-init
   bench --site <site-name> install-app rentpro
   ```

### What NOT to Do

- **Do NOT remove `required_apps = ["erpnext"]`** — this would allow installation on Frappe-only sites, but the app would crash at runtime when trying to create Sales Invoices
- **Do NOT create a Frappe-only site and try to install Rent Pro** — it will fail
- **Do NOT install ERPNext after installing Rent Pro** — the order matters (ERPNext first, then Rent Pro)

---

## Verification Checklist

After deploying to an ERPNext site:

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | ERPNext installed | `frappe.get_installed_apps()` | includes `erpnext` |
| 2 | Rent Pro installed | `frappe.get_installed_apps()` | includes `rentpro` |
| 3 | Module visible | Search "rent pro" in Desk | Shows Rent Pro module |
| 4 | Sales Invoice exists | `frappe.db.exists("DocType", "Sales Invoice")` | `True` |
| 5 | Customer exists | `frappe.db.exists("DocType", "Customer")` | `True` |
| 6 | Custom field exists | `frappe.db.exists("Custom Field", "Sales Invoice_rental_contract")` | `True` |

---

## Summary

| Question | Answer |
|----------|--------|
| Is this a Rent Pro code issue? | **No** — code is correct |
| Is this a Frappe Cloud environment issue? | **Yes** — site lacks ERPNext |
| Is the deployment target missing ERPNext? | **Yes** — `installed_apps = ['frappe']` only |
| Is the `required_apps` config correct? | **Yes** — `["erpnext"]` is correct |
| Should we remove the ERPNext dependency? | **No** — would break billing/invoicing |
| What is the fix? | **Deploy to an ERPNext site, not a Frappe-only site** |
