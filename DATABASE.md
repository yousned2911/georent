# Rent Pro — Database Design

All entities follow Frappe DocType conventions. Table names are prefixed with `tab` in MariaDB. Primary keys are auto-generated names (`VEH-0001`, `RSV-0001`, etc.).

ERPNext core entities (`Customer`, `Employee`, `Sales Invoice`, `Payment Entry`) are **extended**, not replaced. Custom fields are added via the `customise` mechanism or fixtures.

---

## 1. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           RENT PRO — ENTITY RELATIONSHIP DIAGRAM                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  Agency (SaaS)   │
                              │  AGEN-XXXX       │
                              └────────┬─────────┘
                                       │ 1:N
                    ┌──────────────────┼──────────────────┐
                    │                  │                   │
                    ▼                  ▼                   ▼
          ┌──────────────┐   ┌────────────────┐   ┌──────────────┐
          │  TVA Rate    │   │ Geofence Zone  │   │  Employee    │
          │  (Fixture)   │   │  GZF-XXXX      │   │  Extension   │
          └──────────────┘   └───────┬────────┘   └──────────────┘
                                     │ 1:N
                                     ▼
┌──────────────┐        ┌────────────────────┐       ┌──────────────────┐
│  Vehicle     │  1:N   │  Geofence Alert    │  N:1  │  Customer        │
│  Category    │◄───────│  GZA-XXXX          │──────►│  Extension       │
│  VCAT-XXXX   │        └────────────────────┘       │  (extends ERPNext │
└──────┬───────┘                                     │   Customer)      │
       │ 1:N                                         └────────┬─────────┘
       ▼                                                      │
┌──────────────────────┐     N:1          ┌───────────────────┤
│  Vehicle             │◄─────────────────┤                   │
│  VEH-XXXX            │                  │                   │
│                      │     N:1          │                   │
│  ┌────────────────┐  │──────────────────┼──────┐            │
│  │ Vehicle Document│  │                  │      │            │
│  │ (Child Table)  │  │                  │      │            │
│  └────────────────┘  │                  │      │            │
└──────┬───────────────┘                  │      │            │
       │                                  │      │            │
       │ 1:N                              │      │            │
       ▼                                  │      │            │
┌──────────────────────┐   N:1            │      │            │
│  Maintenance Record  │◄─────────────────┘      │            │
│  MNT-XXXX            │                         │            │
└──────────────────────┘                         │            │
                                                 │            │
       ┌─────────────────────────────────────────┘            │
       │ N:1                                                  │
       ▼                                                      │
┌──────────────────────┐    N:1     ┌──────────────────────┐  │
│  Reservation         │◄───────────│  (Customer Ext.)     │  │
│  RSV-XXXX            │            └──────────────────────┘  │
│                      │                                      │
│  ┌────────────────┐  │    N:1     ┌──────────────────────┐  │
│  │ Reservation     │◄────────────│  (Vehicle)            │  │
│  │  Item (Child)   │             └──────────────────────┘  │
│  └────────────────┘                                        │
└──────┬───────────────┘                                     │
       │ 1:1 (from reservation)                              │
       ▼                                                      │
┌──────────────────────┐            ┌──────────────────────┐  │
│  Rental Contract     │◄───────────│  (Customer Ext.)     │──┘
│  CON-XXXX            │   N:1      └──────────────────────┘
│  [SUBMITTABLE]       │
│                      │   N:1     ┌──────────────────────┐
│  ┌────────────────┐  │◄──────────│  (Vehicle)            │
│  │ Contract Item   │  │           └──────────────────────┘
│  │ (Child Table)   │  │
│  └────────────────┘  │   1:N     ┌──────────────────────┐
│                      │──────────►│  OCR Result           │
│  ┌────────────────┐  │           │  OCR-XXXX             │
│  │ Contract       │  │           │                       │
│  │  Amendment     │  │           │  ┌─────────────────┐  │
│  │ (Child Table)  │  │           │  │ OCR Extracted   │  │
│  └────────────────┘  │           │  │ Field (Child)   │  │
└──────┬───────────────┘           │  └─────────────────┘  │
       │                           └───────────────────────┘
       │ 1:N
       ▼
┌──────────────────────┐
│  GPS Position        │
│  GPSP-XXXX           │
│  (or Virtual)        │
└──────────────────────┘
```

### Relationship Summary

```
Agency ──────1:N──────► Vehicle
Agency ──────1:N──────► Reservation
Agency ──────1:N──────► Rental Contract
Agency ──────1:N──────► OCR Result
Agency ──────1:N──────► Maintenance Record
Agency ──────1:N──────► GPS Position
Agency ──────1:N──────► Geofence Zone
Agency ──────1:N──────► Geofence Alert

Vehicle Category ──1:N──► Vehicle
Vehicle ──────1:N──────► Vehicle Document (Child)
Vehicle ──────1:N──────► Reservation
Vehicle ──────1:N──────► Rental Contract
Vehicle ──────1:N──────► Maintenance Record
Vehicle ──────1:N──────► GPS Position
Vehicle ──────1:N──────► Geofence Alert

Customer Extension ──1:N──► Reservation
Customer Extension ──1:N──► Rental Contract
Customer Extension ──1:N──► OCR Result

Reservation ──────1:1────► Rental Contract
Rental Contract ──1:N──► Contract Item (Child)
Rental Contract ──1:N──► Contract Amendment (Child)
Rental Contract ──1:N──► OCR Result

Geofence Zone ──1:N──► Geofence Alert

