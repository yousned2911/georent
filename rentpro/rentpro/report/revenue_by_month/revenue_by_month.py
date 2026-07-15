import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Total Revenue"),
            "fieldname": "total_revenue",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 150,
        },
        {
            "label": _("Transaction Count"),
            "fieldname": "transaction_count",
            "fieldtype": "Int",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = ["pt.status = %(status)s"]
    params = {"status": "Completed"}

    if filters.get("fiscal_year"):
        year = filters["fiscal_year"]
        conditions.append("YEAR(pt.transaction_date) = %(year)s")
        params["year"] = year

    where_clause = " AND ".join(conditions)

    query = """
        SELECT
            DATE_FORMAT(
                pt.transaction_date, '%%Y-%%m'
            ) AS month,
            SUM(pt.amount) AS total_revenue,
            COUNT(*) AS transaction_count
        FROM `tabPayment Transaction` pt
        WHERE {where_clause}
        GROUP BY DATE_FORMAT(
            pt.transaction_date, '%%Y-%%m'
        )
        ORDER BY month
    """.format(where_clause=where_clause)

    return frappe.db.sql(query, params, as_dict=True)
