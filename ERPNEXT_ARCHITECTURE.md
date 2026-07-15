# ERPNext & Frappe Architecture Reference

This document explains the Frappe Framework and ERPNext architecture as it applies to the **Rent Pro** custom app (`rentpro`). It serves as the technical foundation for all development decisions.

---

## 1. Custom Apps

### What Is a Custom App?

A custom app is a Frappe application that extends ERPNext without modifying its core. It lives alongside ERPNext inside the bench directory and follows Frappe conventions. All Rent Pro code resides in `rentpro`.

### App Lifecycle

```
bench new-app rentpro          # Scaffold
bench --site site1 install-app rentpro   # Install on site
bench migrate                  # Apply schema changes and patches
bench build --app rentpro      # Build frontend assets
bench update                   # Pull updates and migrate
```

### App Directory Structure

```
apps/rentpro/
├── rentpro/
│   ├── hooks.py              # Extension point (most important file)
│   ├── modules.txt           # Declared modules
│   ├── patches.txt           # Migration patches
│   ├── __init__.py
│   ├── vehicles/             # Module with DocTypes
│   │   ├── doctype/
│   │   │   ├── vehicle/
│   │   │   │   ├── vehicle.json   # Schema definition
│   │   │   │   ├── vehicle.py     # Server controller
│   │   │   │   ├── vehicle.js     # Client script
│   │   │   │   └── test_vehicle.py
│   │   └── report/
│   ├── public/               # JS/CSS assets
│   ├── templates/            # Jinja HTML templates
│   └── translations/         # i18n CSV files
├── setup.py
├── pyproject.toml
└── requirements.txt
```

### Key Rules for Rent Pro

- **Never** modify ERPNext or Frappe core files
- All custom DocTypes, APIs, and logic live in `rentpro`
- Use `fixtures` to export/import configuration data (e.g., TVA rates)
- Use `required_apps = ["erpnext"]` to declare ERPNext as a dependency

---

## 2. DocTypes

### What Is a DocType?

A DocType is the **model + view + controller** for a piece of data. It is Frappe's central abstraction. Creating a DocType:

1. Creates a MariaDB/PostgreSQL table (prefixed with `tab`)
2. Auto-generates a List View (`/app/vehicle`)
3. Auto-generates a Form View (`/app/vehicle/VEH-001`)
4. Auto-generates REST API endpoints
5. Applies permission rules

### DocType Types

| Type | Description | Rent Pro Example |
|------|-------------|------------------|
| **Document** | Standard table with many records | `Vehicle`, `Reservation`, `Rental Contract` |
| **Single** | One record only (settings) | `Rent Pro Settings`, `TVA Configuration` |
| **Child Table** | Embedded in a parent | `Reservation Item`, `Contract Line Item` |
| **Submittable** | Has Submit/Cancel/Amend lifecycle | `Rental Contract`, `Sales Invoice` |
| **Virtual** | No DB table; reads from external source | `GPS Position` (from external API) |

### Field Types Used in Rent Pro

| Field Type | Use Case |
|------------|----------|
| `Data` | Names, codes, short text (max 140 chars) |
| `Link` | Foreign key to another DocType (e.g., Vehicle → Vehicle Category) |
| `Dynamic Link` | Link where target DocType is a field value |
| `Select` | Fixed options (e.g., status: Available, Rented, Maintenance) |
| `Table` | Child table (e.g., Contract → Contract Line Items) |
| `Date` / `Datetime` | Reservation dates, contract start/end |
| `Currency` | Rental amounts, deposits, TVA |
| `Check` | Boolean flags |
| `Text Editor` | Contract terms, notes |
| `Attach` | Uploaded documents (CIN scans, licenses) |
| `Geolocation` | GPS coordinates (for GeoFleete) |

### Naming Strategies

```python
# In vehicle.json "autoname" field:
"autoname": "format:VEH-{####}"    # VEH-0001, VEH-0002, ...
"autoname": "field:vehicle_number"  # Use a field value
"autoname": "hash"                   # Random hash
"autoname": "naming_series:"        # Configurable series
```

### Controller Lifecycle Hooks

Every DocType controller (Python class) inherits from `frappe.model.document.Document` and can override these methods:

```python
class Vehicle(Document):
    def before_naming(self):      # Before name is assigned
    def validate(self):           # Before save (mandatory checks)
    def before_save(self):        # After validate, before DB write
    def after_insert(self):       # After first insert
    def on_update(self):          # After every save
    def on_submit(self):          # After Submit (submittable only)
    def on_cancel(self):          # After Cancel
    def on_trash(self):           # Before delete
    def after_delete(self):       # After delete
```

