frappe.query_reports.setup(
    "Outstanding Payments Report",
    {
        filters: [
            {
                fieldname: "payment_status",
                label: __("Payment Status"),
                fieldtype: "Select",
                options: [
                    "",
                    "Unpaid",
                    "Partial",
                    "Paid",
                    "Refunded",
                ],
                default: "Unpaid",
            },
        ],
    }
);
