from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class IncidentType(str, Enum):
    poaching = "poaching"
    fence_break = "fence_break"
    other = "other"

class IncidentStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"

class SightingLogEntry(BaseModel):
    local_id: Optional[str] = None
    species: str
    latitude: float
    longitude: float
    observed_at: datetime

class PatrolRouteEntry(BaseModel):
    local_id: Optional[str] = None
    coordinates: List[List[float]]
    patrol_date: datetime

class SyncPayload(BaseModel):
    sightings: Optional[List[SightingLogEntry]] = []
    patrol_routes: Optional[List[PatrolRouteEntry]] = []

class SyncResult(BaseModel):
    sightings_synced: int
    routes_synced: int
    conflicts_resolved: int

class IncidentResponse(BaseModel):
    id: int
    reporter_id: int
    type: IncidentType
    latitude: float
    longitude: float
    gps_timestamp: datetime
    photo_path: str
    status: IncidentStatus
    created_at: datetime

    class Config:
        from_attributes = True

class SosPayload(BaseModel):
    latitude: float
    longitude: float

class SosResponse(BaseModel):
    id: int
    sender_id: int
    latitude: float
    longitude: float
    sent_at: datetime
    resolved: bool

    class Config:
        from_attributes = True
