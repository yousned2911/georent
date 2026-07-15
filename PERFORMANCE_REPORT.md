# PERFORMANCE_REPORT.md — Rent Pro RC1

**Version:** 0.1.0-rc1
**Date:** 2026-07-15
**Methodology:** Static code analysis + query pattern review

---

## Executive Summary

Rent Pro RC1 has **significant performance issues** that will degrade under production load. The most impactful problems are N+1 query patterns in dashboards, unbounded data fetching in GPS/GeoFleete, and missing query optimization in reports. At 100+ vehicles or 50+ agencies, several pages will exceed acceptable load times.

| Category | Rating | Risk |
|----------|:------:|:----:|
| API Response Times | Poor | High |
| Dashboard Load | Poor | High |
| Report Generation | Fair | Medium |
| Background Jobs | Fair | Medium |
| Database Load | Poor | High |
| Memory Usage | Fair | Medium |
| **Overall** | **Poor** | **High** |

---

## 1. N+1 Query Problems

### Super Admin Dashboard — CRITICAL

**Location:** `super_admin/dashboard.py:33-60`

```python
agencies = frappe.get_all("Agency", ...)
for agency in agencies:
    agency["active_users"] = frappe.db.count(...)   # Query 1
    agency["vehicle_count"] = frappe.db.count(...)   # Query 2
    agency["contract_count"] = frappe.db.count(...)   # Query 3
```

**Impact:**
- 50 agencies (default limit) = **150 extra queries** per page load
- With network latency of 1ms per query = 150ms minimum overhead
- At 200 agencies = **600 queries**

**Fix:** Use `GROUP BY` joins or pre-aggregate in a single query.

### Tenant Metrics — CRITICAL

**Location:** `super_admin/tenant_management.py:80-86`

```python
for agency in agencies:
    metrics = get_tenant_metrics(agency.name)  # 7 count queries each
```

**Impact:**
- 50 agencies x 7 queries = **350 queries** per call
- Called from `get_all_tenant_metrics()` which the super admin dashboard uses

### GeoFleete Dashboard

**Location:** Multiple client pages call separate APIs that each hit the database independently.

| API Call | Queries |
|----------|:-------:|
| `get_fleet_positions()` | 1 query |
| `get_all_vehicle_states()` | 1 query |
| `get_active_geofences()` | 1 query |
| `get_recent_alerts()` | 1 query |
| `get_fleet_summary()` | 5 queries |

**Total:** 9 queries per page load, refreshed every 30 seconds.

---

## 2. Unbounded Data Fetches

### GPS Position History — HIGH

**Location:** `mock_provider.py:53-55`

```python
def get_positions(self, since=None):
    for vehicle, history in self._positions.items():
        positions = history if since is None else [...]
```

**Impact:**
- 500 entries max per vehicle (buffer), but no default limit
- 50 vehicles x 500 positions = **25,000 rows** returned to client
- Client must parse and render all positions

**Fix:** Default limit to last 50 positions per vehicle.

### Super Admin Revenue Dashboard — HIGH

**Location:** `super_admin/dashboard.py:182-192`

```python
invoices = frappe.get_all(
    "Sales Invoice",
    filters={"docstatus": 1},
    fields=["posting_date", "grand_total"],
)
```

**Impact:**
- Fetches ALL submitted Sales Invoices across ALL agencies
- A production instance with 10,000+ invoices will return a massive dataset
- In-memory Python processing for monthly aggregation

**Fix:** Use SQL `GROUP BY DATE_FORMAT(posting_date, '%Y-%m')` with proper filters.

---

## 3. Report Query Performance

### All 8 Reports

| Report | Issue | Estimated Rows (1yr) | Query Pattern |
|--------|-------|:--------------------:|---------------|
| Revenue by Month | No date range default | 12,000+ | Full table scan + GROUP BY |
| Revenue by Agency | No agency filter | 12,000+ | Full table scan + JOIN |
| Revenue by Vehicle | No vehicle filter | 12,000+ | Full table scan + JOIN |
| Expenses by Category | No date range default | 5,000+ | Full table scan |
| TVA Summary | Includes Draft contracts | 12,000+ | Full table scan + JOIN |
| Profitability Report | Silent fail on missing filter | 24,000+ | Two full table scans |
| Fleet Utilization | Wrong calculation | N/A | COUNT instead of SUM |
| Outstanding Payments | — | 3,000+ | Full table scan + JOIN |

**Common Issues:**
- No default date range — queries scan entire history
- No pagination — all results returned at once
- SQL fragments use `.format()` — prevents query plan caching

---

## 4. Background Job Performance

### Scheduled Tasks

| Task | Frequency | Queries | Notes |
|------|:---------:|:-------:|-------|
| `daily_tasks` | Daily | ~N vehicles | Checks all non-retired vehicles |
| `hourly_tasks` | Hourly | ~N documents | Checks all document records |
| `geofleete_heartbeat` | Every 5 min | ~10 vehicles | Hardcoded limit of 10 |
| `scheduled_subscription_renewal` | Daily | ~M subscriptions | Iterates all due subscriptions |
| `scheduled_check_overdue_subscriptions` | Daily | ~M subscriptions | Iterates all past-due |
| `scheduled_health_check` | Daily | ~8 | System resource checks |

**Concern:** `hourly_tasks` checking document expiry every hour is excessive. Document expiry changes at most daily. This creates unnecessary DB load 24x/day.

### Fleet Simulation Job

**Location:** `gps/api.py:175-200`

```python
@frappe.whitelist()
def simulate_fleet_movement(duration_seconds=30):
    frappe.enqueue(_simulate_fleet_movement_job, ...)
```

**Issues:**
- No job deduplication — multiple simulation jobs can queue simultaneously
- No error handling — one vehicle failure aborts the entire job
- No progress tracking — no way to know if simulation is running

---

## 5. Print Format Performance

**Location:** `print_formats/rent_pro_standard_contract.json`

Each print execution triggers:

| Query | Count | Type |
|-------|:-----:|------|
| `frappe.db.get_single_value("Rent Pro Settings", ...)` | 3 | Settings lookup |
| `frappe.db.get_value("Vehicle", doc.vehicle, ...)` | 4 | Vehicle details |
| **Total** | **7** | Per print |

**Impact:** At 50 prints/day = 350 extra queries. These values should be pre-fetched and cached.

---

## 6. Boot Session Performance

**Location:** `boot.py:4-8`

```python
def extend_bootinfo(bootinfo):
    settings = frappe.get_single("Rent Pro Settings")
    bootinfo.rent_pro_settings = {
        "agency_name": settings.agency_name,
        "default_currency": settings.default_currency,
        ...
    }
```

**Impact:**
- Runs on EVERY user session creation
- Loads `Rent Pro Settings` (Single doctype) for every user
- No caching — same settings queried repeatedly
- No role check — even API-only users load full settings

---

## 7. Memory Concerns

### Mock GPS Provider

**Location:** `mock_provider.py:24-26`

```python
_simulation_state = {}
_positions = defaultdict(list)
_geofence_status = {}
```

**Impact:**
- Module-level dicts persist for the process lifetime
- `_positions` buffer capped at 500 per vehicle, but never cleaned for sold/inactive vehicles
- 50 vehicles x 500 positions x ~200 bytes = ~5MB per worker
- Multiple Gunicorn workers = multiply by worker count

### Map Auto-Refresh

**Location:** `map_view.js:150`

```javascript
setInterval(() => this.load_vehicles(), 30000);
```

**Impact:**
- Never cleared on page destroy
- Multiple intervals accumulate on SPA navigation
- Each interval holds a reference to the vehicle data closure

---

## 8. Database Index Recommendations

Based on query patterns in the codebase, the following indexes would improve performance:

| Table | Field(s) | Reason |
|-------|----------|--------|
| `tabRental Contract` | `vehicle, status` | Overlap checks, vehicle status |
| `tabRental Contract` | `agency, status` | Dashboard filtering |
| `tabReservation` | `vehicle, status, pickup_date` | Overlap detection |
| `tabPayment Transaction` | `contract, status` | Payment status aggregation |
| `tabPayment Transaction` | `creation` | Monthly revenue reports |
| `tabExpense Entry` | `category, expense_date` | Expense reports |
| `tabDocument Record` | `expiry_date, status` | Hourly expiry checks |
| `tabGPS Position` | `vehicle, creation` | Position history queries |
| `tabGeofence Alert` | `vehicle, zone, creation` | Alert deduplication |

---

## 9. Recommendations

### Immediate (RC1 → RC2)

1. **Fix N+1 queries** in super admin dashboard and tenant management
2. **Add pagination** to all GPS API endpoints
3. **Add date range defaults** to all 8 reports
4. **Cache Rent Pro Settings** in boot session
5. **Reduce hourly_tasks to daily** for document expiry checks

### Short-term (RC2 → GA)

1. **Implement query result caching** for dashboard number cards
2. **Add database indexes** for the 9 tables listed above
3. **Replace in-memory GPS state** with Redis or database persistence
4. **Add rate limiting** to GPS and super admin endpoints
5. **Optimize print format** to pre-fetch vehicle/settings data

### Long-term (Post-GA)

1. **Implement read replicas** for report queries
2. **Add background job monitoring** with progress tracking
3. **Implement CDN** for static assets (JS/CSS)
4. **Add query performance logging** for slow query detection

---

## Benchmark Estimates

| Scenario | Current (est.) | Target | Gap |
|----------|:--------------:|:------:|:---:|
| Dashboard load (50 agencies) | 3-5s | <500ms | 6-10x |
| Fleet map initial load | 1-2s | <1s | 1-2x |
| Revenue report (1yr data) | 2-4s | <1s | 2-4x |
| Contract creation | 200-500ms | <200ms | 1-2x |
| Boot session creation | 100-200ms | <50ms | 2-4x |
| Fleet simulation (50 vehicles) | 5-10s | <3s | 2-3x |
