frappe.listview_settings["Payment Transaction"] = {
	get_indicator(doc) {
		const colors = {
			Pending: "orange",
			Completed: "green",
			Failed: "red",
			Refunded: "blue",
		};
		const c = colors[doc.status] || "grey";
		return [
			__(doc.status),
			c,
			`status,=,${doc.status}`,
		];
	},
	formatters: {
		transaction_number(value) {
			return `<a href="/app/payment-transaction/${value}" style="font-weight:600;">${value}</a>`;
		},
	},
};
