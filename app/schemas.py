"""
Pydantic schemas used for request validation and response formatting.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .models import StatusEnum


class TaskBase(BaseModel):
    """Common fields shared across create/update/response schemas."""
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=500, description="Task description")
    status: StatusEnum = Field(default=StatusEnum.pending, description="Task status")


class TaskCreate(TaskBase):
    """Schema used when creating a new task (POST /tasks)."""
    pass


class TaskUpdate(BaseModel):
    """
    Schema used when updating a task (PUT /tasks/{id}).
    All fields are optional so the client can send only what needs to change.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[StatusEnum] = None


class TaskResponse(TaskBase):
    """Schema used when returning a task in an API response."""
    id: int

    model_config = ConfigDict(from_attributes=True)
