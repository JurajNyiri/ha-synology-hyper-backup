"""The Synology Tasks integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from functools import partial

from homeassistant.components.synology_dsm.const import DOMAIN as SYNOLOGY_DOMAIN
from homeassistant.exceptions import ConfigEntryNotReady
from synology_api.core_backup import Backup

from .const import (
    CONF_API,
    CONF_COORDINATOR,
    CONFIG_DSM_ENTRY_ID,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import SynologyTasksCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType


async def async_setup(hass: HomeAssistant, _: ConfigType) -> bool:
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

        synology_backup = await hass.async_add_executor_job(
            partial(
                Backup,
                ip_address=dsm_entry.data.get("host"),
                port=dsm_entry.data.get("port"),
                username=dsm_entry.data.get("username"),
                password=dsm_entry.data.get("password"),
                secure=dsm_entry.data.get("ssl", True),
                cert_verify=dsm_entry.data.get("verify_ssl", True),
                dsm_version=7,
            )
        )

        coordinator = SynologyTasksCoordinator(hass, synology_backup)
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_COORDINATOR: coordinator,
        CONF_API: synology_backup,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    logout_result = await hass.async_add_executor_job(
        hass.data[DOMAIN][entry.entry_id][CONF_API].logout
    )
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return logout_result and unload_ok
