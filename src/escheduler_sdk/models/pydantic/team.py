"""團隊相關 Pydantic 模型"""
from typing import Optional
from pydantic import BaseModel, Field


class Team(BaseModel):
    """團隊模型"""
    id: int = Field(..., description="團隊 ID")
    name: str = Field(..., description="團隊名稱", examples=["第1小隊"])


class TeamAuthRequest(BaseModel):
    """團隊認證請求模型"""
    token: str = Field(..., min_length=4, max_length=4, description="團隊認證 token", examples=["ABCD"])


class TeamAuthResponse(BaseModel):
    """團隊認證回應模型"""
    status: bool = Field(..., description="認證狀態", examples=[False])
    team: Optional[Team] = Field(None, description="團隊信息")
    access_token: Optional[str] = Field(None, description="JWT 訪問 token")
