# DEPLOYMENT_GUIDE.md — Rent Pro on Frappe Cloud

**Version:** 0.1.0-rc1
**Date:** 2026-07-15
**Prerequisite:** ERPNext v16 bench (not Frappe-only)

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Frappe Framework | v16 | Provided by Frappe Cloud |
| ERPNext | v16 | **Must be installed on the bench** |
| Python | 3.10+ | Frappe Cloud default |
| MariaDB | 10.6+ | Frappe Cloud default |
| Redis | 6+ | Frappe Cloud default |

**Critical:** Rent Pro requires an ERPNext bench. A Frappe-only bench will fail with `ModuleNotFoundError: No module named 'erpnext'`.

---

## Step 1: Create an ERPNext Site on Frappe Cloud

1. Log in to [frappe.cloud](https://frappe.cloud)
2. Click **New Site**
3. During site creation:
   - Select **ERPNext** as the included application
   - This ensures `installed_apps` includes `['frappe', 'erpnext']`
4. Wait for site creation to complete

**Verification:**
```
bench --site <site> console -c "print(frappe.get_installed_apps())"
# Expected: ['frappe', 'erpnext']
```

---

## Step 2: Add Rent Pro to the Bench

### Option A: From GitHub (Recommended)

```bash
bench get-app https://github.com/yousned2911/georent.git --branch feature/rentpro-init
```

### Option B: From Local Directory

```bash
bench get-app /path/to/georent
```

---

## Step 3: Install Rent Pro on the Site

```bash
bench --site <site> install-app rentpro
```

This will:
1. Verify `erpnext` is in `installed_apps` (required_apps check)
2. Create 7 custom roles (Rent Pro Manager, User, Fleet Manager, etc.)
3. Create default Rent Pro Settings
4. Create custom field on Sales Invoice (`rental_contract`)
5. Sync all 25 DocTypes
6. Create the Workspace (Rent Pro module in Desk)

---

## Step 4: Verify Installation

```bash
# 1. Check installed apps
bench --site <site> console -c "print(frappe.get_installed_apps())"
# Expected: ['frappe', 'erpnext', 'rentpro']

# 2. Check Module Def
bench --site <site> console -c "print(frappe.db.exists('Module Def', 'Rent Pro'))"
# Expected: True

# 3. Check Workspace
bench --site <site> console -c "print(frappe.db.exists('Workspace', 'Rent Pro'))"
# Expected: True

# 4. Check key DocTypes
bench --site <site> console -c "
for dt in ['Vehicle', 'Rental Contract', 'Reservation', 'Payment Transaction', 'Document Record']:
    print(f'{dt}: {frappe.db.exists(\"DocType\", dt)}')
"
# Expected: all True

# 5. Check ERPNext integration
bench --site <site> console -c "print(frappe.db.exists('Custom Field', 'Sales Invoice_rental_contract'))"
# Expected: True

# 6. Check Sales Invoice exists (ERPNext)
bench --site <site> console -c "print(frappe.db.exists('DocType', 'Sales Invoice'))"
# Expected: True
```

---

## Step 5: Post-Installation Configuration

### 5.1 Configure Rent Pro Settings

Navigate to: **Rent Pro > Rent Pro Settings**

| Field | Value | Notes |
|-------|-------|-------|
| Agency Name | (your agency name) | Required |
| Default Currency | MAD | Moroccan Dirham |
| Default TVA Rate | 20% | Or applicable rate |
| OCR Enabled | Checked | Enable document scanning |
| GeoFleete Enabled | Checked | Enable GPS tracking |

### 5.2 Configure SaaS Settings (if multi-agency)

Navigate to: **Rent Pro > SaaS Settings**

| Field | Value |
|-------|-------|
| SaaS Enabled | Checked |
| Auto Generate Invoices | Checked |
| Grace Period Days | 7 |

### 5.3 Configure GeoFleete Settings

Navigate to: **Rent Pro > GeoFleete Settings**

| Field | Value |
|-------|-------|
| GPS Provider | Mock (for testing) |
| Mock Mode | Checked |
| GPS Update Interval | 30 seconds |

### 5.4 Create Subscription Plans (if multi-agency)

Navigate to: **Rent Pro > Subscription Plan > New**

Create at least one plan:
- Plan Name: "Basic"
- Plan Label: "Basic Plan"
- Monthly Price: (price in MAD)
- Max Vehicles: 10
- Max Users: 5

### 5.5 Assign Roles to Users

Navigate to: **User > (select user) > Roles**

Assign appropriate Rent Pro roles:
- **Rent Pro Manager** — Full access
- **Rent Pro User** — Standard user
- **Rent Pro Fleet Manager** — Vehicle/GPS management
- **Rent Pro Finance** — Financial operations

---

## Step 6: Create Test Data

```python
# Via bench console:
bench --site <site> console

# Create a test vehicle
vehicle = frappe.get_doc({
    "doctype": "Vehicle",
    "vehicle_name": "Test Vehicle",
    "make": "Toyota",
    "model": "Corolla",
    "year": 2024,
    "plate_number": "A-12345",
    "daily_rate": 500,
    "status": "Available"
})
vehicle.insert(ignore_permissions=True)
frappe.db.commit()

# Create a test customer (uses ERPNext Customer DocType)
customer = frappe.get_doc({
    "doctype": "Customer",
    "customer_name": "Test Customer",
    "customer_group": "All Customer Groups",
    "territory": "All Territories"
})
customer.insert(ignore_permissions=True)
frappe.db.commit()
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'erpnext'`

**Cause:** Site does not have ERPNext installed.
**Fix:** Create a new site with ERPNext enabled, or install ERPNext on the existing site:
```bash
bench get-app erpnext --branch version-16
bench --site <site> install-app erpnext
```

### Error: `required_apps check failed`

**Cause:** ERPNext is not in `installed_apps`.
**Fix:** Verify ERPNext is installed:
```bash
bench --site <site> console -c "print(frappe.get_installed_apps())"
```

### Rent Pro not visible in Desk

**Cause:** Workspace not created.
**Fix:** Run migration:
```bash
bench --site <site> migrate
bench build --app rentpro
```

### Sales Invoice creation fails

**Cause:** ERPNext Accounts module not properly configured.
**Fix:** Ensure ERPNext is fully set up:
1. Create a Company
2. Create a Cost Center
3. Create an Income Account
4. Configure Selling Settings

---

## Deployment Order

```
1. Frappe Framework (provided by Frappe Cloud)
   └── 2. ERPNext (must be installed first)
       └── 3. Rent Pro (depends on ERPNext)
```

**Never install Rent Pro before ERPNext.**

---

## Rollback

If deployment fails and you need to uninstall:

```bash
bench --site <site> uninstall-app rentpro
bench --site <site> migrate
```

This will:
- Remove all 7 custom roles
- Remove the custom field on Sales Invoice
- Remove all Rent Pro DocTypes and data

---

## Summary

| Step | Command | Expected Result |
|------|---------|-----------------|
| Create ERPNext site | Frappe Cloud UI | `installed_apps = ['frappe', 'erpnext']` |
| Get Rent Pro app | `bench get-app` | App downloaded to apps/ |
| Install Rent Pro | `bench install-app rentpro` | 25 DocTypes synced |
| Verify | `frappe.get_installed_apps()` | `['frappe', 'erpnext', 'rentpro']` |
| Configure | Desk > Rent Pro Settings | Agency name, currency, TVA |
| Assign roles | Desk > User > Roles | Rent Pro roles assigned |
