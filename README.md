# DieLiga Home Assistant Integration 🏐

The `dieliga` sensor provides information about your sports league from [DieLiga](https://www.ost.volleyball-freizeit.de/), compatible with scoreboard systems based on "dieLiga" (tested with **Volleyball-Freizeit Ost**).

## Features ✨

- **Scoreboard**: See your team's current position.
- **Schedule**: Track upcoming games and season progress.
- **Notifications**: Get alerts for rank changes and game reminders.

## Installation 🛠️

### 1. Using HACS (Recommended)

This integration is not yet in the default HACS list but can be added as a **Custom Repository**.

1.  Open HACS.
2.  Add Custom Repository: `https://github.com/FaserF/ha-dieliga` (Category: Integration).
3.  Click **Download**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-dieliga&category=integration)

### 2. Manual Installation

1.  Download the latest [Release](https://github.com/FaserF/ha-dieliga/releases/latest).
2.  Extract the ZIP file.
3.  Copy the `dieliga` folder to `<config>/custom_components/`.

## Configuration ⚙️

1.  Go to **Settings** -> **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for "dieliga".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dieliga)

### Configuration Variables
- **base url**: input the base url from the dieliga that should be tracked. For example https://www.ost.volleyball-freizeit.de (please do not append a '/' in the end!).
- **liga id**: input your liga id, that should be tracked. Unfortunatly this changes every new season. You can recieve it by opening Schedule & Table in your browser and then copying the 4/5 digit ID from there. You can find the ID here, as an example this would be 1031: https://www.ost.volleyball-freizeit.de/schedule/overview/1031
- **team_name**: This is optional. You can provide your teamname (it has to be spelled exactly like on the liga page!), then this integration will display your teams scoreboard position as sensor state and will filter the upcoming matches to only display matches of your team.
- **refresh time**: the refresh interval in hours

## Sensor Attributes
The data is being refreshed every 12 hours per default, unless otherwise defined in the refresh time.

The state of the schedule sensor contains in percentage how many games have been completed already this season.
The state of the scoreboard sensor contains the team position (if a team name has been provided).

The attributes contains all the relevant team informations.

## Accessing the data

### Automations
```yaml
automation:
  - alias: "Notification When Team Reaches Position in League Table"
    trigger:
      platform: state
      entity_id: sensor.dieliga_scoreboard_teamname
    condition:
      condition: numeric_state
      entity_id: sensor.dieliga_scoreboard_teamname
      below: 5
    action:
      service: notify.notify
      data:
        message: "Congratulations! Your team is now in position {{ state('sensor.dieliga_scoreboard_teamname') }} in the table!"
```

```yaml
automation:
  - alias: "Reminder for Upcoming Game"
    trigger:
      platform: state
      entity_id: sensor.dieliga_schedule_teamname
    condition:
      condition: template
      value_template: >
        {% set upcoming_game = states('sensor.dieliga_schedule_teamname') %}
        {% if upcoming_game %}
          {% set game_date = strptime(upcoming_game, '%Y-%m-%d') %}
          {% if game_date and game_date > now() %}
            {{ game_date - now() < timedelta(hours=48) }}
          {% else %}
            false
          {% endif %}
        {% else %}
          false
        {% endif %}
    action:
      service: notify.notify
      data:
        message: "Reminder: Your game is coming up on {{ upcoming_game }}! Get ready!"
```

```yaml
automation:
  - alias: "Notify If No Upcoming Matches in the Next Week"
    trigger:
      platform: time
      at: "09:00:00"
    condition:
      condition: template
      value_template: >
        {% set upcoming_matches = state_attr('sensor.dieliga_schedule_teamname', 'games') %}
        {% set no_upcoming_matches = true %}
        {% for match in upcoming_matches %}
          {% set match_date = strptime(match['date'], '%Y-%m-%d') %}
          {% if match_date and match_date > now() and match_date < now() + timedelta(days=7) %}
            {% set no_upcoming_matches = false %}
          {% endif %}
        {% endfor %}
        {{ no_upcoming_matches }}
    action:
      service: notify.notify
      data:
        message: "Reminder: There are no matches scheduled for your team in the next week. Check the schedule for updates."
```

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