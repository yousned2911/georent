# Rent Pro — Technical Roadmap

## Vision

Deliver a production-ready, paperless ERPNext application (`rentpro`) for Moroccan car rental agencies, scaling to 1,000+ tenants on Frappe Cloud.

---

## Phase 1 — Foundation (Months 1–2)

**Goal**: Scaffold the custom app, establish multi-language support, and deliver the core entity module.

| Area | Work | Status |
|------|------|--------|
| App Scaffold | `bench new-app rentpro`, directory structure, CI pipeline | DONE |
| Vehicles | Full CRUD for vehicles, vehicle categories, status workflow, validations | DONE |
| Multi-language | i18n setup for French, Arabic (RTL), English | DONE |
| Deployment | Frappe Cloud staging environment, Docker dev setup | PENDING |
| Testing | Unit tests for Vehicles, integration test harness | DONE |

**Exit Criteria**: Vehicles module fully functional in all 3 languages with 90%+ test coverage.

---

## Phase 2 — Core Business (Months 3–4)

**Goal**: Implement the reservation-to-contract workflow and Moroccan TVA.

| Area | Work | Status |
|------|------|--------|
| Reservations | Availability calendar, booking flow, conflict resolution, overlap detection | DONE |
| Contracts | Digital contract generation, TVA calculation, vehicle condition tracking, Sales Invoice integration | DONE |
| Finance | Moroccan TVA (20%, 14%, 10%, 7%), invoice generation, payment tracking | DONE |
| Integration | Reservations ↔ Contracts ↔ Finance data flow | DONE |

**Exit Criteria**: End-to-end rental workflow (book → contract → invoice → payment) operational.

---

## Phase 3 — Intelligence & Reporting (Months 5–6)

**Goal**: Add OCR, analytics, and dashboards.

| Area | Work | Status |
|------|------|--------|
| OCR | Document scanning (CIN, driver license, vehicle registration), field extraction | DONE |
| Document Management | Document Record DocType, audit trail, expiration monitoring | DONE |
| Reports | Fleet utilization, revenue, customer history, vehicle maintenance | DONE |
| Dashboard | Executive KPIs, real-time fleet status, reservation heatmap | DONE |

**Exit Criteria**: OCR achieves >85% accuracy on Moroccan documents; dashboard loads <2s.

---

## Phase 4 — Advanced Features (Months 7–8)

**Goal**: GPS fleet tracking and finance completion.

| Area | Work | Status |
|------|------|--------|
| GeoFleete | Real-time GPS tracking, geofencing, route history, alerts | DONE |
| GeoFleete UI | Map view, vehicle status, alerts, maintenance, dashboard, geofences | DONE |
| GPS Provider Interface | Abstract provider with MockProvider implementation | DONE |
| Finance+ | Reconciliation, late fees, deposit management, expense tracking | PENDING |
| Contracts+ | Renewals, multi-renter support, insurance integration | PENDING |

**Exit Criteria**: GeoFleete tracks vehicles in real-time; full accounting cycle closed.

---

## Phase 5 — SaaS & Scale (Months 9–10)

**Goal**: Multi-tenant production deployment and performance hardening.

| Area | Work | Status |
|------|------|--------|
| SaaS | Multi-tenant architecture, agency onboarding, subscription billing | DONE |
| SaaS Settings | Platform configuration, white label defaults, enforcement settings | DONE |
| Agency DocType | Agency management, trial handling, suspension/reactivation | DONE |
| Subscription Plans | Pricing plans with limits, feature flags, billing cycles | DONE |
| Agency Subscription | Lifecycle management, renewal, billing, invoice generation | DONE |
| License Keys | Software licensing with activation tracking | DONE |
| Plan Enforcement | Limits checking, vehicle creation hooks, usage tracking | DONE |
| Billing Engine | Invoice generation, renewal processing, overdue handling | DONE |
| Platform Dashboard | MRR, ARR, churn rate, plan distribution, revenue trends | DONE |
| Super Admin Platform | Centralized agency/subscription/user management | DONE |
| Feature Flags | Global and per-agency feature toggling | DONE |
| Audit Center | Complete audit trail for all admin actions | DONE |
| System Health | API, DB, Redis, queue, scheduler monitoring | DONE |
| Support Tools | Impersonate, extend trial, suspend, reset, export | DONE |
| Tenant Management | Isolation verification, metrics, quotas, reports | DONE |
| Performance | Query optimization, caching, CDN for static assets | PENDING |
| Security | Penetration testing, data isolation, GDPR compliance | PENDING |
| Production | Staging → production promotion, monitoring, backup strategy | PENDING |

**Exit Criteria**: 100 concurrent users on staging; production-ready for Frappe Cloud.

---

## Dependency Graph

```
Vehicles ──→ Reservations ──→ Contracts ──→ Finance
    │                                          │
    ├──→ GeoFleete                              │
    │                                          │
    └──→ OCR ──→ Reports ──→ Dashboard ────────┘
                                          │
                                      SaaS
```

---

## Long-Term Vision

- Native mobile app (React Native)
- Multi-country expansion beyond Morocco
- AI-powered pricing optimization
- Fleet procurement marketplace
