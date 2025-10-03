import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .media_player import fetch_profiles

class JFProfileMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                profiles = await fetch_profiles(
                    user_input["api_key"], user_input["server_url"]
                )
                if not profiles:
                    errors["base"] = "no_profiles"
                else:
                    return self.async_create_entry(
                        title="Jellyfin Profile Monitor", data=user_input
                    )
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required("api_key"): str,
                vol.Required("server_url", default="http://localhost:8096"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)