"""Super Admin API — Whitelisted endpoints for UI pages."""

import frappe


@frappe.whitelist()
def get_platform_summary():
    from rentpro.super_admin.dashboard import get_platform_summary

    _require_super_admin()
    return get_platform_summary()


@frappe.whitelist()
def get_agency_list_data(
    status=None,
    plan=None,
    search=None,
    limit=50,
    offset=0,
):
    from rentpro.super_admin.dashboard import (
        get_agency_list_data,
    )

    _require_super_admin()
    return get_agency_list_data(
        status=status,
        plan=plan,
        search=search,
        limit=int(limit),
        offset=int(offset),
    )


@frappe.whitelist()
def get_subscription_monitoring():
    from rentpro.super_admin.dashboard import (
        get_subscription_monitoring,
    )

    _require_super_admin()
    return get_subscription_monitoring()


@frappe.whitelist()
def get_revenue_dashboard():
    from rentpro.super_admin.dashboard import (
        get_revenue_dashboard,
    )

    _require_super_admin()
    return get_revenue_dashboard()


@frappe.whitelist()
def get_health_status():
    from rentpro.super_admin.system_health import (
        get_health_status,
    )

    _require_super_admin()
    return get_health_status()


@frappe.whitelist()
def run_health_check():
    from rentpro.super_admin.system_health import (
        run_health_check,
    )

    _require_super_admin()
    return run_health_check()


@frappe.whitelist()
def get_background_job_stats():
    from rentpro.super_admin.system_health import (
        get_background_job_stats,
    )

    _require_super_admin()
    return get_background_job_stats()


@frappe.whitelist()
def get_audit_logs(
    action_type=None,
    agency=None,
    limit=50,
    offset=0,
):
    _require_super_admin()
    filters = {}
    if action_type:
        filters["action_type"] = action_type
    if agency:
        filters["agency"] = agency

    logs = frappe.get_all(
        "Super Admin Audit Log",
        filters=filters,
        fields=[
            "name",
            "action_type",
            "severity",
            "actor",
            "action_timestamp",
            "target_doctype",
            "target_name",
            "agency",
            "description",
        ],
        limit_start=int(offset),
        limit=int(limit),
        order_by="action_timestamp desc",
    )
    total = frappe.db.count("Super Admin Audit Log", filters)
    return {"logs": logs, "total": total}


@frappe.whitelist()
def extend_trial(agency_name, days, reason=None):
    from rentpro.super_admin.support_tools import extend_trial

    _require_super_admin()
    return extend_trial(agency_name, int(days), reason)


@frappe.whitelist()
def suspend_agency(agency_name, reason=None):
    from rentpro.super_admin.support_tools import suspend_agency

    _require_super_admin()
    return suspend_agency(agency_name, reason)


@frappe.whitelist()
def reactivate_agency(agency_name, reason=None):
    from rentpro.super_admin.support_tools import (
        reactivate_agency,
    )

    _require_super_admin()
    return reactivate_agency(agency_name, reason)


@frappe.whitelist()
def reset_subscription(agency_name, reason=None):
    from rentpro.super_admin.support_tools import (
        reset_subscription,
    )

    _require_super_admin()
    return reset_subscription(agency_name, reason)


@frappe.whitelist()
def toggle_feature_flag(flag_name, enabled):
    from rentpro.super_admin.feature_flags import toggle_flag

    _require_super_admin()
    return toggle_flag(flag_name, enabled == "1" or enabled is True)


@frappe.whitelist()
def get_feature_flags():
    from rentpro.super_admin.feature_flags import (
        get_flag_status,
    )

    _require_super_admin()
    return get_flag_status()


@frappe.whitelist()
def get_tenant_metrics(agency_name):
    from rentpro.super_admin.tenant_management import (
        get_tenant_metrics,
    )

    _require_super_admin()
    return get_tenant_metrics(agency_name)


@frappe.whitelist()
def verify_tenant_isolation(agency_name=None):
    from rentpro.super_admin.tenant_management import (
        verify_tenant_isolation,
    )

    _require_super_admin()
    return verify_tenant_isolation(agency_name)


@frappe.whitelist()
def get_all_tenant_metrics():
    from rentpro.super_admin.tenant_management import (
        get_all_tenant_metrics,
    )

    _require_super_admin()
    return get_all_tenant_metrics()


@frappe.whitelist()
def export_agency_diagnostics(agency_name):
    from rentpro.super_admin.support_tools import (
        export_agency_diagnostics,
    )

    _require_super_admin()
    return export_agency_diagnostics(agency_name)


def _require_super_admin():
    if frappe.session.user == "Administrator":
        return
    roles = frappe.get_roles()
    if "System Manager" not in roles:
        frappe.throw(
            frappe._("Access denied. Super Administrator " "role required."),
            frappe.PermissionError,
        )
