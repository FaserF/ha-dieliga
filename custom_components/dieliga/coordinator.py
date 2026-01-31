"""Coordinator for dieLiga integration."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DieligaApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DieligaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: DieligaApiClient, liga_id: str, update_interval=timedelta(hours=12)) -> None:
        """Initialize."""
        self.client = client
        self.liga_id = liga_id
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            scoreboard = await self.client.async_get_scoreboard(self.liga_id)
            schedule = await self.client.async_get_schedule(self.liga_id)
            return {
                "scoreboard": scoreboard,
                "schedule": schedule
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
