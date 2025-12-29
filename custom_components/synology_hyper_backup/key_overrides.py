"""Key-specific metadata for Synology Hyper Backup sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE


@dataclass(frozen=True)
class KeyOverride:
    """Metadata overrides for a specific task key."""

    name: Optional[str] = None
    unit: Optional[str] = None
    state_class: SensorStateClass | None = None
    device_class: SensorDeviceClass | None = None
    numeric: bool | None = None


KEY_OVERRIDES: dict[str, KeyOverride] = {
    "status_progress_progress": KeyOverride(
        name="Progress",
        unit=PERCENTAGE,
        numeric=True,
    )
}
