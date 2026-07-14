"""
SQLAlchemy ORM model for the Task table.
"""

import enum
from sqlalchemy import Column, Integer, String, Enum
from .database import Base


class StatusEnum(str, enum.Enum):
    """Allowed values for task status."""
    pending = "Pending"
    completed = "Completed"


class Task(Base):
    """Represents a single task row in the database."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending, nullable=False)
