# ERPNEXT_DEPENDENCY_AUDIT.md — Rent Pro RC1

**Date:** 2026-07-15
**Conclusion:** Rent Pro is an ERPNext application. It requires an ERPNext bench.

---

## 1. Declaration

**File:** `rentpro/hooks.py:12`

```python
required_apps = ["erpnext"]
```

This is the single authoritative declaration. It is correct and must not be removed.

---

## 2. ERPNext DocTypes Used

### Sales Invoice (ERPNext Accounts Module)

| Location | Operation | Line |
|----------|-----------|------|
| `rentpro/doctype/rental_contract/rental_contract.py` | `frappe.get_all("Sales Invoice", ...)` | 210 |
| `rentpro/doctype/rental_contract/rental_contract.py` | `frappe.get_doc({"doctype": "Sales Invoice", ...})` | 260 |
| `rentpro/saas/billing.py` | `frappe.get_doc({"doctype": "Sales Invoice", ...})` | 21 |
| `rentpro/saas/dashboard.py` | `frappe.get_all("Sales Invoice", ...)` | 52 |
| `rentpro/super_admin/dashboard.py` | `frappe.get_all("Sales Invoice", ...)` | 183 |
| `rentpro/setup/install.py` | Custom field on `Sales Invoice` | 82 |
| `rentpro/setup/uninstall.py` | Removes custom field from `Sales Invoice` | 32 |
| `rentpro/doctype/rental_contract/test_rental_contract.py` | Test assertions on `Sales Invoice` | 351, 363, 368 |

**Purpose:** Auto-generate invoices when rental contracts are activated. Query revenue data for dashboards and reports.

### Customer (ERPNext CRM Module)

| Location | Operation | Line |
|----------|-----------|------|
| `rentpro/saas/billing.py` | `frappe.db.get_value("Customer", ...)` | 88 |
| `rentpro/saas/billing.py` | `frappe.get_doc("Customer", ...)` | 93 |
| `rentpro/saas/billing.py` | `frappe.get_doc({"doctype": "Customer", ...})` | 99 |
| `rentpro/doctype/rental_contract/rental_contract.py` | `frappe.db.exists("Customer", ...)` | 65 |
| `rentpro/doctype/reservation/reservation.py` | `frappe.db.exists("Customer", ...)` | 57 |
| `rentpro/doctype/rental_contract/test_rental_contract.py` | Test helper creates `Customer` | 36-42 |
| `rentpro/doctype/reservation/test_reservation.py` | Test helper creates `Customer` | 36-42 |
| `rentpro/doctype/payment_transaction/test_payment_transaction.py` | Test helper creates `Customer` | 35-41 |
| `rentpro/doctype/document_record/test_document_record.py` | Test helper creates `Customer` | 18-24 |
| `rentpro/report/outstanding_payments_report/outstanding_payments_report.py` | Column option `Customer` | 24 |
| `rentpro/super_admin/tenant_management.py` | References `Customer Extension` | 139, 150 |

**Purpose:** Validate customers on contracts/reservations. Create customers for SaaS billing.

### Selling Settings (ERPNext Selling Module)

| Location | Operation | Line |
|----------|-----------|------|
| `rentpro/saas/billing.py` | `frappe.db.get_single_value("Selling Settings", "customer_group")` | 95 |
| `rentpro/saas/billing.py` | `frappe.db.get_single_value("Selling Settings", "territory")` | 96 |
| `rentpro/doctype/rental_contract/test_rental_contract.py` | Same pattern | 39-40 |
| `rentpro/doctype/reservation/test_reservation.py` | Same pattern | 38-39 |
| `rentpro/doctype/payment_transaction/test_payment_transaction.py` | Same pattern | 37-38 |
| `rentpro/doctype/document_record/test_document_record.py` | Same pattern | 20-21 |

**Purpose:** Read default customer group and territory when creating Customer records.

---

## 3. Import Analysis

| Pattern | Occurrences |
|---------|:-----------:|
| `import erpnext` | 0 |
| `from erpnext import` | 0 |
| `from erpnext.*` | 0 |
| `erpnext.controllers` | 0 |

**Zero direct Python imports from ERPNext.** All dependencies are resolved at runtime via `frappe.get_doc()`, `frappe.get_all()`, `frappe.db.exists()`, and `frappe.db.get_value()`.

---

## 4. Dependency Classification

| Dependency | Type | Criticality | Used For |
|------------|------|:-----------:|----------|
| `Sales Invoice` | DocType | **Critical** | Invoicing, revenue dashboards, financial reports |
| `Customer` | DocType | **Critical** | Customer validation, SaaS billing |
| `Selling Settings` | Single DocType | **Required** | Default customer group/territory for Customer creation |

---

## 5. Why These Dependencies Exist

Rent Pro is a **car rental ERP**. Car rental agencies need to:

1. **Invoice customers** for rentals → `Sales Invoice`
2. **Track who they're billing** → `Customer`
3. **Set up billing defaults** → `Selling Settings`

These are not optional integrations or nice-to-haves. They are core business functions. A car rental agency cannot operate without invoicing.

---

## 6. What Would Break Without ERPNext

| Without ERPNext | Impact |
|-----------------|--------|
| `Sales Invoice` missing | Contract activation fails. No invoices generated. No revenue tracking. |
| `Customer` missing | Contract/reservation creation fails. Customer validation throws error. |
| `Selling Settings` missing | Customer creation fails. No default group/territory. |
| Custom field on `Sales Invoice` | Install fails. `install.py:82` tries to create field on non-existent DocType. |

---

## 7. Verification

```python
# After deployment to ERPNext site, verify:
frappe.get_installed_apps()
# Expected: ['frappe', 'erpnext', 'rentpro']

frappe.db.exists("DocType", "Sales Invoice")     # True
frappe.db.exists("DocType", "Customer")           # True
frappe.db.exists("DocType", "Selling Settings")   # True
frappe.db.exists("Custom Field", "Sales Invoice_rental_contract")  # True
```

---

## Summary

| Question | Answer |
|----------|--------|
| Is Rent Pro an ERPNext app? | **Yes** |
| Does it import erpnext Python modules? | **No** — uses Frappe document API at runtime |
| Does it depend on ERPNext DocTypes? | **Yes** — Sales Invoice, Customer, Selling Settings |
| Is `required_apps = ["erpnext"]` correct? | **Yes** |
| Should it be removed? | **No** — would break invoicing and billing |
| Can it run on a Frappe-only bench? | **No** |
