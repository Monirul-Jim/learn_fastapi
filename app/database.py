from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Configuration using Pydantic Settings
class Settings(BaseSettings):
    database_url: str
    
    # Automatically reads from .env file
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# 2. SQLAlchemy Setup
# Uses the environment variable from settings
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()