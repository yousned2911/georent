// GeoFleete Alerts Page - View and acknowledge geofence alerts

frappe.provide("geofleete.alerts");

geofleete.alerts = {
	refresh() {
		this.load_alerts();
	},

	load_alerts() {
		frappe.call({
			method: "rentpro.gps.api.get_recent_alerts",
			args: { limit: 50, include_acknowledged: true },
			callback: (r) => {
				if (r.message) {
					this.render_alerts(r.message);
				}
			},
		});
	},

	render_alerts(alerts) {
		const container = document.getElementById("alerts-list");
		if (!container) return;

		if (!alerts.length) {
			container.innerHTML =
				'<p class="text-muted">No alerts</p>';
			return;
		}

		container.innerHTML = alerts
			.map(
				(a) => `
			<div class="flex items-center" style="padding:12px;margin-bottom:8px;border:1px solid #eee;border-radius:6px;background:${a.is_acknowledged ? "#f8f9fa" : "#fff8e1"};">
				<div style="flex:1;">
					<div>
						<span class="indicator-pill ${
							a.severity === "Critical"
								? "red"
								: a.severity === "High"
								? "orange"
								: a.severity === "Medium"
								? "yellow"
								: "blue"
						}" style="margin-right:8px;">${__(a.severity)}</span>
						<b>${a.vehicle}</b> — ${__(a.alert_type)}
					</div>
					<div class="text-muted" style="font-size:12px;margin-top:4px;">
						Zone: ${a.zone_name || a.zone} |
						Time: ${frappe.datetime.str_to_user(a.alert_timestamp)}
						${a.speed ? " | Speed: " + a.speed.toFixed(1) + " km/h" : ""}
					</div>
					${a.resolution_notes ? '<div style="margin-top:4px;font-size:12px;"><i>' + a.resolution_notes + "</i></div>" : ""}
				</div>
				${
					!a.is_acknowledged
						? `<button class="btn btn-sm btn-primary" onclick="geofleete.alerts.acknowledge('${a.name}')">${__("Acknowledge")}</button>`
						: '<span class="text-muted" style="font-size:12px;">✓ ' + __("Resolved") + "</span>"
				}
			</div>
		`
			)
			.join("");
	},

	acknowledge(alert_name) {
		frappe.prompt(
			{
				label: __("Resolution Notes"),
				fieldname: "notes",
				fieldtype: "Small Text",
			},
			(values) => {
				frappe.call({
					method:
						"rentpro.gps.api.acknowledge_alert",
					args: {
						alert_name: alert_name,
						notes: values.notes,
					},
					callback: () => {
						frappe.show_alert({
							message: __("Alert acknowledged"),
							indicator: "green",
						});
						this.load_alerts();
					},
				});
			},
			__("Acknowledge Alert"),
			__("Acknowledge")
		);
	},
};

$(document).ready(() => {
	if (document.getElementById("alerts-list")) {
		geofleete.alerts.refresh();
	}
});
