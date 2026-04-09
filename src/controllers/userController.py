import hmac
import hashlib
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.db import getDb
from src.models.bookingModel import Booking
from src.schemas.bookingSchema import BookingCreate, BookingResponse, BookingBase
from src.models.userModel import User
from src.controllers.authController import get_current_user

router = APIRouter(prefix="/user", tags=["Visitor"])

_SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

def _generate_qr_data(booking_id: int, user_id: int, start_time: str) -> str:
    raw = f"{booking_id}:{user_id}:{start_time}"
    signature = hmac.new(
        _SECRET_KEY.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{raw}:{signature}"

@router.post("/booking", response_model=BookingResponse)
def create_booking(
    booking_in: BookingBase,
    db: Session = Depends(getDb),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != booking_in.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create bookings for your own account.",
        )
    if current_user.role.value != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only visitors (USER role) can create bookings.",
        )

    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.start_time == booking_in.start_time,
        Booking.status != "cancelled",
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a booking at this time.",
        )

    occupancy = db.query(func.count(Booking.id)).filter(
        Booking.location == booking_in.location,
        Booking.start_time == booking_in.start_time,
        Booking.status != "cancelled",
    ).scalar()

    if occupancy >= 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This slot is full. Maximum 30 bookings allowed.",
        )

    new_booking = Booking(
        user_id=current_user.id,
        location=booking_in.location,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        status="pending",
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    qr = _generate_qr_data(new_booking.id, current_user.id, str(new_booking.start_time))
    new_booking.qr_code_data = qr
    db.commit()
    db.refresh(new_booking)

    return new_booking

@router.get("/bookings", response_model=list[BookingResponse])
def my_bookings(
    db: Session = Depends(getDb),
    current_user: User = Depends(get_current_user),
):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()

@router.delete("/booking/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(getDb),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id,
    ).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()