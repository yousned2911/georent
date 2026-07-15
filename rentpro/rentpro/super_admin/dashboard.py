"""Super Admin Dashboard — KPI data and platform overview."""

import frappe
from frappe.utils import add_days, getdate, now_datetime, today


def get_platform_summary():
    agencies = _get_agency_stats()
    subscriptions = _get_subscription_stats()
    usage = _get_usage_stats()

    return {
        **agencies,
        **subscriptions,
        **usage,
        "timestamp": str(now_datetime()),
    }


def get_agency_list_data(
    status=None,
    plan=None,
    search=None,
    limit=50,
    offset=0,
):
    filters = {}
    if status:
        filters["status"] = status
    if plan:
        filters["subscription_plan"] = plan

    agencies = frappe.get_all(
        "Agency",
        filters=filters,
        fields=[
            "name",
            "agency_name",
            "agency_code",
            "status",
            "subscription_plan",
            "subscription_status",
            "trial_start_date",
            "trial_end_date",
            "creation",
        ],
        limit_start=offset,
        limit=limit,
        order_by="creation desc",
    )

    for agency in agencies:
        agency["active_users"] = frappe.db.count(
            "User",
            {"agency_name": agency.name, "enabled": 1},
        )
        agency["vehicle_count"] = frappe.db.count("Vehicle", {"agency": agency.name})
        agency["contract_count"] = frappe.db.count("Rental Contract", {"agency": agency.name})

    total = frappe.db.count("Agency", filters)
    return {"agencies": agencies, "total": total}


def get_subscription_monitoring():
    active = frappe.get_all(
        "Agency Subscription",
        filters={"status": "Active"},
        fields=["name", "agency", "plan", "amount_mad", "next_billing_date"],
    )
    past_due = frappe.get_all(
        "Agency Subscription",
        filters={"status": "Past Due"},
        fields=["name", "agency", "plan", "amount_mad", "next_billing_date"],
    )
    suspended = frappe.get_all(
        "Agency Subscription",
        filters={"status": "Suspended"},
        fields=["name", "agency", "plan"],
    )

    mrr = sum(s.amount_mad or 0 for s in active)
    arr = mrr * 12

    return {
        "active_count": len(active),
        "past_due_count": len(past_due),
        "suspended_count": len(suspended),
        "mrr": mrr,
        "arr": arr,
        "active_subscriptions": active,
        "past_due_subscriptions": past_due,
        "suspended_subscriptions": suspended,
    }


def get_revenue_dashboard():
    monthly = _get_monthly_revenue(12)
    by_plan = _get_revenue_by_plan()
    total_revenue = sum(m["revenue"] for m in monthly)

    return {
        "monthly_revenue": monthly,
        "revenue_by_plan": by_plan,
        "total_revenue": total_revenue,
    }


def _get_agency_stats():
    total = frappe.db.count("Agency")
    active = frappe.db.count("Agency", {"status": "Active"})
    trial = frappe.db.count("Agency", {"status": "Trial"})
    suspended = frappe.db.count("Agency", {"status": "Suspended"})
    expired = frappe.db.count("Agency", {"status": "Expired"})
    cancelled = frappe.db.count("Agency", {"status": "Cancelled"})

    return {
        "total_agencies": total,
        "active_agencies": active,
        "trial_agencies": trial,
        "suspended_agencies": suspended,
        "expired_agencies": expired,
        "cancelled_agencies": cancelled,
    }


def _get_subscription_stats():
    active_subs = frappe.db.count("Agency Subscription", {"status": "Active"})
    plans = frappe.get_all(
        "Subscription Plan",
        filters={"is_active": 1},
        fields=["name", "plan_label", "price_mad"],
    )
    plan_dist = []
    for p in plans:
        count = frappe.db.count(
            "Agency Subscription",
            {"plan": p.name, "status": "Active"},
        )
        plan_dist.append(
            {
                "plan": p.plan_label or p.name,
                "price": p.price_mad,
                "count": count,
            }
        )

    mrr = 0
    for p in plan_dist:
        mrr += (p["price"] or 0) * p["count"]

    return {
        "active_subscriptions": active_subs,
        "plan_distribution": plan_dist,
        "mrr": mrr,
        "arr": mrr * 12,
    }


def _get_usage_stats():
    vehicles = frappe.db.count("Vehicle")
    contracts = frappe.db.count("Rental Contract")
    users = frappe.db.count("User", {"enabled": 1})
    ocr_docs = frappe.db.count("Document Record", {"ocr_status": "Completed"})
    geofence_alerts = frappe.db.count("Geofence Alert", {"is_acknowledged": 0})

    return {
        "total_vehicles": vehicles,
        "total_contracts": contracts,
        "total_users": users,
        "total_ocr_docs": ocr_docs,
        "active_geofence_alerts": geofence_alerts,
    }


def _get_monthly_revenue(months=12):
    result = []
    for i in range(months - 1, -1, -1):
        ref_date = add_days(today(), -30 * i)
        month_label = getdate(ref_date).strftime("%b %Y")
        result.append({"month": month_label, "revenue": 0})

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1},
        fields=["posting_date", "grand_total"],
    )
    for inv in invoices:
        month_key = getdate(inv.posting_date).strftime("%b %Y")
        for m in result:
            if m["month"] == month_key:
                m["revenue"] += inv.grand_total or 0
                break

    return result


def _get_revenue_by_plan():
    plans = frappe.get_all(
        "Subscription Plan",
        filters={"is_active": 1},
        fields=["name", "plan_label", "price_mad"],
    )
    result = []
    for plan in plans:
        count = frappe.db.count(
            "Agency Subscription",
            {"plan": plan.name, "status": "Active"},
        )
        result.append(
            {
                "plan": plan.plan_label or plan.name,
                "mrr": (plan.price_mad or 0) * count,
                "subscribers": count,
            }
        )
    return result
