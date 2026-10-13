import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CannotConnect, InvalidAuth
from .media_player import fetch_profiles


class JFProfileMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            user_input["server_url"] = user_input["server_url"].rstrip("/")
            await self.async_set_unique_id(user_input["server_url"])
            self._abort_if_unique_id_configured()
            try:
                profiles = await fetch_profiles(
                    self.hass, user_input["api_key"], user_input["server_url"]
                )
                if not profiles:
                    errors["base"] = "no_profiles"
                else:
                    return self.async_create_entry(
                        title="Jellyfin Profile Monitor", data=user_input
                    )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required("api_key"): str,
                vol.Required("server_url", default="http://localhost:8096"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )