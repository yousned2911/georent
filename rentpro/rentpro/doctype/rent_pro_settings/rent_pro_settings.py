import frappe
from frappe.model.document import Document


class RentProSettings(Document):
    def validate(self):
        self._validate_ocr_threshold()
        self._validate_gps_retention()

    def _validate_ocr_threshold(self):
        if self.ocr_enabled and (self.ocr_confidence_threshold < 0 or self.ocr_confidence_threshold > 100):
            frappe.throw(frappe._("OCR confidence threshold must be between 0 and 100"))

    def _validate_gps_retention(self):
        if self.geofleete_enabled and self.gps_retention_days < 1:
            frappe.throw(frappe._("GPS retention days must be at least 1"))


def has_permission(doc, user=None, permission_type=None, **kwargs):
    if frappe.session.user == "Administrator":
        return True
    if permission_type == "read":
        return True
    roles = frappe.get_roles(user)
    if "Rent Pro Manager" in roles or "System Manager" in roles:
        return True
    return False
