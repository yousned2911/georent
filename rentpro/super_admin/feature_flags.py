"""Super Admin — Feature Flag Management."""

import frappe
from frappe.utils import now_datetime


def toggle_flag(flag_name, enabled, agency_name=None):
    flag = frappe.get_doc("Feature Flag", flag_name)
    old_val = flag.enabled
    flag.enabled = 1 if enabled else 0
    flag.last_toggled_by = frappe.session.user
    flag.last_toggled_on = now_datetime()
    flag.save(ignore_permissions=True)
    frappe.db.commit()

    _log_flag_toggle(flag_name, old_val, flag.enabled, agency_name)
    return {"success": True, "flag": flag_name, "enabled": bool(flag.enabled)}


def get_flag_status():
    flags = frappe.get_all(
        "Feature Flag",
        fields=[
            "flag_name",
            "flag_label",
            "enabled",
            "category",
            "scope",
            "flag_type",
        ],
    )
    enabled_count = sum(1 for f in flags if f.enabled)
    return {
        "total_flags": len(flags),
        "enabled_count": enabled_count,
        "disabled_count": len(flags) - enabled_count,
        "flags": flags,
    }


def get_flags_for_agency(agency_name):
    from rentpro.doctype.feature_flag.feature_flag import (
        get_all_flags,
    )

    return get_all_flags(agency_name)


def bulk_toggle(category, enabled):
    flags = frappe.get_all(
        "Feature Flag",
        filters={"category": category},
        fields=["name"],
    )
    count = 0
    for f in flags:
        doc = frappe.get_doc("Feature Flag", f.name)
        doc.enabled = 1 if enabled else 0
        doc.last_toggled_by = frappe.session.user
        doc.last_toggled_on = now_datetime()
        doc.save(ignore_permissions=True)
        count += 1

    frappe.db.commit()
    return {"success": True, "toggled_count": count}


def _log_flag_toggle(flag_name, old_val, new_val, agency_name):
    try:
        from rentpro.doctype.super_admin_audit_log.super_admin_audit_log import (
            create_audit_log,
        )

        create_audit_log(
            action_type="Feature Flag Toggle",
            description=(f"Toggled feature flag '{flag_name}' " f"from {bool(old_val)} to {bool(new_val)}"),
            agency=agency_name,
            target_doctype="Feature Flag",
            target_name=flag_name,
            old_value=str(old_val),
            new_value=str(new_val),
        )
    except Exception:
        pass
