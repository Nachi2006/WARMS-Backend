from sqlalchemy import Column, Integer, String,Float, DateTime, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.sql import func
from src.db.db import Base
from src.auth.auth import UserRole

class User(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    location = Column(String)
    bookingtime = Column(DateTime)
    duration = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


