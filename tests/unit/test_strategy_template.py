import pytest
from escheduler_sdk.models import (
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
    EmailTemplateCreateTemplate,
    TemplateVariable,
    ScheduledTaskCreate,
    EmailTemplateCreate,
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
        task_model = template.build()
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test HTTP Task"
        assert task_model.target_type == TargetType.HTTP
        assert task_model.target_arn == "http://example.com/api"
        assert task_model.schedule_expression == "rate(1 hour)"
        assert task_model.description == "A test HTTP task"
        assert task_model.target_input == {"method": "POST", "json": {"key": "value"}}
        assert task_model.max_retry_attempts == 5
        assert task_model.timezone == "Asia/Taipei"

    def test_webhook_task_template(self):
        """驗證 WebhookTaskTemplate 是否能正確構建 ScheduledTaskCreate 物件"""
        template = WebhookTaskTemplate(
            name="Test Webhook",
            url="http://example.com/webhook",
            schedule_expression="cron(0 0 * * *)",
            payload={"event": "test", "user": "gemini"},
        )
        task_model = template.build()
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test Webhook"
        assert task_model.target_type == TargetType.WEBHOOK
        assert task_model.target_arn == "http://example.com/webhook"
        assert task_model.schedule_expression == "cron(0 0 * * *)"
        assert task_model.target_input == {"event": "test", "user": "gemini"}
        assert task_model.max_retry_attempts == 5

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
        task_model = template.build()
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Test RabbitMQ Message"
        assert task_model.target_type == TargetType.RABBITMQ
        assert task_model.target_arn == "my.queue"
        assert task_model.schedule_expression == "rate(5 minutes)"
        assert task_model.target_input["exchange"] == "my_exchange"
        assert task_model.target_input["payload"] == {"message": "hello world"}
        assert task_model.target_input["properties"] == {"content_type": "application/json"}

    def test_email_task_template_direct_build(self):
        """驗證 EmailTaskTemplate (Direct) 是否能正確構建"""
        template = EmailTaskTemplate(
            name="Direct Report Email",
            subject="Direct Report",
            recipients=["test@example.com"],
            body="This is the direct report.",
            schedule_expression="cron(0 8 * * *)",
        )
        task_model = template.build()
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Direct Report Email"
        assert task_model.target_type == TargetType.EMAIL
        assert task_model.target_arn == "Direct Report"
        assert task_model.target_input["recipients"] == ["test@example.com"]
        assert task_model.target_input["body"] == "This is the direct report."
        assert task_model.target_input["use_template"] is False

    def test_email_task_template_with_template_build(self):
        """驗證 EmailTaskTemplate (With Template) 是否能正確構建"""
        template = EmailTaskTemplate(
            name="Template Report Email",
            schedule_expression="cron(0 9 * * *)",
            use_template=True,
            template_id=123,
            recipients=["template@example.com"],
            template_variables={"user": "Gemini"},
        )
        task_model = template.build()
        assert isinstance(task_model, ScheduledTaskCreate)
        assert task_model.name == "Template Report Email"
        assert task_model.target_type == TargetType.EMAIL
        assert task_model.target_arn == "email:template_id:123"
        assert task_model.target_input["use_template"] is True
        assert task_model.target_input["template_id"] == 123
        assert task_model.target_input["template_variables"] == {"user": "Gemini"}
        assert "subject" not in task_model.target_input
        assert "body" not in task_model.target_input

    def test_email_task_template_validation(self):
        """驗證 EmailTaskTemplate 的初始化驗證邏輯"""
        # 使用模板但未提供 template_id
        with pytest.raises(ValueError, match="必須提供 'template_id'"):
            EmailTaskTemplate(
                name="Invalid Template Task",
                schedule_expression="rate(1m)",
                use_template=True,
                recipients=["test@example.com"],
            )

        # 不使用模板但未提供 subject
        with pytest.raises(ValueError, match="必須提供 'subject'"):
            EmailTaskTemplate(
                name="Invalid Direct Task",
                schedule_expression="rate(1m)",
                use_template=False,
                recipients=["test@example.com"],
                body="some body",
            )

        # 不使用模板但未提供 recipients
        with pytest.raises(ValueError, match="必須提供 'recipients'"):
            EmailTaskTemplate(
                name="Invalid Direct Task",
                schedule_expression="rate(1m)",
                use_template=False,
                subject="some subject",
            )

    def test_email_template_create_template_build(self):
        """驗證 EmailTemplateCreateTemplate 是否能正確構建"""
        variables = [
            TemplateVariable(name="user_name", type="string", required=True),
            TemplateVariable(name="order_id", type="number"),
        ]
        template = EmailTemplateCreateTemplate(
            name="Test Email Template",
            subject_template="Order {{ order_id }} for {{ user_name }}",
            body_template="Details for order {{ order_id }}.",
            html_template="<p>Details for order {{ order_id }}.</p>",
            variables=variables,
            default_sender="noreply@example.com",
        )
        template_model = template.build()
        assert isinstance(template_model, EmailTemplateCreate)
        assert template_model.name == "Test Email Template"
        assert template_model.subject_template == "Order {{ order_id }} for {{ user_name }}"
        assert len(template_model.variables) == 2
        assert template_model.variables[0].name == "user_name"
        assert template_model.default_sender == "noreply@example.com"