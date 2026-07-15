"""Mock GPS Provider — Simulates realistic fleet data for development.

Generates vehicle positions with realistic movement patterns,
speed variations, fuel consumption, and geofence events.
"""

import math
import random

import frappe
from frappe.utils import now_datetime

from rentpro.gps.provider import GPSProviderInterface

# Casablanca city center approximate coordinates
_DEFAULT_LAT = 33.5731
_DEFAULT_LNG = -7.5898

# Realistic vehicle movement parameters
_SPEED_RANGE = (0, 120)  # km/h
_FUEL_CONSUMPTION_PER_KM = 0.08  # % per km
_BATTERY_DRAIN_PER_HOUR = 0.5  # % per hour
_GPS_SIGNAL_RANGE = (60, 100)  # %
_ACCURACY_RANGE = (3, 15)  # meters

# Simulation state cache (in-memory per process)
_simulation_state = {}


class MockProvider(GPSProviderInterface):
    """Mock GPS provider generating realistic fleet telemetry."""

    def __init__(self):
        self._ensure_vehicles_tracked()

    def _ensure_vehicles_tracked(self):
        vehicles = frappe.get_all(
            "Vehicle",
            filters={"status": ["not in", ["Sold", "Inactive"]]},
            fields=["name", "plate_number"],
        )
        for v in vehicles:
            if v.name not in _simulation_state:
                _simulation_state[v.name] = _init_vehicle_state(v.name, v.plate_number)

    def get_positions(self, vehicle_name=None, since=None):
        self._ensure_vehicles_tracked()
        positions = []
        targets = [vehicle_name] if vehicle_name else list(_simulation_state.keys())
        for vname in targets:
            state = _simulation_state.get(vname)
            if not state:
                continue
            for pos in state.get("position_history", []):
                if since and pos["timestamp"] < since:
                    continue
                positions.append(
                    {
                        "vehicle": vname,
                        "latitude": pos["latitude"],
                        "longitude": pos["longitude"],
                        "speed": pos["speed"],
                        "heading": pos.get("heading", 0),
                        "altitude": pos.get("altitude", 50),
                        "accuracy": pos.get("accuracy", 5),
                        "timestamp": pos["timestamp"],
                        "ignition": state.get("ignition", True),
                        "battery": state.get("battery", 100),
                        "fuel_level": state.get("fuel_level", 100),
                        "engine_running": state.get("engine_running", True),
                        "gps_signal_strength": state.get("gps_signal", 85),
                    }
                )
        return positions

    def get_vehicle_state(self, vehicle_name):
        self._ensure_vehicles_tracked()
        state = _simulation_state.get(vehicle_name)
        if not state:
            return None
        return {
            "vehicle": vehicle_name,
            "latitude": state["latitude"],
            "longitude": state["longitude"],
            "speed": state["speed"],
            "heading": state.get("heading", 0),
            "altitude": state.get("altitude", 50),
            "accuracy": state.get("accuracy", 5),
            "timestamp": state["last_update"],
            "ignition": state.get("ignition", True),
            "battery": state.get("battery", 100),
            "fuel_level": state.get("fuel_level", 100),
            "engine_running": state.get("engine_running", True),
            "gps_signal_strength": state.get("gps_signal", 85),
            "is_moving": state.get("speed", 0) > 2,
            "last_update": state["last_update"],
        }

    def get_all_vehicle_states(self):
        self._ensure_vehicles_tracked()
        result = {}
        for vname in _simulation_state:
            state = self.get_vehicle_state(vname)
            if state:
                result[vname] = state
        return result

    def simulate_movement(self, vehicle_name, duration_seconds=30):
        state = _simulation_state.get(vehicle_name)
        if not state:
            return

        steps = max(1, duration_seconds // 5)
        for _ in range(steps):
            if not state.get("ignition", True):
                break

            speed = state.get("speed", 0)
            target_speed = random.uniform(20, 80)
            state["speed"] = speed + (target_speed - speed) * 0.3
            state["speed"] = max(
                _SPEED_RANGE[0],
                min(_SPEED_RANGE[1], state["speed"]),
            )

            heading = state.get("heading", 0)
            heading += random.uniform(-15, 15)
            heading = heading % 360
            state["heading"] = heading

            speed_ms = state["speed"] / 3.6
            delta_lat = speed_ms * math.cos(math.radians(heading)) * 5 / 111320
            delta_lng = (
                speed_ms
                * math.sin(math.radians(heading))
                * 5
                / (111320 * math.cos(math.radians(state["latitude"])))
            )
            state["latitude"] += delta_lat
            state["longitude"] += delta_lng

            state["fuel_level"] = max(
                0,
                state.get("fuel_level", 100) - _FUEL_CONSUMPTION_PER_KM * (state["speed"] / 360),
            )
            state["battery"] = max(
                0,
                state.get("battery", 100) - _BATTERY_DRAIN_PER_HOUR / 720,
            )
            state["gps_signal"] = random.randint(*_GPS_SIGNAL_RANGE)
            state["accuracy"] = random.uniform(*_ACCURACY_RANGE)
            state["last_update"] = now_datetime()

            state.setdefault("position_history", []).append(
                {
                    "latitude": state["latitude"],
                    "longitude": state["longitude"],
                    "speed": state["speed"],
                    "heading": heading,
                    "altitude": state.get("altitude", 50),
                    "accuracy": state["accuracy"],
                    "timestamp": state["last_update"],
                }
            )
            if len(state["position_history"]) > 500:
                state["position_history"] = state["position_history"][-500:]

    def check_geofences(self, vehicle_name, latitude, longitude):
        events = []
        zones = frappe.get_all(
            "Geofence Zone",
            filters={"is_active": 1},
            fields=[
                "name",
                "zone_name",
                "center_latitude",
                "center_longitude",
                "radius",
                "zone_type",
                "notify_on_entry",
                "notify_on_exit",
                "notify_on_violation",
            ],
        )
        state = _simulation_state.get(vehicle_name, {})
        prev_inside = state.get("_geofence_status", {})

        for zone in zones:
            if not zone.center_latitude or not zone.center_longitude:
                continue
            dist = _haversine(
                latitude,
                longitude,
                zone.center_latitude,
                zone.center_longitude,
            )
            is_inside = dist <= (zone.radius or 500)
            was_inside = prev_inside.get(zone.name, False)

            if is_inside and not was_inside:
                if zone.notify_on_entry:
                    events.append(
                        {
                            "vehicle": vehicle_name,
                            "zone": zone.name,
                            "zone_name": zone.zone_name,
                            "event_type": "Entry",
                            "latitude": latitude,
                            "longitude": longitude,
                            "distance": round(dist, 1),
                        }
                    )
            elif not is_inside and was_inside:
                if zone.notify_on_exit:
                    events.append(
                        {
                            "vehicle": vehicle_name,
                            "zone": zone.name,
                            "zone_name": zone.zone_name,
                            "event_type": "Exit",
                            "latitude": latitude,
                            "longitude": longitude,
                            "distance": round(dist, 1),
                        }
                    )

            prev_inside[zone.name] = is_inside

        state["_geofence_status"] = prev_inside
        return events

    def get_maintenance_status(self, vehicle_name=None):
        reminders = []
        vehicles = [vehicle_name] if vehicle_name else list(_simulation_state.keys())
        for vname in vehicles:
            state = _simulation_state.get(vname, {})
            mileage = state.get("current_mileage", 50000)

            if mileage > 45000:
                reminders.append(
                    {
                        "vehicle": vname,
                        "type": "Oil Change",
                        "due_mileage": 50000,
                        "current_mileage": mileage,
                        "priority": "High" if mileage > 52000 else "Medium",
                        "description": ("Oil change overdue" if mileage > 50000 else "Oil change due soon"),
                    }
                )
            if mileage > 90000:
                reminders.append(
                    {
                        "vehicle": vname,
                        "type": "Tire Rotation",
                        "due_mileage": 100000,
                        "current_mileage": mileage,
                        "priority": "High" if mileage > 100000 else "Low",
                        "description": "Tire rotation due",
                    }
                )

            fuel = state.get("fuel_level", 100)
            if fuel < 15:
                reminders.append(
                    {
                        "vehicle": vname,
                        "type": "Low Fuel",
                        "due_date": str(now_datetime().date()),
                        "current_mileage": mileage,
                        "priority": "High",
                        "description": (f"Fuel level critical: {fuel:.0f}%"),
                    }
                )

        return reminders

    def is_available(self):
        return True


def _init_vehicle_state(vehicle_name, plate_number):
    lat = _DEFAULT_LAT + random.uniform(-0.05, 0.05)
    lng = _DEFAULT_LNG + random.uniform(-0.05, 0.05)
    return {
        "latitude": lat,
        "longitude": lng,
        "speed": random.uniform(0, 60),
        "heading": random.uniform(0, 360),
        "altitude": random.uniform(30, 200),
        "accuracy": random.uniform(3, 10),
        "ignition": True,
        "battery": random.uniform(80, 100),
        "fuel_level": random.uniform(30, 100),
        "engine_running": True,
        "gps_signal": random.randint(70, 100),
        "current_mileage": random.randint(10000, 80000),
        "last_update": now_datetime(),
        "position_history": [],
        "_geofence_status": {},
    }


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
