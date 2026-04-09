from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from src.schemas.userSchema import UserRole

class RoleUpdateRequest(BaseModel):
    role: UserRole

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    is_locked: bool
    failed_login_count: int
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    ip_address: Optional[str]
    success: bool
    detail: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
