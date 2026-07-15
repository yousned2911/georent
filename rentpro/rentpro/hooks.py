app_name = "rentpro"
app_title = "Rent Pro"
app_publisher = "Rent Pro"
app_description = "Paperless ERP for Moroccan car rental agencies"
app_email = "dev@rentpro.ma"
app_license = "MIT"

# --------------------------------------------------------------------------
# Apps
# --------------------------------------------------------------------------

required_apps = ["erpnext"]

# --------------------------------------------------------------------------
# Includes
# --------------------------------------------------------------------------

app_include_css = "assets/css/rentpro.css"
app_include_js = "assets/js/rentpro.js"

# --------------------------------------------------------------------------
# Install
# --------------------------------------------------------------------------

before_install = "rentpro.setup.install.before_install"
after_install = "rentpro.setup.install.after_install"

# --------------------------------------------------------------------------
# Uninstall
# --------------------------------------------------------------------------

before_uninstall = "rentpro.setup.uninstall.before_uninstall"
after_uninstall = "rentpro.setup.uninstall.after_uninstall"

# --------------------------------------------------------------------------
# Migrate
# --------------------------------------------------------------------------

before_migrate = "rentpro.setup.migrate.before_migrate"
after_migrate = "rentpro.setup.migrate.after_migrate"

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

fixtures = []

# --------------------------------------------------------------------------
# Document Events
# --------------------------------------------------------------------------

doc_events = {
    "Rental Contract": {
        "on_update": "rentpro.doctype.rental_contract.rental_contract.on_contract_update",
        "on_submit": "rentpro.doctype.rental_contract.rental_contract.on_contract_submit",
        "on_cancel": "rentpro.doctype.rental_contract.rental_contract.on_contract_cancel",
    },
    "Reservation": {
        "on_update": "rentpro.doctype.reservation.reservation.on_reservation_update",
    },
    "Payment Transaction": {
        "on_update": "rentpro.doctype.payment_transaction.payment_transaction.on_payment_update",
    },
    "Expense Entry": {
        "on_update": "rentpro.doctype.expense_entry.expense_entry.on_expense_update",
    },
    "Document Record": {
        "on_update": "rentpro.doctype.document_record.document_record.on_document_record_update",
    },
    "Geofence Alert": {
        "on_update": "rentpro.doctype.geofence_alert.geofence_alert.on_geofence_alert_update",
    },
    "Vehicle": {
        "before_insert": "rentpro.saas.plan_enforcement.on_vehicle_insert_validate",
    },
}

# --------------------------------------------------------------------------
# Scheduled Jobs
# --------------------------------------------------------------------------

scheduler_events = {
    "daily": [
        "rentpro.tasks.daily_tasks",
        "rentpro.tasks.scheduled_subscription_renewal",
        "rentpro.tasks.scheduled_check_overdue_subscriptions",
        "rentpro.tasks.scheduled_health_check",
    ],
    "hourly": [
        "rentpro.tasks.hourly_tasks",
    ],
    "every_five_minutes": [
        "rentpro.tasks.geofleete_heartbeat",
    ],
}

# --------------------------------------------------------------------------
# Permissions
# --------------------------------------------------------------------------

has_permission = {
    "Rent Pro Settings": "rentpro.doctype.rent_pro_settings.rent_pro_settings.has_permission",
    "SaaS Settings": "rentpro.doctype.saas_settings.saas_settings.has_permission",
    "Super Admin Settings": "rentpro.doctype.super_admin_settings.super_admin_settings.has_permission",
    "System Health Settings": "rentpro.doctype.system_health_settings.system_health_settings.has_permission",
}

# --------------------------------------------------------------------------
# Jinja
# --------------------------------------------------------------------------

jinja = {
    "methods": [
        "rentpro.utils.get_rent_pro_version",
    ],
}

# --------------------------------------------------------------------------
# Boot Session
# --------------------------------------------------------------------------

extend_bootinfo = "rentpro.boot.extend_bootinfo"
