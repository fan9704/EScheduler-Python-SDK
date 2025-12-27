"""Email 相關功能的端到端測試"""
import pytest
import os
from datetime import datetime

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import (
    EmailTemplateCreateTemplate,
    TemplateVariable,
    EmailTaskTemplate,
)
from escheduler_sdk.exceptions import NotFoundError, ESchedulerError
from escheduler_sdk.utils.test_logger import test_logger as logger

TARGET_EMAIL = os.environ.get("TARGET_EMAIL", None)

@pytest.mark.e2e
class TestEmailFeaturesE2E:
    """Email 功能的端到端測試"""

    @pytest.mark.asyncio
    async def test_create_email_template(self, test_sdk: ESchedulerSDK):
        """測試創建和刪除 Email 模板"""
        template_to_create = EmailTemplateCreateTemplate(
            name=f"e2e-template-{int(datetime.now().timestamp())}",
            subject_template="你好 {{ name }}!",
            body_template="這是一個給使用者 {{ name }} 的 E2E 測試。",
            variables=[
                TemplateVariable(name="name", type="string", required=True)
            ],
        )
        
        created_template = None
        try:
            created_template = await test_sdk.scheduler.create_email_template(template_to_create)
        
            assert created_template is not None
            assert created_template.id is not None
            assert "e2e-template" in created_template.name
            assert len(created_template.variables) == 1
            assert created_template.variables[0]["name"] == "name"
        finally:
            if created_template:
                try:
                    await test_sdk.scheduler.delete_email_template(created_template.id)
                    logger.info(f"模板 {created_template.id} 清理成功。")
                except (NotFoundError, ESchedulerError) as e:
                    logger.error(f"清理模板 {created_template.id} 失敗：{e}")
                    pytest.fail(f"清理模板 {created_template.id} 失敗：{e}")

    @pytest.mark.asyncio
    async def test_create_task_with_template(self, test_sdk: ESchedulerSDK):
        """測試使用 Email 模板創建排程任務"""
        # 步驟 1: 創建一個依賴的 Email 模板
        template_to_create = EmailTemplateCreateTemplate(
            name=f"e2e-dependency-template-{int(datetime.now().timestamp())}",
            subject_template="依賴模板: {{ name }}",
            body_template="依賴模板的內容。",
            variables=[TemplateVariable(name="name", type="string")],
        )
        
        created_template = None
        created_task = None
        
        try:
            created_template = await test_sdk.scheduler.create_email_template(template_to_create)
            assert created_template is not None, "前置模板創建失敗"

            # 步驟 2: 使用創建的模板來創建任務
            task_to_create = EmailTaskTemplate(
                name=f"e2e-task-with-template-{int(datetime.now().timestamp())}",
                schedule_expression="cron(0 0 1 1 *)",  # 每年一次
                use_template=True,
                template_id=created_template.id,
                recipients=[TARGET_EMAIL or "test@example.com"],
                template_variables={"name": "E2E 使用者"},
            )
            
            created_task = await test_sdk.scheduler.create_task(task_to_create)
            assert created_task is not None
            assert created_task.id is not None
            assert "e2e-task-with-template" in created_task.name
            assert created_task.target_input.get("use_template") is True
            assert created_task.target_input.get("template_id") == created_template.id

            # 手動發送測試(如果有輸入 TARGET_EMAIL)
            if TARGET_EMAIL:
                await test_sdk.scheduler.trigger_task(created_task.id)

        finally:
            # 步驟 3: 清理創建的資源
            if created_task:
                try:
                    await test_sdk.scheduler.delete_task(created_task.id)
                    logger.info(f"任務 {created_task.id} 清理成功。")
                except (NotFoundError, ESchedulerError) as e:
                    logger.error(f"清理任務 {created_task.id} 失敗：{e}")
                    pytest.fail(f"清理任務 {created_task.id} 失敗：{e}")
            if created_template:
                try:
                    await test_sdk.scheduler.delete_email_template(created_template.id)
                    logger.info(f"模板 {created_template.id} 清理成功。")
                except (NotFoundError, ESchedulerError) as e:
                    logger.error(f"清理模板 {created_template.id} 失敗：{e}")
                    pytest.fail(f"清理模板 {created_template.id} 失敗：{e}")

    @pytest.mark.asyncio
    async def test_create_direct_email_task(self, test_sdk: ESchedulerSDK):
        """測試不使用模板直接創建 Email 排程任務"""
        task_to_create = EmailTaskTemplate(
            name=f"e2e-direct-email-task-{int(datetime.now().timestamp())}",
            schedule_expression="rate(1 day)",
            subject="直接的 E2E 測試郵件",
            recipients=["direct@example.com"],
            body="這是一封來自 E2E 測試的直接郵件內容。",
            use_template=False,
        )

        created_task = None
        try:
            created_task = await test_sdk.scheduler.create_task(task_to_create)
            assert created_task is not None
            assert created_task.id is not None
            assert "e2e-direct-email-task" in created_task.name
            assert created_task.target_arn == "直接的 E2E 測試郵件"
            assert created_task.target_input.get("use_template") is False

        finally:
            if created_task:
                try:
                    await test_sdk.scheduler.delete_task(created_task.id)
                except (NotFoundError, ESchedulerError) as e:
                    logger.error(f"清理任務 {created_task.id} 失敗：{e}")
                    pytest.fail(f"清理任務 {created_task.id} 失敗：{e}")
