"""任務範本 (Strategy Template) 使用範例"""

import asyncio
from datetime import datetime
from typing import List

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskResponse,
    HttpTaskTemplate,
    WebhookTaskTemplate,
    RabbitMQTaskTemplate,
    EmailTaskTemplate,
    EmailTemplateCreateTemplate,
    TemplateVariable,
)
from escheduler_sdk.exceptions import ESchedulerError
from escheduler_sdk.utils.test_logger import test_logger as logger


async def demonstrate_strategy_templates():
    """展示如何使用各種任務範本來快速創建排程任務"""

    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here",
        timeout=30.0,
    ) as sdk:
        logger.info("=== 任務範本 (Strategy Template) 使用範例 ===")
        logger.info("此範例將展示如何使用預定義的範本快速創建不同類型的任務.\n")

        created_tasks: List[ScheduledTaskResponse] = []
        created_email_templates = []

        try:
            # 1. 使用 HttpTaskTemplate 創建 HTTP 任務
            logger.info("1. 創建 HTTP 任務 (使用 HttpTaskTemplate)")
            http_template = HttpTaskTemplate(
                name=f"HTTP 範本任務 - {int(datetime.now().timestamp())}",
                url="https://httpbin.org/post",
                schedule_expression="rate(1 day)",
                description="這是一個使用 HttpTaskTemplate 創建的任務",
                target_input={"method": "POST", "json": {"source": "http_template"}},
                max_retry_attempts=3,
            )

            # 範本物件可以直接傳遞給 create_task
            http_task = await sdk.scheduler.create_task(http_template)
            created_tasks.append(http_task)
            logger.info(f"✅ HTTP 任務創建成功，ID: {http_task.id}")
            logger.info(f"   目標 ARN: {http_task.target_arn}\n")

            # 2. 使用 WebhookTaskTemplate 創建 Webhook 任務
            logger.info("2. 創建 Webhook 任務 (使用 WebhookTaskTemplate)")
            webhook_template = WebhookTaskTemplate(
                name=f"Webhook 範本任務 - {int(datetime.now().timestamp())}",
                url="https://httpbin.org/post",
                schedule_expression="rate(12 hours)",
                description="這是一個使用 WebhookTaskTemplate 創建的任務",
                payload={"event": "test_user", "user": "test_user"},
            )

            webhook_task = await sdk.scheduler.create_task(webhook_template)
            created_tasks.append(webhook_task)
            logger.info(f"✅ Webhook 任務創建成功，ID: {webhook_task.id}")
            logger.info(f"   目標 ARN: {webhook_task.target_arn}\n")

            # 3. 使用 RabbitMQTaskTemplate 創建 RabbitMQ 任務
            logger.info("3. 創建 RabbitMQ 任務 (使用 RabbitMQTaskTemplate)")
            rabbitmq_template = RabbitMQTaskTemplate(
                name=f"RabbitMQ 範本任務 - {int(datetime.now().timestamp())}",
                routing_key="my.test.queue",
                payload={"message": "Hello from RabbitMQ template!"},
                schedule_expression="rate(5 minutes)",
                exchange="default_exchange",
                description="這是一個使用 RabbitMQTaskTemplate 創建的任務",
            )

            rabbitmq_task = await sdk.scheduler.create_task(rabbitmq_template)
            created_tasks.append(rabbitmq_task)
            logger.info(f"✅ RabbitMQ 任務創建成功，ID: {rabbitmq_task.id}")
            logger.info(f"   目標 ARN (Routing Key): {rabbitmq_task.target_arn}\n")

            # 4. 使用 EmailTaskTemplate 創建直接發送的 Email 任務
            logger.info("4. 創建 Email 任務 (使用 EmailTaskTemplate - 直接發送)")
            email_template = EmailTaskTemplate(
                name=f"Email 範本任務 - {int(datetime.now().timestamp())}",
                subject="來自範本的測試郵件",
                recipients=["test1@example.com", "test2@example.com"],
                body="這是一封使用 EmailTaskTemplate 直接發送的測試郵件。",
                schedule_expression="cron(0 10 * * MON)",  # 每週一早上10點
                description="這是一個使用 EmailTaskTemplate 創建的郵件任務",
            )

            email_task = await sdk.scheduler.create_task(email_template)
            created_tasks.append(email_task)
            logger.info(f"✅ Email 任務創建成功，ID: {email_task.id}")
            logger.info(f"   目標 ARN (Subject): {email_task.target_arn}\n")

            # 5. 創建使用郵件範本的 Email 任務
            logger.info("5. 創建使用郵件範本的 Email 任務 (使用 EmailTaskTemplate with Template)")

            # 5.1 先創建一個郵件範本
            logger.info("   5.1. 創建郵件範本...")
            email_template_def = EmailTemplateCreateTemplate(
                name=f"範例郵件範本 - {int(datetime.now().timestamp())}",
                subject_template="您好 {{ user_name }}，這是一封範本郵件",
                body_template="這封郵件是關於訂單 #{{ order_id }} 的通知。",
                variables=[
                    TemplateVariable(name="user_name", type="string", required=True),
                    TemplateVariable(name="order_id", type="number", required=True),
                ],
            )
            created_template = await sdk.scheduler.create_email_template(
                email_template_def
            )
            created_email_templates.append(created_template)
            logger.info(f"   ✅ 郵件範本創建成功，ID: {created_template.id}")

            # 5.2 使用範本創建任務
            logger.info("   5.2. 使用範本 ID 創建排程任務...")
            email_task_with_template = EmailTaskTemplate(
                name=f"Email (from Template) - {int(datetime.now().timestamp())}",
                schedule_expression="cron(0 18 * * FRI)",  # 每週五下午 6 點
                use_template=True,
                template_id=created_template.id,
                recipients=["user@example.com"],
                template_variables={"user_name": "Gemini", "order_id": 12345},
                description="這是一個使用郵件範本創建的任務",
            )

            email_task_2 = await sdk.scheduler.create_task(email_task_with_template)
            created_tasks.append(email_task_2)
            logger.info(f"✅ 使用範本的 Email 任務創建成功，ID: {email_task_2.id}")
            logger.info(f"   目標 ARN: {email_task_2.target_arn}\n")

            logger.info("=== 所有範本任務創建成功 ===")
            logger.info("創建的任務列表:")
            for task in created_tasks:
                logger.info(f"  - {task.name} (ID: {task.id}, 類型: {task.target_type})")

        except ESchedulerError as e:
            logger.error(f"❌ 發生 API 錯誤: {e}")
            logger.error(f"   狀態碼: {e.status_code}")
            logger.error(f"   回應: {e.response_data}")
        except Exception as e:
            logger.error(f"❌ 發生未知錯誤: {e}")

        finally:
            # 6. 清理所有已創建的資源
            if created_tasks:
                logger.info("\n6. 清理創建的任務...")
                for task in created_tasks:
                    try:
                        await sdk.scheduler.delete_task(task.id)
                        logger.info(f"✅ 任務 {task.name} (ID: {task.id}) 已成功刪除。")
                    except ESchedulerError as e:
                        logger.error(f"❌ 刪除任務 {task.name} (ID: {task.id}) 失敗: {e}")

            if created_email_templates:
                logger.info("\n7. 清理創建的郵件範本...")
                for template in created_email_templates:
                    try:
                        await sdk.scheduler.delete_email_template(template.id)
                        logger.info(
                            f"✅ 郵件範本 {template.name} (ID: {template.id}) 已成功刪除。"
                        )
                    except ESchedulerError as e:
                        logger.error(
                            f"❌ 刪除郵件範本 {template.name} (ID: {template.id}) 失敗: {e}"
                        )


if __name__ == "__main__":
    # 運行範例
    asyncio.run(demonstrate_strategy_templates())
