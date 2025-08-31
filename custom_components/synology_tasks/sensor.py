"""Support for Synology DSM Task sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CAN_RUN,
    ATTR_NEXT_RUN_TIME,
    ATTR_TASK_ENABLED,
    ATTR_TASK_ID,
    ATTR_TASK_NAME,
    ATTR_TASK_OWNER,
    ATTR_TASK_TYPE,
    DOMAIN,
)
from .coordinator import SynologyTasksCoordinator
from .models import Task

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynologyTaskSensorEntityDescription(SensorEntityDescription):
    """Class describing Synology task sensor entities."""

    value_fn: Callable[[Task], StateType] = lambda task: None


TASK_SENSORS = [
    SynologyTaskSensorEntityDescription(
        key="task_status",
        translation_key="task_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda task: "enabled" if task.enabled else "disabled",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Synology task sensors."""
    coordinator: SynologyTasksCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    @callback
    def _create_entities(tasks: list[Task]) -> list[SynologyTaskSensor]:
        """Create sensor entities for the tasks."""
        entities: list[SynologyTaskSensor] = []

        for task in tasks:
            for description in TASK_SENSORS:
                entities.append(
                    SynologyTaskSensor(
                        coordinator=coordinator,
                        task=task,
                        entity_description=description,
                    )
                )

        return entities

    coordinator.async_add_listener(
        lambda: async_add_entities(_create_entities(coordinator.data))
    )

    async_add_entities(_create_entities(coordinator.data))


class SynologyTaskSensor(CoordinatorEntity[SynologyTasksCoordinator], SensorEntity):
    """Representation of a Synology task sensor."""

    entity_description: SynologyTaskSensorEntityDescription

    def __init__(
        self,
        coordinator: SynologyTasksCoordinator,
        task: Task,
        entity_description: SynologyTaskSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._task = task
        self._attr_unique_id = f"{task.id}_{entity_description.key}"
        self._attr_device_info = None  # Tasks don't have a physical device
        self._attr_has_entity_name = True
        self._attr_name = task.name

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not (task := self._get_task()):
            return None
        return self.entity_description.value_fn(task)

    @property
    def extra_state_attributes(self) -> dict[str, str | int | bool | datetime | None]:
        """Return the state attributes."""
        if not (task := self._get_task()):
            return {}

        return {
            ATTR_TASK_ID: task.id,
            ATTR_TASK_NAME: task.name,
            ATTR_TASK_TYPE: task.type,
            ATTR_TASK_OWNER: task.owner,
            ATTR_TASK_ENABLED: task.enabled,
            ATTR_NEXT_RUN_TIME: task.next_run_time,
            ATTR_CAN_RUN: task.can_run,
        }

    def _get_task(self) -> Task | None:
        """Get the task data from the coordinator."""
        if not self.coordinator.data:
            return None
        return next(
            (task for task in self.coordinator.data if task.id == self._task.id),
            None,
        )
