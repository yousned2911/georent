"""SaaS Super Admin Dashboard — KPI data for platform overview."""

import frappe
from frappe.utils import add_days, getdate, today


def get_platform_summary():
    total_agencies = frappe.db.count("Agency")
    active_agencies = frappe.db.count("Agency", {"status": "Active"})
    trial_agencies = frappe.db.count("Agency", {"status": "Trial"})
    suspended_agencies = frappe.db.count("Agency", {"status": "Suspended"})

    active_subs = frappe.db.count("Agency Subscription", {"status": "Active"})

    mrr = _get_mrr()
    arr = mrr * 12

    total_vehicles = frappe.db.count("Vehicle")
    total_contracts = frappe.db.count("Rental Contract")
    total_ocr = frappe.db.count("Document Record", {"ocr_status": "Completed"})
    total_alerts = frappe.db.count("Geofence Alert", {"is_acknowledged": 0})

    churn_rate = _get_churn_rate()

    plan_distribution = _get_plan_distribution()

    return {
        "total_agencies": total_agencies,
        "active_agencies": active_agencies,
        "trial_agencies": trial_agencies,
        "suspended_agencies": suspended_agencies,
        "active_subscriptions": active_subs,
        "mrr": mrr,
        "arr": arr,
        "total_vehicles": total_vehicles,
        "total_contracts": total_contracts,
        "total_ocr_scans": total_ocr,
        "active_alerts": total_alerts,
        "churn_rate": churn_rate,
        "plan_distribution": plan_distribution,
    }


def get_monthly_revenue_data():
    months = []
    for i in range(11, -1, -1):
        month_start = add_days(today(), -30 * i)
        month_label = getdate(month_start).strftime("%b %Y")
        months.append({"month": month_label, "revenue": 0})

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "status": "Paid",
            "docstatus": 1,
        },
        fields=["posting_date", "grand_total"],
    )

    for inv in invoices:
        for m in months:
            if getdate(inv.posting_date).strftime("%b %Y") == m["month"]:
                m["revenue"] += inv.grand_total or 0

    return months


def _get_mrr():
    active = frappe.get_all(
        "Agency Subscription",
        filters={"status": "Active"},
        fields=["amount_mad", "billing_cycle"],
    )
    mrr = 0
    for sub in active:
        if sub.billing_cycle == "Yearly":
            mrr += (sub.amount_mad or 0) / 12
        else:
            mrr += sub.amount_mad or 0
    return round(mrr, 2)


def _get_churn_rate():
    thirty_days_ago = add_days(today(), -30)
    cancelled = frappe.db.count(
        "Agency Subscription",
        {
            "status": "Cancelled",
            "cancelled_on": [">", thirty_days_ago],
        },
    )
    total_start = frappe.db.count("Agency Subscription")
    if total_start == 0:
        return 0
    return round(cancelled / total_start * 100, 1)


def _get_plan_distribution():
    plans = frappe.get_all(
        "Subscription Plan",
        filters={"is_active": 1},
        fields=["name", "plan_label", "plan_type"],
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
                "type": plan.plan_type,
                "count": count,
            }
        )
    return result
