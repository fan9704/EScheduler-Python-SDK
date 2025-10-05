"""任務範本模組"""
from .strategy_templates import (
    BaseTaskTemplate,
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
    EmailTemplateCreateTemplate
)

__all__ = [
    "BaseTaskTemplate",
    "HttpTaskTemplate",
    "WebhookTaskTemplate",
    "RabbitMQTaskTemplate",
    "EmailTaskTemplate",
    "EmailTemplateCreateTemplate"
]