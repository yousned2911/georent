import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Category"),
            "fieldname": "category",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Total Expenses"),
            "fieldname": "total_expenses",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 150,
        },
        {
            "label": _("Entry Count"),
            "fieldname": "entry_count",
            "fieldtype": "Int",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters.get("from_date"):
        conditions.append("expense_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("expense_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = """
        SELECT
            category,
            SUM(amount) AS total_expenses,
            COUNT(*) AS entry_count
        FROM `tabExpense Entry`
        {where_clause}
        GROUP BY category
        ORDER BY total_expenses DESC
    """.format(where_clause=where_clause)

    return frappe.db.sql(query, params, as_dict=True)
