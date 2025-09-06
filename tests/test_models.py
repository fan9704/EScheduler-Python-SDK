"""EScheduler SDK 數據模型測試"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from escheduler_sdk.models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionResponse,
    SchedulerStatsResponse,
    TaskStateUpdateRequest,
    Team,
    TeamAuthRequest,
    TeamAuthResponse,
    TaskState,
    TargetType,
    ExecutionStatus,
    ScheduleType
)


class TestEnums:
    """測試枚舉類型"""
    
    def test_task_state_enum(self):
        """測試任務狀態枚舉"""
        assert TaskState.ENABLED == "ENABLED"
        assert TaskState.DISABLED == "DISABLED"
        assert TaskState.PAUSED == "PAUSED"
    
    def test_target_type_enum(self):
        """測試目標類型枚舉"""
        assert TargetType.HTTP == "http"
        assert TargetType.WEBHOOK == "webhook"
        assert TargetType.RABBITMQ == "rabbitmq"
        assert TargetType.EMAIL == "email"
    
    def test_execution_status_enum(self):
        """測試執行狀態枚舉"""
        assert ExecutionStatus.PENDING == "PENDING"
        assert ExecutionStatus.RUNNING == "RUNNING"
        assert ExecutionStatus.SUCCEEDED == "SUCCEEDED"
        assert ExecutionStatus.FAILED == "FAILED"
        assert ExecutionStatus.TIMEOUT == "TIMEOUT"
        assert ExecutionStatus.CANCELLED == "CANCELLED"
    
    def test_schedule_type_enum(self):
        """測試排程類型枚舉"""
        assert ScheduleType.CRON == "cron"
        assert ScheduleType.RATE == "rate"
        assert ScheduleType.ONE_TIME == "one_time"
        assert ScheduleType.AT == "at"


class TestScheduledTaskCreate:
    """測試排程任務創建模型"""
    
    def test_valid_task_creation(self):
        """測試有效的任務創建"""
        task_data = ScheduledTaskCreate(
            name="測試任務",
            description="這是一個測試任務",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://httpbin.org/post",
            target_input={"message": "test"},
            max_retry_attempts=3
        )
        
        assert task_data.name == "測試任務"
        assert task_data.description == "這是一個測試任務"
        assert task_data.schedule_expression == "rate(5 minutes)"
        assert task_data.timezone == "Asia/Taipei"
        assert task_data.target_type == TargetType.HTTP
        assert task_data.target_arn == "https://httpbin.org/post"
        assert task_data.target_input == {"message": "test"}
        assert task_data.max_retry_attempts == 3
    
    def test_minimal_task_creation(self):
        """測試最小化任務創建"""
        task_data = ScheduledTaskCreate(
            name="最小任務",
            schedule_expression="cron(0 12 * * ? *)",
            target_type=TargetType.WEBHOOK,
            target_arn="https://example.com/webhook"
        )
        
        assert task_data.name == "最小任務"
        assert task_data.description is None
        assert task_data.timezone == "Asia/Taipei"  # 預設值
        assert task_data.max_retry_attempts == 3  # 預設值
    
    def test_invalid_schedule_expression(self):
        """測試無效的排程表達式"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduledTaskCreate(
                name="無效任務",
                schedule_expression="invalid expression",
                target_type=TargetType.HTTP,
                target_arn="https://example.com"
            )
        
        assert "排程表達式必須是 cron(expression) 或 rate(expression) 格式" in str(exc_info.value)
    
    def test_valid_schedule_expressions(self):
        """測試有效的排程表達式"""
        valid_expressions = [
            "rate(5 minutes)",
            "rate(1 hour)",
            "rate(1 day)",
            "cron(0 12 * * ? *)",
            "cron(0 */2 * * ? *)",
            "cron(0 9 ? * MON-FRI *)"
        ]
        
        for expression in valid_expressions:
            task_data = ScheduledTaskCreate(
                name="測試任務",
                schedule_expression=expression,
                target_type=TargetType.HTTP,
                target_arn="https://example.com"
            )
            assert task_data.schedule_expression == expression
    
    def test_name_validation(self):
        """測試名稱驗證"""
        # 測試空名稱
        with pytest.raises(ValidationError):
            ScheduledTaskCreate(
                name="",
                schedule_expression="rate(5 minutes)",
                target_type=TargetType.HTTP,
                target_arn="https://example.com"
            )
        
        # 測試過長名稱
        with pytest.raises(ValidationError):
            ScheduledTaskCreate(
                name="a" * 256,  # 超過 255 字符
                schedule_expression="rate(5 minutes)",
                target_type=TargetType.HTTP,
                target_arn="https://example.com"
            )
    
    def test_retry_attempts_validation(self):
        """測試重試次數驗證"""
        # 測試負數
        with pytest.raises(ValidationError):
            ScheduledTaskCreate(
                name="測試任務",
                schedule_expression="rate(5 minutes)",
                target_type=TargetType.HTTP,
                target_arn="https://example.com",
                max_retry_attempts=-1
            )
        
        # 測試超過最大值
        with pytest.raises(ValidationError):
            ScheduledTaskCreate(
                name="測試任務",
                schedule_expression="rate(5 minutes)",
                target_type=TargetType.HTTP,
                target_arn="https://example.com",
                max_retry_attempts=11
            )
        
        # 測試有效範圍
        for attempts in [0, 5, 10]:
            task_data = ScheduledTaskCreate(
                name="測試任務",
                schedule_expression="rate(5 minutes)",
                target_type=TargetType.HTTP,
                target_arn="https://example.com",
                max_retry_attempts=attempts
            )
            assert task_data.max_retry_attempts == attempts


