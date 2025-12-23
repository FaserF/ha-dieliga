import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration."""
    _LOGGER.debug("dieLiga integration setup called.")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up dieLiga from a config entry."""
    _LOGGER.debug("Setting up dieLiga entry with entry_id: %s", entry.entry_id)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    hass.data[DOMAIN] = {}
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload dieLiga config entry."""
    _LOGGER.debug("Unloading dieLiga entry with entry_id: %s", entry.entry_id)
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new_unique_id = str(config_entry.unique_id)
        if new_unique_id != config_entry.unique_id:
            _LOGGER.debug("Migrating unique_id from %s to %s", config_entry.unique_id, new_unique_id)
            hass.config_entries.async_update_entry(config_entry, unique_id=new_unique_id)

        config_entry.version = 2

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
