frappe.listview_settings["Feature Flag"] = {
  "get_indicator": function (doc) {
    if (doc.enabled) {
      return [__("Enabled"), "green", "enabled,=,1"];
    }
    return [__("Disabled"), "red", "enabled,=,0"];
  },
};
