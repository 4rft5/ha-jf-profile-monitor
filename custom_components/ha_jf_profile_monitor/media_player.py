import logging
import os

import aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CannotConnect, InvalidAuth, auth_headers

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def fetch_profiles(hass, api_key, server):
    """Fetch the list of Jellyfin users.

    Raises InvalidAuth if the key is rejected, CannotConnect for anything else.
    """
    session = async_get_clientsession(hass)
    try:
        async with session.get(
            f"{server}/Users",
            headers=auth_headers(api_key),
            timeout=REQUEST_TIMEOUT,
        ) as resp:
            if resp.status in (401, 403):
                raise InvalidAuth(f"Jellyfin returned HTTP {resp.status}")
            if resp.status != 200:
                raise CannotConnect(f"Jellyfin returned HTTP {resp.status}")
            return await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError) as err:
        raise CannotConnect(str(err)) from err


def _write_image(img_path, img_bytes):
    with open(img_path, "wb") as f:
        f.write(img_bytes)


class JellyfinProfilePlayer(MediaPlayerEntity):
    def __init__(self, user_id, username, api_key, server, hass):
        self._attr_name = f"Jellyfin - {username}"
        self._attr_available = True
        self._user_id = user_id
        self._username = username
        self._api_key = api_key
        self._server = server
        self._hass = hass
        self._state = MediaPlayerState.IDLE
        self._media_title = None
        self._episode_title = None
        self._media_image_url = None
        self._current_item_id = None
        self._show_title = None
        self._status = "Idle"
        self._icon = "mdi:stop"

    def _mark_unavailable(self, reason):
        if self._attr_available:
            _LOGGER.warning("Jellyfin unavailable for %s: %s", self._username, reason)
        self._attr_available = False

    async def async_update(self):
        session = async_get_clientsession(self._hass)

        try:
            async with session.get(
                f"{self._server}/Sessions",
                headers=auth_headers(self._api_key),
                timeout=REQUEST_TIMEOUT,
            ) as resp:
                if resp.status != 200:
                    self._mark_unavailable(f"/Sessions returned HTTP {resp.status}")
                    return
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            self._mark_unavailable(str(err))
            return

        if not self._attr_available:
            _LOGGER.info("Jellyfin is reachable again for %s", self._username)
        self._attr_available = True

        if not data:
            self._set_idle()
            return

        for session_data in data:
            if (
                session_data.get("UserId") == self._user_id
                and "NowPlayingItem" in session_data
            ):
                item = session_data["NowPlayingItem"]

                self._show_title = item.get("SeriesName")
                self._episode_title = item.get("Name", "N/A")
                self._media_title = self._show_title or "Unknown Show"

                item_id = item["Id"]

                if item_id != self._current_item_id:
                    await self._update_cover(session, item_id)

                playback_state = session_data.get("PlayState", {})
                if playback_state.get("IsPaused", False):
                    self._state = MediaPlayerState.PAUSED
                    self._status = "Paused"
                    self._icon = "mdi:pause"
                else:
                    self._state = MediaPlayerState.PLAYING
                    self._status = "Playing"
                    self._icon = "mdi:play"

                return

        self._set_idle()

    async def _update_cover(self, session, item_id):
        cover_url = f"{self._server}/Items/{item_id}/Images/Primary"
        try:
            async with session.get(
                cover_url,
                headers=auth_headers(self._api_key),
                timeout=REQUEST_TIMEOUT,
            ) as img_resp:
                if img_resp.status != 200:
                    self._media_image_url = None
                    return
                img_bytes = await img_resp.read()

            www_path = self._hass.config.path("www")
            await self._hass.async_add_executor_job(
                os.makedirs, www_path, 0o777, True
            )
            img_filename = f"jellyfin_cover_{self._username}.jpg"
            img_path = os.path.join(www_path, img_filename)
            await self._hass.async_add_executor_job(_write_image, img_path, img_bytes)
            self._current_item_id = item_id
            self._media_image_url = f"/local/{img_filename}?v={item_id}"
        except Exception as err:
            _LOGGER.debug("Could not update cover for %s: %s", self._username, err)
            self._media_image_url = None

    def _set_idle(self):
        self._state = MediaPlayerState.IDLE
        self._status = "Idle"
        self._media_title = None
        self._episode_title = None
        self._show_title = None
        self._media_image_url = None
        self._current_item_id = None
        self._icon = "mdi:stop"

    @property
    def state(self):
        return self._status

    @property
    def icon(self):
        return self._icon

    @property
    def entity_picture(self):
        return self._media_image_url

    @property
    def extra_state_attributes(self):
        return {
            "Show Title": self._show_title,
            "Episode Title": self._episode_title,
        }

    @property
    def media_title(self):
        if self._episode_title:
            return self._episode_title
        return self._show_title or self._media_title

    @property
    def media_artist(self):
        if self._show_title:
            return self._show_title
        return None

    @property
    def media_content_type(self):
        return "music"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up media_player from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    api_key = data["api_key"]
    server = data["server_url"].rstrip("/")

    try:
        profiles = await fetch_profiles(hass, api_key, server)
    except (CannotConnect, InvalidAuth) as err:
        raise ConfigEntryNotReady(f"Jellyfin not ready: {err}") from err

    players = []
    for profile in profiles:
        user_id = profile["Id"]
        username = profile["Name"]
        players.append(JellyfinProfilePlayer(user_id, username, api_key, server, hass))

    async_add_entities(players)