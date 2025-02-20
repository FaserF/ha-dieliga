import logging
import aiohttp
import xml.etree.ElementTree as ET
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_URL
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DieligaTableSensor(SensorEntity):
    """Sensor to fetch the league table."""

    def __init__(self, base_url, liga_id):
        self._base_url = base_url
        self._liga_id = liga_id
        self._name = f"Dieliga Table {liga_id}"
        self._state = None
        self._unique_id = f"dieliga_table_{liga_id}"
        self._attributes = {}
        self._icon = "mdi:volleyball"

    async def async_update(self):
        """Fetch the latest league table."""
        url = f"{self._base_url}/schedule/summary/{self._liga_id}?output=xml"
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
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

            # Set the league name as the state
            self._state = root.find("league").text if root.find("league") is not None else "Unknown"

            # Extract other relevant attributes
            self._attributes = {
                "group": root.find("group").text if root.find("group") is not None else "Unknown",
                "region": root.find("region").text if root.find("region") is not None else "Unknown",
                "last_change": root.find("last_change").text if root.find("last_change") is not None else "Unknown"
            }

            # Extract teams and their information
            teams = []
            for team in root.findall(".//table/team"):
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

            # Add the teams list as an attribute
            self._attributes["teams"] = teams

        except Exception as e:
            _LOGGER.error("Error parsing XML data: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon


class DieligaScheduleSensor(SensorEntity):
    """Sensor to fetch the match schedule."""

    def __init__(self, base_url, liga_id):
        self._base_url = base_url
        self._liga_id = liga_id
        self._name = f"Dieliga Schedule {liga_id}"
        self._state = None
        self._unique_id = f"dieliga_schedule_{liga_id}"
        self._attributes = {}
        self._icon = "mdi:volleyball"

    async def async_update(self):
        """Fetch the latest match schedule."""
        url = f"{self._base_url}/schedule/schedule/{self._liga_id}?output=xml"
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
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

            # Set the league name as the state
            self._state = root.find("league").text if root.find("league") is not None else "Unknown"

            # Extract other relevant attributes
            self._attributes = {
                "group": root.find("group").text if root.find("group") is not None else "Unknown",
                "region": root.find("region").text if root.find("region") is not None else "Unknown",
                "last_change": root.find("last_change").text if root.find("last_change") is not None else "Unknown"
            }

            # Extract match details
            games = []
            for day in root.findall(".//day_of_play"):
                for game in day.findall("game"):
                    game_info = {
                        "game_number": game.find("gamenr").text if game.find("gamenr") is not None else "Unknown",
                        "date": game.find("date").text if game.find("date") is not None else "Unknown",
                        "new_date": game.find("new_date").text if game.find("new_date") is not None else "Unknown",
                        "time": game.find("time").text if game.find("time") is not None else "Unknown",
                        "team_a_name": game.find("team_a").get("name") if game.find("team_a") is not None else "Unknown",
                        "team_b_name": game.find("team_b").get("name") if game.find("team_b") is not None else "Unknown",
                        "team_a_points": game.find("team_a").get("points") if game.find("team_a") is not None else "0",
                        "team_b_points": game.find("team_b").get("points") if game.find("team_b") is not None else "0",
                        "team_a_sets": game.find("team_a").get("sets") if game.find("team_a") is not None else "0",
                        "team_b_sets": game.find("team_b").get("sets") if game.find("team_b") is not None else "0",
                        "team_a_balls": game.find("team_a").get("balls") if game.find("team_a") is not None else "0",
                        "team_b_balls": game.find("team_b").get("balls") if game.find("team_b") is not None else "0",
                        "state": game.find("state").text if game.find("state") is not None else "Unknown",
                    }
                    games.append(game_info)

            # Add the games list as an attribute
            self._attributes["games"] = games

        except Exception as e:
            _LOGGER.error("Error parsing XML data: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    base_url = config_entry.data.get("base_url")
    liga_id = config_entry.data.get("liga_id")

    _LOGGER.debug("Setting up dieLigaSensors for base url: %s with liga id: %s", base_url, liga_id)
    async_add_entities([DieligaTableSensor(base_url, liga_id), DieligaScheduleSensor(base_url, liga_id)])