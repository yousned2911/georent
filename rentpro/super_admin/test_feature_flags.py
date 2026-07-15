import frappe
from frappe.tests import TestCase


class TestFeatureFlagManagement(TestCase):
    def setUp(self):
        self.flag = frappe.get_doc(
            {
                "doctype": "Feature Flag",
                "flag_name": "test-mgmt-flag",
                "flag_label": "Test Mgmt Flag",
                "enabled": 0,
                "category": "Feature",
                "scope": "Global",
                "flag_type": "Boolean",
            }
        )
        self.flag.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.delete_doc("Feature Flag", self.flag.name, force=True)
        frappe.db.commit()

    def test_toggle_flag(self):
        from rentpro.super_admin.feature_flags import (
            toggle_flag,
        )

        result = toggle_flag("test-mgmt-flag", True)
        self.assertTrue(result["success"])
        self.assertTrue(result["enabled"])

    def test_toggle_flag_off(self):
        from rentpro.super_admin.feature_flags import (
            toggle_flag,
        )

        toggle_flag("test-mgmt-flag", True)
        result = toggle_flag("test-mgmt-flag", False)
        self.assertTrue(result["success"])
        self.assertFalse(result["enabled"])

    def test_get_flag_status(self):
        from rentpro.super_admin.feature_flags import (
            get_flag_status,
        )

        result = get_flag_status()
        self.assertIn("total_flags", result)
        self.assertIn("enabled_count", result)
        self.assertIn("flags", result)
        self.assertGreaterEqual(result["total_flags"], 1)
