import frappe
from frappe.model.document import Document


class SuperAdminAuditLog(Document):
    pass


def create_audit_log(
    action_type,
    description,
    actor=None,
    agency=None,
    target_doctype=None,
    target_name=None,
    severity="Info",
    old_value=None,
    new_value=None,
    ip_address=None,
    metadata=None,
):
    log = frappe.get_doc(
        {
            "doctype": "Super Admin Audit Log",
            "action_type": action_type,
            "description": description,
            "actor": actor or frappe.session.user,
            "agency": agency,
            "target_doctype": target_doctype,
            "target_name": target_name,
            "severity": severity,
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip_address or frappe.local.request_ip if frappe.local else None,
            "metadata": frappe.as_json(metadata) if metadata else None,
        }
    )
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    return log
