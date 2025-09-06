"""HTTP 任務排程範例"""

import asyncio
from datetime import datetime

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskCreate,
    TargetType
)


async def create_http_tasks():
    """創建各種 HTTP 任務的範例"""
    
    # 初始化 SDK（不使用團隊認證）
    async with ESchedulerSDK(
        base_url="http://localhost:8000",  # 替換為你的 EScheduler API URL
        jwt_token="your-jwt-token-here",  # 使用 JWT 認證
        timeout=30.0
    ) as sdk:
        
        try:
            print("=== HTTP 任務排程範例 ===")
            
            # 1. 創建每日備份任務
            print("\n1. 創建每日備份任務")
            backup_task = ScheduledTaskCreate(
                name="每日數據備份",
                description="每天凌晨2點執行數據備份",
                schedule_expression="cron(0 2 * * *)",  # 每天凌晨2點
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://api.example.com/backup",
                target_input={
                    "backup_type": "full",
                    "retention_days": 30,
                    "notify_email": "admin@example.com"
                },
                max_retry_attempts=3
            )
            
            created_backup = await sdk.scheduler.create_task(backup_task)
            print(f"✅ 備份任務創建成功，ID: {created_backup.id}")
            print(f"   下次執行時間: {created_backup.next_execution_time}")
            
            # 2. 創建健康檢查任務
            print("\n2. 創建健康檢查任務")
            health_check_task = ScheduledTaskCreate(
                name="服務健康檢查",
                description="每5分鐘檢查服務狀態",
                schedule_expression="rate(5 minutes)",
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://api.example.com/health",
                target_input={
                    "check_type": "full",
                    "timeout": 30,
                    "expected_status": 200
                },
                max_retry_attempts=2
            )
            
            created_health = await sdk.scheduler.create_task(health_check_task)
            print(f"✅ 健康檢查任務創建成功，ID: {created_health.id}")
            
            # 3. 創建報告生成任務
            print("\n3. 創建週報生成任務")
            report_task = ScheduledTaskCreate(
                name="週報生成",
                description="每週一上午9點生成週報",
                schedule_expression="cron(0 9 * * MON)",  # 每週一上午9點
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://api.example.com/reports/weekly",
                target_input={
                    "report_type": "weekly",
                    "format": "pdf",
                    "recipients": ["manager@example.com", "team@example.com"],
                    "include_charts": True
                },
                max_retry_attempts=3
            )
            
            created_report = await sdk.scheduler.create_task(report_task)
            print(f"✅ 週報任務創建成功，ID: {created_report.id}")
            
            # 4. 創建數據同步任務
            print("\n4. 創建數據同步任務")
            sync_task = ScheduledTaskCreate(
                name="數據同步",
                description="每小時同步外部數據",
                schedule_expression="rate(1 hour)",
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://api.example.com/sync",
                target_input={
                    "source": "external_api",
                    "destination": "local_database",
                    "batch_size": 1000,
                    "incremental": True
                },
                max_retry_attempts=5
            )
            
            created_sync = await sdk.scheduler.create_task(sync_task)
            print(f"✅ 數據同步任務創建成功，ID: {created_sync.id}")
            
            # 5. 查看所有創建的任務
            print("\n=== 查看所有任務 ===")
            all_tasks = await sdk.scheduler.get_all_tasks()
            print(f"總共有 {len(all_tasks)} 個任務:")
            for task in all_tasks:
                print(f"  - {task.name} ({task.state})")
                print(f"    排程: {task.schedule_expression}")
                print(f"    目標: {task.target_arn}")
                print()
            
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            print(f"   錯誤類型: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"   HTTP 狀態碼: {e.status_code}")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(create_http_tasks())