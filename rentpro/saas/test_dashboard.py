from frappe.tests import TestCase


class TestSaaSDashboard(TestCase):
    def test_platform_summary(self):
        from rentpro.saas.dashboard import get_platform_summary

        summary = get_platform_summary()
        self.assertIn("total_agencies", summary)
        self.assertIn("active_agencies", summary)
        self.assertIn("mrr", summary)
        self.assertIn("arr", summary)
        self.assertIn("plan_distribution", summary)

    def test_monthly_revenue_data(self):
        from rentpro.saas.dashboard import (
            get_monthly_revenue_data,
        )

        data = get_monthly_revenue_data()
        self.assertEqual(len(data), 12)
        self.assertIn("month", data[0])
        self.assertIn("revenue", data[0])
