"""Diagnostics support for dieLiga."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    from homeassistant.components.diagnostics import async_redact_data
    from .const import DOMAIN

    coordinator = hass.data[DOMAIN][entry.entry_id]

    to_redact = {
        "entry_id",
    }

    diagnostics_data = {
        "config_entry": async_redact_data(entry.as_dict(), to_redact),
        "coordinator_data": {
            "liga_id": coordinator.liga_id,
            "data": coordinator.data,
        },
    }

    return diagnostics_data
