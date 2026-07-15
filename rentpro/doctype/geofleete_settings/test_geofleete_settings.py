import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime


class TestGeoFleete(IntegrationTestCase):
    def setUp(self):
        self.vehicle = self._create_vehicle()

    def tearDown(self):
        frappe.db.rollback()

    def _create_vehicle(self, status="Available"):
        uid = frappe.utils.now_datetime().microsecond % 100000
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle",
                "plate_number": f"GEO-{uid}",
                "make": "Mercedes",
                "model": "C-Class",
                "year": 2023,
                "status": status,
                "daily_rate": 800,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_zone(self, **kwargs):
        data = {
            "doctype": "Geofence Zone",
            "zone_name": f"Test Zone {frappe.utils.now_datetime().microsecond % 1000}",
            "zone_type": "Depot",
            "center_latitude": 33.5731,
            "center_longitude": -7.5898,
            "radius": 1000,
            "is_active": 1,
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    def _create_alert(self, zone_name, **kwargs):
        data = {
            "doctype": "Geofence Alert",
            "vehicle": self.vehicle.name,
            "zone": zone_name,
            "alert_type": "Entry",
            "severity": "Low",
            "latitude": 33.5731,
            "longitude": -7.5898,
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────── 1. GPS Position ────────

    def test_gps_position_creation(self):
        doc = frappe.get_doc(
            {
                "doctype": "GPS Position",
                "vehicle": self.vehicle.name,
                "latitude": 33.5731,
                "longitude": -7.5898,
                "speed": 60,
                "heading": 180,
                "ignition": 1,
                "fuel_level": 85,
                "battery_level": 95,
                "timestamp": now_datetime(),
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        self.assertTrue(doc.name)

    def test_gps_position_invalid_latitude(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_gps_position,
            latitude=999,
        )

    def _create_gps_position(self, **kwargs):
        data = {
            "doctype": "GPS Position",
            "vehicle": self.vehicle.name,
            "latitude": 33.5731,
            "longitude": -7.5898,
            "speed": 60,
            "timestamp": now_datetime(),
        }
        data.update(kwargs)
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc

    # ──────── 2. Geofence Zone ────────

    def test_geofence_zone_creation(self):
        zone = self._create_zone()
        self.assertTrue(zone.name)
        self.assertEqual(zone.zone_type, "Depot")

    def test_geofence_zone_invalid_coords(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_zone,
            center_latitude=999,
        )

    def test_geofence_zone_zero_radius_throws(self):
        self.assertRaises(
            frappe.exceptions.ValidationError,
            self._create_zone,
            radius=0,
        )

    # ──────── 3. Geofence Alert ────────

    def test_geofence_alert_creation(self):
        zone = self._create_zone()
        alert = self._create_alert(zone.name)
        self.assertTrue(alert.name)
        self.assertEqual(alert.alert_type, "Entry")

    def test_alert_acknowledge(self):
        zone = self._create_zone()
        alert = self._create_alert(zone.name)
        alert.acknowledge(notes="Checked by operator")
        frappe.db.commit()
        self.assertTrue(alert.is_acknowledged)
        self.assertEqual(alert.acknowledged_by, frappe.session.user)
        self.assertEqual(alert.resolution_notes, "Checked by operator")

    def test_alert_auto_severity_speed_violation(self):
        zone = self._create_zone()
        alert = self._create_alert(zone.name, alert_type="Speed Violation")
        self.assertEqual(alert.severity, "High")

    def test_alert_auto_severity_unauthorized(self):
        zone = self._create_zone()
        alert = self._create_alert(zone.name, alert_type="Unauthorized Use")
        self.assertEqual(alert.severity, "Critical")

    # ──────── 4. Vehicle Tracking ────────

    def test_vehicle_tracking_creation(self):
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle Tracking",
                "vehicle": self.vehicle.name,
                "status": "Moving",
                "last_latitude": 33.5731,
                "last_longitude": -7.5898,
                "last_speed": 65,
                "ignition": 1,
                "fuel_level": 75,
                "battery_level": 90,
                "engine_running": 1,
                "gps_signal_strength": 85,
                "current_mileage": 45000,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        self.assertTrue(doc.name)

    def test_vehicle_tracking_update_from_position(self):
        doc = frappe.get_doc(
            {
                "doctype": "Vehicle Tracking",
                "vehicle": self.vehicle.name,
                "status": "Offline",
                "current_mileage": 45000,
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        doc.update_from_position(
            {
                "latitude": 33.58,
                "longitude": -7.59,
                "speed": 45,
                "ignition": True,
                "fuel_level": 70,
                "battery": 88,
                "engine_running": True,
                "gps_signal_strength": 80,
            }
        )
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        self.assertEqual(doc.status, "Moving")
        self.assertAlmostEqual(doc.last_speed, 45)

    # ──────── 5. MockProvider ────────

    def test_mock_provider_positions(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        positions = provider.get_positions()
        self.assertIsInstance(positions, list)

    def test_mock_provider_vehicle_state(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        state = provider.get_vehicle_state(self.vehicle.name)
        self.assertIsNotNone(state)
        self.assertIn("latitude", state)
        self.assertIn("longitude", state)
        self.assertIn("speed", state)

    def test_mock_provider_all_states(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        states = provider.get_all_vehicle_states()
        self.assertIsInstance(states, dict)

    def test_mock_provider_movement(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        state_before = provider.get_vehicle_state(self.vehicle.name)
        provider.simulate_movement(self.vehicle.name, 10)
        state_after = provider.get_vehicle_state(self.vehicle.name)
        self.assertNotEqual(
            state_before["latitude"],
            state_after["latitude"],
        )

    def test_mock_provider_maintenance(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        reminders = provider.get_maintenance_status()
        self.assertIsInstance(reminders, list)

    def test_mock_provider_is_available(self):
        from rentpro.gps.mock_provider import MockProvider

        provider = MockProvider()
        self.assertTrue(provider.is_available())

    # ──────── 6. Geofleete Settings ────────

    def test_geofleete_settings_creation(self):
        settings = frappe.get_single("GeoFleete Settings")
        self.assertTrue(settings)

    def test_provider_factory_mock(self):
        from rentpro.gps import get_provider

        settings = frappe.get_single("GeoFleete Settings")
        settings.geofleete_enabled = 1
        settings.gps_provider = "Mock"
        settings.mock_mode = 1
        settings.save(ignore_permissions=True)
        frappe.db.commit()

        provider = get_provider()
        self.assertIsNotNone(provider)
        self.assertTrue(provider.is_available())
