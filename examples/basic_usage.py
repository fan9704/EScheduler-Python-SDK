"""EScheduler SDK 基本使用範例"""

import asyncio
from datetime import datetime

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    TaskState,
    TargetType,
    TaskStateUpdateRequest
)
from escheduler_sdk.utils.test_logger import test_logger as logger


async def main():
    """主要範例函數"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",  # 替換為你的 EScheduler API URL
        jwt_token="your-jwt-token-here",  # 替換為你的 JWT token
        timeout=30.0
    ) as sdk:
        
        try:
            # 1. 創建排程任務
            logger.info("=== 創建排程任務 ===")
            task_data = ScheduledTaskCreate(
                name="測試任務",
                description="這是一個測試排程任務",
                schedule_expression="rate(5 minutes)",  # 每5分鐘執行一次
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://httpbin.org/post",
                target_input={
                    "message": "Hello from EScheduler!",
                    "timestamp": datetime.now().isoformat()
                },
                max_retry_attempts=3
            )
            
            created_task = await sdk.scheduler.create_task(task_data)
            logger.info(f"✅ 任務創建成功，ID: {created_task.id}")
            logger.info(f"   任務名稱: {created_task.name}")
            logger.info(f"   狀態: {created_task.state}")
            logger.info(f"   下次執行時間: {created_task.next_execution_time}")
            
            task_id = created_task.id
            
            # 2. 獲取所有任務
            logger.info("\n=== 獲取所有任務 ===")
            all_tasks = await sdk.scheduler.get_all_tasks()
            logger.info(f"✅ 共有 {len(all_tasks)} 個任務")
            for task in all_tasks:
                logger.info(f"   - {task.name} (ID: {task.id}, 狀態: {task.state})")
            
            # 3. 獲取單個任務
            logger.info("\n=== 獲取單個任務 ===")
            task = await sdk.scheduler.get_task(task_id)
            logger.info(f"✅ 任務詳情:")
            logger.info(f"   ID: {task.id}")
            logger.info(f"   名稱: {task.name}")
            logger.info(f"   描述: {task.description}")
            logger.info(f"   排程表達式: {task.schedule_expression}")
            logger.info(f"   目標類型: {task.target_type}")
            logger.info(f"   目標 ARN: {task.target_arn}")
            logger.info(f"   執行次數: {task.execution_count}")
            
            # 4. 更新任務
            logger.info("\n=== 更新任務 ===")
            update_data = ScheduledTaskUpdate(
                description="更新後的任務描述",
                schedule_expression="rate(10 minutes)"  # 改為每10分鐘執行一次
            )
            
            updated_task = await sdk.scheduler.update_task(task_id, update_data)
            logger.info(f"✅ 任務更新成功")
            logger.info(f"   新描述: {updated_task.description}")
            logger.info(f"   新排程表達式: {updated_task.schedule_expression}")
            
            # 5. 搜索任務
            logger.info("\n=== 搜索任務 ===")
            search_results = await sdk.scheduler.search_tasks("測試")
            logger.info(f"✅ 搜索到 {len(search_results)} 個任務")
            for task in search_results:
                logger.info(f"   - {task.name} (ID: {task.id})")
            
            # 6. 任務狀態管理
            logger.info("\n=== 任務狀態管理 ===")
            
            # 暫停任務
            paused_task = await sdk.scheduler.pause_task(task_id)
            logger.info(f"✅ 任務已暫停，狀態: {paused_task.state}")
            
            # 重新啟用任務
            enabled_task = await sdk.scheduler.enable_task(task_id)
            logger.info(f"✅ 任務已啟用，狀態: {enabled_task.state}")
            
            # 7. 手動觸發任務
            logger.info("\n=== 手動觸發任務 ===")
            trigger_result = await sdk.scheduler.trigger_task(task_id)
            logger.info(f"✅ 任務觸發成功: {trigger_result.message}")
            
            # 8. 獲取排程器統計
            logger.info("\n=== 排程器統計 ===")
            stats = await sdk.scheduler.get_scheduler_stats()
            logger.info(f"✅ 排程器統計:")
            logger.info(f"   總任務數: {stats.total_tasks}")
            logger.info(f"   啟用任務數: {stats.enabled_tasks}")
            logger.info(f"   禁用任務數: {stats.disabled_tasks}")
            logger.info(f"   今日總執行次數: {stats.total_executions_today}")
            logger.info(f"   今日成功執行次數: {stats.successful_executions_today}")
            logger.info(f"   今日失敗執行次數: {stats.failed_executions_today}")
            
            # 9. 刪除任務
            logger.info("\n=== 刪除任務 ===")
            delete_result = await sdk.scheduler.delete_task(task_id)
            logger.info(f"✅ 任務刪除成功: {delete_result.message}")
            
        except Exception as e:
            logger.error(f"❌ 發生錯誤: {e}")
            logger.error(f"   錯誤類型: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                logger.error(f"   HTTP 狀態碼: {e.status_code}")
            if hasattr(e, 'response_data'):
                logger.error(f"   回應數據: {e.response_data}")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(main())