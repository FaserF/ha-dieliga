import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, TEAM_NAME, LIGA_URL

class TeamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(TEAM_NAME): str,
                    vol.Required(LIGA_URL): str,
                })
            )
        return self.async_create_entry(title=user_input[TEAM_NAME], data=user_input)
