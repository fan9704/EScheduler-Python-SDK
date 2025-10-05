"""任務創建範本"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from ..pydantic import ScheduledTaskCreate, EmailTemplateCreate, TemplateVariable
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
        schedule_expression: str,
        # Direct email settings (if not using a template)
        subject: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        body: Optional[str] = None,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        sender: Optional[str] = None,
        # Template settings
        use_template: bool = False,
        template_id: Optional[int] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        # Common task settings
        description: Optional[str] = None,
        max_retry_attempts: int = 2,
        timezone: str = "Asia/Taipei",
    ):
        """
        初始化 Email 任務範本

        Args:
            name (str): 任務名稱
            schedule_expression (str): 排程表達式 (例如 "cron(* * * * *)" 或 "rate(1 minute)")

            subject (Optional[str]): 郵件主旨 (不使用模板時為必填)
            recipients (Optional[List[str]]): 收件人列表 (不使用模板時為必填)
            body (Optional[str]): 純文字郵件內容
            html_body (Optional[str]): HTML 郵件內容
            cc (Optional[List[str]]): 副本收件人列表
            bcc (Optional[List[str]]): 密件副本收件人列表
            sender (Optional[str]): 寄件人

            use_template (bool): 是否使用模板. Defaults to False.
            template_id (Optional[int]): 模板 ID (使用模板時為必填)
            template_variables (Optional[Dict[str, Any]]): 模板變數

            description (Optional[str]): 任務描述
            max_retry_attempts (int): 最大重試次數. Defaults to 2.
            timezone (str): 任務執行的時區. Defaults to "Asia/Taipei".
        """
        if use_template:
            if not template_id:
                raise ValueError("使用模板時，必須提供 'template_id'")
        else:
            if not subject:
                raise ValueError("不使用模板時，必須提供 'subject'")
            if not recipients:
                raise ValueError("不使用模板時，必須提供 'recipients'")

        self.name = name
        self.schedule_expression = schedule_expression
        self.description = description
        self.max_retry_attempts = max_retry_attempts
        self.timezone = timezone

        # Email specific attributes
        self.use_template = use_template
        self.template_id = template_id
        self.template_variables = template_variables
        self.subject = subject
        self.body = body
        self.html_body = html_body
        self.recipients = recipients
        self.cc = cc
        self.bcc = bcc
        self.sender = sender

    def build(self) -> ScheduledTaskCreate:
        """構建 ScheduledTaskCreate 物件"""
        target_arn = (
            self.subject
            if not self.use_template
            else f"email:template_id:{self.template_id}"
        )

        target_input = {
            "use_template": self.use_template,
            "template_id": self.template_id,
            "template_variables": self.template_variables,
            "subject": self.subject,
            "body": self.body,
            "html_body": self.html_body,
            "recipients": self.recipients,
            "cc": self.cc,
            "bcc": self.bcc,
            "sender": self.sender,
        }

        # Remove keys with None values to keep the payload clean
        final_target_input = {k: v for k, v in target_input.items() if v is not None}

        # If using template, we don't need to send subject/body in target_input
        if self.use_template:
            final_target_input.pop("subject", None)
            final_target_input.pop("body", None)
            final_target_input.pop("html_body", None)

        return ScheduledTaskCreate(
            name=self.name,
            description=self.description,
            schedule_expression=self.schedule_expression,
            timezone=self.timezone,
            target_type=TargetType.EMAIL,
            target_arn=target_arn,
            target_input=final_target_input,
            max_retry_attempts=self.max_retry_attempts,
        )


class EmailTemplateCreateTemplate:
    """用於創建 Email 模板的範本"""

    def __init__(
        self,
        name: str,
        subject_template: str,
        body_template: str,
        description: Optional[str] = None,
        html_template: Optional[str] = None,
        variables: Optional[List[TemplateVariable]] = None,
        default_sender: Optional[str] = None,
        default_cc: Optional[List[str]] = None,
        default_bcc: Optional[List[str]] = None,
        is_active: bool = True,
    ):
        """
        初始化 Email 模板創建範本

        Args:
            name (str): 模板名稱
            subject_template (str): 主旨模板
            body_template (str): 內容模板
            description (Optional[str]): 模板描述
            html_template (Optional[str]): HTML 模板
            variables (Optional[List[TemplateVariable]]): 模板變數定義
            default_sender (Optional[str]): 預設寄件人
            default_cc (Optional[List[str]]): 預設副本收件人
            default_bcc (Optional[List[str]]): 預設密件副本收件人
            is_active (bool): 是否啟用
        """
        self.name = name
        self.subject_template = subject_template
        self.body_template = body_template
        self.description = description
        self.html_template = html_template
        self.variables = variables if variables is not None else []
        self.default_sender = default_sender
        self.default_cc = default_cc
        self.default_bcc = default_bcc
        self.is_active = is_active

    def build(self) -> EmailTemplateCreate:
        """構建 EmailTemplateCreate 物件"""
        return EmailTemplateCreate(
            name=self.name,
            description=self.description,
            subject_template=self.subject_template,
            body_template=self.body_template,
            html_template=self.html_template,
            variables=self.variables,
            default_sender=self.default_sender,
            default_cc=self.default_cc,
            default_bcc=self.default_bcc,
            is_active=self.is_active,
        )