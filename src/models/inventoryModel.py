from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from src.db.db import Base
from src.schemas.inventorySchema import ItemCategory, ItemStatus

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.available)
    location = Column(String, nullable=True)
    last_maintained = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
