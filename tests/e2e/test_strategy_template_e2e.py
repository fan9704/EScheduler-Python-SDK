import pytest
from datetime import datetime
from typing import Union

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import (
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
)
from escheduler_sdk.exceptions import ESchedulerError
from escheduler_sdk.utils.test_logger import test_logger as logger

@pytest.mark.e2e
class TestStrategyTemplateE2E:
    """使用範本進行任務生命週期的端對端測試"""

    async def _test_template_lifecycle(
        self,
        sdk: ESchedulerSDK,
        template: Union[
            HttpTaskTemplate,
            WebhookTaskTemplate,
            RabbitMQTaskTemplate,
            EmailTaskTemplate,
        ],
        expected_arn: str,
    ):
        """
        測試範本創建和刪除的通用流程
        """
        created_task = None
        try:
            # 1. 創建任務
            logger.info(f"\n正在使用 {template.__class__.__name__} 創建任務：{template.name}")
            created_task = await sdk.scheduler.create_task(template)

            assert created_task is not None
            assert created_task.id is not None
            assert created_task.name == template.name
            assert created_task.target_arn == expected_arn
            logger.info(f"任務創建成功，ID: {created_task.id}")

        except ESchedulerError as e:
            logger.error(f"創建任務時 API 回應錯誤：{e}")
            pytest.fail(f"創建任務時 API 回應錯誤：{e}")

        finally:
            # 2. 清理任務
            if created_task and created_task.id:
                logger.info(f"正在刪除任務，ID: {created_task.id}")
                try:
                    await sdk.scheduler.delete_task(created_task.id)
                    logger.info(f"任務 {created_task.id} 清理成功。")
                except ESchedulerError as e:
                    logger.error(f"清理（刪除）任務 {created_task.id} 失敗：{e}")
                    pytest.fail(f"清理（刪除）任務 {created_task.id} 失敗：{e}")

    @pytest.mark.asyncio
    async def test_http_template_create_and_delete(self, test_sdk: ESchedulerSDK):
        """測試使用 HttpTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-http-template-{int(datetime.now().timestamp())}"
        template = HttpTaskTemplate(
            name=task_name,
            url="http://e2e-test.dev/http",
            schedule_expression="rate(1 day)",
            description="由 E2E 測試創建",
        )
        await self._test_template_lifecycle(
            test_sdk, template, expected_arn="http://e2e-test.dev/http"
        )

    @pytest.mark.asyncio
    async def test_webhook_template_create_and_delete(self, test_sdk: ESchedulerSDK):
        """測試使用 WebhookTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-webhook-template-{int(datetime.now().timestamp())}"
        template = WebhookTaskTemplate(
            name=task_name,
            url="http://e2e-test.dev/webhook",
            schedule_expression="rate(1 hour)",
            payload={"message": "來自 E2E 測試"},
        )
        await self._test_template_lifecycle(
            test_sdk, template, expected_arn="http://e2e-test.dev/webhook"
        )

    @pytest.mark.asyncio
    async def test_rabbitmq_template_create_and_delete(self, test_sdk: ESchedulerSDK):
        """測試使用 RabbitMQTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-rabbitmq-template-{int(datetime.now().timestamp())}"
        template = RabbitMQTaskTemplate(
            name=task_name,
            routing_key="e2e.test.key",
            payload={"data": "some-payload"},
            schedule_expression="rate(5 minutes)",
            exchange="e2e_exchange",
        )
        await self._test_template_lifecycle(
            test_sdk, template, expected_arn="e2e.test.key"
        )

    @pytest.mark.asyncio
    async def test_email_template_create_and_delete(self, test_sdk: ESchedulerSDK):
        """測試使用 EmailTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-email-template-{int(datetime.now().timestamp())}"
        template = EmailTaskTemplate(
            name=task_name,
            subject="E2E 測試郵件",
            recipients=["test@example.com"],
            body="這是一封由 E2E 測試自動發送的郵件。",
            schedule_expression="rate(1 hour)",
        )
        await self._test_template_lifecycle(
            test_sdk, template, expected_arn="E2E 測試郵件"
        )