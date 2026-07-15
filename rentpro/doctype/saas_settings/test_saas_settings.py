import frappe
from frappe.tests import TestCase


class TestSaaSSettings(TestCase):
    def test_get_settings(self):
        settings = frappe.get_single("SaaS Settings")
        self.assertIsNotNone(settings)

    def test_settings_validation(self):
        settings = frappe.get_single("SaaS Settings")
        settings.grace_period_days = -1
        self.assertRaises(
            frappe.exceptions.ValidationError,
            settings.save,
        )
