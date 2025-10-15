"""EScheduler SDK 排程任務 API 封裝"""

from typing import List, Optional, Union

from .client import ESchedulerClient
from .models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    SchedulerStatsResponse,
    TaskStateUpdateRequest,
    TaskState,
    MessageResponse,
    BaseTaskTemplate,
    EmailTemplateCreateTemplate,
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
)


class SchedulerAPI:
    """排程任務 API 封裝類"""
    
    def __init__(self, client: ESchedulerClient):
        """
        初始化排程任務 API
        
        Args:
            client: EScheduler 客戶端實例
        """
        self.client = client
        self.base_endpoint = "/api/scheduler"
        self.template_endpoint = "/api/email-templates"
    
    async def create_task(
        self, 
        task: Union[ScheduledTaskCreate, BaseTaskTemplate]
    ) -> ScheduledTaskResponse:
        """
        創建新的排程任務。
        
        可以接受一個完整的 `ScheduledTaskCreate` 模型，
        或者一個 `BaseTaskTemplate` 的子類實例來快速創建任務。
        
        Args:
            task: 任務創建數據模型或任務範本
            
        Returns:
            創建的任務信息
            
        Raises:
            ValidationError: 當任務數據驗證失敗時
            AuthenticationError: 當認證失敗時
            ESchedulerError: 其他 API 錯誤
        """
        if isinstance(task, BaseTaskTemplate):
            task_data = task.build()
        else:
            task_data = task

        response_data = await self.client.post(
            self.base_endpoint,
            json_data=task_data.model_dump(exclude_none=True)
        )
        return ScheduledTaskResponse(**response_data)

    async def create_email_template(
        self,
        template: Union[EmailTemplateCreate, EmailTemplateCreateTemplate]
    ) -> EmailTemplateResponse:
        """
        創建新的 Email 模板。

        可以接受一個完整的 `EmailTemplateCreate` 模型，
        或者一個 `EmailTemplateCreateTemplate` 的實例來快速創建模板。

        Args:
            template: 模板創建數據模型或模板範本

        Returns:
            創建的模板信息

        Raises:
            ValidationError: 當模板數據驗證失敗時
            AuthenticationError: 當認證失敗時
            ESchedulerError: 其他 API 錯誤
        """
        if isinstance(template, EmailTemplateCreateTemplate):
            template_data = template.build()
        else:
            template_data = template

        response_data = await self.client.post(
            self.template_endpoint,
            json_data=template_data.model_dump(exclude_none=True)
        )
        return EmailTemplateResponse(**response_data)

    async def update_email_template(
        self, 
        template_id: int, 
        template_data: EmailTemplateUpdate
    ) -> EmailTemplateResponse:
        """
        更新排程任務
        
        Args:
            task_id: 任務 ID
            task_data: 任務更新數據
            
        Returns:
            更新後的任務信息
            
        Raises:
            NotFoundError: 當任務不存在時
            ValidationError: 當更新數據驗證失敗時
        """
        response_data = await self.client.put(
            f"{self.template_endpoint}/{template_id}",
            json_data=template_data.model_dump(exclude_none=True)
        )
        return EmailTemplateResponse(**response_data)

    async def delete_email_template(self, template_id: int):
        """
        刪除 Email 模板。

        Args:
            template_id: 模板 ID

        Raises:
            NotFoundError: 當模板不存在時
        """
        await self.client.delete(f"{self.template_endpoint}/{template_id}")
    
    async def get_all_tasks(
        self, 
        state: Optional[TaskState] = None
    ) -> List[ScheduledTaskResponse]:
        """
        獲取所有排程任務
        
        Args:
            state: 可選的任務狀態過濾
            
        Returns:
            任務列表
        """
        params = {}
        if state:
            params["state"] = state.value
        
        response_data = await self.client.get(
            self.base_endpoint,
            params=params
        )
        return [ScheduledTaskResponse(**task) for task in response_data]
    
    async def get_task(self, task_id: int) -> ScheduledTaskResponse:
        """
        獲取單個排程任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            任務信息
            
        Raises:
            NotFoundError: 當任務不存在時
        """
        response_data = await self.client.get(f"{self.base_endpoint}/{task_id}")
        return ScheduledTaskResponse(**response_data)
    
    async def update_task(
        self, 
        task_id: int, 
        task_data: ScheduledTaskUpdate
    ) -> ScheduledTaskResponse:
        """
        更新排程任務
        
        Args:
            task_id: 任務 ID
            task_data: 任務更新數據
            
        Returns:
            更新後的任務信息
            
        Raises:
            NotFoundError: 當任務不存在時
            ValidationError: 當更新數據驗證失敗時
        """
        response_data = await self.client.put(
            f"{self.base_endpoint}/{task_id}",
            json_data=task_data.model_dump(exclude_none=True)
        )
        return ScheduledTaskResponse(**response_data)
    
    async def delete_task(self, task_id: int) -> MessageResponse:
        """
        刪除排程任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            刪除結果消息
            
        Raises:
            NotFoundError: 當任務不存在時
        """
        response_data = await self.client.delete(f"{self.base_endpoint}/{task_id}")
        return MessageResponse(**response_data)
    
    async def update_task_state(
        self, 
        task_id: int, 
        state_data: TaskStateUpdateRequest
    ) -> ScheduledTaskResponse:
        """
        更新任務狀態
        
        Args:
            task_id: 任務 ID
            state_data: 狀態更新數據
            
        Returns:
            更新後的任務信息
            
        Raises:
            NotFoundError: 當任務不存在時
            ValidationError: 當狀態數據驗證失敗時
        """
        response_data = await self.client.patch(
            f"{self.base_endpoint}/{task_id}/state",
            json_data=state_data.model_dump()
        )
        return ScheduledTaskResponse(**response_data)
    
    async def trigger_task(self, task_id: int) -> MessageResponse:
        """
        手動觸發任務執行
        
        Args:
            task_id: 任務 ID
            
        Returns:
            觸發結果消息
            
        Raises:
            NotFoundError: 當任務不存在時
        """
        response_data = await self.client.post(f"{self.base_endpoint}/{task_id}/trigger")
        return MessageResponse(**response_data)
    
    async def get_scheduler_stats(self) -> SchedulerStatsResponse:
        """
        獲取排程器統計信息
        
        Returns:
            排程器統計數據
        """
        response_data = await self.client.get(f"{self.base_endpoint}/stats")
        return SchedulerStatsResponse(**response_data)
    
    async def search_tasks(self, keyword: str) -> List[ScheduledTaskResponse]:
        """
        搜索排程任務
        
        Args:
            keyword: 搜索關鍵字
            
        Returns:
            匹配的任務列表
        """
        params = {"keyword": keyword}
        response_data = await self.client.get(
            f"{self.base_endpoint}/search",
            params=params
        )
        return [ScheduledTaskResponse(**task) for task in response_data]
    
    # 便利方法
    async def enable_task(self, task_id: int) -> ScheduledTaskResponse:
        """
        啟用任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            更新後的任務信息
        """
        state_data = TaskStateUpdateRequest(state=TaskState.ENABLED)
        return await self.update_task_state(task_id, state_data)
    
    async def disable_task(self, task_id: int) -> ScheduledTaskResponse:
        """
        禁用任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            更新後的任務信息
        """
        state_data = TaskStateUpdateRequest(state=TaskState.DISABLED)
        return await self.update_task_state(task_id, state_data)
    
    async def pause_task(self, task_id: int) -> ScheduledTaskResponse:
        """
        暫停任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            更新後的任務信息
        """
        state_data = TaskStateUpdateRequest(state=TaskState.PAUSED)
        return await self.update_task_state(task_id, state_data)