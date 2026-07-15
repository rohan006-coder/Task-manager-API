"""
Pydantic schemas used for request validation and response formatting.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .models import StatusEnum


# ---------------------------------------------------------------------------
# User / Auth schemas
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    """Schema for the signup request (POST /auth/signup)."""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Plain-text password (min 6 chars)")


class UserLogin(BaseModel):
    """Schema for the login request (POST /auth/login)."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema used when returning user info (never includes the password)."""
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema returned after a successful login."""
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Task schemas
# ---------------------------------------------------------------------------
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
    user_id: int

    model_config = ConfigDict(from_attributes=True)
