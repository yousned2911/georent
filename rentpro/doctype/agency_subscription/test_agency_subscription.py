import frappe
from frappe.tests import TestCase
from frappe.utils import add_months, today


class TestAgencySubscription(TestCase):
    def setUp(self):
        self.plan = frappe.get_doc(
            {
                "doctype": "Subscription Plan",
                "plan_label": "Test Pro Sub",
                "plan_type": "Professional",
                "plan_code": "TPS-001",
                "price_mad": 1500,
                "billing_cycle": "Monthly",
                "max_vehicles": 20,
                "max_users": 5,
                "max_storage_mb": 2000,
                "max_ocr_per_month": 200,
                "max_api_calls_per_month": 5000,
                "is_active": 1,
            }
        )
        self.plan.insert(ignore_permissions=True)

        self.agency = frappe.get_doc(
            {
                "doctype": "Agency",
                "agency_name": "Test Sub Agency",
                "agency_code": "TSA-002",
                "status": "Active",
            }
        )
        self.agency.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.delete_doc(
            "Agency Subscription",
            frappe.get_all(
                "Agency Subscription",
                filters={"agency": self.agency.name},
                pluck="name",
            ),
            force=True,
        )
        frappe.delete_doc("Agency", self.agency.name, force=True)
        frappe.delete_doc("Subscription Plan", self.plan.name, force=True)
        frappe.db.commit()

    def _create_sub(self, **kwargs):
        defaults = {
            "doctype": "Agency Subscription",
            "agency": self.agency.name,
            "plan": self.plan.name,
            "status": "Active",
            "billing_cycle": "Monthly",
            "start_date": today(),
            "next_billing_date": add_months(today(), 1),
            "amount_mad": 1500,
            "auto_renew": 1,
        }
        defaults.update(kwargs)
        sub = frappe.get_doc(defaults)
        sub.insert(ignore_permissions=True)
        frappe.db.commit()
        return sub

    def test_subscription_creation(self):
        sub = self._create_sub()
        self.assertEqual(sub.status, "Active")
        self.assertEqual(sub.amount_mad, 1500)

    def test_subscription_suspend(self):
        sub = self._create_sub()
        sub.suspend()
        sub.reload()
        self.assertEqual(sub.status, "Suspended")

    def test_subscription_reactivate(self):
        sub = self._create_sub()
        sub.suspend()
        sub.reload()
        self.assertEqual(sub.status, "Suspended")
        sub.reactivate()
        sub.reload()
        self.assertEqual(sub.status, "Active")

    def test_subscription_cancel(self):
        sub = self._create_sub()
        sub.cancel_subscription()
        sub.reload()
        self.assertEqual(sub.status, "Cancelled")

    def test_subscription_renew(self):
        sub = self._create_sub()
        old_billing = sub.next_billing_date
        sub.renew()
        sub.reload()
        self.assertNotEqual(sub.next_billing_date, old_billing)
