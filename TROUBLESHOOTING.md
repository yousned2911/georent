# TROUBLESHOOTING.md — Rent Pro v1.0 RC1

**Date:** 2026-07-15  
**Version:** Rent Pro v1.0 RC1

---

## 1. Installation Failures

### Check Dependencies
```bash
bench doctor
```
Ensure all required Python packages are installed:
```bash
pip install -r requirements.txt
```

### ERPNext Must Be Installed First
Rent Pro depends on ERPNext. Install ERPNext before Rent Pro:
```bash
bench get-app erpnext
bench --site <site-name> install-app erpnext
bench get-app rent_pro
bench --site <site-name> install-app rent_pro
```

### Python Version
Rent Pro requires Python 3.10+:
```bash
python --version
```
If using Frappe Cloud, ensure the Python version is set in your `Procfile` or app config.

---

## 2. Migration Errors

### Conflicts with ERPNext Core DocTypes
Rent Pro defines custom DocTypes that may conflict with ERPNext core DocTypes:

- **Vehicle** — ERPNext already has a `Vehicle` DocType. Rent Pro extends it. Ensure ERPNext is fully installed before installing Rent Pro.
- **Expense Entry** — ERPNext has an `Expense Claim` DocType. Rent Pro adds `Expense Entry`. Check for naming collisions.

If migration fails with a conflict:
```bash
bench --site <site-name> clear-cache
bench migrate
```

---

## 3. Permission Issues

### Ensure Roles Are Created
After installing Rent Pro, verify that the custom roles are created:
```bash
bench --site <site-name> execute rent_pro.utils.validate_roles
```

### Assign Roles to Users
Go to **User > Select User > Roles** and assign the Rent Pro roles:
- **Fleet Manager**
- **Rent Operations**
- **Property Manager**
- **Finance Team**

---

## 4. Scheduler Not Running

### Verify Scheduler Is Enabled
```bash
bench --site <site-name> enable-scheduler
```
Check scheduler status:
```bash
bench --site <site-name> doctor
```

### Check Background Jobs
Ensure the worker is running:
```bash
bench worker --queue default
bench worker --queue short
bench worker --queue long
```

---

## 5. Number Cards Not Showing Data

### Verify DocType Data Exists
Number cards require existing records in the linked DocTypes. Ensure you have:
- At least one active **Rental Contract**
- At least one **Vehicle** record
- At least one **Invoice**

### Check Module Naming
Verify the number card's `document_type` field points to the correct DocType:
```bash
bench --site <site-name> console
>>> frappe.get_all("Number Card", filters={"module": "Rent Pro"}, fields=["name", "document_type"])
```

---

## 6. GeoFleete Not Working

### Enable in Settings
1. Go to **Rent Pro Settings > GeoFleete**
2. Ensure the feature is enabled

### GPS Provider Configuration
Configure your GPS provider in **Rent Pro Settings > GeoFleete > GPS Provider**:
- **Traccar** — Set the server URL and API key
- **OpenGPS** — Set the endpoint URL
- **Custom** — Provide the API endpoint

Verify connectivity:
```bash
bench --site <site-name> execute rent_pro.geo_fleete.utils.test_connection
```

---

## 7. OCR Not Processing

### Verify Tesseract Installation
```bash
tesseract --version
```
If not installed:
```bash
sudo apt-get install tesseract-ocr
pip install pytesseract
```

### Check Settings
1. Go to **Rent Pro Settings > OCR**
2. Ensure OCR is enabled
3. Verify the language packs are installed for your supported languages

---

## 8. Multi-Tenancy Issues

### Verify Agency Field on All Records
All Rent Pro DocTypes must have an **agency** field set for multi-tenancy to work correctly. Check for orphaned records:
```bash
bench --site <site-name> execute rent_pro.utils.check_orphaned_records
```

If records are missing the agency field:
```bash
bench --site <site-name> execute rent_pro.utils.set_missing_agencies
```

---

## 9. Performance Issues

### Check Redis
Ensure Redis is running:
```bash
redis-cli ping
```
Expected response: `PONG`

### Database Indexing
Run indexing for large tables:
```bash
bench --site <site-name> execute rent_pro.utils.optimize_indexes
```

### Background Jobs
Check for stuck or failed jobs:
```bash
bench --site <site-name> execute frappe.utils.background_jobs.get_queue_list
```

---

## 10. Frappe Cloud Specific Issues

### App Not Found
Ensure the app is added to your Frappe Cloud account:
1. Go to **Frappe Cloud > Apps > Add App**
2. Enter the GitHub repository URL for Rent Pro
3. Add the app to your bench group

### Migration Timeouts
If migration times out on Frappe Cloud:
1. Increase the timeout in your site config
2. Run the migration manually via SSH:
   ```bash
   bench migrate
   bench clear-cache
   bench build
   ```

### Build Failures
If `bench build` fails:
```bash
bench build --app rent_pro
bench clear-cache
bench build
```

---

*For additional support, contact the Rent Pro team or open an issue on the repository.*
