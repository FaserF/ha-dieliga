"""API Client for dieLiga."""
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

import aiohttp

_LOGGER = logging.getLogger(__name__)

class DieligaApiClient:
    """API Client for dieLiga."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str):
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def async_get_scoreboard(self, liga_id: str) -> dict:
        """Fetch the scoreboard for a given liga_id."""
        url = f"{self._base_url}/schedule/summary/{liga_id}?output=xml"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                return self._parse_scoreboard_xml(text)
        except Exception as e:
            _LOGGER.error("Error fetching scoreboard: %s", e)
            raise

    async def async_get_schedule(self, liga_id: str) -> dict:
        """Fetch the schedule for a given liga_id."""
        url = f"{self._base_url}/schedule/schedule/{liga_id}?output=xml"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                return self._parse_schedule_xml(text)
        except Exception as e:
            _LOGGER.error("Error fetching schedule: %s", e)
            raise

    def _parse_scoreboard_xml(self, xml_data: str) -> dict:
        """Parse the scoreboard XML."""
        root = ET.fromstring(xml_data)

        data = {
            "group": root.findtext("group", "Unknown"),
            "region": root.findtext("region", "Unknown"),
            "last_change": root.findtext("last_change", "Unknown"),
            "league": root.findtext("league", "Unknown"),
            "teams": [],
        }

        for team in root.findall(".//table/team"):
            data["teams"].append({
                "name": team.findtext("name", "Unknown"),
                "points_positive": team.find("points").get("positive", "0") if team.find("points") is not None else "0",
                "points_negative": team.find("points").get("negative", "0") if team.find("points") is not None else "0",
                "sets_positive": team.find("sets").get("positive", "0") if team.find("sets") is not None else "0",
                "sets_negative": team.find("sets").get("negative", "0") if team.find("sets") is not None else "0",
                "balls_positive": team.find("balls").get("positive", "0") if team.find("balls") is not None else "0",
                "balls_negative": team.find("balls").get("negative", "0") if team.find("balls") is not None else "0",
                "games": team.findtext("games", "0"),
                "games_won": team.findtext("games_won", "0"),
            })

        return data

    def _parse_schedule_xml(self, xml_data: str) -> dict:
        """Parse the schedule XML."""
        root = ET.fromstring(xml_data)

        data = {
            "group": root.findtext("group", "Unknown"),
            "region": root.findtext("region", "Unknown"),
            "games": [],
            "total_games": 0,
            "completed_games": 0,
        }

        now = datetime.now()

        for day in root.findall(".//day_of_play"):
            for game in day.findall("game"):
                game_info = {
                     "game_number": game.findtext("gamenr", "Unknown"),
                     "date": game.findtext("date", "Unknown"),
                     "new_date": game.findtext("new_date", "Unknown"),
                     "time": game.findtext("time", "Unknown"),
                     "team_a_name": game.find("team_a").get("name", "Unknown") if game.find("team_a") is not None else "Unknown",
                     "team_b_name": game.find("team_b").get("name", "Unknown") if game.find("team_b") is not None else "Unknown",
                     "team_a_points": game.find("team_a").get("points", "0") if game.find("team_a") is not None else "0",
                     "team_b_points": game.find("team_b").get("points", "0") if game.find("team_b") is not None else "0",
                     "team_a_sets": game.find("team_a").get("sets", "0") if game.find("team_a") is not None else "0",
                     "team_b_sets": game.find("team_b").get("sets", "0") if game.find("team_b") is not None else "0",
                     "team_a_balls": game.find("team_a").get("balls", "0") if game.find("team_a") is not None else "0",
                     "team_b_balls": game.find("team_b").get("balls", "0") if game.find("team_b") is not None else "0",
                     "state": game.findtext("state", "Unknown"),
                }

                data["games"].append(game_info)
                data["total_games"] += 1

                # Check if game is completed
                game_date_str = game_info["new_date"] if game_info["new_date"] not in ("-", "", "Unknown", "?") else game_info["date"]
                if game_date_str not in ("-", "", "Unknown", "?"):
                    try:
                         # Dates in XML tend to be YYYY-MM-DD
                        game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
                        if game_date < now:
                            data["completed_games"] += 1
                    except ValueError:
                         _LOGGER.debug("Invalid date format: %s", game_date_str)

        return data
