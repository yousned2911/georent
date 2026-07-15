frappe.provide("rentpro.super_admin");

rentpro.super_admin = {
    get_platform_summary: function () {
        return frappe.call({
            method: "rentpro.super_admin.dashboard.get_platform_summary",
        });
    },

    get_agency_list: function (filters) {
        return frappe.call({
            method: "rentpro.super_admin.dashboard.get_agency_list_data",
            args: filters || {},
        });
    },

    get_subscription_monitoring: function () {
        return frappe.call({
            method: "rentpro.super_admin.dashboard.get_subscription_monitoring",
        });
    },

    get_revenue_dashboard: function () {
        return frappe.call({
            method: "rentpro.super_admin.dashboard.get_revenue_dashboard",
        });
    },

    get_health_status: function () {
        return frappe.call({
            method: "rentpro.super_admin.system_health.get_health_status",
        });
    },

    run_health_check: function () {
        return frappe.call({
            method: "rentpro.super_admin.system_health.run_health_check",
        });
    },

    get_audit_logs: function (filters) {
        return frappe.call({
            method: "rentpro.super_admin.api.get_audit_logs",
            args: filters || {},
        });
    },

    extend_trial: function (agency, days, reason) {
        return frappe.call({
            method: "rentpro.super_admin.support_tools.extend_trial",
            args: {
                agency_name: agency,
                days: days,
                reason: reason,
            },
        });
    },

    suspend_agency: function (agency, reason) {
        return frappe.call({
            method: "rentpro.super_admin.support_tools.suspend_agency",
            args: { agency_name: agency, reason: reason },
        });
    },

    reactivate_agency: function (agency, reason) {
        return frappe.call({
            method: "rentpro.super_admin.support_tools.reactivate_agency",
            args: { agency_name: agency, reason: reason },
        });
    },

    toggle_flag: function (flag, enabled) {
        return frappe.call({
            method: "rentpro.super_admin.feature_flags.toggle_flag",
            args: { flag_name: flag, enabled: enabled },
        });
    },

    get_tenant_metrics: function (agency) {
        return frappe.call({
            method: "rentpro.super_admin.tenant_management.get_tenant_metrics",
            args: { agency_name: agency },
        });
    },

    verify_isolation: function (agency) {
        return frappe.call({
            method: "rentpro.super_admin.tenant_management.verify_tenant_isolation",
            args: agency ? { agency_name: agency } : {},
        });
    },

    get_background_jobs: function () {
        return frappe.call({
            method: "rentpro.super_admin.system_health.get_background_job_stats",
        });
    },
};
