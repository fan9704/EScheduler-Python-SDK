from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, EmailStr

class TemplateVariable(BaseModel):
    """模板變數定義"""
    name: str = Field(..., description="變數名稱")
    type: str = Field("string", description="變數類型: string, number, email, date, boolean")
    description: Optional[str] = Field(None, description="變數描述")
    required: bool = Field(False, description="是否必填")
    default_value: Optional[Any] = Field(None, description="預設值")
    validation_pattern: Optional[str] = Field(None, description="驗證正則表達式")
    
    @field_validator('type')
    def validate_type(cls, v):
        allowed_types = ['string', 'number', 'email', 'date', 'boolean']
        if v not in allowed_types:
            raise ValueError(f'變數類型必須是: {", ".join(allowed_types)}')
        return v

class EmailTemplateCreate(BaseModel):
    """創建 Email 模板請求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="模板名稱")
    description: Optional[str] = Field(None, description="模板描述")
    subject_template: str = Field(..., min_length=1, max_length=500, description="主旨模板")
    body_template: str = Field(..., min_length=1, description="內容模板")
    html_template: Optional[str] = Field(None, description="HTML 模板")
    variables: List[TemplateVariable] = Field(default=[], description="模板變數定義")
    default_sender: Optional[EmailStr] = Field(None, description="預設寄件人")
    default_cc: Optional[List[EmailStr]] = Field(None, description="預設副本收件人")
    default_bcc: Optional[List[EmailStr]] = Field(None, description="預設密件副本收件人")
    is_active: bool = Field(True, description="是否啟用")


class EmailTemplateUpdate(BaseModel):
    """更新 Email 模板請求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject_template: Optional[str] = Field(None, min_length=1, max_length=500)
    body_template: Optional[str] = Field(None, min_length=1)
    html_template: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    default_sender: Optional[EmailStr] = None
    default_cc: Optional[List[EmailStr]] = None
    default_bcc: Optional[List[EmailStr]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    """Email 模板回應模型"""
    id: int
    name: str
    description: Optional[str]
    subject_template: str
    body_template: str
    html_template: Optional[str]
    variables: List[Dict[str, Any]]
    default_sender: Optional[str]
    default_cc: Optional[List[str]]
    default_bcc: Optional[List[str]]
    is_active: bool
    is_system_template: bool
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



class EmailTaskCreate(BaseModel):
    """創建 Email 任務請求模型"""
    # 基本任務資訊
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    schedule_expression: str = Field(..., description="排程表達式")
    timezone: str = Field("Asia/Taipei", description="時區")
    
    # Email 特定設定
    use_template: bool = Field(False, description="是否使用模板")
    template_id: Optional[int] = Field(None, description="模板 ID")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="模板變數值")
    
    # 直接 Email 設定 (不使用模板時)
    subject: Optional[str] = Field(None, description="郵件主旨")
    body: Optional[str] = Field(None, description="郵件內容")
    html_body: Optional[str] = Field(None, description="HTML 內容")
    
    # 收件人設定
    recipients: List[EmailStr] = Field(..., min_items=1, description="收件人列表")
    cc: Optional[List[EmailStr]] = Field(None, description="副本收件人")
    bcc: Optional[List[EmailStr]] = Field(None, description="密件副本收件人")
    sender: Optional[EmailStr] = Field(None, description="寄件人")
    
    # 任務設定
    max_retry_attempts: int = Field(3, ge=0, le=10, description="最大重試次數")
    retry_policy: Optional[Dict[str, Any]] = Field(None, description="重試策略")
    
    @field_validator('template_id')
    def validate_template_usage(cls, v, values):
        use_template = values.get('use_template', False)
        if use_template and not v:
            raise ValueError('使用模板時必須提供 template_id')
        return v
    
    @field_validator('subject')
    def validate_direct_email_fields(cls, v, values):
        use_template = values.get('use_template', False)
        if not use_template and not v:
            raise ValueError('不使用模板時必須提供 subject')
        return v


class EmailTaskUpdate(BaseModel):
    """更新 Email 任務請求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_expression: Optional[str] = None
    timezone: Optional[str] = None
    use_template: Optional[bool] = None
    template_id: Optional[int] = None
    template_variables: Optional[Dict[str, Any]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    html_body: Optional[str] = None
    recipients: Optional[List[EmailStr]] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    sender: Optional[EmailStr] = None
    max_retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    retry_policy: Optional[Dict[str, Any]] = None


class EmailTaskResponse(BaseModel):
    """Email 任務回應模型"""
    id: int
    name: str
    description: Optional[str]
    schedule_expression: str
    timezone: str
    target_type: str
    target_arn: str
    target_input: Dict[str, Any]
    state: str
    last_execution_time: Optional[datetime]
    next_execution_time: Optional[datetime]
    execution_count: int
    max_retry_attempts: int
    created_at: datetime
    updated_at: datetime
    
    # Email 特定資訊
    use_template: bool
    template_id: Optional[int]
    template_name: Optional[str]
    recipients: List[str]
    
    class Config:
        from_attributes = True


class EmailSendRequest(BaseModel):
    """立即發送 Email 請求模型"""
    use_template: bool = Field(False, description="是否使用模板")
    template_id: Optional[int] = Field(None, description="模板 ID")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="模板變數值")
    
    # 直接 Email 設定
    subject: Optional[str] = Field(None, description="郵件主旨")
    body: Optional[str] = Field(None, description="郵件內容")
    html_body: Optional[str] = Field(None, description="HTML 內容")
    
    # 收件人設定
    recipients: List[EmailStr] = Field(..., min_items=1, description="收件人列表")
    cc: Optional[List[EmailStr]] = Field(None, description="副本收件人")
    bcc: Optional[List[EmailStr]] = Field(None, description="密件副本收件人")
    sender: Optional[EmailStr] = Field(None, description="寄件人")


class EmailSendResponse(BaseModel):
    """Email 發送回應模型"""
    success: bool = Field(..., description="是否發送成功")
    message: str = Field(..., description="發送結果訊息")
    usage_id: Optional[int] = Field(None, description="使用記錄 ID")
    execution_time: float = Field(..., description="執行時間 (秒)")
    data: Optional[Dict[str, Any]] = Field(None, description="額外資料")