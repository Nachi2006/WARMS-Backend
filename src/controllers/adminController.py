from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.db import getDb
from src.models.userModel import User
from src.models.auditLogModel import AuditLog
from src.schemas.adminSchema import AdminUserResponse, AuditLogResponse, RoleUpdateRequest
from src.schemas.userSchema import UserRole
from src.auth.auth import require_roles
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

_admin_only = require_roles("admin")

@router.get("/users", response_model=List[AdminUserResponse])
def list_users(
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    return db.query(User).all()

@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
def update_user_role(
    user_id: int,
    body: RoleUpdateRequest,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{user_id}/unlock", response_model=AdminUserResponse)
def unlock_user(
    user_id: int,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_locked = False
    user.failed_login_count = 0
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{user_id}/deactivate", response_model=AdminUserResponse)
def deactivate_user(
    user_id: int,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
