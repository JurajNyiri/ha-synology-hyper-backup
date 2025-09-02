"""Data models for the Synology Tasks integration."""
from dataclasses import dataclass
from typing import TypedDict


class SynologyResponse(TypedDict):
    """Synology response."""

    success: bool
    data: dict


class SynologyAuthData(TypedDict):
    """Synology authentication data."""

    account: str
    device_id: str
    ik_message: str
    is_portal_port: bool
    sid: str
    synotoken: str


class SynologyTask(TypedDict):
    """Task data from Synology API."""

    name: str
    action: str
    can_delete: bool
    can_edit: bool
    can_run: bool
    enable: bool
    id: int
    next_trigger_time: str
    owner: str
    type: str


class SynologyTaskData(TypedDict):
    """Synology task data."""

    tasks: list[SynologyTask]


@dataclass
class Task:
    """Task entity data."""

    id: int
    name: str
    type: str
    owner: str
    enabled: bool
    can_run: bool
    next_run_time: str

    @classmethod
    def from_api(cls, data: SynologyTaskData) -> "Task":
        """Create Task from API response data."""

        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            owner=data["owner"],
            enabled=data["enable"],
            can_run=data["can_run"],
            next_run_time=data["next_trigger_time"],
        )
