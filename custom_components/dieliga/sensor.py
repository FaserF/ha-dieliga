import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_TEAM_NAME
from .coordinator import DieligaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: DieligaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    team_name = config_entry.data.get(CONF_TEAM_NAME)

    async_add_entities(
        [
            DieligaScoreboardSensor(coordinator, team_name),
            DieligaScheduleSensor(coordinator, team_name),
        ]
    )

from homeassistant.helpers.device_registry import DeviceInfo

class DieligaCoordinatorEntity(CoordinatorEntity[DieligaDataUpdateCoordinator]):
    """Base class for Dieliga sensors."""

    def __init__(self, coordinator: DieligaDataUpdateCoordinator, team_name: str | None = None) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._team_name = team_name
        self._attr_attribution = f"Data provided by dieLiga (ID: {coordinator.liga_id})"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.liga_id)},
            name=f"dieLiga {coordinator.liga_id}",
            manufacturer="dieLiga",
            model="League Monitor",
            configuration_url=f"{coordinator.client._base_url}/schedule/overview/{coordinator.liga_id}",
        )

class DieligaScoreboardSensor(DieligaCoordinatorEntity, SensorEntity):
    """Sensor to fetch the league table."""

    _attr_icon = "mdi:podium-gold"

    def __init__(self, coordinator: DieligaDataUpdateCoordinator, team_name: str | None = None) -> None:
        """Initialize the scoreboard sensor."""
        super().__init__(coordinator, team_name)
        self._attr_name = f"dieLiga Scoreboard {team_name}" if team_name else f"dieLiga Scoreboard {coordinator.liga_id}"
        self._attr_unique_id = f"dieliga_table_{coordinator.liga_id}"

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get("scoreboard")
        if not data:
            return None

        if self._team_name:
            for index, team in enumerate(data.get("teams", [])):
                if team["name"].lower() == self._team_name.lower():
                    self._attr_native_unit_of_measurement = "position"
                    return index + 1

        return data.get("league", "Unknown")

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        data = self.coordinator.data.get("scoreboard")
        if not data:
            return {}

        return {
            "group": data.get("group"),
            "region": data.get("region"),
            "last_change": data.get("last_change"),
            "teams": data.get("teams"),
            "last_update_success": self.coordinator.last_update_success,
        }

class DieligaScheduleSensor(DieligaCoordinatorEntity, SensorEntity):
    """Sensor to fetch the match schedule."""

    _attr_icon = "mdi:calendar-month-outline"

    def __init__(self, coordinator: DieligaDataUpdateCoordinator, team_name: str | None = None) -> None:
        """Initialize the schedule sensor."""
        super().__init__(coordinator, team_name)
        self._attr_name = f"dieLiga Schedule {team_name}" if team_name else f"dieLiga Schedule {coordinator.liga_id}"
        self._attr_unique_id = f"dieliga_schedule_{coordinator.liga_id}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get("schedule")
        if not data:
            return None

        total_games = 0
        completed_games = 0

        if self._team_name:
            for game in data.get("games", []):
                if (self._team_name.lower() == game["team_a_name"].lower() or
                    self._team_name.lower() == game["team_b_name"].lower()):
                    total_games += 1
                    # We check if game is completed based on date (simpler than XML state sometimes)
                    # But api.py already calculates completed_games if we want.
                    # However here we are filtering by team.
                    game_date_str = game["new_date"] if game["new_date"] not in ("-", "", "Unknown", "?") else game["date"]
                    if game_date_str not in ("-", "", "Unknown", "?"):
                        try:
                            game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
                            if game_date < datetime.now():
                                completed_games += 1
                        except ValueError:
                            pass
        else:
            total_games = data.get("total_games", 0)
            completed_games = data.get("completed_games", 0)

        if total_games > 0:
            return f"{(completed_games / total_games) * 100:.0f}"

        # If no games for this team, return league name or Unknown
        scoreboard_data = self.coordinator.data.get("scoreboard")
        return scoreboard_data.get("league") if scoreboard_data else "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        data = self.coordinator.data.get("schedule")
        if not data:
            return {}

        games = data.get("games", [])
        if self._team_name:
            games = [
                g for g in games
                if self._team_name.lower() == g["team_a_name"].lower() or
                   self._team_name.lower() == g["team_b_name"].lower()
            ]

        return {
            "group": data.get("group"),
            "region": data.get("region"),
            "games": games,
            "total_games": len(games) if self._team_name else data.get("total_games"),
            "completed_games": sum(1 for g in games if self._is_completed(g)) if self._team_name else data.get("completed_games"),
            "last_update_success": self.coordinator.last_update_success,
        }

    def _is_completed(self, game: dict) -> bool:
        """Check if a game is completed."""
        game_date_str = game["new_date"] if game["new_date"] not in ("-", "", "Unknown", "?") else game["date"]
        if game_date_str not in ("-", "", "Unknown", "?"):
            try:
                game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
                return game_date < datetime.now()
            except ValueError:
                pass
        return False