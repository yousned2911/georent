import frappe
from frappe.tests import TestCase


class TestSupportTools(TestCase):
    def test_export_diagnostics(self):
        from rentpro.super_admin.support_tools import (
            export_agency_diagnostics,
        )

        result = export_agency_diagnostics("AGC-0001")
        self.assertIn("agency", result)
        self.assertIn("vehicles", result)
        self.assertIn("contracts", result)

    def test_suspend_requires_reason(self):
        from rentpro.super_admin.support_tools import (
            suspend_agency,
        )

        settings = frappe.get_single("Super Admin Settings")
        settings.require_notes_for_suspend = 1
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            suspend_agency,
            "AGC-0001",
            None,
        )
