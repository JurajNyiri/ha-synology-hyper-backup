"""Config flow for Synology Tasks integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components.synology_dsm.const import DOMAIN as SYNOLOGY_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_user_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate that the synology_dsm entry exists and is working."""
    if not (dsm_entry := next(
        (
            entry
            for entry in hass.config_entries.async_entries(SYNOLOGY_DOMAIN)
            if entry.entry_id == data["dsm_entry_id"]
        ),
        None,
    )):
        raise InvalidDSMEntry

    if not dsm_entry.state.recoverable:
        raise InvalidDSMEntry


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
            return self.async_abort(reason="no_dsm_instances")

        # Get the user to select a pre-configured Synology DSM instance.
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=self.add_suggested_values_to_schema(
                    config_entries.vol.Schema(
                        {
                            config_entries.vol.Required("dsm_entry_id"): config_entries.vol.In(
                                dsm_entries
                            ),
                        }
                    ),
                    user_input or {},
                ),
            )

        # Validate the selected Synology DSM instance.
        try:
            await validate_user_input(self.hass, user_input)
        except InvalidDSMEntry as err:
            return self.async_abort(reason=err.reason)
        except Exception:
            return self.async_abort(reason="unknown")
        else:
            await self.async_set_unique_id(user_input["dsm_entry_id"])
            self._abort_if_unique_id_configured()

            # Get the device info for the Synology DSM instance.
            device_registry = dr.async_get(self.hass)
            # Find the device associated with the DSM config entry
            dsm_devices = dr.async_entries_for_config_entry(device_registry, user_input["dsm_entry_id"])
            if dsm_devices:
                # Use the first device (there should typically be only one)
                device_info = dsm_devices[0]
                user_input["device_identifiers"] = device_info.identifiers
                user_input["device_name"] = device_info.name
                user_input["device_manufacturer"] = device_info.manufacturer
                user_input["device_model"] = device_info.model
                user_input["device_sw_version"] = device_info.sw_version

            # Create the config entry for the Synology Tasks integration.
            return self.async_create_entry(
                title=dsm_entries[user_input["dsm_entry_id"]],
                data=user_input,
            )

class InvalidDSMEntry(HomeAssistantError):
    """Error to indicate the DSM entry is invalid."""
    reason = "invalid_dsm_entry"
