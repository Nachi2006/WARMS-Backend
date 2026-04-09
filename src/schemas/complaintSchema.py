from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ComplaintStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class ComplaintCreate(BaseModel):
    description: str
    latitude: float
    longitude: float

class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus

class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    description: str
    latitude: float
    longitude: float
    status: ComplaintStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
