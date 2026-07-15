"""Super Admin — Support Tools for agency management."""

import frappe
from frappe.utils import add_days, today


def extend_trial(agency_name, days, reason=None):
    settings = frappe.get_single("Super Admin Settings")
    if not settings.allow_impersonation and not settings.super_admin_enabled:
        frappe.throw(frappe._("Super Admin is disabled."))

    max_days = settings.max_trial_extension_days or 30
    if days > max_days:
        frappe.throw(frappe._("Cannot extend trial by more than {0} days.").format(max_days))

    agency = frappe.get_doc("Agency", agency_name)
    if agency.status not in ("Trial", "Active"):
        frappe.throw(frappe._("Agency must be in Trial or Active status."))

    old_end = str(agency.trial_end_date or "None")
    agency.trial_end_date = add_days(agency.trial_end_date or today(), days)
    agency.status = "Trial"
    agency.save(ignore_permissions=True)
    frappe.db.commit()

    _log_support_action(
        "Trial Extension",
        f"Extended trial for {agency_name} by {days} days",
        agency=agency_name,
        old_value=old_end,
        new_value=str(agency.trial_end_date),
        reason=reason,
    )

    return {"success": True, "new_end_date": str(agency.trial_end_date)}


def suspend_agency(agency_name, reason=None):
    settings = frappe.get_single("Super Admin Settings")
    if settings.require_notes_for_suspend and not reason:
        frappe.throw(frappe._("Reason is required for suspension."))

    agency = frappe.get_doc("Agency", agency_name)
    old_status = agency.status
    agency.suspend_for_non_payment()

    _log_support_action(
        "Agency Suspension",
        f"Suspended agency {agency_name}: {reason or 'No reason provided'}",
        agency=agency_name,
        old_value=old_status,
        new_value="Suspended",
        severity="Warning",
        reason=reason,
    )

    return {"success": True}


def reactivate_agency(agency_name, reason=None):
    agency = frappe.get_doc("Agency", agency_name)
    old_status = agency.status
    agency.reactivate()

    _log_support_action(
        "Agency Reactivation",
        f"Reactivated agency {agency_name}: {reason or 'No reason provided'}",
        agency=agency_name,
        old_value=old_status,
        new_value="Active",
        reason=reason,
    )

    return {"success": True}


def reset_subscription(agency_name, reason=None):
    settings = frappe.get_single("Super Admin Settings")
    if not settings.allow_subscription_reset:
        frappe.throw(frappe._("Subscription reset is disabled."))

    subs = frappe.get_all(
        "Agency Subscription",
        filters={"agency": agency_name},
        fields=["name", "status"],
    )
    reset_count = 0
    for sub in subs:
        doc = frappe.get_doc("Agency Subscription", sub.name)
        doc.status = "Cancelled"
        doc.save(ignore_permissions=True)
        reset_count += 1

    frappe.db.commit()

    _log_support_action(
        "Subscription Reset",
        f"Reset {reset_count} subscription(s) for {agency_name}",
        agency=agency_name,
        severity="Warning",
        reason=reason,
    )

    return {"success": True, "reset_count": reset_count}


def impersonate_user(target_user, reason=None):
    settings = frappe.get_single("Super Admin Settings")
    if not settings.allow_impersonation:
        frappe.throw(frappe._("Impersonation is disabled."))
    if settings.impersonation_requires_reason and not reason:
        frappe.throw(frappe._("Reason is required for impersonation."))

    _log_support_action(
        "Support Action",
        f"Impersonating user {target_user}",
        target_doctype="User",
        target_name=target_user,
        severity="Warning",
        reason=reason,
    )

    frappe.session.user = target_user
    return {"success": True, "impersonating": target_user}


def export_agency_diagnostics(agency_name):
    agency = frappe.get_doc("Agency", agency_name)
    vehicles = frappe.get_all(
        "Vehicle",
        filters={"agency": agency_name},
        fields=["name", "vehicle_number", "status"],
    )
    contracts = frappe.get_all(
        "Rental Contract",
        filters={"agency": agency_name},
        fields=["name", "status", "grand_total"],
        limit=100,
    )
    subscriptions = frappe.get_all(
        "Agency Subscription",
        filters={"agency": agency_name},
        fields=["name", "plan", "status", "amount_mad"],
    )
    documents = frappe.get_all(
        "Document Record",
        filters={"agency": agency_name},
        fields=["name", "document_type", "status", "ocr_status"],
        limit=100,
    )

    _log_support_action(
        "Data Export",
        f"Exported diagnostics for {agency_name}",
        agency=agency_name,
    )

    return {
        "agency": {
            "name": agency.name,
            "status": agency.status,
            "created": str(agency.creation),
        },
        "vehicles": vehicles,
        "contracts": contracts,
        "subscriptions": subscriptions,
        "documents": documents,
        "vehicle_count": len(vehicles),
        "contract_count": len(contracts),
    }


def _log_support_action(
    action_type,
    description,
    agency=None,
    target_doctype=None,
    target_name=None,
    severity="Info",
    old_value=None,
    new_value=None,
    reason=None,
):
    try:
        from rentpro.doctype.super_admin_audit_log.super_admin_audit_log import (
            create_audit_log,
        )

        metadata = {}
        if reason:
            metadata["reason"] = reason

        create_audit_log(
            action_type=action_type,
            description=description,
            agency=agency,
            target_doctype=target_doctype,
            target_name=target_name,
            severity=severity,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata,
        )
    except Exception:
        frappe.log_error(
            title="Super Admin Audit Log Error",
            message=f"Failed to log action: {action_type}",
        )
