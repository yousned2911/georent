import frappe
from frappe.utils import add_days, getdate, today


def daily_tasks():
    _check_document_expiries()
    _check_vehicle_expiry_warnings()


def hourly_tasks():
    _check_document_expirations()


def _check_document_expiries():
    frappe.enqueue(
        "rentpro.tasks._check_document_expiries_job",
        queue="short",
        timeout=300,
    )


def _check_document_expiries_job():
    settings = frappe.get_single("Rent Pro Settings")
    warning_days = getattr(settings, "expiry_warning_days", 30) or 30
    warning_date = add_days(getdate(today()), warning_days)

    vehicles = frappe.get_all(
        "Vehicle",
        filters={"status": ["!=", "Retired"]},
        fields=[
            "name",
            "vehicle_number",
            "insurance_expiry",
            "technical_inspection_expiry",
        ],
    )

    for vehicle in vehicles:
        for field in [
            "insurance_expiry",
            "technical_inspection_expiry",
        ]:
            expiry = vehicle.get(field)
            if expiry and getdate(expiry) <= warning_date:
                frappe.publish_realtime(
                    "rent_pro_expiry_warning",
                    {
                        "vehicle": vehicle.name,
                        "vehicle_number": (vehicle.vehicle_number),
                        "field": field,
                        "expiry_date": str(expiry),
                    },
                    user=frappe.session.user,
                )


def _check_vehicle_expiry_warnings():
    warning_thresholds = [30, 15, 7, 1]

    vehicles = frappe.get_all(
        "Vehicle",
        filters={"status": ["!=", "Retired"]},
        fields=[
            "name",
            "vehicle_number",
            "insurance_expiry",
            "technical_inspection_expiry",
        ],
    )

    today_date = getdate(today())
    for vehicle in vehicles:
        for field in [
            "insurance_expiry",
            "technical_inspection_expiry",
        ]:
            expiry = vehicle.get(field)
            if not expiry:
                continue
            expiry_date = getdate(expiry)
            if expiry_date < today_date:
                continue
            days_until = (expiry_date - today_date).days
            if days_until in warning_thresholds:
                _create_expiry_notification(
                    vehicle.name,
                    vehicle.vehicle_number or vehicle.name,
                    field,
                    days_until,
                )


def _check_document_expirations():
    warning_thresholds = [30, 15, 7, 1]
    today_date = getdate(today())

    documents = frappe.get_all(
        "Document Record",
        filters={"status": "Active", "expiry_date": [">=", today_date]},
        fields=[
            "name",
            "document_number",
            "document_type",
            "customer",
            "expiry_date",
        ],
    )

    for doc in documents:
        expiry_date = getdate(doc.expiry_date)
        days_until = (expiry_date - today_date).days
        if days_until in warning_thresholds:
            _create_document_expiry_notification(
                doc.name,
                doc.document_number,
                doc.document_type,
                doc.customer,
                days_until,
            )


def _create_expiry_notification(vehicle_name, vehicle_number, field, days_until):
    label = field.replace("_", " ").title()
    message = f"Vehicle {vehicle_number}: {label} expires " f"in {days_until} day(s)."
    _create_notification(
        subject=message,
        type="Alert",
        document_name=vehicle_name,
    )


def _create_document_expiry_notification(doc_name, doc_number, doc_type, customer, days_until):
    message = (
        f"Document {doc_number} ({doc_type}) for " f"customer {customer} expires in " f"{days_until} day(s)."
    )
    _create_notification(
        subject=message,
        type="Alert",
        document_name=doc_name,
    )


def _create_notification(subject, type, document_name):
    try:
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "subject": subject,
                "type": type,
                "document_name": document_name,
                "for_user": frappe.session.user,
            }
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            title="Rent Pro Notification",
            message=f"Failed to create notification: {subject}",
        )


def geofleete_heartbeat():
    settings = frappe.get_single("GeoFleete Settings")
    if not getattr(settings, "geofleete_enabled", 0):
        return
    if not getattr(settings, "mock_mode", 0):
        return

    frappe.enqueue(
        "rentpro.tasks._geofleete_simulation_job",
        queue="short",
        timeout=120,
    )


def _geofleete_simulation_job():
    from rentpro.gps import get_provider
    from rentpro.gps.api import (
        _create_geofence_alert,
        _save_position,
    )

    provider = get_provider()
    if not provider:
        return

    states = provider.get_all_vehicle_states()
    for vname in list(states.keys())[:10]:
        provider.simulate_movement(vname, 15)
        state = provider.get_vehicle_state(vname)
        if state:
            _save_position(vname, state)
            events = provider.check_geofences(vname, state["latitude"], state["longitude"])
            for event in events:
                _create_geofence_alert(event)


def scheduled_subscription_renewal():
    from rentpro.saas.billing import process_renewals

    process_renewals()


def scheduled_check_overdue_subscriptions():
    from rentpro.saas.billing import (
        check_and_suspend_overdue,
        mark_past_due,
    )

    mark_past_due()
    check_and_suspend_overdue()


def scheduled_health_check():
    from rentpro.super_admin.system_health import (
        run_health_check,
    )

    run_health_check()
