# dieliga Homeassistant Integration
The `dieliga` sensor will give informations about your liga. It is compatible with any scoreboard, that is based on "dieLiga".

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
- **team name**: input your dieliga teamname (it usually is your dieliga subdomain, f.e.: teamname.dieliga.de)
- **refresh time**: the refresh interval in minutes
- **event limit**: the event limit count that should be fetched
- **fetch player info**: try player info fetching (like event response) or not -> If the events are not public, you can disable this to lower the traffic
- **fetch comments**: try event comments fetching -> If the events are not public, you can disable this to lower the traffic

**IMPORTANT: Currently it looks like sign in by "bots" are blocked from dieliga, therefore login wont work (yet)**
- **username** (optional - without less informations can be fetched): input your dieliga username (usually an email)
- **password** (optional - without less informations can be fetched): input your dieliga password

## Sensor Attributes
The data is being refreshed every 30 minutes per default, unless otherwise defined in the refresh time.

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

The data is coming from the [dieliga.online](https://www.dieliga.online/) website.
