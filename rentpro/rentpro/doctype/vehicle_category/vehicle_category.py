import frappe
from frappe.model.document import Document


class VehicleCategory(Document):
    def validate(self):
        self._validate_daily_rate_multiplier()

    def _validate_daily_rate_multiplier(self):
        if self.daily_rate_multiplier and self.daily_rate_multiplier < 0:
            frappe.throw(frappe._("Daily rate multiplier cannot be negative"))
