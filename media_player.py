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

class JellyfinProfilePlayer(MediaPlayerEntity):
    def __init__(self, user_id, username, api_key, server):
        self._attr_name = f"Jellyfin - {username}"
        self._user_id = user_id
        self._username = username
        self._api_key = api_key
        self._server = server
        self._state = MediaPlayerState.IDLE
        self._media_title = None
        self._episode_title = None
        self._media_image_url = None
        self._show_title = None
        self._status = "Idle"
        self._icon = "mdi:stop"

    async def async_update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._server}/Sessions", headers={"X-Emby-Token": self._api_key}) as resp:
                data = await resp.json()

                if not data:
                    self._state = MediaPlayerState.IDLE
                    self._status = "Idle"
                    self._media_title = None
                    self._episode_title = None
                    self._show_title = None
                    self._media_image_url = None
                    self._icon = "mdi:stop"
                    return

                for session_data in data:
                    if session_data["UserId"] == self._user_id and "NowPlayingItem" in session_data:
                        item = session_data["NowPlayingItem"]

                        self._show_title = item.get("SeriesName")
                        self._episode_title = item.get("Name", "N/A")
                        self._media_title = self._show_title or "Unknown Show"
                        
                        tag = item.get("PrimaryImageTag")
                        id_ = item["Id"]
                        self._media_image_url = f"{self._server}/Items/{id_}/Images/Primary?tag={tag}"

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
        players.append(JellyfinProfilePlayer(user_id, username, api_key, server))

    async_add_entities(players)
