import frappe
from frappe.model.document import Document


class GeofenceZone(Document):
    def validate(self):
        self._validate_coordinates()
        self._validate_radius()

    def _validate_coordinates(self):
        if self.center_latitude is not None:
            if self.center_latitude < -90 or self.center_latitude > 90:
                frappe.throw(frappe._("Latitude must be between -90 and 90."))
        if self.center_longitude is not None:
            if self.center_longitude < -180 or self.center_longitude > 180:
                frappe.throw(frappe._("Longitude must be between -180 and 180."))

    def _validate_radius(self):
        if self.boundary_type == "Circle":
            if not self.radius or self.radius <= 0:
                frappe.throw(frappe._("Radius must be positive for circular zones."))
