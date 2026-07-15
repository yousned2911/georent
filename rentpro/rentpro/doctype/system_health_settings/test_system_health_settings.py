import frappe
from frappe.tests import TestCase


class TestSystemHealthSettings(TestCase):
    def test_get_settings(self):
        settings = frappe.get_single("System Health Settings")
        self.assertIsNotNone(settings)

    def test_default_thresholds(self):
        settings = frappe.get_single("System Health Settings")
        self.assertEqual(settings.cpu_threshold_percent or 80, 80)
        self.assertEqual(settings.memory_threshold_percent or 85, 85)
        self.assertEqual(settings.disk_threshold_percent or 90, 90)
