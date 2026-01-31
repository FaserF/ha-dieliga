"""Tests for the dieLiga sensor platform."""
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.core import HomeAssistant

from custom_components.dieliga.sensor import DieligaScoreboardSensor, DieligaScheduleSensor

async def test_scoreboard_sensor_attributes(hass: HomeAssistant):
    """Test that the scoreboard sensor has correct attributes and doesn't crash."""
    coordinator = MagicMock()
    coordinator.data = {
        "scoreboard": {
            "league": "Test League",
            "region": "Test Region",
            "last_change": "2026-01-31",
            "teams": [{"name": "Team 1", "points": "10"}],
            "group": "Group A",
        }
    }
    coordinator.last_update_success = True
    coordinator.liga_id = "1234"

    sensor = DieligaScoreboardSensor(coordinator, team_name="Team 1")

    # Check attributes
    attrs = sensor.extra_state_attributes
    assert attrs["league"] == "Test League"
    assert attrs["region"] == "Test Region"
    assert attrs["last_update_success"] is True
    # If this had the old last_update_success_time, it would have failed here.

async def test_schedule_sensor_attributes(hass: HomeAssistant):
    """Test that the schedule sensor has correct attributes and doesn't crash."""
    coordinator = MagicMock()
    coordinator.data = {
        "schedule": {
            "group": "Group A",
            "region": "Test Region",
            "total_games": 2,
            "completed_games": 1,
            "games": [
                {
                    "team_a_name": "Team 1",
                    "team_b_name": "Team 2",
                    "date": "2026-01-01",
                    "new_date": "",
                    "time": "10:00",
                    "game_number": "1",
                    "state": "Completed"
                }
            ]
        }
    }
    coordinator.last_update_success = True
    coordinator.liga_id = "1234"

    sensor = DieligaScheduleSensor(coordinator, team_name="Team 1")

    # Check attributes
    attrs = sensor.extra_state_attributes
    assert attrs["group"] == "Group A"
    assert attrs["total_games"] == 1 # Filtered by team
    assert attrs["last_update_success"] is True
