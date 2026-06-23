"""Tests for the dieLiga calendar platform."""

from unittest.mock import MagicMock
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
import pytest
from custom_components.dieliga.calendar import DieligaCalendarEntity


@pytest.mark.asyncio
async def test_calendar_events(hass: HomeAssistant):
    """Test calendar entity methods and attributes."""
    coordinator = MagicMock()
    coordinator.liga_id = "1234"

    start_date = dt_util.as_local(datetime(2026, 1, 1, 10, 0))
    end_date = start_date + timedelta(hours=2)

    coordinator.data = {
        "scoreboard": {
            "region": "Test Region",
        },
        "schedule": {
            "games": [
                {
                    "team_a_name": "Team 1",
                    "team_b_name": "Team 2",
                    "date": "2026-01-01",
                    "new_date": "",
                    "time": "10:00",
                    "game_number": "1",
                    "state": "Scheduled",
                },
                {
                    "team_a_name": "Team 3",
                    "team_b_name": "Team 4",
                    "date": "2026-01-02",
                    "new_date": "",
                    "time": "14:00",
                    "game_number": "2",
                    "state": "Scheduled",
                },
            ]
        },
    }

    calendar = DieligaCalendarEntity(coordinator, team_name="Team 1")

    # Get events
    events = await calendar.async_get_events(
        hass,
        dt_util.as_local(datetime(2026, 1, 1, 0, 0)),
        dt_util.as_local(datetime(2026, 1, 1, 23, 59)),
    )

    assert len(events) == 1
    event = events[0]
    assert event.summary == "Team 1 vs Team 2"
    assert event.start == start_date
    assert event.end == end_date
    assert event.location == "Test Region"

    assert calendar.name == "dieLiga Calendar Team 1"
    assert calendar.unique_id == "dieliga_calendar_1234"
