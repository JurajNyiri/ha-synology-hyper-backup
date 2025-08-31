"""Data update coordinator for Synology Tasks."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from .synology import SynologyDSM
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import Task

_LOGGER = logging.getLogger(__name__)


class SynologyTasksCoordinator(DataUpdateCoordinator[list[Task]]):
    """Class to manage fetching Synology task data."""

    def __init__(
        self,
        hass: HomeAssistant,
        dsm_entry: ConfigEntry,
    ) -> None:
        """Initialize the data updater."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = SynologyDSM(self.hass, dsm_entry)


    async def _async_update_data(self) -> list[Task]:
        """Fetch data from API."""
        try:
            return await self.api.get_tasks()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
