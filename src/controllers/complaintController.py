from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.db import getDb
from src.models.complaintModel import Complaint
from src.schemas.complaintSchema import ComplaintCreate, ComplaintResponse, ComplaintStatusUpdate
from src.auth.auth import require_roles, get_current_user_token
from src.models.userModel import User

router = APIRouter(prefix="/complaints", tags=["Complaints"])

_visitor_only = require_roles("user")
_admin_only = require_roles("admin")

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(
    body: ComplaintCreate,
    token_data: dict = Depends(_visitor_only),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()
    complaint = Complaint(
        user_id=user.id,
        description=body.description,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("/my", response_model=List[ComplaintResponse])
def my_complaints(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()
    return (
        db.query(Complaint)
        .filter(Complaint.user_id == user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )

@router.get("", response_model=List[ComplaintResponse])
def list_all_complaints(
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()

@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    body: ComplaintStatusUpdate,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    complaint.status = body.status
    db.commit()
    db.refresh(complaint)
    return complaint
