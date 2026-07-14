"""
Database configuration for the Task Manager API.
Uses SQLite as the database and SQLAlchemy as the ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file will be created in the project directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# check_same_thread=False is required only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory used to create DB sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models will inherit from
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session to path operations
    and ensures it is closed after the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
