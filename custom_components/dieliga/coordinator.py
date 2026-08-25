"""Coordinator for dieLiga integration."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DieligaApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DieligaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DieligaApiClient,
        liga_id: str,
        update_interval=timedelta(hours=12),
    ) -> None:
        """Initialize."""
        self.client = client
        self.liga_id = liga_id
        from homeassistant.helpers import storage

        self._store = storage.Store(hass, 1, f"dieliga_{liga_id}_cache")
        self.last_successful_fetch = None

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint concurrently."""
        import asyncio

        from homeassistant.util import dt as dt_util

        # Check stored cache on initial startup
        if self.data is None:
            try:
                cached = await self._store.async_load()
                if cached and isinstance(cached, dict):
                    data = cached.get("data")
                    ts_str = cached.get("timestamp")
                    if data and ts_str:
                        ts = dt_util.parse_datetime(ts_str)
                        if ts and (dt_util.now() - ts) < self.update_interval:
                            _LOGGER.info(
                                "Reusing cached dieLiga data on boot for league %s",
                                self.liga_id,
                            )
                            return data
            except Exception as err:
                _LOGGER.debug("Could not load dieLiga storage cache: %s", err)

        try:
            scoreboard, schedule = await asyncio.gather(
                self.client.async_get_scoreboard(self.liga_id),
                self.client.async_get_schedule(self.liga_id),
            )
            res = {"scoreboard": scoreboard, "schedule": schedule}
            try:
                await self._store.async_save(
                    {
                        "data": res,
                        "timestamp": dt_util.now().isoformat(),
                    }
                )
            except Exception as err:
                _LOGGER.debug("Could not save dieLiga cache to store: %s", err)
            return res
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
