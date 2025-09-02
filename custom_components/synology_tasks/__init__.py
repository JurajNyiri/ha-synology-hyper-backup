"""The Synology Tasks integration."""
from __future__ import annotations

import logging

from homeassistant.components.synology_dsm.const import DOMAIN as SYNOLOGY_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_COORDINATOR,
    DOMAIN,
    PLATFORMS,
    SERVICE_RUN_TASK,
    CONFIG_DSM_ENTRY_ID,
    SERVICE_DATA_TASK_NAME,
)
from .coordinator import SynologyTasksCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Synology Tasks component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Synology Tasks from a config entry."""
    try:
        # Get synology_dsm entry to create the SynologyDSM client.
        dsm_entry = next(
            e
            for e in hass.config_entries.async_entries(SYNOLOGY_DOMAIN)
            if e.entry_id == entry.data.get(CONFIG_DSM_ENTRY_ID)
        )

        # Fetch initial data so we have data when entities subscribe
        #
        # If the refresh fails, async_config_entry_first_refresh will
        # raise ConfigEntryNotReady and setup will try again later
        #
        # If you do not want to retry setup on failure, use
        # coordinator.async_refresh() instead
        #
        coordinator = SynologyTasksCoordinator(hass, dsm_entry)
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_COORDINATOR: coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def async_run_task_service(call: ServiceCall) -> None:
        """Run a task by name."""
        await coordinator.api.run_task(call.data[SERVICE_DATA_TASK_NAME])

    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_TASK,
        async_run_task_service,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
