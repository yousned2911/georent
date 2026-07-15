import frappe
from frappe.model.document import Document


class SystemHealthSettings(Document):
    def validate(self):
        self._validate_thresholds()

    def _validate_thresholds(self):
        for field in [
            "cpu_threshold_percent",
            "memory_threshold_percent",
            "disk_threshold_percent",
        ]:
            val = getattr(self, field, None)
            if val is not None and (val < 0 or val > 100):
                frappe.throw(
                    frappe._("{0} must be between 0 and 100.").format(field.replace("_", " ").title())
                )


def has_permission(doc, user=None, permission_type=None):
    if frappe.session.user == "Administrator":
        return True
    roles = frappe.get_roles(user)
    if "System Manager" in roles:
        return True
    return False
