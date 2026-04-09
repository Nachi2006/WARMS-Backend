from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.db import getDb
from src.models.announcementModel import Announcement
from src.schemas.announcementSchema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from src.auth.auth import require_roles, get_current_user_token
from src.models.userModel import User

router = APIRouter(prefix="/announcements", tags=["Announcements"])

_admin_only = require_roles("admin")

@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    body: AnnouncementCreate,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()
    announcement = Announcement(
        title=body.title,
        body=body.body,
        created_by=user.id,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.get("", response_model=List[AnnouncementResponse])
def list_announcements(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(getDb),
):
    return (
        db.query(Announcement)
        .filter(Announcement.is_active == True)
        .order_by(Announcement.created_at.desc())
        .all()
    )

@router.patch("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    body: AnnouncementUpdate,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(announcement, field, value)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_announcement(
    announcement_id: int,
    token_data: dict = Depends(_admin_only),
    db: Session = Depends(getDb),
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    announcement.is_active = False
    db.commit()
