# Rent Pro — Milestones

---

## Milestone 1 — Foundation

**Duration**: Weeks 1–8
**Target Date**: End of Month 2

### Deliverables

- [ ] Custom app `rentpro` scaffolded and pushed to GitHub
- [ ] CI pipeline (linting, unit tests, build)
- [ ] Development environment documented (GitHub Codespaces + Docker)
- [ ] Vehicles module: full CRUD (Vehicle, VehicleCategory, VehicleDocument, VehicleMaintenance)
- [ ] Multi-language support (FR, AR, EN) with RTL rendering
- [ ] Frappe Cloud staging deployment
- [ ] Unit test coverage ≥ 90% for Vehicles module

### Acceptance Criteria

- All Vehicles doctypes created, listed, and editable
- App installs cleanly on a fresh ERPNext bench
- All 3 languages selectable in user profile with correct rendering
- CI passes on all branches

---

## Milestone 2 — Core Business

**Duration**: Weeks 9–16
**Target Date**: End of Month 4

### Deliverables

- [ ] Reservations module (booking, availability, conflict resolution)
- [ ] Contracts module (generation, lifecycle, e-signature placeholder)
- [ ] Finance module with Moroccan TVA (20%, 14%, 10%, 7%)
- [ ] Invoice generation with TVA breakdown
- [ ] Payment tracking (cash, bank transfer, card)
- [ ] Integration tests for reservation → contract → invoice flow
- [ ] User documentation (FR + EN)

### Acceptance Criteria

- End-to-end workflow: create reservation → convert to contract → generate invoice → record payment
- TVA calculated correctly for all 4 rates
- Contract PDF generated with correct data
- No data loss across the full workflow

---

## Milestone 3 — Intelligence & Reporting

**Duration**: Weeks 17–24
**Target Date**: End of Month 6

### Deliverables

- [ ] OCR module (CIN, driver license, vehicle registration scanning)
- [ ] OCR field extraction with >85% accuracy
- [ ] Reports: fleet utilization, revenue, customer history, maintenance schedule
- [ ] Dashboard: executive KPIs, fleet status, reservation heatmap
- [ ] Report export (PDF, CSV)
- [ ] Performance benchmarks documented

### Acceptance Criteria

- OCR processes documents in <5 seconds
- Dashboard loads in <2 seconds
- Reports export correctly in all 3 languages
- Arabic report layout verified with RTL support

---

## Milestone 4 — Advanced Features

**Duration**: Weeks 25–32
**Target Date**: End of Month 8

### Deliverables

- [ ] GeoFleete: real-time GPS tracking integration
- [ ] Geofencing with configurable zones and alerts
- [ ] Route history and playback
- [ ] Finance: reconciliation, late fees, deposit management
- [ ] Contracts: renewals, multi-renter, insurance integration
- [ ] Vehicle maintenance alerts based on mileage/time

### Acceptance Criteria

- GPS position updates within 30-second intervals
- Geofence breach triggers notification within 60 seconds
- Full accounting cycle: invoice → payment → reconciliation
- Contract renewal creates new contract with linked history

---

## Milestone 5 — SaaS & Scale

**Duration**: Weeks 33–40
**Target Date**: End of Month 10

### Deliverables

- [ ] Multi-tenant architecture with site isolation
- [ ] Agency onboarding workflow
- [ ] Subscription billing integration
- [ ] Performance: support 100 concurrent users
- [ ] Security audit and penetration testing
- [ ] Production deployment on Frappe Cloud
- [ ] Monitoring and alerting setup
- [ ] Backup and disaster recovery plan
- [ ] Production runbook

### Acceptance Criteria

- Each agency operates in isolated site
- Onboarding a new agency takes <30 minutes
- Zero critical vulnerabilities from security audit
- 99.9% uptime SLA met on staging
- Data backup verified via restore test
