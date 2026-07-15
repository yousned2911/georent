import frappe
from frappe.tests import TestCase


class TestSuperAdminSettings(TestCase):
    def test_get_settings(self):
        settings = frappe.get_single("Super Admin Settings")
        self.assertIsNotNone(settings)

    def test_default_values(self):
        settings = frappe.get_single("Super Admin Settings")
        self.assertEqual(settings.max_trial_extension_days or 30, 30)
        self.assertEqual(settings.allow_impersonation or 1, 1)
