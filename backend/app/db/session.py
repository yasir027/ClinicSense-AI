# Purpose:
# This file creates the SQLAlchemy database engine, session factory,
# and shared database dependency used by the backend.
#
# Why this file exists:
# The backend needs one standard way to talk to PostgreSQL.
# Instead of opening database connections manually in every route or service,
# this file defines one consistent connection pattern and one reusable session provider.
# It opens and closes database connections the proper way.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()