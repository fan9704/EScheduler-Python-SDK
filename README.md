# EScheduler Python SDK

一個用於與 EScheduler API 互動的 Python SDK，提供簡潔易用的介面來管理排程任務和團隊認證。

## 特性

- 🚀 **簡潔的 API**: 提供直觀易用的方法來操作排程任務
- 🔐 **完整的認證支持**: 支援團隊 token 和 JWT 認證
- 📝 **類型提示**: 完整的 TypeScript 風格類型提示
- 🛡️ **錯誤處理**: 詳細的異常類型和錯誤信息
- ⚡ **異步支持**: 基於 asyncio 的異步 API
- 🔄 **自動重試**: 內建請求重試機制
- 📊 **統計信息**: 支援獲取排程器統計數據

## 安裝

### 從源碼安裝

```bash
git clone https://github.com/escheduler/escheduler-python-sdk.git
cd escheduler-python-sdk
pip install -e .
```

### 開發環境安裝

```bash
uv sync # 安裝依賴
pip install -e ".[dev]"
uv run python -m build # 建立發行包
twine upload --repository escheduler_sdk dist/*
```

## 快速開始

### 基本使用

```python
import asyncio
from escheduler_sdk import ESchedulerSDK, ScheduledTaskCreate, TargetType

async def main():
    async with ESchedulerSDK(base_url="http://localhost:8000") as sdk:
        # 團隊認證
        await sdk.authenticate("ABCD")  # 你的團隊 token
        
        # 創建排程任務
        task_data = ScheduledTaskCreate(
            name="我的任務",
            description="每5分鐘執行一次的測試任務",
            schedule_expression="rate(5 minutes)",
            target_type=TargetType.HTTP,
            target_arn="https://httpbin.org/post",
            target_input={"message": "Hello World!"}
        )
        
        task = await sdk.scheduler.create_task(task_data)
        print(f"任務創建成功，ID: {task.id}")
        
        # 獲取所有任務
        tasks = await sdk.scheduler.get_all_tasks()
        print(f"共有 {len(tasks)} 個任務")

asyncio.run(main())
```

### 團隊認證

```python
import asyncio
from escheduler_sdk import ESchedulerSDK

async def auth_example():
    async with ESchedulerSDK(base_url="http://localhost:8000") as sdk:
        # 方法 1: 使用便利方法
        success = await sdk.authenticate("ABCD")
        if success:
            print("認證成功")
        
        # 方法 2: 獲取詳細認證信息
        auth_response = await sdk.team.auth_and_set_token("ABCD")
        if auth_response.status:
            print(f"團隊: {auth_response.team.name}")
            print(f"JWT Token: {auth_response.access_token}")

asyncio.run(auth_example())
```

## API 參考

### ESchedulerSDK

主要的 SDK 類，提供統一的 API 介面。

```python
sdk = ESchedulerSDK(
    base_url="http://localhost:8000",
    timeout=30.0,
    max_retries=3
)
```

#### 參數

- `base_url` (str): EScheduler API 的基礎 URL
- `token` (str, optional): 團隊認證 token
- `jwt_token` (str, optional): JWT 認證 token
- `timeout` (float): 請求超時時間，預設 30 秒
- `max_retries` (int): 最大重試次數，預設 3 次

#### 方法

- `authenticate(token: str) -> bool`: 使用團隊 token 進行認證
- `is_authenticated() -> bool`: 檢查是否已認證
- `logout()`: 登出並清除認證信息

### 排程任務 API (sdk.scheduler)

#### 任務管理

```python
# 創建任務
task = await sdk.scheduler.create_task(task_data)

# 獲取所有任務
tasks = await sdk.scheduler.get_all_tasks(state=TaskState.ENABLED)

# 獲取單個任務
task = await sdk.scheduler.get_task(task_id)

# 更新任務
task = await sdk.scheduler.update_task(task_id, update_data)

# 刪除任務
result = await sdk.scheduler.delete_task(task_id)
```

#### 任務狀態管理

```python
# 啟用任務
task = await sdk.scheduler.enable_task(task_id)

# 禁用任務
task = await sdk.scheduler.disable_task(task_id)

# 暫停任務
task = await sdk.scheduler.pause_task(task_id)

# 手動觸發任務
result = await sdk.scheduler.trigger_task(task_id)
```

#### 其他功能

```python
# 搜索任務
tasks = await sdk.scheduler.search_tasks("關鍵字")

# 獲取統計信息
stats = await sdk.scheduler.get_scheduler_stats()
```

### 團隊 API (sdk.team)

```python
# 獲取所有團隊
teams = await sdk.team.get_all_teams()

# 透過 token 獲取團隊
team = await sdk.team.get_team_by_token("ABCD")

# 團隊認證
auth_response = await sdk.team.auth_team("ABCD")

# 認證並自動設置 token
auth_response = await sdk.team.auth_and_set_token("ABCD")
```

## 數據模型

### 排程任務

```python
from escheduler_sdk import ScheduledTaskCreate, TargetType

task_data = ScheduledTaskCreate(
    name="任務名稱",
    description="任務描述",
    schedule_expression="rate(5 minutes)",  # 或 "cron(0 */5 * * * *)"
    timezone="Asia/Taipei",
    target_type=TargetType.HTTP,
    target_arn="https://example.com/webhook",
    target_input={"key": "value"},
    max_retry_attempts=3
)
```

### 排程表達式

支援兩種格式：

1. **Rate 表達式**: `rate(value unit)`
   - `rate(5 minutes)` - 每5分鐘
   - `rate(1 hour)` - 每小時
   - `rate(1 day)` - 每天

2. **Cron 表達式**: `cron(minute hour day month day-of-week year)`
   - `cron(0 12 * * ? *)` - 每天中午12點
   - `cron(0 */2 * * ? *)` - 每2小時
   - `cron(0 9 ? * MON-FRI *)` - 工作日上午9點

### 目標類型

```python
from escheduler_sdk import TargetType

# 支援的目標類型
TargetType.HTTP      # HTTP 請求
TargetType.WEBHOOK   # Webhook
TargetType.RABBITMQ  # RabbitMQ 消息
TargetType.EMAIL     # 電子郵件
```

### 任務狀態

```python
from escheduler_sdk import TaskState

TaskState.ENABLED   # 啟用
TaskState.DISABLED  # 禁用
TaskState.PAUSED    # 暫停
```

## 錯誤處理

SDK 提供了詳細的異常類型：

```python
from escheduler_sdk import (
    ESchedulerError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    TimeoutError,
    NetworkError
)

try:
    await sdk.scheduler.get_task(999)
except NotFoundError as e:
    print(f"任務不存在: {e}")
except AuthenticationError as e:
    print(f"認證失敗: {e}")
except ESchedulerError as e:
    print(f"API 錯誤: {e}")
    print(f"狀態碼: {e.status_code}")
    print(f"回應數據: {e.response_data}")
```

## 範例

查看 `examples/` 目錄中的完整範例：

- `basic_usage.py` - 基本使用範例
- `team_auth_example.py` - 團隊認證範例

## 開發

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 運行測試

```bash
pytest
```

### 代碼格式化

```bash
black src/
isort src/
```

### 類型檢查

```bash
mypy src/
```

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 更新日誌

### v0.1.0

- 初始版本
- 支援排程任務 CRUD 操作
- 支援團隊認證
- 完整的錯誤處理
- 異步 API 支援