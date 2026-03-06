from pydantic import BaseModel, EmailStr, Field
from enum import Enum
class UserRole(str, Enum):
    ADMIN = "admin"
    RANGER = "ranger"
    USER = "user"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    role: UserRole = UserRole.USER

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
class UserLogin(BaseModel):
    email: EmailStr
    password: str