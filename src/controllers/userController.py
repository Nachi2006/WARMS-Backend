from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..utils.logger import logger
from src.db.db import getDb
from src.models.userModel import User  # Ensure you have a User model defined
from src.schemas.userSchema import UserCreate, UserResponse, Token, UserLogin
from src.auth.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    UserRole
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(getDb)):
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and save
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        role=user_in.role.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("User added",new_user.username)
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(getDb)):
    # 1. Search by email directly from the JSON body
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 2. Generate token with RBAC role
    access_token = create_access_token(
        data={"sub": user.email}, 
        role=user.role
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role
    }
    # Find user by email (username field in OAuth2 form)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token with RBAC role
    access_token = create_access_token(
        data={"sub": user.email}, 
        role=user.role
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role
    }