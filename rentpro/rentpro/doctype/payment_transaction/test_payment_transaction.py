import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate


class TestPaymentTransaction(IntegrationTestCase):
    def setUp(self):
        self.vehicle = self._create_vehicle()
        self.customer = self._create_customer()
        self.contract = self._create_contract()
        self.transaction = self._create_transaction()

    def tearDown(self):
        frappe.db.rollback()

    def _create_vehicle(self, status="Available"):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": f"FIN-{uid}",
                "make": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "status": status,
                "daily_rate": 500,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_customer(self, name=None):
        cname = name or "_Finance Test Customer"
        if frappe.db.exists("Customer", cname):
            return frappe.get_doc("Customer", cname)
        cg = frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups"
        terr = frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
        doc = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": cname,
                "customer_group": cg,
                "territory": terr,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_contract(self):
        pickup = add_days(nowdate(), 1)
        ret = add_days(nowdate(), 4)
        doc = frappe.get_doc(
            {
                "doctype": "Rental Contract",
                "customer": self.customer.name,
                "vehicle": self.vehicle.name,
                "contract_date": nowdate(),
                "pickup_datetime": (f"{pickup} 09:00:00"),
                "expected_return_datetime": (f"{ret} 09:00:00"),
                "daily_rate": 500,
                "tva_rate": "20%",
                "deposit_amount": 500,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_transaction(self, **kwargs):
        data = {
            "doctype": "Payment Transaction",
            "contract": self.contract.name,
            "customer": self.customer.name,
            "amount": 1500,
            "payment_method": "Cash",
            "transaction_date": nowdate(),
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────── 1. Creation ────────

    def test_transaction_creation(self):
        self.assertTrue(self.transaction.name)
        self.assertEqual(self.transaction.status, "Pending")

    def test_autoname_format(self):
        self.assertTrue(self.transaction.transaction_number.startswith("PAY-"))

    def test_currency_defaults_to_mad(self):
        self.assertEqual(self.transaction.currency, "MAD")

    # ──────── 2. Amount validation ────────

    def test_zero_amount_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_transaction,
            amount=0,
        )

    def test_negative_amount_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_transaction,
            amount=-100,
        )

    # ──────── 3. Contract linkage ────────

    def test_invalid_contract_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_transaction,
            contract="NON-EXISTENT",
        )

    def test_customer_mismatch_throws(self):
        other = self._create_customer("_Finance Test Customer 2")
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_transaction,
            customer=other.name,
        )

    # ──────── 4. Status ────────

    def test_completed_updates_contract(self):
        self.transaction.status = "Completed"
        self.transaction.save()
        frappe.db.commit()
        contract = frappe.get_doc("Rental Contract", self.contract.name)
        self.assertIn(
            contract.payment_status,
            ["Partial", "Paid"],
        )

    def test_refund_updates_contract(self):
        self.transaction.status = "Completed"
        self.transaction.save()
        frappe.db.commit()
        self.transaction.status = "Refunded"
        self.transaction.save()
        frappe.db.commit()
        contract = frappe.get_doc("Rental Contract", self.contract.name)
        self.assertEqual(contract.payment_status, "Unpaid")

    def test_cannot_edit_completed(self):
        self.transaction.status = "Completed"
        self.transaction.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._update_amount,
            self.transaction,
            999,
        )

    def _update_amount(self, txn, amount):
        txn.amount = amount
        txn.save()
        frappe.db.commit()

    # ──────── 5. Payment methods ────────

    def test_all_payment_methods(self):
        methods = [
            "Cash",
            "Credit Card",
            "Bank Transfer",
            "Mobile Payment",
            "Payzone",
            "Cash Plus",
            "Check",
        ]
        for method in methods:
            t = self._create_transaction(payment_method=method)
            self.assertEqual(t.payment_method, method)
