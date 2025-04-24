"""Config flow for Ezetrol Touch integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_IP_ADDRESS

class EzetrolTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ezetrol Touch."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        errors = {}

        if user_input is not None:
            # Validate the IP address (basic validation for now)
            ip_address = user_input[CONF_IP_ADDRESS]
            if not ip_address or not isinstance(ip_address, str):
                errors["base"] = "invalid_ip"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=f"Ezetrol Touch ({ip_address})",
                    data={CONF_IP_ADDRESS: ip_address}
                )

        # Show the form to input the IP address
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Ezetrol Touch."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Show the form to update the IP address
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=self.config_entry.data.get(CONF_IP_ADDRESS)
                ): str,
            }),
        )