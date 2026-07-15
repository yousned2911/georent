import frappe
from frappe.tests import IntegrationTestCase


class TestRentProSettings(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.settings = frappe.get_single("Rent Pro Settings")

    def test_settings_exists(self):
        self.assertTrue(frappe.db.exists("Rent Pro Settings", "settings"))

    def test_default_currency_is_mad(self):
        self.assertEqual(self.settings.default_currency, "MAD")

    def test_ocr_enabled_by_default(self):
        self.assertEqual(self.settings.ocr_enabled, 1)

    def test_ocr_confidence_threshold_default(self):
        self.assertEqual(self.settings.ocr_confidence_threshold, 80)

    def test_geofleete_disabled_by_default(self):
        self.assertEqual(self.settings.geofleete_enabled, 0)

    def test_gps_retention_days_default(self):
        self.assertEqual(self.settings.gps_retention_days, 90)

    def test_reservation_overlap_check_enabled(self):
        self.assertEqual(self.settings.reservation_overlap_check, 1)

    def test_auto_complete_contracts_disabled(self):
        self.assertEqual(self.settings.auto_complete_contracts, 0)

    def test_validate_ocr_threshold_valid(self):
        self.settings.ocr_confidence_threshold = 85
        self.settings.validate()
        self.assertEqual(self.settings.ocr_confidence_threshold, 85)

    def test_validate_ocr_threshold_too_low(self):
        self.settings.ocr_enabled = 1
        self.settings.ocr_confidence_threshold = -1
        self.assertRaises(frappe.ValidationError, self.settings.validate)

    def test_validate_ocr_threshold_too_high(self):
        self.settings.ocr_enabled = 1
        self.settings.ocr_confidence_threshold = 101
        self.assertRaises(frappe.ValidationError, self.settings.validate)

    def test_validate_gps_retention(self):
        self.settings.geofleete_enabled = 1
        self.settings.gps_retention_days = 0
        self.assertRaises(frappe.ValidationError, self.settings.validate)

    def test_manager_can_read(self):
        email = "test_manager@rentpro.com"
        self._ensure_user(email, "Test Manager", "Rent Pro Manager")
        frappe.set_user(email)
        self.assertTrue(frappe.has_permission("Rent Pro Settings", "read", user=email))
        frappe.set_user("Administrator")

    def test_readonly_user_cannot_write(self):
        email = "test_readonly@rentpro.com"
        self._ensure_user(email, "Test Readonly", "Rent Pro Read Only")
        frappe.set_user(email)
        self.assertFalse(frappe.has_permission("Rent Pro Settings", "write", user=email))
        frappe.set_user("Administrator")

    def _ensure_user(self, email, first_name, role):
        if not frappe.db.exists("User", email):
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": email,
                    "first_name": first_name,
                    "roles": [{"role": role}],
                }
            )
            user.insert(ignore_permissions=True)
