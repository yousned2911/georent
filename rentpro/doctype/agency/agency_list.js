frappe.listview_settings["Agency"] = {
	get_indicator(doc) {
		const colors = {
			Active: "green",
			Trial: "blue",
			Suspended: "red",
			Cancelled: "darkgrey",
		};
		const c = colors[doc.status] || "grey";
		return [
			__(doc.status),
			c,
			`status,=,${doc.status}`,
		];
	},
	formatters: {
		agency_name(value) {
			return `<a href="/app/agency/${value}" style="font-weight:600;">${value}</a>`;
		},
	},
};
