// Rent Pro - Client Side Application

frappe.provide("rentpro");

rentpro.get_settings = function () {
  return frappe.boot.rent_pro_settings || {};
};

rentpro.format_currency_local = function (amount) {
  var settings = rentpro.get_settings();
  var currency = settings.default_currency || "MAD";
  return format_currency(amount, currency);
};

rentpro.notify_expiry = function (vehicle, field, expiry_date) {
  frappe.show_alert(
    {
      message: __("Vehicle {0}: {1} expires on {2}", [vehicle, __(field), expiry_date]),
      indicator: "orange",
    },
    15
  );
};

frappe.realtime.on("rent_pro_expiry_warning", function (data) {
  rentpro.notify_expiry(data.vehicle_number, data.field, data.expiry_date);
});
