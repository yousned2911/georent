import frappe
from frappe.model.document import Document


class SaaSSettings(Document):
    def validate(self):
        self._validate_grace_period()

    def _validate_grace_period(self):
        if self.grace_period_days and self.grace_period_days < 0:
            frappe.throw(frappe._("Grace period cannot be negative."))


def has_permission(doc, user=None, permission_type=None, **kwargs):
    if frappe.session.user == "Administrator":
        return True
    if permission_type == "read":
        return True
    roles = frappe.get_roles(user)
    if "System Manager" in roles:
        return True
    return False
