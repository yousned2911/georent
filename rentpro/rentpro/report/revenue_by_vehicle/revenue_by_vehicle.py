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
            "label": _("Make"),
            "fieldname": "make",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Model"),
            "fieldname": "model",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 150,
        },
        {
            "label": _("Contract Count"),
            "fieldname": "contract_count",
            "fieldtype": "Int",
            "width": 130,
        },
    ]


def get_data(filters):
    conditions = ["pt.status = %(status)s"]
    params = {"status": "Completed"}

    if filters.get("from_date"):
        conditions.append("pt.transaction_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("pt.transaction_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    where_clause = " AND ".join(conditions)

    query = """
        SELECT
            v.name AS vehicle,
            v.make,
            v.model,
            COALESCE(SUM(pt.amount), 0) AS revenue,
            COUNT(DISTINCT rc.name)
                AS contract_count
        FROM `tabVehicle` v
        INNER JOIN `tabRental Contract` rc
            ON rc.vehicle = v.name
        INNER JOIN `tabPayment Transaction` pt
            ON pt.contract = rc.name
            AND {where_clause}
        GROUP BY v.name, v.make, v.model
        ORDER BY revenue DESC
    """.format(where_clause=where_clause)

    return frappe.db.sql(query, params, as_dict=True)
