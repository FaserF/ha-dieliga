"""API Client for dieLiga."""

import logging
from typing import Any
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

    def _parse_scoreboard_xml(self, xml_data: str) -> dict[str, Any]:
        """Parse the scoreboard XML."""
        root = ET.fromstring(xml_data)

        data: dict[str, Any] = {
            "group": root.findtext("group", "Unknown"),
            "region": root.findtext("region", "Unknown"),
            "last_change": root.findtext("last_change", "Unknown"),
            "league": root.findtext("league", "Unknown"),
            "teams": [],
        }

        for team in root.findall(".//table/team"):
            points_el = team.find("points")
            sets_el = team.find("sets")
            balls_el = team.find("balls")
            
            data["teams"].append(
                {
                    "name": team.findtext("name", "Unknown"),
                    "points_positive": points_el.get("positive", "0")
                    if points_el is not None
                    else "0",
                    "points_negative": points_el.get("negative", "0")
                    if points_el is not None
                    else "0",
                    "sets_positive": sets_el.get("positive", "0")
                    if sets_el is not None
                    else "0",
                    "sets_negative": sets_el.get("negative", "0")
                    if sets_el is not None
                    else "0",
                    "balls_positive": balls_el.get("positive", "0")
                    if balls_el is not None
                    else "0",
                    "balls_negative": balls_el.get("negative", "0")
                    if balls_el is not None
                    else "0",
                    "games": team.findtext("games", "0"),
                    "games_won": team.findtext("games_won", "0"),
                }
            )

        return data

    def _parse_schedule_xml(self, xml_data: str) -> dict[str, Any]:
        """Parse the schedule XML."""
        root = ET.fromstring(xml_data)

        data: dict[str, Any] = {
            "group": root.findtext("group", "Unknown"),
            "region": root.findtext("region", "Unknown"),
            "games": [],
            "total_games": 0,
            "completed_games": 0,
        }

        now = datetime.now()

        for day in root.findall(".//day_of_play"):
            for game in day.findall("game"):
                team_a = game.find("team_a")
                team_b = game.find("team_b")
                
                game_info = {
                    "game_number": game.findtext("gamenr", "Unknown"),
                    "date": game.findtext("date", "Unknown"),
                    "new_date": game.findtext("new_date", "Unknown"),
                    "time": game.findtext("time", "Unknown"),
                    "team_a_name": team_a.get("name", "Unknown")
                    if team_a is not None
                    else "Unknown",
                    "team_b_name": team_b.get("name", "Unknown")
                    if team_b is not None
                    else "Unknown",
                    "team_a_points": team_a.get("points", "0")
                    if team_a is not None
                    else "0",
                    "team_b_points": team_b.get("points", "0")
                    if team_b is not None
                    else "0",
                    "team_a_sets": team_a.get("sets", "0")
                    if team_a is not None
                    else "0",
                    "team_b_sets": team_b.get("sets", "0")
                    if team_b is not None
                    else "0",
                    "team_a_balls": team_a.get("balls", "0")
                    if team_a is not None
                    else "0",
                    "team_b_balls": team_b.get("balls", "0")
                    if team_b is not None
                    else "0",
                    "state": game.findtext("state", "Unknown"),
                }

                data["games"].append(game_info)
                data["total_games"] += 1

                # Check if game is completed
                game_date_str = (
                    game_info["new_date"]
                    if game_info["new_date"] not in ("-", "", "Unknown", "?")
                    else game_info["date"]
                )
                if game_date_str not in ("-", "", "Unknown", "?"):
                    try:
                        # Dates in XML tend to be YYYY-MM-DD
                        game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
                        if game_date < now:
                            data["completed_games"] += 1
                    except ValueError:
                        _LOGGER.debug("Invalid date format: %s", game_date_str)

        return data
