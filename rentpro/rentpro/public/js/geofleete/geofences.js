// GeoFleete Geofences Page - View and manage geofence zones

frappe.provide("geofleete.geofences");

geofleete.geofences = {
	refresh() {
		this.load_zones();
	},

	load_zones() {
		frappe.call({
			method: "rentpro.gps.api.get_active_geofences",
			callback: (r) => {
				if (r.message) {
					this.render_zones(r.message);
				}
			},
		});
	},

	render_zones(zones) {
		const container = document.getElementById("zones-list");
		if (!container) return;

		if (!zones.length) {
			container.innerHTML =
				'<p class="text-muted">No geofence zones configured</p>';
			return;
		}

		const zone_type_colors = {
			Depot: "blue",
			"Customer Zone": "green",
			Restricted: "red",
			"Speed Limit": "orange",
			Airport: "purple",
		};

		container.innerHTML = zones
			.map(
				(z) => `
			<div style="padding:12px;margin-bottom:8px;border:1px solid #eee;border-radius:6px;">
				<div class="flex items-center">
					<span class="indicator-pill ${
						zone_type_colors[z.zone_type] || "grey"
					}" style="margin-right:8px;">${z.zone_type}</span>
					<b style="flex:1;"><a href="/app/geofence-zone/${z.name}">${z.zone_name}</a></b>
					${z.is_active ? '<span class="text-muted">Active</span>' : '<span class="text-muted">Inactive</span>'}
				</div>
				<div class="text-muted" style="font-size:12px;margin-top:4px;">
					Radius: ${z.radius || "N/A"}m |
					Lat: ${(z.center_latitude || 0).toFixed(4)} |
					Lng: ${(z.center_longitude || 0).toFixed(4)}
					${z.speed_limit ? " | Speed Limit: " + z.speed_limit + " km/h" : ""}
				</div>
				<div style="margin-top:4px;font-size:12px;">
					${z.notify_on_entry ? "✓ Entry alerts " : ""}
					${z.notify_on_exit ? "✓ Exit alerts " : ""}
					${z.notify_on_violation ? "✓ Violation alerts" : ""}
				</div>
			</div>
		`
			)
			.join("");
	},
};

$(document).ready(() => {
	if (document.getElementById("zones-list")) {
		geofleete.geofences.refresh();
	}
});
