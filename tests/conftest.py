"""測試配置和共用 fixtures"""

import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import TargetType


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_task_create_data():
    """範例任務創建數據"""
    return {
        "name": "測試任務",
        "description": "這是一個測試任務",
        "schedule_expression": "rate(5 minutes)",
        "timezone": "Asia/Taipei",
        "target_type": TargetType.HTTP,
        "target_arn": "https://httpbin.org/post",
        "target_input": {"message": "test"},
        "max_retry_attempts": 3
    }


@pytest.fixture
def sample_task_response_data():
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


@pytest.fixture
async def test_sdk() -> AsyncGenerator[ESchedulerSDK, None]:
    """測試用 SDK 實例"""
    sdk = ESchedulerSDK(
        base_url="http://localhost:8000",
        jwt_token="test-jwt-token",
        timeout=10.0
    )
    yield sdk
    await sdk.close()


# 標記配置
pytest_plugins = []


def pytest_configure(config):
    """配置 pytest 標記"""
    config.addinivalue_line(
        "markers", "e2e: 標記為端到端測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記為整合測試"
    )
    config.addinivalue_line(
        "markers", "unit: 標記為單元測試"
    )
    config.addinivalue_line(
        "markers", "slow: 標記為慢速測試"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試項目收集"""
    # 為 e2e 目錄下的測試添加 e2e 標記
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)