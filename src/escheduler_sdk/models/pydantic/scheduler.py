"""排程任務相關 Pydantic 模型"""
from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..enum.enums import TargetType, TaskState, ExecutionStatus


class ScheduledTaskCreate(BaseModel):
    """創建排程任務請求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    schedule_expression: str = Field(..., description="排程表達式")
    timezone: str = Field("Asia/Taipei", description="時區")
    target_type: TargetType = Field(..., description="目標類型")
    target_arn: str = Field(..., description="目標 ARN 或 URL")
    target_input: Optional[Dict[str, Any]] = Field(None, description="目標輸入參數")
    max_retry_attempts: int = Field(3, ge=0, le=10, description="最大重試次數")
    retry_policy: Optional[Dict[str, Any]] = Field(None, description="重試策略")
    dead_letter_config: Optional[Dict[str, Any]] = Field(None, description="死信佇列配置")
    state: TaskState = Field(default=TaskState.ENABLED, description="任務狀態")
    
    @field_validator('schedule_expression')
    @classmethod
    def validate_schedule_expression(cls, v):
        """驗證排程表達式格式"""
        if v.startswith('cron(') and v.endswith(')'):
            return v
        elif v.startswith('rate(') and v.endswith(')'):
            return v
        else:
            raise ValueError('排程表達式必須是 cron(expression) 或 rate(expression) 格式')


class ScheduledTaskUpdate(BaseModel):
    """更新排程任務請求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_expression: Optional[str] = None
    timezone: Optional[str] = None
    target_type: Optional[TargetType] = None
    target_arn: Optional[str] = None
    target_input: Optional[Dict[str, Any]] = None
    state: Optional[TaskState] = None
    max_retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    retry_policy: Optional[Dict[str, Any]] = None
    dead_letter_config: Optional[Dict[str, Any]] = None


class ScheduledTaskResponse(BaseModel):
    """排程任務回應模型"""
    id: int
    name: str
    description: Optional[str]
    schedule_expression: str
    timezone: str
    target_type: str
    target_arn: str
    target_input: Optional[Dict[str, Any]]
    state: TaskState
    last_execution_time: Optional[datetime]
    next_execution_time: Optional[datetime]
    execution_count: int
    max_retry_attempts: int
    retry_policy: Optional[Dict[str, Any]]
    dead_letter_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class TaskExecutionResponse(BaseModel):
    """任務執行記錄回應模型"""
    id: int
    task_id: int
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    response_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_number: int


class SchedulerStatsResponse(BaseModel):
    """排程器統計回應模型"""
    total_tasks: int
    enabled_tasks: int
    disabled_tasks: int
    total_executions_today: int
    successful_executions_today: int
    failed_executions_today: int


class TaskStateUpdateRequest(BaseModel):
    """任務狀態更新請求模型"""
    state: TaskState = Field(..., description="新的任務狀態")
