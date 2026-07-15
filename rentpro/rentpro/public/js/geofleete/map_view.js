// GeoFleete Map View - Fleet Map with vehicle markers and geofences

frappe.provide("geofleete.map");

geofleete.map = {
	map: null,
	markers: {},
	circles: [],
	polylines: [],

	init() {
		if (typeof L === "undefined") {
			frappe.msgprint __("Leaflet.js is required for the map. Please load the map library."));
			return;
		}
		this.create_map();
		this.load_vehicles();
		this.load_geofences();
		this.start_auto_refresh();
	},

	create_map() {
		const container = document.getElementById("geofleete-map");
		if (!container) return;

		this.map = L.map("geofleete-map").setView(
			[33.5731, -7.5898], 12
		);

		L.tileLayer(
			"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
			{
				attribution: "© OpenStreetMap contributors",
				maxZoom: 19,
			}
		).addTo(this.map);

		setTimeout(() => this.map.invalidateSize(), 100);
	},

	load_vehicles() {
		frappe.call({
			method:
				"rentpro.gps.api.get_fleet_positions",
			callback: (r) => {
				if (r.message) {
					this.update_markers(r.message);
				}
			},
		});
	},

	load_geofences() {
		frappe.call({
			method:
				"rentpro.gps.api.get_active_geofences",
			callback: (r) => {
				if (r.message) {
					this.draw_geofences(r.message);
				}
			},
		});
	},

	update_markers(vehicles) {
		Object.values(this.markers).forEach((m) =>
			this.map.removeLayer(m)
		);
		this.markers = {};

		vehicles.forEach((v) => {
			const color = this.get_status_color(v.status);
			const icon = L.divIcon({
				className: "fleet-marker",
				html: `<div style="
					background:${color};
					width:12px;height:12px;
					border-radius:50%;
					border:2px solid white;
					box-shadow:0 1px 3px rgba(0,0,0,0.4);
				"></div>`,
				iconSize: [12, 12],
				iconAnchor: [6, 6],
			});

			const marker = L.marker(
				[v.latitude, v.longitude],
				{ icon }
			).addTo(this.map);

			marker.bindPopup(`
				<b>${v.plate_number || v.vehicle}</b><br>
				Status: ${v.status}<br>
				Speed: ${(v.speed || 0).toFixed(1)} km/h<br>
				Fuel: ${(v.fuel_level || 0).toFixed(0)}%<br>
				Battery: ${(v.battery_level || 0).toFixed(0)}%<br>
				Last update: ${v.last_update || "N/A"}
			`);

			this.markers[v.vehicle] = marker;
		});
	},

	draw_geofences(zones) {
		this.circles.forEach((c) => this.map.removeLayer(c));
		this.circles = [];

		zones.forEach((z) => {
			if (z.center_latitude && z.center_longitude) {
				const circle = L.circle(
					[z.center_latitude, z.center_longitude],
					{
						radius: z.radius || 500,
						color: this.get_zone_color(z.zone_type),
						fillOpacity: 0.1,
						weight: 2,
					}
				).addTo(this.map);
				circle.bindPopup(
					`<b>${z.zone_name}</b><br>${z.zone_type}`
				);
				this.circles.push(circle);
			}
		});
	},

	get_status_color(status) {
		const colors = {
			Moving: "#3b82f6",
			Idle: "#f59e0b",
			Online: "#22c55e",
			Offline: "#ef4444",
			Maintenance: "#6b7280",
		};
		return colors[status] || "#9ca3af";
	},

	get_zone_color(type) {
		const colors = {
			Depot: "#3b82f6",
			"Customer Zone": "#22c55e",
			Restricted: "#ef4444",
			"Speed Limit": "#f59e0b",
			Airport: "#8b5cf6",
		};
		return colors[type] || "#6b7280";
	},

	start_auto_refresh() {
		setInterval(() => this.load_vehicles(), 30000);
	},
};

$(document).ready(() => {
	if (
		document.getElementById("geofleete-map")
	) {
		geofleete.map.init();
	}
});
