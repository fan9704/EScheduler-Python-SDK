"""EScheduler SDK 主要類"""

from typing import Optional

from .client import ESchedulerClient
from .scheduler import SchedulerAPI
from .team import TeamAPI


class ESchedulerSDK:
    """EScheduler SDK 主要類
    
    這個類提供了一個統一的介面來訪問所有 EScheduler API 功能。
    """
    
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        jwt_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        初始化 EScheduler SDK
        
        Args:
            base_url: EScheduler API 基礎 URL
            token: 團隊認證 token (4位字符)
            jwt_token: JWT 認證 token
            timeout: 請求超時時間（秒）
            max_retries: 最大重試次數
            **kwargs: 其他 httpx.AsyncClient 參數
        """
        # 創建客戶端
        self.client = ESchedulerClient(
            base_url=base_url,
            token=token,
            jwt_token=jwt_token,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        
        # 初始化 API 模組
        self.scheduler = SchedulerAPI(self.client)
        self.team = TeamAPI(self.client)
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """關閉 SDK 連接"""
        await self.client.close()
    
    async def authenticate(self, token: str) -> bool:
        """
        使用團隊 token 進行認證
        
        這是一個便利方法，會自動進行團隊認證並設置 JWT token。
        
        Args:
            token: 團隊認證 token (4位字符)
            
        Returns:
            認證是否成功
            
        Raises:
            AuthenticationError: 當認證失敗時
            ValidationError: 當 token 格式不正確時
            ESchedulerError: 其他 API 錯誤
        """
        try:
            auth_response = await self.team.auth_and_set_token(token)
            return auth_response.status
        except Exception:
            return False
    
    def is_authenticated(self) -> bool:
        """
        檢查是否已認證
        
        Returns:
            是否已設置 JWT token
        """
        return self.client.jwt_token is not None
    
    def logout(self) -> None:
        """
        登出，清除認證信息
        """
        self.team.logout()