# EScheduler Python SDK 範例

本目錄包含了 EScheduler Python SDK 的各種使用範例，幫助您快速上手和了解 SDK 的功能。

## 範例列表

### 1. 基本使用範例 (`basic_usage.py`)

展示 EScheduler SDK 的基本功能，包括：
- 初始化 SDK 客戶端
- 創建排程任務
- 獲取任務列表和詳情
- 更新任務配置
- 搜索任務
- 任務狀態管理（暫停/啟用）
- 手動觸發任務
- 獲取排程器統計信息
- 刪除任務

**適用場景**：初學者入門，了解基本 API 操作

### 2. HTTP 任務範例 (`http_task_example.py`)

專門展示如何創建各種 HTTP 類型的排程任務：
- 每日數據備份任務
- 系統健康檢查任務
- 週報生成任務
- 數據同步任務

**適用場景**：需要創建 HTTP 請求類型的排程任務

### 3. 任務管理範例 (`task_management_example.py`)

展示如何管理現有的排程任務：
- 批量獲取任務
- 任務詳情查看
- 任務配置更新
- 任務狀態切換
- 任務執行歷史查詢
- 任務搜索和過濾

**適用場景**：需要對現有任務進行管理和維護

### 4. Cron 表達式範例 (`cron_examples.py`)

展示各種 Cron 表達式的使用方法：
- 基本時間間隔（每分鐘、每小時、每天等）
- 特定時間點執行
- 複雜的時間規則
- 月末、季度末、年末執行

**適用場景**：需要設置複雜時間規則的排程任務

### 5. 錯誤處理範例 (`error_handling_example.py`)

展示如何處理各種錯誤情況：
- 驗證錯誤處理
- 認證錯誤處理
- 網路錯誤處理
- 重試機制
- 批量操作錯誤處理
- 自定義錯誤處理函數

**適用場景**：生產環境部署，需要健壯的錯誤處理機制

### 6. 進階功能範例 (`advanced_features_example.py`)

展示 SDK 的進階功能：
- 任務執行歷史分析
- 調度器統計信息
- 任務健康檢查
- 批量任務管理
- 任務性能分析
- 監控和告警

**適用場景**：需要深入監控和分析排程系統的運行狀況

## 使用前準備

### 1. 安裝依賴

```bash
# 使用 uv（推薦）
uv add escheduler-sdk

# 或使用 pip
pip install escheduler-sdk
```

### 2. 配置認證

在運行範例之前，請確保：

1. **設置正確的 API URL**：將範例中的 `http://localhost:8000` 替換為您的 EScheduler 服務地址

2. **設置 JWT Token**：將範例中的 `"your-jwt-token-here"` 替換為您的有效 JWT token

```python
async with ESchedulerSDK(
    base_url="https://your-escheduler-api.com",  # 您的 API 地址
    jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # 您的 JWT token
    timeout=30.0
) as sdk:
    # 您的代碼
```

### 3. 運行範例

```bash
# 運行基本使用範例
python examples/basic_usage.py

# 運行 HTTP 任務範例
python examples/http_task_example.py

# 運行其他範例
python examples/task_management_example.py
python examples/cron_examples.py
python examples/error_handling_example.py
python examples/advanced_features_example.py
```

## 範例特點

### 🚀 無需團隊認證

所有範例都已移除團隊認證步驟，直接使用 JWT token 進行認證，簡化了使用流程。

### 📝 詳細註釋

每個範例都包含詳細的中文註釋，解釋每個步驟的作用和參數含義。

### 🛡️ 錯誤處理

範例中包含完整的錯誤處理邏輯，展示如何優雅地處理各種異常情況。

### 🎯 實際場景

範例基於真實的業務場景設計，可以直接應用到實際項目中。

### 🔧 可配置參數

範例中的參數都可以根據實際需求進行調整，如超時時間、重試次數等。

## 最佳實踐

### 1. 異步上下文管理

始終使用 `async with` 語句來管理 SDK 客戶端：

```python
async with ESchedulerSDK(...) as sdk:
    # 您的操作
    pass
# 客戶端會自動關閉
```

### 2. 錯誤處理

為每個 API 調用添加適當的錯誤處理：

```python
try:
    result = await sdk.scheduler.create_task(task_data)
except ValidationError as e:
    print(f"驗證錯誤: {e}")
except AuthenticationError as e:
    print(f"認證錯誤: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")
```

### 3. 資源清理

在測試或演示完成後，記得清理創建的資源：

```python
# 刪除測試任務
for task in created_tasks:
    await sdk.scheduler.delete_task(task.id)
```

### 4. 配置管理

在生產環境中，建議使用環境變量或配置文件管理敏感信息：

```python
import os

async with ESchedulerSDK(
    base_url=os.getenv("ESCHEDULER_API_URL"),
    jwt_token=os.getenv("ESCHEDULER_JWT_TOKEN"),
    timeout=30.0
) as sdk:
    # 您的代碼
```

## 常見問題

### Q: 如何獲取 JWT Token？

A: JWT Token 通常通過您的認證系統獲取。請聯繫您的系統管理員或查看 EScheduler 的認證文檔。

### Q: 任務創建失敗怎麼辦？

A: 檢查以下幾點：
1. JWT Token 是否有效
2. Cron 表達式是否正確
3. 目標 URL 是否可訪問
4. 請求參數是否符合 API 規範

### Q: 如何調試 API 調用？

A: 可以啟用 SDK 的調試模式：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q: 支援哪些時區？

A: 支援所有標準的 IANA 時區，如 `Asia/Taipei`、`UTC`、`America/New_York` 等。

## 技術支援

如果您在使用過程中遇到問題，請：

1. 查看範例代碼中的錯誤處理部分
2. 檢查 API 文檔
3. 聯繫技術支援團隊

## 貢獻

歡迎提交新的範例或改進現有範例！請確保：

1. 代碼風格一致
2. 包含詳細註釋
3. 添加適當的錯誤處理
4. 更新此 README 文件