import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate


class TestDocumentRecord(IntegrationTestCase):
    def setUp(self):
        self.customer = self._create_customer()
        self.vehicle = self._create_vehicle()
        self.contract = self._create_contract()
        self.doc_record = self._create_document()

    def tearDown(self):
        frappe.db.rollback()

    def _create_customer(self, name=None):
        cname = name or "_DMS Test Customer"
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

    def _create_vehicle(self):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": f"DMS-{uid}",
                "make": "Renault",
                "model": "Clio",
                "year": 2022,
                "status": "Available",
                "daily_rate": 400,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_contract(self):
        pickup = add_days(nowdate(), 1)
        ret = add_days(nowdate(), 4)
        doc = frappe.get_doc(
            {
                "doctype": "Rental Contract",
                "customer": self.customer.name,
                "vehicle": self.vehicle.name,
                "contract_date": nowdate(),
                "pickup_datetime": f"{pickup} 09:00:00",
                "expected_return_datetime": (f"{ret} 09:00:00"),
                "daily_rate": 400,
                "tva_rate": "20%",
                "deposit_amount": 400,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_document(self, **kwargs):
        data = {
            "doctype": "Document Record",
            "document_number": f"CIN-{frappe.utils.now_datetime().microsecond % 100000}",
            "customer": self.customer.name,
            "document_type": "National ID",
            "document_name": "CIN Test Document",
            "attachment": "/files/test_doc.pdf",
            "expiry_date": add_days(nowdate(), 365),
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────── 1. Creation ────────

    def test_document_creation(self):
        self.assertTrue(self.doc_record.name)
        self.assertEqual(self.doc_record.status, "Active")

    def test_autoname_format(self):
        self.assertTrue(self.doc_record.document_number.startswith("DOC-"))

    def test_uploaded_by_set(self):
        self.assertEqual(self.doc_record.uploaded_by, frappe.session.user)

    def test_uploaded_at_set(self):
        self.assertTrue(self.doc_record.uploaded_at)

    # ──────── 2. Validation ────────

    def test_issue_after_expiry_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_document,
            issue_date=add_days(nowdate(), 10),
            expiry_date=nowdate(),
        )

    def test_vehicle_document_type_warns(self):
        doc = self._create_document(
            document_type="Registration Card",
            vehicle=None,
        )
        self.assertTrue(doc.name)

    # ──────── 3. Status transitions ────────

    def test_active_to_archived(self):
        self.doc_record.status = "Archived"
        self.doc_record.save()
        frappe.db.commit()
        self.assertEqual(self.doc_record.status, "Archived")

    def test_archived_cannot_go_back(self):
        self.doc_record.status = "Archived"
        self.doc_record.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._set_status,
            self.doc_record,
            "Active",
        )

    def test_expired_to_archived(self):
        self.doc_record.status = "Expired"
        self.doc_record.save()
        frappe.db.commit()
        self.doc_record.status = "Archived"
        self.doc_record.save()
        frappe.db.commit()
        self.assertEqual(self.doc_record.status, "Archived")

    def _set_status(self, doc, status):
        doc.status = status
        doc.save()
        frappe.db.commit()

    # ──────── 4. OCR ────────

    def test_ocr_status_default(self):
        self.assertEqual(self.doc_record.ocr_status, "Pending")

    def test_ocr_correction(self):
        self.doc_record.correct_ocr_field("extracted_name", "Ahmed Ben Ali")
        frappe.db.commit()
        self.assertEqual(self.doc_record.extracted_name, "Ahmed Ben Ali")
        self.assertEqual(self.doc_record.ocr_status, "Manual Review")

    def test_ocr_invalid_field_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self.doc_record.correct_ocr_field,
            "invalid_field",
            "value",
        )

    # ──────── 5. Audit trail ────────

    def test_audit_log_on_insert(self):
        self.assertTrue(self.doc_record.audit_log)
        self.assertEqual(self.doc_record.audit_log[0].action, "Upload")

    def test_audit_log_on_status_change(self):
        old_count = len(self.doc_record.audit_log)
        self.doc_record.status = "Archived"
        self.doc_record.save()
        frappe.db.commit()
        self.assertGreater(len(self.doc_record.audit_log), old_count)

    def test_audit_log_on_ocr_correction(self):
        old_count = len(self.doc_record.audit_log)
        self.doc_record.correct_ocr_field("extracted_name", "Test Name")
        frappe.db.commit()
        self.assertGreater(len(self.doc_record.audit_log), old_count)

    # ──────── 6. Document types ────────

    def test_all_customer_document_types(self):
        types = [
            "National ID",
            "Passport",
            "Driver License",
            "Residence Permit",
        ]
        for dtype in types:
            doc = self._create_document(
                document_type=dtype,
            )
            self.assertEqual(doc.document_type, dtype)

    def test_all_vehicle_document_types(self):
        types = [
            "Registration Card",
            "Insurance Certificate",
            "Technical Inspection",
            "Ownership Document",
        ]
        for dtype in types:
            doc = self._create_document(
                document_type=dtype,
                vehicle=self.vehicle.name,
            )
            self.assertEqual(doc.document_type, dtype)

    # ──────── 7. Archive ────────

    def test_archive_method_active(self):
        self.doc_record.archive_document()
        frappe.db.commit()
        self.assertEqual(self.doc_record.status, "Archived")

    def test_archive_method_non_active_throws(self):
        self.doc_record.status = "Expired"
        self.doc_record.save()
        frappe.db.commit()
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self.doc_record.archive_document,
        )
