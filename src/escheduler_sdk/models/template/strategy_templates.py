"""任務創建範本"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from ..pydantic import ScheduledTaskCreate
from ..enum import TargetType


class BaseTaskTemplate(ABC):
    """任務範本基礎類別"""

    @abstractmethod
    def build(self) -> ScheduledTaskCreate:
        """
        根據範本配置構建一個 ScheduledTaskCreate 物件
        
        Returns:
            一個配置好的 ScheduledTaskCreate 實例
        """
        pass


class HttpTaskTemplate(BaseTaskTemplate):
    """用於創建 HTTP 目標類型任務的範本"""
    def __init__(
        self,
        name: str,
        url: str,
        schedule_expression: str,
        description: Optional[str] = None,
        target_input: Optional[Dict[str, Any]] = None,
        max_retry_attempts: int = 3,
        timezone: str = "Asia/Taipei",
    ):
        """
        初始化 HTTP 任務範本

        Args:
            name: 任務名稱嗨
            url: 要請求的目標 URL
            schedule_expression: 排程表達式 (例如 "cron(* * * * *)" 或 "rate(1 minute)")
            description: 任務描述
            target_input: 傳遞給目標的輸入 (例如 HTTP headers 或 body)
            max_retry_attempts: 最大重試次數
            timezone: 任務執行的時區
        """
        self.name = name
        self.url = url
        self.schedule_expression = schedule_expression
        self.description = description
        self.target_input = target_input
        self.max_retry_attempts = max_retry_attempts
        self.timezone = timezone

    def build(self) -> ScheduledTaskCreate:
        """構建 ScheduledTaskCreate 物件"""
        return ScheduledTaskCreate(
            name=self.name,
            description=self.description,
            schedule_expression=self.schedule_expression,
            timezone=self.timezone,
            target_type=TargetType.HTTP,
            target_arn=self.url,
            target_input=self.target_input,
            max_retry_attempts=self.max_retry_attempts,
        )


class WebhookTaskTemplate(BaseTaskTemplate):
    """用於創建 Webhook 目標類型任務的範本"""
    def __init__(
        self,
        name: str,
        url: str,
        schedule_expression: str,
        description: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        max_retry_attempts: int = 5,
        timezone: str = "Asia/Taipei",
    ):
        self.name = name
        self.url = url
        self.schedule_expression = schedule_expression
        self.description = description
        self.payload = payload
        self.max_retry_attempts = max_retry_attempts
        self.timezone = timezone

    def build(self) -> ScheduledTaskCreate:
        """構建 ScheduledTaskCreate 物件"""
        return ScheduledTaskCreate(
            name=self.name,
            description=self.description,
            schedule_expression=self.schedule_expression,
            timezone=self.timezone,
            target_type=TargetType.WEBHOOK,
            target_arn=self.url,
            target_input=self.payload,
            max_retry_attempts=self.max_retry_attempts,
        )


class RabbitMQTaskTemplate(BaseTaskTemplate):
    """用於創建 RabbitMQ 目標類型任務的範本"""
    def __init__(
        self,
        name: str,
        routing_key: str,
        payload: Dict[str, Any],
        schedule_expression: str,
        description: Optional[str] = None,
        exchange: str = "", # Default exchange
        properties: Optional[Dict[str, Any]] = None,
        max_retry_attempts: int = 3,
        timezone: str = "Asia/Taipei",
    ):
        self.name = name
        self.routing_key = routing_key
        self.payload = payload
        self.schedule_expression = schedule_expression
        self.description = description
        self.exchange = exchange
        self.properties = properties
        self.max_retry_attempts = max_retry_attempts
        self.timezone = timezone

    def build(self) -> ScheduledTaskCreate:
        """構建 ScheduledTaskCreate 物件"""
        target_input = {
            "exchange": self.exchange,
            "payload": self.payload,
            "properties": self.properties,
        }
        return ScheduledTaskCreate(
            name=self.name,
            description=self.description,
            schedule_expression=self.schedule_expression,
            timezone=self.timezone,
            target_type=TargetType.RABBITMQ,
            target_arn=self.routing_key,
            target_input=target_input,
            max_retry_attempts=self.max_retry_attempts,
        )


class EmailTaskTemplate(BaseTaskTemplate):
    """用於創建 Email 目標類型任務的範本"""
    def __init__(
        self,
        name: str,
        subject: str,
        recipients: List[str],
        body: str,
        schedule_expression: str,
        description: Optional[str] = None,
        max_retry_attempts: int = 2,
        timezone: str = "Asia/Taipei",
    ):
        self.name = name
        self.subject = subject
        self.recipients = recipients
        self.body = body
        self.schedule_expression = schedule_expression
        self.description = description
        self.max_retry_attempts = max_retry_attempts
        self.timezone = timezone

    def build(self) -> ScheduledTaskCreate:
        """構建 ScheduledTaskCreate 物件"""
        target_input = {
            "recipients": self.recipients,
            "body": self.body,
        }
        return ScheduledTaskCreate(
            name=self.name,
            description=self.description,
            schedule_expression=self.schedule_expression,
            timezone=self.timezone,
            target_type=TargetType.EMAIL,
            target_arn=self.subject,
            target_input=target_input,
            max_retry_attempts=self.max_retry_attempts,
        )