"""
SQLAlchemy ORM models for the Task Manager API.

Contains two tables:
- User: stores registered users (for authentication)
- Task: stores tasks, each linked to the user who owns it
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class StatusEnum(str, enum.Enum):
    """Allowed values for task status."""
    pending = "Pending"
    completed = "Completed"


class User(Base):
    """Represents a registered user (for authentication)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One user can have many tasks. "back_populates" links this to Task.owner
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    """Represents a single task row in the database, owned by a user."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending, nullable=False)

    # Foreign key linking each task to the user who created it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Lets us access task.owner to get the User object directly
    owner = relationship("User", back_populates="tasks")
