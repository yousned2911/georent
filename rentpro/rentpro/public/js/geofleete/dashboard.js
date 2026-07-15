// GeoFleete Dashboard - Fleet overview with KPIs and real-time data

frappe.provide("geofleete.dashboard");

geofleete.dashboard = {
	refresh() {
		this.load_summary();
		this.load_alerts();
		this.load_maintenance();
	},

	load_summary() {
		frappe.call({
			method: "rentpro.gps.api.get_fleet_summary",
			callback: (r) => {
				if (r.message) {
					this.render_summary(r.message);
				}
			},
		});
	},

	render_summary(data) {
		const container = document.getElementById("fleet-summary");
		if (!container) return;

		const cards = [
			{
				label: "Total Vehicles",
				value: data.total || 0,
				color: "#3b82f6",
				icon: "fa-truck",
			},
			{
				label: "Moving",
				value: data.moving || 0,
				color: "#22c55e",
				icon: "fa-road",
			},
			{
				label: "Idle",
				value: data.idle || 0,
				color: "#f59e0b",
				icon: "fa-pause",
			},
			{
				label: "Offline",
				value: data.offline || 0,
				color: "#ef4444",
				icon: "fa-power-off",
			},
			{
				label: "Avg Fuel",
				value: (data.avg_fuel || 0).toFixed(0) + "%",
				color: "#06b6d4",
				icon: "fa-gas-pump",
			},
			{
				label: "Active Alerts",
				value: data.active_alerts || 0,
				color: "#dc2626",
				icon: "fa-bell",
			},
		];

		container.innerHTML = cards
			.map(
				(c) => `
			<div class="col-sm-2">
				<div class="rent-pro-kpi-card" style="border-left:4px solid ${c.color}">
					<div class="number" style="color:${c.color}">${c.value}</div>
					<div class="label">${__(c.label)}</div>
				</div>
			</div>
		`
			)
			.join("");
	},

	load_alerts() {
		frappe.call({
			method: "rentpro.gps.api.get_recent_alerts",
			args: { limit: 5 },
			callback: (r) => {
				if (r.message) {
					this.render_alerts(r.message);
				}
			},
		});
	},

	render_alerts(alerts) {
		const container = document.getElementById("recent-alerts");
		if (!container) return;

		if (!alerts.length) {
			container.innerHTML =
				'<p class="text-muted">No recent alerts</p>';
			return;
		}

		container.innerHTML = alerts
			.map(
				(a) => `
			<div class="flex items-center" style="padding:8px 0;border-bottom:1px solid #eee;">
				<span class="indicator-pill whitespace-nowrap ${
					a.severity === "Critical"
						? "red"
						: a.severity === "High"
						? "orange"
						: "blue"
				}" style="margin-right:8px;">${__(a.severity)}</span>
				<span style="flex:1;">${a.vehicle} — ${__(a.alert_type)} in ${a.zone_name || a.zone}</span>
				<span class="text-muted" style="font-size:12px;">${frappe.datetime.str_to_user(a.alert_timestamp)}</span>
			</div>
		`
			)
			.join("");
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
			"maintenance-alerts"
		);
		if (!container) return;

		if (!items.length) {
			container.innerHTML =
				'<p class="text-muted">No maintenance due</p>';
			return;
		}

		container.innerHTML = items
			.map(
				(m) => `
			<div style="padding:8px 0;border-bottom:1px solid #eee;">
				<b>${m.vehicle}</b> — ${m.type}<br>
				<span class="text-muted">${m.description}</span>
				<span class="indicator-pill ${
					m.priority === "High" ? "red" : "orange"
				}" style="margin-left:8px;">${m.priority}</span>
			</div>
		`
			)
			.join("");
	},
};

$(document).ready(() => {
	if (document.getElementById("geofleete-dashboard")) {
		geofleete.dashboard.refresh();
	}
});
