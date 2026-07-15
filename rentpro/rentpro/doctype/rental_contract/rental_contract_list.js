frappe.listview_settings["Rental Contract"] = {
	get_indicator(doc) {
		const status_colors = {
			Draft: "orange",
			Active: "green",
			Completed: "darkgrey",
			Cancelled: "red",
		};
		const color = status_colors[doc.status] || "grey";
		return [
			__(doc.status),
			color,
			`status,=,${doc.status}`,
		];
	},
	formatters: {
		contract_number(value) {
			return `<a href="/app/rental-contract/${value}" style="font-weight:600;">${value}</a>`;
		},
	},
};
