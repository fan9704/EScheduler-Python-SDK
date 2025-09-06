"""EScheduler SDK 團隊認證 API 封裝"""

from typing import List, Optional

from .client import ESchedulerClient
from .models import (
    Team,
    TeamAuthRequest,
    TeamAuthResponse
)


class TeamAPI:
    """團隊認證 API 封裝類"""
    
    def __init__(self, client: ESchedulerClient):
        """
        初始化團隊 API
        
        Args:
            client: EScheduler 客戶端實例
        """
        self.client = client
        self.base_endpoint = "/api/team"
    
    async def get_all_teams(self) -> List[Team]:
        """
        取得所有團隊
        
        Returns:
            團隊列表
            
        Raises:
            AuthenticationError: 當認證失敗時
            ESchedulerError: 其他 API 錯誤
        """
        response_data = await self.client.get(self.base_endpoint)
        return [Team(**team) for team in response_data]
    
    async def get_team_by_token(self, token: str) -> Optional[Team]:
        """
        透過 Token 認證團隊
        
        Args:
            token: 團隊認證 token (4位字符)
            
        Returns:
            團隊信息，如果 token 無效則返回 None
            
        Raises:
            ValidationError: 當 token 格式不正確時
            ESchedulerError: 其他 API 錯誤
        """
        response_data = await self.client.get(f"{self.base_endpoint}/{token}/")
        if response_data:
            return Team(**response_data)
        return None
    
    async def auth_team(self, token: str) -> TeamAuthResponse:
        """
        團隊認證並取得 JWT Token
        
        Args:
            token: 團隊認證 token (4位字符)
            
        Returns:
            認證結果，包含團隊信息和 JWT token
            
        Raises:
            AuthenticationError: 當認證失敗時
            ValidationError: 當 token 格式不正確時
            ESchedulerError: 其他 API 錯誤
        """
        auth_request = TeamAuthRequest(token=token)
        response_data = await self.client.post(
            f"{self.base_endpoint}/auth/token/",
            json_data=auth_request.model_dump()
        )
        return TeamAuthResponse(**response_data)
    
    async def auth_and_set_token(self, token: str) -> TeamAuthResponse:
        """
        團隊認證並自動設置 JWT Token 到客戶端
        
        這是一個便利方法，會自動將獲得的 JWT token 設置到客戶端中，
        後續的 API 請求將自動使用此 token 進行認證。
        
        Args:
            token: 團隊認證 token (4位字符)
            
        Returns:
            認證結果，包含團隊信息和 JWT token
            
        Raises:
            AuthenticationError: 當認證失敗時
            ValidationError: 當 token 格式不正確時
            ESchedulerError: 其他 API 錯誤
        """
        auth_response = await self.auth_team(token)
        
        # 如果認證成功且有 JWT token，自動設置到客戶端
        if auth_response.status and auth_response.access_token:
            self.client.set_jwt_token(auth_response.access_token)
        
        return auth_response
    
    def logout(self) -> None:
        """
        登出，清除客戶端中的 JWT token
        """
        self.client.clear_jwt_token()