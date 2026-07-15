import frappe


def before_install():
    frappe.publish_progress(50, title="Installing Rent Pro")
    _create_custom_roles()


def after_install():
    frappe.publish_progress(100, title="Installing Rent Pro")
    frappe.db.commit()
    frappe.clear_cache()
    _create_default_settings()
    _create_custom_fields()
    frappe.db.commit()


def _create_custom_roles():
    roles = [
        {
            "role_name": "Rent Pro Manager",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Rent Pro User",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Rent Pro Fleet Manager",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Rent Pro Finance",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Rent Pro Read Only",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Reservation Agent",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Rental Agent",
            "desk_access": 1,
            "is_custom": 1,
        },
    ]
    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            role["doctype"] = "Role"
            frappe.get_doc(role).insert(ignore_permissions=True)


def _create_default_settings():
    if not frappe.db.exists("Rent Pro Settings", "settings"):
        settings = frappe.get_doc(
            {
                "doctype": "Rent Pro Settings",
                "name": "settings",
                "agency_name": "Rent Pro Agency",
                "default_currency": "MAD",
                "ocr_enabled": 1,
                "ocr_confidence_threshold": 80,
                "geofleete_enabled": 0,
                "gps_retention_days": 90,
                "reservation_overlap_check": 1,
                "auto_complete_contracts": 0,
            }
        )
        settings.insert(ignore_permissions=True)


def _create_custom_fields():
    fields = [
        {
            "dt": "Sales Invoice",
            "fieldname": "rental_contract",
            "fieldtype": "Link",
            "label": "Rental Contract",
            "options": "Rental Contract",
            "read_only": 1,
            "insert_after": "customer",
        },
    ]
    for field_data in fields:
        dt = field_data.pop("dt")
        fieldname = field_data.pop("fieldname")
        cf_name = f"{dt}_{fieldname}"
        if not frappe.db.exists("Custom Field", cf_name):
            field_data.update(
                {
                    "doctype": "Custom Field",
                    "name": cf_name,
                    "dt": dt,
                    "fieldname": fieldname,
                }
            )
            frappe.get_doc(field_data).insert(ignore_permissions=True)
