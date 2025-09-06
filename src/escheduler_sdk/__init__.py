"""EScheduler Python SDK

A Python SDK for interacting with the EScheduler API.
"""

from .client import ESchedulerClient
from .sdk import ESchedulerSDK
from .models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionResponse,
    SchedulerStatsResponse,
    TaskStateUpdateRequest,
    Team,
    TeamAuthRequest,
    TeamAuthResponse,
    TaskState,
    TargetType,
    ExecutionStatus,
    ScheduleType
)
from .exceptions import (
    ESchedulerError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError
)

__version__ = "0.1.0"
__author__ = "EScheduler Team"
__email__ = "team@escheduler.com"

__all__ = [
    "ESchedulerSDK",
    "ESchedulerClient",
    "ScheduledTaskCreate",
    "ScheduledTaskUpdate", 
    "ScheduledTaskResponse",
    "TaskExecutionResponse",
    "SchedulerStatsResponse",
    "TaskStateUpdateRequest",
    "Team",
    "TeamAuthRequest",
    "TeamAuthResponse",
    "TaskState",
    "TargetType",
    "ExecutionStatus",
    "ScheduleType",
    "ESchedulerError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "ServerError"
]