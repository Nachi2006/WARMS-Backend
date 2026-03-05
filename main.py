from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session,text
from src.db.db import getDb, testConnection
from contextlib import asynccontextmanager
from src.logger.logger import logger
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not testConnection():
        logger.error("Could not connect to the database on startup.")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Welcome to Warms Backend"}

@app.get("/ping")
async def ping(db: Session = Depends(getDb)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection failed")