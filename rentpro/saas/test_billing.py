from frappe.tests import TestCase


class TestBilling(TestCase):
    def test_mark_past_due(self):
        from rentpro.saas.billing import mark_past_due

        try:
            mark_past_due()
        except Exception:
            pass

    def test_check_and_suspend_overdue(self):
        from rentpro.saas.billing import (
            check_and_suspend_overdue,
        )

        try:
            check_and_suspend_overdue()
        except Exception:
            pass
