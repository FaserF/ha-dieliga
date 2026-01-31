# DieLiga Home Assistant Integration 🏐

The `dieliga` sensor provides information about your sports league from [DieLiga](https://www.ost.volleyball-freizeit.de/), compatible with scoreboard systems based on "dieLiga" (tested with **Volleyball-Freizeit Ost**).

## Features ✨

- **Modern Architecture**: Uses `DataUpdateCoordinator` for efficient API polling.
- **Scoreboard**: See your team's current position or the league name.
- **Schedule**: Track upcoming games and season progress (percentage of completed games).
- **Notifications**: Get alerts for rank changes and game reminders via Home Assistant automations.

## Installation 🛠️

### 1. Using HACS (Recommended)

1.  Open **HACS** in your Home Assistant instance.
2.  Click the three dots in the top right corner and select **Custom repositories**.
3.  Add Repository: `https://github.com/FaserF/ha-dieliga`
4.  Category: **Integration**
5.  Click **Add**.
6.  Search for "die Liga" and click **Download**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-dieliga&category=integration)

### 2. Manual Installation

1.  Download the latest [Release](https://github.com/FaserF/ha-dieliga/releases/latest).
2.  Extract the ZIP file.
3.  Copy the `custom_components/dieliga` folder to your `<config>/custom_components/` directory.
4.  Restart Home Assistant.

## Configuration ⚙️

1.  Go to **Settings** -> **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **"die Liga"**.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dieliga)

### Configuration Variables

| Variable | Description |
| :--- | :--- |
| **Base URL** | The URL of the DieLiga instance (e.g., `https://www.ost.volleyball-freizeit.de`). |
| **Liga ID** | The numeric ID of your league. Found in the URL of your league's schedule page (e.g., `1031`). |
| **Team Name** | (Optional) Your team's name exactly as it appears on the website. Used for filtering the schedule and showing your rank. |

## Sensors & Platforms 🚀

The integration provides the following entities to keep you up to date:

| Platform | Entity | Description |
| :--- | :--- | :--- |
| `sensor` | **Scoreboard** 🏆 | Your team's current position in the league or the league name. |
| `sensor` | **Schedule** 📅 | The progress of the season (%) and a full list of matches in attributes. |
| `calendar` | **Match Calendar** 🗓️ | All upcoming matches displayed directly in your Home Assistant calendar. |
| `binary_sensor` | **Match Today** ⚡ | Turns `on` if your team has a game today. perfect for automation triggers! |

> [!TIP]
> **Pro Tip:** The **Match Today** sensor is **disabled by default** to keep your setup clean. You can manually enable it under **Settings** -> **Devices & Services** -> **dieLiga** -> **Entities**. 🛠️

## Automations 🤖

Below are several examples of how you can use the sensor data in your automations.

<details>
<summary><b>1. Basic: Rank Change Notification</b></summary>

This automation sends a notification whenever your team's position in the league table changes.

```yaml
alias: "dieLiga: Notify Rank Change"
trigger:
  platform: state
  entity_id: sensor.dieliga_scoreboard_myteam
condition:
  # Ensure the state is a number (position) and has actually changed
  - condition: template
    value_template: "{{ trigger.from_state.state != trigger.to_state.state }}"
action:
  service: notify.mobile_app_myphone
  data:
    title: "League Update! 🏐"
    message: >
      Your team is now in position {{ states('sensor.dieliga_scoreboard_myteam') }}.
```
</details>

<details>
<summary><b>2. Intermediate: Match Day Reminder (1 day before)</b></summary>

Sends a reminder at 8 PM the day before a game.

```yaml
alias: "dieLiga: Game Tomorrow Reminder"
trigger:
  platform: time
  at: "20:00:00"
condition:
  - condition: template
    value_template: >
      {% set games = state_attr('sensor.dieliga_schedule_myteam', 'games') %}
      {% if games %}
        {% set next_game = games | selectattr('state', 'ne', 'Completed') | first %}
        {% if next_game %}
          {{ (strptime(next_game.date, '%Y-%m-%d').date() - now().date()).days == 1 }}
        {% else %}
          false
        {% endif %}
      {% else %}
        false
      {% endif %}
action:
  service: notify.mobile_app_myphone
  data:
    title: "Match Day Tomorrow! 🏐"
    message: >
      Reminder: You play against {{ state_attr('sensor.dieliga_schedule_myteam', 'games')[0].team_a_name if state_attr('sensor.dieliga_schedule_myteam', 'games')[0].team_b_name == 'My Team Name' else state_attr('sensor.dieliga_schedule_myteam', 'games')[0].team_b_name }} tomorrow!
```
</details>

<details>
<summary><b>3. Advanced: Post-Match Result Notification</b></summary>

This automation triggers when the season progress increases (meaning a game was completed) and sends the result of the last game.

```yaml
alias: "dieLiga: Post-Match Result"
trigger:
  platform: state
  entity_id: sensor.dieliga_schedule_myteam
condition:
  # Only trigger if the completed percentage increased
  - condition: template
    value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
action:
  - set_variable:
      last_game: >
        {% set games = state_attr('sensor.dieliga_schedule_myteam', 'games') %}
        {{ games | selectattr('state', 'eq', 'Completed') | list | last }}
  - service: notify.mobile_app_myphone
    data:
      title: "Game Result 🏐"
      message: >
        Result for {{ last_game.team_a_name }} vs {{ last_game.team_b_name }}:
        {{ last_game.team_a_sets }} : {{ last_game.team_b_sets }} sets.
```
</details>

<details>
<summary><b>4. Dashboard: Next 3 Matches (Markdown)</b></summary>

You can use this template in a manual `markdown` card to see your upcoming schedule.

```yaml
type: markdown
content: >
  ### Upcoming Matches 🏐
  | Date | Opponent | Time |
  | :--- | :--- | :--- |
  {% set games = state_attr('sensor.dieliga_schedule_myteam', 'games') | selectattr('state', 'ne', 'Completed') | list %}
  {% for game in games[:3] %}
  | {{ game.date }} | {{ game.team_b_name if game.team_a_name == 'My Team Name' else game.team_a_name }} | {{ game.time }} |
  {% endfor %}
```
</details>

## Bug Reporting 🐛

Please open an issue on [GitHub](https://github.com/FaserF/ha-dieliga/issues). For debugging, add this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.dieliga: debug
```

## Developers 💻

Tests can be run using `pytest`:
```bash
pip install pytest pytest-homeassistant-custom-component
pytest
```
