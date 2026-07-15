import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, now_datetime, today


class AgencySubscription(Document):
    def validate(self):
        self._validate_dates()
        self._validate_plan_change()

    def before_insert(self):
        if not self.status:
            self.status = "Trial"
        if not self.amount_mad and self.plan:
            plan = frappe.get_doc("Subscription Plan", self.plan)
            self.amount_mad = plan.price_mad
            self.billing_cycle = plan.billing_cycle

    def on_update(self):
        self._sync_agency_plan()

    def activate(self):
        self.status = "Active"
        self.start_date = today()
        plan = frappe.get_doc("Subscription Plan", self.plan)
        if plan.billing_cycle == "Monthly":
            self.next_billing_date = add_days(today(), 30)
        elif plan.billing_cycle == "Yearly":
            self.next_billing_date = add_days(today(), 365)
        self.save(ignore_permissions=True)
        frappe.db.commit()

    def cancel(self, reason=None):
        self.status = "Cancelled"
        self.cancellation_reason = reason
        self.cancelled_on = now_datetime()
        self.save(ignore_permissions=True)
        frappe.db.commit()
        agency = frappe.get_doc("Agency", self.agency)
        agency.status = "Cancelled"
        agency.save(ignore_permissions=True)
        frappe.db.commit()

    def renew(self):
        if self.status != "Active":
            frappe.throw(frappe._("Only active subscriptions can be renewed."))
        plan = frappe.get_doc("Subscription Plan", self.plan)
        if plan.billing_cycle == "Monthly":
            self.next_billing_date = add_days(self.next_billing_date, 30)
        elif plan.billing_cycle == "Yearly":
            self.next_billing_date = add_days(self.next_billing_date, 365)
        self.last_billing_date = today()
        self.invoices_created = (self.invoices_created or 0) + 1
        self.save(ignore_permissions=True)
        frappe.db.commit()

    def _validate_dates(self):
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw(frappe._("Start date cannot be after end date."))

    def _validate_plan_change(self):
        if self._is_new():
            return
        old = self.get_doc_before_save()
        if not old:
            return
        if old.plan != self.plan:
            if self.status == "Active":
                frappe.msgprint(
                    frappe._("Plan changed. New limits will " "apply on next billing cycle."),
                    alert=True,
                )

    def _sync_agency_plan(self):
        agency = frappe.get_doc("Agency", self.agency)
        agency.subscription_plan = self.plan
        if self.status == "Active":
            agency.status = "Active"
        elif self.status == "Trial":
            agency.status = "Trial"
        agency.subscription_start = self.start_date
        agency.next_billing_date = self.next_billing_date
        agency.auto_renew = self.auto_renew
        agency.save(ignore_permissions=True)
        frappe.db.commit()
