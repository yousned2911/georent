frappe.listview_settings["Expense Entry"] = {
	get_indicator(doc) {
		return [
			__(doc.category),
			"blue",
			`category,=,${doc.category}`,
		];
	},
	formatters: {
		expense_number(value) {
			return `<a href="/app/expense-entry/${value}" style="font-weight:600;">${value}</a>`;
		},
	},
};
