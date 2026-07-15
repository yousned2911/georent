"""SaaS Billing Engine — Invoice generation and renewal processing."""

import frappe
from frappe.utils import add_days, today


def generate_invoice(subscription_name):
    sub = frappe.get_doc("Agency Subscription", subscription_name)
    if sub.status != "Active":
        return None

    agency = frappe.get_doc("Agency", sub.agency)
    plan = frappe.get_doc("Subscription Plan", sub.plan)

    customer = _get_or_create_customer(agency)
    if not customer:
        return None

    invoice = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "customer": customer.name,
            "posting_date": today(),
            "due_date": add_days(today(), 30),
            "company": frappe.defaults.get_global_default("company"),
            "items": [
                {
                    "item_name": f"Rent Pro - {plan.plan_label}",
                    "description": (f"{plan.plan_label} subscription " f"({sub.billing_cycle})"),
                    "qty": 1,
                    "rate": sub.amount_mad,
                }
            ],
        }
    )
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    frappe.db.commit()

    sub.last_billing_date = today()
    sub.invoices_created = (sub.invoices_created or 0) + 1
    sub.save(ignore_permissions=True)
    frappe.db.commit()

    return invoice


def process_renewals():
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled:
        return

    today_date = today()
    subscriptions = frappe.get_all(
        "Agency Subscription",
        filters={
            "status": "Active",
            "next_billing_date": ["<=", today_date],
            "auto_renew": 1,
        },
        fields=["name", "agency", "plan"],
    )

    for sub in subscriptions:
        try:
            _process_single_renewal(sub.name)
        except Exception:
            frappe.log_error(
                title="SaaS Renewal Error",
                message=f"Failed to renew subscription {sub.name}",
            )


def _process_single_renewal(subscription_name):
    sub = frappe.get_doc("Agency Subscription", subscription_name)
    settings = frappe.get_single("SaaS Settings")

    if settings.auto_generate_invoices:
        generate_invoice(subscription_name)

    sub.renew()

    _create_renewal_notification(sub)


def _get_or_create_customer(agency):
    customer_name = frappe.db.get_value(
        "Customer",
        {"agency_name": agency.name},
        "name",
    )
    if customer_name:
        return frappe.get_doc("Customer", customer_name)

    cg = frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups"
    terr = frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": agency.agency_name,
            "customer_group": cg,
            "territory": terr,
            "agency_name": agency.name,
        }
    )
    customer.insert(ignore_permissions=True)
    frappe.db.commit()
    return customer


def _create_renewal_notification(sub):
    try:
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "subject": (f"Subscription renewed for " f"{sub.agency}: {sub.plan}"),
                "type": "Info",
                "document_name": sub.name,
                "for_user": frappe.session.user,
            }
        ).insert(ignore_permissions=True)
    except Exception:
        pass


def check_and_suspend_overdue():
    settings = frappe.get_single("SaaS Settings")
    if not settings.saas_enabled or not settings.suspend_on_non_payment:
        return

    grace = settings.grace_period_days or 7
    overdue_date = add_days(today(), -grace)

    subscriptions = frappe.get_all(
        "Agency Subscription",
        filters={
            "status": "Past Due",
            "next_billing_date": ["<", overdue_date],
        },
        fields=["name", "agency"],
    )

    for sub in subscriptions:
        agency = frappe.get_doc("Agency", sub.agency)
        agency.suspend_for_non_payment()


def mark_past_due():
    today_date = today()
    frappe.db.set_value(
        "Agency Subscription",
        {
            "status": "Active",
            "next_billing_date": ["<", today_date],
            "auto_renew": 1,
        },
        "status",
        "Past Due",
    )
    frappe.db.commit()
