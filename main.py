from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.db.db import getDb, testConnection, engine, Base
from src.controllers.authController import router as auth_router
from src.controllers.userController import router as user_router
from contextlib import asynccontextmanager
from src.utils.logger import logger
from src.models.userModel import User
from src.models.bookingModel import Booking

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up WARMS-Backend...")
    logger.info("Starting up WARMS-Backend...")
    logger.info(f"Registered tables: {Base.metadata.tables.keys()}")
    if testConnection():
        # Create tables if they don't exist based on your User model
        Base.metadata.create_all(bind=engine)
    else:
        logger.error("Could not connect to the database on startup.")
    yield
    logger.info("Shutting down WARMS-Backend...")

app = FastAPI(
    title="WARMS API",
    lifespan=lifespan
)

# Registering the User endpoints (signup, login)
app.include_router(auth_router)
app.include_router(user_router)
@app.get("/")
async def root():
    return {"message": "Welcome to Warms Backend"}

@app.get("/ping", tags=["Health"])
async def ping(db: Session = Depends(getDb)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")
