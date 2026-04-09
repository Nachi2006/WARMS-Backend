from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementCreate(BaseModel):
    title: str
    body: str

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    body: str
    created_by: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
