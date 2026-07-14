"""
Simple FastAPI Task Manager API

Provides CRUD REST APIs to manage tasks:
    POST    /tasks        -> Create a new task
    GET     /tasks        -> View all tasks
    GET     /tasks/{id}   -> View a single task
    PUT     /tasks/{id}   -> Update a task
    DELETE  /tasks/{id}   -> Delete a task
"""

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db

# Create all database tables on startup (if they don't already exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Simple Task Manager API",
    description="A simple backend application to manage tasks using FastAPI, SQLite and SQLAlchemy.",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def read_root():
    """Basic health check / welcome route."""
    return {"message": "Task Manager API is running. Visit /docs for Swagger UI."}


@app.post(
    "/tasks",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def add_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create (add) a new task."""
    return crud.create_task(db, task)


@app.get(
    "/tasks",
    response_model=List[schemas.TaskResponse],
    tags=["Tasks"],
)
def view_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """View all tasks."""
    return crud.get_tasks(db, skip=skip, limit=limit)


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
)
def view_task(task_id: int, db: Session = Depends(get_db)):
    """View a single task by ID."""
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task (title, description, and/or status)."""
    db_task = crud.update_task(db, task_id, task_update)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    tags=["Tasks"],
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task by ID."""
    db_task = crud.delete_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"message": f"Task with id {task_id} deleted successfully"}
