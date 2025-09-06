"""錯誤處理和重試機制範例"""

import asyncio
from datetime import datetime

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskCreate,
    TargetType,
    # 異常類
    ESchedulerError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    TimeoutError,
    NetworkError
)


async def demonstrate_error_handling():
    """展示各種錯誤處理和重試機制"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here",
        timeout=10.0,  # 較短的超時時間用於演示
        max_retries=3   # 設置重試次數
    ) as sdk:
        
        print("=== 錯誤處理和重試機制範例 ===")
        
        # 1. 處理驗證錯誤
        print("\n1. 處理驗證錯誤")
        try:
            # 嘗試創建一個無效的任務（無效的 cron 表達式）
            invalid_task = ScheduledTaskCreate(
                name="無效任務",
                description="這個任務有無效的 cron 表達式",
                schedule_expression="invalid-cron",  # 無效的表達式
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://httpbin.org/post",
                target_input={"test": "data"}
            )
            
            await sdk.scheduler.create_task(invalid_task)
            print("✅ 任務創建成功（不應該到這裡）")
            
        except ValidationError as e:
            print(f"❌ 驗證錯誤（預期的）: {e}")
            print(f"   狀態碼: {e.status_code}")
            if hasattr(e, 'response_data') and e.response_data:
                print(f"   詳細信息: {e.response_data}")
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
        
        # 2. 處理認證錯誤
        print("\n2. 處理認證錯誤")
        try:
            # 創建一個使用無效 JWT 的客戶端
            async with ESchedulerSDK(
                base_url="http://localhost:8000",
                jwt_token="invalid-jwt-token",
                timeout=5.0
            ) as invalid_sdk:
                await invalid_sdk.scheduler.get_all_tasks()
                print("✅ 獲取任務成功（不應該到這裡）")
                
        except AuthenticationError as e:
            print(f"❌ 認證錯誤（預期的）: {e}")
            print(f"   狀態碼: {e.status_code}")
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
        
        # 3. 處理不存在的資源
        print("\n3. 處理不存在的資源")
        try:
            # 嘗試獲取不存在的任務
            non_existent_id = "non-existent-task-id"
            await sdk.scheduler.get_task(non_existent_id)
            print("✅ 獲取任務成功（不應該到這裡）")
            
        except NotFoundError as e:
            print(f"❌ 資源不存在（預期的）: {e}")
            print(f"   狀態碼: {e.status_code}")
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
        
        # 4. 處理網路錯誤
        print("\n4. 處理網路錯誤")
        try:
            # 使用無效的 URL
            async with ESchedulerSDK(
                base_url="http://invalid-host:9999",
                jwt_token="test-token",
                timeout=2.0,
                max_retries=1  # 減少重試次數以加快演示
            ) as network_sdk:
                await network_sdk.scheduler.get_all_tasks()
                print("✅ 獲取任務成功（不應該到這裡）")
                
        except NetworkError as e:
            print(f"❌ 網路錯誤（預期的）: {e}")
        except TimeoutError as e:
            print(f"❌ 超時錯誤（預期的）: {e}")
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
        
        # 5. 重試機制演示
        print("\n5. 重試機制演示")
        
        # 創建一個有效的任務來演示重試
        try:
            print("創建測試任務...")
            test_task = ScheduledTaskCreate(
                name="重試測試任務",
                description="用於測試重試機制的任務",
                schedule_expression="rate(1 hour)",
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://httpbin.org/post",
                target_input={
                    "test": "retry_mechanism",
                    "created_at": datetime.now().isoformat()
                },
                max_retry_attempts=5  # 設置任務本身的重試次數
            )
            
            created_task = await sdk.scheduler.create_task(test_task)
            print(f"✅ 測試任務創建成功，ID: {created_task.id}")
            
            # 嘗試多次操作來觸發重試機制
            task_id = created_task.id
            
            # 正常操作
            print("執行正常操作...")
            task_detail = await sdk.scheduler.get_task(task_id)
            print(f"✅ 獲取任務詳情成功: {task_detail.name}")
            
            # 手動觸發任務
            print("手動觸發任務...")
            trigger_result = await sdk.scheduler.trigger_task(task_id)
            print(f"✅ 任務觸發成功: {trigger_result.message}")
            
            # 清理：刪除測試任務
            print("清理測試任務...")
            delete_result = await sdk.scheduler.delete_task(task_id)
            print(f"✅ 任務刪除成功: {delete_result.message}")
            
        except Exception as e:
            print(f"❌ 重試演示過程中發生錯誤: {e}")
            print(f"   錯誤類型: {type(e).__name__}")
        
        # 6. 批量操作錯誤處理
        print("\n6. 批量操作錯誤處理")
        
        # 創建多個任務，其中一些可能失敗
        tasks_to_create = [
            {
                "name": "批量任務1",
                "cron": "rate(1 hour)",
                "valid": True
            },
            {
                "name": "批量任務2（無效）",
                "cron": "invalid-expression",
                "valid": False
            },
            {
                "name": "批量任務3",
                "cron": "cron(0 */2 * * *)",
                "valid": True
            }
        ]
        
        successful_tasks = []
        failed_tasks = []
        
        for task_info in tasks_to_create:
            try:
                print(f"創建任務: {task_info['name']}")
                
                task_data = ScheduledTaskCreate(
                    name=task_info['name'],
                    description=f"批量創建的任務 - {task_info['name']}",
                    schedule_expression=task_info['cron'],
                    timezone="Asia/Taipei",
                    target_type=TargetType.HTTP,
                    target_arn="https://httpbin.org/post",
                    target_input={
                        "batch_id": "batch_001",
                        "task_name": task_info['name']
                    }
                )
                
                created_task = await sdk.scheduler.create_task(task_data)
                successful_tasks.append(created_task)
                print(f"  ✅ 成功創建，ID: {created_task.id}")
                
            except ValidationError as e:
                failed_tasks.append({"name": task_info['name'], "error": str(e)})
                print(f"  ❌ 驗證失敗: {e}")
            except Exception as e:
                failed_tasks.append({"name": task_info['name'], "error": str(e)})
                print(f"  ❌ 創建失敗: {e}")
        
        # 批量操作結果
        print(f"\n批量操作結果:")
        print(f"  成功: {len(successful_tasks)} 個任務")
        print(f"  失敗: {len(failed_tasks)} 個任務")
        
        if successful_tasks:
            print("\n成功創建的任務:")
            for task in successful_tasks:
                print(f"  - {task.name} (ID: {task.id})")
        
        if failed_tasks:
            print("\n失敗的任務:")
            for failed in failed_tasks:
                print(f"  - {failed['name']}: {failed['error']}")
        
        # 7. 自定義錯誤處理函數
        print("\n7. 自定義錯誤處理")
        
        async def safe_operation(operation_name, operation_func, *args, **kwargs):
            """安全執行操作的包裝函數"""
            try:
                print(f"執行操作: {operation_name}")
                result = await operation_func(*args, **kwargs)
                print(f"  ✅ {operation_name} 成功")
                return result
            except AuthenticationError as e:
                print(f"  ❌ {operation_name} 認證失敗: {e}")
                return None
            except ValidationError as e:
                print(f"  ❌ {operation_name} 驗證失敗: {e}")
                return None
            except NotFoundError as e:
                print(f"  ❌ {operation_name} 資源不存在: {e}")
                return None
            except TimeoutError as e:
                print(f"  ❌ {operation_name} 超時: {e}")
                return None
            except NetworkError as e:
                print(f"  ❌ {operation_name} 網路錯誤: {e}")
                return None
            except ServerError as e:
                print(f"  ❌ {operation_name} 服務器錯誤: {e}")
                return None
            except RateLimitError as e:
                print(f"  ❌ {operation_name} 請求頻率限制: {e}")
                return None
            except ESchedulerError as e:
                print(f"  ❌ {operation_name} EScheduler 錯誤: {e}")
                return None
            except Exception as e:
                print(f"  ❌ {operation_name} 未知錯誤: {e}")
                return None
        
        # 使用安全操作函數
        tasks = await safe_operation("獲取所有任務", sdk.scheduler.get_all_tasks)
        stats = await safe_operation("獲取統計信息", sdk.scheduler.get_scheduler_stats)
        
        if tasks:
            print(f"  當前共有 {len(tasks)} 個任務")
        
        if stats:
            print(f"  啟用任務: {stats.enabled_tasks}")
            print(f"  今日執行: {stats.total_executions_today}")
        
        # 清理成功創建的任務
        if successful_tasks:
            print("\n清理測試任務...")
            for task in successful_tasks:
                await safe_operation(
                    f"刪除任務 {task.name}",
                    sdk.scheduler.delete_task,
                    task.id
                )
        
        print("\n=== 錯誤處理演示完成 ===")
        print("\n錯誤處理最佳實踐:")
        print("1. 總是使用 try-except 包裝 API 調用")
        print("2. 根據不同的錯誤類型採取不同的處理策略")
        print("3. 記錄錯誤信息以便調試")
        print("4. 對於臨時性錯誤（網路、超時），考慮重試")
        print("5. 對於永久性錯誤（驗證、認證），不要重試")
        print("6. 在批量操作中，單個失敗不應影響其他操作")
        print("7. 提供有意義的錯誤信息給用戶")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(demonstrate_error_handling())