frappe.query_reports.setup(
    "Fleet Utilization Report",
    {
        filters: [
            {
                fieldname: "month",
                label: __("Month"),
                fieldtype: "Month",
                default: frappe.datetime.get_today().substring(
                    0,
                    7
                ),
            },
        ],
    }
);
