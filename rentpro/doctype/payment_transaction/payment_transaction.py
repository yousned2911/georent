import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class PaymentTransaction(Document):
    def validate(self):
        self._validate_amount()
        self._validate_contract_exists()
        self._validate_customer_matches()
        self._validate_no_edit_after_completed()

    def before_insert(self):
        if not self.status:
            self.status = "Pending"
        if not self.transaction_date:
            self.transaction_date = nowdate()
        if not self.currency:
            self.currency = "MAD"

    def on_update(self):
        self._handle_status_change()

    # ──────────── validation ────────────

    def _validate_amount(self):
        if self.amount is not None and self.amount <= 0:
            frappe.throw(frappe._("Amount must be positive."))

    def _validate_contract_exists(self):
        if self.contract and not frappe.db.exists("Rental Contract", self.contract):
            frappe.throw(frappe._("Contract {0} does not exist.").format(self.contract))

    def _validate_customer_matches(self):
        if self.contract and self.customer:
            contract_customer = frappe.db.get_value(
                "Rental Contract",
                self.contract,
                "customer",
            )
            if contract_customer != self.customer:
                frappe.throw(frappe._("Customer does not match " "the contract customer."))

    def _validate_no_edit_after_completed(self):
        if self._is_new():
            return
        old_doc = self.get_doc_before_save()
        if not old_doc:
            return
        terminal = ("Completed", "Refunded")
        if old_doc.status in terminal:
            frappe.throw(frappe._("Transaction cannot be edited " "once {0}.").format(old_doc.status))

    # ──────── status handling ────────

    def _handle_status_change(self):
        if self._is_new():
            return
        if not self.has_value_changed("status"):
            return

        if self.status == "Completed":
            self._update_contract_payment_status()
            self._create_timeline_entry("Payment received.")
        elif self.status == "Refunded":
            self._update_contract_payment_status()
            self._create_timeline_entry("Payment refunded.")

    def _update_contract_payment_status(self):
        if not self.contract:
            return

        contract = frappe.get_doc("Rental Contract", self.contract)
        total_paid = frappe.db.sql(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM `tabPayment Transaction`
            WHERE contract = %s
              AND status = 'Completed'
            """,
            self.contract,
        )[0][0]

        if total_paid >= contract.grand_total:
            new_status = "Paid"
        elif total_paid > 0:
            new_status = "Partial"
        else:
            new_status = "Unpaid"

        if contract.payment_status != new_status:
            contract.payment_status = new_status
            contract.save(ignore_permissions=True)

    def _create_timeline_entry(self, message):
        if not self.contract:
            return
        contract = frappe.get_doc("Rental Contract", self.contract)
        contract.add_comment("Info", message)


def on_payment_update(doc, method):
    """Hook handler for Payment Transaction."""
    pass
