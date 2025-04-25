"""The Ezetrol Touch integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)  # Add logger

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ezetrol Touch from a config entry."""
    _LOGGER.debug("Starting setup for Ezetrol Touch with entry: %s", entry.data)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform
    _LOGGER.debug("Forwarding setup to sensor platform")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("Ezetrol Touch setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Ezetrol Touch entry: %s", entry.entry_id)
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Ezetrol Touch unloaded successfully")
        return True
    _LOGGER.warning("Failed to unload Ezetrol Touch")
    return False