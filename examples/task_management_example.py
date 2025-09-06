"""任務管理範例"""

import asyncio
from datetime import datetime

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskUpdate,
    TaskState
)


async def manage_tasks():
    """任務管理操作範例"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here",
        timeout=30.0
    ) as sdk:
        
        try:
            print("=== 任務管理範例 ===")
            
            # 1. 獲取所有任務
            print("\n1. 獲取所有任務")
            all_tasks = await sdk.scheduler.get_all_tasks()
            print(f"找到 {len(all_tasks)} 個任務")
            
            if not all_tasks:
                print("沒有找到任務，請先創建一些任務")
                return
            
            # 顯示任務列表
            for i, task in enumerate(all_tasks, 1):
                print(f"  {i}. {task.name}")
                print(f"     ID: {task.id}")
                print(f"     狀態: {task.state}")
                print(f"     排程: {task.schedule_expression}")
                print(f"     執行次數: {task.execution_count}")
                print()
            
            # 選擇第一個任務進行操作
            task_to_manage = all_tasks[0]
            task_id = task_to_manage.id
            print(f"選擇任務進行管理: {task_to_manage.name} (ID: {task_id})")
            
            # 2. 獲取任務詳細信息
            print("\n2. 獲取任務詳細信息")
            task_detail = await sdk.scheduler.get_task(task_id)
            print(f"任務詳情:")
            print(f"  名稱: {task_detail.name}")
            print(f"  描述: {task_detail.description}")
            print(f"  創建時間: {task_detail.created_at}")
            print(f"  更新時間: {task_detail.updated_at}")
            print(f"  下次執行: {task_detail.next_execution_time}")
            print(f"  目標配置: {task_detail.target_input}")
            
            # 3. 更新任務配置
            print("\n3. 更新任務配置")
            update_data = ScheduledTaskUpdate(
                description=f"更新於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                target_input={
                    **task_detail.target_input,
                    "updated_at": datetime.now().isoformat(),
                    "version": "2.0"
                }
            )
            
            updated_task = await sdk.scheduler.update_task(task_id, update_data)
            print(f"✅ 任務更新成功")
            print(f"  新描述: {updated_task.description}")
            
            # 4. 任務狀態管理
            print("\n4. 任務狀態管理")
            
            # 檢查當前狀態
            current_state = updated_task.state
            print(f"當前狀態: {current_state}")
            
            if current_state == TaskState.ENABLED:
                # 暫停任務
                print("暫停任務...")
                paused_task = await sdk.scheduler.pause_task(task_id)
                print(f"✅ 任務已暫停，狀態: {paused_task.state}")
                
                # 等待一下
                await asyncio.sleep(2)
                
                # 重新啟用任務
                print("重新啟用任務...")
                enabled_task = await sdk.scheduler.enable_task(task_id)
                print(f"✅ 任務已啟用，狀態: {enabled_task.state}")
                
            elif current_state == TaskState.PAUSED:
                # 啟用任務
                print("啟用任務...")
                enabled_task = await sdk.scheduler.enable_task(task_id)
                print(f"✅ 任務已啟用，狀態: {enabled_task.state}")
            
            # 5. 手動觸發任務
            print("\n5. 手動觸發任務")
            trigger_result = await sdk.scheduler.trigger_task(task_id)
            print(f"✅ 任務觸發成功: {trigger_result.message}")
            
            # 6. 搜索任務
            print("\n6. 搜索任務")
            search_keyword = task_to_manage.name.split()[0]  # 使用任務名稱的第一個詞
            search_results = await sdk.scheduler.search_tasks(search_keyword)
            print(f"搜索關鍵字 '{search_keyword}' 找到 {len(search_results)} 個任務:")
            for task in search_results:
                print(f"  - {task.name} (ID: {task.id})")
            
            # 7. 獲取任務執行歷史（如果有的話）
            print("\n7. 獲取任務執行歷史")
            try:
                executions = await sdk.scheduler.get_task_executions(task_id)
                print(f"找到 {len(executions)} 次執行記錄:")
                for execution in executions[-5:]:  # 顯示最近5次執行
                    print(f"  - {execution.execution_time}: {execution.status}")
                    if execution.error_message:
                        print(f"    錯誤: {execution.error_message}")
            except Exception as e:
                print(f"無法獲取執行歷史: {e}")
            
            # 8. 獲取排程器統計
            print("\n8. 排程器統計")
            stats = await sdk.scheduler.get_scheduler_stats()
            print(f"排程器統計:")
            print(f"  總任務數: {stats.total_tasks}")
            print(f"  啟用任務: {stats.enabled_tasks}")
            print(f"  暫停任務: {stats.disabled_tasks}")
            print(f"  今日執行: {stats.total_executions_today}")
            print(f"  今日成功: {stats.successful_executions_today}")
            print(f"  今日失敗: {stats.failed_executions_today}")
            
            # 9. 批量操作示例
            print("\n9. 批量操作示例")
            
            # 獲取所有啟用的任務
            enabled_tasks = [task for task in all_tasks if task.state == TaskState.ENABLED]
            print(f"找到 {len(enabled_tasks)} 個啟用的任務")
            
            # 批量暫停（僅作示例，實際使用時要小心）
            if len(enabled_tasks) > 1:
                print("批量暫停前兩個啟用的任務...")
                for task in enabled_tasks[:2]:
                    try:
                        paused = await sdk.scheduler.pause_task(task.id)
                        print(f"  ✅ {task.name} 已暫停")
                    except Exception as e:
                        print(f"  ❌ {task.name} 暫停失敗: {e}")
                
                # 等待一下
                await asyncio.sleep(2)
                
                # 批量重新啟用
                print("批量重新啟用...")
                for task in enabled_tasks[:2]:
                    try:
                        enabled = await sdk.scheduler.enable_task(task.id)
                        print(f"  ✅ {task.name} 已啟用")
                    except Exception as e:
                        print(f"  ❌ {task.name} 啟用失敗: {e}")
            
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            print(f"   錯誤類型: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"   HTTP 狀態碼: {e.status_code}")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(manage_tasks())