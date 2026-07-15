# Security Policy

## Reporting a Vulnerability

The Rent Pro team takes security seriously. We appreciate your efforts to responsibly disclose any security vulnerabilities.

**Do NOT open public GitHub issues for security vulnerabilities.**

### How to Report

1. **Email:** security@rentpro.ma
2. **Subject:** [SECURITY] Vulnerability Report — [Brief Description]
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 1 week
- **Resolution Timeline:** Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next release

### Disclosure Policy

- We will work with you to understand and resolve the issue
- We will credit reporters in the release notes (unless anonymity is requested)
- We request a 90-day disclosure embargo before public disclosure

---

## Security Measures

### Authentication & Authorization

- Frappe's built-in authentication
- Role-based access control (7 custom roles)
- Session management via Frappe framework
- No custom authentication bypass

### Data Protection

- Multi-tenant data isolation via `agency` field
- Parameterized SQL queries (no injection)
- CSRF protection via Frappe tokens
- File upload handled by Frappe framework

### API Security

- All write endpoints require authentication
- Super Admin endpoints require System Manager role
- GPS API endpoints validate permissions
- Rate limiting recommended (not yet implemented)

### Infrastructure

- HTTPS required for production
- Redis for session management
- MariaDB with proper user permissions
- Regular security updates recommended

---

## Known Security Considerations

### v1.0.0-rc1

The following items are known and documented in SECURITY_AUDIT.md:

1. **GPS API Permission Checks** — Some endpoints need additional validation
2. **XSS in GeoFleete JS** — innerHTML usage with user data
3. **Session Impersonation** — Super Admin feature requires careful use
4. **File Upload Validation** — Relying on Frappe defaults

These are tracked and will be addressed in v1.1.0.

---

## Security Updates

Security patches will be released as:

- **Critical:** Immediate patch release
- **High:** Within 1 week
- **Medium:** Next minor release
- **Low:** Next major release

Subscribe to security announcements via GitHub watch.

---

## Compliance

- OWASP Top 10 awareness
- Frappe security guidelines followed
- Moroccan data protection considerations
- GDPR-aware data handling

---

## Contact

- **Security Email:** security@rentpro.ma
- **General Issues:** [GitHub Issues](https://github.com/your-org/rentpro/issues)

Thank you for helping keep Rent Pro secure!
