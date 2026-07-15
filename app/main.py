"""
Task Manager API with User Authentication & Authorization.

Auth routes:
    POST    /auth/signup   -> Register a new user
    POST    /auth/login    -> Login, returns a JWT access token
    GET     /auth/me       -> Get the currently logged-in user's profile

Task routes (all require a valid JWT, all scoped to the logged-in user):
    POST    /tasks         -> Create a new task
    GET     /tasks         -> View all of MY tasks
    GET     /tasks/{id}    -> View a single task (must be mine)
    PUT     /tasks/{id}    -> Update a task (must be mine)
    DELETE  /tasks/{id}    -> Delete a task (must be mine)
"""

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db
from .auth import create_access_token, get_current_user

# Create all database tables on startup (if they don't already exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API with Authentication",
    description=(
        "A Task Manager API built with FastAPI, SQLite, and SQLAlchemy, "
        "featuring JWT-based authentication so each user can only see "
        "and manage their own tasks."
    ),
    version="2.0.0",
)


@app.get("/", tags=["Health"])
def read_root():
    """Basic health check / welcome route."""
    return {"message": "Task Manager API is running. Visit /docs for Swagger UI."}


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.post(
    "/auth/signup",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Rejects the request if the email is already registered (409 Conflict).
    - Password is hashed with bcrypt before being stored - it is never saved
      in plain text.
    """
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    return crud.create_user(db, user)


@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login using email (as 'username') and password.
    Returns a JWT access token on success.

    Uses OAuth2PasswordRequestForm so this endpoint works directly with
    Swagger UI's "Authorize" button (send email in the 'username' field).
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
def read_current_user(current_user: models.User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


# ---------------------------------------------------------------------------
# Task routes (protected - require a valid JWT via the 'current_user' dependency)
# ---------------------------------------------------------------------------
@app.post(
    "/tasks",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def add_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new task, owned by the logged-in user."""
    return crud.create_task(db, task, user_id=current_user.id)


@app.get("/tasks", response_model=List[schemas.TaskResponse], tags=["Tasks"])
def view_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """View all tasks belonging to the logged-in user."""
    return crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def view_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """View a single task - only if it belongs to the logged-in user."""
    db_task = crud.get_task(db, task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update a task - only if it belongs to the logged-in user."""
    db_task = crud.update_task(db, task_id, user_id=current_user.id, task_update=task_update)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["Tasks"])
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a task - only if it belongs to the logged-in user."""
    db_task = crud.delete_task(db, task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"message": f"Task with id {task_id} deleted successfully"}
