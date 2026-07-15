import frappe
from frappe.model.document import Document


class FeatureFlag(Document):
    def validate(self):
        self._validate_rollout()
        self._update_metadata()

    def _validate_rollout(self):
        if self.rollout_percentage and self.scope == "Global":
            if self.rollout_percentage < 0 or self.rollout_percentage > 100:
                frappe.throw(frappe._("Rollout percentage must be 0-100."))

    def _update_metadata(self):
        if self.has_value_changed("enabled"):
            self.last_toggled_by = frappe.session.user
            self.last_toggled_on = frappe.utils.now_datetime()

    def before_update_after_submit(self):
        self._update_metadata()


def is_enabled(flag_name, agency_name=None):
    flag = frappe.db.get_value(
        "Feature Flag",
        flag_name,
        ["enabled", "scope", "rollout_percentage", "min_plan_type"],
        as_dict=True,
    )
    if not flag:
        return False
    if not flag.enabled:
        return False
    if flag.scope == "Global":
        return True
    if agency_name and flag.scope == "Per Agency":
        return _check_agency_flag(flag_name, agency_name)
    return flag.enabled


def _check_agency_flag(flag_name, agency_name):
    agency_flag = frappe.db.get_value(
        "Agency Feature Flag",
        {"parent": agency_name, "feature_flag": flag_name},
        "enabled",
    )
    return bool(agency_flag)


def get_all_flags(agency_name=None):
    flags = frappe.get_all(
        "Feature Flag",
        fields=[
            "flag_name",
            "flag_label",
            "enabled",
            "category",
            "scope",
            "flag_type",
        ],
    )
    result = []
    for f in flags:
        effective = f.enabled
        if f.scope == "Per Agency" and agency_name:
            effective = _check_agency_flag(f.flag_name, agency_name)
        result.append({**f, "effective_enabled": effective})
    return result
