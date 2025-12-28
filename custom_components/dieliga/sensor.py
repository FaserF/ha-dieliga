import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import aiohttp
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

class DieligaScoreboardSensor(SensorEntity):
    """Sensor to fetch the league table."""

    def __init__(self, base_url, liga_id, team_name=None):
        self._base_url = str(base_url)
        self._liga_id = str(liga_id)
        self._team_name = str(team_name)
        self._name = f"dieLiga Scoreboard {team_name}" if team_name else f"dieLiga Scoreboard {liga_id}"
        self._state = None
        self._previous_state = None
        self._unique_id = f"dieliga_table_{liga_id}"
        self._attributes = {}
        self._icon = "mdi:podium-gold"
        self._attribution = f"Data provided by API {self._base_url}/schedule/summary/{self._liga_id}?output=xml"
        self._last_updated = None

    async def async_update(self):
        """Fetch the latest league scoreboard."""
        if self._last_updated and datetime.now() - self._last_updated < timedelta(hours=12):
            _LOGGER.debug("Update skipped; last update was less than 12 hours ago.")
            return

        url = f"{self._base_url}/schedule/summary/{self._liga_id}?output=xml"
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                self._last_updated = datetime.now()
                if response.status == 200:
                    data = await response.text()
                    # Parse the XML response
                    self._parse_xml(data)
                else:
                    _LOGGER.error("Failed to fetch league table, status code: %s", response.status)
        except Exception as e:
            _LOGGER.error("Error fetching league table: %s", e)

    def _parse_xml(self, xml_data):
        """Parse the XML data to extract league information."""
        try:
            # Parse XML data
            root = ET.fromstring(xml_data)

            # Extract other relevant attributes
            self._attributes = {
                "group": root.find("group").text if root.find("group") is not None else "Unknown",
                "region": root.find("region").text if root.find("region") is not None else "Unknown",
                "last_change": root.find("last_change").text if root.find("last_change") is not None else "Unknown"
            }

            # Extract teams and their information
            teams = []
            team_position = None  # To store the position of the team if found
            for index, team in enumerate(root.findall(".//table/team")):
                team_info = {
                    "name": team.find("name").text if team.find("name") is not None else "Unknown",
                    "points_positive": team.find("points").get("positive") if team.find("points") is not None else "0",
                    "points_negative": team.find("points").get("negative") if team.find("points") is not None else "0",
                    "sets_positive": team.find("sets").get("positive") if team.find("sets") is not None else "0",
                    "sets_negative": team.find("sets").get("negative") if team.find("sets") is not None else "0",
                    "balls_positive": team.find("balls").get("positive") if team.find("balls") is not None else "0",
                    "balls_negative": team.find("balls").get("negative") if team.find("balls") is not None else "0",
                    "games": team.find("games").text if team.find("games") is not None else "0",
                    "games_won": team.find("games_won").text if team.find("games_won") is not None else "0",
                }
                teams.append(team_info)

                # Check if the team matches the user's input team name
                if self._team_name and team_info["name"].lower() == self._team_name.lower():
                    team_position = index + 1

            # Set the league name as the state
            if team_position:
                self._state = team_position
                self._unit_of_measurement = "position"
            else:
                self._state = root.find("league").text if root.find("league") is not None else "Unknown"

            # Add the teams list as an attribute
            self._attributes["teams"] = teams
            self._attributes["last_updated"] = self._last_updated
            self._attributes["attribution"] = self._attribution

        except Exception as e:
            _LOGGER.error("Error parsing XML data: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        if self._state is None:
            return self._previous_state or "Unknown"
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self._attributes:
            return self._previous_attributes
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    async def async_added_to_hass(self):
        """Called when the sensor is added to Home Assistant."""
        # Ensure the previous state and attributes are retained across restarts
        self._previous_state = self._state
        self._previous_attributes = self._attributes

class DieligaScheduleSensor(SensorEntity):
    """Sensor to fetch the match schedule."""

    def __init__(self, base_url, liga_id, team_name=None):
        self._base_url = str(base_url)
        self._liga_id = str(liga_id)
        self._team_name = str(team_name)
        self._name = f"dieLiga Schedule {team_name}" if team_name else f"dieLiga Schedule {liga_id}"
        self._state = None
        self._previous_state = None
        self._unique_id = f"dieliga_schedule_{liga_id}"
        self._attributes = {}
        self._icon = "mdi:calendar-month-outline"
        self._attribution = f"Data provided by API {self._base_url}/schedule/schedule/{self._liga_id}?output=xml"
        self._last_updated = None

    async def async_update(self):
        """Fetch the latest match schedule."""
        if self._last_updated and datetime.now() - self._last_updated < timedelta(hours=12):
            _LOGGER.debug("Update skipped; last update was less than 12 hours ago.")
            return
        url = f"{self._base_url}/schedule/schedule/{self._liga_id}?output=xml"
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                self._last_updated = datetime.now()
                if response.status == 200:
                    data = await response.text()
                    # Parse the XML response for the match schedule
                    self._parse_xml(data)
                else:
                    _LOGGER.error("Failed to fetch match schedule, status code: %s", response.status)
        except Exception as e:
            _LOGGER.error("Error fetching match schedule: %s", e)

    def _parse_xml(self, xml_data):
        """Parse the XML data to extract match schedule."""
        try:
            # Parse XML data
            root = ET.fromstring(xml_data)

            # Extract other relevant attributes
            self._attributes = {
                "group": root.find("group").text if root.find("group") is not None else "Unknown",
                "region": root.find("region").text if root.find("region") is not None else "Unknown",
            }

            if self._team_name:
                _LOGGER.debug("Filtering for team_name: %s", self._team_name)
            # Extract match details
            games = []
            completed_games = 0
            total_games = 0
            for day in root.findall(".//day_of_play"):
                for game in day.findall("game"):
                    team_a_name = game.find("team_a").get("name") if game.find("team_a") is not None else "Unknown"
                    team_b_name = game.find("team_b").get("name") if game.find("team_b") is not None else "Unknown"

                    # Only add the game if the team_name is found in either team_a or team_b
                    if self._team_name:
                        if self._team_name.strip().lower() == team_a_name.strip().lower() or self._team_name.strip().lower() == team_b_name.strip().lower():
                            _LOGGER.debug("Keeping game: %s vs %s", team_a_name, team_b_name)
                            game_info = {
                                "game_number": game.find("gamenr").text if game.find("gamenr") is not None else "Unknown",
                                "date": game.find("date").text if game.find("date") is not None else "Unknown",
                                "new_date": game.find("new_date").text if game.find("new_date") is not None else "Unknown",
                                "time": game.find("time").text if game.find("time") is not None else "Unknown",
                                "team_a_name": team_a_name,
                                "team_b_name": team_b_name,
                                "team_a_points": game.find("team_a").get("points") if game.find("team_a") is not None else "0",
                                "team_b_points": game.find("team_b").get("points") if game.find("team_b") is not None else "0",
                                "team_a_sets": game.find("team_a").get("sets") if game.find("team_a") is not None else "0",
                                "team_b_sets": game.find("team_b").get("sets") if game.find("team_b") is not None else "0",
                                "team_a_balls": game.find("team_a").get("balls") if game.find("team_a") is not None else "0",
                                "team_b_balls": game.find("team_b").get("balls") if game.find("team_b") is not None else "0",
                                "state": game.find("state").text if game.find("state") is not None else "Unknown",
                            }
                            games.append(game_info)

                            game_date = game.find("new_date").text if game.find("new_date") is not None and game.find("new_date").text not in ("-", "") else (game.find("date").text if game.find("date") is not None else "Unknown")
                            if game_date != "Unknown":
                                try:
                                    game_date = datetime.strptime(game_date, "%Y-%m-%d")
                                    if game_date < datetime.now():
                                        completed_games += 1
                                except ValueError as e:
                                    _LOGGER.warning("Invalid date format for game %s: %s", game.find("gamenr").text, game_date)
                            else:
                                _LOGGER.debug("Game date is unknown for game %s", game.find("gamenr").text)

                            total_games += 1

                        else:
                            _LOGGER.debug("Skipping game: %s vs %s", team_a_name, team_b_name)
                    else:
                        # If no team_name is provided, include all games
                        _LOGGER.debug("Processing game: %s vs %s", team_a_name, team_b_name)
                        game_info = {
                            "game_number": game.find("gamenr").text if game.find("gamenr") is not None else "Unknown",
                            "date": game.find("date").text if game.find("date") is not None else "Unknown",
                            "new_date": game.find("new_date").text if game.find("new_date") is not None else "Unknown",
                            "time": game.find("time").text if game.find("time") is not None else "Unknown",
                            "team_a_name": team_a_name,
                            "team_b_name": team_b_name,
                            "team_a_points": game.find("team_a").get("points") if game.find("team_a") is not None else "0",
                            "team_b_points": game.find("team_b").get("points") if game.find("team_b") is not None else "0",
                            "team_a_sets": game.find("team_a").get("sets") if game.find("team_a") is not None else "0",
                            "team_b_sets": game.find("team_b").get("sets") if game.find("team_b") is not None else "0",
                            "team_a_balls": game.find("team_a").get("balls") if game.find("team_a") is not None else "0",
                            "team_b_balls": game.find("team_b").get("balls") if game.find("team_b") is not None else "0",
                            "state": game.find("state").text if game.find("state") is not None else "Unknown",
                        }
                        games.append(game_info)

                        game_date = game.find("new_date").text if game.find("new_date") is not None and game.find("new_date").text not in ("-", "") else (game.find("date").text if game.find("date") is not None else "Unknown")
                        if game_date != "Unknown":
                            try:
                                game_date = datetime.strptime(game_date, "%Y-%m-%d")
                                if game_date < datetime.now():
                                    completed_games += 1
                            except ValueError as e:
                                _LOGGER.warning("Invalid date format for game %s: %s", game.find("gamenr").text, game_date)
                        else:
                            _LOGGER.debug("Game date is unknown for game %s", game.find("gamenr").text)

                        total_games += 1

            # Add the games list as an attribute
            self._attributes["games"] = games
            self._attributes["total_games"] = total_games
            self._attributes["completed_games"] = completed_games
            self._attributes["last_updated"] = self._last_updated
            self._attributes["attribution"] = self._attribution

            # If there are games, calculate the completion percentage
            if total_games > 0:
                percentage_completed = (completed_games / total_games) * 100
                _LOGGER.debug("Detected total game count: %s where %s are already completed in the past. Using this to calculate the percentage.", total_games, completed_games)
                self._state = f"{percentage_completed:.0f}"
            else:
                _LOGGER.debug("No games to calculate completion percentage.")
                # Set the league name as the state
                self._state = root.find("league").text if root.find("league") is not None else "Unknown"

        except Exception as e:
            _LOGGER.error("Error parsing XML data: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        if self._state is None:
            return self._previous_state or "Unknown"
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self._attributes:
            return self._previous_attributes
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    async def async_added_to_hass(self):
        """Called when the sensor is added to Home Assistant."""
        # Ensure the previous state and attributes are retained across restarts
        self._previous_state = self._state
        self._previous_attributes = self._attributes

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    base_url = config_entry.data.get("base_url")
    liga_id = str(config_entry.data.get("liga_id"))
    team_name = config_entry.data.get("team_name")

    _LOGGER.debug("Setting up dieLigaSensors for base url: %s with liga id: %s", base_url, liga_id)
    async_add_entities([DieligaScoreboardSensor(base_url, liga_id, team_name), DieligaScheduleSensor(base_url, liga_id, team_name)])