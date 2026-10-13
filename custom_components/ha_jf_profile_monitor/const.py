DOMAIN = "ha_jf_profile_monitor"
DEFAULT_NAME = "Jellyfin Profile Monitor"


class CannotConnect(Exception):
    """Raised when the Jellyfin server can't be reached or returns an error."""


class InvalidAuth(Exception):
    """Raised when Jellyfin rejects the API key."""


def auth_headers(api_key):
    """Return auth headers accepted by Jellyfin 10.x and 12.x.

    Jellyfin 12 disabled the legacy X-Emby-Token header, so use the
    standard Authorization header instead.
    """
    return {"Authorization": f'MediaBrowser Token="{api_key}"'}
