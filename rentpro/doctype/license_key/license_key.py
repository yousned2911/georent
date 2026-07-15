import hashlib
import json

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class LicenseKey(Document):
    def validate(self):
        self._validate_dates()
        self._generate_license_data()

    def _validate_dates(self):
        if self.issued_date and self.expiry_date:
            if getdate(self.issued_date) > getdate(self.expiry_date):
                frappe.throw(frappe._("Issued date cannot be after expiry date."))

    def _generate_license_data(self):
        payload = {
            "agency": self.agency,
            "plan": self.plan,
            "issued": str(self.issued_date),
            "expiry": str(self.expiry_date),
            "max_agencies": self.max_agencies,
        }
        raw = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(raw.encode()).hexdigest()[:32]
        self.license_data = f"{raw}|sig:{signature}"

    def activate_for_agency(self):
        if self.status != "Active":
            frappe.throw(frappe._("License is not active."))
        if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
            self.status = "Expired"
            self.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.throw(frappe._("License has expired."))

        if self.max_agencies and self.activated_count >= self.max_agencies:
            frappe.throw(frappe._("License has reached maximum " "activation count."))

        self.activated_count = (self.activated_count or 0) + 1
        self.save(ignore_permissions=True)
        frappe.db.commit()

    def is_valid(self):
        if self.status != "Active":
            return False
        if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
            return False
        return True

    def revoke(self):
        self.status = "Revoked"
        self.save(ignore_permissions=True)
        frappe.db.commit()
