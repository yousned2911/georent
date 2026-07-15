// GeoFleete Vehicle Status - Real-time vehicle telemetry display

frappe.provide("geofleete.status");

geofleete.status = {
	refresh() {
		this.load_vehicle_states();
	},

	load_vehicle_states() {
		frappe.call({
			method: "rentpro.gps.api.get_all_vehicle_states",
			callback: (r) => {
				if (r.message) {
					this.render_table(r.message);
				}
			},
		});
	},

	render_table(states) {
		const container = document.getElementById(
			"vehicle-status-table"
		);
		if (!container) return;

		const vehicles = Object.entries(states);
		if (!vehicles.length) {
			container.innerHTML =
				'<p class="text-muted">No vehicle data available</p>';
			return;
		}

		const rows = vehicles
			.map(([name, s]) => {
				const status_class = s.is_moving
					? "green"
					: s.ignition
					? "orange"
					: "red";
				const fuel_class =
					s.fuel_level < 15
						? "red"
						: s.fuel_level < 30
						? "orange"
						: "green";
				const battery_class =
					s.battery_level < 20 ? "red" : "green";

				return `
				<tr>
					<td><a href="/app/vehicle/${name}">${name}</a></td>
					<td><span class="indicator-pill ${status_class}">${s.is_moving ? "Moving" : s.ignition ? "Idle" : "Offline"}</span></td>
					<td>${(s.speed || 0).toFixed(1)} km/h</td>
					<td><span class="indicator-pill ${fuel_class}">${(s.fuel_level || 0).toFixed(0)}%</span></td>
					<td><span class="indicator-pill ${battery_class}">${(s.battery_level || 0).toFixed(0)}%</span></td>
					<td>${s.ignition ? __("On") : __("Off")}</td>
					<td>${(s.gps_signal_strength || 0).toFixed(0)}%</td>
					<td>${frappe.datetime.str_to_user(s.last_update)}</td>
				</tr>
			`;
			})
			.join("");

		container.innerHTML = `
			<table class="table table-striped" style="width:100%">
				<thead>
					<tr>
						<th>${__("Vehicle")}</th>
						<th>${__("Status")}</th>
						<th>${__("Speed")}</th>
						<th>${__("Fuel")}</th>
						<th>${__("Battery")}</th>
						<th>${__("Ignition")}</th>
						<th>${__("GPS Signal")}</th>
						<th>${__("Last Update")}</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		`;
	},
};

$(document).ready(() => {
	if (document.getElementById("vehicle-status-table")) {
		geofleete.status.refresh();
		setInterval(
		() => geofleete.status.refresh(),
		30000
		);
	}
});
