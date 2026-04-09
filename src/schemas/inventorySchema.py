from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ItemCategory(str, Enum):
    vehicle = "vehicle"
    radio = "radio"
    trap = "trap"
    other = "other"

class ItemStatus(str, Enum):
    available = "available"
    in_use = "in_use"
    maintenance = "maintenance"
    decommissioned = "decommissioned"

class InventoryItemCreate(BaseModel):
    name: str
    category: ItemCategory
    quantity: int
    status: ItemStatus = ItemStatus.available
    location: Optional[str] = None

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    quantity: Optional[int] = None
    status: Optional[ItemStatus] = None
    location: Optional[str] = None
    last_maintained: Optional[datetime] = None

class InventoryItemResponse(BaseModel):
    id: int
    name: str
    category: ItemCategory
    quantity: int
    status: ItemStatus
    location: Optional[str]
    last_maintained: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
