# Rent Pro

Paperless ERP for Moroccan car rental agencies.

Built on [ERPNext](https://erpnext.com) and [Frappe Framework](https://frappeframework.com).

## Features

- **Vehicle Management** — Fleet tracking, documents, maintenance scheduling
- **Reservations** — Availability calendar, conflict detection, booking workflow
- **Contracts** — Digital contract generation with Moroccan TVA support
- **OCR** — Automatic document scanning (CIN, driver licenses, vehicle registration)
- **Finance** — Invoice generation with Moroccan TVA (20%, 14%, 10%, 7%)
- **GeoFleete** — Real-time GPS tracking, geofencing, route history
- **Reports** — Fleet utilization, revenue, customer analytics
- **Dashboard** — Executive KPIs, real-time fleet status
- **SaaS** — Multi-tenant architecture for 1,000+ agencies

## Tech Stack

- ERPNext v15+
- Frappe Framework v15+
- Python 3.10+
- MariaDB 10.6+ / PostgreSQL 14+
- Node.js 18+

## Installation

See [docs/installation.md](docs/installation.md) for detailed instructions.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/georent.git

# In your Frappe bench directory
bench get-app /path/to/georent
bench --site your-site.local install-app rentpro
bench --site your-site.local migrate
bench build --app rentpro
bench restart
```

## Development

### Prerequisites

- Frappe Bench installed
- Python 3.10+
- Node.js 18+
- MariaDB or PostgreSQL

### Setup

```bash
# Create a new site (if needed)
bench new-site dev.rentpro.local

# Install the app
bench --site dev.rentpro.local install-app rentpro

# Enable developer mode
bench --site dev.rentpro.local set-config developer_mode 1
bench restart

# Run tests
bench --site dev.rentpro.local run-tests --app rentpro
```

### Running Tests

```bash
# Run all tests
bench --site dev.rentpro.local run-tests --app rentpro

# Run specific test
bench --site dev.rentpro.local run-tests --app rentpro --module rentpro.rentpro.doctype.rent_pro_settings.test_rent_pro_settings

# With coverage
coverage run -m pytest rentpro/
coverage report
```

### Code Quality

```bash
# Lint
flake8 rentpro/ --max-line-length=110

# Format
black rentpro/ --line-length=110
isort rentpro/ --profile=black

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Modules

| Module | Description |
|--------|-------------|
| Vehicles | Fleet management, vehicle categories, maintenance |
| Reservations | Booking system, availability calendar |
| Contracts | Digital rental contracts, lifecycle management |
| OCR | Document scanning and data extraction |
| Finance | Invoicing, payments, Moroccan TVA |
| GeoFleete | GPS tracking, geofencing, alerts |
| Reports | Analytics and reporting |
| Dashboard | Executive dashboards and KPIs |
| SaaS | Multi-tenant management |

## License

MIT License. See [license.txt](license.txt).

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests
4. Run the test suite
5. Submit a pull request

See [GIT_STRATEGY.md](GIT_STRATEGY.md) for branch naming and workflow details.
