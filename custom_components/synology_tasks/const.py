"""Constants for the Synology Tasks integration."""
from typing import Final

DOMAIN: Final = "synology_tasks"
PLATFORMS: Final = ["sensor", "button"]

# Configuration
CONF_COORDINATOR = "coordinator"

# Services
SERVICE_RUN_TASK = "run_task"

# API
API_LOGIN = "SYNO.API.Auth"
API_METHOD_LOGIN = "login"
API_VERSION_LOGIN = "7"
API_TASK_SCHEDULER = "SYNO.Core.TaskScheduler"
API_VERSION_TASK_SCHEDULER = "3"
API_METHOD_TASK_SCHEDULER = "list"
API_EVENT_SCHEDULER = "SYNO.Core.EventScheduler"
API_METHOD_EVENT_SCHEDULER = "run"
API_VERSION_EVENT_SCHEDULER = "1"

# Attributes
ATTR_TASK_ID = "task_id"
ATTR_TASK_NAME = "task_name"
ATTR_TASK_TYPE = "task_type"
ATTR_TASK_OWNER = "task_owner"
ATTR_TASK_ENABLED = "task_enabled"
ATTR_NEXT_RUN_TIME = "next_run_time"
ATTR_CAN_RUN = "can_run"

# Entity naming
ENTITY_DOMAIN_SENSOR = "sensor"
ENTITY_DOMAIN_BUTTON = "button"
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"
ENTITY_CATEGORY_CONFIG = "config"

# Entity key patterns
KEY_STATUS = "status"
KEY_RUN = "run_task"

# Default values
DEFAULT_SCAN_INTERVAL = 60  # seconds
