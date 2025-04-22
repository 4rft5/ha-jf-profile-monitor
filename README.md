# Jellyfin Profile Monitor
<img src="https://github.com/user-attachments/assets/07f8339c-7043-49f8-a692-8c65f07af1e4" width=100>

A Home Assistant add-on that monitors a Jellyfin profile and allows it to be displayed as a card.

## Information
This add-on differs from other Jellyfin addons for HA as it uses per-profile monitoring with the API, instead of per-device monitoring with account credentials. This allows for any source used by a single user to be monitored and displayed in your dashboard.

As a result, it will not infinitely create entities for devices, instead only making entities for each profile.

The add-on uses the API to communicate playback state and the title of the show and episode. The playback state status is represented and updated as the icon for the card.

## Installation
1. Download the latest version of the add-on from <a href="https://github.com/4rft5/ha-jf-profile-monitor/releases">Releases</a>.

2. Place the extracted ha-jf-profile-monitor folder into your `custom_components` folder.

3. <a href="https://gethomepage.dev/widgets/services/jellyfin/">Create a Jellyfin API Key</a>.
   
4. Add the following to your `configuration.yaml` file:
   ```
   media_player:
    - platform: ha-jf-profile-monitor
      api_key: "your_jellyfin_api_key"
      server: "your_jellyfin_url"
   ```

5. Restart Home Assistant.

6. Add the newly-created entity to your cards or dashboard.

## Screenshots
A Regular Card:

![image](https://github.com/user-attachments/assets/8b3a101b-0a67-4ce2-ab95-045143ea25dc)

Regular Card with playback information:

![image](https://github.com/user-attachments/assets/39348e75-05a6-42be-8094-63919c0edbcc)

Example of the "idle" playback state:

![image](https://github.com/user-attachments/assets/9851c36e-d649-4125-8b96-b3fb2a551eb4)

Example of the media-control card:

![image](https://github.com/user-attachments/assets/e252bf6c-b27b-4c1e-916c-f78d45da594d)

### Contributions

Pull Requests and other contributions are welcome. I've never made an HA add-on before, so things like the config_flow, an icon for the integrations menu, and HACS publishing are all beyond me.

Another thing I couldn't figure out personally was how to include multiple lines on the media-control card. This results in the title being [Show Title] - [Episode Title] (or just [Episode Title] for movies). I would prefer if they were on their own lines to make things more streamlined and reduce the risk of text not being able to be read as a result of how wide the card is.

Media Controls do not work, as this is more to just display the status of a profile, but would be welcomed additions if someone wanted to tackle them.

### Issues

The console will log that the newly created media_player does not support media_player features (playback). This is intended as playback controls are not integrated.

