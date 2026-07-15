import frappe


def extend_bootinfo(bootinfo):
    from rentpro import __version__

    bootinfo.rent_pro_version = __version__
    bootinfo.rent_pro_settings = _get_settings_dict()


def _get_settings_dict():
    try:
        settings = frappe.get_single("Rent Pro Settings")
        return {
            "agency_name": settings.agency_name,
            "default_currency": settings.default_currency,
            "ocr_enabled": settings.ocr_enabled,
            "geofleete_enabled": settings.geofleete_enabled,
        }
    except Exception:
        frappe.log_error("Failed to load Rent Pro settings for bootinfo")
        return {}
