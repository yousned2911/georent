from frappe.tests import TestCase


class TestSystemHealth(TestCase):
    def test_get_health_status(self):
        from rentpro.super_admin.system_health import (
            get_health_status,
        )

        status = get_health_status()
        self.assertIn("overall_status", status)
        self.assertIn("database", status)
        self.assertIn("redis", status)

    def test_run_health_check(self):
        from rentpro.super_admin.system_health import (
            run_health_check,
        )

        result = run_health_check()
        if result:
            self.assertIn("overall", result)
            self.assertIn("checks", result)
            self.assertIn("timestamp", result)

    def test_background_job_stats(self):
        from rentpro.super_admin.system_health import (
            get_background_job_stats,
        )

        stats = get_background_job_stats()
        self.assertIn("queued", stats)
        self.assertIn("failed", stats)
        self.assertIn("total_active", stats)