### Document Flow in Rent Pro

```
Reservation (Draft)
    ↓ Submit
Reservation (Confirmed)
    ↓ Link
Rental Contract (Draft)
    ↓ Submit
Rental Contract (Active) ──→ Sales Invoice (Draft)
                                ↓ Submit
                           Sales Invoice (Paid)
```

---

## 3. Workspaces

### What Is a Workspace?

A Workspace is a customizable Desk page that groups links, shortcuts, charts, and reports for a module. It is the user's primary navigation within a module.

### Workspace Structure

Each module in Rent Pro gets a Workspace:

| Module | Workspace |
|--------|-----------|
| Vehicles | Fleet Management dashboard with vehicle list, categories, maintenance |
| Reservations | Calendar view, reservation list, availability overview |
| Contracts | Active contracts, pending approvals, renewal alerts |
| Finance | Invoices, payments, TVA reports, reconciliation |
| OCR | Document scanning queue, OCR results |
| GeoFleete | Live map, geofence alerts, route history |
| Reports | All report links organized by category |
| Dashboard | Executive KPIs, charts, number cards |
| SaaS | Agency management, subscription plans |

### Workspace Components

| Component | Purpose |
|-----------|---------|
| **Shortcuts** | Quick links to frequently used DocTypes |
| **Charts** | Dashboard charts embedded in workspace |
| **Number Cards** | KPI tiles (e.g., "Active Vehicles: 42") |
| **Custom HTML** | Static content blocks |
| **Cards** | Grouped links with icons |

### Rent Pro Workspace Configuration

Workspaces are defined as JSON in:

```
rentpro/vehicles/workspace/vehicles/
├── vehicles.json         # Workspace definition
```

They can also be customized from the Desk UI and exported as fixtures.

---

## 4. Print Formats

### What Is a Print Format?

A Print Format defines how a document is rendered for printing or PDF generation. Frappe supports multiple format types.

### Print Format Types

| Type | Description | Use in Rent Pro |
|------|-------------|-----------------|
| **Standard** | Auto-generated from DocType fields | Quick preview of any document |
| **Custom** | Built with HTML/Jinja templates | Contract, Invoice, Reservation confirmation |
| **Letter Head** | Branded header/footer | All official documents |

### Print Format Structure

Print Formats use Jinja templating:

```
rentpro/contracts/template/
├── rental_contract.html    # Jinja template for contract PDF
```

```html
<!-- rental_contract.html -->
<div class="contract">
    <h1>{{ doc.customer_name }}</h1>
    <p>Vehicle: {{ doc.vehicle_name }}</p>
    <p>Period: {{ frappe.format_date(doc.start_date) }} → {{ frappe.format_date(doc.end_date) }}</p>
    <table>
        {% for item in doc.items %}
        <tr>
            <td>{{ item.description }}</td>
            <td>{{ frappe.format_currency(item.amount, doc.currency) }}</td>
        </tr>
        {% endfor %}
    </table>
    <p><strong>TVA:</strong> {{ doc.tva_amount }}</p>
    <p><strong>Total:</strong> {{ frappe.format_currency(doc.grand_total, doc.currency) }}</p>
</div>
```

### Print Format Features

| Feature | Description |
|---------|-------------|
| **Attach PDF** | Auto-attach PDF to email |
| **Letter Head** | Company logo, address, footer |
| **Multi-language** | Jinja `{{ _("Vehicle") }}` for translated labels |
| **Custom Scripts** | Run JS to modify print layout dynamically |
| **HTML Field** | Store HTML directly in a field, rendered in print |

### Rent Pro Print Formats Needed

| Document | Language | Notes |
|----------|----------|-------|
| Rental Contract | FR / AR / EN | Multi-page, signature blocks |
| Sales Invoice | FR / AR / EN | Moroccan TVA breakdown required |
| Reservation Confirmation | FR / EN | Single page |
| Vehicle Condition Report | FR / EN | Pre/post rental checklist |
| CIN/Document Scan | — | OCR results in printable format |

---

## 5. APIs

### Frappe API Layers

Frappe provides multiple API layers for different use cases:

### 5.1 REST API (Auto-generated)

Every DocType automatically gets CRUD endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/resource/Vehicle` | List vehicles |
| GET | `/api/resource/Vehicle/VEH-0001` | Get single vehicle |
| POST | `/api/resource/Vehicle` | Create vehicle |
| PUT | `/api/resource/Vehicle/VEH-0001` | Update vehicle |
| DELETE | `/api/resource/Vehicle/VEH-0001` | Delete vehicle |

### 5.2 Whitelisted Methods (Custom APIs)

Decorate Python functions with `@frappe.whitelist()` to expose custom endpoints:

```python
# In rentpro/vehicles/api.py
@frappe.whitelist()
def get_available_vehicles(from_date, to_date, category=None):
    """API: /api/method/rentpro.vehicles.api.get_available_vehicles"""
    # Business logic here
    return available_vehicles

