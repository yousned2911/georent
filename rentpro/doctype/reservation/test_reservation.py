import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


class TestReservation(IntegrationTestCase):
    def setUp(self):
        self.vehicle = self._create_vehicle()
        self.customer = self._create_customer()
        self.reservation = self._create_reservation()

    def tearDown(self):
        frappe.db.rollback()

    # ────────────────────── helpers ──────────────────────

    def _create_vehicle(self, status="Available", name=None):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": name or f"RES-TST-{uid}",
                "make": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "status": status,
                "daily_rate": 500,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_customer(self):
        cname = "_Reservation Test Customer"
        if frappe.db.exists("Customer", cname):
            return frappe.get_doc("Customer", cname)
        cg = frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups"
        terr = frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
        doc = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": cname,
                "customer_group": cg,
                "territory": terr,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_reservation(self, **kwargs):
        data = {
            "doctype": "Reservation",
            "customer": self.customer.name,
            "vehicle": self.vehicle.name,
            "pickup_date": today(),
            "expected_return_date": add_days(today(), 3),
            "daily_rate": 500,
            "discount": 0,
            "deposit_amount": 0,
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────────── 1. Reservation creation ────────────

    def test_reservation_creation(self):
        self.assertTrue(self.reservation.name)
        self.assertEqual(self.reservation.status, "Draft")

    def test_autoname_format(self):
        self.assertTrue(self.reservation.reservation_number.startswith("RES-"))

    def test_created_by_populated(self):
        self.assertEqual(self.reservation.created_by, frappe.session.user)

    def test_reservation_date_set(self):
        self.assertEqual(self.reservation.reservation_date, today())

    # ──────────── 2. Date validation ────────────

    def test_pickup_before_today_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            pickup_date=add_days(today(), -1),
            expected_return_date=add_days(today(), 2),
        )

    def test_return_before_pickup_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            pickup_date=add_days(today(), 2),
            expected_return_date=add_days(today(), 1),
        )

    def test_return_same_as_pickup_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            pickup_date=add_days(today(), 1),
            expected_return_date=add_days(today(), 1),
        )

    # ──────────── 3. Overlap detection ────────────

    def test_overlap_rejected(self):
        vehicle = self._create_vehicle(name="OVLP-001")
        self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 1),
            expected_return_date=add_days(today(), 5),
        )
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 3),
            expected_return_date=add_days(today(), 7),
        )

    def test_no_overlap_adjacent(self):
        vehicle = self._create_vehicle(name="ADJ-001")
        self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 1),
            expected_return_date=add_days(today(), 4),
        )
        r2 = self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 4),
            expected_return_date=add_days(today(), 7),
        )
        self.assertTrue(r2.name)

    def test_overlap_same_dates_rejected(self):
        vehicle = self._create_vehicle(name="OVLP-002")
        self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 2),
            expected_return_date=add_days(today(), 6),
        )
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 2),
            expected_return_date=add_days(today(), 6),
        )

    def test_overlap_cancelled_not_counted(self):
        vehicle = self._create_vehicle(name="CNCL-001")
        r = self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 1),
            expected_return_date=add_days(today(), 5),
        )
        r.status = "Cancelled"
        r.save()
        frappe.db.commit()
        r2 = self._create_reservation(
            vehicle=vehicle.name,
            pickup_date=add_days(today(), 2),
            expected_return_date=add_days(today(), 4),
        )
        self.assertTrue(r2.name)

    # ──────────── 4. Status transitions ────────────

    def test_valid_transitions(self):
        transitions = [
            ("Draft", "Confirmed"),
            ("Confirmed", "Picked Up"),
            ("Picked Up", "Completed"),
            ("Draft", "Cancelled"),
            ("Confirmed", "Cancelled"),
            ("Confirmed", "No Show"),
        ]
        for old, new in transitions:
            r = self._create_reservation()
            if old != "Draft":
                r.status = old
                r.save()
                frappe.db.commit()
            r.status = new
            r.save()
            frappe.db.commit()

    def test_invalid_transition_throws(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._set_status,
            self.reservation,
            "Draft",
        )

    def test_completed_is_terminal(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Picked Up"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Completed"
        self.reservation.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._set_status,
            self.reservation,
            "Draft",
        )

    def _set_status(self, reservation, status):
        reservation.status = status
        reservation.save()
        frappe.db.commit()

    # ──────────── 5. Financial calculations ────────────

    def test_estimated_total_calculation(self):
        self.reservation.daily_rate = 500
        self.reservation.expected_return_date = add_days(today(), 5)
        self.reservation.save()
        frappe.db.commit()
        self.reservation.reload()
        days = self.reservation.number_of_days
        expected = 500 * days
        self.assertEqual(self.reservation.estimated_total, expected)

    def test_discount_applied(self):
        self.reservation.daily_rate = 1000
        self.reservation.expected_return_date = add_days(today(), 5)
        self.reservation.discount = 500
        self.reservation.save()
        frappe.db.commit()
        self.reservation.reload()
        expected = 1000 * self.reservation.number_of_days - 500
        self.assertEqual(self.reservation.estimated_total, expected)

    def test_deposit_exceeds_total_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            daily_rate=100,
            expected_return_date=add_days(today(), 2),
            deposit_amount=9999,
        )

    # ──────────── 6. Vehicle status updates ────────────

    def test_confirmed_sets_reserved(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Reserved")

    def test_picked_up_sets_rented(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Picked Up"
        self.reservation.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Rented")

    def test_completed_sets_available(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Picked Up"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Completed"
        self.reservation.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Available")

    def test_cancelled_sets_available(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Cancelled"
        self.reservation.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Available")

    # ──────────── 7. No-edit after terminal ────────────

    def test_cannot_edit_completed(self):
        self.reservation.status = "Confirmed"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Picked Up"
        self.reservation.save()
        frappe.db.commit()
        self.reservation.status = "Completed"
        self.reservation.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._update_notes,
            self.reservation,
            "Should fail",
        )

    def _update_notes(self, reservation, notes):
        reservation.notes = notes
        reservation.save()
        frappe.db.commit()

    # ──────────── 8. Entity validation ────────────

    def test_invalid_vehicle_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            vehicle="NON-EXISTENT-VEHICLE",
        )

    def test_invalid_customer_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_reservation,
            customer="NON-EXISTENT-CUSTOMER",
        )
