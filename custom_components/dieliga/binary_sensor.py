"""Binary sensor platform for dieLiga."""
import logging
from datetime import datetime

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_TEAM_NAME
from .coordinator import DieligaDataUpdateCoordinator
from .sensor import DieligaCoordinatorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: DieligaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    team_name = config_entry.data.get(CONF_TEAM_NAME)

    if team_name:
        async_add_entities([DieligaMatchTodayBinarySensor(coordinator, team_name)])

class DieligaMatchTodayBinarySensor(DieligaCoordinatorEntity, BinarySensorEntity):
    """Binary sensor to indicate if a match is scheduled for today."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_icon = "mdi:soccer"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: DieligaDataUpdateCoordinator, team_name: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, team_name)
        self._attr_name = f"dieLiga Match Today {team_name}"
        self._attr_unique_id = f"dieliga_match_today_{coordinator.liga_id}_{team_name.replace(' ', '_').lower()}"

    @property
    def is_on(self) -> bool:
        """Return true if a match is scheduled for today."""
        data = self.coordinator.data.get("schedule")
        if not data:
            return False

        today_str = datetime.now().strftime("%Y-%m-%d")

        for game in data.get("games", []):
            if (self._team_name.lower() == game["team_a_name"].lower() or
                self._team_name.lower() == game["team_b_name"].lower()):

                game_date_str = game["new_date"] if game["new_date"] not in ("-", "", "Unknown", "?") else game["date"]
                if game_date_str == today_str:
                    return True

        return False
