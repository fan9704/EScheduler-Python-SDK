"""EScheduler SDK 枚舉類型"""
from enum import Enum


class TaskState(str, Enum):
    """任務狀態枚舉"""
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    PAUSED = "PAUSED"


class TargetType(str, Enum):
    """目標類型枚舉"""
    HTTP = "http"
    WEBHOOK = "webhook"
    RABBITMQ = "rabbitmq"
    EMAIL = "email"


class ExecutionStatus(str, Enum):
    """執行狀態枚舉"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class ScheduleType(str, Enum):
    """排程類型枚舉"""
    CRON = "cron"
    RATE = "rate"
    ONE_TIME = "one_time"
    AT = "at"
