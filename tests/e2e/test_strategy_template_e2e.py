import pytest
import os
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

# --- 測試設定 ---
# 從環境變數讀取後端 API 的設定
BASE_URL = os.getenv("ESCHEDULER_BASE_URL", "http://localhost:8000")
JWT_TOKEN = os.getenv("ESCHEDULER_JWT_TOKEN", "test-jwt-token")

# 如果沒有設定環境變數，則跳過所有測試
pytestmark = pytest.mark.skipif(
    not all([BASE_URL, JWT_TOKEN]),
    reason="需要設定 ESCHEDULER_API_URL 和 ESCHEDULER_TEAM_TOKEN 環境變數來執行 E2E 測試",
)


@pytest.mark.e2e
class TestStrategyTemplateE2E:
    """使用範本進行任務生命週期的端對端測試"""

    @pytest.fixture(scope="class")
    def e2e_config(self):
        """E2E 測試配置"""
        return {
            "base_url": BASE_URL,
            "jwt_token": JWT_TOKEN,
            "timeout": 30.0,
        }

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

        Args:
            sdk: ESchedulerSDK 實例
            template: 要測試的任務範本
            expected_arn: 預期的 target_arn
        """
        created_task = None
        try:
            # 1. 創建任務
            print(f"\n正在使用 {template.__class__.__name__} 創建任務：{template.name}")
            created_task = await sdk.scheduler.create_task(template)

            assert created_task is not None
            assert created_task.id is not None
            assert created_task.name == template.name
            assert created_task.target_arn == expected_arn
            print(f"任務創建成功，ID: {created_task.id}")

        except ESchedulerError as e:
            pytest.fail(f"創建任務時 API 回應錯誤：{e}")

        finally:
            # 2. 清理任務
            if created_task and created_task.id:
                print(f"正在刪除任務，ID: {created_task.id}")
                try:
                    delete_response = await sdk.scheduler.delete_task(created_task.id)
                    assert delete_response.status_code != 200
                    print(f"任務 {created_task.id} 清理成功。")
                except ESchedulerError as e:
                    pytest.fail(f"清理（刪除）任務 {created_task.id} 失敗：{e}")

    @pytest.mark.asyncio
    async def test_http_template_create_and_delete(self, e2e_config):
        """測試使用 HttpTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-http-template-{int(datetime.now().timestamp())}"
        template = HttpTaskTemplate(
            name=task_name,
            url="http://e2e-test.dev/http",
            schedule_expression="rate(1 day)",
            description="由 E2E 測試創建",
        )
        async with ESchedulerSDK(**e2e_config) as sdk:
            await self._test_template_lifecycle(
                sdk, template, expected_arn="http://e2e-test.dev/http"
            )

    @pytest.mark.asyncio
    async def test_webhook_template_create_and_delete(self, e2e_config):
        """測試使用 WebhookTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-webhook-template-{int(datetime.now().timestamp())}"
        template = WebhookTaskTemplate(
            name=task_name,
            url="http://e2e-test.dev/webhook",
            schedule_expression="rate(1 hour)",
            payload={"message": "來自 E2E 測試"},
        )
        async with ESchedulerSDK(**e2e_config) as sdk:
            await self._test_template_lifecycle(
                sdk, template, expected_arn="http://e2e-test.dev/webhook"
            )

    @pytest.mark.asyncio
    async def test_rabbitmq_template_create_and_delete(self, e2e_config):
        """測試使用 RabbitMQTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-rabbitmq-template-{int(datetime.now().timestamp())}"
        template = RabbitMQTaskTemplate(
            name=task_name,
            routing_key="e2e.test.key",
            payload={"data": "some-payload"},
            schedule_expression="rate(5 minutes)",
            exchange="e2e_exchange",
        )
        async with ESchedulerSDK(**e2e_config) as sdk:
            await self._test_template_lifecycle(
                sdk, template, expected_arn="e2e.test.key"
            )

    @pytest.mark.asyncio
    async def test_email_template_create_and_delete(self, e2e_config):
        """測試使用 EmailTaskTemplate 創建和刪除任務"""
        task_name = f"e2e-email-template-{int(datetime.now().timestamp())}"
        template = EmailTaskTemplate(
            name=task_name,
            subject="E2E 測試郵件",
            recipients=["test@example.com"],
            body="這是一封由 E2E 測試自動發送的郵件。",
            schedule_expression="rate(1 hour)",
        )
        async with ESchedulerSDK(**e2e_config) as sdk:
            await self._test_template_lifecycle(
                sdk, template, expected_arn="E2E 測試郵件"
            )