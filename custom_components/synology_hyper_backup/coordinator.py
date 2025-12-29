"""Data update coordinator for Synology Tasks."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from synology_api.core_backup import Backup

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .utils import search_logs

_LOGGER = logging.getLogger(__name__)


class SynologyTasksCoordinator(DataUpdateCoordinator[list[dict]]):
    """Class to manage fetching Synology task data."""

    def __init__(self, hass: HomeAssistant, synology_backup: Backup) -> None:
        """Initialize the data updater."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.hass = hass
        self.synology_backup = synology_backup

    @staticmethod
    def _merge_with_prefix(task: dict, payload: dict | None, prefix: str) -> None:
        """Merge payload data onto task under the given prefix."""
        if not isinstance(payload, dict):
            return
        data = payload.get("data", payload)
        if isinstance(data, dict):
            task.update({f"{prefix}{key}": value for key, value in data.items()})

    async def _async_update_data(self) -> list[dict]:
        """Fetch data from API."""
        try:
            tasks_list = await self.hass.async_add_executor_job(
                self.synology_backup.backup_task_list
            )
            data = tasks_list.get("data", None)
            if data is None:
                raise Exception("Unexpected data returned from Synology.")

            hb_logs_resp = await self.hass.async_add_executor_job(
                self.synology_backup.hb_logs_get,
                1000,
                0,
                "Backup integrity check is finished. No error was found.",
            )

            log_list = hb_logs_resp.get("data", {}).get("log_list", [])

            for task in data.get("task_list"):
                latest_ic = search_logs(log_list, task.get("name"))
                last_result = await self.hass.async_add_executor_job(
                    self.synology_backup.backup_task_result, task.get("task_id")
                )
                status = await self.hass.async_add_executor_job(
                    self.synology_backup.backup_task_status, task.get("task_id")
                )
                status = status.get("data", {})
                status_progress = status.get("progress")
                self._merge_with_prefix(task, last_result, "last_result_")
                self._merge_with_prefix(task, status, "status_")
                self._merge_with_prefix(task, status_progress, "status_progress_")

                if log_list and latest_ic:
                    self._merge_with_prefix(task, latest_ic, "integrity_check_")

            return data
        except Exception as err:
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err