@frappe.whitelist(allow_guest=True)
def public_vehicle_search(category):
    """Public endpoint - no login required"""
    pass
```

**Endpoint format:** `/api/method/{dotted.module.path}`

### 5.3 RPC via `frappe.call` (Client → Server)

```javascript
// In vehicle.js
frappe.call({
    method: "rentpro.vehicles.api.get_available_vehicles",
    args: { from_date: "2026-01-01", to_date: "2026-01-31" },
    callback: function(r) {
        console.log(r.message);
    }
});
```

### 5.4 Client API (Frappe JS SDK)

```javascript
// Document operations
let doc = frappe.get_doc("Vehicle", "VEH-0001");
frappe.call({
    method: "frappe.client.get_value",
    args: { doctype: "Vehicle", filters: {name: "VEH-0001"}, fieldname: "status" }
});
```

### 5.5 Webhook Integration

Configure webhooks via the Desk UI to call external APIs on document events:

| Event | Webhook Target | Use Case |
|-------|----------------|----------|
| `on_submit` (Rental Contract) | SMS Gateway | Send contract confirmation |
| `on_update` (GPS Position) | GeoFleete Alert Engine | Geofence breach check |
| `after_insert` (OCR Document) | OCR Service | Trigger document processing |

### 5.6 Scheduler API

```python
# In hooks.py
scheduler_events = {
    "daily": ["rentpro.finance.tasks.recurring_invoices"],
    "hourly": ["rentpro.geofleete.tasks.cleanup_old_positions"],
}
```

### Authentication

| Method | Header | Use Case |
|--------|--------|----------|
| Token Auth | `Authorization: token api_key:api_secret` | Server-to-server |
| Session Auth | Cookie-based (`sid`) | Browser / Desk |
| Basic Auth | `Authorization: Basic base64(user:pass)` | Legacy |

---

## 6. Hooks

### What Are Hooks?

Hooks are Frappe's primary extension mechanism. They allow a custom app to override or extend core framework behavior **without modifying core files**. Defined in `hooks.py`.

### How Hooks Resolve

- **Extending behavior**: All apps' hooks are collected (appended)
- **Overriding behavior**: "Last writer wins" — last installed app takes priority
- Priority order can be changed via **Installed Applications** page

### Key Hooks for Rent Pro

#### App Metadata

```python
app_name = "rentpro"
app_title = "Rent Pro"
app_publisher = "Your Company"
app_version = "0.1.0"
required_apps = ["erpnext"]
```

#### Asset Injection

```python
app_include_js = [
    "assets/js/rentpro.min.js",
    "assets/js/vehicles.js",
    "assets/js/geofleete.js",
]
app_include_css = "assets/css/rentpro.css"
```

#### Document Events

```python
doc_events = {
    "Vehicle": {
        "validate": "rentpro.vehicles.events.validate_vehicle",
        "on_update": "rentpro.vehicles.events.on_vehicle_update",
    },
    "Rental Contract": {
        "on_submit": "rentpro.contracts.events.on_contract_submit",
        "on_cancel": "rentpro.contracts.events.on_contract_cancel",
    },
    "*": {
        "after_insert": "rentpro.core.events.log_creation",
    }
}
```

#### Scheduled Jobs

```python
scheduler_events = {
    "daily": [
        "rentpro.finance.tasks.send_payment_reminders",
        "rentpro.contracts.tasks.check_expiring_contracts",
    ],
    "hourly": [
        "rentpro.geofleete.tasks.cleanup_old_positions",
    ],
    "cron": {
        "0 8 * * 1": ["rentpro.reports.tasks.weekly_fleet_report"],
    }
}
```

#### Override Whitelisted Methods

```python
override_whitelisted_methods = {
    "erpnext.controllers.queries.get_query": "rentpro.overrides.custom_query",
}
```

#### Extend DocType Class (v16+)

```python
extend_doctype_class = {
    "Address": ["rentpro.extensions.rental_address.AddressMixin"],
}
```

#### Fixtures (Data Sync)

```python
fixtures = [
    {"dt": "TVA Rate", "filters": [["name", "in", ["20%", "14%", "10%", "7%"]]]},
    {"dt": "Role", "filters": [["role_name", "like", "Rent Pro%"]]},
]
```

#### Permissions

```python
permission_query_conditions = {
    "Vehicle": "rentpro.vehicles.permissions.vehicle_permissions",
    "Rental Contract": "rentpro.contracts.permissions.contract_permissions",
}

