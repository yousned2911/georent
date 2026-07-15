"""Super Admin — Tenant Management for multi-tenant isolation."""

import frappe


def verify_tenant_isolation(agency_name=None):
    agencies = [agency_name] if agency_name else [a.name for a in frappe.get_all("Agency")]
    results = []
    for agency in agencies:
        violations = []
        orphans = _find_orphan_records(agency)
        if orphans:
            violations.extend(orphans)
        cross = _find_cross_tenant_references(agency)
        if cross:
            violations.extend(cross)

        results.append(
            {
                "agency": agency,
                "isolated": len(violations) == 0,
                "violations": violations,
            }
        )
    return results


def get_tenant_metrics(agency_name):
    vehicles = frappe.db.count("Vehicle", {"agency": agency_name})
    contracts = frappe.db.count("Rental Contract", {"agency": agency_name})
    users = frappe.db.count("User", {"agency_name": agency_name, "enabled": 1})
    documents = frappe.db.count("Document Record", {"agency": agency_name})
    gps_positions = frappe.db.count("GPS Position", {"agency": agency_name})
    geofence_alerts = frappe.db.count("Geofence Alert", {"agency": agency_name})
    ocr_completed = frappe.db.count(
        "Document Record",
        {"agency": agency_name, "ocr_status": "Completed"},
    )

    plan = frappe.db.get_value("Agency", agency_name, "subscription_plan")
    plan_doc = frappe.get_doc("Subscription Plan", plan) if plan else None
    limits = {}
    if plan_doc:
        limits = {
            "max_vehicles": plan_doc.max_vehicles,
            "max_users": plan_doc.max_users,
            "max_ocr_per_month": plan_doc.max_ocr_per_month,
        }

    return {
        "agency": agency_name,
        "vehicles": vehicles,
        "contracts": contracts,
        "users": users,
        "documents": documents,
        "gps_positions": gps_positions,
        "geofence_alerts": geofence_alerts,
        "ocr_completed": ocr_completed,
        "limits": limits,
    }


def get_tenant_quota_usage(agency_name):
    metrics = get_tenant_metrics(agency_name)
    limits = metrics.get("limits", {})

    usage = {}
    for key, limit in limits.items():
        metric_key = key.replace("max_", "")
        current = metrics.get(metric_key, 0)
        usage[key] = {
            "current": current,
            "limit": limit,
            "percent": round(current / limit * 100, 1) if limit else 0,
            "exceeded": limit > 0 and current >= limit,
        }
    return usage


def get_all_tenant_metrics():
    agencies = frappe.get_all("Agency", fields=["name", "status"])
    result = []
    for agency in agencies:
        metrics = get_tenant_metrics(agency.name)
        result.append({**metrics, "status": agency.status})
    return result


def generate_usage_report():
    agencies = frappe.get_all(
        "Agency",
        fields=["name", "agency_name", "status", "subscription_plan"],
    )
    report = []
    for agency in agencies:
        metrics = get_tenant_metrics(agency.name)
        quota = get_tenant_quota_usage(agency.name)
        report.append(
            {
                "agency": agency.name,
                "agency_name": agency.agency_name,
                "status": agency.status,
                "plan": agency.subscription_plan,
                "metrics": metrics,
                "quota_usage": quota,
            }
        )
    return report


def _find_orphan_records(agency_name):
    violations = []
    check_doctypes = [
        ("Vehicle", "agency"),
        ("Rental Contract", "agency"),
        ("Document Record", "agency"),
        ("GPS Position", "agency"),
        ("Geofence Alert", "agency"),
    ]
    for doctype, field in check_doctypes:
        if not frappe.db.exists("DocType", doctype):
            continue
        count = frappe.db.count(doctype, {field: agency_name})
        if count > 0:
            pass
    return violations


def _find_cross_tenant_references(agency_name):
    violations = []
    reservations = frappe.get_all(
        "Reservation",
        filters={"agency": agency_name},
        fields=["name", "customer"],
    )
    for res in reservations:
        if res.customer:
            cust_agency = frappe.db.get_value(
                "Customer Extension",
                {"customer": res.customer},
                "agency",
            )
            if cust_agency and cust_agency != agency_name:
                violations.append(
                    {
                        "type": "cross_tenant_reference",
                        "doctype": "Reservation",
                        "name": res.name,
                        "detail": (
                            f"Customer {res.customer} belongs to "
                            f"agency {cust_agency}, not "
                            f"{agency_name}"
                        ),
                    }
                )
    return violations
