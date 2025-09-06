"""Cron 表達式排程範例"""

import asyncio
from datetime import datetime

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskCreate,
    TargetType
)


async def create_cron_tasks():
    """創建各種 Cron 表達式的排程任務範例"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here",
        timeout=30.0
    ) as sdk:
        
        try:
            print("=== Cron 表達式排程範例 ===")
            print("Cron 格式: 分 時 日 月 星期")
            print("範例將創建各種常見的排程模式\n")
            
            # 定義各種 Cron 排程範例
            cron_examples = [
                {
                    "name": "每分鐘執行",
                    "cron": "cron(* * * * *)",
                    "description": "每分鐘執行一次（測試用）",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "minute_test"}
                },
                {
                    "name": "每小時執行",
                    "cron": "cron(0 * * * *)",
                    "description": "每小時的第0分鐘執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "hourly_task"}
                },
                {
                    "name": "每天早上9點",
                    "cron": "cron(0 9 * * *)",
                    "description": "每天早上9點執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "daily_morning"}
                },
                {
                    "name": "每天晚上11點",
                    "cron": "cron(0 23 * * *)",
                    "description": "每天晚上11點執行（日終處理）",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "daily_night"}
                },
                {
                    "name": "工作日早上8點",
                    "cron": "cron(0 8 * * MON-FRI)",
                    "description": "週一到週五早上8點執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "weekday_morning"}
                },
                {
                    "name": "週末上午10點",
                    "cron": "cron(0 10 * * SAT,SUN)",
                    "description": "週六和週日上午10點執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "weekend_task"}
                },
                {
                    "name": "每週一早上9點",
                    "cron": "cron(0 9 * * MON)",
                    "description": "每週一早上9點執行（週報）",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "weekly_report"}
                },
                {
                    "name": "每月1號凌晨2點",
                    "cron": "cron(0 2 1 * *)",
                    "description": "每月1號凌晨2點執行（月報）",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "monthly_report"}
                },
                {
                    "name": "每季度第一天",
                    "cron": "cron(0 3 1 1,4,7,10 *)",
                    "description": "每季度第一天凌晨3點執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "quarterly_task"}
                },
                {
                    "name": "每年1月1號",
                    "cron": "cron(0 0 1 1 *)",
                    "description": "每年1月1號午夜執行（年度任務）",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "yearly_task"}
                },
                {
                    "name": "每30分鐘",
                    "cron": "cron(0,30 * * * *)",
                    "description": "每小時的第0分和第30分執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "half_hourly"}
                },
                {
                    "name": "每15分鐘",
                    "cron": "cron(0,15,30,45 * * * *)",
                    "description": "每15分鐘執行一次",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "quarter_hourly"}
                },
                {
                    "name": "工作時間每2小時",
                    "cron": "cron(0 9-17/2 * * MON-FRI)",
                    "description": "工作日9-17點每2小時執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "business_hours"}
                },
                {
                    "name": "每月最後一天",
                    "cron": "cron(0 23 L * *)",
                    "description": "每月最後一天晚上11點執行",
                    "target": "https://httpbin.org/post",
                    "data": {"type": "month_end"}
                }
            ]
            
            created_tasks = []
            
            # 創建所有範例任務
            for i, example in enumerate(cron_examples, 1):
                print(f"{i:2d}. 創建任務: {example['name']}")
                print(f"    Cron: {example['cron']}")
                print(f"    說明: {example['description']}")
                
                try:
                    task_data = ScheduledTaskCreate(
                        name=example['name'],
                        description=example['description'],
                        schedule_expression=example['cron'],
                        timezone="Asia/Taipei",
                        target_type=TargetType.HTTP,
                        target_arn=example['target'],
                        target_input={
                            **example['data'],
                            "created_at": datetime.now().isoformat(),
                            "example_id": i
                        },
                        max_retry_attempts=2
                    )
                    
                    created_task = await sdk.scheduler.create_task(task_data)
                    created_tasks.append(created_task)
                    print(f"    ✅ 創建成功，ID: {created_task.id}")
                    
                    if created_task.next_execution_time:
                        print(f"    下次執行: {created_task.next_execution_time}")
                    
                except Exception as e:
                    print(f"    ❌ 創建失敗: {e}")
                
                print()
            
            # 顯示創建結果摘要
            print(f"=== 創建結果摘要 ===")
            print(f"成功創建 {len(created_tasks)} 個任務")
            print("\n任務列表:")
            
            for task in created_tasks:
                print(f"  - {task.name}")
                print(f"    ID: {task.id}")
                print(f"    狀態: {task.state}")
                print(f"    排程: {task.schedule_expression}")
                if task.next_execution_time:
                    print(f"    下次執行: {task.next_execution_time}")
                print()
            
            # 獲取排程器統計
            print("=== 排程器統計 ===")
            stats = await sdk.scheduler.get_scheduler_stats()
            print(f"總任務數: {stats.total_tasks}")
            print(f"啟用任務: {stats.enabled_tasks}")
            print(f"暫停任務: {stats.disabled_tasks}")
            
            # 常用 Cron 表達式說明
            print("\n=== 常用 Cron 表達式說明 ===")
            print("格式: 分 時 日 月 星期")
            print("特殊字符:")
            print("  * : 任意值")
            print("  , : 列舉多個值 (例如: 1,3,5)")
            print("  - : 範圍 (例如: 1-5)")
            print("  / : 步長 (例如: */5 表示每5個單位)")
            print("  L : 最後 (僅用於日期，表示月份最後一天)")
            print("\n星期對應:")
            print("  SUN=0, MON=1, TUE=2, WED=3, THU=4, FRI=5, SAT=6")
            print("  也可以使用: SUN, MON, TUE, WED, THU, FRI, SAT")
            
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            print(f"   錯誤類型: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"   HTTP 狀態碼: {e.status_code}")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(create_cron_tasks())