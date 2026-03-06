from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.db import getDb
from src.models.bookingModel import Booking
from src.schemas.bookingSchema import BookingCreate, BookingResponse,BookingBase
from src.models.userModel import User
from src.controllers.authController import get_current_user
router = APIRouter(prefix="/user", tags=["users"])

@router.post("/booking", response_model=BookingResponse)
def create_booking(
    booking_in: BookingBase, 
    db: Session = Depends(getDb),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != booking_in.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create bookings for your own account."
        )
    if(current_user.role!='USER'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create bookings being a USER. It is not Allowed for ADMIN or RANGER"
        )

    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.start_time == booking_in.start_time,
        Booking.status != "cancelled"
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a booking at this time."
        )

    occupancy = db.query(func.count(Booking.id)).filter(
        Booking.location == booking_in.location,
        Booking.start_time == booking_in.start_time,
        Booking.status != "cancelled"
    ).scalar()

    if occupancy >= 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This slot is full. Maximum 30 bookings allowed."
        )

    new_booking = Booking(
        user_id=current_user.id,
        location=booking_in.location,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        status="pending"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking