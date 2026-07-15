# Rent Pro v1.0 — Performance Report

**Audit Date:** 2026-07-15
**Status:** Analysis complete — no runtime benchmarks possible in dev environment

---

## Methodology

Since no running Frappe instance is available, this report analyzes the codebase for performance patterns, identifies potential bottlenecks, and provides recommendations.

---

## Database Performance

### Query Patterns

| Pattern | Count | Risk |
|---------|-------|------|
| `frappe.db.count()` | 25+ | LOW — indexed |
| `frappe.db.sql()` | 12 | MEDIUM — complex joins in reports |
| `frappe.get_all()` | 100+ | LOW-MEDIUM |
| `frappe.get_doc()` | 50+ | LOW |
| `frappe.db.set_value()` | 5+ | LOW |

### Missing Indexes (Recommended)

| Table | Columns | Reason |
|-------|---------|--------|
| `tabVehicle` | `(agency, status)` | Frequent fleet availability queries |
| `tabReservation` | `(vehicle, start_date, end_date)` | Overlap detection |
| `tabRental Contract` | `(vehicle, start_date, end_date)` | Contract queries |
| `tabGPS Position` | `(vehicle, creation)` | Position history |
| `tabDocument Record` | `(agency, ocr_status)` | OCR queue |
| `tabGeofence Alert` | `(agency, is_acknowledged)` | Alert queries |

### N+1 Query Risks

**HIGH RISK:** `super_admin/dashboard.py:get_agency_list_data()` (line 30-40)
```python
for agency in agencies:
    agency["active_users"] = frappe.db.count("User", ...)
    agency["vehicle_count"] = frappe.db.count("Vehicle", ...)
    agency["contract_count"] = frappe.db.count("Rental Contract", ...)
```
This fires 3 queries per agency. For 100 agencies = 300 queries.
**Fix:** Use a single SQL query with subqueries or denormalize counts.

**MEDIUM RISK:** `tasks.py:_check_document_expiries_job()` (line 38-54)
Iterates all vehicles and checks 2 fields each. For 1000 vehicles = 2000 checks.
**Fix:** Use a single SQL query with date comparisons.

**MEDIUM RISK:** `super_admin/tenant_management.py:get_all_tenant_metrics()`
Calls `get_tenant_metrics()` per agency, each firing 7 queries.
**Fix:** Batch queries across all agencies.

---

## API Performance

### Response Time Expectations

| Endpoint | Expected | Bottleneck |
|----------|----------|------------|
| `get_platform_summary` | < 500ms | Multiple count queries |
| `get_agency_list_data` | < 2000ms | N+1 queries (see above) |
| `get_subscription_monitoring` | < 300ms | 3 count queries + all active |
| `get_revenue_dashboard` | < 1000ms | Full Sales Invoice scan |
| `run_health_check` | < 2000ms | psutil + Redis + DB checks |
| `get_fleet_positions` | < 1000ms | Mock provider or GPS API |
| `simulate_fleet_movement` | < 5000ms | Creates positions for ALL vehicles |

### GPS API Performance

**CRITICAL:** `simulate_fleet_movement()` processes ALL vehicles without limit.
```python
states = provider.get_all_vehicle_states()
for vname in list(states.keys())[:10]:  # Only 10 in heartbeat
```
But the whitelisted version has no `[:10]` limit. For 1000 vehicles, this creates 1000 GPS Position records per call.

**Fix:** Add pagination or limit to 50 vehicles max.

### Report Performance

| Report | Query Complexity | Estimated Time (1000 contracts) |
|--------|-----------------|-------------------------------|
| TVA Summary | Single table scan | < 500ms |
| Revenue by Month | Group by + date range | < 1000ms |
| Revenue by Vehicle | 3-table JOIN | < 2000ms |
| Revenue by Agency | 2-table JOIN | < 1000ms |
| Expenses by Category | Group by category | < 500ms |
| Profitability | 2-table JOIN + aggregation | < 2000ms |
| Fleet Utilization | 2-table JOIN + date calc | < 2000ms |
| Outstanding Payments | 2-table JOIN + filter | < 1000ms |

**Note:** No agency filtering means reports scan ALL data. Adding agency filters will improve performance.

---

## Background Job Performance

| Job | Frequency | Est. Duration | Resources |
|-----|-----------|---------------|-----------|
| `daily_tasks` | Daily | < 30s | Low |
| `scheduled_subscription_renewal` | Daily | < 10s | Low |
| `scheduled_check_overdue_subscriptions` | Daily | < 5s | Low |
| `scheduled_health_check` | Daily | < 5s | Medium (psutil) |
| `hourly_tasks` | Hourly | < 15s | Low |
| `geofleete_heartbeat` | Every 5min | < 30s | Medium |

**geofleete_heartbeat** is the most resource-intensive. It simulates movement for up to 10 vehicles per tick. At 12 ticks/hour = 120 vehicle simulations/hour.

---

## Memory Usage

### Potential Memory Issues

1. **MockProvider** (`gps/mock_provider.py`): Maintains in-memory position history cache of 500 positions per vehicle. For 100 vehicles = 50,000 position objects in memory.

2. **Report Results**: No pagination in report JS. For large datasets, the browser may struggle with thousands of rows.

3. **GPS Position Table**: High-volume inserts without cleanup. After 1 year at 1 position/minute/vehicle = 525,600 records per vehicle.

---

## Scalability Analysis

### Current Capacity (Estimated)

| Metric | Safe Limit | Bottleneck |
|--------|------------|------------|
| Agencies | 50-100 | N+1 queries in dashboard |
| Vehicles per agency | 100 | GPS simulation load |
| Total vehicles | 1,000 | GPS heartbeat processing |
| Contracts per agency | 500 | Report query time |
| GPS positions/day | 10,000 | Table size, no cleanup |
| Concurrent users | 20-30 | No connection pooling tuning |

### Recommended Limits

```python
# In SaaS Settings or Agency Subscription
MAX_VEHICLES_PER_AGENCY = 500
MAX_CONTRACTS_PER_AGENCY = 1000
GPS_RETENTION_DAYS = 90
MAX_GPS_POSITIONS_PER_DAY = 50000
```

---

## Performance Recommendations

### Critical (Before Production)
1. Fix N+1 queries in `get_agency_list_data()`
2. Add pagination to GPS API endpoints
3. Add agency filtering to improve query performance
4. Implement GPS position cleanup job

### High Priority
5. Add database indexes for common query patterns
6. Implement Redis caching for platform summary
7. Add report pagination
8. Limit GPS simulation to 50 vehicles

### Medium Priority
9. Optimize MockProvider memory usage
10. Add query count monitoring
11. Implement connection pooling
12. Add response time logging

### Low Priority
13. Compress GPS position data older than 30 days
14. Implement lazy loading for dashboard JS
15. Add CDN for static assets

---

## Monitoring Recommendations

```python
# Add to key API endpoints
import time
start = time.time()
result = execute_logic()
elapsed = time.time() - start
if elapsed > 2.0:
    frappe.log_error(f"Slow API: {elapsed:.2f}s", "Performance")
```

---

## Conclusion

The app is suitable for **small to medium agencies** (< 200 vehicles, < 50 concurrent users). For larger deployments, the N+1 queries, missing indexes, and GPS data volume must be addressed. The 1,000+ agency SaaS target requires significant query optimization and caching implementation.
