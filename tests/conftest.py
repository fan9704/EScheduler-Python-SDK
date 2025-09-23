"""測試配置和共用 fixtures"""

import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import TargetType
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    print("啟動 Postgres 容器...")
    with PostgresContainer("postgres:16") \
        .with_exposed_ports(5432) as pg:
        yield {
            "POSTGRES_USER": pg.username,
            "POSTGRES_PASSWORD": pg.password,
            "POSTGRES_DB": pg.dbname,
            "POSTGRES_PORT": pg.get_exposed_port(5432),
            "POSTGRES_HOST": pg.get_container_host_ip(),
        }

@pytest.fixture(scope="session")
def rabbitmq():
    print("啟動 RabbitMQ 容器...")
    with DockerContainer("rabbitmq:3.13-management") \
        .with_exposed_ports(5672) as rmq:
        yield {
            "RABBITMQ_HOST": rmq.get_container_host_ip(),
            "RABBITMQ_PORT": rmq.get_exposed_port(5672),
            "RABBITMQ_USER": "guest",
            "RABBITMQ_PASSWORD": "guest", 
            "RABBITMQ_VHOST": "/",
        }

@pytest.fixture(scope="session")
def loki():
    print("啟動 Loki 容器...")
    with DockerContainer("grafana/loki:2.9.2") \
        .with_exposed_ports(3100) as l:
        host = l.get_container_host_ip()
        port = l.get_exposed_port(3100)
        base_url = f"http://{host}:{port}"
        yield f'{base_url}/loki/api/v1/push'

@pytest.fixture(scope="session")
def escheduler_container():
    print("啟動 EScheduler 容器...")
    with DockerContainer("escheduler:latest") \
        .with_env("POSTGRES_USER", postgres["POSTGRES_USER"]) \
        .with_env("POSTGRES_PASSWORD", postgres["POSTGRES_PASSWORD"]) \
        .with_env("POSTGRES_DB", postgres["POSTGRES_DB"]) \
        .with_env("POSTGRES_PORT", postgres["POSTGRES_PORT"]) \
        .with_env("POSTGRES_HOST", postgres["POSTGRES_HOST"]) \
        .with_env("RABBITMQ_HOST", rabbitmq["RABBITMQ_HOST"]) \
        .with_env("RABBITMQ_PORT", rabbitmq["RABBITMQ_PORT"]) \
        .with_env("RABBITMQ_USER", rabbitmq["RABBITMQ_USER"]) \
        .with_env("RABBITMQ_PASSWORD", rabbitmq["RABBITMQ_PASSWORD"]) \
        .with_env("RABBITMQ_VHOST", rabbitmq["RABBITMQ_VHOST"]) \
        .with_env("LOKI_ENDPOINT", loki) \
        .with_exposed_ports(8000) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(8000)
        base_url = f"http://{host}:{port}"
        yield base_url  # 提供給測試使用



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