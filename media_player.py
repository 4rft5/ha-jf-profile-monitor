import aiohttp
import asyncio
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState

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
                        self._show_title = item.get("SeriesName", "Unknown Show")
                        self._episode_title = item.get("Name", "N/A")
                        if "SeriesName" in item:
                            self._show_title = item["SeriesName"]
                            self._episode_title = item.get("Name", "N/A")
                            self._media_title = f"{self._show_title} - {self._episode_title}"
                        else:
                            self._show_title = None
                            self._episode_title = item.get("Name", "Unknown Title")
                            self._media_title = self._episode_title
                        tag = item.get("PrimaryImageTag")
                        id_ = item["Id"]
                        self._media_image_url = f"{self._server}/Items/{id_}/Images/Primary?tag={tag}"
                        playback_state = session_data.get("PlayState", {})

                        if playback_state.get("IsPaused", False):
                            if self._state != MediaPlayerState.PAUSED:
                                self._state = MediaPlayerState.PAUSED
                                self._status = "Paused"
                                self._icon = "mdi:pause"
                        else:
                            if self._state != MediaPlayerState.PLAYING:
                                self._state = MediaPlayerState.PLAYING
                                self._status = "Playing"
                                self._icon = "mdi:play"
                        
                        return

        if self._state != MediaPlayerState.IDLE:
            self._state = MediaPlayerState.IDLE
            self._status = "Idle"
            self._icon = "mdi:stop"

        self._media_title = None
        self._episode_title = None
        self._show_title = None
        self._media_image_url = None

    @property
    def state(self):
        return self._status

    @property
    def media_title(self):
        return self._media_title

    @property
    def media_artist(self):
        return self._episode_title

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

async def async_setup_platform(hass, config, async_add_entities=None, discovery_info=None):
    api_key = config.get("api_key")
    server = config.get("server")

    if not api_key or not server:
        raise ValueError("API key and server URL must be provided in configuration.yaml")

    profiles = await fetch_profiles(api_key, server)

    players = []
    for profile in profiles:
        user_id = profile["Id"]
        username = profile["Name"]
        players.append(JellyfinProfilePlayer(user_id, username, api_key, server))

    async_add_entities(players)
