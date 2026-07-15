# Upgrade Guide: Rent Pro v1.0 RC1

**Date:** 2026-07-15

---

## 1. Version Compatibility

| Component  | Minimum Version | Recommended Version |
|------------|----------------|---------------------|
| Frappe     | v15            | v15 (latest)        |
| ERPNext    | v15            | v15 (latest)        |
| Rent Pro   | v1.0 RC1       | v1.0 RC1            |

Ensure your bench environment is running Frappe v15 and ERPNext v15 before proceeding.

---

## 2. Pre-Upgrade Steps

1. **Backup your site:**
   ```bash
   bench --site <site-name> backup --with-files
   ```
2. **Review the changelog** for Rent Pro v1.0 RC1 to understand new features and any deprecations.
3. **Check known issues** on the repository issue tracker before upgrading.
4. **Verify disk space** — migrations and builds may require additional storage.
5. **Notify users** and schedule a maintenance window if upgrading a production environment.

---

## 3. Upgrade Steps

```bash
# Pull the latest Rent Pro code
bench get-app --branch main rent_pro

# Run database migrations
bench --site <site-name> migrate

# Rebuild assets
bench build

# Restart bench processes
bench restart
```

---

## 4. Post-Upgrade Verification Checklist

- [ ] All Rent Pro doctypes are synced (`bench --site <site-name` console: `frappe.get_all("DocType", filters={"module": "Rent Pro"})`)
- [ ] Scheduler is running (`bench --site <site-name> scheduler status`)
- [ ] Number cards are loading on the Rent Pro dashboard
- [ ] Custom reports execute without errors
- [ ] Spot-check core workflows (lease creation, rent invoicing, property management)

---

## 5. Rollback Procedure

If issues arise after the upgrade:

```bash
# Restore from the most recent backup
bench --site <site-name> restore <backup-file> --with-files

# Restart bench
bench restart
```

Verify the site is operational after restoration.

---

## 6. Important Notes for Rent Pro

- **Custom fields are preserved** — RC1 does not remove or alter existing custom fields on standard ERPNext doctypes.
- **Data remains intact** — no destructive data migrations are included in this release.
- **No breaking changes** — RC1 is a feature release with backward-compatible changes. Existing configurations and workflows will continue to function as expected.
