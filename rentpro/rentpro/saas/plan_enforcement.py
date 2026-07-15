"""SaaS Plan Enforcement — Checks and enforces subscription limits."""

import frappe
from frappe.utils import today


def get_agency_plan(agency_name):
    agency = frappe.get_doc("Agency", agency_name)
    if not agency.subscription_plan:
        return None
    return frappe.get_doc("Subscription Plan", agency.subscription_plan)


def get_agency_usage(agency_name):
    plan = get_agency_plan(agency_name)
    limits = {}
    if plan:
        limits = {
            "vehicles": plan.max_vehicles or 0,
            "users": plan.max_users or 0,
            "storage_mb": plan.max_storage_mb or 0,
            "ocr_scans": plan.max_ocr_per_month or 0,
            "api_calls": plan.max_api_calls_per_month or 0,
        }

    usage = {
        "vehicles": frappe.db.count("Vehicle", {"agency": agency_name}),
        "users": _count_users(agency_name),
        "storage_mb": _get_storage_usage(agency_name),
        "ocr_scans": _get_ocr_usage(agency_name),
        "api_calls": _get_api_usage(agency_name),
    }

    result = {}
    for metric, used in usage.items():
        limit = limits.get(metric, 0)
        result[metric] = {
            "used": used,
            "limit": limit,
            "percent": (round(used / limit * 100, 1) if limit > 0 else 0),
            "exceeded": limit > 0 and used >= limit,
        }
    return result


def check_vehicle_limit(agency_name):
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.enforce_limits:
        return True
    plan = get_agency_plan(agency_name)
    if not plan:
        return True
    count = frappe.db.count("Vehicle", {"agency": agency_name})
    return count < plan.max_vehicles


def check_user_limit(agency_name):
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.enforce_limits:
        return True
    plan = get_agency_plan(agency_name)
    if not plan:
        return True
    count = _count_users(agency_name)
    return count < plan.max_users


def check_ocr_limit(agency_name):
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.enforce_limits:
        return True
    plan = get_agency_plan(agency_name)
    if not plan:
        return True
    used = _get_ocr_usage(agency_name)
    return used < plan.max_ocr_per_month


def check_api_limit(agency_name):
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.enforce_limits:
        return True
    plan = get_agency_plan(agency_name)
    if not plan:
        return True
    used = _get_api_usage(agency_name)
    return used < plan.max_api_calls_per_month


def enforce_all_limits(agency_name):
    results = {}
    results["vehicles"] = check_vehicle_limit(agency_name)
    results["users"] = check_user_limit(agency_name)
    results["ocr"] = check_ocr_limit(agency_name)
    results["api"] = check_api_limit(agency_name)
    all_ok = all(results.values())
    if not all_ok:
        exceeded = [k for k, v in results.items() if not v]
        frappe.throw(
            frappe._("Plan limit exceeded for: {0}. " "Please upgrade your subscription.").format(
                ", ".join(exceeded)
            )
        )
    return results


def _count_users(agency_name):
    return frappe.db.count(
        "User",
        {
            "agency_name": agency_name,
            "enabled": 1,
        },
    )


def _get_storage_usage(agency_name):
    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(file_size), 0)
        FROM `tabFile`
        WHERE attached_to_doctype = 'Agency'
          AND attached_to_name = %s
        """,
        agency_name,
    )
    if result and result[0][0]:
        return round(result[0][0] / (1024 * 1024), 2)
    return 0


def _get_ocr_usage(agency_name):
    return frappe.db.count(
        "Document Record",
        {
            "agency": agency_name,
            "ocr_status": "Completed",
            "creation": (">", frappe.utils.add_days(today(), -30)),
        },
    )


def _get_api_usage(agency_name):
    return (
        frappe.db.count(
            "API Request Log",
            {"agency": agency_name},
        )
        if frappe.db.exists("DocType", "API Request Log")
        else 0
    )


def on_vehicle_insert_validate(doc, method):
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.enforce_limits:
        return
    agency_name = getattr(doc, "agency", None)
    if not agency_name:
        return
    if not check_vehicle_limit(agency_name):
        frappe.throw(
            frappe._("Vehicle limit reached for agency {0}. " "Please upgrade your subscription.").format(
                agency_name
            )
        )
