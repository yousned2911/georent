import frappe
from frappe.tests import TestCase


class TestSubscriptionPlan(TestCase):
    def setUp(self):
        self.plan = frappe.get_doc(
            {
                "doctype": "Subscription Plan",
                "plan_label": "Test Starter Plan",
                "plan_type": "Starter",
                "plan_code": "TSP-001",
                "price_mad": 500,
                "billing_cycle": "Monthly",
                "max_vehicles": 5,
                "max_users": 2,
                "max_storage_mb": 500,
                "max_ocr_per_month": 50,
                "max_api_calls_per_month": 1000,
                "is_active": 1,
            }
        )
        self.plan.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.delete_doc("Subscription Plan", self.plan.name, force=True)
        frappe.db.commit()

    def test_plan_creation(self):
        self.assertEqual(self.plan.plan_label, "Test Starter Plan")
        self.assertEqual(self.plan.plan_type, "Starter")

    def test_plan_pricing(self):
        self.assertEqual(self.plan.price_mad, 500)
        self.assertEqual(self.plan.billing_cycle, "Monthly")

    def test_plan_limits(self):
        self.assertEqual(self.plan.max_vehicles, 5)
        self.assertEqual(self.plan.max_users, 2)
        self.assertEqual(self.plan.max_ocr_per_month, 50)

    def test_plan_features(self):
        self.assertEqual(self.plan.is_active, 1)

    def test_plan_validation_no_label(self):
        plan = frappe.get_doc(
            {
                "doctype": "Subscription Plan",
                "plan_type": "Starter",
                "price_mad": 500,
                "billing_cycle": "Monthly",
            }
        )
        self.assertRaises(
            frappe.exceptions.MandatoryError,
            plan.insert,
        )
