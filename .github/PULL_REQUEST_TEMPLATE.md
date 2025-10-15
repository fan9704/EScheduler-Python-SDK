# **這支 PR 所做的事情**

盡可能詳細取代本文字。 Replace this text and describe This PR doing(Better to be detail)

- feat: 新功能 New feature
- fix: 修復 Bug Bug fix
- docs: 文件更新 Documentation update
- style: 程式碼格式調整 Code format
- refactor: 重構程式碼 Code refactor
- test: 新增測試或修改測試 Test update
- chore: 其他不修改 src 或 test 的內容 Other change
- revert: 回復先前的 commit Revert to previous commit

## 所屬 Issue

- Related Issues 相關的 Issues : Paste Issue Link 貼上 Issue 連結

---

## SDK 相關資訊

- SDK 方法: create_task()
- 對應 API 路由使用的通訊協定: http://127.0.0.1:8000/api/xx
- Simple Test Method 提供簡單的測試方法:

### 使用範例

```python
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
```

### 範例 Response

```json
{
    "example":"value"
}
```

---

## 變更的類型 Change Type

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## 影響的 SDK Affect SDK

- [ ] Schedule(HTTP/Webhook/RabbitMQ/Email)
- [ ] Email Template
- [ ] 不影響 SDK No affect SDK
- [ ] 其他（請填寫） Other(Please enter it)


## 檢查清單 Check List

- [ ] 我已經在本地手動測試過，確保功能的完整性和穩定性 I have done fully correct manual test
- [ ] 我對我的程式碼進行了註解，特別是在難以理解的地方 I have added comment in my code
- [ ] 我已經更新了文件，或者我的更改不需要更新文件 I have commented in document
- [ ] 我的 PR 有明確的標題與內容描述 My PR has right title and description

## 相關的資源或參考文件連結 Related Resource/Document Link

If this PR related some resource/document please offer link
