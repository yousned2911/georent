import frappe
from frappe.model.document import Document


class GeoFleeteSettings(Document):
    def validate(self):
        self._validate_gps_retention()
        self._validate_simulation_params()

    def before_save(self):
        self._set_coming_soon_banner()

    def _validate_gps_retention(self):
        if self.gps_retention_days and self.gps_retention_days < 1:
            frappe.throw(frappe._("GPS retention days must be at least 1."))

    def _validate_simulation_params(self):
        if self.mock_mode:
            if self.default_latitude and (self.default_latitude < -90 or self.default_latitude > 90):
                frappe.throw(frappe._("Latitude must be between -90 and 90."))
            if self.default_longitude and (self.default_longitude < -180 or self.default_longitude > 180):
                frappe.throw(frappe._("Longitude must be between -180 and 180."))

    def _set_coming_soon_banner(self):
        if self.gps_provider and self.gps_provider != "Mock":
            self.coming_soon_banner = (
                '<div style="padding:15px;background:#fff3cd;'
                "border:1px solid #ffc107;border-radius:6px;"
                'margin:10px 0;">'
                "<h5 style='color:#856404;'>"
                "🚧 Coming Soon: "
                f"{self.gps_provider} Integration</h5>"
                "<p style='color:#856404;margin:5px 0 0;'>"
                "External GPS provider integration is under "
                "development. The Mock provider is currently "
                "active and simulating realistic fleet data."
                "</p></div>"
            )
        else:
            self.coming_soon_banner = ""


def has_permission(doc, user=None, permission_type=None, **kwargs):
    if frappe.session.user == "Administrator":
        return True
    if permission_type == "read":
        return True
    roles = frappe.get_roles(user)
    if "Rent Pro Manager" in roles or "System Manager" in roles:
        return True
    if "Rent Pro Fleet Manager" in roles:
        return True
    return False
