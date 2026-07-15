import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, today

VALID_STATUS_TRANSITIONS = {
    "Draft": ["Confirmed", "Cancelled"],
    "Confirmed": ["Picked Up", "Cancelled", "No Show"],
    "Picked Up": ["Completed"],
    "Completed": [],
    "Cancelled": [],
    "No Show": [],
}

# Statuses that count as "active" for overlap detection
ACTIVE_STATUSES = ["Confirmed", "Picked Up"]


def on_reservation_update(doc, method):
    """Hook handler called via doc_events when Reservation is saved."""
    pass


class Reservation(Document):
    def validate(self):
        self._validate_vehicle_exists()
        self._validate_customer_exists()
        self._validate_pickup_date()
        self._validate_return_date()
        self._validate_status_transition()
        self._validate_no_edit_after_complete()
        self._calculate_number_of_days()
        self._calculate_estimated_total()
        self._validate_deposit()
        self._validate_overlap()

    def before_insert(self):
        if not self.status:
            self.status = "Draft"
        if not self.reservation_date:
            self.reservation_date = today()
        if not self.created_by:
            self.created_by = frappe.session.user
        if self.active is None:
            self.active = 1

    def on_update(self):
        self._update_vehicle_status()

    def on_trash(self):
        self._restore_vehicle_on_delete()

    def _validate_vehicle_exists(self):
        if not frappe.db.exists("Vehicle", self.vehicle):
            frappe.throw(frappe._("Vehicle {0} does not exist.").format(self.vehicle))

    def _validate_customer_exists(self):
        if not frappe.db.exists("Customer", self.customer):
            frappe.throw(frappe._("Customer {0} does not exist.").format(self.customer))

    def _validate_pickup_date(self):
        if self.pickup_date and getdate(self.pickup_date) < getdate(today()):
            frappe.throw(frappe._("Pickup date cannot be before today."))

    def _validate_return_date(self):
        if self.pickup_date and self.expected_return_date:
            if getdate(self.expected_return_date) <= getdate(self.pickup_date):
                frappe.throw(frappe._("Expected return date must be after pickup date."))

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
        terminal = ("Completed", "Cancelled", "No Show")
        if old_doc.status in terminal:
            frappe.throw(frappe._("Reservation cannot be edited once {0}.").format(old_doc.status))

    def _calculate_number_of_days(self):
        if self.pickup_date and self.expected_return_date:
            self.number_of_days = max(
                date_diff(self.expected_return_date, self.pickup_date),
                0,
            )

    def _calculate_estimated_total(self):
        if self.daily_rate and self.number_of_days:
            total = self.daily_rate * self.number_of_days
            if self.discount:
                total -= self.discount
            self.estimated_total = max(total, 0)
        else:
            self.estimated_total = 0

    def _validate_deposit(self):
        if self.deposit_amount and self.estimated_total and self.deposit_amount > self.estimated_total:
            frappe.throw(
                frappe._("Deposit amount ({0}) cannot exceed " "estimated total ({1}).").format(
                    self.deposit_amount, self.estimated_total
                )
            )

    def _validate_overlap(self):
        if not self.vehicle or not self.pickup_date or not self.expected_return_date:
            return

        overlapping = frappe.db.sql(
            """
            SELECT
                name, reservation_number,
                pickup_date, expected_return_date
            FROM `tabReservation`
            WHERE vehicle = %s
              AND status IN %s
              AND name != %s
              AND expected_return_date > %s
              AND pickup_date < %s
            """,
            (
                self.vehicle,
                tuple(ACTIVE_STATUSES),
                self.name or "#####__NEW__",
                self.pickup_date,
                self.expected_return_date,
            ),
            as_dict=True,
        )

        if overlapping:
            conflict = overlapping[0]
            frappe.throw(
                frappe._(
                    "Vehicle already reserved during the "
                    "selected period. "
                    "Conflicting reservation: "
                    "{0} ({1} to {2})"
                ).format(
                    conflict.reservation_number,
                    conflict.pickup_date,
                    conflict.expected_return_date,
                )
            )

    def _update_vehicle_status(self):
        if not self.vehicle:
            return

        vehicle = frappe.get_doc("Vehicle", self.vehicle)

        status_map = {
            "Confirmed": "Reserved",
            "Picked Up": "Rented",
            "Completed": "Available",
            "Cancelled": "Available",
            "No Show": "Available",
        }

        new_status = status_map.get(self.status)
        if new_status and vehicle.status != new_status:
            vehicle.status = new_status
            vehicle.save(ignore_permissions=True)
            frappe.msgprint(
                frappe._("Vehicle {0} status updated to {1}.").format(vehicle.name, new_status),
                alert=True,
            )

    def _restore_vehicle_on_delete(self):
        if not self.vehicle:
            return

        if self.status in ("Confirmed", "Picked Up"):
            vehicle = frappe.get_doc("Vehicle", self.vehicle)
            if vehicle.status in ("Reserved", "Rented"):
                vehicle.status = "Available"
                vehicle.save(ignore_permissions=True)
