frappe.listview_settings["GPS Position"] = {
	get_indicator(doc) {
		if (doc.speed > 100) return [__("Overspeed"), "red", "speed,>,100"];
		if (doc.ignition) return [__("Moving"), "green", "ignition,=,1"];
		return [__("Stationary"), "orange", "ignition,=,0"];
	},
};