has_permission = {
    "Rental Contract": "rentpro.contracts.permissions.contract_has_permission",
}
```

#### Install/Uninstall

```python
before_install = "rentpro.setup.install.before_install"
after_install = "rentpro.setup.install.after_install"
before_uninstall = "rentpro.setup.uninstall.before_uninstall"
```

#### Migration

```python
before_migrate = "rentpro.migrate.before_migrate"
after_migrate = "rentpro.migrate.after_migrate"
```

#### Session

```python
on_login = "rentpro.auth.on_login"
on_logout = "rentpro.auth.on_logout"
```

### Complete Hooks Reference

| Category | Key Hooks |
|----------|-----------|
| **Assets** | `app_include_js`, `app_include_css`, `web_include_js` |
| **Documents** | `doc_events`, `has_permission`, `permission_query_conditions` |
| **Override** | `override_whitelisted_methods`, `override_doctype_class`, `extend_doctype_class` |
| **Scheduler** | `scheduler_events` (hourly, daily, weekly, cron) |
| **Lifecycle** | `before_install`, `after_install`, `before_migrate`, `after_migrate` |
| **Session** | `on_login`, `on_logout`, `on_session_creation` |
| **Fixtures** | `fixtures` |
| **Website** | `website_route_rules`, `portal_menu_items`, `homepage` |
| **Boot** | `extend_bootinfo` |
| **Jinja** | `jinja.methods`, `jinja.filters` |

---

## 7. Permissions

### Permission Model

Frappe uses a **role-based access control (RBAC)** system with multiple layers:

### Layer 1: Role Assignment

Users are assigned roles. Rent Pro will define custom roles:

| Role | Description |
|------|-------------|
| `Rent Pro Manager` | Full access to all modules |
| `Rent Pro User` | Day-to-day operations (reservations, contracts) |
| `Rent Pro Fleet Manager` | Vehicle management and GeoFleete |
| `Rent Pro Finance` | Invoices, payments, TVA |
| `Rent Pro OCR Operator` | Document scanning and verification |
| `Rent Pro Read Only` | View-only access |

### Layer 2: DocType Permissions

Each DocType defines per-role permissions:

| Permission | Effect |
|------------|--------|
| `read` | Can view document |
| `write` | Can edit document |
| `create` | Can create new documents |
| `delete` | Can delete documents |
| `submit` | Can submit (submittable DocTypes) |
| `cancel` | Can cancel submitted documents |
| `amend` | Can amend cancelled documents |
| `report` | Can view in reports |
| `export` | Can export data |

### Layer 3: User Permissions (Record-Level)

Restrict access to specific records:

```python
# A fleet manager can only see vehicles in their agency
user_permissions = {
    "Vehicle": {
        "agency": "User Agency"  # User can only see vehicles where vehicle.agency matches their agency
    }
}
```

### Layer 4: Permission Query Conditions

Custom SQL WHERE clauses injected into list queries:

```python
# hooks.py
permission_query_conditions = {
    "Vehicle": "rentpro.vehicles.permissions.vehicle_query"
}

# rentpro/vehicles/permissions.py
def vehicle_query(user):
    if "Rent Pro Manager" in frappe.get_roles(user):
        return None  # No restriction — sees all vehicles
    agencies = get_user_agencies(user)
    if agencies:
        agency_list = ", ".join([f"'{a}'" for a in agencies])
        return f"`tabVehicle`.agency IN ({agency_list})"
    return "`tabVehicle`.owner = {}".format(frappe.db.escape(user))
```

### Layer 5: Has Permission Hook

Per-document permission check:

```python
# hooks.py
has_permission = {
    "Rental Contract": "rentpro.contracts.permissions.contract_permission"
}

# rentpro/contracts/permissions.py
def contract_permission(doc, user=None, permission_type=None):
    if permission_type == "read" and doc.status == "Active":
        return True  # Anyone can read active contracts
    if permission_type == "write" and doc.owner == user:
        return True  # Owner can edit
    return False
```

### Permission Priority

```
DocType Permissions (role-based)
    ↓ filtered by
User Permissions (record-level)
    ↓ filtered by
Permission Query Conditions (SQL WHERE)
    ↓ filtered by
