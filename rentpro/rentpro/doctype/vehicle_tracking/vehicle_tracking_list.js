frappe.listview_settings["Vehicle Tracking"] = {
	get_indicator(doc) {
		const colors = {
			Online: "green",
			Offline: "red",
			Idle: "orange",
			Moving: "blue",
			Maintenance: "darkgrey",
		};
		const c = colors[doc.status] || "grey";
		return [
			__(doc.status),
			c,
			`status,=,${doc.status}`,
		];
	},
};