class TestScheduledTaskUpdate:
    """測試排程任務更新模型"""
    
    def test_partial_update(self):
        """測試部分更新"""
        update_data = ScheduledTaskUpdate(
            name="新名稱",
            description="新描述"
        )
        
        assert update_data.name == "新名稱"
        assert update_data.description == "新描述"
        assert update_data.schedule_expression is None
        assert update_data.state is None
    
    def test_empty_update(self):
        """測試空更新"""
        update_data = ScheduledTaskUpdate()
        
        # 所有欄位都應該是 None
        assert update_data.name is None
        assert update_data.description is None
        assert update_data.schedule_expression is None
        assert update_data.state is None


class TestTeamModels:
    """測試團隊相關模型"""
    
    def test_team_model(self):
        """測試團隊模型"""
        team = Team(id=1, name="第1小隊")
        
        assert team.id == 1
        assert team.name == "第1小隊"
    
    def test_team_auth_request(self):
        """測試團隊認證請求"""
        auth_request = TeamAuthRequest(token="ABCD")
        
        assert auth_request.token == "ABCD"
    
    def test_team_auth_request_validation(self):
        """測試團隊認證請求驗證"""
        # 測試過短的 token
        with pytest.raises(ValidationError):
            TeamAuthRequest(token="ABC")
        
        # 測試過長的 token
        with pytest.raises(ValidationError):
            TeamAuthRequest(token="ABCDE")
        
        # 測試有效的 token
        valid_tokens = ["ABCD", "1234", "A1B2"]
        for token in valid_tokens:
            auth_request = TeamAuthRequest(token=token)
            assert auth_request.token == token
    
    def test_team_auth_response(self):
        """測試團隊認證回應"""
        team = Team(id=1, name="第1小隊")
        auth_response = TeamAuthResponse(
            status=True,
            team=team,
            access_token="jwt-token-here"
        )
        
        assert auth_response.status is True
        assert auth_response.team.id == 1
        assert auth_response.team.name == "第1小隊"
        assert auth_response.access_token == "jwt-token-here"
    
    def test_team_auth_response_failure(self):
        """測試團隊認證失敗回應"""
        auth_response = TeamAuthResponse(
            status=False,
            team=None,
            access_token=None
        )
        
        assert auth_response.status is False
        assert auth_response.team is None
        assert auth_response.access_token is None


class TestTaskStateUpdateRequest:
    """測試任務狀態更新請求"""
    
    def test_state_update_request(self):
        """測試狀態更新請求"""
        for state in [TaskState.ENABLED, TaskState.DISABLED, TaskState.PAUSED]:
            request = TaskStateUpdateRequest(state=state)
            assert request.state == state


class TestResponseModels:
    """測試回應模型"""
    
    def test_scheduled_task_response(self):
        """測試排程任務回應模型"""
        now = datetime.now()
        
        task_response = ScheduledTaskResponse(
            id=1,
            name="測試任務",
            description="測試描述",
            schedule_expression="rate(5 minutes)",
            timezone="Asia/Taipei",
            target_type="http",
            target_arn="https://example.com",
            target_input={"key": "value"},
            state="ENABLED",
            last_execution_time=now,
            next_execution_time=now,
            execution_count=5,
            max_retry_attempts=3,
            retry_policy=None,
            dead_letter_config=None,
            created_at=now,
            updated_at=now
        )
        
        assert task_response.id == 1
        assert task_response.name == "測試任務"
        assert task_response.state == "ENABLED"
        assert task_response.execution_count == 5
    
    def test_scheduler_stats_response(self):
        """測試排程器統計回應模型"""
        stats = SchedulerStatsResponse(
            total_tasks=10,
            enabled_tasks=8,
            disabled_tasks=2,
            total_executions_today=50,
            successful_executions_today=45,
            failed_executions_today=5
        )
        
        assert stats.total_tasks == 10
        assert stats.enabled_tasks == 8
        assert stats.disabled_tasks == 2
        assert stats.total_executions_today == 50
        assert stats.successful_executions_today == 45
        assert stats.failed_executions_today == 5
    
    def test_task_execution_response(self):
        """測試任務執行回應模型"""
        now = datetime.now()
        
        execution = TaskExecutionResponse(
            id=1,
            task_id=10,
            status=ExecutionStatus.SUCCEEDED,
            started_at=now,
            completed_at=now,
            response_code=200,
            response_body="Success",
            error_message=None,
            attempt_number=1
        )
        
        assert execution.id == 1
        assert execution.task_id == 10
        assert execution.status == ExecutionStatus.SUCCEEDED
        assert execution.response_code == 200
        assert execution.attempt_number == 1