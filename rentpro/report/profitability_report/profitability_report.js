frappe.query_reports.setup("Profitability Report", {
    filters: [
        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Int",
            default: frappe.datetime.get_today().split(
                "-"
            )[0],
        },
    ],
});
