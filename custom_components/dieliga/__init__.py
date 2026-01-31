import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DieligaApiClient
from .coordinator import DieligaDataUpdateCoordinator
from .const import DOMAIN, CONF_URL, CONF_LIGA_ID, CONF_REFRESH_TIME

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "calendar"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up dieLiga from a config entry."""
    _LOGGER.debug("Setting up dieLiga entry with entry_id: %s", entry.entry_id)

    base_url = entry.data[CONF_URL]
    liga_id = str(entry.data[CONF_LIGA_ID])

    # Use refresh time from options if available, otherwise default to 12
    refresh_time = entry.options.get(CONF_REFRESH_TIME, 12)

    session = async_get_clientsession(hass)
    client = DieligaApiClient(session, base_url)

    coordinator = DieligaDataUpdateCoordinator(
        hass,
        client,
        liga_id,
        update_interval=timedelta(hours=refresh_time)
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add listener to handle options updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    coordinator: DieligaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    refresh_time = entry.options.get(CONF_REFRESH_TIME, 12)
    _LOGGER.debug("Updating refresh interval to %s hours", refresh_time)
    coordinator.update_interval = timedelta(hours=refresh_time)
    await coordinator.async_request_refresh()

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new_data = {**config_entry.data}
        # In version 2, we might want to ensure certain keys exist
        # However, the current logic is robust enough.
        # We just bump the version to 2.
        hass.config_entries.async_update_entry(config_entry, data=new_data, version=2)

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload dieLiga config entry."""
    _LOGGER.debug("Unloading dieLiga entry with entry_id: %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
