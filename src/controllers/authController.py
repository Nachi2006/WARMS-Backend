import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from src.db.db import getDb
from src.models.userModel import User
from src.models.auditLogModel import AuditLog
from src.schemas.userSchema import UserCreate, UserResponse, Token, UserLogin
from src.auth.auth import (
    get_password_hash,
    verify_password,
    needs_rehash,
    create_access_token,
    get_current_user_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

MAX_FAILED_ATTEMPTS = 5

def _log_audit(db: Session, user_id, action: str, ip: str, success: bool, detail: str = None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip,
        success=success,
        detail=detail,
    )
    db.add(log)
    db.commit()

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_current_user(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(getDb),
) -> User:
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
    if user.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked")
    return user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, request: Request, db: Session = Depends(getDb)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        role=user_in.role.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _log_audit(db, new_user.id, "signup", _get_client_ip(request), True)
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, request: Request, db: Session = Depends(getDb)):
    ip = _get_client_ip(request)
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        _log_audit(db, None, "login", ip, False, f"No account for {login_data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if user.is_locked:
        _log_audit(db, user.id, "login", ip, False, "Account locked")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked due to too many failed attempts")

    if not verify_password(login_data.password, user.hashed_password):
        user.failed_login_count = (user.failed_login_count or 0) + 1
        if user.failed_login_count >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            _log_audit(db, user.id, "login", ip, False, f"Account locked after {MAX_FAILED_ATTEMPTS} failures")
        else:
            _log_audit(db, user.id, "login", ip, False, f"Wrong password (attempt {user.failed_login_count})")
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if needs_rehash(user.hashed_password):
        user.hashed_password = get_password_hash(login_data.password)

    user.failed_login_count = 0
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    _log_audit(db, user.id, "login", ip, True)

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user