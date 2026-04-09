from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.db import getDb
from src.models.hotspotModel import AnimalHotspot
from src.schemas.geospatialSchema import HotspotCreate, HotspotResponse
from src.auth.auth import get_current_user_token, require_roles
from src.utils.geomasking import apply_geomasking

router = APIRouter(prefix="/geospatial", tags=["Geospatial"])

_ranger_or_admin = require_roles("ranger", "admin")

@router.post("/hotspots", response_model=HotspotResponse, status_code=status.HTTP_201_CREATED)
def create_hotspot(
    body: HotspotCreate,
    token_data: dict = Depends(_ranger_or_admin),
    db: Session = Depends(getDb),
):
    user_email = token_data["email"]
    from src.models.userModel import User
    user = db.query(User).filter(User.email == user_email).first()

    hotspot = AnimalHotspot(
        species=body.species,
        latitude=body.latitude,
        longitude=body.longitude,
        notes=body.notes,
        recorded_by=user.id,
    )
    db.add(hotspot)
    db.commit()
    db.refresh(hotspot)

    return HotspotResponse(
        id=hotspot.id,
        species=hotspot.species,
        latitude=hotspot.latitude,
        longitude=hotspot.longitude,
        notes=hotspot.notes,
        recorded_by=hotspot.recorded_by,
        recorded_at=hotspot.recorded_at,
        masked=False,
    )

@router.get("/hotspots", response_model=List[HotspotResponse])
def list_hotspots(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(getDb),
):
    role = token_data.get("role", "user")
    hotspots = db.query(AnimalHotspot).all()
    results = []
    for h in hotspots:
        if role == "user":
            masked_lat, masked_lon = apply_geomasking(h.latitude, h.longitude)
            results.append(HotspotResponse(
                id=h.id,
                species=h.species,
                latitude=masked_lat,
                longitude=masked_lon,
                notes=None,
                recorded_by=h.recorded_by,
                recorded_at=h.recorded_at,
                masked=True,
            ))
        else:
            results.append(HotspotResponse(
                id=h.id,
                species=h.species,
                latitude=h.latitude,
                longitude=h.longitude,
                notes=h.notes,
                recorded_by=h.recorded_by,
                recorded_at=h.recorded_at,
                masked=False,
            ))
    return results
