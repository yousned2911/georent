# Contributing to Rent Pro

Thank you for your interest in contributing to Rent Pro! This guide will help you get started.

---

## Development Setup

### Prerequisites

- Python 3.10+
- MariaDB 10.6+
- Node.js 18+
- Redis 6+
- Git

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/rentpro.git
cd rentpro

# 2. Set up Frappe Bench
bench init --frappe-branch version-15 bench-root
cd bench-root

# 3. Get the app
bench get-app /path/to/rentpro

# 4. Create a development site
bench new-site dev.rentpro.local
bench --site dev.rentpro.local install-app rentpro

# 5. Set developer mode
bench --site dev.rentpro.local set-config developer_mode 1
bench restart
```

---

## Development Workflow

### Branch Strategy

- `main` — Production-ready code
- `develop` — Integration branch
- `feature/*` — New features
- `fix/*` — Bug fixes
- `hotfix/*` — Critical production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature
```

### Code Standards

#### Python

- **Formatter:** Black (line-length=110)
- **Import sorting:** isort
- **Linter:** Flake8 (max-line-length=110)
- **Type hints:** Encouraged but not required

```bash
# Run formatters
black rentpro/
isort rentpro/

# Check for issues
flake8 rentpro/
```

#### JavaScript

- Use Frappe's `__()` for translatable strings
- Avoid `innerHTML` with user data (XSS risk)
- Use `frappe.utils.escape_html()` for user input

#### DocTypes

- Follow Frappe naming conventions
- Include `agency` field for tenant isolation
- Add permissions for all roles
- Include `__init__.py` in doctype directory

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add vehicle maintenance tracking
fix: resolve reservation overlap detection
docs: update deployment guide
refactor: optimize GPS position queries
test: add contract TVA calculation tests
chore: update dependencies
```

### Running Tests

```bash
# Run all tests
bench --site dev.rentpro.local run-tests --app rentpro

# Run specific test file
bench --site dev.rentpro.local run-tests --app rentpro --module rentpro.doctype.vehicle.test_vehicle

# Run with coverage
bench --site dev.rentpro.local run-tests --app rentpro --coverage
```

---

## Code Review Process

1. Create a pull request against `develop`
2. Ensure all tests pass
3. Ensure lint passes (black, isort, flake8)
4. Update documentation if needed
5. Request review from maintainers
6. Address feedback
7. Merge after approval

---

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, Frappe version)
- Screenshots if applicable

### Feature Requests

Include:
- Problem description
- Proposed solution
- Alternatives considered
- Use cases

---

## Security Issues

**Do NOT open public issues for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for responsible disclosure instructions.

---

## Documentation

- Update README.md for new features
- Update relevant guides (DEPLOYMENT, UPGRADE, BACKUP)
- Add inline code comments for complex logic
- Update translations in `translations/` directory

---

## Translation

Rent Pro supports English, French, and Arabic. To add translations:

1. Edit CSV files in `rentpro/translations/`
2. Ensure all keys match across en.csv, fr.csv, ar.csv
3. Test with Arabic locale for RTL support

---

## Questions?

- Open a [GitHub Discussion](https://github.com/your-org/rentpro/discussions)
- Email: dev@rentpro.ma

---

Thank you for contributing to Rent Pro!
