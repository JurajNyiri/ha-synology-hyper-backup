"""API client for Synology DSM."""
from __future__ import annotations

import json
import logging
from typing import List
import requests

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry

from .const import (
    API_LOGIN,
    API_METHOD_LOGIN,
    API_VERSION_LOGIN,
    API_ENTRY_REQUEST,
    API_METHOD_REQUEST,
    API_TASK_SCHEDULER,
    API_METHOD_TASK_SCHEDULER,
    API_VERSION_REQUEST,
    API_VERSION_TASK_SCHEDULER,
    API_EVENT_SCHEDULER,
    API_METHOD_EVENT_SCHEDULER,
    API_VERSION_EVENT_SCHEDULER,
)
from .models import SynologyAuthData, Task, SynologyTaskData, SynologyResponse, SynologyTask

_LOGGER = logging.getLogger(__name__)


class SynologyDSM:
    """Synology DSM API client."""

    def __init__(self, hass: HomeAssistant, dsm_entry: ConfigEntry) -> None:
        """Initialize the API client."""
        self.hass = hass

        host = dsm_entry.data.get("host")
        port = dsm_entry.data.get("port")
        ssl = dsm_entry.data.get("ssl", True)

        self._verify_ssl = dsm_entry.data.get("verify_ssl", True)
        self._username = dsm_entry.data.get("username")
        self._password = dsm_entry.data.get("password")
        self._url = f"{ssl and 'https' or 'http'}://{host}:{port}/webapi/entry.cgi"

        self._session = None
        self._sid = None
        self._synotoken = None


    async def get_tasks(self) -> list[Task]:
        """Get list of tasks."""
        params = {
            "api": API_TASK_SCHEDULER,
            "method": API_METHOD_TASK_SCHEDULER,
            "version": API_VERSION_TASK_SCHEDULER,
            "sort_by": "name",
            "sort_direction": "asc",
            "limit": "50",
            "offset": "0",
        }

        try:
            response = await self.hass.async_add_executor_job(self._sync_request, params)
        except Exception as err:
            _LOGGER.error("Error getting tasks: %s", err)
            raise SynologyTaskRunError from err

        tasks_data: SynologyTaskData = response.get("data", {})
        tasks: List[SynologyTask] = tasks_data.get("tasks", [])
        return [Task.from_api(task) for task in tasks]


    async def run_task(self, task_name: str) -> None:
        """Run a task by name."""
        params = {
            "api": API_ENTRY_REQUEST,
            "method": API_METHOD_REQUEST,
            "version": API_VERSION_REQUEST,
            "stop_when_error": "false",
            "mode": "sequential",
            "compound": json.dumps({
                "api": API_EVENT_SCHEDULER,
                "method": API_METHOD_EVENT_SCHEDULER,
                "version": API_VERSION_EVENT_SCHEDULER,
                "task_name": task_name
            })
        }

        try:
            await self.hass.async_add_executor_job(self._sync_request, params)
        except Exception as err:
            _LOGGER.error("Error running task %s: %s", task_name, err)
            raise SynologyTaskRunError from err


    def _sync_login(self) -> None:
        """Login to the DSM."""
        if self._session is None:
            self._session = requests.Session()

        params = {
            "api": API_LOGIN,
            "version": API_VERSION_LOGIN,
            "method": API_METHOD_LOGIN,
            "enable_syno_token": "yes",
            "account": self._username,
            "passwd": self._password,
        }

        response = self._sync_request(params, True)
        data: SynologyAuthData = response.get("data", {})
        self._sid = data.get("sid")
        self._synotoken = data.get("synotoken")


    def _sync_request(self, params: dict | None = None, is_login: bool = False) -> SynologyResponse:
        """Do a request to the DSM."""
        if not is_login and (not self._sid or not self._synotoken or not self._session):
            self._sync_login()
        
        params["SynoToken"] = self._synotoken

        response: SynologyResponse | None = None
        try:
            r = self._session.get(self._url, params=params, verify=self._verify_ssl)
            response = r.json()
        except Exception as err:
            _LOGGER.error("Error requesting: %s", err)
            raise SynologyDSMAPIErrorException from err

        if not response.get("success", False):
            raise SynologyDSMAPIErrorException

        return response


class SynologyTaskRunError(HomeAssistantError):
    """Error to indicate the task run failed."""

class SynologyDSMAPIErrorException(HomeAssistantError):
    """Error to indicate the DSM API error."""
