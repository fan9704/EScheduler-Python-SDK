"""Scheduler API End-to-End Tests"""

import pytest
import asyncio
from datetime import datetime
import os
from unittest.mock import patch, AsyncMock

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    TaskState,
    TargetType
)


@pytest.mark.e2e
class TestSchedulerE2E:
    """Scheduler API 端到端測試類"""
    
    @pytest.fixture(scope="class")
    def e2e_config(self):
        """E2E 測試配置"""
        return {
            "base_url": os.getenv("ESCHEDULER_BASE_URL", "http://localhost:8000"),
            "jwt_token": os.getenv("ESCHEDULER_JWT_TOKEN", "test-jwt-token"),
            "timeout": 30.0
        }
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.getenv("ESCHEDULER_BASE_URL", "http://localhost:8000") is None,
        reason="需要設置 ESCHEDULER_BASE_URL 環境變數才能運行真實的 E2E 測試"
    )
    async def test_real_server_workflow(self, e2e_config):
        """測試與真實服務器的完整工作流程"""
        # 直接創建 SDK 實例，不使用有問題的 fixture
        sdk = ESchedulerSDK(**e2e_config)
        
        try:
            # 1. 創建任務
            task_data = ScheduledTaskCreate(
                name=f"E2E測試任務_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description="這是一個端到端測試任務",
                schedule_expression="rate(1 hour)",
                timezone="Asia/Taipei",
                target_type=TargetType.HTTP,
                target_arn="https://httpbin.org/post",
                target_input={
                    "test_type": "e2e",
                    "created_at": datetime.now().isoformat()
                },
                max_retry_attempts=2
            )
            
            created_task = await sdk.scheduler.create_task(task_data)
            
            try:
                assert created_task.id is not None
                assert created_task.name == task_data.name
                assert created_task.state == "ENABLED"  # 預設狀態
                
                # 2. 獲取任務詳情
                retrieved_task = await sdk.scheduler.get_task(created_task.id)
                assert retrieved_task.id == created_task.id
                assert retrieved_task.name == created_task.name
                
                # 3. 測試任務狀態變更
                disabled_task = await sdk.scheduler.disable_task(created_task.id)
                assert disabled_task.state == "DISABLED"
                
                enabled_task = await sdk.scheduler.enable_task(created_task.id)
                assert enabled_task.state == "ENABLED"
                
            finally:
                # 清理：刪除測試任務
                try:
                    await sdk.scheduler.delete_task(created_task.id)
                except Exception:
                    pass  # 忽略清理錯誤
                    
        finally:
            await sdk.close()
    
    @pytest.mark.asyncio
    async def test_mock_complete_workflow(self):
        """測試完整的模擬工作流程（不需要真實服務器）"""
        # 正確地 mock ESchedulerClient
        with patch('escheduler_sdk.sdk.ESchedulerClient') as mock_client_class:
            # 設置 mock 客戶端
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock close 方法
            mock_client.close = AsyncMock()
            
            # 創建正確格式的 mock 數據（使用 datetime 對象）
            now = datetime.now()
            task_data = {
                "id": 1,
                "name": "E2E模擬測試任務",
                "description": "這是一個E2E模擬測試任務",
                "state": "ENABLED",
                "schedule_expression": "rate(1 hour)",
                "timezone": "Asia/Taipei",
                "target_type": "http",
                "target_arn": "https://httpbin.org/post",
                "target_input": {"test": "e2e_mock"},
                "last_execution_time": None,
                "next_execution_time": now,
                "execution_count": 0,
                "max_retry_attempts": 3,
                "retry_policy": None,
                "dead_letter_config": None,
                "created_at": now,
                "updated_at": now
            }
            
            # 設置不同狀態的回應
            enabled_task_data = task_data.copy()
            enabled_task_data["state"] = "ENABLED"
            
            disabled_task_data = task_data.copy()
            disabled_task_data["state"] = "DISABLED"
            
            paused_task_data = task_data.copy()
            paused_task_data["state"] = "PAUSED"
            
            # 設置 mock 回應序列
            mock_client.post.side_effect = [
                task_data,  # create_task
                {"message": "任務已觸發"},  # trigger_task
            ]
            
            mock_client.get.side_effect = [
                task_data,  # get_task
                [task_data],  # get_all_tasks
                [task_data],  # search_tasks
                {  # get_scheduler_stats
                    "total_tasks": 5,
                    "enabled_tasks": 3,
                    "disabled_tasks": 2,
                    "total_executions_today": 25,
                    "successful_executions_today": 20,
                    "failed_executions_today": 5
                }
            ]
            
            mock_client.put.return_value = task_data  # update_task
            
            mock_client.patch.side_effect = [
                disabled_task_data,  # disable_task
                enabled_task_data,   # enable_task
                paused_task_data,    # pause_task
            ]
            
            mock_client.delete.return_value = {"message": "任務已刪除"}
            
            # 創建 SDK 實例
            sdk = ESchedulerSDK(
                base_url="http://mock-server:8000",
                jwt_token="mock-token"
            )
            
            try:
                # 1. 創建任務
                task_create = ScheduledTaskCreate(
                    name="E2E模擬測試任務",
                    description="這是一個E2E模擬測試任務",
                    schedule_expression="rate(1 hour)",
                    target_type=TargetType.HTTP,
                    target_arn="https://httpbin.org/post",
                    target_input={"test": "e2e_mock"}
                )
                
                created_task = await sdk.scheduler.create_task(task_create)
                assert created_task.id == 1
                assert created_task.name == "E2E模擬測試任務"
                
                # 2. 獲取任務
                retrieved_task = await sdk.scheduler.get_task(1)
                assert retrieved_task.id == 1
                
                # 3. 更新任務
                update_data = ScheduledTaskUpdate(description="更新後的描述")
                updated_task = await sdk.scheduler.update_task(1, update_data)
                assert updated_task.id == 1
                
                # 4. 測試任務狀態變更
                disabled_task = await sdk.scheduler.disable_task(1)
                assert disabled_task.state == "DISABLED"
                
                enabled_task = await sdk.scheduler.enable_task(1)
                assert enabled_task.state == "ENABLED"
                
                paused_task = await sdk.scheduler.pause_task(1)
                assert paused_task.state == "PAUSED"
                
                # 5. 手動觸發任務
                trigger_result = await sdk.scheduler.trigger_task(1)
                assert "觸發" in trigger_result.message
                
                # 6. 獲取所有任務
                all_tasks = await sdk.scheduler.get_all_tasks()
                assert len(all_tasks) == 1
                
                # 7. 搜索任務
                search_results = await sdk.scheduler.search_tasks("E2E")
                assert len(search_results) == 1
                
                # 8. 獲取統計信息
                stats = await sdk.scheduler.get_scheduler_stats()
                assert stats.total_tasks == 5
                assert stats.enabled_tasks == 3
                
                # 9. 刪除任務
                delete_result = await sdk.scheduler.delete_task(1)
                assert "刪除" in delete_result.message
                
            finally:
                await sdk.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_mock(self):
        """測試並發操作（使用 mock）"""
        with patch('escheduler_sdk.sdk.ESchedulerClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock close 方法
            mock_client.close = AsyncMock()
            
            # 創建正確格式的基礎任務數據
            now = datetime.now()
            base_task_data = {
                "schedule_expression": "rate(2 hours)",
                "timezone": "Asia/Taipei",
                "target_type": "http",
                "target_arn": "https://httpbin.org/post",
                "last_execution_time": None,
                "next_execution_time": now,
                "execution_count": 0,
                "max_retry_attempts": 3,
                "retry_policy": None,
                "dead_letter_config": None,
                "created_at": now,
                "updated_at": now
            }
            
            # Mock 並發創建任務的回應
            task_responses = [
                {
                    **base_task_data,
                    "id": i,
                    "name": f"並發測試任務_{i}",
                    "description": f"並發測試任務 {i}",
                    "state": "ENABLED",
                    "target_input": {"task_index": i}
                }
                for i in range(1, 4)
            ]
            
            mock_client.post.side_effect = task_responses
            mock_client.get.side_effect = task_responses
            mock_client.patch.side_effect = [
                {**task, "state": "DISABLED"} for task in task_responses
            ]
            mock_client.delete.side_effect = [
                {"message": "任務已刪除"} for _ in range(3)
            ]
            
            sdk = ESchedulerSDK(
                base_url="http://mock-server:8000",
                jwt_token="mock-token"
            )
            
            try:
                # 創建多個任務
                tasks_to_create = 3
                create_tasks = []
                
                for i in range(tasks_to_create):
                    task_data = ScheduledTaskCreate(
                        name=f"並發測試任務_{i}",
                        description=f"並發測試任務 {i}",
                        schedule_expression="rate(2 hours)",
                        target_type=TargetType.HTTP,
                        target_arn="https://httpbin.org/post",
                        target_input={"task_index": i}
                    )
                    create_tasks.append(sdk.scheduler.create_task(task_data))
                
                # 並發創建任務
                created_tasks = await asyncio.gather(*create_tasks)
                assert len(created_tasks) == tasks_to_create
                
                # 並發獲取任務
                get_tasks = [sdk.scheduler.get_task(task.id) for task in created_tasks]
                retrieved_tasks = await asyncio.gather(*get_tasks)
                assert len(retrieved_tasks) == tasks_to_create
                
                # 並發更新任務狀態
                disable_tasks = [sdk.scheduler.disable_task(task.id) for task in created_tasks]
                disabled_tasks = await asyncio.gather(*disable_tasks)
                
                for task in disabled_tasks:
                    assert task.state == "DISABLED"
                
                # 並發刪除任務
                delete_tasks = [sdk.scheduler.delete_task(task.id) for task in created_tasks]
                delete_results = await asyncio.gather(*delete_tasks)
                assert len(delete_results) == tasks_to_create
                
            finally:
                await sdk.close()