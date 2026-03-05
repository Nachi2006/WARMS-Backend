from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from ..utils.logger import logger

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=os.getenv("SQL_ECHO", "False") == "True",
    pool_pre_ping=True,  
    pool_recycle=3600,   
    pool_size=10,        
    max_overflow=20      
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def getDb():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def testConnection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database Connection Successful!")
            return True
    except Exception as e:
        logger.error(f"Database Connection failed: {e}")
        return False