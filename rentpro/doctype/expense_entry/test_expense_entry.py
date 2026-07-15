import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate


class TestExpenseEntry(IntegrationTestCase):
    def setUp(self):
        self.vehicle = self._create_vehicle()
        self.expense = self._create_expense()

    def tearDown(self):
        frappe.db.rollback()

    def _create_vehicle(self):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": f"EXP-{uid}",
                "make": "Renault",
                "model": "Clio",
                "year": 2022,
                "status": "Available",
                "daily_rate": 400,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_expense(self, **kwargs):
        data = {
            "doctype": "Expense Entry",
            "category": "Fuel",
            "amount": 350,
            "vehicle": self.vehicle.name,
            "expense_date": nowdate(),
            "supplier": "Total Energy",
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────── 1. Creation ────────

    def test_expense_creation(self):
        self.assertTrue(self.expense.name)
        self.assertEqual(self.expense.category, "Fuel")

    def test_autoname_format(self):
        self.assertTrue(self.expense.expense_number.startswith("EXP-"))

    def test_amount_stored(self):
        self.assertEqual(self.expense.amount, 350)

    # ──────── 2. Validation ────────

    def test_zero_amount_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_expense,
            amount=0,
        )

    def test_negative_amount_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_expense,
            amount=-50,
        )

    def test_future_date_throws(self):
        future = add_days(nowdate(), 5)
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_expense,
            expense_date=future,
        )

    # ──────── 3. Categories ────────

    def test_all_categories(self):
        categories = [
            "Fuel",
            "Maintenance",
            "Insurance",
            "Technical Inspection",
            "Registration",
            "Cleaning",
            "Repairs",
            "Taxes",
            "Miscellaneous",
        ]
        for cat in categories:
            e = self._create_expense(category=cat)
            self.assertEqual(e.category, cat)

    # ──────── 4. Vehicle optional ────────

    def test_no_vehicle(self):
        e = self._create_expense(vehicle=None)
        self.assertTrue(e.name)

    # ──────── 5. Supplier ────────

    def test_supplier_stored(self):
        self.assertEqual(self.expense.supplier, "Total Energy")
