"""測試配置和共用 fixtures"""

import pytest
import asyncio
import pytest_asyncio
from datetime import datetime
from typing import AsyncGenerator

from escheduler_sdk import ESchedulerSDK
from escheduler_sdk.models import TargetType
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import wait_for_logs

@pytest.fixture(scope="session")
def docker_network():
    import docker
    client = docker.from_env()
    network = client.networks.create("test-network", driver="bridge")
    yield network
    network.remove()

@pytest.fixture(scope="session")
def postgres(docker_network):
    print("啟動 Postgres 容器...")
    with PostgresContainer("postgres:16") \
        .with_network(docker_network) \
        .with_name("test-postgres")  as pg:
        yield pg

@pytest.fixture(scope="session")
def rabbitmq(docker_network):
    print("啟動 RabbitMQ 容器...")
    with DockerContainer("rabbitmq:3.13-management") \
        .with_network(docker_network) \
        .with_name("test-rabbitmq") as rmq:
        yield rmq

@pytest.fixture(scope="session")
def loki(docker_network):
    print("啟動 Loki 容器...")
    with DockerContainer("grafana/loki:2.9.2") \
        .with_network(docker_network) \
        .with_name("test-loki")  as l:
        yield l

@pytest.fixture(scope="session")
def escheduler_base_url(
    postgres: PostgresContainer,
    rabbitmq: DockerContainer,
    loki: DockerContainer,
    docker_network
) -> str:
    print("啟動 EScheduler 容器...")

    # 從依賴的容器 fixture 取得連線資訊
    pg_host = "test-postgres"
    pg_port = "5432"
    pg_user = postgres.username
    pg_password = postgres.password
    pg_dbname = postgres.dbname
    print("POSTGRESQL ENV")
    print(f"PG_HOST: {pg_host}")
    print(f"PG_PORT: {pg_port}")
    print(f"PG_USER: {pg_user}")
    print(f"PG_PASSWORD: {pg_password}")
    print(f"PG_DBNAME: {pg_dbname}")
    rmq_host = "test-rabbitmq"
    rmq_port = "5672"
    print("RABBITMQ ENV")
    print(f"RMQ_HOST: {rmq_host}")
    print(f"RMQ_PORT: {rmq_port}")

    loki_host = "test-loki"
    loki_port = "3100"
    loki_endpoint = f"http://{loki_host}:{loki_port}/loki/api/v1/push"

    # 啟動主應用程式容器
    with DockerContainer("ghcr.io/fan9704/escheduler") \
        .with_env("POSTGRES_USER", pg_user) \
        .with_env("POSTGRES_PASSWORD", pg_password) \
        .with_env("POSTGRES_DB", pg_dbname) \
        .with_env("POSTGRES_PORT", pg_port) \
        .with_env("POSTGRES_HOST", pg_host) \
        .with_env("RABBITMQ_HOST", rmq_host) \
        .with_env("RABBITMQ_PORT", rmq_port) \
        .with_env("RABBITMQ_USER", "guest") \
        .with_env("RABBITMQ_PASSWORD", "guest") \
        .with_env("RABBITMQ_VHOST", "/") \
        .with_env("LOKI_ENDPOINT", loki_endpoint) \
        .with_env("IS_CONTAINER",None) \
        .with_env("ENABLE_LOKI_LOGGING", False) \
        .with_network(docker_network) \
        .with_exposed_ports(8000) as escheduler:
        try:
            # 等待容器日誌出現特定訊息，確保服務已準備就緒
            wait_for_logs(escheduler, "Uvicorn running on")
            host = escheduler.get_container_host_ip()
            port = escheduler.get_exposed_port(8000)
            base_url = f"http://{host}:{port}"
            print(f"EScheduler 服務已啟動於: {base_url}")
            yield base_url

        except Exception as e:
            print("="*80)
            print("EScheduler 容器啟動失敗：")
            print("="*80)
            print(escheduler.get_logs()[0].decode('utf-8'))
            print("="*80)
            raise e



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


@pytest_asyncio.fixture
async def test_sdk(escheduler_base_url: str) -> AsyncGenerator[ESchedulerSDK, None]:
    """測試用 SDK 實例"""
    sdk = ESchedulerSDK(
        base_url=escheduler_base_url,
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