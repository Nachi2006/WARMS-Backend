from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
from db.db import getDb, testConnection, engine, Base
from utils.logger import logger

from models.userModel import User
from models.bookingModel import Booking
from models.auditLogModel import AuditLog
from models.hotspotModel import AnimalHotspot
from models.rangerModels import SightingLog, PatrolRoute, Incident, SosAlert
from models.complaintModel import Complaint
from models.inventoryModel import InventoryItem
from models.announcementModel import Announcement

from controllers.authController import router as auth_router
from controllers.userController import router as user_router
from controllers.adminController import router as admin_router
from controllers.geospatialController import router as geo_router
from controllers.speciesController import router as species_router
from controllers.rangerController import router as ranger_router
from controllers.wsController import router as ws_router
from controllers.complaintController import router as complaint_router
from controllers.inventoryController import router as inventory_router
from controllers.announcementController import router as announcement_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WARMS-Backend...")
    if testConnection():
        Base.metadata.create_all(bind=engine)
        logger.info(f"Tables registered: {list(Base.metadata.tables.keys())}")
    else:
        logger.error("Database connection failed on startup.")
    yield
    logger.info("Shutting down WARMS-Backend.")

app = FastAPI(
    title="WARMS API",
    description="Wildlife Administration and Reserve Management System",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(geo_router)
app.include_router(species_router)
app.include_router(ranger_router)
app.include_router(ws_router)
app.include_router(complaint_router)
app.include_router(inventory_router)
app.include_router(announcement_router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "WARMS API is running", "version": "1.0.0"}

@app.get("/ping", tags=["Health"])
async def ping(db: Session = Depends(getDb)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
