import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Contract"),
            "fieldname": "contract",
            "fieldtype": "Link",
            "options": "Rental Contract",
            "width": 130,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Vehicle"),
            "fieldname": "vehicle",
            "fieldtype": "Link",
            "options": "Vehicle",
            "width": 120,
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Total Paid"),
            "fieldname": "total_paid",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Status"),
            "fieldname": "payment_status",
            "fieldtype": "Data",
            "width": 100,
        },
    ]


def get_data(filters):
    statuses = ("Unpaid", "Partial")
    params = {"statuses": statuses}

    status_filter = ""
    if filters.get("payment_status"):
        params["statuses"] = (filters["payment_status"],)
        status_filter = " AND rc.payment_status = %(filter_status)s"
        params["filter_status"] = filters["payment_status"]

    query = """
        SELECT
            rc.name AS contract,
            rc.customer,
            rc.vehicle,
            rc.grand_total,
            COALESCE(paid.total, 0) AS total_paid,
            rc.grand_total
                - COALESCE(paid.total, 0) AS balance,
            rc.payment_status
        FROM `tabRental Contract` rc
        LEFT JOIN (
            SELECT
                contract,
                SUM(amount) AS total
            FROM `tabPayment Transaction`
            WHERE status = 'Completed'
            GROUP BY contract
        ) paid ON paid.contract = rc.name
        WHERE rc.payment_status
            IN %(statuses)s
        {status_filter}
        ORDER BY balance DESC
    """.format(status_filter=status_filter)

    return frappe.db.sql(query, params, as_dict=True)