TVA Rate ──(referenced by)──► Rental Contract, Contract Item
```

---

## 2. Field Definitions

### 2.1 Agency (SaaS Tenancy)

**DocType:** `Agency` | **Type:** Document | **Module:** SaaS

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `agency_name` | Data | — | Yes | Legal name of the agency |
| `agency_code` | Data | Unique | Yes | Short code (e.g., `AGCAS`) |
| `domain` | Data | — | No | Subdomain for SaaS (`agency.rentpro.ma`) |
| `contact_person` | Data | — | Yes | Primary contact name |
| `email` | Data | Email | Yes | Agency email |
| `phone` | Phone | — | Yes | Primary phone |
| `address` | Small Text | — | No | Full address |
| `city` | Data | — | No | City |
| `license_number` | Data | — | Yes | Moroccan business license |
| `subscription_plan` | Select | `Basic`, `Professional`, `Enterprise` | Yes | Active plan |
| `is_active` | Check | — | Yes | Default: 1 |
| `max_vehicles` | Int | — | No | Plan vehicle limit |
| `default_currency` | Link | `Currency` | Yes | Default: `MAD` |
| `default_tva_rate` | Link | `TVA Rate` | Yes | Default TVA rate |
| `logo` | Attach Image | — | No | Agency logo for documents |

**Naming:** `autoname: "format:AGC-{####}"`

---

### 2.2 TVA Rate (Configuration Fixture)

**DocType:** `TVA Rate` | **Type:** Document | **Module:** Finance

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `rate_name` | Data | — | Yes | Display name (`20% TVA`) |
| `percentage` | Percent | — | Yes | Numeric rate (20, 14, 10, 7) |
| `is_active` | Check | — | Yes | Default: 1 |
| `description` | Small Text | — | No | When this rate applies |

**Naming:** `autoname: "field:rate_name"` → `20%`, `14%`, `10%`, `7%`

**Fixtures:** Exported via `bench export-fixtures` so all sites get the 4 standard Moroccan rates.

---

### 2.3 Vehicle Category

**DocType:** `Vehicle Category` | **Type:** Document | **Module:** Vehicles

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `category_name` | Data | — | Yes | e.g., Economy, SUV, Luxury, Van |
| `description` | Small Text | — | No | Category description |
| `daily_rate_multiplier` | Float | — | Yes | Default: 1.0. Multiplied by base rate |
| `security_deposit` | Currency | `MAD` | Yes | Default deposit for this category |
| `is_active` | Check | — | Yes | Default: 1 |

**Naming:** `autoname: "field:category_name"` → `Economy`, `SUV`, `Luxury`

---

### 2.4 Vehicle

**DocType:** `Vehicle` | **Type:** Document | **Module:** Rent Pro

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `plate_number` | Data | Unique | Yes | License plate (`12345-A-12`) |
| `vin` | Data | Unique | Yes | Vehicle Identification Number (17 chars) |
| `make` | Data | — | Yes | Manufacturer (`Renault`, `Peugeot`) |
| `model` | Data | — | Yes | Model name (`Clio`, `208`) |
| `year` | Int | — | Yes | Manufacturing year (≤ current year) |
| `color` | Data | — | Yes | Exterior color |
| `category` | Link | `Vehicle Category` | Yes | FK → Vehicle Category |
| `status` | Select | `Available`, `Reserved`, `Rented`, `Maintenance`, `Sold`, `Inactive` | Yes | Current status (default: Available) |
| `current_mileage` | Int | — | Yes | Current odometer (km, ≥ 0) |
| `fuel_type` | Select | `Petrol`, `Diesel`, `Electric`, `Hybrid` | Yes | Fuel type |
| `transmission` | Select | `Manual`, `Automatic` | Yes | Transmission type |
| `seats` | Int | — | Yes | Number of seats |
| `agency` | Link | `Agency` | No | Owning agency (SaaS tenant) |
| `daily_rate` | Currency | — | Yes | Base daily rental rate (≥ 0) |
| `weekly_rate` | Currency | — | No | Weekly rental rate |
| `monthly_rate` | Currency | — | No | Monthly rental rate |
| `deposit_amount` | Currency | — | No | Security deposit required |
| `insurance_expiry` | Date | — | Yes | Insurance expiration date (≥ today) |
| `technical_inspection_expiry` | Date | — | Yes | Technical inspection expiry (≥ today) |
| `registration_expiry` | Date | — | Yes | Registration card expiry (≥ today) |
| `active` | Check | — | Yes | Default: 1 |
| `notes` | Small Text | — | No | Internal notes |

**Naming:** `autoname: "format:VEH-{####}"`

**Status Transitions:**

```
Available ──► Reserved
Available ──► Maintenance
Available ──► Sold
Available ──► Inactive
Reserved ──► Rented
Reserved ──► Available
Reserved ──► Maintenance
Reserved ──► Sold
Reserved ──► Inactive
Rented ──► Available
Rented ──► Maintenance
Rented ──► Sold
Rented ──► Inactive
Maintenance ──► Available
Maintenance ──► Sold
Maintenance ──► Inactive
Sold ──► (terminal)
Inactive ──► Available
```

**Validations:**
- Year cannot exceed current year
- Daily rate must be non-negative
- Mileage cannot be negative
- Expiry dates cannot be before today
- Status transitions are enforced

---

### 2.5 Vehicle Document (Child Table)

**DocType:** `Vehicle Document` | **Type:** Child Table | **Module:** Vehicles

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `document_type` | Select | `Insurance`, `Registration`, `Technical Inspection`, `Ownership Certificate`, `Other` | Yes | Type of document |
| `document_number` | Data | — | Yes | Document reference number |
| `issue_date` | Date | — | Yes | Date of issue |
| `expiry_date` | Date | — | Yes | Expiration date |
| `issuing_authority` | Data | — | No | Issuing body |
| `attachment` | Attach | — | Yes | Scanned copy |
| `is_valid` | Check | — | Yes | Default: 1. Set to 0 on expiry |

**Parent:** `Vehicle` (Table field `documents`)

---

### 2.6 Customer Extension

**DocType:** `Customer Extension` | **Type:** Document | **Module:** Vehicles

This extends ERPNext's `Customer` DocType. It adds rental-specific fields via a linked DocType (not modifying ERPNext core).

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `customer` | Link | `Customer` | Yes | FK → ERPNext Customer (unique) |
| `cin_number` | Data | — | Yes | Moroccan national ID number |
| `cin_expiry` | Date | — | Yes | CIN expiration date |
| `cin_image` | Attach | — | Yes | Scanned CIN |
| `driver_license_number` | Data | — | Yes | Driver license number |
| `driver_license_expiry` | Date | — | Yes | License expiration date |
| `driver_license_category` | Check | — | No | `A`, `B`, `C`, `D` (multi) |
| `driver_license_image` | Attach | — | Yes | Scanned license |
| `nationality` | Link | `Country` | Yes | Nationality |
| `phone_secondary` | Phone | — | No | Secondary phone |
| `address_line_2` | Data | — | No | Additional address line |
| `city` | Data | — | Yes | City of residence |
| `postal_code` | Data | — | No | Postal code |
| `emergency_contact_name` | Data | — | No | Emergency contact |
| `emergency_contact_phone` | Phone | — | No | Emergency phone |
| `agency` | Link | `Agency` | Yes | Registering agency |

**Naming:** `autoname: "format:CUSTX-{####}"`

---

### 2.7 Employee Extension

**DocType:** `Employee Extension` | **Type:** Document | **Module:** Vehicles

Extends ERPNext's `Employee` with agency-specific operational fields.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `employee` | Link | `Employee` | Yes | FK → ERPNext Employee (unique) |
| `agency` | Link | `Agency` | Yes | Assigned agency |
| `agency_role` | Select | `Manager`, `Agent`, `Fleet Supervisor`, `Mechanic`, `Accountant` | Yes | Role within agency |
| `can_manage_vehicles` | Check | — | Yes | Default: 0 |
| `can_create_contracts` | Check | — | Yes | Default: 0 |
| `can_process_payments` | Check | — | Yes | Default: 0 |
| `can_scan_documents` | Check | — | Yes | Default: 0 |
| `can_view_reports` | Check | — | Yes | Default: 0 |
| `max_discount_percent` | Percent | — | No | Max discount this employee can grant |
| `pin_code` | Password | — | No | 4-digit PIN for terminal operations |

**Naming:** `autoname: "format:EMPX-{####}"`

---

### 2.8 Reservation

**DocType:** `Reservation` | **Type:** Document | **Module:** Reservations

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `reservation_number` | Data | Unique, Read Only | No | Auto-named `RES-{#####}` |
| `customer` | Link | `Customer` | Yes | FK → ERPNext Customer |
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `agency` | Link | `Agency` | No | Owning agency |
| `reservation_date` | Date | — | Yes | Date reservation was created (auto-set) |
| `pickup_date` | Date | — | Yes | Scheduled pickup date (≥ today) |
| `expected_return_date` | Date | — | Yes | Expected return date (> pickup_date) |
| `daily_rate` | Currency | `MAD` | No | Rate locked at reservation time |
| `number_of_days` | Int | Read Only | No | Auto-calculated: `expected_return_date - pickup_date` |
| `discount` | Currency | `MAD` | No | Discount amount |
| `deposit_amount` | Currency | `MAD` | No | Security deposit (must ≤ estimated_total) |
| `estimated_total` | Currency | `MAD` | Read Only | `daily_rate × number_of_days - discount` |
| `status` | Select | `Draft`, `Confirmed`, `Picked Up`, `Completed`, `Cancelled`, `No Show` | Yes | Workflow state (default: Draft) |
| `notes` | Small Text | — | No | Internal notes |
| `created_by` | Data | Read Only | No | Auto-set to session user |
| `active` | Check | Read Only | No | Default: 1 |

**Naming:** `autoname: "format:RES-{#####}"`

**Status Workflow:**

```
Draft ──(confirm)──► Confirmed ──(pick up)──► Picked Up ──(return)──► Completed
Draft ──(cancel)──► Cancelled
Confirmed ──(cancel)──► Cancelled
Confirmed ──(no show)──► No Show
```

**Validation Rules:**
- Vehicle must exist
- Customer must exist
- Pickup date cannot be before today
- Expected return date must be after pickup date
- Deposit cannot exceed estimated total
- No overlapping Confirmed/Picked Up reservations for the same vehicle
- Reservation cannot be edited once Completed/Cancelled/No Show

**Vehicle Status Integration:**
- Confirmed → Vehicle status set to Reserved
- Picked Up → Vehicle status set to Rented
- Completed → Vehicle status set to Available
- Cancelled → Vehicle status set to Available
- No Show → Vehicle status set to Available

---

### 2.9 Reservation Item (Child Table)

**DocType:** `Reservation Item` | **Type:** Child Table | **Module:** Reservations

Optional add-ons or services bundled with a reservation. (Not yet implemented)

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `item_description` | Data | — | Yes | e.g., "GPS Navigator", "Child Seat" |
| `item_type` | Select | `Accessory`, `Insurance`, `Service`, `Other` | Yes | Item category |
| `daily_rate` | Currency | `MAD` | Yes | Daily cost of this add-on |
| `quantity` | Int | — | Yes | Default: 1 |
| `total_amount` | Currency | `MAD` | Read Only | Yes | `daily_rate × quantity × days` |

**Parent:** `Reservation` (Table field `items`)

---

### 2.10 Rental Contract

**DocType:** `Rental Contract` | **Type:** Document | **Module:** Contracts

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `contract_number` | Data | Unique, Read Only | No | Auto-named `CON-{#####}` |
| `reservation` | Link | `Reservation` | No | FK → Reservation (if created from one) |
| `customer` | Link | `Customer` | Yes | FK → ERPNext Customer |
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `agency` | Link | `Agency` | No | Owning agency |
| `contract_date` | Date | — | Yes | Date contract is signed |
| `pickup_datetime` | Datetime | — | No | Scheduled pickup date & time |
| `expected_return_datetime` | Datetime | — | No | Expected return date & time |
| `actual_return_datetime` | Datetime | — | No | Filled on return |
| `pickup_mileage` | Int | — | No | Odometer at pickup (km) |
| `pickup_fuel_level` | Int | — | No | Fuel at pickup (0-100%) |
| `pickup_notes` | Small Text | — | No | Vehicle condition at pickup |
| `return_mileage` | Int | — | No | Odometer at return (km, ≥ pickup) |
| `return_fuel_level` | Int | — | No | Fuel at return (0-100%) |
| `return_notes` | Small Text | — | No | Vehicle condition at return |
| `daily_rate` | Currency | `MAD` | No | Locked daily rate |
| `number_of_days` | Int | Read Only | No | `expected_return - pickup` |
| `subtotal` | Currency | `MAD` | Read Only | `daily_rate × number_of_days` |
| `discount` | Currency | `MAD` | No | Discount amount |
| `tva_rate` | Select | `20%`, `14%`, `10%`, `7%`, `0%` | Yes | Moroccan TVA rate |
| `tva_amount` | Currency | `MAD` | Read Only | `taxable × tva_rate` |
| `additional_charges` | Currency | `MAD` | No | Extra charges |
| `late_return_fee` | Currency | `MAD` | No | Penalty for late return |
| `damage_fee` | Currency | `MAD` | No | Damage charge |
| `deposit_amount` | Currency | `MAD` | No | Security deposit collected |
| `grand_total` | Currency | `MAD` | Read Only | `taxable + tva_amount` |
| `payment_status` | Select | `Unpaid`, `Partial`, `Paid`, `Refunded` | Yes | Payment tracking |
| `status` | Select | `Draft`, `Active`, `Completed`, `Cancelled` | Yes | Contract status |
| `customer_signature` | Attach | — | No | Customer signature image |
| `agency_signature` | Attach | — | No | Agency signature image |
| `attachments` | Attach | — | No | Supporting documents |
| `notes` | Small Text | — | No | Internal notes |
| `created_by` | Data | Read Only | No | Auto-set to session user |
| `active` | Check | Read Only | No | Default: 1 |

**Naming:** `autoname: "format:CON-{#####}"`

**Status Workflow:**

```
Draft ──(activate)──► Active ──(complete)──► Completed
Draft ──(cancel)──► Cancelled
Active ──(cancel)──► Cancelled
```

**TVA Calculation:**

```
Subtotal - Discount + Additional Charges + Late Fee + Damage Fee
= Taxable Amount

Taxable Amount × TVA Rate = TVA Amount
Taxable Amount + TVA Amount = Grand Total
```

**Vehicle Status Integration:**

| Contract Status | Vehicle Status |
|----------------|----------------|
| Draft | Reserved |
| Active | Rented |
| Completed | Available |
| Cancelled | Available |

**ERPNext Integration:**
- Automatically creates Sales Invoice when contract becomes Active
- Invoice linked via `rental_contract` custom field on Sales Invoice

---

### 2.11 Contract Item (Child Table)

**DocType:** `Contract Item` | **Type:** Child Table | **Module:** Contracts

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `description` | Data | — | Yes | Line item description |
| `item_type` | Select | `Rental`, `Accessory`, `Insurance`, `Service`, `Penalty`, `Discount` | Yes | Category |
| `quantity` | Int | — | Yes | Default: 1 |
| `rate` | Currency | `MAD` | Yes | Unit rate |
| `amount` | Currency | `MAD` | Read Only | Yes | `quantity × rate` |
| `tva_applicable` | Check | — | Yes | Default: 1 |
| `tva_rate` | Link | `TVA Rate` | No | FK → TVA Rate (override per line) |

**Parent:** `Rental Contract` (Table field `items`)

---

### 2.12 Contract Amendment (Child Table)

**DocType:** `Contract Amendment` | **Type:** Child Table | **Module:** Contracts

Tracks changes made to an active contract (date extensions, rate changes).

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `amendment_date` | Date | — | Yes | Date of change |
| `amendment_type` | Select | `Date Extension`, `Rate Change`, `Vehicle Swap`, `Other` | Yes | Type of change |
| `previous_value` | Small Text | — | Yes | Value before change |
| `new_value` | Small Text | — | Yes | Value after change |
| `reason` | Small Text | — | Yes | Justification |
| `approved_by` | Link | `Employee` | Yes | Authorizing employee |

**Parent:** `Rental Contract` (Table field `amendments`)

---

### 2.13 Payment Transaction

**DocType:** `Payment Transaction` | **Type:** Document | **Module:** Finance

Tracks individual cash receipts against rental contracts.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `transaction_number` | Data | Unique, Read Only | No | Auto-named `PAY-{#####}` |
| `contract` | Link | `Rental Contract` | No | FK → Rental Contract |
| `customer` | Link | `Customer` | Yes | FK → ERPNext Customer |
| `amount` | Currency | `MAD` | Yes | Must be > 0 |
| `currency` | Link | `Currency` | Yes | Default: `MAD` |
| `payment_method` | Select | `Cash`, `Credit Card`, `Bank Transfer`, `Mobile Payment`, `Payzone`, `Cash Plus`, `Check` | Yes | How payment was received |
| `transaction_date` | Date | — | Yes | Date of payment |
| `reference_number` | Data | — | No | External reference (check #, transfer ID) |
| `status` | Select | `Pending`, `Completed`, `Refunded`, `Cancelled` | Yes | Default: `Pending` |
| `notes` | Small Text | — | No | Additional details |

**Naming:** `autoname: "format:PAY-{#####}"`

**Status Workflow:**

```
Pending ──(complete)──► Completed
Pending ──(cancel)──► Cancelled
Completed ──(refund)──► Refunded
```

**Contract Integration:**
- Links to Rental Contract and updates its `payment_status` on completion/refund
- Customer must match the contract's customer (validated on save)
- Cannot edit amount after status is Completed

---

### 2.14 Expense Entry

**DocType:** `Expense Entry` | **Type:** Document | **Module:** Finance

Records fleet-related expenses (fuel, maintenance, tolls, etc.).

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `entry_number` | Data | Unique, Read Only | No | Auto-named `EXP-{#####}` |
| `expense_date` | Date | — | Yes | Date expense was incurred |
| `category` | Select | `Fuel`, `Maintenance`, `Insurance`, `Tolls`, `Parking`, `Cleaning`, `Tires`, `Battery`, `Body Work`, `Other` | Yes | Expense type |
| `vehicle` | Link | `Vehicle` | No | FK → Vehicle (optional) |
| `contract` | Link | `Rental Contract` | No | FK → Rental Contract (optional) |
| `amount` | Currency | `MAD` | Yes | Must be > 0 |
| `currency` | Link | `Currency` | Yes | Default: `MAD` |
| `vendor` | Data | — | No | Vendor/supplier name |
| `reference_number` | Data | — | No | Invoice/receipt reference |
| `status` | Select | `Draft`, `Approved`, `Rejected`, `Paid` | Yes | Default: `Draft` |
| `notes` | Small Text | — | No | Additional details |
| `attachments` | Attach | — | No | Receipt or invoice image |

**Naming:** `autoname: "format:EXP-{#####}"`

**Status Workflow:**

```
Draft ──(approve)──► Approved ──(pay)──► Paid
Draft ──(reject)──► Rejected
```

---

### 2.15 OCR Result

**DocType:** `OCR Result` | **Type:** Document | **Module:** OCR

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `document_type` | Select | `CIN`, `Driver License`, `Vehicle Registration`, `Insurance Certificate`, `Other` | Yes | Type of scanned document |
| `source_image` | Attach | — | Yes | Uploaded/scanned image |
| `processed_image` | Attach | — | No | Cleaned/enhanced version |
| `raw_text` | Long Text | — | No | Full OCR output text |
| `confidence_score` | Percent | — | No | Overall extraction confidence |
| `status` | Select | `Pending`, `Processing`, `Completed`, `Failed`, `Manual Review` | Yes | Processing state |
| `customer` | Link | `Customer` | No | FK → Customer (if matched) |
| `vehicle` | Link | `Vehicle` | No | FK → Vehicle (if registration scan) |
| `contract` | Link | `Rental Contract` | No | FK → Contract (if attached to one) |
| `extracted_cin_number` | Data | — | No | Extracted CIN |
| `extracted_name` | Data | — | No | Extracted full name |
| `extracted_license_number` | Data | — | No | Extracted license # |
| `extracted_expiry_date` | Date | — | No | Extracted expiry |
| `extracted_plate_number` | Data | — | No | Extracted plate |
| `requires_manual_review` | Check | — | Yes | Default: 0. Flag if confidence < threshold |
| `reviewed_by` | Link | `Employee` | No | Who verified the OCR result |
| `review_notes` | Small Text | — | No | Manual correction notes |
| `processing_time_ms` | Int | — | No | Time taken for OCR processing |
| `ocr_engine` | Data | — | No | Which engine was used |
| `agency` | Link | `Agency` | Yes | Owning agency |

**Naming:** `autoname: "format:OCR-{####}"`

---

### 2.16 OCR Extracted Field (Child Table)

**DocType:** `OCR Extracted Field` | **Type:** Child Table | **Module:** OCR

Stores individual extracted key-value pairs from OCR processing.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `field_label` | Data | — | Yes | e.g., "Full Name", "CIN Number" |
| `field_value` | Data | — | Yes | Extracted value |
| `confidence` | Percent | — | Yes | Per-field confidence |
| `is_valid` | Check | — | Yes | Confirmed correct? |
| `corrected_value` | Data | — | No | Manual correction if wrong |

**Parent:** `OCR Result` (Table field `extracted_fields`)

---

### 2.17 Maintenance Record

**DocType:** `Maintenance Record` | **Type:** Document | **Module:** Vehicles

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `maintenance_type` | Select | `Scheduled Service`, `Unscheduled Repair`, `Tire Change`, `Oil Change`, `Technical Inspection`, `Body Work`, `Electrical`, `Other` | Yes | Type of work |
| `priority` | Select | `Low`, `Medium`, `High`, `Critical` | Yes | Urgency |
| `description` | Text Editor | — | Yes | Detailed description of work |
| `start_date` | Date | — | Yes | Service start date |
| `end_date` | Date | — | No | Completion date (null if in progress) |
| `mileage_at_service` | Int | — | Yes | Odometer reading at service |
| `cost` | Currency | `MAD` | Yes | Total service cost |
| `service_provider` | Data | — | No | External garage / internal |
| `status` | Select | `Scheduled`, `In Progress`, `Completed`, `Cancelled` | Yes | Work status |
| `next_service_date` | Date | — | No | Next scheduled service |
| `next_service_mileage` | Int | — | No | Next mileage threshold |
| `parts_replaced` | Small Text | — | No | List of parts replaced |
| `invoice_attachment` | Attach | — | No | Service invoice scan |
| `agency` | Link | `Agency` | Yes | Owning agency |

**Naming:** `autoname: "format:MNT-{####}"`

**Status Workflow:**

```
Scheduled ──(start work)──► In Progress ──(complete)──► Completed
Scheduled ──(cancel)──► Cancelled
```

---

### 2.18 GPS Position

**DocType:** `GPS Position` | **Type:** Document | **Module:** GeoFleete

For high-frequency GPS data, this can be implemented as a **Virtual DocType** backed by an external time-series store, or as a regular DocType with background job cleanup.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `device_id` | Data | — | Yes | GPS tracker hardware ID |
| `latitude` | Float | — | Yes | Decimal degrees |
| `longitude` | Float | — | Yes | Decimal degrees |
| `altitude` | Float | — | No | Meters above sea level |
| `speed` | Float | — | No | km/h |
| `heading` | Float | — | No | Degrees (0-360) |
| `position_timestamp` | Datetime | — | Yes | When position was recorded |
| `received_timestamp` | Datetime | — | Yes | When server received it |
| `ignition_status` | Check | — | No | Engine on/off |
| `battery_level` | Percent | — | No | GPS device battery |
| `agency` | Link | `Agency` | Yes | Owning agency |

**Naming:** `autoname: "hash"` (high-volume, no sequential needed)

**Indexing:** Composite index on `(vehicle, position_timestamp)` for fast queries.

**Retention:** Background job deletes records older than 90 days (configurable).

---

### 2.19 Geofence Zone

**DocType:** `Geofence Zone` | **Type:** Document | **Module:** GeoFleete

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `zone_name` | Data | — | Yes | e.g., "Main Depot", "Airport Zone" |
| `description` | Small Text | — | No | Zone description |
| `boundary` | Geolocation | — | Yes | Polygon defining zone boundary |
| `radius` | Float | — | No | For circular zones (meters from center point) |
| `center_point` | Geolocation | — | No | For radius-based zones |
| `zone_type` | Select | `Depot`, `Customer Zone`, `Restricted`, `Speed Limit`, `Alert` | Yes | Purpose of zone |
| `speed_limit` | Int | — | No | km/h (for Speed Limit zones) |
| `is_active` | Check | — | Yes | Default: 1 |
| `notify_on_entry` | Check | — | Yes | Default: 0 |
| `notify_on_exit` | Check | — | Yes | Default: 0 |
| `notify_on_violation` | Check | — | Yes | Default: 0 |
| `agency` | Link | `Agency` | Yes | Owning agency |

**Naming:** `autoname: "format:GZF-{####}"`

---

### 2.20 Geofence Alert

**DocType:** `Geofence Alert` | **Type:** Document | **Module:** GeoFleete

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `zone` | Link | `Geofence Zone` | Yes | FK → Geofence Zone |
| `alert_type` | Select | `Entry`, `Exit`, `Speed Violation`, `Unauthorized Use`, `Prolonged Stay` | Yes | Type of alert |
| `alert_timestamp` | Datetime | — | Yes | When alert triggered |
| `latitude` | Float | — | Yes | Position at alert time |
| `longitude` | Float | — | Yes | Position at alert time |
| `speed` | Float | — | No | Speed at time of alert |
| `is_acknowledged` | Check | — | Yes | Default: 0 |
| `acknowledged_by` | Link | `Employee` | No | Who acknowledged |
| `acknowledged_at` | Datetime | — | No | When acknowledged |
| `resolution_notes` | Small Text | — | No | What was done |
| `severity` | Select | `Low`, `Medium`, `High`, `Critical` | Yes | Alert severity |
| `agency` | Link | `Agency` | Yes | Owning agency |

**Naming:** `autoname: "format:GZA-{####}"`

---

### 2.21 Rent Pro Settings (Single)

**DocType:** `Rent Pro Settings` | **Type:** Single | **Module:** SaaS

Global configuration for the Rent Pro installation.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `agency_name` | Data | — | Yes | Default agency name |
| `default_currency` | Link | `Currency` | Yes | Default: `MAD` |
| `default_tva_rate` | Link | `TVA Rate` | Yes | Default TVA rate |
| `ocr_enabled` | Check | — | Yes | Default: 1 |
| `ocr_confidence_threshold` | Percent | — | Yes | Below this → manual review. Default: 80% |
| `geofleete_enabled` | Check | — | Yes | Default: 0 |
| `gps_retention_days` | Int | — | Yes | Default: 90 |
| `reservation_overlap_check` | Check | — | Yes | Default: 1. Prevent double-booking |
| `auto_complete_contracts` | Check | — | Yes | Default: 0. Auto-complete on end_date |
| `late_fee_daily_rate` | Currency | `MAD` | No | Daily penalty for overdue returns |
| `contract_template` | Link | `Print Format` | No | Default contract print format |
| `logo` | Attach Image | — | No | Company logo for documents |
| `footer_text` | Small Text | — | No | Default footer for printed documents |

**Naming:** `autoname: "settings"` (Single DocType — always one record)

---

### 2.22 Document Record

**DocType:** `Document Record` | **Type:** Document | **Module:** OCR

Paperless document management for customer and vehicle documents.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `document_number` | Data | Unique | Yes | Auto-named `DOC-{#####}` |
| `customer` | Link | `Customer` | Yes | FK → ERPNext Customer |
| `vehicle` | Link | `Vehicle` | No | FK → Vehicle (for vehicle docs) |
| `contract` | Link | `Rental Contract` | No | FK → Rental Contract |
| `document_type` | Select | `National ID`, `Passport`, `Driver License`, `Residence Permit`, `Registration Card`, `Insurance Certificate`, `Technical Inspection`, `Ownership Document` | Yes | Document category |
| `document_name` | Data | — | Yes | Human-readable name |
| `issuing_country` | Link | `Country` | No | Country of issue |
| `issuing_authority` | Data | — | No | Authority that issued the document |
| `issue_date` | Date | — | No | When document was issued |
| `expiry_date` | Date | — | No | When document expires |
| `ocr_enabled` | Check | — | Yes | Default: 1 |
| `ocr_status` | Select | `Pending`, `Processing`, `Completed`, `Failed`, `Manual Review` | Yes | Default: `Pending` |
| `extracted_name` | Data | — | No | OCR: full name |
| `extracted_document_number` | Data | — | No | OCR: document number |
| `extracted_expiry_date` | Date | — | No | OCR: expiry date |
| `extracted_date_of_birth` | Date | — | No | OCR: date of birth |
| `extracted_license_number` | Data | — | No | OCR: license number |
| `extracted_country` | Data | — | No | OCR: country |
| `extracted_text` | Long Text | — | No | Full OCR raw text |
| `confidence_score` | Percent | — | No | OCR confidence |
| `ocr_provider` | Data | — | No | Which provider was used |
| `ocr_error` | Small Text | — | No | OCR error message (hidden) |
| `attachment` | Attach | — | Yes | Document file |
| `thumbnail` | Attach Image | — | No | Thumbnail image |
| `status` | Select | `Active`, `Expired`, `Archived` | Yes | Default: `Active` |
| `notes` | Small Text | — | No | Free-form notes |
| `uploaded_by` | Link | `User` | No | Auto-set to session user |
| `uploaded_at` | Datetime | — | No | Auto-set on creation |
| `audit_log` | Table | `Document Audit Log` | No | Audit trail entries |
| `agency` | Link | `Agency` | No | Owning agency |

**Naming:** `autoname: "format:DOC-{#####}"`

**Status Workflow:**

```
Active ──(auto on expiry)──► Expired
Active ──(archive)──► Archived
Expired ──(archive)──► Archived
Archived (terminal)
```

**Document Types:**

| Category | Types |
|----------|-------|
| Customer | National ID, Passport, Driver License, Residence Permit |
| Vehicle | Registration Card, Insurance Certificate, Technical Inspection, Ownership Document |

---

### 2.23 Document Audit Log (Child Table)

**DocType:** `Document Audit Log` | **Type:** Child Table | **Module:** OCR

Tracks all actions performed on a Document Record.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `action` | Select | `Upload`, `Modification`, `OCR Execution`, `Manual Correction`, `Download`, `Archive`, `Deletion Request`, `Status Change` | Yes | Action type |
| `detail` | Small Text | — | Yes | Description of what happened |
| `performed_by` | Link | `User` | Yes | Who performed the action |
| `performed_at` | Datetime | — | Yes | When the action occurred |

**Parent:** `Document Record` (Table field `audit_log`)

---

### 2.24 GeoFleete Settings (Single)

**DocType:** `GeoFleete Settings` | **Type:** Single | **Module:** GeoFleete

GPS fleet tracking configuration.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `geofleete_enabled` | Check | — | Yes | Default: 0 |
| `gps_provider` | Select | `Mock`, `Traccar` | Yes | Default: `Mock` |
| `mock_mode` | Check | — | Yes | Default: 1 |
| `gps_update_interval` | Int | — | Yes | Default: 30 (seconds) |
| `gps_retention_days` | Int | — | Yes | Default: 90 |
| `coming_soon_banner` | HTML | — | No | Auto-generated for external providers |
| `default_latitude` | Float | — | No | Default: 33.5731 (Casablanca) |
| `default_longitude` | Float | — | No | Default: -7.5898 |
| `simulation_speed_factor` | Float | — | No | Default: 1.0 |
| `max_fuel_consumption` | Float | — | No | Default: 0.08 (%/km) |
| `low_fuel_threshold` | Percent | — | No | Default: 15 |
| `speed_limit` | Int | — | No | Default: 120 (km/h) |
| `idle_threshold_minutes` | Int | — | No | Default: 30 |
| `low_battery_threshold` | Percent | — | No | Default: 20 |

**Naming:** `autoname: "settings"` (Single DocType)

---

### 2.25 GPS Position

**DocType:** `GPS Position` | **Type:** Document | **Module:** GeoFleete

Historical vehicle position records.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `timestamp` | Datetime | — | Yes | Position timestamp |
| `latitude` | Float | — | Yes | -90 to 90 |
| `longitude` | Float | — | Yes | -180 to 180 |
| `speed` | Float | — | No | km/h (0-300) |
| `heading` | Float | — | No | 0-360 degrees |
| `altitude` | Float | — | No | meters |
| `accuracy` | Float | — | No | meters |
| `ignition` | Check | — | Yes | Ignition state |
| `engine_running` | Check | — | Yes | Engine state |
| `fuel_level` | Percent | — | No | Fuel percentage |
| `battery_level` | Percent | — | No | Battery percentage |
| `gps_signal_strength` | Percent | — | No | GPS signal quality |
| `agency` | Link | `Agency` | No | Owning agency |
| `provider` | Data | — | No | GPS provider name |

**Naming:** `autoname: "hash"`

---

### 2.26 Geofence Zone

**DocType:** `Geofence Zone` | **Type:** Document | **Module:** GeoFleete

Geofenced area definitions.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `zone_name` | Data | — | Yes | e.g., "Main Depot" |
| `zone_type` | Select | `Depot`, `Customer Zone`, `Restricted`, `Speed Limit`, `Airport` | Yes | Zone purpose |
| `description` | Small Text | — | No | Zone description |
| `boundary_type` | Select | `Circle`, `Polygon` | Yes | Default: Circle |
| `center_latitude` | Float | — | Yes | Center point latitude |
| `center_longitude` | Float | — | Yes | Center point longitude |
| `radius` | Int | — | Yes | meters (for circles) |
| `speed_limit` | Int | — | No | Optional per-zone limit |
| `notify_on_entry` | Check | — | Yes | Default: 1 |
| `notify_on_exit` | Check | — | Yes | Default: 1 |
| `notify_on_violation` | Check | — | Yes | Default: 0 |
| `is_active` | Check | — | Yes | Default: 1 |
| `agency` | Link | `Agency` | No | Owning agency |

**Naming:** `autoname: "format:GZF-{####}"`

---

### 2.27 Geofence Alert

**DocType:** `Geofence Alert` | **Type:** Document | **Module:** GeoFleete

Geofence event records.

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle |
| `zone` | Link | `Geofence Zone` | Yes | FK → Geofence Zone |
| `alert_type` | Select | `Entry`, `Exit`, `Speed Violation`, `Unauthorized Use`, `Prolonged Stay` | Yes | Event type |
| `alert_timestamp` | Datetime | — | Yes | When alert triggered |
| `severity` | Select | `Low`, `Medium`, `High`, `Critical` | Yes | Auto-set from type |
| `latitude` | Float | — | No | Position at alert |
| `longitude` | Float | — | No | Position at alert |
| `speed` | Float | — | No | Speed at alert |
| `distance` | Float | — | No | Distance from zone (m) |
| `is_acknowledged` | Check | — | Yes | Default: 0 |
| `acknowledged_by` | Link | `User` | No | Who acknowledged |
| `acknowledged_at` | Datetime | — | No | When acknowledged |
| `resolution_notes` | Small Text | — | No | Resolution details |
| `agency` | Link | `Agency` | No | Owning agency |

**Naming:** `autoname: "format:GZA-{#####}"`

---

### 2.28 Vehicle Tracking

**DocType:** `Vehicle Tracking` | **Type:** Document | **Module:** GeoFleete

Current vehicle state snapshot (one record per vehicle).

| Field | Type | Options / Format | Required | Description |
|-------|------|-------------------|----------|-------------|
| `vehicle` | Link | `Vehicle` | Yes | FK → Vehicle (unique) |
| `status` | Select | `Online`, `Offline`, `Idle`, `Moving`, `Maintenance` | Yes | Default: Offline |
| `last_latitude` | Float | — | No | Last known latitude |
| `last_longitude` | Float | — | No | Last known longitude |
| `last_speed` | Float | — | No | Last speed (km/h) |
| `ignition` | Check | — | Yes | Ignition state |
| `fuel_level` | Percent | — | No | Current fuel level |
| `battery_level` | Percent | — | No | Current battery |
| `engine_running` | Check | — | Yes | Engine state |
| `gps_signal_strength` | Percent | — | No | GPS signal quality |
| `current_mileage` | Int | — | No | Odometer (km) |
| `last_update` | Datetime | — | No | Last telemetry update |
| `provider` | Data | — | No | GPS provider name |

**Naming:** `autoname: "field:vehicle"`

---

## 3. Relationships Detail

### 3.1 Foreign Key Relationships

| Source DocType | Field | Target DocType | Relationship | On Delete |
|----------------|-------|----------------|-------------|-----------|
| `Vehicle` | `category` | `Vehicle Category` | N:1 | Restrict |
| `Vehicle` | `agency` | `Agency` | N:1 | Cascade |
| `Vehicle Document` | (parent) | `Vehicle` | Child | Cascade |
| `Customer Extension` | `customer` | `Customer` (ERPNext) | 1:1 | Cascade |
| `Customer Extension` | `agency` | `Agency` | N:1 | Cascade |
| `Employee Extension` | `employee` | `Employee` (ERPNext) | 1:1 | Cascade |
| `Employee Extension` | `agency` | `Agency` | N:1 | Cascade |
| `Reservation` | `customer` | `Customer` (ERPNext) | N:1 | Restrict |
| `Reservation` | `vehicle` | `Vehicle` | N:1 | Restrict |
| `Reservation` | `category` | `Vehicle Category` | N:1 | Set Null |
| `Reservation` | `agency` | `Agency` | N:1 | Cascade |
| `Reservation` | `created_by_agent` | `Employee Extension` | N:1 | Set Null |
| `Reservation Item` | (parent) | `Reservation` | Child | Cascade |
| `Rental Contract` | `reservation` | `Reservation` | N:1 | Set Null |
| `Rental Contract` | `customer` | `Customer` (ERPNext) | N:1 | Restrict |
| `Rental Contract` | `customer_extension` | `Customer Extension` | N:1 | Set Null |
| `Rental Contract` | `vehicle` | `Vehicle` | N:1 | Restrict |
| `Rental Contract` | `tva_rate` | `TVA Rate` | N:1 | Restrict |
| `Rental Contract` | `agency` | `Agency` | N:1 | Cascade |
| `Rental Contract` | `created_by_agent` | `Employee Extension` | N:1 | Set Null |
| `Contract Item` | (parent) | `Rental Contract` | Child | Cascade |
| `Contract Amendment` | (parent) | `Rental Contract` | Child | Cascade |
| `Contract Item` | `tva_rate` | `TVA Rate` | N:1 | Set Null |
| `Payment Transaction` | `contract` | `Rental Contract` | N:1 | Set Null |
| `Payment Transaction` | `customer` | `Customer` (ERPNext) | N:1 | Restrict |
| `Payment Transaction` | `currency` | `Currency` (ERPNext) | N:1 | Restrict |
| `Expense Entry` | `vehicle` | `Vehicle` | N:1 | Set Null |
| `Expense Entry` | `contract` | `Rental Contract` | N:1 | Set Null |
| `Expense Entry` | `currency` | `Currency` (ERPNext) | N:1 | Restrict |
| `OCR Result` | `customer` | `Customer` (ERPNext) | N:1 | Set Null |
| `OCR Result` | `vehicle` | `Vehicle` | N:1 | Set Null |
| `OCR Result` | `contract` | `Rental Contract` | N:1 | Set Null |
| `OCR Result` | `reviewed_by` | `Employee Extension` | N:1 | Set Null |
| `OCR Result` | `agency` | `Agency` | N:1 | Cascade |
| `OCR Extracted Field` | (parent) | `OCR Result` | Child | Cascade |
| `Maintenance Record` | `vehicle` | `Vehicle` | N:1 | Restrict |
| `Maintenance Record` | `agency` | `Agency` | N:1 | Cascade |
| `GPS Position` | `vehicle` | `Vehicle` | N:1 | Cascade |
| `GPS Position` | `agency` | `Agency` | N:1 | Cascade |
| `Geofence Zone` | `agency` | `Agency` | N:1 | Cascade |
| `Geofence Alert` | `vehicle` | `Vehicle` | N:1 | Cascade |
| `Geofence Alert` | `zone` | `Geofence Zone` | N:1 | Cascade |
| `Geofence Alert` | `acknowledged_by` | `Employee Extension` | N:1 | Set Null |
| `Geofence Alert` | `agency` | `Agency` | N:1 | Cascade |
| `Document Record` | `customer` | `Customer` (ERPNext) | N:1 | Restrict |
| `Document Record` | `vehicle` | `Vehicle` | N:1 | Set Null |
| `Document Record` | `contract` | `Rental Contract` | N:1 | Set Null |
| `Document Record` | `agency` | `Agency` | N:1 | Cascade |
| `Document Record` | `uploaded_by` | `User` (Frappe) | N:1 | Set Null |
| `Document Audit Log` | (parent) | `Document Record` | Child | Cascade |
| `Document Audit Log` | `performed_by` | `User` (Frappe) | N:1 | Restrict |
| `GPS Position` | `vehicle` | `Vehicle` | N:1 | Cascade |
| `GPS Position` | `agency` | `Agency` | N:1 | Cascade |
| `Geofence Zone` | `agency` | `Agency` | N:1 | Cascade |
| `Geofence Alert` | `vehicle` | `Vehicle` | N:1 | Cascade |
| `Geofence Alert` | `zone` | `Geofence Zone` | N:1 | Cascade |
| `Geofence Alert` | `acknowledged_by` | `User` (Frappe) | N:1 | Set Null |
| `Geofence Alert` | `agency` | `Agency` | N:1 | Cascade |
| `Vehicle Tracking` | `vehicle` | `Vehicle` | 1:1 | Cascade |

### 3.2 Business Rule Relationships

| Rule | Description |
|------|-------------|
| **Reservation → Vehicle Availability** | A vehicle can only have one `Confirmed` or `Active` reservation at any given date range. Overlap check required. |
| **Contract → Reservation** | A contract may be created from a reservation. The reservation links to at most one contract. |
| **Contract → Vehicle Status** | On submit: vehicle status → `Rented`. On complete/cancel: vehicle status → `Available`. |
| **OCR → Entity Linking** | OCR results can be linked to a Customer (CIN/license scan), Vehicle (registration scan), or Contract. |
| **Maintenance → Vehicle Status** | When maintenance starts: vehicle status → `Maintenance`. When completed: → `Available` (if no active reservation). |
| **GPS → Geofence** | Each GPS position is checked against active geofence zones. Alerts generated on entry/exit/violation. |
| **TVA → Contract** | Every contract references a TVA rate. Each contract item can override the rate. Grand total = sum(items) + TVA. |
| **Payment Transaction → Contract** | Payments link to contracts and update payment_status. Customer must match. Amount immutable after completion. |
| **Expense Entry → Vehicle/Contract** | Expenses can optionally link to a vehicle or contract for cost tracking. |
| **Document Record → Entity** | Documents link to a Customer (required), and optionally to a Vehicle or Contract. OCR extracts fields automatically. |
| **Document Expiration → Alerts** | Expiration monitoring runs hourly (documents) and daily (vehicles). Alerts at 30/15/7/1 day thresholds. |
| **Agency → All** | Every document has an `agency` field for SaaS tenant isolation. |

### 3.3 Cross-Module Data Flow

```
Customer ──registers──► Customer Extension
     │
     └──creates──► Reservation ──(confirmed)── locks Vehicle
                        │
                        └──converts to──► Rental Contract ──(submitted)──► Sales Invoice
                             │                      │
                             │                      ├── OCR Result (customer docs)
                             │                      └── Contract Amendments
                             │
                             ├──generates──► Payment Entry (deposit)
                             └──receives──► Payment Transaction ──(updates)──► contract.payment_status

Vehicle ──tracked by──► GPS Positions ──checked against──► Geofence Zones ──triggers──► Geofence Alerts
     │
     ├──maintained via──► Maintenance Records
     └──incurs──► Expense Entry (Fuel, Maintenance, Tolls, etc.)

All documents ──scoped to──► Agency (SaaS tenant)

Document Record ──(linked to)──► Customer, Vehicle, or Rental Contract
     │
     ├──receives──► OCR Extraction (Tesseract / Google Vision / Azure)
     ├──maintains──► Audit Log (upload, OCR, corrections, archive)
     └──monitors──► Expiration Alerts (30/15/7/1 day thresholds)
```

---

## 4. ERPNext Core Extensions

These are **custom fields** added to existing ERPNext DocTypes, not new DocTypes.

### 4.1 Customer (ERPNext) — Custom Fields

| Field | Type | Description |
|-------|------|-------------|
| `rent_pro_customer_id` | Data (Read Only) | Link back to Customer Extension |

### 4.2 Employee (ERPNext) — Custom Fields

| Field | Type | Description |
|-------|------|-------------|
| `rent_pro_employee_id` | Data (Read Only) | Link back to Employee Extension |

### 4.3 Sales Invoice (ERPNext) — Custom Fields

| Field | Type | Description |
|-------|------|-------------|
| `rental_contract` | Link (Rental Contract) | FK → Rental Contract |
| `tva_breakdown` | Small Text | TVA itemization for Moroccan compliance |

---

## 5. Database Indexes

Critical indexes for performance at scale:

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| `tabVehicle` | `agency_status` | `(agency, status)` | Fleet availability queries |
| `tabReservation` | `vehicle_dates` | `(vehicle, start_date, end_date)` | Overlap detection |
| `tabReservation` | `customer_reservations` | `(customer, status)` | Customer history |
| `tabRental Contract` | `vehicle_contracts` | `(vehicle, start_date, end_date)` | Contract overlap |
| `tabRental Contract` | `customer_contracts` | `(customer, status)` | Customer contracts |
| `tabGPS Position` | `vehicle_time` | `(vehicle, position_timestamp)` | Position history queries |
| `tabGPS Position` | `agency_time` | `(agency, position_timestamp)` | Agency-wide tracking |
| `tabMaintenance Record` | `vehicle_maintenance` | `(vehicle, start_date)` | Service history |
| `tabGeofence Alert` | `vehicle_alerts` | `(vehicle, alert_timestamp)` | Alert history |
| `tabOCR Result` | `agency_status` | `(agency, status)` | OCR queue management |

---

## 6. Naming Conventions Summary

| DocType | Pattern | Example |
|---------|---------|---------|
| `Agency` | `AGC-{####}` | `AGC-0001` |
| `Vehicle Category` | `field:category_name` | `Economy` |
| `Vehicle` | `VEH-{####}` | `VEH-0001` |
| `Customer Extension` | `CUSTX-{####}` | `CUSTX-0001` |
| `Employee Extension` | `EMPX-{####}` | `EMPX-0001` |
| `Reservation` | `RES-{#####}` | `RES-00001` |
| `Rental Contract` | `CON-{####}` | `CON-0001` |
| `Payment Transaction` | `PAY-{#####}` | `PAY-00001` |
| `Expense Entry` | `EXP-{#####}` | `EXP-00001` |
| `OCR Result` | `OCR-{####}` | `OCR-0001` |
| `Maintenance Record` | `MNT-{####}` | `MNT-0001` |
| `GPS Position` | `hash` | `a3f8b2c1...` |
| `Geofence Zone` | `GZF-{####}` | `GZF-0001` |
| `Geofence Alert` | `GZA-{####}` | `GZA-0001` |
| `TVA Rate` | `field:rate_name` | `20%` |
| `Rent Pro Settings` | `settings` | `settings` |
| `Document Record` | `DOC-{#####}` | `DOC-00001` |
| `GPS Position` | `hash` | `a3f8b2c1...` |
| `Geofence Zone` | `GZF-{####}` | `GZF-0001` |
| `Geofence Alert` | `GZA-{#####}` | `GZA-00001` |
| `Vehicle Tracking` | `field:vehicle` | `VEH-0001` |
