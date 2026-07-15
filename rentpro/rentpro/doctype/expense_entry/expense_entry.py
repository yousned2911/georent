import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class ExpenseEntry(Document):
    def validate(self):
        self._validate_amount()
        self._validate_no_future_date()

    def before_insert(self):
        if not self.expense_date:
            self.expense_date = nowdate()

    # ──────────── validation ────────────

    def _validate_amount(self):
        if self.amount is not None and self.amount <= 0:
            frappe.throw(frappe._("Amount must be positive."))

    def _validate_no_future_date(self):
        if self.expense_date:
            exp = getdate(self.expense_date)
            today = getdate(nowdate())
            if exp > today:
                frappe.throw(frappe._("Expense date cannot be " "in the future."))


def on_expense_update(doc, method):
    """Hook handler for Expense Entry on_update."""
    pass
