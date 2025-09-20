"""Scheduler API Unit Tests"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from escheduler_sdk.scheduler import SchedulerAPI
from escheduler_sdk.models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionResponse,
    SchedulerStatsResponse,
    TaskStateUpdateRequest,
    TaskState,
    TargetType,
    MessageResponse
)
from escheduler_sdk.exceptions import (
    NotFoundError,
    ValidationError,
    AuthenticationError
)


@pytest.mark.unit
class TestSchedulerAPI:
    """Scheduler API 單元測試類"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock EScheduler 客戶端"""
        client = Mock()
        client.post = AsyncMock()
        client.get = AsyncMock()
        client.put = AsyncMock()
        client.patch = AsyncMock()
        client.delete = AsyncMock()
        return client
    
    @pytest.fixture
    def scheduler_api(self, mock_client):
        """Scheduler API 實例"""
        return SchedulerAPI(mock_client)
    
    @pytest.fixture
    def sample_task_create(self):
        """範例任務創建數據"""
        return ScheduledTaskCreate(
            name="測試任務",
            description="這是一個測試任務",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://httpbin.org/post",
            target_input={"message": "test"},
            max_retry_attempts=3
        )
    
    @pytest.fixture
    def sample_task_response(self):
        """範例任務回應數據"""
        now = datetime.now()
        return {
            "id": 1,
            "name": "測試任務",
            "description": "這是一個測試任務",
            "schedule_expression": "rate(5 minutes)",
            "timezone": "Asia/Taipei",
            "target_type": "http",
            "target_arn": "https://httpbin.org/post",
            "target_input": {"message": "test"},
            "state": "ENABLED",
            "last_execution_time": now,
            "next_execution_time": now,
            "execution_count": 0,
            "max_retry_attempts": 3,
            "retry_policy": None,
            "dead_letter_config": None,
            "created_at": now,
            "updated_at": now
        }

    @pytest.mark.asyncio
    async def test_create_task_success(self, scheduler_api, mock_client, sample_task_create, sample_task_response):
        """測試成功創建任務"""
        # 設置 mock 回應
        mock_client.post.return_value = sample_task_response
        
        # 執行測試
        result = await scheduler_api.create_task(sample_task_create)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.id == 1
        assert result.name == "測試任務"
        assert result.state == TaskState.ENABLED
        
        # 驗證 API 調用
        mock_client.post.assert_called_once_with(
            "/api/scheduler",
            json_data=sample_task_create.model_dump(exclude_none=True)
        )
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, scheduler_api, mock_client):
        """測試創建任務時的驗證錯誤"""
        # 設置 mock 拋出驗證錯誤
        mock_client.post.side_effect = ValidationError("驗證失敗")
        
        # 創建無效的任務數據
        invalid_task = ScheduledTaskCreate(
            name="測試",  # 有效名稱
            schedule_expression="rate(5 minutes)",
            target_type=TargetType.HTTP,
            target_arn="https://httpbin.org/post"
        )
        
        # 驗證拋出異常
        with pytest.raises(ValidationError):
            await scheduler_api.create_task(invalid_task)
    
    @pytest.mark.asyncio
    async def test_get_all_tasks_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功獲取所有任務"""
        # 設置 mock 回應
        mock_client.get.return_value = [sample_task_response]
        
        # 執行測試
        result = await scheduler_api.get_all_tasks()
        
        # 驗證結果
        assert len(result) == 1
        assert isinstance(result[0], ScheduledTaskResponse)
        assert result[0].id == 1
        
        # 驗證 API 調用
        mock_client.get.assert_called_once_with("/api/scheduler", params={})
    
    @pytest.mark.asyncio
    async def test_get_all_tasks_with_state_filter(self, scheduler_api, mock_client, sample_task_response):
        """測試使用狀態過濾獲取任務"""
        # 設置 mock 回應
        mock_client.get.return_value = [sample_task_response]
        
        # 執行測試
        result = await scheduler_api.get_all_tasks(state=TaskState.ENABLED)
        
        # 驗證結果
        assert len(result) == 1
        
        # 驗證 API 調用
        mock_client.get.assert_called_once_with(
            "/api/scheduler", 
            params={"state": "ENABLED"}
        )
    
    @pytest.mark.asyncio
    async def test_get_task_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功獲取單個任務"""
        # 設置 mock 回應
        mock_client.get.return_value = sample_task_response
        
        # 執行測試
        result = await scheduler_api.get_task(1)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.id == 1
        
        # 驗證 API 調用
        mock_client.get.assert_called_once_with("/api/scheduler/1")
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self, scheduler_api, mock_client):
        """測試獲取不存在的任務"""
        # 設置 mock 拋出 NotFoundError
        mock_client.get.side_effect = NotFoundError("任務不存在")
        
        # 驗證拋出異常
        with pytest.raises(NotFoundError):
            await scheduler_api.get_task(999)
    
    @pytest.mark.asyncio
    async def test_update_task_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功更新任務"""
        # 設置 mock 回應
        updated_response = sample_task_response.copy()
        updated_response["name"] = "更新後的任務"
        mock_client.put.return_value = updated_response
        
        # 創建更新數據
        update_data = ScheduledTaskUpdate(name="更新後的任務")
        
        # 執行測試
        result = await scheduler_api.update_task(1, update_data)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.name == "更新後的任務"
        
        # 驗證 API 調用
        mock_client.put.assert_called_once_with(
            "/api/scheduler/1",
            json_data=update_data.model_dump(exclude_none=True)
        )
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, scheduler_api, mock_client):
        """測試成功刪除任務"""
        # 設置 mock 回應
        mock_client.delete.return_value = {"message": "任務已刪除"}
        
        # 執行測試
        result = await scheduler_api.delete_task(1)
        
        # 驗證結果
        assert isinstance(result, MessageResponse)
        assert result.message == "任務已刪除"
        
        # 驗證 API 調用
        mock_client.delete.assert_called_once_with("/api/scheduler/1")
    
    @pytest.mark.asyncio
    async def test_update_task_state_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功更新任務狀態"""
        # 設置 mock 回應
        updated_response = sample_task_response.copy()
        updated_response["state"] = "DISABLED"
        mock_client.patch.return_value = updated_response
        
        # 創建狀態更新數據
        state_data = TaskStateUpdateRequest(state=TaskState.DISABLED)
        
        # 執行測試
        result = await scheduler_api.update_task_state(1, state_data)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.state == "DISABLED"
        
        # 驗證 API 調用
        mock_client.patch.assert_called_once_with(
            "/api/scheduler/1/state",
            json_data=state_data.model_dump()
        )
    
    @pytest.mark.asyncio
    async def test_trigger_task_success(self, scheduler_api, mock_client):
        """測試成功觸發任務"""
        # 設置 mock 回應
        mock_client.post.return_value = {"message": "任務已觸發"}
        
        # 執行測試
        result = await scheduler_api.trigger_task(1)
        
        # 驗證結果
        assert isinstance(result, MessageResponse)
        assert result.message == "任務已觸發"
        
        # 驗證 API 調用
        mock_client.post.assert_called_once_with("/api/scheduler/1/trigger")
    
    @pytest.mark.asyncio
    async def test_get_scheduler_stats_success(self, scheduler_api, mock_client):
        """測試成功獲取排程器統計"""
        # 設置 mock 回應
        stats_data = {
            "total_tasks": 10,
            "enabled_tasks": 8,
            "disabled_tasks": 2,
            "total_executions_today": 50,
            "successful_executions_today": 45,
            "failed_executions_today": 5
        }
        mock_client.get.return_value = stats_data
        
        # 執行測試
        result = await scheduler_api.get_scheduler_stats()
        
        # 驗證結果
        assert isinstance(result, SchedulerStatsResponse)
        assert result.total_tasks == 10
        assert result.enabled_tasks == 8
        assert result.failed_executions_today == 5
        
        # 驗證 API 調用
        mock_client.get.assert_called_once_with("/api/scheduler/stats")
    
    @pytest.mark.asyncio
    async def test_search_tasks_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功搜索任務"""
        # 設置 mock 回應
        mock_client.get.return_value = [sample_task_response]
        
        # 執行測試
        result = await scheduler_api.search_tasks("測試")
        
        # 驗證結果
        assert len(result) == 1
        assert isinstance(result[0], ScheduledTaskResponse)
        assert result[0].name == "測試任務"
        
        # 驗證 API 調用
        mock_client.get.assert_called_once_with(
            "/api/scheduler/search",
            params={"keyword": "測試"}
        )
    
    @pytest.mark.asyncio
    async def test_enable_task_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功啟用任務"""
        # 設置 mock 回應
        mock_client.patch.return_value = sample_task_response
        
        # 執行測試
        result = await scheduler_api.enable_task(1)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.state == "ENABLED"
        
        # 驗證 API 調用
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/api/scheduler/1/state"
        assert call_args[1]["json_data"]["state"] == "ENABLED"
    
    @pytest.mark.asyncio
    async def test_disable_task_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功禁用任務"""
        # 設置 mock 回應
        disabled_response = sample_task_response.copy()
        disabled_response["state"] = "DISABLED"
        mock_client.patch.return_value = disabled_response
        
        # 執行測試
        result = await scheduler_api.disable_task(1)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.state == "DISABLED"
        
        # 驗證 API 調用
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/api/scheduler/1/state"
        assert call_args[1]["json_data"]["state"] == "DISABLED"
    
    @pytest.mark.asyncio
    async def test_pause_task_success(self, scheduler_api, mock_client, sample_task_response):
        """測試成功暫停任務"""
        # 設置 mock 回應
        paused_response = sample_task_response.copy()
        paused_response["state"] = "PAUSED"
        mock_client.patch.return_value = paused_response
        
        # 執行測試
        result = await scheduler_api.pause_task(1)
        
        # 驗證結果
        assert isinstance(result, ScheduledTaskResponse)
        assert result.state == "PAUSED"
        
        # 驗證 API 調用
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[0][0] == "/api/scheduler/1/state"
        assert call_args[1]["json_data"]["state"] == "PAUSED"
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, scheduler_api, mock_client, sample_task_create):
        """測試認證錯誤"""
        # 設置 mock 拋出認證錯誤
        mock_client.post.side_effect = AuthenticationError("認證失敗")
        
        # 驗證拋出異常
        with pytest.raises(AuthenticationError):
            await scheduler_api.create_task(sample_task_create)