// GeoFleete Maintenance Page - Vehicle maintenance reminders and status

frappe.provide("geofleete.maintenance");

geofleete.maintenance = {
	refresh() {
		this.load_maintenance();
	},

	load_maintenance() {
		frappe.call({
			method: "rentpro.gps.api.get_maintenance_alerts",
			callback: (r) => {
				if (r.message) {
					this.render_maintenance(r.message);
				}
			},
		});
	},

	render_maintenance(items) {
		const container = document.getElementById(
			"maintenance-list"
		);
		if (!container) return;

		if (!items.length) {
			container.innerHTML =
				'<p class="text-muted">No maintenance reminders</p>';
			return;
		}

		const priority_colors = {
			High: "red",
			Medium: "orange",
			Low: "blue",
		};

		container.innerHTML = items
			.map(
				(m) => `
			<div style="padding:12px;margin-bottom:8px;border:1px solid #eee;border-radius:6px;border-left:4px solid ${
				m.priority === "High"
					? "#ef4444"
					: m.priority === "Medium"
					? "#f59e0b"
					: "#3b82f6"
			};">
				<div class="flex items-center">
					<b style="flex:1;"><a href="/app/vehicle/${m.vehicle}">${m.vehicle}</a></b>
					<span class="indicator-pill ${priority_colors[m.priority] || "grey"}">${m.priority}</span>
				</div>
				<div style="margin-top:4px;">
					${m.type}: ${m.description}
				</div>
				<div class="text-muted" style="font-size:12px;margin-top:4px;">
					${
						m.due_mileage
							? "Due at: " +
							  m.due_mileage.toLocaleString() +
							  " km (current: " +
							  m.current_mileage.toLocaleString() +
							  " km)"
							: ""
					}
					${m.due_date ? "Due: " + m.due_date : ""}
				</div>
			</div>
		`
			)
			.join("");
	},
};

$(document).ready(() => {
	if (document.getElementById("maintenance-list")) {
		geofleete.maintenance.refresh();
	}
});
