# Rent Pro — Risks

---

## R1 — ERPNext/Frappe Upgrade Breaking Changes

| | |
|---|---|
| **Severity** | High |
| **Probability** | Medium |
| **Impact** | Breaking custom app on major Frappe/ERPNext upgrades |
| **Mitigation** | Pin ERPNext version per release; upgrade in staging first; maintain compatibility test suite; avoid any core modifications (per Rule 1) |

---

## R2 — Arabic OCR Accuracy

| | |
|---|---|
| **Severity** | High |
| **Probability** | High |
| **Impact** | OCR fails on Arabic documents (CIN, licenses) due to RTL, handwriting, or poor scan quality |
| **Mitigation** | Evaluate multiple OCR providers (Tesseract, Google Vision, AWS Textract); build manual correction UI; start with machine-printed documents only; iterate accuracy metrics per document type |

---

## R3 — Multi-Tenant Data Isolation

| | |
|---|---|
| **Severity** | Critical |
| **Probability** | Low |
| **Impact** | Data leakage between agencies in SaaS mode |
| **Mitigation** | Leverage Frappe's built-in site isolation on Frappe Cloud; add application-level tenant checks; conduct security audit before SaaS launch |

---

## R4 — Moroccan Regulatory Changes

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | Medium |
| **Impact** | TVA rates or tax rules change, requiring immediate updates |
| **Mitigation** | Make TVA rates configurable (not hardcoded); build admin UI for rate management; monitor Moroccan tax authority announcements |

---

## R5 — Frappe Cloud Limitations

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | Medium |
| **Impact** | Frappe Cloud may restrict background jobs, file storage, or custom scheduling needed by GeoFleete/OCR |
| **Mitigation** | Validate all required APIs on Frappe Cloud early (Phase 1); identify fallback hosting; design modules to degrade gracefully |

---

## R6 — GPS/Hardware Integration Complexity

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | High |
| **Impact** | GeoFleete requires integration with diverse GPS hardware vendors; vendor APIs are inconsistent |
| **Mitigation** | Define a standard GPS device abstraction layer; support top 3 Moroccan GPS providers; accept manual position entry as fallback |

---

## R7 — Scaling to 1,000+ Agencies

| | |
|---|---|
| **Severity** | High |
| **Probability** | Low |
| **Impact** | Database queries slow down, background jobs queue, file storage grows beyond Frappe Cloud limits |
| **Mitigation** | Profile query performance from Phase 1; implement pagination and indexing; use Redis caching; load test at 2x target before launch |

---

## R8 — Team Capacity

| | |
|---|---|
| **Severity** | High |
| **Probability** | Medium |
| **Impact** | Single developer (or small team) cannot deliver 9 modules in 10 months |
| **Mitigation** | Strict phase prioritization; defer non-critical features to post-launch; use Frappe's built-in features wherever possible; consider contractor augmentation for OCR/SaaS phases |

---

## R9 — E-Signature Legal Compliance

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | Medium |
| **Impact** | Digital contracts may not hold legal weight in Morocco without proper e-signature |
| **Mitigation** | Research Moroccan e-signature laws (Loi 53-05); integrate with certified Moroccan e-signature providers; start with PDF contracts + manual signing as MVP |

---

## R10 — RTL UI/UX Quality

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | Medium |
| **Impact** | Arabic (RTL) rendering may break layouts, tables, forms, or charts |
| **Mitigation** | Test RTL from Day 1; use Frappe's built-in RTL support; add RTL-specific CSS audit to CI; dedicate QA time per module for Arabic |

---

## R11 — Data Migration from Legacy Systems

| | |
|---|---|
| **Severity** | Medium |
| **Probability** | High |
| **Impact** | Agencies using spreadsheets or legacy software may resist adoption due to difficult data import |
| **Mitigation** | Build CSV/Excel import tools per module; provide migration guide; offer onboarding support; import scripts tested against sample agency data |

---

## R12 — Third-Party Dependency Vulnerabilities

| | |
|---|---|
| **Severity** | High |
| **Probability** | Low |
| **Impact** | Vulnerabilities in Frappe framework, Python libraries, or JS dependencies |
| **Mitigation** | Enable Dependabot/Renovate; run `pip-audit` and `npm audit` in CI; subscribe to Frappe security advisories; patch within 72 hours for critical CVEs |
