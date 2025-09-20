"""任務範本模組"""
from .strategy_templates import (
    BaseTaskTemplate,
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
)

__all__ = [
    "BaseTaskTemplate",
    "HttpTaskTemplate",
    "WebhookTaskTemplate",
    "RabbitMQTaskTemplate",
    "EmailTaskTemplate",
]