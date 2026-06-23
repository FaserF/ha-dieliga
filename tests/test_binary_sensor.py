"""Tests for the dieLiga binary sensor platform."""

from unittest.mock import MagicMock
from datetime import datetime

from homeassistant.core import HomeAssistant
import pytest
from custom_components.dieliga.binary_sensor import DieligaMatchTodayBinarySensor


@pytest.mark.asyncio
async def test_match_today_binary_sensor_is_on(hass: HomeAssistant):
    """Test that the binary sensor is ON if a match is scheduled for today."""
    coordinator = MagicMock()
    coordinator.liga_id = "1234"

    today_str = datetime.now().strftime("%Y-%m-%d")
    coordinator.data = {
        "schedule": {
            "games": [
                {
                    "team_a_name": "Team 1",
                    "team_b_name": "Team 2",
                    "date": today_str,
                    "new_date": "",
                    "time": "10:00",
                    "game_number": "1",
                    "state": "Scheduled",
                }
            ]
        }
    }

    sensor = DieligaMatchTodayBinarySensor(coordinator, team_name="Team 1")
    assert sensor.is_on is True

    sensor_b = DieligaMatchTodayBinarySensor(coordinator, team_name="Team 2")
    assert sensor_b.is_on is True

    sensor_c = DieligaMatchTodayBinarySensor(coordinator, team_name="Team 3")
    assert sensor_c.is_on is False


@pytest.mark.asyncio
async def test_match_today_binary_sensor_new_date(hass: HomeAssistant):
    """Test that the binary sensor checks new_date field correctly."""
    coordinator = MagicMock()
    coordinator.liga_id = "1234"

    today_str = datetime.now().strftime("%Y-%m-%d")
    coordinator.data = {
        "schedule": {
            "games": [
                {
                    "team_a_name": "Team 1",
                    "team_b_name": "Team 2",
                    "date": "2026-01-01",
                    "new_date": today_str,
                    "time": "10:00",
                    "game_number": "1",
                    "state": "Scheduled",
                }
            ]
        }
    }

    sensor = DieligaMatchTodayBinarySensor(coordinator, team_name="Team 1")
    assert sensor.is_on is True
