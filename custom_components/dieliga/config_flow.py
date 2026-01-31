import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DieligaApiClient
from .const import (
    CONF_LIGA_ID,
    CONF_TEAM_NAME,
    CONF_URL,
    DOMAIN,
    CONF_REFRESH_TIME,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dieliga integration."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the user input for the config flow."""
        errors = {}

        if user_input is not None:
            base_url = user_input[CONF_URL]
            liga_id = str(user_input[CONF_LIGA_ID])

            # Basic unique ID based on liga_id
            await self.async_set_unique_id(liga_id)
            self._abort_if_unique_id_configured()

            # Validate connection
            session = async_get_clientsession(self.hass)
            client = DieligaApiClient(session, base_url)
            try:
                await client.async_get_scoreboard(liga_id)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                _LOGGER.debug("Validated dieliga integration with liga_id: %s", liga_id)
                return self.async_create_entry(
                    title=f"dieLiga {liga_id}", data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_URL, default="https://www.ost.volleyball-freizeit.de"): str,
                vol.Required(CONF_LIGA_ID, default=1234): int,
                vol.Optional(CONF_TEAM_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data
        options_schema = vol.Schema({
            vol.Optional(CONF_TEAM_NAME, default=options.get(CONF_TEAM_NAME, data.get(CONF_TEAM_NAME, ""))): str,
            vol.Optional(CONF_REFRESH_TIME, default=options.get(CONF_REFRESH_TIME, 12)): int,
        })

        return self.async_show_form(
            step_id="init", data_schema=options_schema
        )
