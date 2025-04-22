DOMAIN = "ha-jf-profile-monitor"

async def async_setup_entry(hass, config_entry):
    from .media_player import async_setup_platform
    await async_setup_platform(hass, config_entry)
    return True

async def async_setup(hass, config):
    return True
