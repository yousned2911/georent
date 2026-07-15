"""GPS Provider Factory — Returns the configured provider instance.

Replace MockProvider with TraccarProvider here when ready.
No other code should import providers directly.
"""

import frappe


def get_provider():
    """Return the active GPS provider based on GeoFleete Settings."""
    settings = frappe.get_single("GeoFleete Settings")

    if not getattr(settings, "geofleete_enabled", 0):
        return None

    provider_name = getattr(settings, "gps_provider", "Mock") or "Mock"

    if provider_name == "Traccar":
        try:
            from rentpro.gps.traccar_provider import TraccarProvider

            return TraccarProvider(settings)
        except ImportError:
            frappe.log_error(
                title="GeoFleete",
                message="TraccarProvider not yet implemented. Falling back to MockProvider.",
            )

    from rentpro.gps.mock_provider import MockProvider

    return MockProvider()
