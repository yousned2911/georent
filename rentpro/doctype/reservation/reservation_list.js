frappe.listview_settings["Reservation"] = {
	get_indicator(doc) {
		const status_colors = {
			Draft: "orange",
			Confirmed: "blue",
			"Picked Up": "green",
			Completed: "darkgrey",
			Cancelled: "red",
			"No Show": "red",
		};
		const color = status_colors[doc.status] || "grey";
		return [__(doc.status), color, `status,=,${doc.status}`];
	},
};

frappe.listview_settings["Reservation"].formatters = {
	reservation_number(value) {
		return `<a href="/app/reservation/${value}" style="font-weight:600;">${value}</a>`;
	},
};
