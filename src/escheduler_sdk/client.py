"""EScheduler SDK 客戶端類"""

import asyncio
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .exceptions import (
    ESchedulerError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    TimeoutError,
    NetworkError
)


class ESchedulerClient:
    """EScheduler API 客戶端"""
    
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
        初始化 EScheduler 客戶端
        
        Args:
            base_url: EScheduler API 基礎 URL
            token: 團隊認證 token (4位字符)
            jwt_token: JWT 認證 token
            timeout: 請求超時時間（秒）
            max_retries: 最大重試次數
            **kwargs: 其他 httpx.AsyncClient 參數
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.jwt_token = jwt_token
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 設置預設 headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EScheduler-Python-SDK/0.1.0"
        }
        
        # 如果有 JWT token，添加到 headers
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        
        # 創建 HTTP 客戶端
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
            **kwargs
        )
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """關閉客戶端連接"""
        await self._client.aclose()
    
    def _build_url(self, endpoint: str) -> str:
        """構建完整的 API URL"""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))
    
    def _handle_response_error(self, response: httpx.Response) -> None:
        """處理 HTTP 回應錯誤"""
        status_code = response.status_code
        
        try:
            error_data = response.json()
            message = error_data.get("detail", error_data.get("message", "未知錯誤"))
        except Exception:
            message = response.text or f"HTTP {status_code} 錯誤"
        
        if status_code == 400:
            raise ValidationError(message, status_code=status_code, response_data=error_data)
        elif status_code == 401:
            raise AuthenticationError(message, status_code=status_code, response_data=error_data)
        elif status_code == 404:
            raise NotFoundError(message, status_code=status_code, response_data=error_data)
        elif status_code == 429:
            raise RateLimitError(message, status_code=status_code, response_data=error_data)
        elif 500 <= status_code < 600:
            raise ServerError(message, status_code=status_code, response_data=error_data)
        else:
            raise ESchedulerError(message, status_code=status_code, response_data=error_data)
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """發送 HTTP 請求"""
        url = self._build_url(endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    **kwargs
                )
                
                # 檢查回應狀態
                if response.is_success:
                    try:
                        return response.json()
                    except Exception:
                        # 如果回應不是 JSON，返回空字典
                        return {}
                else:
                    self._handle_response_error(response)
                    
            except httpx.TimeoutException:
                if attempt == self.max_retries:
                    raise TimeoutError(f"請求超時: {url}")
                await asyncio.sleep(2 ** attempt)  # 指數退避
                
            except httpx.NetworkError as e:
                if attempt == self.max_retries:
                    raise NetworkError(f"網路錯誤: {str(e)}")
                await asyncio.sleep(2 ** attempt)
                
            except (AuthenticationError, ValidationError, NotFoundError, RateLimitError, ServerError):
                # 這些錯誤不需要重試
                raise
                
            except Exception as e:
                if attempt == self.max_retries:
                    raise ESchedulerError(f"未知錯誤: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        # 這行理論上不會執行到
        raise ESchedulerError("請求失敗")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """發送 GET 請求"""
        return await self._request("GET", endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """發送 POST 請求"""
        return await self._request("POST", endpoint, json_data=json_data, **kwargs)
    
    async def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """發送 PUT 請求"""
        return await self._request("PUT", endpoint, json_data=json_data, **kwargs)
    
    async def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """發送 PATCH 請求"""
        return await self._request("PATCH", endpoint, json_data=json_data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """發送 DELETE 請求"""
        return await self._request("DELETE", endpoint, **kwargs)
    
    def set_jwt_token(self, jwt_token: str) -> None:
        """設置 JWT token"""
        self.jwt_token = jwt_token
        self._client.headers["Authorization"] = f"Bearer {jwt_token}"
    
    def clear_jwt_token(self) -> None:
        """清除 JWT token"""
        self.jwt_token = None
        if "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]