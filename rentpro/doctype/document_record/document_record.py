import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

DOCUMENT_TYPES_CUSTOMER = [
    "National ID",
    "Passport",
    "Driver License",
    "Residence Permit",
]
DOCUMENT_TYPES_VEHICLE = [
    "Registration Card",
    "Insurance Certificate",
    "Technical Inspection",
    "Ownership Document",
]


class DocumentRecord(Document):
    def validate(self):
        self._validate_dates()
        self._validate_expiry()
        self._validate_status_transitions()
        self._validate_document_type_vehicle()
        self._auto_set_status()

    def before_insert(self):
        self.uploaded_by = frappe.session.user
        self.uploaded_at = now_datetime()
        if not self.status:
            self.status = "Active"
        self._add_audit_entry("Upload", "Document uploaded.")

    def on_update(self):
        if self.has_value_changed("status"):
            self._add_audit_entry(
                "Status Change",
                f"Status changed to {self.status}.",
            )
        if self.has_value_changed("extracted_text") and self.extracted_text:
            self._add_audit_entry(
                "OCR Execution",
                f"OCR completed. Confidence: {self.confidence_score or 0}%",
            )
        if self.has_value_changed("notes") and not self._is_new():
            self._add_audit_entry("Modification", "Notes updated.")

    # ──────────── validation ────────────

    def _validate_dates(self):
        if self.issue_date and self.expiry_date:
            if getdate(self.issue_date) > getdate(self.expiry_date):
                frappe.throw(frappe._("Issue date cannot be after expiry date."))

    def _validate_expiry(self):
        if self.expiry_date:
            if getdate(self.expiry_date) < getdate(nowdate()):
                if self.status == "Active":
                    frappe.msgprint(
                        frappe._("Warning: This document has expired."),
                        alert=True,
                    )

    def _validate_status_transitions(self):
        if self._is_new():
            return
        old_doc = self.get_doc_before_save()
        if not old_doc:
            return
        allowed = {
            "Active": ["Expired", "Archived"],
            "Expired": ["Archived"],
            "Archived": [],
        }
        old_status = old_doc.status
        new_status = self.status
        if old_status == new_status:
            return
        if new_status not in allowed.get(old_status, []):
            frappe.throw(frappe._("Cannot change status from {0} to {1}.").format(old_status, new_status))

    def _validate_document_type_vehicle(self):
        if self.document_type in DOCUMENT_TYPES_VEHICLE and not self.vehicle:
            frappe.msgprint(
                frappe._("Vehicle document type '{0}' should " "have a vehicle linked.").format(
                    self.document_type
                ),
                alert=True,
            )

    def _auto_set_status(self):
        if self.expiry_date and not self._is_new():
            old_doc = self.get_doc_before_save()
            if old_doc and old_doc.status == "Active":
                if getdate(self.expiry_date) < getdate(nowdate()):
                    self.status = "Expired"

    # ──────── audit ────────

    def _add_audit_entry(self, action, detail):
        self.append(
            "audit_log",
            {
                "action": action,
                "detail": detail,
                "performed_by": frappe.session.user,
                "performed_at": now_datetime(),
            },
        )

    # ──────── OCR ────────

    def run_ocr(self):
        from rentpro.ocr.service import extract_document

        if not self.attachment:
            frappe.throw(frappe._("No attachment to process."))

        self.ocr_status = "Processing"
        self.save(ignore_permissions=True)
        frappe.db.commit()

        try:
            result = extract_document(self.attachment)
            self.extracted_text = result.get("raw_text", "")
            self.confidence_score = result.get("confidence", 0)
            self.ocr_provider = result.get("provider", "Tesseract")
            self.extracted_name = result.get("full_name", "")
            self.extracted_document_number = result.get("document_number", "")
            self.extracted_expiry_date = result.get("expiry_date", "")
            self.extracted_date_of_birth = result.get("date_of_birth", "")
            self.extracted_license_number = result.get("license_number", "")
            self.extracted_country = result.get("country", "")
            self.ocr_status = "Completed"
            self.ocr_error = ""
        except Exception as e:
            self.ocr_status = "Failed"
            self.ocr_error = str(e)
            frappe.log_error(
                title="Rent Pro OCR Error",
                message=f"Document {self.name}: {e}",
            )

        self.save(ignore_permissions=True)
        frappe.db.commit()

    def correct_ocr_field(self, fieldname, value):
        valid_fields = [
            "extracted_name",
            "extracted_document_number",
            "extracted_expiry_date",
            "extracted_date_of_birth",
            "extracted_license_number",
            "extracted_country",
        ]
        if fieldname not in valid_fields:
            frappe.throw(frappe._("Invalid field for correction."))
        old_value = self.get(fieldname)
        self.set(fieldname, value)
        self.ocr_status = "Manual Review"
        self._add_audit_entry(
            "Manual Correction",
            f"Field '{fieldname}' corrected from " f"'{old_value}' to '{value}'.",
        )
        self.save(ignore_permissions=True)
        frappe.db.commit()

    def archive_document(self):
        if self.status != "Active":
            frappe.throw(frappe._("Only Active documents can be archived."))
        self.status = "Archived"
        self._add_audit_entry("Archive", "Document archived.")
        self.save(ignore_permissions=True)
        frappe.db.commit()


def on_document_record_update(doc, method):
    """Hook handler for Document Record on_update."""
    pass
