"""進階功能範例 - 任務執行歷史、統計信息和監控"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from escheduler_sdk import (
    ESchedulerSDK,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    TargetType,
    TaskState
)


async def demonstrate_advanced_features():
    """展示進階功能：執行歷史、統計信息、監控等"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here",
        timeout=30.0
    ) as sdk:
        
        print("=== EScheduler 進階功能範例 ===")
        
        # 1. 創建多個不同類型的任務用於演示
        print("\n1. 創建演示任務")
        
        demo_tasks = []
        
        # 數據備份任務
        backup_task = ScheduledTaskCreate(
            name="每日數據備份",
            description="每天凌晨 2 點執行數據備份",
            schedule_expression="cron(0 2 * * *)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://api.example.com/backup",
            target_input={
                "backup_type": "full",
                "retention_days": 30,
                "notify_on_completion": True
            },
            max_retry_attempts=3,
            retry_delay_seconds=300
        )
        
        # 健康檢查任務
        health_check_task = ScheduledTaskCreate(
            name="系統健康檢查",
            description="每 5 分鐘檢查系統健康狀態",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://api.example.com/health",
            target_input={
                "check_database": True,
                "check_cache": True,
                "check_external_apis": True
            },
            max_retry_attempts=2,
            retry_delay_seconds=60
        )
        
        # 報告生成任務
        report_task = ScheduledTaskCreate(
            name="週報生成",
            description="每週一上午 9 點生成週報",
            schedule_expression="cron(0 9 * * 1)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://api.example.com/reports/weekly",
            target_input={
                "report_type": "weekly",
                "include_charts": True,
                "email_recipients": ["manager@example.com", "team@example.com"]
            },
            max_retry_attempts=1
        )
        
        # 創建任務
        for task_data in [backup_task, health_check_task, report_task]:
            try:
                created_task = await sdk.scheduler.create_task(task_data)
                demo_tasks.append(created_task)
                print(f"✅ 創建任務: {created_task.name} (ID: {created_task.id})")
            except Exception as e:
                print(f"❌ 創建任務失敗 {task_data.name}: {e}")
        
        if not demo_tasks:
            print("❌ 沒有成功創建任務，無法演示進階功能")
            return
        
        # 2. 獲取和分析調度器統計信息
        print("\n2. 調度器統計信息")
        
        try:
            stats = await sdk.scheduler.get_scheduler_stats()
            print(f"📊 調度器統計信息:")
            print(f"   總任務數: {stats.total_tasks}")
            print(f"   啟用任務: {stats.enabled_tasks}")
            print(f"   暫停任務: {stats.paused_tasks}")
            print(f"   今日執行次數: {stats.total_executions_today}")
            print(f"   今日成功執行: {stats.successful_executions_today}")
            print(f"   今日失敗執行: {stats.failed_executions_today}")
            
            # 計算成功率
            if stats.total_executions_today > 0:
                success_rate = (stats.successful_executions_today / stats.total_executions_today) * 100
                print(f"   今日成功率: {success_rate:.2f}%")
            
        except Exception as e:
            print(f"❌ 獲取統計信息失敗: {e}")
        
        # 3. 任務執行歷史分析
        print("\n3. 任務執行歷史分析")
        
        for task in demo_tasks[:2]:  # 只分析前兩個任務
            try:
                print(f"\n📈 分析任務: {task.name}")
                
                # 獲取任務執行歷史
                history = await sdk.scheduler.get_task_execution_history(
                    task.id,
                    limit=10  # 獲取最近 10 次執行記錄
                )
                
                if history:
                    print(f"   最近 {len(history)} 次執行記錄:")
                    
                    success_count = 0
                    failure_count = 0
                    total_duration = 0
                    
                    for i, execution in enumerate(history, 1):
                        status_emoji = "✅" if execution.status == "SUCCESS" else "❌"
                        print(f"   {i}. {status_emoji} {execution.execution_time} - {execution.status}")
                        
                        if hasattr(execution, 'duration_ms') and execution.duration_ms:
                            print(f"      執行時間: {execution.duration_ms}ms")
                            total_duration += execution.duration_ms
                        
                        if execution.status == "SUCCESS":
                            success_count += 1
                        else:
                            failure_count += 1
                            if hasattr(execution, 'error_message') and execution.error_message:
                                print(f"      錯誤信息: {execution.error_message}")
                    
                    # 執行統計
                    total_executions = len(history)
                    if total_executions > 0:
                        success_rate = (success_count / total_executions) * 100
                        print(f"   執行統計:")
                        print(f"     成功: {success_count}/{total_executions} ({success_rate:.1f}%)")
                        print(f"     失敗: {failure_count}/{total_executions}")
                        
                        if total_duration > 0:
                            avg_duration = total_duration / total_executions
                            print(f"     平均執行時間: {avg_duration:.1f}ms")
                else:
                    print("   暫無執行歷史")
                
            except Exception as e:
                print(f"❌ 獲取任務 {task.name} 執行歷史失敗: {e}")
        
        # 4. 任務監控和健康檢查
        print("\n4. 任務監控和健康檢查")
        
        async def check_task_health(task_id: str, task_name: str) -> Dict[str, Any]:
            """檢查單個任務的健康狀態"""
            health_info = {
                "task_id": task_id,
                "task_name": task_name,
                "is_healthy": True,
                "issues": []
            }
            
            try:
                # 獲取任務詳情
                task_detail = await sdk.scheduler.get_task(task_id)
                
                # 檢查任務狀態
                if task_detail.state != TaskState.ENABLED:
                    health_info["is_healthy"] = False
                    health_info["issues"].append(f"任務狀態異常: {task_detail.state}")
                
                # 檢查最近執行情況
                try:
                    recent_history = await sdk.scheduler.get_task_execution_history(
                        task_id, limit=5
                    )
                    
                    if recent_history:
                        # 檢查最近 5 次執行的失敗率
                        failed_count = sum(1 for exec in recent_history if exec.status != "SUCCESS")
                        failure_rate = failed_count / len(recent_history)
                        
                        if failure_rate > 0.6:  # 失敗率超過 60%
                            health_info["is_healthy"] = False
                            health_info["issues"].append(f"最近執行失敗率過高: {failure_rate*100:.1f}%")
                        
                        # 檢查是否長時間沒有執行
                        if recent_history:
                            last_execution = recent_history[0]
                            # 這裡假設 execution_time 是 datetime 對象
                            # 實際使用時需要根據 API 返回的格式調整
                            if hasattr(last_execution, 'execution_time'):
                                # 如果超過預期間隔時間的 2 倍沒有執行，標記為異常
                                # 這裡簡化處理，實際應該根據任務的調度表達式計算
                                pass
                    else:
                        health_info["issues"].append("沒有執行歷史記錄")
                        
                except Exception as e:
                    health_info["issues"].append(f"無法獲取執行歷史: {e}")
                
            except Exception as e:
                health_info["is_healthy"] = False
                health_info["issues"].append(f"無法獲取任務詳情: {e}")
            
            return health_info
        
        # 檢查所有演示任務的健康狀態
        print("🏥 任務健康檢查:")
        
        healthy_tasks = 0
        unhealthy_tasks = 0
        
        for task in demo_tasks:
            health_info = await check_task_health(task.id, task.name)
            
            if health_info["is_healthy"]:
                print(f"   ✅ {health_info['task_name']}: 健康")
                healthy_tasks += 1
            else:
                print(f"   ❌ {health_info['task_name']}: 異常")
                for issue in health_info["issues"]:
                    print(f"      - {issue}")
                unhealthy_tasks += 1
        
        print(f"\n健康檢查摘要:")
        print(f"   健康任務: {healthy_tasks}")
        print(f"   異常任務: {unhealthy_tasks}")
        
        # 5. 批量任務管理
        print("\n5. 批量任務管理")
        
        # 批量暫停任務
        print("暫停所有演示任務...")
        paused_tasks = []
        for task in demo_tasks:
            try:
                result = await sdk.scheduler.pause_task(task.id)
                paused_tasks.append(task.id)
                print(f"   ✅ 暫停任務: {task.name}")
            except Exception as e:
                print(f"   ❌ 暫停任務失敗 {task.name}: {e}")
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 批量啟用任務
        print("\n啟用所有演示任務...")
        for task_id in paused_tasks:
            try:
                task_detail = await sdk.scheduler.get_task(task_id)
                result = await sdk.scheduler.enable_task(task_id)
                print(f"   ✅ 啟用任務: {task_detail.name}")
            except Exception as e:
                print(f"   ❌ 啟用任務失敗 {task_id}: {e}")
        
        # 6. 任務搜索和過濾
        print("\n6. 任務搜索和過濾")
        
        # 搜索包含特定關鍵字的任務
        search_keywords = ["備份", "檢查", "報告"]
        
        for keyword in search_keywords:
            try:
                search_results = await sdk.scheduler.search_tasks(
                    query=keyword,
                    limit=10
                )
                
                print(f"🔍 搜索 '{keyword}' 的結果: {len(search_results)} 個任務")
                for task in search_results:
                    print(f"   - {task.name} (ID: {task.id})")
                    
            except Exception as e:
                print(f"❌ 搜索 '{keyword}' 失敗: {e}")
        
        # 7. 任務性能分析
        print("\n7. 任務性能分析")
        
        async def analyze_task_performance(task_id: str, task_name: str):
            """分析任務性能"""
            try:
                print(f"\n📊 分析任務性能: {task_name}")
                
                # 獲取更多執行歷史用於分析
                history = await sdk.scheduler.get_task_execution_history(
                    task_id, limit=50
                )
                
                if not history:
                    print("   暫無足夠的執行數據進行分析")
                    return
                
                # 性能指標
                durations = []
                success_count = 0
                failure_count = 0
                
                for execution in history:
                    if execution.status == "SUCCESS":
                        success_count += 1
                    else:
                        failure_count += 1
                    
                    if hasattr(execution, 'duration_ms') and execution.duration_ms:
                        durations.append(execution.duration_ms)
                
                # 計算統計信息
                total_executions = len(history)
                success_rate = (success_count / total_executions) * 100
                
                print(f"   執行次數: {total_executions}")
                print(f"   成功率: {success_rate:.2f}%")
                
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    min_duration = min(durations)
                    max_duration = max(durations)
                    
                    print(f"   平均執行時間: {avg_duration:.2f}ms")
                    print(f"   最快執行時間: {min_duration}ms")
                    print(f"   最慢執行時間: {max_duration}ms")
                    
                    # 性能建議
                    if avg_duration > 10000:  # 超過 10 秒
                        print(f"   ⚠️  建議: 執行時間較長，考慮優化任務邏輯")
                    
                    if max_duration > avg_duration * 3:  # 最慢執行時間是平均時間的 3 倍以上
                        print(f"   ⚠️  建議: 執行時間不穩定，檢查資源使用情況")
                
                if success_rate < 95:
                    print(f"   ⚠️  建議: 成功率較低，檢查任務配置和目標服務")
                
            except Exception as e:
                print(f"❌ 分析任務 {task_name} 性能失敗: {e}")
        
        # 分析所有演示任務的性能
        for task in demo_tasks:
            await analyze_task_performance(task.id, task.name)
        
        # 8. 清理演示任務
        print("\n8. 清理演示任務")
        
        for task in demo_tasks:
            try:
                result = await sdk.scheduler.delete_task(task.id)
                print(f"✅ 刪除任務: {task.name}")
            except Exception as e:
                print(f"❌ 刪除任務失敗 {task.name}: {e}")
        
        print("\n=== 進階功能演示完成 ===")
        
        # 最佳實踐建議
        print("\n🎯 進階功能使用建議:")
        print("1. 定期檢查調度器統計信息，監控整體健康狀態")
        print("2. 分析任務執行歷史，識別性能瓶頸和失敗模式")
        print("3. 實施任務健康檢查，及時發現和解決問題")
        print("4. 使用批量操作提高管理效率")
        print("5. 利用搜索功能快速定位特定任務")
        print("6. 基於性能分析結果優化任務配置")
        print("7. 建立監控告警機制，自動化問題響應")
        print("8. 定期清理不需要的任務，保持系統整潔")


if __name__ == "__main__":
    # 運行範例
    asyncio.run(demonstrate_advanced_features())