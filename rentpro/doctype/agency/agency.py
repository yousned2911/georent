import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class Agency(Document):
    def validate(self):
        self._validate_dates()
        self._validate_trial_to_active()

    def before_insert(self):
        if not self.status:
            self.status = "Trial"
        if not self.trial_end_date:
            self.trial_end_date = add_days(today(), 14)

    def on_update(self):
        self._sync_subscription_status()

    def _validate_dates(self):
        if self.subscription_start and self.trial_end_date:
            if getdate(self.subscription_start) < getdate(self.trial_end_date):
                pass  # subscription can start after trial

    def _validate_trial_to_active(self):
        if self._is_new():
            return
        old = self.get_doc_before_save()
        if not old:
            return
        if old.status == "Trial" and self.status == "Active":
            if not self.subscription_plan:
                frappe.throw(frappe._("Cannot activate without a " "subscription plan."))
            if not self.subscription_start:
                self.subscription_start = today()
            if not self.next_billing_date:
                plan = frappe.get_doc("Subscription Plan", self.subscription_plan)
                if plan.billing_cycle == "Monthly":
                    self.next_billing_date = add_days(today(), 30)
                elif plan.billing_cycle == "Yearly":
                    self.next_billing_date = add_days(today(), 365)

    def _sync_subscription_status(self):
        if self.status == "Cancelled":
            return
        if self.trial_end_date and getdate(self.trial_end_date) < getdate(today()):
            if self.status == "Trial":
                self.db_set("status", "Suspended")

    def is_trial_expired(self):
        if not self.trial_end_date:
            return False
        return getdate(self.trial_end_date) < getdate(today())

    def get_usage(self):
        from rentpro.saas.plan_enforcement import get_agency_usage

        return get_agency_usage(self.name)

    def can_add_vehicle(self):
        from rentpro.saas.plan_enforcement import (
            check_vehicle_limit,
        )

        return check_vehicle_limit(self.name)

    def can_add_user(self):
        from rentpro.saas.plan_enforcement import (
            check_user_limit,
        )

        return check_user_limit(self.name)

    def suspend_for_non_payment(self):
        if self.status == "Active":
            self.status = "Suspended"
            self.add_comment("Info", "Agency suspended for non-payment.")
            self.save(ignore_permissions=True)
            frappe.db.commit()


def on_agency_update(doc, method):
    """Hook handler for Agency on_update."""
    pass
