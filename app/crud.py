"""
CRUD (Create, Read, Update, Delete) operations for the Task model.
Keeping these separate from the route handlers keeps main.py clean.
"""

from sqlalchemy.orm import Session
from . import models, schemas


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Insert a new task into the database."""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    """Return all tasks (with basic skip/limit support)."""
    return db.query(models.Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> models.Task | None:
    """Return a single task by its ID, or None if it doesn't exist."""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> models.Task | None:
    """Update an existing task with only the fields the client provided."""
    db_task = get_task(db, task_id)
    if db_task is None:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> models.Task | None:
    """Delete a task by ID. Returns the deleted task, or None if not found."""
    db_task = get_task(db, task_id)
    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()
    return db_task
