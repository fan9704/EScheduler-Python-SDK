"""EScheduler SDK 客戶端測試"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch

from escheduler_sdk.client import ESchedulerClient
from escheduler_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    TimeoutError,
    NetworkError
)


class TestESchedulerClient:
    """EScheduler 客戶端測試類"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    @pytest.fixture
    async def client(self):
        """測試客戶端 fixture"""
        client = ESchedulerClient(
            base_url=self.BASE_URL,
            jwt_token="test-jwt-token",
            timeout=10.0
        )
        yield client
        await client.close()
    
    def test_client_initialization(self):
        """測試客戶端初始化"""
        client = ESchedulerClient(
            base_url=self.BASE_URL,
            token="ABCD",
            jwt_token="test-jwt",
            timeout=15.0,
            max_retries=5
        )
        
        assert client.base_url == self.BASE_URL
        assert client.token == "ABCD"
        assert client.jwt_token == "test-jwt"
        assert client.timeout == 15.0
        assert client.max_retries == 5
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == "Bearer test-jwt"
    
    def test_build_url(self):
        """測試 URL 構建"""
        client = ESchedulerClient(base_url=self.BASE_URL)
        
        # 測試基本 URL 構建
        assert client._build_url("/api/v1/scheduler/tasks") == f"{self.BASE_URL}/api/v1/scheduler/tasks"
        assert client._build_url("api/v1/scheduler/tasks") == f"{self.BASE_URL}/api/v1/scheduler/tasks"
        
        # 測試帶斜線的基礎 URL
        client.base_url = f"{self.BASE_URL}/"
        assert client._build_url("/api/v1/scheduler/tasks") == f"{self.BASE_URL}/api/v1/scheduler/tasks"
    
    def test_jwt_token_management(self):
        """測試 JWT token 管理"""
        client = ESchedulerClient(base_url=self.BASE_URL)
        
        # 初始狀態沒有 Authorization header
        assert "Authorization" not in client._client.headers
        
        # 設置 JWT token (模擬真實的 JWT token 格式)
        real_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        client.set_jwt_token(real_jwt)
        assert client.jwt_token == real_jwt
        assert client._client.headers["Authorization"] == f"Bearer {real_jwt}"
        
        # 清除 JWT token
        client.clear_jwt_token()
        assert client.jwt_token is None
        assert "Authorization" not in client._client.headers
    
    @pytest.mark.asyncio
    async def test_successful_request(self, client):
        """測試成功的請求"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "tasks": [
                {
                    "id": "task-123",
                    "name": "測試任務",
                    "schedule_expression": "cron(0 9 * * MON-FRI)",
                    "target_type": "HTTP",
                    "target_config": {"url": "https://api.example.com/webhook"},
                    "state": "ENABLED",
                    "created_at": "2024-01-15T09:00:00Z"
                }
            ],
            "total": 1
        }

        with patch.object(client._client, 'request', return_value=mock_response):
            result = await client.get("/api/v1/scheduler/tasks")
            assert "tasks" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["id"] == "task-123"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """測試錯誤處理"""
        # 測試 401 錯誤 - 無效的 JWT token
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.text = "Invalid authentication credentials"
        mock_response.json.return_value = {
            "detail": "Invalid authentication credentials",
            "error_code": "INVALID_TOKEN"
        }

        with patch.object(client._client, 'request', return_value=mock_response):
            with pytest.raises(AuthenticationError) as exc_info:
                await client.get("/api/v1/scheduler/tasks")
            assert exc_info.value.status_code == 401
            assert "Invalid authentication credentials" in str(exc_info.value)
        
        # 測試 400 錯誤 - 無效的請求參數
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.text = "Invalid schedule expression format"
        mock_response.json.return_value = {
            "detail": "Invalid schedule expression format",
            "error_code": "VALIDATION_ERROR",
            "field": "schedule_expression"
        }
        
        with patch.object(client._client, 'request', return_value=mock_response):
            with pytest.raises(ValidationError):
                await client.post("/api/v1/scheduler/tasks", json_data={"name": "test", "schedule_expression": "invalid"})
        
        # 測試 404 錯誤 - 任務不存在
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_response.text = "Task not found"
        mock_response.json.return_value = {
            "detail": "Task not found",
            "error_code": "TASK_NOT_FOUND",
            "task_id": "non-existent-task"
        }
        
        with patch.object(client._client, 'request', return_value=mock_response):
            with pytest.raises(NotFoundError):
                await client.get("/api/v1/scheduler/tasks/non-existent-task")
        
        # 測試 500 錯誤 - 服務器內部錯誤
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.text = "Database connection failed"
        mock_response.json.return_value = {
            "detail": "Database connection failed",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
        
        with patch.object(client._client, 'request', return_value=mock_response):
            with pytest.raises(ServerError):
                await client.get("/api/v1/scheduler/tasks")
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """測試超時處理"""
        with patch.object(client._client, 'request', side_effect=httpx.TimeoutException("Request timeout after 10 seconds")):
            with pytest.raises(TimeoutError) as exc_info:
                await client.get("/api/v1/scheduler/tasks")
            assert "請求超時" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, client):
        """測試網路錯誤處理"""
        with patch.object(client._client, 'request', side_effect=httpx.NetworkError("Connection refused - server may be down")):
            with pytest.raises(NetworkError) as exc_info:
                await client.get("/api/v1/scheduler/tasks")
            assert "Connection refused" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, client):
        """測試重試機制"""
        # 模擬前兩次請求失敗，第三次成功
        success_response = Mock()
        success_response.is_success = True
        success_response.json.return_value = {
            "message": "Task created successfully",
            "task_id": "task-456",
            "status": "ENABLED"
        }

        mock_responses = [
            httpx.TimeoutException("Request timeout"),
            httpx.NetworkError("Connection failed"),
            success_response
        ]

        with patch.object(client._client, 'request', side_effect=mock_responses):
            with patch('asyncio.sleep'):  # 跳過實際的睡眠
                result = await client.post("/api/v1/scheduler/tasks", json_data={
                    "name": "重試測試任務",
                    "schedule_expression": "rate(5 minutes)",
                    "target_type": "HTTP",
                    "target_config": {"url": "https://api.example.com/webhook"}
                })
                assert result["task_id"] == "task-456"
                assert result["status"] == "ENABLED"
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """測試上下文管理器"""
        async with ESchedulerClient(base_url=self.BASE_URL) as client:
            assert client is not None
            assert client.base_url == self.BASE_URL
            # 模擬在上下文中進行 API 調用
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {"health": "ok", "version": "1.0.0"}
            
            with patch.object(client._client, 'request', return_value=mock_response):
                result = await client.get("/api/v1/health")
                assert result["health"] == "ok"
        # 客戶端應該已經關閉
    
    @pytest.mark.asyncio
    async def test_http_methods(self, client):
        """測試各種 HTTP 方法"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"operation": "success"}
        
        with patch.object(client._client, 'request', return_value=mock_response) as mock_request:
            # 測試 GET - 獲取任務列表
            await client.get("/api/v1/scheduler/tasks", params={"state": "ENABLED", "limit": 10})
            mock_request.assert_called_with(
                method="GET",
                url=f"{self.BASE_URL}/api/v1/scheduler/tasks",
                json=None,
                params={"state": "ENABLED", "limit": 10}
            )
            
            # 測試 POST - 創建新任務
            task_data = {
                "name": "每日備份任務",
                "schedule_expression": "cron(0 2 * * *)",
                "target_type": "HTTP",
                "target_config": {
                    "url": "https://api.example.com/backup",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
            }
            await client.post("/api/v1/scheduler/tasks", json_data=task_data)
            mock_request.assert_called_with(
                method="POST",
                url=f"{self.BASE_URL}/api/v1/scheduler/tasks",
                json=task_data,
                params=None
            )
            
            # 測試 PUT - 完整更新任務
            updated_task_data = {
                "name": "每日備份任務 (更新)",
                "schedule_expression": "cron(0 3 * * *)",
                "target_type": "HTTP",
                "target_config": {
                    "url": "https://api.example.com/backup-v2",
                    "method": "POST"
                }
            }
            await client.put("/api/v1/scheduler/tasks/task-123", json_data=updated_task_data)
            mock_request.assert_called_with(
                method="PUT",
                url=f"{self.BASE_URL}/api/v1/scheduler/tasks/task-123",
                json=updated_task_data,
                params=None
            )
            
            # 測試 PATCH - 部分更新任務狀態
            state_update = {"state": "PAUSED"}
            await client.patch("/api/v1/scheduler/tasks/task-123/state", json_data=state_update)
            mock_request.assert_called_with(
                method="PATCH",
                url=f"{self.BASE_URL}/api/v1/scheduler/tasks/task-123/state",
                json=state_update,
                params=None
            )
            
            # 測試 DELETE - 刪除任務
            await client.delete("/api/v1/scheduler/tasks/task-123")
            mock_request.assert_called_with(
                method="DELETE",
                url=f"{self.BASE_URL}/api/v1/scheduler/tasks/task-123",
                json=None,
                params=None
            )