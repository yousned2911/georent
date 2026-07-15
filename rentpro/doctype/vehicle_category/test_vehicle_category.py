import frappe
from frappe.tests import IntegrationTestCase


class TestVehicleCategory(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()

    def tearDown(self):
        frappe.db.rollback()

    def test_create_category(self):
        self.assertTrue(self.category.name)
        self.assertEqual(self.category.category_name, "Test Economy")

    def test_default_multiplier(self):
        self.assertEqual(self.category.daily_rate_multiplier, 1.0)

    def test_negative_multiplier_validation(self):
        self.category.daily_rate_multiplier = -1
        self.assertRaises(frappe.ValidationError, self.category.validate)

    def test_unique_category_name(self):
        duplicate = self._create_category()
        self.assertRaises(frappe.ValidationError, duplicate.insert)

    def test_is_active_by_default(self):
        self.assertEqual(self.category.is_active, 1)

    def _create_category(self):
        return frappe.get_doc(
            {
                "doctype": "Vehicle Category",
                "category_name": "Test Economy",
                "daily_rate_multiplier": 1.0,
                "security_deposit": 2000,
                "description": "Economy vehicles for daily rentals",
            }
        ).insert(ignore_permissions=True)
