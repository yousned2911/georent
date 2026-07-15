frappe.listview_settings["Geofence Zone"] = {
	get_indicator(doc) {
		const colors = {
			Depot: "blue",
			"Customer Zone": "green",
			Restricted: "red",
			"Speed Limit": "orange",
			Airport: "purple",
		};
		const c = colors[doc.zone_type] || "grey";
		return [
			__(doc.zone_type),
			c,
			`zone_type,=,${doc.zone_type}`,
		];
	},
};
