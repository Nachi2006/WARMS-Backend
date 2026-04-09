from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
from src.db.db import getDb, testConnection, engine, Base
from src.utils.logger import logger

from src.models.userModel import User
from src.models.bookingModel import Booking
from src.models.auditLogModel import AuditLog
from src.models.hotspotModel import AnimalHotspot
from src.models.rangerModels import SightingLog, PatrolRoute, Incident, SosAlert
from src.models.complaintModel import Complaint
from src.models.inventoryModel import InventoryItem
from src.models.announcementModel import Announcement

from src.controllers.authController import router as auth_router
from src.controllers.userController import router as user_router
from src.controllers.adminController import router as admin_router
from src.controllers.geospatialController import router as geo_router
from src.controllers.speciesController import router as species_router
from src.controllers.rangerController import router as ranger_router
from src.controllers.wsController import router as ws_router
from src.controllers.complaintController import router as complaint_router
from src.controllers.inventoryController import router as inventory_router
from src.controllers.announcementController import router as announcement_router

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