Has Permission Hook (per-document)
```

### Multi-Tenant Permissions for Rent Pro

In SaaS mode, each agency must only see their own data. Strategy:

1. **User Permissions** on `agency` field across all DocTypes
2. **Permission Query Conditions** to enforce agency isolation at query level
3. **Has Permission Hook** for document-level checks
4. **Frappe Cloud site isolation** provides the ultimate data boundary

---

## 8. Multi-Tenancy Considerations

### Frappe Multi-Tenancy Architecture

Frappe is multi-tenant **by design**. The hierarchy:

```
Server → Bench → Site → User
```

| Layer | What It Is | Isolation |
|-------|-----------|-----------|
| **Server** | Physical/virtual machine | Hardware-level |
| **Bench** | Python env + app source + config | Shared code, isolated sites |
| **Site** | One tenant = one site | **Complete isolation**: own DB, files, users, config |

### Site Isolation Model

Each site has:

| Resource | Isolation |
|----------|-----------|
| Database | Own MariaDB/PostgreSQL database (`site_XXXXXXX`) |
| Files | Own `sites/<site>/public/files/` and `private/files/` |
| Config | Own `site_config.json` |
| Users | Own user base |
| Apps | Can install different app versions |

### URL Routing

Nginx routes by hostname:

```
agency1.rentpro.ma  → site "agency1"
agency2.rentpro.ma  → site "agency2"
```

Frappe reads the `Host` header to determine which site to load.

### Multi-Tenancy Options for Rent Pro

#### Option A: Site-Per-Tenant (Recommended)

| Aspect | Detail |
|--------|--------|
| **How** | Each agency gets its own Frappe site |
| **Isolation** | Complete — separate database, files, users |
| **Scaling** | Add sites on same bench; split benches as needed |
| **Cost** | Higher per-tenant (each site uses resources) |
| **Security** | Strongest — no cross-tenant data leakage possible |
| **Frappe Cloud** | Native support |

**Onboarding flow:**

```bash
bench new-site agency1.rentpro.ma --mariadb-root-password xxx
bench --site agency1.rentpro.ma install-app rentpro
bench --site agency1.rentpro.ma migrate
bench --site agency1.rentpro.ma execute rentpro.scripts.setup.setup_agency
```

#### Option B: Shared-Database with Row-Level Isolation

| Aspect | Detail |
|--------|--------|
| **How** | Single site, `agency` field on all DocTypes |
| **Isolation** | Application-level (permission query conditions) |
| **Scaling** | Simpler but requires careful permission engineering |
| **Cost** | Lower per-tenant |
| **Risk** | Higher — permission bugs could leak data |

**Not recommended** for production SaaS due to data leakage risk.

### Hybrid Approach (Recommended)

| Phase | Strategy |
|-------|----------|
| **MVP / Single Agency** | Single site, `agency` field for future-proofing |
| **SaaS Launch** | Site-per-tenant on Frappe Cloud |
| **Admin Portal** | Separate site for cross-agency administration |

### SaaS Module Considerations

| Feature | Implementation |
|---------|----------------|
| **Agency Onboarding** | Script to create site, install app, seed data |
| **Subscription Billing** | Custom DocType tracking plan, usage, billing |
| **Cross-Agency Reports** | Background job iterating over all sites |
| **Data Migration** | CSV/Excel import tools per module |
| **Branding** | Per-site logo, colors, letter head via fixtures |
| **Feature Flags** | Single DocType controlling module visibility per agency |

### Performance at Scale (1,000+ Agencies)

| Concern | Mitigation |
|---------|------------|
| **Database** | MariaDB connection pooling; separate DB server per bench |
| **File Storage** | Frappe Cloud CDN; migrate to S3-compatible storage |
| **Background Jobs** | Redis Queue with dedicated workers; rate limiting per site |
| **Caching** | Redis cache for frequently accessed data |
| **Monitoring** | Per-site metrics; alerting on resource usage |
| **Backups** | Automated daily backups per site; tested restore procedure |

---

## Appendix: Rent Pro Module → Frappe Feature Mapping

| Rent Pro Module | Frappe Features Used |
|-----------------|---------------------|
| **Vehicles** | DocType (Document), Workspace, Print Format, REST API |
| **Reservations** | DocType (Document), Calendar View, Workflow, Doc Events |
| **Contracts** | DocType (Submittable), Print Format (PDF), Jinja Templates |
| **OCR** | DocType, Whitelisted API, Background Jobs, File Handling |
| **Finance** | DocType (Submittable), Custom Report, Print Format, Scheduler |
| **GeoFleete** | DocType (Virtual + Document), Webhook, REST API, Scheduler |
| **Reports** | Script Report, Query Report, Dashboard Chart, Number Card |
| **Dashboard** | Page, Dashboard Chart, Number Card, Workspace |
| **SaaS** | Single DocType, Fixtures, Site Management API, Custom Auth |
