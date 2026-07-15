import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_to_date, nowdate


class TestRentalContract(IntegrationTestCase):
    def setUp(self):
        self.vehicle = self._create_vehicle()
        self.customer = self._create_customer()
        self.contract = self._create_contract()

    def tearDown(self):
        frappe.db.rollback()

    # ────────────────────── helpers ──────────────────────

    def _create_vehicle(self, status="Available", name=None):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": name or f"RCT-{uid}",
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
        cname = "_Contract Test Customer"
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

    def _create_contract(self, **kwargs):
        pickup = add_to_date(nowdate(), days=1)
        ret = add_to_date(nowdate(), days=4)
        data = {
            "doctype": "Rental Contract",
            "customer": self.customer.name,
            "vehicle": self.vehicle.name,
            "contract_date": nowdate(),
            "pickup_datetime": f"{pickup} 09:00:00",
            "expected_return_datetime": (f"{ret} 09:00:00"),
            "daily_rate": 500,
            "tva_rate": "20%",
            "deposit_amount": 500,
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ───────── 1. Creation ─────────

    def test_contract_creation(self):
        self.assertTrue(self.contract.name)
        self.assertEqual(self.contract.status, "Draft")

    def test_autoname_format(self):
        self.assertTrue(self.contract.contract_number.startswith("CON-"))

    def test_created_by_populated(self):
        self.assertEqual(self.contract.created_by, frappe.session.user)

    def test_contract_date_set(self):
        self.assertEqual(self.contract.contract_date, nowdate())

    def test_payment_status_defaults(self):
        self.assertEqual(self.contract.payment_status, "Unpaid")

    # ───────── 2. TVA calculations ─────────

    def test_tva_20_percent(self):
        c = self._create_contract(daily_rate=1000, tva_rate="20%")
        c.reload()
        self.assertEqual(c.tva_amount, 600)
        self.assertEqual(c.grand_total, 3600)

    def test_tva_14_percent(self):
        c = self._create_contract(daily_rate=1000, tva_rate="14%")
        c.reload()
        self.assertEqual(c.tva_amount, 420)
        self.assertEqual(c.grand_total, 3420)

    def test_tva_10_percent(self):
        c = self._create_contract(daily_rate=1000, tva_rate="10%")
        c.reload()
        self.assertEqual(c.tva_amount, 300)
        self.assertEqual(c.grand_total, 3300)

    def test_tva_7_percent(self):
        c = self._create_contract(daily_rate=1000, tva_rate="7%")
        c.reload()
        self.assertEqual(c.tva_amount, 210)
        self.assertEqual(c.grand_total, 3210)

    # ───────── 3. Financial calculations ─────────

    def test_subtotal_calculation(self):
        c = self._create_contract(daily_rate=800)
        c.reload()
        expected = 800 * c.number_of_days
        self.assertEqual(c.subtotal, expected)

    def test_discount_reduces_taxable(self):
        c = self._create_contract(
            daily_rate=1000,
            discount=500,
            tva_rate="20%",
        )
        c.reload()
        self.assertEqual(c.tva_amount, 500)
        self.assertEqual(c.grand_total, 3000)

    def test_additional_charges_increase(self):
        c = self._create_contract(
            daily_rate=1000,
            additional_charges=200,
            tva_rate="20%",
        )
        c.reload()
        self.assertEqual(c.tva_amount, 640)
        self.assertEqual(c.grand_total, 3840)

    def test_late_return_fee(self):
        c = self._create_contract(
            daily_rate=1000,
            late_return_fee=300,
            tva_rate="20%",
        )
        c.reload()
        self.assertEqual(c.tva_amount, 660)
        self.assertEqual(c.grand_total, 3960)

    def test_damage_fee(self):
        c = self._create_contract(
            daily_rate=1000,
            damage_fee=150,
            tva_rate="20%",
        )
        c.reload()
        self.assertEqual(c.tva_amount, 630)
        self.assertEqual(c.grand_total, 3630)

    def test_grand_total_includes_all(self):
        c = self._create_contract(
            daily_rate=1000,
            discount=200,
            additional_charges=100,
            damage_fee=50,
            tva_rate="20%",
        )
        c.reload()
        self.assertEqual(c.tva_amount, 590)
        self.assertEqual(c.grand_total, 3540)

    def test_number_of_days(self):
        pickup = add_to_date(nowdate(), days=1)
        ret = add_to_date(nowdate(), days=11)
        c = self._create_contract(
            pickup_datetime=f"{pickup} 09:00:00",
            expected_return_datetime=(f"{ret} 09:00:00"),
        )
        c.reload()
        self.assertEqual(c.number_of_days, 10)

    # ───────── 4. Status transitions ─────────

    def test_valid_transitions(self):
        transitions = [
            ("Draft", "Active"),
            ("Active", "Completed"),
            ("Draft", "Cancelled"),
            ("Active", "Cancelled"),
        ]
        for old, new in transitions:
            c = self._create_contract()
            if old != "Draft":
                c.status = old
                c.save()
                frappe.db.commit()
            c.status = new
            c.save()
            frappe.db.commit()

    def test_invalid_transition_throws(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._set_status,
            self.contract,
            "Draft",
        )

    def test_completed_is_terminal(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.status = "Completed"
        self.contract.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._set_status,
            self.contract,
            "Draft",
        )

    def _set_status(self, contract, status):
        contract.status = status
        contract.save()
        frappe.db.commit()

    # ───────── 5. Vehicle status ─────────

    def test_vehicle_reserved_on_draft(self):
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Reserved")

    def test_vehicle_rented_on_active(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Rented")

    def test_vehicle_available_on_completed(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.status = "Completed"
        self.contract.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Available")

    def test_vehicle_available_on_cancelled(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.status = "Cancelled"
        self.contract.save()
        frappe.db.commit()
        v = frappe.get_doc("Vehicle", self.vehicle.name)
        self.assertEqual(v.status, "Available")

    # ───────── 6. Validations ─────────

    def test_invalid_vehicle_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_contract,
            vehicle="NON-EXISTENT",
        )

    def test_invalid_customer_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_contract,
            customer="NON-EXISTENT",
        )

    def test_return_mileage_less_throws(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.return_mileage = 100
        self.contract.pickup_mileage = 200
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self.contract.save,
        )

    def test_fuel_over_100_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_contract,
            pickup_fuel_level=150,
        )

    def test_fuel_negative_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_contract,
            pickup_fuel_level=-1,
        )

    # ───────── 7. Read-only ─────────

    def test_cannot_edit_completed(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.status = "Completed"
        self.contract.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._update_notes,
            self.contract,
            "fail",
        )

    def test_cannot_edit_cancelled(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        self.contract.status = "Cancelled"
        self.contract.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._update_notes,
            self.contract,
            "fail",
        )

    def _update_notes(self, contract, notes):
        contract.notes = notes
        contract.save()
        frappe.db.commit()

    # ───────── 8. Invoice ─────────

    def test_invoice_created_on_active(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"rental_contract": self.contract.name},
            fields=["name", "docstatus"],
        )
        self.assertTrue(len(invoices) > 0)
        self.assertEqual(invoices[0].docstatus, 1)

    def test_invoice_links_to_contract(self):
        self.contract.status = "Active"
        self.contract.save()
        frappe.db.commit()
        si = frappe.get_all(
            "Sales Invoice",
            filters={"rental_contract": self.contract.name},
            fields=["name"],
        )
        self.assertTrue(len(si) > 0)
        invoice = frappe.get_doc("Sales Invoice", si[0].name)
        self.assertEqual(
            invoice.rental_contract,
            self.contract.name,
        )

    # ───────── 9. Deposit ─────────

    def test_deposit_stored(self):
        self.assertEqual(self.contract.deposit_amount, 500)
