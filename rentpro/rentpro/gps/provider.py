"""GPS Provider Interface — Abstract base for all GPS providers.

Any concrete provider (Mock, Traccar, etc.) must implement this interface.
The rest of the GeoFleete module consumes only this interface.
"""

from abc import ABC, abstractmethod


class GPSProviderInterface(ABC):
    """Abstract GPS provider that all implementations must satisfy."""

    @abstractmethod
    def get_positions(self, vehicle_name=None, since=None):
        """Return list of position dicts for vehicle(s).

        Args:
            vehicle_name: Optional vehicle name to filter.
            since: Optional datetime; only return positions after this.

        Returns:
            list[dict]: Each dict has keys:
                vehicle, latitude, longitude, speed, heading,
                altitude, accuracy, timestamp, ignition,
                battery, fuel_level, engine_running,
                gps_signal_strength
        """

    @abstractmethod
    def get_vehicle_state(self, vehicle_name):
        """Return current state for a single vehicle.

        Returns:
            dict with keys:
                vehicle, latitude, longitude, speed, heading,
                altitude, accuracy, timestamp, ignition,
                battery, fuel_level, engine_running,
                gps_signal_strength, is_moving, last_update
        """

    @abstractmethod
    def get_all_vehicle_states(self):
        """Return current state for all tracked vehicles.

        Returns:
            dict[str, dict]: Mapping of vehicle_name -> state dict.
        """

    @abstractmethod
    def simulate_movement(self, vehicle_name, duration_seconds=30):
        """Simulate vehicle movement for the given duration.

        Generates positions, updates state, checks geofences.
        """

    @abstractmethod
    def check_geofences(self, vehicle_name, latitude, longitude):
        """Check if vehicle is inside/outside any geofence.

        Returns:
            list[dict]: Geofence events (entry, exit, violation).
        """

    @abstractmethod
    def get_maintenance_status(self, vehicle_name=None):
        """Return maintenance reminders for vehicle(s).

        Returns:
            list[dict]: Each dict has keys:
                vehicle, type, due_date, due_mileage,
                current_mileage, priority, description
        """

    @abstractmethod
    def is_available(self):
        """Return True if provider is connected and operational."""
