import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class VehicleTracking(Document):
    def validate(self):
        self._validate_coordinates()

    def _validate_coordinates(self):
        if self.last_latitude is not None:
            if self.last_latitude < -90 or self.last_latitude > 90:
                frappe.throw(frappe._("Latitude must be between -90 and 90."))
        if self.last_longitude is not None:
            if self.last_longitude < -180 or self.last_longitude > 180:
                frappe.throw(frappe._("Longitude must be between -180 and 180."))

    def update_from_position(self, position_data):
        self.last_latitude = position_data.get("latitude")
        self.last_longitude = position_data.get("longitude")
        self.last_speed = position_data.get("speed", 0)
        self.ignition = position_data.get("ignition", False)
        self.fuel_level = position_data.get("fuel_level", 0)
        self.battery_level = position_data.get("battery", 0)
        self.engine_running = position_data.get("engine_running", False)
        self.gps_signal_strength = position_data.get("gps_signal_strength", 0)
        self.current_mileage = position_data.get("current_mileage", self.current_mileage)
        self.last_update = position_data.get("timestamp", now_datetime())
        self.provider = position_data.get("provider", "Mock")

        speed = self.last_speed or 0
        if speed > 2:
            self.status = "Moving"
        elif self.ignition:
            self.status = "Idle"
        else:
            self.status = "Offline"

        if self.fuel_level and self.fuel_level < 10:
            self.status = "Maintenance"
