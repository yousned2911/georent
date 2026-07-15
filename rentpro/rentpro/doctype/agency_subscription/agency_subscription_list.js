frappe.listview_settings["Agency Subscription"] = {
	get_indicator(doc) {
		const colors = {
			Active: "green",
			"Past Due": "orange",
			Cancelled: "red",
			Trial: "blue",
		};
		const c = colors[doc.status] || "grey";
		return [
			__(doc.status),
			c,
			`status,=,${doc.status}`,
		];
	},
};
