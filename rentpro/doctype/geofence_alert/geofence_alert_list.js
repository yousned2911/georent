frappe.listview_settings["Geofence Alert"] = {
	get_indicator(doc) {
		const severity_colors = {
			Low: "blue",
			Medium: "orange",
			High: "red",
			Critical: "darkred",
		};
		const c = severity_colors[doc.severity] || "grey";
		if (doc.is_acknowledged) return [__("Resolved"), "green"];
		return [
			__(doc.severity),
			c,
			`severity,=,${doc.severity}`,
		];
	},
};
