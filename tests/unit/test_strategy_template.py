"""任務創建範本的單元測試"""
import pytest
from escheduler_sdk.models import (
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
    ScheduledTaskCreate,
    TargetType,
)


@pytest.mark.unit
class TestTaskTemplates:
    """所有任務範本的測試套件"""

    def test_http_task_template(self):
        """驗證 HttpTaskTemplate 是否能正確構建 ScheduledTaskCreate 物件"""
        template = HttpTaskTemplate(
            name="Test HTTP Task",
            url="http://example.com/api",
            schedule_expression="rate(1 hour)",
            description="A test HTTP task",
            target_input={"method": "POST", "json": {"key": "value"}},
            max_retry_attempts=5,
        )

        # 執行測試
        task_model = template.build()

        # 驗證結果
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test HTTP Task"
        assert task_model.target_type == TargetType.HTTP
        assert task_model.target_arn == "http://example.com/api"
        assert task_model.schedule_expression == "rate(1 hour)"
        assert task_model.description == "A test HTTP task"
        assert task_model.target_input == {"method": "POST", "json": {"key": "value"}}
        assert task_model.max_retry_attempts == 5
        assert task_model.timezone == "Asia/Taipei"  # 驗證預設值

    def test_webhook_task_template(self):
        """驗證 WebhookTaskTemplate 是否能正確構建 ScheduledTaskCreate 物件"""
        template = WebhookTaskTemplate(
            name="Test Webhook",
            url="http://example.com/webhook",
            schedule_expression="cron(0 0 * * *)",
            payload={"event": "test", "user": "gemini"},
        )

        # 執行測試
        task_model = template.build()

        # 驗證結果
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test Webhook"
        assert task_model.target_type == TargetType.WEBHOOK
        assert task_model.target_arn == "http://example.com/webhook"
        assert task_model.schedule_expression == "cron(0 0 * * *)"
        assert task_model.target_input == {"event": "test", "user": "gemini"}
        assert task_model.max_retry_attempts == 5  # 驗證預設值

    def test_rabbitmq_task_template(self):
        """驗證 RabbitMQTaskTemplate 是否能正確構建 ScheduledTaskCreate 物件"""
        template = RabbitMQTaskTemplate(
            name="Test RabbitMQ Message",
            routing_key="my.queue",
            payload={"message": "hello world"},
            schedule_expression="rate(5 minutes)",
            exchange="my_exchange",
            properties={"content_type": "application/json"},
        )

        # 執行測試
        task_model = template.build()

        # 驗證結果
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test RabbitMQ Message"
        assert task_model.target_type == TargetType.RABBITMQ
        assert task_model.target_arn == "my.queue"
        assert task_model.schedule_expression == "rate(5 minutes)"
        assert task_model.target_input["exchange"] == "my_exchange"
        assert task_model.target_input["payload"] == {"message": "hello world"}
        assert task_model.target_input["properties"] == {"content_type": "application/json"}

    def test_email_task_template(self):
        """驗證 EmailTaskTemplate 是否能正確構建 ScheduledTaskCreate 物件"""
        template = EmailTaskTemplate(
            name="Daily Report Email",
            subject="Daily Report",
            recipients=["test@example.com", "admin@example.com"],
            body="This is the daily report.",
            schedule_expression="cron(0 8 * * *)",
        )

        # 執行測試
        task_model = template.build()

        # 驗證結果
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Daily Report Email"
        assert task_model.target_type == TargetType.EMAIL
        assert task_model.target_arn == "Daily Report"
        assert task_model.schedule_expression == "cron(0 8 * * *)"
        assert task_model.target_input["recipients"] == ["test@example.com", "admin@example.com"]
        assert task_model.target_input["body"] == "This is the daily report."
        assert task_model.max_retry_attempts == 2  # 驗證預設值
