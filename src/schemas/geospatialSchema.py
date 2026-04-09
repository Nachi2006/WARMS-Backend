from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class HotspotCreate(BaseModel):
    species: str
    latitude: float
    longitude: float
    notes: Optional[str] = None

class HotspotResponse(BaseModel):
    id: int
    species: str
    latitude: float
    longitude: float
    notes: Optional[str] = None
    recorded_by: int
    recorded_at: datetime
    masked: bool

    class Config:
        from_attributes = True
