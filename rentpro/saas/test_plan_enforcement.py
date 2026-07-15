import frappe
from frappe.tests import TestCase


class TestPlanEnforcement(TestCase):
    def setUp(self):
        self.settings = frappe.get_single("SaaS Settings")
        self.settings.saas_enabled = 1
        self.settings.enforce_limits = 1
        self.settings.save(ignore_permissions=True)

        self.plan = frappe.get_doc(
            {
                "doctype": "Subscription Plan",
                "plan_label": "Enforcement Test Plan",
                "plan_type": "Starter",
                "plan_code": "ETP-001",
                "price_mad": 500,
                "billing_cycle": "Monthly",
                "max_vehicles": 2,
                "max_users": 1,
                "max_storage_mb": 100,
                "max_ocr_per_month": 5,
                "max_api_calls_per_month": 100,
                "is_active": 1,
            }
        )
        self.plan.insert(ignore_permissions=True)

        self.agency = frappe.get_doc(
            {
                "doctype": "Agency",
                "agency_name": "Enforcement Agency",
                "agency_code": "EF-001",
                "status": "Active",
                "subscription_plan": self.plan.name,
            }
        )
        self.agency.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.delete_doc("Agency", self.agency.name, force=True)
        frappe.delete_doc("Subscription Plan", self.plan.name, force=True)
        frappe.db.commit()

    def test_get_usage(self):
        from rentpro.saas.plan_enforcement import (
            get_agency_usage,
        )

        usage = get_agency_usage(self.agency.name)
        self.assertIn("vehicles", usage)
        self.assertIn("users", usage)
        self.assertIn("ocr_scans", usage)

    def test_vehicle_limit_check(self):
        from rentpro.saas.plan_enforcement import (
            check_vehicle_limit,
        )

        result = check_vehicle_limit(self.agency.name)
        self.assertTrue(result)

    def test_user_limit_check(self):
        from rentpro.saas.plan_enforcement import (
            check_user_limit,
        )

        result = check_user_limit(self.agency.name)
        self.assertTrue(result)

    def test_ocr_limit_check(self):
        from rentpro.saas.plan_enforcement import (
            check_ocr_limit,
        )

        result = check_ocr_limit(self.agency.name)
        self.assertTrue(result)

    def test_api_limit_check(self):
        from rentpro.saas.plan_enforcement import (
            check_api_limit,
        )

        result = check_api_limit(self.agency.name)
        self.assertTrue(result)

    def test_enforce_all_limits(self):
        from rentpro.saas.plan_enforcement import (
            enforce_all_limits,
        )

        results = enforce_all_limits(self.agency.name)
        self.assertTrue(all(results.values()))
