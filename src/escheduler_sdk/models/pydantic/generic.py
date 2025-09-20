"""通用回應 Pydantic 模型"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """通用消息回應模型"""
    message: str = Field(..., description="回應消息")
    status_code: Optional[int] = Field(None, description="狀態碼")


class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    detail: str = Field(..., description="錯誤詳情")
    error_code: Optional[str] = Field(None, description="錯誤代碼")
    timestamp: Optional[datetime] = Field(None, description="錯誤時間")
