"""GeoFleete API — Server-side methods called by UI pages."""

import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def get_fleet_positions():
    from rentpro.gps import get_provider

    provider = get_provider()
    if not provider:
        return []

    states = provider.get_all_vehicle_states()
    result = []
    for vname, state in states.items():
        vehicle_doc = frappe.db.get_value(
            "Vehicle",
            vname,
            ["plate_number", "make", "model"],
            as_dict=True,
        )
        result.append(
            {
                "vehicle": vname,
                "plate_number": (vehicle_doc.plate_number if vehicle_doc else vname),
                "make": vehicle_doc.make if vehicle_doc else "",
                "model": vehicle_doc.model if vehicle_doc else "",
                "latitude": state.get("latitude", 0),
                "longitude": state.get("longitude", 0),
                "speed": state.get("speed", 0),
                "fuel_level": state.get("fuel_level", 0),
                "battery_level": state.get("battery", 0),
                "status": state.get(
                    "status",
                    "Moving" if state.get("speed", 0) > 2 else "Idle" if state.get("ignition") else "Offline",
                ),
                "ignition": state.get("ignition", False),
                "last_update": str(state.get("last_update", "")),
            }
        )
    return result


@frappe.whitelist()
def get_all_vehicle_states():
    from rentpro.gps import get_provider

    provider = get_provider()
    if not provider:
        return {}

    states = provider.get_all_vehicle_states()
    result = {}
    for vname, state in states.items():
        vehicle_doc = frappe.db.get_value(
            "Vehicle",
            vname,
            ["plate_number"],
            as_dict=True,
        )
        state["plate_number"] = vehicle_doc.plate_number if vehicle_doc else vname
        result[vname] = state
    return result


@frappe.whitelist()
def get_active_geofences():
    zones = frappe.get_all(
        "Geofence Zone",
        filters={"is_active": 1},
        fields=[
            "name",
            "zone_name",
            "zone_type",
            "center_latitude",
            "center_longitude",
            "radius",
            "speed_limit",
            "is_active",
            "notify_on_entry",
            "notify_on_exit",
            "notify_on_violation",
        ],
    )
    return zones


@frappe.whitelist()
def get_recent_alerts(limit=10, include_acknowledged=0):
    filters = {}
    if not include_acknowledged:
        filters["is_acknowledged"] = 0

    alerts = frappe.get_all(
        "Geofence Alert",
        filters=filters,
        fields=[
            "name",
            "vehicle",
            "zone",
            "alert_type",
            "alert_timestamp",
            "severity",
            "speed",
            "distance",
            "is_acknowledged",
            "acknowledged_by",
            "resolution_notes",
        ],
        order_by="alert_timestamp desc",
        limit=int(limit),
    )

    for alert in alerts:
        zone_name = frappe.db.get_value("Geofence Zone", alert.zone, "zone_name")
        alert["zone_name"] = zone_name or alert.zone

    return alerts


@frappe.whitelist()
def acknowledge_alert(alert_name, notes=None):
    alert = frappe.get_doc("Geofence Alert", alert_name)
    alert.acknowledge(notes=notes)
    return {"status": "ok"}


@frappe.whitelist()
def get_maintenance_alerts():
    from rentpro.gps import get_provider

    provider = get_provider()
    if not provider:
        return []

    return provider.get_maintenance_status()


@frappe.whitelist()
def get_fleet_summary():
    from rentpro.gps import get_provider

    provider = get_provider()
    if not provider:
        return {
            "total": 0,
            "moving": 0,
            "idle": 0,
            "offline": 0,
            "avg_fuel": 0,
            "active_alerts": 0,
        }

    states = provider.get_all_vehicle_states()
    total = len(states)
    moving = sum(1 for s in states.values() if s.get("speed", 0) > 2)
    idle = sum(1 for s in states.values() if s.get("ignition") and s.get("speed", 0) <= 2)
    offline = sum(1 for s in states.values() if not s.get("ignition"))
    avg_fuel = sum(s.get("fuel_level", 0) for s in states.values()) / total if total else 0

    active_alerts = frappe.db.count("Geofence Alert", {"is_acknowledged": 0})

    return {
        "total": total,
        "moving": moving,
        "idle": idle,
        "offline": offline,
        "avg_fuel": avg_fuel,
        "active_alerts": active_alerts,
    }


@frappe.whitelist()
def simulate_fleet_movement(duration_seconds=30):
    frappe.enqueue(
        "_simulate_fleet_movement_job",
        queue="short",
        duration_seconds=int(duration_seconds),
    )
    return {"status": "ok", "message": "Fleet simulation queued"}


def _simulate_fleet_movement_job(duration_seconds):
    from rentpro.gps import get_provider

    provider = get_provider()
    if not provider:
        return

    states = provider.get_all_vehicle_states()
    for vname in states:
        provider.simulate_movement(vname, duration_seconds)
        state = provider.get_vehicle_state(vname)
        if state:
            _save_position(vname, state)
            events = provider.check_geofences(vname, state["latitude"], state["longitude"])
            for event in events:
                _create_geofence_alert(event)


def _save_position(vehicle_name, state):
    pos = frappe.get_doc(
        {
            "doctype": "GPS Position",
            "vehicle": vehicle_name,
            "latitude": state["latitude"],
            "longitude": state["longitude"],
            "speed": state.get("speed", 0),
            "heading": state.get("heading", 0),
            "altitude": state.get("altitude", 0),
            "accuracy": state.get("accuracy", 5),
            "ignition": state.get("ignition", False),
            "engine_running": state.get("engine_running", False),
            "fuel_level": state.get("fuel_level", 0),
            "battery_level": state.get("battery", 0),
            "gps_signal_strength": state.get("gps_signal_strength", 85),
            "timestamp": state.get("timestamp", now_datetime()),
            "provider": "Mock",
        }
    )
    pos.insert(ignore_permissions=True)

    tracking = frappe.db.exists("Vehicle Tracking", vehicle_name)
    if tracking:
        doc = frappe.get_doc("Vehicle Tracking", vehicle_name)
        doc.update_from_position({**state, "provider": "Mock"})
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle Tracking",
                "vehicle": vehicle_name,
                "last_latitude": state["latitude"],
                "last_longitude": state["longitude"],
                "last_speed": state.get("speed", 0),
                "ignition": state.get("ignition", False),
                "fuel_level": state.get("fuel_level", 0),
                "battery_level": state.get("battery", 0),
                "engine_running": state.get("engine_running", False),
                "gps_signal_strength": state.get("gps_signal_strength", 85),
                "last_update": state.get("timestamp", now_datetime()),
                "provider": "Mock",
            }
        )
        doc.insert(ignore_permissions=True)

    frappe.db.commit()


def _create_geofence_alert(event):
    from rentpro.doctype.geofence_alert.geofence_alert import (
        create_alert,
    )

    create_alert(
        vehicle=event["vehicle"],
        zone=event["zone"],
        event_type=event["event_type"],
        latitude=event.get("latitude"),
        longitude=event.get("longitude"),
        distance=event.get("distance"),
    )
