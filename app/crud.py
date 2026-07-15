"""
CRUD (Create, Read, Update, Delete) operations.
Keeping these separate from the route handlers keeps main.py clean.
"""

from sqlalchemy.orm import Session
from . import models, schemas
from .auth import hash_password, verify_password


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------
def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Fetch a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with a securely hashed password."""
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """
    Verify email + password combination.
    Returns the User if valid, otherwise None.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---------------------------------------------------------------------------
# Task CRUD (all scoped to a specific user - "user-specific tasks")
# ---------------------------------------------------------------------------
def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    """Insert a new task, owned by the given user."""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Return all tasks belonging to the given user only."""
    return (
        db.query(models.Task)
        .filter(models.Task.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_task(db: Session, task_id: int, user_id: int) -> models.Task | None:
    """
    Return a single task by ID, but ONLY if it belongs to the given user.
    This is what enforces "users cannot access other users' tasks".
    """
    return (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == user_id)
        .first()
    )


def update_task(
    db: Session, task_id: int, user_id: int, task_update: schemas.TaskUpdate
) -> models.Task | None:
    """Update a task, but only if it belongs to the given user."""
    db_task = get_task(db, task_id, user_id)
    if db_task is None:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int) -> models.Task | None:
    """Delete a task, but only if it belongs to the given user."""
    db_task = get_task(db, task_id, user_id)
    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()
    return db_task
