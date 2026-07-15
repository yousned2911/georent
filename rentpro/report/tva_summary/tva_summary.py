import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("TVA Rate"),
            "fieldname": "tva_rate",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Taxable Amount"),
            "fieldname": "taxable_amount",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 150,
        },
        {
            "label": _("TVA Amount"),
            "fieldname": "tva_amount",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Contract Count"),
            "fieldname": "contract_count",
            "fieldtype": "Int",
            "width": 130,
        },
    ]


def get_data(filters):
    conditions = ["status != %(cancelled)s"]
    params = {"cancelled": "Cancelled"}

    if filters.get("from_date"):
        conditions.append("contract_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("contract_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    where_clause = " AND ".join(conditions)

    query = """
        SELECT
            tva_rate,
            SUM(
                subtotal - discount
            ) AS taxable_amount,
            SUM(tva_amount) AS tva_amount,
            COUNT(*) AS contract_count
        FROM `tabRental Contract`
        WHERE {where_clause}
        GROUP BY tva_rate
        ORDER BY tva_rate
    """.format(where_clause=where_clause)

    return frappe.db.sql(query, params, as_dict=True)
