from frappe.tests import TestCase


class TestSuperAdminDashboard(TestCase):
    def test_platform_summary(self):
        from rentpro.super_admin.dashboard import (
            get_platform_summary,
        )

        summary = get_platform_summary()
        self.assertIn("total_agencies", summary)
        self.assertIn("active_agencies", summary)
        self.assertIn("mrr", summary)
        self.assertIn("arr", summary)
        self.assertIn("total_vehicles", summary)
        self.assertIn("total_contracts", summary)
        self.assertIn("timestamp", summary)

    def test_agency_list_data(self):
        from rentpro.super_admin.dashboard import (
            get_agency_list_data,
        )

        result = get_agency_list_data()
        self.assertIn("agencies", result)
        self.assertIn("total", result)
        self.assertIsInstance(result["agencies"], list)

    def test_subscription_monitoring(self):
        from rentpro.super_admin.dashboard import (
            get_subscription_monitoring,
        )

        result = get_subscription_monitoring()
        self.assertIn("active_count", result)
        self.assertIn("mrr", result)
        self.assertIn("arr", result)

    def test_revenue_dashboard(self):
        from rentpro.super_admin.dashboard import (
            get_revenue_dashboard,
        )

        result = get_revenue_dashboard()
        self.assertIn("monthly_revenue", result)
        self.assertIn("total_revenue", result)
        self.assertEqual(len(result["monthly_revenue"]), 12)
