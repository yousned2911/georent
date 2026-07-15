import frappe
from frappe.model.document import Document


class GPSPosition(Document):
    def validate(self):
        self._validate_coordinates()
        self._validate_speed()

    def _validate_coordinates(self):
        if self.latitude is not None:
            if self.latitude < -90 or self.latitude > 90:
                frappe.throw(frappe._("Latitude must be between -90 and 90."))
        if self.longitude is not None:
            if self.longitude < -180 or self.longitude > 180:
                frappe.throw(frappe._("Longitude must be between -180 and 180."))

    def _validate_speed(self):
        if self.speed is not None and self.speed < 0:
            frappe.throw(frappe._("Speed cannot be negative."))
        if self.speed is not None and self.speed > 300:
            frappe.throw(frappe._("Speed exceeds maximum (300 km/h)."))
