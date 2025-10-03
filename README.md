# Jellyfin Profile Monitor

A Home Assistant add-on that monitors a Jellyfin profile and allows it to be displayed as a card.

## Information
This add-on differs from other Jellyfin addons for HA as it uses per-profile monitoring with the API, instead of per-device monitoring with account credentials. This allows for any source used by a single user to be monitored and displayed in your dashboard.

As a result, it will not infinitely create entities for devices, instead only making entities for each profile.

The add-on uses the API to communicate playback state and the title of the show and episode. The playback state status is represented and updated as the icon for the card.

## Installation
1. Download the latest version of the add-on from <a href="https://github.com/4rft5/ha-jf-profile-monitor/releases">Releases</a>.

2. Place the extracted ha-jf-profile-monitor folder into your `custom_components` folder.

3. <a href="https://gethomepage.dev/widgets/services/jellyfin/">Create a Jellyfin API Key</a>.
   
4. Add Integration by clicking "Add Integration" and searching for "Jellyfin Profile Monitor".

5. Input API Key and Jellyfin Server IP.

6. Add the newly-created entity to your cards or dashboard.

## Screenshots
A Regular Card:

![image](https://github.com/user-attachments/assets/8b3a101b-0a67-4ce2-ab95-045143ea25dc)

Regular Card with playback information:

![image](https://github.com/user-attachments/assets/39348e75-05a6-42be-8094-63919c0edbcc)

Example of the "idle" playback state:

![image](https://github.com/user-attachments/assets/9851c36e-d649-4125-8b96-b3fb2a551eb4)

Examples of the media-control card:

TV Show:
![image](https://github.com/user-attachments/assets/2d83dbfc-d834-487c-b658-6db1d1713258)

Movie
![image](https://github.com/user-attachments/assets/5a60d94c-159a-4b7b-90d9-e2702e5f29dc)


## Contributions

Pull Requests and other contributions are welcome. I've never made an HA add-on before, so things like the config_flow, an icon for the integrations menu, and HACS publishing are all beyond me.

Media Controls do not work, as this is more to just display the status of a profile, but would be welcomed additions if someone wanted to tackle them.

### Issues

The console will log that the newly created media_player does not support media_player features (playback). This is intended as playback controls are not integrated.

