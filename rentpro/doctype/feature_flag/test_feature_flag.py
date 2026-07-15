import frappe
from frappe.tests import TestCase


class TestFeatureFlag(TestCase):
    def setUp(self):
        self.flag = frappe.get_doc(
            {
                "doctype": "Feature Flag",
                "flag_name": "test-ocr-flag",
                "flag_label": "Test OCR Feature",
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

    def test_flag_creation(self):
        self.assertEqual(self.flag.flag_name, "test-ocr-flag")
        self.assertEqual(self.flag.enabled, 0)

    def test_flag_toggle(self):
        from rentpro.doctype.feature_flag.feature_flag import (
            is_enabled,
        )

        self.assertFalse(is_enabled("test-ocr-flag"))
        self.flag.enabled = 1
        self.flag.save(ignore_permissions=True)
        frappe.db.commit()
        self.assertTrue(is_enabled("test-ocr-flag"))

    def test_flag_metadata_update(self):
        self.flag.enabled = 1
        self.flag.save(ignore_permissions=True)
        self.flag.reload()
        self.assertEqual(self.flag.last_toggled_by, frappe.session.user)
        self.assertIsNotNone(self.flag.last_toggled_on)

    def test_flag_disabled_returns_false(self):
        from rentpro.doctype.feature_flag.feature_flag import (
            is_enabled,
        )

        self.assertFalse(is_enabled("test-ocr-flag"))

    def test_nonexistent_flag(self):
        from rentpro.doctype.feature_flag.feature_flag import (
            is_enabled,
        )

        self.assertFalse(is_enabled("nonexistent-flag-xyz"))

    def test_bulk_toggle(self):
        from rentpro.super_admin.feature_flags import (
            bulk_toggle,
        )

        result = bulk_toggle("Feature", True)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["toggled_count"], 1)
