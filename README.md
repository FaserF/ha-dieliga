# dieliga Homeassistant Integration
The `dieliga` sensor will give informations about your liga. It is compatible with any scoreboard, that is based on "dieLiga". It is tested only with [Volleyball-Freizeit Ost](https://www.ost.volleyball-freizeit.de/).
After adding this integration, you will have two sensors, one showing the current scoreboard and another containing all the liga games.

## Installation
### 1. Using HACS (recommended way)

Not available in HACS yet, but it is planned.

### 2. Manual

- Download the latest zip release from [here](https://github.com/FaserF/ha-dieliga/releases/latest)
- Extract the zip file
- Copy the folder "dieliga" from within custom_components with all of its components to `<config>/custom_components/`

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly, the status in the "master" branch can be in development and therefore is maybe not working.

## Configuration

Go to Configuration -> Integrations and click on "add integration". Then search for "dieliga".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dieliga)

### Configuration Variables
- **base url**: input the base url from the dieliga that should be tracked. For example https://www.ost.volleyball-freizeit.de (please do not append a '/' in the end!).
- **liga id**: input your liga id, that should be tracked. Unfortunatly this changes every new season. You can recieve it by opening Schedule & Table in your browser and then copying the 4/5 digit ID from there. You can find the ID here, as an example this would be 1031: https://www.ost.volleyball-freizeit.de/schedule/overview/1031
- **team_name**: This is optional. You can provide your teamname (it has to be spelled exactly like on the liga page!), then this integration will display your teams scoreboard position as sensor state and will filter the upcoming matches to only display matches of your team.
- **refresh time**: the refresh interval in minutes

## Sensor Attributes
The data is being refreshed every 1440 minutes (once a day) per default, unless otherwise defined in the refresh time.

The state of the schedule sensor contains in percentage how many games have been completed already this season.
The state of the scoreboard sensor contains the team position (if a team name has been provided).

The attributes contains all the relevant team informations.

## Bug reporting
Open an issue over at [github issues](https://github.com/FaserF/ha-dieliga/issues). Please prefer sending over a log with debugging enabled.

To enable debugging enter the following in your configuration.yaml

```yaml
logger:
    logs:
        custom_components.dieliga: debug
```

You can then find the log in the HA settings -> System -> Logs -> Enter "dieliga" in the search bar -> "Load full logs"

## Thanks to
Thanks to dieliga for their great software!