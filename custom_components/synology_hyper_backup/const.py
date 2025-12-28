"""Constants for the Synology Tasks integration."""

from typing import Final
import logging

DOMAIN: Final = "synology_hyper_backup"
PLATFORMS: Final = ["sensor"]

# Configuration
CONF_COORDINATOR = "coordinator"
CONF_API = "api"

LOGGER = logging.getLogger("custom_components." + DOMAIN)

# Config Flow Keys
CONFIG_DSM_ENTRY_ID = "dsm_entry_id"
CONFIG_DEVICE_IDENTIFIERS = "device_identifiers"
CONFIG_DEVICE_NAME = "device_name"
CONFIG_DEVICE_MANUFACTURER = "device_manufacturer"
CONFIG_DEVICE_MODEL = "device_model"
CONFIG_DEVICE_SW_VERSION = "device_sw_version"

# Config Flow Step and Reason Constants
STEP_USER = "user"
REASON_NO_DSM_INSTANCES = "no_dsm_instances"
REASON_UNKNOWN = "unknown"
REASON_INVALID_DSM_ENTRY = "invalid_dsm_entry"

# Default values
DEFAULT_SCAN_INTERVAL = 60  # seconds
