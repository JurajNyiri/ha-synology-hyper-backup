"""Config flow for Synology Tasks integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant import config_entries
from homeassistant.components.synology_dsm.const import DOMAIN as SYNOLOGY_DOMAIN
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import (
    CONFIG_DEVICE_IDENTIFIERS,
    CONFIG_DEVICE_MANUFACTURER,
    CONFIG_DEVICE_MODEL,
    CONFIG_DEVICE_NAME,
    CONFIG_DEVICE_SW_VERSION,
    CONFIG_DSM_ENTRY_ID,
    DOMAIN,
    REASON_INVALID_DSM_ENTRY,
    REASON_NO_DSM_INSTANCES,
    REASON_UNKNOWN,
    STEP_USER,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)


async def validate_user_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate that the synology_dsm entry exists and is working."""
    if not (
        dsm_entry := next(
            (
                entry
                for entry in hass.config_entries.async_entries(SYNOLOGY_DOMAIN)
                if entry.entry_id == data[CONFIG_DSM_ENTRY_ID]
            ),
            None,
        )
    ):
        raise InvalidDSMEntryError

    if not dsm_entry.state.recoverable:
        raise InvalidDSMEntryError


class SynologyTasksConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Synology Tasks."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Setup the initial Synology Tasks integration."""
        # Only configure against Synology DSM instances that are setup
        # through the Home Assistant Core Synology DSM integration.
        dsm_entries = {
            entry.entry_id: entry.title
            for entry in self.hass.config_entries.async_entries(SYNOLOGY_DOMAIN)
            if entry.state.recoverable
        }

        if not dsm_entries:
            # No Synology DSM instances configured through the Home Assistant
            # Core Synology DSM integration, abort.
            return self.async_abort(reason=REASON_NO_DSM_INSTANCES)

        # Get the user to select a pre-configured Synology DSM instance.
        if user_input is None:
            return self.async_show_form(
                step_id=STEP_USER,
                data_schema=self.add_suggested_values_to_schema(
                    config_entries.vol.Schema(
                        {
                            config_entries.vol.Required(
                                CONFIG_DSM_ENTRY_ID
                            ): config_entries.vol.In(dsm_entries),
                        }
                    ),
                    user_input or {},
                ),
            )

        # Validate the selected Synology DSM instance.
        try:
            await validate_user_input(self.hass, user_input)
        except InvalidDSMEntryError as err:
            return self.async_abort(reason=err.reason)
        except Exception:
            _LOGGER.exception("Unexpected error during config flow")
            return self.async_abort(reason=REASON_UNKNOWN)
        else:
            await self.async_set_unique_id(user_input[CONFIG_DSM_ENTRY_ID])
            self._abort_if_unique_id_configured()

            # Get the device info for the Synology DSM instance.
            device_registry = dr.async_get(self.hass)
            # Find the device associated with the DSM config entry
            dsm_devices = dr.async_entries_for_config_entry(
                device_registry, user_input[CONFIG_DSM_ENTRY_ID]
            )
            if dsm_devices:
                # Use the first device (there should typically be only one)
                device_info = dsm_devices[0]
                user_input[CONFIG_DEVICE_IDENTIFIERS] = device_info.identifiers
                user_input[CONFIG_DEVICE_NAME] = device_info.name
                user_input[CONFIG_DEVICE_MANUFACTURER] = device_info.manufacturer
                user_input[CONFIG_DEVICE_MODEL] = device_info.model
                user_input[CONFIG_DEVICE_SW_VERSION] = device_info.sw_version

            # Create the config entry for the Synology Tasks integration.
            return self.async_create_entry(
                title=dsm_entries[user_input[CONFIG_DSM_ENTRY_ID]],
                data=user_input,
            )


class InvalidDSMEntryError(HomeAssistantError):
    """Error to indicate the DSM entry is invalid."""

    reason = REASON_INVALID_DSM_ENTRY
