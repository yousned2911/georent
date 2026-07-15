import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


class TestVehicle(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()
        self.vehicle = self._create_vehicle()

    def tearDown(self):
        frappe.db.rollback()

    def _create_category(self, name="Economy"):
        return frappe.get_doc(
            {
                "doctype": "Vehicle Category",
                "category_name": name,
                "daily_rate_multiplier": 1.0,
            }
        ).insert(ignore_permissions=True)

    def _create_vehicle(self, **kwargs):
        defaults = {
            "plate_number": "12345-A-12",
            "vin": "1HGBH41JXMN109186",
            "make": "Renault",
            "model": "Clio",
            "year": 2023,
            "color": "White",
            "category": self.category.name,
            "status": "Available",
            "current_mileage": 10000,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "seats": 5,
            "daily_rate": 250,
            "insurance_expiry": add_days(today(), 365),
            "technical_inspection_expiry": add_days(today(), 180),
            "registration_expiry": add_days(today(), 730),
        }
        defaults.update(kwargs)
        return frappe.get_doc({"doctype": "Vehicle", **defaults}).insert(ignore_permissions=True)

    def test_create_vehicle(self):
        self.assertTrue(self.vehicle.name.startswith("VEH-"))
        self.assertEqual(self.vehicle.status, "Available")
        self.assertEqual(self.vehicle.plate_number, "12345-A-12")

    def test_autoname_format(self):
        self.assertTrue(self.vehicle.name.startswith("VEH-"))
        self.assertEqual(len(self.vehicle.name), 8)

    def test_unique_plate_number(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="12345-A-12",
            vin="3HGBH41JXMN109188",
        )

    def test_unique_vin(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="33333-C-33",
            vin="1HGBH41JXMN109186",
        )

    def test_year_cannot_exceed_current_year(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="99999-Z-99",
            vin="9HGBH41JXMN109199",
            year=2099,
        )

    def test_year_before_1900(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="00000-X-00",
            vin="0HGBH41JXMN109180",
            year=1800,
        )

    def test_daily_rate_must_be_positive(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="11111-B-11",
            vin="1HGBH41JXMN109181",
            daily_rate=-100,
        )

    def test_mileage_cannot_be_negative(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="22222-C-22",
            vin="2HGBH41JXMN109182",
            current_mileage=-1,
        )

    def test_insurance_expiry_before_today(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="44444-E-44",
            vin="4HGBH41JXMN109184",
            insurance_expiry=add_days(today(), -1),
        )

    def test_inspection_expiry_before_today(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="55555-F-55",
            vin="5HGBH41JXMN109185",
            technical_inspection_expiry=add_days(today(), -1),
        )

    def test_registration_expiry_before_today(self):
        self.assertRaises(
            frappe.ValidationError,
            self._create_vehicle,
            plate_number="66666-G-66",
            vin="6HGBH41JXMN109186",
            registration_expiry=add_days(today(), -1),
        )

    def test_status_available_to_reserved(self):
        self.vehicle.status = "Reserved"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Reserved")

    def test_status_reserved_to_rented(self):
        self.vehicle.status = "Reserved"
        self.vehicle.save()
        self.vehicle.status = "Rented"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Rented")

    def test_status_rented_to_available(self):
        self.vehicle.status = "Reserved"
        self.vehicle.save()
        self.vehicle.status = "Rented"
        self.vehicle.save()
        self.vehicle.status = "Available"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Available")

    def test_status_available_to_maintenance(self):
        self.vehicle.status = "Maintenance"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Maintenance")

    def test_status_maintenance_to_available(self):
        self.vehicle.status = "Maintenance"
        self.vehicle.save()
        self.vehicle.status = "Available"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Available")

    def test_status_sold_is_terminal(self):
        self.vehicle.status = "Sold"
        self.vehicle.save()
        self.vehicle.status = "Available"
        self.assertRaises(frappe.ValidationError, self.vehicle.save)

    def test_status_sold_from_reserved(self):
        self.vehicle.status = "Reserved"
        self.vehicle.save()
        self.vehicle.status = "Sold"
        self.vehicle.save()
        self.assertEqual(self.vehicle.status, "Sold")

    def test_invalid_status_reserved_to_maintenance(self):
        self.vehicle.status = "Reserved"
        self.vehicle.save()
        self.vehicle.status = "Maintenance"
        self.assertRaises(frappe.ValidationError, self.vehicle.save)

    def test_invalid_status_maintenance_to_rented(self):
        self.vehicle.status = "Maintenance"
        self.vehicle.save()
        self.vehicle.status = "Rented"
        self.assertRaises(frappe.ValidationError, self.vehicle.save)

    def test_invalid_status_inactive_to_rented(self):
        self.vehicle.status = "Inactive"
        self.vehicle.save()
        self.vehicle.status = "Rented"
        self.assertRaises(frappe.ValidationError, self.vehicle.save)

    def test_set_reserved_method(self):
        self.vehicle.set_reserved()
        self.assertEqual(self.vehicle.status, "Reserved")

    def test_set_rented_method(self):
        self.vehicle.set_rented()
        self.assertEqual(self.vehicle.status, "Rented")

    def test_set_available_method(self):
        self.vehicle.status = "Rented"
        self.vehicle.save()
        self.vehicle.set_available()
        self.assertEqual(self.vehicle.status, "Available")

    def test_set_maintenance_method(self):
        self.vehicle.set_maintenance()
        self.assertEqual(self.vehicle.status, "Maintenance")

    def test_set_sold_method(self):
        self.vehicle.set_sold()
        self.assertEqual(self.vehicle.status, "Sold")
        self.assertEqual(self.vehicle.active, 0)

    def test_set_inactive_method(self):
        self.vehicle.set_inactive()
        self.assertEqual(self.vehicle.status, "Inactive")
        self.assertEqual(self.vehicle.active, 0)

    def test_active_default(self):
        self.assertEqual(self.vehicle.active, 1)

    def test_weekly_rate_optional(self):
        self.vehicle.weekly_rate = 1500
        self.vehicle.save()
        self.assertEqual(self.vehicle.weekly_rate, 1500)

    def test_monthly_rate_optional(self):
        self.vehicle.monthly_rate = 5000
        self.vehicle.save()
        self.assertEqual(self.vehicle.monthly_rate, 5000)

    def test_deposit_amount_optional(self):
        self.vehicle.deposit_amount = 3000
        self.vehicle.save()
        self.assertEqual(self.vehicle.deposit_amount, 3000)

    def test_category_link(self):
        self.assertEqual(self.vehicle.category, self.category.name)

    def test_notes_optional(self):
        self.vehicle.notes = "Test vehicle for QA"
        self.vehicle.save()
        self.assertEqual(self.vehicle.notes, "Test vehicle for QA")
