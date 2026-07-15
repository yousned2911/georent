import frappe
from frappe.tests import TestCase


class TestSuperAdminAuditLog(TestCase):
    def test_create_audit_log(self):
        from rentpro.doctype.super_admin_audit_log.super_admin_audit_log import (
            create_audit_log,
        )

        log = create_audit_log(
            action_type="Agency Creation",
            description="Test agency created",
            severity="Info",
        )
        self.assertIsNotNone(log.name)
        self.assertEqual(log.action_type, "Agency Creation")
        frappe.delete_doc("Super Admin Audit Log", log.name, force=True)
        frappe.db.commit()

    def test_audit_log_with_agency(self):
        from rentpro.doctype.super_admin_audit_log.super_admin_audit_log import (
            create_audit_log,
        )

        log = create_audit_log(
            action_type="Support Action",
            description="Test support action",
            agency="AGC-9999",
            severity="Warning",
        )
        self.assertEqual(log.agency, "AGC-9999")
        frappe.delete_doc("Super Admin Audit Log", log.name, force=True)
        frappe.db.commit()

    def test_audit_log_severity(self):
        from rentpro.doctype.super_admin_audit_log.super_admin_audit_log import (
            create_audit_log,
        )

        log = create_audit_log(
            action_type="Failed Payment",
            description="Payment failed for test",
            severity="Critical",
        )
        self.assertEqual(log.severity, "Critical")
        frappe.delete_doc("Super Admin Audit Log", log.name, force=True)
        frappe.db.commit()
