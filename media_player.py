import os
import aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from .const import DOMAIN

async def fetch_profiles(api_key, server):
    url = f"{server}/Users"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"X-Emby-Token": api_key}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                return []

def _write_image(img_path, img_bytes):
    with open(img_path, "wb") as f:
        f.write(img_bytes)

class JellyfinProfilePlayer(MediaPlayerEntity):
    def __init__(self, user_id, username, api_key, server, hass):
        self._attr_name = f"Jellyfin - {username}"
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

    async def async_update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._server}/Sessions", headers={"X-Emby-Token": self._api_key}) as resp:
                data = await resp.json()

                if not data:
                    self._set_idle()
                    return

                for session_data in data:
                    if session_data["UserId"] == self._user_id and "NowPlayingItem" in session_data:
                        item = session_data["NowPlayingItem"]

                        self._show_title = item.get("SeriesName")
                        self._episode_title = item.get("Name", "N/A")
                        self._media_title = self._show_title or "Unknown Show"

                        item_id = item["Id"]

                        if item_id != self._current_item_id:
                            cover_url = f"{self._server}/Items/{item_id}/Images/Primary"
                            try:
                                async with aiohttp.ClientSession() as img_session:
                                    async with img_session.get(cover_url, headers={"X-Emby-Token": self._api_key}) as img_resp:
                                        if img_resp.status == 200:
                                            img_bytes = await img_resp.read()
                                            www_path = self._hass.config.path("www")
                                            os.makedirs(www_path, exist_ok=True)
                                            img_filename = f"jellyfin_cover_{self._username}.jpg"
                                            img_path = os.path.join(www_path, img_filename)
                                            await self._hass.async_add_executor_job(_write_image, img_path, img_bytes)
                                            self._current_item_id = item_id
                                            self._media_image_url = f"/local/{img_filename}?v={item_id}"
                            except Exception:
                                self._media_image_url = None

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

    def _set_idle(self):
        self._state = MediaPlayerState.IDLE
        self._status = "Idle"
        self._media_title = None
        self._episode_title = None
        self._show_title = None
        self._media_image_url = None
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
    server = data["server_url"]

    profiles = await fetch_profiles(api_key, server)

    players = []
    for profile in profiles:
        user_id = profile["Id"]
        username = profile["Name"]
        players.append(JellyfinProfilePlayer(user_id, username, api_key, server, hass))

    async_add_entities(players)
