# User Guide

## Getting Started

After installing Rent Pro, follow this guide to set up your car rental operations.

### First Login

1. Log in to your ERPNext instance
2. You will see the **Rent Pro** module in the Desk sidebar
3. Click on **Rent Pro** to access the module

### Initial Setup

#### Step 1: Configure Settings

Go to **Rent Pro > Settings**:

- Set your agency name
- Choose default currency (MAD)
- Configure OCR settings
- Set TVA default rate

#### Step 2: Create Vehicle Categories

Go to **Rent Pro > Vehicle Category > New**:

- Define categories (Economy, SUV, Luxury, etc.)
- Set daily rate multipliers per category
- Set default security deposits

#### Step 3: Add Vehicles

Go to **Rent Pro > Vehicle > New**:

- Enter vehicle details (plate, make, model, year)
- Set daily rental rate
- Upload insurance and registration documents
- Set expiry dates for alerts

#### Step 4: Add Customers

Customer records use ERPNext's Customer DocType. Navigate to **Selling > Customer > New**:

- Enter customer details
- Go to **Rent Pro > Customer Extension** to add:
  - CIN number and expiry
  - Driver license number and expiry
  - Emergency contact

## Daily Operations

### Creating a Reservation

1. Go to **Rent Pro > Reservation > New**
2. Select the customer
3. Select the vehicle (or category)
4. Set pickup and return dates
5. Set pickup and return locations
6. Save and confirm

### Converting Reservation to Contract

1. Open the confirmed reservation
2. Click **Create Rental Contract**
3. Review contract details
4. Upload customer documents (CIN, license)
5. Submit the contract

### Processing Vehicle Return

1. Open the active contract
2. Enter return date, mileage, and fuel level
3. Record any condition notes
4. Click **Complete Contract**
5. Generate invoice if not auto-created

### Processing Payments

1. Go to the Sales Invoice linked to the contract
2. Record payment via **Payment Entry**
3. Process deposit return if applicable

## OCR Document Scanning

1. Go to **Rent Pro > OCR Result > New**
2. Select document type (CIN, License, Registration)
3. Upload the scanned image
4. Click **Process OCR**
5. Review extracted fields
6. Link to customer or vehicle record

## Reports

### Available Reports

- **Fleet Utilization** — Vehicle availability and rental rates
- **Revenue Report** — Income by period, vehicle, category
- **Customer History** — Rental history per customer
- **Maintenance Schedule** — Upcoming and overdue maintenance
- **Tax Summary** — TVA collected by rate

### Accessing Reports

Go to **Rent Pro > Reports** or use the workspace shortcuts.

## GeoFleete (GPS Tracking)

If enabled:

1. Go to **Rent Pro > GeoFleete** workspace
2. View live map with vehicle positions
3. Configure geofence zones
4. Set up alerts for entry/exit/violations
