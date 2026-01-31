"""Calendar platform for dieLiga."""
import logging
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    """Set up the calendar platform."""
    coordinator: DieligaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    team_name = config_entry.data.get(CONF_TEAM_NAME)

    async_add_entities([DieligaCalendarEntity(coordinator, team_name)])

class DieligaCalendarEntity(DieligaCoordinatorEntity, CalendarEntity):
    """Calendar entity for dieLiga matches."""

    def __init__(self, coordinator: DieligaDataUpdateCoordinator, team_name: str | None = None) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator, team_name)
        self._attr_name = f"dieLiga Calendar {team_name}" if team_name else f"dieLiga Calendar {coordinator.liga_id}"
        self._attr_unique_id = f"dieliga_calendar_{coordinator.liga_id}"
        self._events: list[CalendarEvent] = []

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = datetime.now()
        upcoming_events = [e for e in self._events if e.end > now]
        if upcoming_events:
            return sorted(upcoming_events, key=lambda x: x.start)[0]
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events between two bound dates."""
        self._update_events()
        return [
            e for e in self._events
            if e.start >= start_date and e.start <= end_date
        ]

    def _update_events(self) -> None:
        """Update the internal list of calendar events."""
        data = self.coordinator.data.get("schedule")
        if not data:
            self._events = []
            return

        events = []
        for game in data.get("games", []):
            # If team_name is set, only show games for that team
            if self._team_name:
                if (self._team_name.lower() != game["team_a_name"].lower() and
                    self._team_name.lower() != game["team_b_name"].lower()):
                    continue

            game_date_str = game["new_date"] if game["new_date"] not in ("-", "", "Unknown", "?") else game["date"]
            game_time_str = game["time"] if game["time"] not in ("-", "", "Unknown", "?") else "00:00"

            if game_date_str == "Unknown":
                continue

            try:
                # dieLiga times are often just HH:MM
                start_dt = datetime.strptime(f"{game_date_str} {game_time_str}", "%Y-%m-%d %H:%M")
                # Assume 2 hours duration for a match
                end_dt = start_dt + timedelta(hours=2)

                event = CalendarEvent(
                    summary=f"{game['team_a_name']} vs {game['team_b_name']}",
                    start=start_dt,
                    end=end_dt,
                    description=f"Match number: {game['game_number']}. Status: {game['state']}",
                    location=self.coordinator.data.get("scoreboard", {}).get("region", "Unknown"),
                )
                events.append(event)
            except ValueError:
                _LOGGER.debug("Could not parse date/time for game %s: %s %s", game['game_number'], game_date_str, game_time_str)

        self._events = events
