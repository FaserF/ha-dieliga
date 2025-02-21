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
