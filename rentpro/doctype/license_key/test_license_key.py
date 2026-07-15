import frappe
from frappe.tests import TestCase
from frappe.utils import add_days, today


class TestLicenseKey(TestCase):
    def setUp(self):
        self.agency = frappe.get_doc(
            {
                "doctype": "Agency",
                "agency_name": "Test License Agency",
                "agency_code": "TLA-001",
                "status": "Active",
            }
        )
        self.agency.insert(ignore_permissions=True)

        self.plan = frappe.get_doc(
            {
                "doctype": "Subscription Plan",
                "plan_label": "Test License Plan",
                "plan_type": "Starter",
                "plan_code": "TLP-001",
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
        frappe.delete_doc(
            "License Key",
            frappe.get_all(
                "License Key",
                filters={"agency": self.agency.name},
                pluck="name",
            ),
            force=True,
        )
        frappe.delete_doc("Agency", self.agency.name, force=True)
        frappe.delete_doc("Subscription Plan", self.plan.name, force=True)
        frappe.db.commit()

    def _create_key(self, **kwargs):
        defaults = {
            "doctype": "License Key",
            "license_key": "TEST-LIC-001",
            "agency": self.agency.name,
            "status": "Active",
            "plan": self.plan.name,
            "issued_date": today(),
            "expiry_date": add_days(today(), 365),
            "max_agencies": 1,
            "activated_count": 0,
        }
        defaults.update(kwargs)
        key = frappe.get_doc(defaults)
        key.insert(ignore_permissions=True)
        frappe.db.commit()
        return key

    def test_key_creation(self):
        key = self._create_key()
        self.assertEqual(key.status, "Active")

    def test_key_activation(self):
        key = self._create_key()
        key.activate_for_agency()
        key.reload()
        self.assertEqual(key.activated_count, 1)

    def test_key_is_valid(self):
        key = self._create_key()
        self.assertTrue(key.is_valid())

    def test_key_revoke(self):
        key = self._create_key()
        key.revoke()
        key.reload()
        self.assertEqual(key.status, "Revoked")
        self.assertFalse(key.is_valid())

    def test_key_expired(self):
        key = self._create_key(
            expiry_date=add_days(today(), -1),
        )
        self.assertFalse(key.is_valid())
