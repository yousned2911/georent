import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Agency"),
            "fieldname": "agency",
            "fieldtype": "Link",
            "options": "Agency",
            "width": 150,
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
            rc.agency AS agency,
            COALESCE(SUM(pt.amount), 0) AS revenue,
            COUNT(DISTINCT rc.name)
                AS contract_count
        FROM `tabRental Contract` rc
        INNER JOIN `tabPayment Transaction` pt
            ON pt.contract = rc.name
            AND {where_clause}
        WHERE rc.agency IS NOT NULL
        GROUP BY rc.agency
        ORDER BY revenue DESC
    """.format(where_clause=where_clause)

    return frappe.db.sql(query, params, as_dict=True)
