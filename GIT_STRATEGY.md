# Rent Pro — Git Strategy

## Branch Model

Uses a simplified Git Flow optimized for a Frappe custom app.

```
main ──────────────────────────────────────────────→ (production)
  │
  └── develop ─────────────────────────────────────→ (integration)
        │
        ├── feature/vehicles-module ───────────────→ (feature)
        ├── feature/reservations-module ───────────→ (feature)
        ├── feature/ocr-integration ───────────────→ (feature)
        ├── bugfix/reservation-date-conflict ──────→ (bugfix)
        └── hotfix/tva-calculation-error ──────────→ (hotfix)
```

## Branch Rules

### `main`

- **Protected**: no direct commits, no force pushes
- **Source of truth** for production
- Only updated via merge from `develop` (release) or `hotfix/*` (emergency)
- Tagged with semver on every merge (`v1.0.0`, `v1.1.0`, etc.)

### `develop`

- **Protected**: no direct commits, no force pushes
- Integration branch for all completed features
- All `feature/*` and `bugfix/*` branches merge here
- Must pass CI before merging
- Merged into `main` at the end of each milestone

### `feature/*`

- Branch naming: `feature/{module-name}` or `feature/{short-description}`
- Examples:
  - `feature/vehicles-module`
  - `feature/reservations-calendar`
  - `feature/ocr-cin-extractor`
  - `feature/tva-rates-config`
- Created from: `develop`
- Merged into: `develop` via Pull Request
- Deleted after merge

### `bugfix/*`

- Branch naming: `bugfix/{short-description}`
- Created from: `develop`
- Merged into: `develop` via Pull Request
- Deleted after merge

### `hotfix/*`

- Branch naming: `hotfix/{short-description}`
- Created from: `main`
- Merged into: **both** `main` and `develop`
- Tagged on `main` merge

## Pull Request Workflow

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/vehicles-module
```

### 2. Work and Commit

- Commit often with clear messages
- Follow conventional commits (see below)
- Push to remote regularly

### 3. Open Pull Request

- Target: `develop`
- Title matches feature name
- Description includes:
  - What was built
  - Doctypes added/modified
  - Tests included
  - Documentation updated
  - Migration instructions (if applicable)

### 4. Review and Merge

- CI must pass (lint + tests)
- Squash and merge to keep history clean
- Delete branch after merge

## Commit Convention

Format:

```
type(scope): description

[optional body]
```

**Types**:

| Type | Usage |
|------|-------|
| `feat` | New feature or module |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code restructuring without behavior change |
| `chore` | Build, CI, tooling changes |
| `perf` | Performance improvement |

**Scopes** (module names):

- `vehicles`, `reservations`, `contracts`, `ocr`, `finance`, `geofleete`, `reports`, `dashboard`, `saas`
- `core` (for cross-module changes)
- `infra` (for CI/Docker/deployment)

**Examples**:

```
feat(vehicles): add vehicle category doctype with CRUD
fix(finance): correct TVA calculation for 10% rate
test(reservations): add conflict resolution unit tests
docs(contracts): add user guide for contract generation
chore(infra): add CI pipeline with lint and test stages
refactor(ocr): extract common field extraction logic
```

## Release Process

### At End of Each Milestone

1. All feature branches merged into `develop`
2. CI green on `develop`
3. Create PR: `develop` → `main`
4. QA verification on staging (if applicable)
5. Merge and tag:

```bash
git checkout main
git merge --no-ff develop
git tag -a v{milestone} -m "Milestone {n} release"
git push origin main --tags
```

6. Delete merged feature branches

### Milestone Tags

| Milestone | Tag |
|-----------|-----|
| M1 — Foundation | `v0.1.0` |
| M2 — Core Business | `v0.2.0` |
| M3 — Intelligence | `v0.3.0` |
| M4 — Advanced | `v0.4.0` |
| M5 — SaaS & Scale | `v1.0.0` |

## CI Pipeline

Triggered on: push to any branch, PR to `develop` or `main`.

### Stages

1. **Lint**: `flake8` (Python), `prettier` (JS), `eslint` (JS)
2. **Test**: `bench --site test_site run-tests --app rentpro`
3. **Build**: Verify app builds cleanly (`bench build --app rentpro`)
4. **Security**: `pip-audit`, `npm audit`

## Branch Protection Rules (GitHub)

| Branch | Required Reviews | CI Required | Force Push |
|--------|-------------------|-------------|------------|
| `main` | 1 | Yes | No |
| `develop` | 1 | Yes | No |
| `feature/*` | — | — | — |
| `hotfix/*` | — | — | — |

## Temporary Branches

- `wip/*` — work-in-progress, never merged directly; used for early feedback
- Stale branches older than 30 days are auto-cleaned
