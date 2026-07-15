from frappe.tests import TestCase


class TestTenantManagement(TestCase):
    def test_verify_isolation(self):
        from rentpro.super_admin.tenant_management import (
            verify_tenant_isolation,
        )

        result = verify_tenant_isolation("AGC-0001")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("agency", result[0])
        self.assertIn("isolated", result[0])

    def test_tenant_metrics(self):
        from rentpro.super_admin.tenant_management import (
            get_tenant_metrics,
        )

        result = get_tenant_metrics("AGC-0001")
        self.assertIn("vehicles", result)
        self.assertIn("contracts", result)
        self.assertIn("users", result)

    def test_tenant_quota_usage(self):
        from rentpro.super_admin.tenant_management import (
            get_tenant_quota_usage,
        )

        result = get_tenant_quota_usage("AGC-0001")
        self.assertIsInstance(result, dict)

    def test_all_tenant_metrics(self):
        from rentpro.super_admin.tenant_management import (
            get_all_tenant_metrics,
        )

        result = get_all_tenant_metrics()
        self.assertIsInstance(result, list)

    def test_usage_report(self):
        from rentpro.super_admin.tenant_management import (
            generate_usage_report,
        )

        report = generate_usage_report()
        self.assertIsInstance(report, list)
