# Development Guide

## Architecture Overview

Rent Pro is a Frappe custom app that extends ERPNext. It follows these principles:

- **No core modifications** — All code lives in the `rentpro` app
- **DocType-driven** — Data models defined as Frappe DocTypes
- **Hook-based** — Behavior extended via `hooks.py`
- **SaaS-ready** — Every document scoped to an Agency

## Project Structure

```
rentpro/
├── __init__.py
├── hooks.py              # App hooks
├── modules.txt           # Declared modules
├── patches.txt           # Migration patches
├── tasks.py              # Scheduled jobs
├── boot.py               # Session boot extension
├── utils.py              # Utility functions
├── setup/                # Install/uninstall/migrate
├── rentpro/              # Default module
│   ├── doctype/
│   │   └── rent_pro_settings/
│   ├── patches/
│   └── ...
├── public/               # JS/CSS assets
├── templates/            # Jinja templates
├── translations/         # i18n (EN, FR, AR)
└── www/                  # Web pages
```

## Adding a New DocType

### 1. Create the DocType

In the Frappe Desk, go to **New DocType** or create the JSON file manually:

```
rentpro/rentpro/doctype/vehicle/
├── __init__.py
├── vehicle.json
├── vehicle.py
├── vehicle.js
└── test_vehicle.py
```

### 2. Define the Schema

The `.json` file defines fields, permissions, and naming:

```json
{
  "name": "Vehicle",
  "module": "Rent Pro",
  "fields": [...],
  "permissions": [...],
  "autoname": "format:VEH-{####}"
}
```

### 3. Write the Controller

The `.py` file contains business logic:

```python
import frappe
from frappe.model.document import Document

class Vehicle(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        if self.insurance_expiry and self.insurance_expiry < frappe.utils.today():
            frappe.throw("Insurance has expired")
```

### 4. Write the Client Script

The `.js` file handles form behavior:

```javascript
frappe.ui.form.on("Vehicle", {
    refresh(frm) {
        // Custom buttons, indicators, etc.
    }
});
```

### 5. Write Tests

The `test_*.py` file contains integration tests:

```python
import frappe
from frappe.tests import IntegrationTestCase

class TestVehicle(IntegrationTestCase):
    def test_vehicle_creation(self):
        vehicle = frappe.get_doc({
            "doctype": "Vehicle",
            "vehicle_number": "TEST-001",
            ...
        })
        vehicle.insert()
        self.assertEqual(vehicle.status, "Available")
```

## Adding a New Module

### 1. Update modules.txt

Add the module name to `rentpro/modules.txt`:

```
Rent Pro
Vehicles
Reservations
Contracts
```

### 2. Create Module Directory

```
rentpro/rentpro/doctype/
├── rent_pro_settings/
├── vehicle/
├── reservation/
└── ...
```

### 3. Add Workspace

Create a workspace JSON for the module:

```
rentpro/rentpro/workspace/vehicles/
└── vehicles.json
```

## Hooks Reference

See `ERPNEXT_ARCHITECTURE.md` for the complete hooks reference.

### Key Hooks Used

| Hook | Purpose |
|------|---------|
| `doc_events` | React to document CRUD events |
| `scheduler_events` | Run periodic tasks |
| `has_permission` | Custom permission logic |
| `extend_bootinfo` | Pass data to frontend |
| `fixtures` | Sync configuration data |

## Testing

### Running Tests

```bash
# All tests
bench --site dev.rentpro.local run-tests --app rentpro

# Specific module
bench --site dev.rentpro.local run-tests --app rentpro --module rentpro.rentpro.doctype.rent_pro_settings

# With coverage
coverage run -m pytest rentpro/
coverage report -m
```

### Test Conventions

- Test files: `test_*.py`
- Test classes: `Test*` (extend `IntegrationTestCase`)
- Test methods: `test_*`
- Use `frappe.set_user()` for permission tests
- Clean up test data in `setUp`/`tearDown`

## Code Style

- **Python**: Black formatter, 110 char line length
- **JavaScript**: Frappe conventions, ES6+
- **CSS**: BEM naming, CSS variables
- **Commits**: Conventional commits (`feat:`, `fix:`, etc.)

## Migration Patches

When changing DocType schemas:

1. Create patch file in `rentpro/rentpro/patches/v{X}_{Y}/`
2. Add entry to `rentpro/patches.txt`
3. Test migration on clean site

```bash
bench --site test-site migrate
```
