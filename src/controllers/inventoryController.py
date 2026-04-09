from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.db import getDb
from src.models.inventoryModel import InventoryItem
from src.schemas.inventorySchema import InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse
from src.auth.auth import require_roles

router = APIRouter(prefix="/inventory", tags=["Inventory"])

_admin_only = require_roles("admin")
_admin_or_ranger = require_roles("admin", "ranger")

@router.get("", response_model=List[InventoryItemResponse])
def list_inventory(
    token_data: dict = Depends(_admin_or_ranger),
    db: Session = Depends(getDb),
):
    return db.query(InventoryItem).order_by(InventoryItem.created_at.desc()).all()

@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    body: InventoryItemCreate,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    item = InventoryItem(
        name=body.name,
        category=body.category,
        quantity=body.quantity,
        status=body.status,
        location=body.location,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_item(
    item_id: int,
    body: InventoryItemUpdate,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(item)
    db.commit()
