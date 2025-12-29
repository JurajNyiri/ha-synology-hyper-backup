"""Key-specific metadata for Synology Hyper Backup sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfInformation


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
        state_class=SensorStateClass.MEASUREMENT,
        numeric=True,
    ),
    "status_progress_total_size": KeyOverride(
        name="Progress: Total Size",
        unit=UnitOfInformation.BYTES,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        numeric=True,
    ),
    "status_progress_processed_size": KeyOverride(
        name="Progress: Processed Size",
        unit=UnitOfInformation.BYTES,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        numeric=True,
    ),
    "status_progress_scan_file_count": KeyOverride(
        name="Progress: Files Scanned",
        state_class=SensorStateClass.TOTAL,
        numeric=True,
    ),
    "status_progress_transmitted_size": KeyOverride(
        name="Progress: Transmitted Size",
        unit=UnitOfInformation.BYTES,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        numeric=True,
    ),
}
