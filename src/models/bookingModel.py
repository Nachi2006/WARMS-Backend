from sqlalchemy import Column, Integer, String,Float, DateTime, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.sql import func
from src.db.db import Base
from src.schemas.bookingSchema import BookingStatus
from sqlalchemy.orm import relationship

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(BookingStatus), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="bookings")

