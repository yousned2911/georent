import frappe
from frappe.model.document import Document


class SubscriptionPlan(Document):
    def validate(self):
        self._validate_pricing()
        self._validate_limits()

    def _validate_pricing(self):
        if self.price_mad is not None and self.price_mad < 0:
            frappe.throw(frappe._("Price cannot be negative."))
        if self.price_yearly_mad and self.price_mad:
            if self.price_yearly_mad >= self.price_mad * 12:
                frappe.msgprint(
                    frappe._("Yearly price should be less than " "12x monthly price for discount."),
                    alert=True,
                )

    def _validate_limits(self):
        if self.max_vehicles is not None and self.max_vehicles < 1:
            frappe.throw(frappe._("Maximum vehicles must be at least 1."))
        if self.max_users is not None and self.max_users < 1:
            frappe.throw(frappe._("Maximum users must be at least 1."))
