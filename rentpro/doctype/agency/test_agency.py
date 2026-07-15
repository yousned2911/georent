import frappe
from frappe.tests import TestCase
from frappe.utils import add_days, today


class TestAgency(TestCase):
    def setUp(self):
        self.agency = frappe.get_doc(
            {
                "doctype": "Agency",
                "agency_name": "Test SaaS Agency",
                "agency_code": "TSA-001",
                "status": "Active",
            }
        )
        self.agency.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.delete_doc("Agency", self.agency.name, force=True)
        frappe.db.commit()

    def test_agency_creation(self):
        self.assertEqual(self.agency.status, "Active")
        self.assertEqual(self.agency.agency_name, "Test SaaS Agency")

    def test_agency_trial_activation(self):
        self.agency.status = "Trial"
        self.agency.trial_start_date = today()
        self.agency.trial_end_date = add_days(today(), 14)
        self.agency.save(ignore_permissions=True)
        self.agency.reload()
        self.assertEqual(self.agency.status, "Trial")

    def test_agency_suspend(self):
        self.agency.suspend_for_non_payment()
        self.agency.reload()
        self.assertEqual(self.agency.status, "Suspended")

    def test_agency_reactivate(self):
        self.agency.suspend_for_non_payment()
        self.agency.reload()
        self.assertEqual(self.agency.status, "Suspended")
        self.agency.reactivate()
        self.agency.reload()
        self.assertEqual(self.agency.status, "Active")

    def test_agency_trial_expired(self):
        self.agency.status = "Trial"
        self.agency.trial_end_date = add_days(today(), -1)
        self.agency.save(ignore_permissions=True)
        result = self.agency.is_trial_expired()
        self.assertTrue(result)
