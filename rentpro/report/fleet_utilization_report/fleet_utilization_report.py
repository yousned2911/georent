import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Vehicle"),
            "fieldname": "vehicle",
            "fieldtype": "Link",
            "options": "Vehicle",
            "width": 120,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Days Rented This Month"),
            "fieldname": "days_rented",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Utilization %"),
            "fieldname": "utilization_percent",
            "fieldtype": "Float",
            "width": 120,
            "precision": 2,
        },
    ]


def get_data(filters):
    target_month = filters.get("month")
    if not target_month:
        target_month = frappe.utils.nowdate()[:7]

    year, month = target_month.split("-")
    month_start = f"{year}-{month}-01"

    days_in_month = frappe.utils.date_diff(
        frappe.utils.add_to_date(
            frappe.utils.getdate(month_start),
            months=1,
        ),
        frappe.utils.getdate(month_start),
    )

    params = {
        "month_start": month_start,
        "month_end": frappe.utils.add_to_date(
            frappe.utils.getdate(month_start),
            days=days_in_month - 1,
        ),
        "days_in_month": days_in_month,
    }

    query = """
        SELECT
            v.name AS vehicle,
            v.status,
            COUNT(DISTINCT rc.name) AS days_rented,
            CASE
                WHEN %(days_in_month)s > 0 THEN
                    ROUND(
                        COUNT(DISTINCT rc.name)
                        * 100.0
                        / %(days_in_month)s,
                        2
                    )
                ELSE 0
            END AS utilization_percent
        FROM `tabVehicle` v
        LEFT JOIN `tabRental Contract` rc
            ON rc.vehicle = v.name
            AND rc.status IN (
                'Active', 'Completed'
            )
            AND rc.pickup_datetime
                <= %(month_end)s
            AND COALESCE(
                rc.actual_return_datetime,
                rc.expected_return_datetime,
                %(month_end)s
            ) >= %(month_start)s
        WHERE v.active = 1
        GROUP BY v.name, v.status
        ORDER BY utilization_percent DESC
    """

    return frappe.db.sql(query, params, as_dict=True)
