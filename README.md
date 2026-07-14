# Simple Task Manager API

A simple backend application built with **FastAPI**, **SQLAlchemy**, and **SQLite** that allows users to manage tasks using REST APIs (Create, Read, Update, Delete).

## Features

- Add a new task
- View all tasks
- View a single task by ID
- Update a task
- Delete a task
- Request validation using Pydantic
- Proper HTTP status codes and error handling (404 for missing tasks, 422 for invalid input)
- Auto-generated interactive API docs (Swagger UI)

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite
- **Libraries:** SQLAlchemy (ORM), Pydantic (validation), Uvicorn (ASGI server)

## Project Structure

```
task_manager_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and route handlers
│   ├── models.py        # SQLAlchemy ORM model (Task)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── crud.py           # Database CRUD logic
│   └── database.py       # DB engine, session, and Base setup
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd task_manager_api
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
uvicorn app.main:app --reload
```

The API will start at: `http://127.0.0.1:8000`

The SQLite database file (`tasks.db`) is created automatically in the project folder the first time you run the app.

### 5. Explore the API (Swagger UI)
Open your browser and go to:
```
http://127.0.0.1:8000/docs
```
This gives you an interactive UI to test every endpoint directly.

Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`

## API Endpoints

| Method | Endpoint          | Description             |
|--------|-------------------|--------------------------|
| POST   | `/tasks`          | Add a new task           |
| GET    | `/tasks`          | View all tasks           |
| GET    | `/tasks/{id}`     | View a single task by ID |
| PUT    | `/tasks/{id}`     | Update a task            |
| DELETE | `/tasks/{id}`     | Delete a task             |

### Task Fields

| Field       | Type   | Required | Notes                                |
|-------------|--------|----------|----------------------------------------|
| title       | string | Yes      | 1–100 characters                       |
| description | string | No       | Up to 500 characters                   |
| status      | string | No       | `"Pending"` or `"Completed"` (default: Pending) |

### Example Requests

**Create a task**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "status": "Pending"}'
```

**View all tasks**
```bash
curl http://127.0.0.1:8000/tasks
```

**Update a task**
```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Completed"}'
```

**Delete a task**
```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

## Error Handling

- Requesting a task that doesn't exist returns **404 Not Found**.
- Sending invalid data (e.g., missing title) returns **422 Unprocessable Entity** with details about what's wrong.

## Notes

- Optional/bonus features (search & filter, Swagger customization, Docker, pagination) are **not included** in this submission, as per scope.
