from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from src.db.db import Base
from src.schemas.rangerSchema import IncidentType, IncidentStatus

class SightingLog(Base):
    __tablename__ = "sighting_logs"

    id = Column(Integer, primary_key=True, index=True)
    ranger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    local_id = Column(String, nullable=True)
    species = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

class PatrolRoute(Base):
    __tablename__ = "patrol_routes"

    id = Column(Integer, primary_key=True, index=True)
    ranger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    local_id = Column(String, nullable=True)
    coordinates = Column(JSON, nullable=False)
    patrol_date = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(IncidentType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    gps_timestamp = Column(DateTime(timezone=True), nullable=False)
    photo_path = Column(String, nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.open)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SosAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Integer, default=0)
