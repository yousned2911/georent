import frappe
from frappe.model.document import Document
from frappe.utils import getdate

VALID_STATUS_TRANSITIONS = {
    "Available": ["Reserved", "Maintenance", "Sold", "Inactive"],
    "Reserved": ["Rented", "Available", "Maintenance", "Sold", "Inactive"],
    "Rented": ["Available", "Maintenance", "Sold", "Inactive"],
    "Maintenance": ["Available", "Sold", "Inactive"],
    "Sold": [],
    "Inactive": ["Available"],
}


class Vehicle(Document):
    def validate(self):
        self._validate_year()
        self._validate_daily_rate()
        self._validate_mileage()
        self._validate_dates()
        self._validate_status_transition()

    def before_insert(self):
        if not self.status:
            self.status = "Available"
        if self.active is None:
            self.active = 1

    def _validate_year(self):
        current_year = getdate().year
        if self.year and self.year > current_year:
            frappe.throw(frappe._("Year cannot be in the future. Current year is {0}.").format(current_year))
        if self.year and self.year < 1900:
            frappe.throw(frappe._("Year must be after 1900."))

    def _validate_daily_rate(self):
        if self.daily_rate is not None and self.daily_rate < 0:
            frappe.throw(frappe._("Daily rate must be positive."))

    def _validate_mileage(self):
        if self.current_mileage is not None and self.current_mileage < 0:
            frappe.throw(frappe._("Mileage cannot be negative."))

    def _validate_dates(self):
        today = getdate()

        if self.insurance_expiry and getdate(self.insurance_expiry) < today:
            frappe.throw(
                frappe._("Insurance expiry date ({0}) cannot be before today.").format(self.insurance_expiry)
            )

        if self.technical_inspection_expiry and getdate(self.technical_inspection_expiry) < today:
            frappe.throw(
                frappe._("Technical inspection expiry date ({0}) cannot be before today.").format(
                    self.technical_inspection_expiry
                )
            )

        if self.registration_expiry and getdate(self.registration_expiry) < today:
            frappe.throw(
                frappe._("Registration expiry date ({0}) cannot be before today.").format(
                    self.registration_expiry
                )
            )

    def _validate_status_transition(self):
        if self._is_new():
            return

        if not self.has_value_changed("status"):
            return

        old_doc = self.get_doc_before_save()
        if not old_doc:
            return

        old_status = old_doc.status
        new_status = self.status

        allowed = VALID_STATUS_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            frappe.throw(
                frappe._("Cannot transition from {0} to {1}. Allowed: {2}").format(
                    old_status,
                    new_status,
                    ", ".join(allowed) if allowed else "None (terminal state)",
                )
            )

    def set_reserved(self):
        self.status = "Reserved"
        self.save()

    def set_rented(self):
        self.status = "Rented"
        self.save()

    def set_available(self):
        self.status = "Available"
        self.save()

    def set_maintenance(self):
        self.status = "Maintenance"
        self.save()

    def set_sold(self):
        self.status = "Sold"
        self.active = 0
        self.save()

    def set_inactive(self):
        self.status = "Inactive"
        self.active = 0
        self.save()
