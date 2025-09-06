"""EScheduler SDK 異常類定義"""

from typing import Optional, Any, Dict


class ESchedulerError(Exception):
    """EScheduler SDK 基礎異常類"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ESchedulerError):
    """認證錯誤異常"""
    
    def __init__(self, message: str = "認證失敗", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(ESchedulerError):
    """驗證錯誤異常"""
    
    def __init__(self, message: str = "請求參數驗證失敗", **kwargs):
        super().__init__(message, **kwargs)


class NotFoundError(ESchedulerError):
    """資源不存在異常"""
    
    def __init__(self, message: str = "請求的資源不存在", **kwargs):
        super().__init__(message, **kwargs)


class ServerError(ESchedulerError):
    """伺服器錯誤異常"""
    
    def __init__(self, message: str = "伺服器內部錯誤", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitError(ESchedulerError):
    """請求頻率限制異常"""
    
    def __init__(self, message: str = "請求頻率超過限制", **kwargs):
        super().__init__(message, **kwargs)


class TimeoutError(ESchedulerError):
    """請求超時異常"""
    
    def __init__(self, message: str = "請求超時", **kwargs):
        super().__init__(message, **kwargs)


class NetworkError(ESchedulerError):
    """網路錯誤異常"""
    
    def __init__(self, message: str = "網路連接錯誤", **kwargs):
        super().__init__(message, **kwargs)