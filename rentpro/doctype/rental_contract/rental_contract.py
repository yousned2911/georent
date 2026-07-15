import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt, nowdate

VALID_STATUS_TRANSITIONS = {
    "Draft": ["Active", "Cancelled"],
    "Active": ["Completed", "Cancelled"],
    "Completed": [],
    "Cancelled": [],
}

VEHICLE_STATUS_MAP = {
    "Draft": "Reserved",
    "Active": "Rented",
    "Completed": "Available",
    "Cancelled": "Available",
}

TVA_RATE_MAP = {
    "20%": 0.20,
    "14%": 0.14,
    "10%": 0.10,
    "7%": 0.07,
    "0%": 0.0,
}


class RentalContract(Document):
    def validate(self):
        self._validate_vehicle_exists()
        self._validate_customer_exists()
        self._validate_status_transition()
        self._validate_no_edit_after_complete()
        self._validate_return_mileage()
        self._validate_fuel_levels()
        self._validate_return_date()
        self._calculate_number_of_days()
        self._calculate_financials()

    def before_insert(self):
        if not self.status:
            self.status = "Draft"
        if not self.contract_date:
            self.contract_date = nowdate()
        if not self.created_by:
            self.created_by = frappe.session.user
        if self.active is None:
            self.active = 1
        if not self.payment_status:
            self.payment_status = "Unpaid"

    def on_update(self):
        self._handle_status_change()

    def on_trash(self):
        self._restore_vehicle_on_delete()

    # ──────────── validation ────────────

    def _validate_vehicle_exists(self):
        if self.vehicle and not frappe.db.exists("Vehicle", self.vehicle):
            frappe.throw(frappe._("Vehicle {0} does not exist.").format(self.vehicle))

    def _validate_customer_exists(self):
        if self.customer and not frappe.db.exists("Customer", self.customer):
            frappe.throw(frappe._("Customer {0} does not exist.").format(self.customer))

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
                frappe._("Cannot transition from {0} to {1}. " "Allowed: {2}").format(
                    old_status,
                    new_status,
                    ", ".join(allowed) if allowed else "None (terminal state)",
                )
            )

    def _validate_no_edit_after_complete(self):
        if self._is_new():
            return
        old_doc = self.get_doc_before_save()
        if not old_doc:
            return
        if old_doc.status in ("Completed", "Cancelled"):
            frappe.throw(frappe._("Contract cannot be edited once {0}.").format(old_doc.status))

    def _validate_return_mileage(self):
        if (
            self.return_mileage is not None
            and self.pickup_mileage is not None
            and self.return_mileage < self.pickup_mileage
        ):
            frappe.throw(
                frappe._("Return mileage ({0}) cannot be less " "than pickup mileage ({1}).").format(
                    self.return_mileage,
                    self.pickup_mileage,
                )
            )

    def _validate_fuel_levels(self):
        for field in (
            "pickup_fuel_level",
            "return_fuel_level",
        ):
            val = getattr(self, field, None)
            if val is not None and (val < 0 or val > 100):
                frappe.throw(
                    frappe._("{0} must be between 0 and 100.").format(field.replace("_", " ").title())
                )

    def _validate_return_date(self):
        if self.pickup_datetime and self.actual_return_datetime:
            if self.actual_return_datetime < self.pickup_datetime:
                frappe.throw(frappe._("Actual return date cannot be " "before pickup date."))

    # ──────────── calculations ────────────

    def _calculate_number_of_days(self):
        if self.pickup_datetime and self.expected_return_datetime:
            self.number_of_days = max(
                date_diff(
                    self.expected_return_datetime,
                    self.pickup_datetime,
                ),
                0,
            )

    def _calculate_financials(self):
        if self.daily_rate and self.number_of_days:
            self.subtotal = flt(self.daily_rate * self.number_of_days)
        else:
            self.subtotal = 0

        taxable = self.subtotal
        if self.discount:
            taxable -= self.discount
        if self.additional_charges:
            taxable += self.additional_charges
        if self.late_return_fee:
            taxable += self.late_return_fee
        if self.damage_fee:
            taxable += self.damage_fee

        taxable = max(taxable, 0)

        tva_pct = TVA_RATE_MAP.get(self.tva_rate or "20%", 0.20)
        self.tva_amount = flt(taxable * tva_pct)

        self.grand_total = flt(taxable + self.tva_amount)

    # ──────────── status & vehicle ────────────

    def _handle_status_change(self):
        if self._is_new():
            return
        if not self.has_value_changed("status"):
            return

        self._update_vehicle_status()
        self._create_timeline_entry()
        self._create_sales_invoice_if_active()

    def _update_vehicle_status(self):
        if not self.vehicle:
            return

        new_vehicle_status = VEHICLE_STATUS_MAP.get(self.status)
        if not new_vehicle_status:
            return

        vehicle = frappe.get_doc("Vehicle", self.vehicle)
        if vehicle.status != new_vehicle_status:
            vehicle.status = new_vehicle_status
            vehicle.save(ignore_permissions=True)
            frappe.msgprint(
                frappe._("Vehicle {0} status updated to {1}.").format(vehicle.name, new_vehicle_status),
                alert=True,
            )

    def _create_timeline_entry(self):
        if not self.name:
            return
        messages = {
            "Active": frappe._("Contract activated."),
            "Completed": frappe._("Contract completed."),
            "Cancelled": frappe._("Contract cancelled."),
        }
        msg = messages.get(self.status)
        if msg:
            self.add_comment("Info", msg)

    def _create_sales_invoice_if_active(self):
        if self.status != "Active":
            return

        existing = frappe.db.get_all(
            "Sales Invoice",
            filters={
                "rental_contract": self.name,
                "docstatus": 1,
            },
            fields=["name"],
        )
        if existing:
            return

        items = []
        if self.daily_rate and self.number_of_days:
            items.append(
                {
                    "item_name": "Rental - {0} days".format(self.number_of_days),
                    "description": ("Vehicle rental: {0} to {1}").format(
                        self.pickup_datetime,
                        self.expected_return_datetime,
                    ),
                    "qty": self.number_of_days,
                    "rate": self.daily_rate,
                    "amount": self.subtotal,
                }
            )

        if self.additional_charges:
            items.append(
                {
                    "item_name": "Additional Charges",
                    "qty": 1,
                    "rate": self.additional_charges,
                    "amount": self.additional_charges,
                }
            )

        if self.damage_fee:
            items.append(
                {
                    "item_name": "Damage Fee",
                    "qty": 1,
                    "rate": self.damage_fee,
                    "amount": self.damage_fee,
                }
            )

        if not items:
            return

        si = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "rental_contract": self.name,
                "posting_date": nowdate(),
                "due_date": nowdate(),
                "items": items,
                "remarks": ("Auto-generated from Rental " "Contract {0}").format(self.name),
            }
        )

        tva_pct = TVA_RATE_MAP.get(self.tva_rate or "20%", 0.20)
        if tva_pct > 0:
            taxable = sum(item["amount"] for item in items)
            if self.discount:
                taxable -= self.discount
            taxable = max(taxable, 0)
            si.append(
                "taxes",
                {
                    "charge_type": "On Net Total",
                    "account_head": "VAT - RP",
                    "description": "TVA {0}".format(self.tva_rate),
                    "rate": tva_pct * 100,
                    "tax_amount": flt(taxable * tva_pct),
                },
            )

        si.insert(ignore_permissions=True)
        frappe.msgprint(
            frappe._("Sales Invoice {0} created.").format(si.name),
            alert=True,
        )

    def _restore_vehicle_on_delete(self):
        if not self.vehicle:
            return
        if self.status in ("Draft", "Active"):
            vehicle = frappe.get_doc("Vehicle", self.vehicle)
            if vehicle.status in ("Reserved", "Rented"):
                vehicle.status = "Available"
                vehicle.save(ignore_permissions=True)


def on_contract_update(doc, method=None):
    """Hook handler for Rental Contract on_update."""
    pass


def on_contract_submit(doc, method=None):
    """Hook handler - kept for backward compat."""
    pass


def on_contract_cancel(doc, method=None):
    """Hook handler - kept for backward compat."""
    pass
