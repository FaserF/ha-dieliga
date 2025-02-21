import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from .const import (
    CONF_URL,
    CONF_LIGA_ID,
    CONF_TEAM_NAME,
    CONF_REFRESH_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dieliga integration."""

    VERSION = 1
    async def async_step_user(self, user_input=None):
        """Handle the user input for the config flow."""
        errors = {}

        if user_input is not None:
            liga_id = str(user_input[CONF_LIGA_ID])
            await self.async_set_unique_id(user_input[CONF_LIGA_ID])
            self._abort_if_unique_id_configured()

            _LOGGER.debug("Initialized dieliga integration with liga_id: %s", user_input[CONF_LIGA_ID])
            return self.async_create_entry(
                title=f"dieLiga {liga_id}", data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_URL, default="https://www.ost.volleyball-freizeit.de"): str,
                vol.Required(CONF_LIGA_ID, default=1234): int,
                vol.Required(CONF_REFRESH_TIME, default=12): int,
                vol.Optional(CONF_TEAM_NAME, default=None): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Erstelle den Optionen-Flow (optional, falls du später Optionen anpassen möchtest)."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow (optional, falls gewünscht)."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.data
        options_schema = vol.Schema({
            vol.Optional(CONF_REFRESH_TIME, default=options.get(CONF_REFRESH_TIME, 1440)): cv.positive_int,
            vol.Optional(CONF_TEAM_NAME, default=options.get(CONF_TEAM_NAME, None)): cv.string,
        })

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
