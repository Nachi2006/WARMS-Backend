import os
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from src.db.db import getDb
from src.models.rangerModels import SightingLog, PatrolRoute, Incident, SosAlert
from src.models.userModel import User
from src.schemas.rangerSchema import (
    SyncPayload, SyncResult,
    IncidentType, IncidentStatus, IncidentResponse,
    SosPayload, SosResponse,
)
from src.auth.auth import require_roles, get_current_user_token
from src.services.websocketManager import manager

router = APIRouter(prefix="/ranger", tags=["Ranger Operations"])

_ranger_or_admin = require_roles("ranger", "admin")

UPLOAD_DIR = "uploads/incidents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/sync-logs", response_model=SyncResult)
def sync_logs(
    payload: SyncPayload,
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()
    sightings_synced = 0
    routes_synced = 0
    conflicts_resolved = 0

    for entry in payload.sightings:
        existing = None
        if entry.local_id:
            existing = (
                db.query(SightingLog)
                .filter(SightingLog.local_id == entry.local_id, SightingLog.ranger_id == user.id)
                .first()
            )

        if existing:
            if entry.observed_at > existing.observed_at:
                existing.species = entry.species
                existing.latitude = entry.latitude
                existing.longitude = entry.longitude
                existing.observed_at = entry.observed_at
                existing.synced_at = datetime.now(timezone.utc)
                conflicts_resolved += 1
        else:
            new_log = SightingLog(
                ranger_id=user.id,
                local_id=entry.local_id,
                species=entry.species,
                latitude=entry.latitude,
                longitude=entry.longitude,
                observed_at=entry.observed_at,
            )
            db.add(new_log)
            sightings_synced += 1

    for route in payload.patrol_routes:
        existing = None
        if route.local_id:
            existing = (
                db.query(PatrolRoute)
                .filter(PatrolRoute.local_id == route.local_id, PatrolRoute.ranger_id == user.id)
                .first()
            )

        if existing:
            if route.patrol_date > existing.patrol_date:
                existing.coordinates = route.coordinates
                existing.patrol_date = route.patrol_date
                existing.synced_at = datetime.now(timezone.utc)
                conflicts_resolved += 1
        else:
            new_route = PatrolRoute(
                ranger_id=user.id,
                local_id=route.local_id,
                coordinates=route.coordinates,
                patrol_date=route.patrol_date,
            )
            db.add(new_route)
            routes_synced += 1

    db.commit()
    return SyncResult(
        sightings_synced=sightings_synced,
        routes_synced=routes_synced,
        conflicts_resolved=conflicts_resolved,
    )

@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    type: IncidentType = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    photo: UploadFile = File(...),
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Photo must be a valid image (JPEG, PNG, WEBP)",
        )

    contents = await photo.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Attached photo is empty",
        )

    user = db.query(User).filter(User.email == token_data["email"]).first()
    timestamp_now = datetime.now(timezone.utc)

    safe_name = f"{user.id}_{int(timestamp_now.timestamp())}_{photo.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    incident = Incident(
        reporter_id=user.id,
        type=type,
        latitude=latitude,
        longitude=longitude,
        gps_timestamp=timestamp_now,
        photo_path=file_path,
        status=IncidentStatus.open,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.post("/sos", response_model=SosResponse, status_code=status.HTTP_201_CREATED)
async def send_sos(
    payload: SosPayload,
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    user = db.query(User).filter(User.email == token_data["email"]).first()

    alert = SosAlert(
        sender_id=user.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    broadcast_payload = {
        "event": "SOS_ALERT",
        "alert_id": alert.id,
        "sender_id": user.id,
        "sender_username": user.username,
        "latitude": alert.latitude,
        "longitude": alert.longitude,
        "sent_at": alert.sent_at.isoformat(),
    }
    await manager.broadcast_to_roles(["admin", "ranger"], broadcast_payload)

    return alert

@router.get("/incidents", response_model=List[IncidentResponse])
def list_incidents(
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()

@router.patch("/incidents/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    new_status: IncidentStatus,
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    incident.status = new_status
    db.commit()
    db.refresh(incident)
    return incident
