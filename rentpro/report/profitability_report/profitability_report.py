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
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Expenses"),
            "fieldname": "expenses",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Net Profit"),
            "fieldname": "net_profit",
            "fieldtype": "Currency",
            "options": "MAD",
            "width": 130,
        },
        {
            "label": _("Margin %"),
            "fieldname": "margin_percent",
            "fieldtype": "Float",
            "width": 100,
            "precision": 2,
        },
    ]


def get_data(filters):
    year = filters.get("fiscal_year")
    params = {"year": year}

    query = """
        SELECT
            rev.month,
            rev.revenue,
            COALESCE(exp.expenses, 0) AS expenses,
            rev.revenue
                - COALESCE(exp.expenses, 0)
                AS net_profit,
            CASE
                WHEN rev.revenue > 0 THEN
                    ROUND(
                        (rev.revenue
                            - COALESCE(
                                exp.expenses, 0))
                        / rev.revenue * 100,
                        2
                    )
                ELSE 0
            END AS margin_percent
        FROM (
            SELECT
                DATE_FORMAT(
                    transaction_date,
                    '%%Y-%%m'
                ) AS month,
                SUM(amount) AS revenue
            FROM `tabPayment Transaction`
            WHERE status = 'Completed'
                AND YEAR(transaction_date)
                    = %(year)s
            GROUP BY DATE_FORMAT(
                transaction_date, '%%Y-%%m'
            )
        ) rev
        LEFT JOIN (
            SELECT
                DATE_FORMAT(
                    expense_date, '%%Y-%%m'
                ) AS month,
                SUM(amount) AS expenses
            FROM `tabExpense Entry`
            WHERE YEAR(expense_date)
                = %(year)s
            GROUP BY DATE_FORMAT(
                expense_date, '%%Y-%%m'
            )
        ) exp ON exp.month = rev.month
        ORDER BY rev.month
    """

    return frappe.db.sql(query, params, as_dict=True)
