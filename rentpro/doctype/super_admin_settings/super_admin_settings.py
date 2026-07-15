import frappe
from frappe.model.document import Document


class SuperAdminSettings(Document):
    def validate(self):
        self._validate_limits()

    def _validate_limits(self):
        if self.max_trial_extension_days and self.max_trial_extension_days < 0:
            frappe.throw(frappe._("Max trial extension cannot be negative."))
        if self.max_extensions_per_agency and self.max_extensions_per_agency < 0:
            frappe.throw(frappe._("Max extensions per agency cannot be negative."))


def has_permission(doc, user=None, permission_type=None, **kwargs):
    if frappe.session.user == "Administrator":
        return True
    roles = frappe.get_roles(user)
    if "System Manager" in roles:
        return True
    return False
