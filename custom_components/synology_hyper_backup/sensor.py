"""Support for Synology DSM Task sensors."""

from __future__ import annotations
from typing import TYPE_CHECKING

from homeassistant.const import STATE_UNKNOWN
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONFIG_DEVICE_IDENTIFIERS,
    CONFIG_DEVICE_MANUFACTURER,
    CONFIG_DEVICE_MODEL,
    CONFIG_DEVICE_NAME,
    CONFIG_DEVICE_SW_VERSION,
    DOMAIN,
)
from .coordinator import SynologyTasksCoordinator

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType


class SynologyTaskSensor(CoordinatorEntity[SynologyTasksCoordinator], SensorEntity):
    """Representation of a Synology task sensor."""

    def __init__(
        self,
        name: str,
        key: str,
        task: dict,
        coordinator: SynologyTasksCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        task_name_id = name.lower().replace(" ", "_")
        self._attr_unique_id = f"{task_name_id}_{key}"
        self.unique_id = self._attr_unique_id
        self.task = task
        self.key = key
        self._state_is_numeric = self._is_numeric(task.get(key))

        # Set device info from the Synology DSM device
        if config_entry.data.get(CONFIG_DEVICE_IDENTIFIERS):
            identifiers = {
                tuple(identifier)
                for identifier in config_entry.data[CONFIG_DEVICE_IDENTIFIERS]
            }
            self._attr_device_info = DeviceInfo(
                identifiers=identifiers,
                name=config_entry.data.get(CONFIG_DEVICE_NAME),
                manufacturer=config_entry.data.get(CONFIG_DEVICE_MANUFACTURER),
                model=config_entry.data.get(CONFIG_DEVICE_MODEL),
                sw_version=config_entry.data.get(CONFIG_DEVICE_SW_VERSION),
            )

        # Set a clean display name - just the task name
        self._attr_name = f"Hyper Backup: {name} - {key}"
        self._attr_has_entity_name = False

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not (task := self._get_task()):
            return None
        value = task.get(self.key)
        if self._state_is_numeric:
            numeric_value = self._coerce_numeric(value)
            if numeric_value is not None:
                return numeric_value
        if isinstance(value, (dict, list)):
            # Keep state simple; detailed payload goes to attributes
            return STATE_UNKNOWN
        return value

    @property
    def extra_state_attributes(self) -> dict[str, str | int | bool | datetime | None]:
        """Return the state attributes."""
        if not (task := self._get_task()):
            return None
        value = task.get(self.key)
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            return {f"{self.key}_item_{idx}": item for idx, item in enumerate(value)}
        return {}

    def _get_task(self):
        """Get the task data from the coordinator."""
        if not self.coordinator.data:
            return None
        return next(
            (
                task
                for task in self.coordinator.data.get("task_list")
                if task.get("task_id") == self.task.get("task_id")
            ),
            None,
        )

    @staticmethod
    def _is_numeric(value) -> bool:
        """Check if a value is numeric or a numeric string."""
        if isinstance(value, bool):
            return False
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except (TypeError, ValueError):
                return False
        return False

    @staticmethod
    def _coerce_numeric(value):
        """Convert a value to int or float if possible."""
        if isinstance(value, bool) or value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                as_float = float(value)
                return int(as_float) if as_float.is_integer() else as_float
            except (TypeError, ValueError):
                return None
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Synology task sensors."""
    coordinator: SynologyTasksCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    @callback
    def _create_entities(tasks: list) -> list[SynologyTaskSensor]:
        """Create sensor entities for the tasks."""
        entities: list[SynologyTaskSensor] = []

        for task in tasks:
            entities.extend(
                SynologyTaskSensor(
                    name=task.get("name"),
                    key=key,
                    task=task,
                    coordinator=coordinator,
                    config_entry=entry,
                )
                for key in task
            )

        return entities

    task_list = coordinator.data.get("task_list")

    # Create initial entities
    async_add_entities(_create_entities(task_list))

    # Track existing entity IDs to avoid duplicates
    existing_ids = {entity.unique_id for entity in _create_entities(task_list)}

    @callback
    def _async_update_entities() -> None:
        """Create new entities for new tasks."""
        new_entities = []
        current_entities = _create_entities(task_list)

        for entity in current_entities:
            if entity.unique_id not in existing_ids:
                new_entities.append(entity)
                existing_ids.add(entity.unique_id)

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_update_entities)
