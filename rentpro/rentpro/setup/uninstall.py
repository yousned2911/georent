import frappe


def before_uninstall():
    pass


def after_uninstall():
    _remove_custom_roles()
    _remove_custom_fields()
    _remove_settings()
    frappe.db.commit()


def _remove_custom_roles():
    roles = [
        "Rent Pro Manager",
        "Rent Pro User",
        "Rent Pro Fleet Manager",
        "Rent Pro Finance",
        "Rent Pro Read Only",
        "Reservation Agent",
        "Rental Agent",
    ]
    for role_name in roles:
        if frappe.db.exists("Role", role_name):
            frappe.delete_doc("Role", role_name, ignore_permissions=True)


def _remove_custom_fields():
    custom_fields = [
        "Sales Invoice_rental_contract",
    ]
    for cf_name in custom_fields:
        if frappe.db.exists("Custom Field", cf_name):
            frappe.delete_doc("Custom Field", cf_name, ignore_permissions=True)


def _remove_settings():
    if frappe.db.exists("Rent Pro Settings", "settings"):
        frappe.delete_doc(
            "Rent Pro Settings",
            "settings",
            ignore_permissions=True,
        )
