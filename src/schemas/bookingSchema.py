from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class BookingBase(BaseModel):
    user_id:int
    location: str
    start_time: datetime
    end_time: datetime
    status: Optional[BookingStatus] = BookingStatus.pending

class BookingCreate(BookingBase):
    user_id: int

class BookingResponse(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None