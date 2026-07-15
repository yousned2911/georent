import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class GeofenceAlert(Document):
    def validate(self):
        self._validate_vehicle()
        self._validate_zone()

    def before_insert(self):
        self._auto_set_severity()

    def acknowledge(self, notes=None):
        self.is_acknowledged = 1
        self.acknowledged_by = frappe.session.user
        self.acknowledged_at = now_datetime()
        if notes:
            self.resolution_notes = notes
        self.save(ignore_permissions=True)
        frappe.db.commit()

    def _validate_vehicle(self):
        if self.vehicle and not frappe.db.exists("Vehicle", self.vehicle):
            frappe.throw(frappe._("Vehicle {0} does not exist.").format(self.vehicle))

    def _validate_zone(self):
        if self.zone and not frappe.db.exists("Geofence Zone", self.zone):
            frappe.throw(frappe._("Geofence Zone {0} does not exist.").format(self.zone))

    def _auto_set_severity(self):
        if self.alert_type == "Speed Violation":
            self.severity = "High"
        elif self.alert_type == "Unauthorized Use":
            self.severity = "Critical"
        elif self.alert_type == "Prolonged Stay":
            self.severity = "Medium"


def create_alert(vehicle, zone, event_type, latitude=None, longitude=None, speed=None, distance=None):
    """Create a Geofence Alert from provider event."""
    zone_doc = frappe.get_doc("Geofence Zone", zone)
    severity_map = {
        "Entry": "Low",
        "Exit": "Medium",
        "Speed Violation": "High",
        "Unauthorized Use": "Critical",
        "Prolonged Stay": "Medium",
    }
    alert = frappe.get_doc(
        {
            "doctype": "Geofence Alert",
            "vehicle": vehicle,
            "zone": zone,
            "alert_type": event_type,
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "distance": distance,
            "severity": severity_map.get(event_type, "Medium"),
            "agency": zone_doc.agency,
        }
    )
    alert.insert(ignore_permissions=True)
    frappe.db.commit()
    return alert


def on_geofence_alert_update(doc, method):
    """Hook handler for Geofence Alert on_update."""
    pass
