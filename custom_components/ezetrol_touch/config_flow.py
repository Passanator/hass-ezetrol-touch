import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_SCAN_INTERVAL

class EzetrolTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            if not ip_address or not isinstance(ip_address, str):
                errors["base"] = "invalid_ip"
            scan_interval = user_input[CONF_SCAN_INTERVAL]
            if not isinstance(scan_interval, int) or scan_interval < 60:
                errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
            if not errors:
                return self.async_create_entry(
                    title=f"Ezetrol Touch ({ip_address})",
                    data={CONF_IP_ADDRESS: ip_address, CONF_SCAN_INTERVAL: scan_interval}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_SCAN_INTERVAL, default=300): int,
            }),
            errors=errors,
        )