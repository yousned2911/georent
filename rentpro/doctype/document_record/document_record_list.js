frappe.listview_settings["Document Record"] = {
	get_indicator(doc) {
		const colors = {
			Active: "green",
			Expired: "red",
			Archived: "grey",
		};
		const c = colors[doc.status] || "grey";
		return [
			__(doc.status),
			c,
			`status,=,${doc.status}`,
		];
	},
	formatters: {
		document_number(value) {
			return `<a href="/app/document-record/${value}" style="font-weight:600;">${value}</a>`;
		},
	},
};
