# Task Manager API (with Authentication & Authorization)

A backend Task Manager API built with **FastAPI**, **SQLAlchemy**, and **SQLite**, secured with **JWT authentication**. Each user can only view and manage their own tasks.

## Features

- User registration (signup) with securely hashed passwords (bcrypt)
- User login with JWT access token generation
- Protected task endpoints — only accessible with a valid token
- Tasks are user-specific: users can never see, update, or delete another user's tasks
- Request validation using Pydantic (including email format validation)
- Proper HTTP status codes and error handling (401, 404, 409, 422)
- Auto-generated interactive API docs (Swagger UI) with built-in "Authorize" support

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Auth:** JWT (via `python-jose`), password hashing via `bcrypt`

## Project Structure

```
task_manager_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, all API routes (auth + tasks)
│   ├── auth.py           # Password hashing, JWT creation/verification, get_current_user
│   ├── models.py         # SQLAlchemy models: User, Task (with FK relationship)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── crud.py            # Database operations (user CRUD + user-scoped task CRUD)
│   └── database.py        # DB engine, session, and Base setup
├── requirements.txt
├── Task_Manager_API.postman_collection.json   # Importable Postman collection
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

The API starts at: `http://127.0.0.1:8000`
The SQLite database file (`tasks.db`) is created automatically on first run.

### 5. Explore the API (Swagger UI)
Open: `http://127.0.0.1:8000/docs`

To test protected routes in Swagger:
1. Call `POST /auth/signup` to create a user.
2. Click the **Authorize** button (top right, lock icon).
3. Enter your email in the **username** field and your password, then Authorize.
4. Now all `/tasks` requests will include your token automatically.

## Authentication Flow

1. **Signup** (`POST /auth/signup`) — Create an account with full name, email, and password. Password is hashed with bcrypt before being stored; it is never saved as plain text.
2. **Login** (`POST /auth/login`) — Send email + password (as form fields `username` and `password`). Returns a JWT `access_token`.
3. **Use the token** — Pass it in the `Authorization` header as `Bearer <token>` on every `/tasks` request.
4. **`GET /auth/me`** — Returns the profile of whoever the token belongs to.

Tokens expire after 60 minutes (configurable in `app/auth.py`).

## API Endpoints

### Auth

| Method | Endpoint        | Auth Required | Description                          |
|--------|-----------------|:--------------:|----------------------------------------|
| POST   | `/auth/signup`  | No             | Register a new user                    |
| POST   | `/auth/login`   | No             | Login, returns a JWT access token      |
| GET    | `/auth/me`      | Yes            | Get the logged-in user's profile       |

### Tasks (all require a valid JWT)

| Method | Endpoint          | Description                          |
|--------|-------------------|----------------------------------------|
| POST   | `/tasks`          | Create a task (owned by logged-in user)|
| GET    | `/tasks`          | View all of MY tasks                   |
| GET    | `/tasks/{id}`     | View a single task (must be mine)      |
| PUT    | `/tasks/{id}`     | Update a task (must be mine)            |
| DELETE | `/tasks/{id}`     | Delete a task (must be mine)            |

### Field Reference

**User (signup)**

| Field     | Type   | Required | Notes                       |
|-----------|--------|----------|------------------------------|
| full_name | string | Yes      | 1–100 characters             |
| email     | string | Yes      | Must be a valid, unique email|
| password  | string | Yes      | Min 6 characters             |

**Task**

| Field       | Type   | Required | Notes                                |
|-------------|--------|----------|----------------------------------------|
| title       | string | Yes      | 1–100 characters                       |
| description | string | No       | Up to 500 characters                   |
| status      | string | No       | `"Pending"` or `"Completed"` (default: Pending) |

### Example Requests

**Signup**
```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Rohan Yeluguri", "email": "rohan@example.com", "password": "secret123"}'
```

**Login**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=rohan@example.com&password=secret123"
```
Response:
```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

**Create a task (authenticated)**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "status": "Pending"}'
```

**View my tasks**
```bash
curl http://127.0.0.1:8000/tasks -H "Authorization: Bearer <your_access_token>"
```

## Authorization Logic (User-Specific Tasks)

- Every `Task` row has a `user_id` foreign key pointing to the `User` who owns it.
- Every task query (`GET`, `PUT`, `DELETE`) filters by **both** `task_id` AND the logged-in user's `id`.
- If a task exists but belongs to someone else, the API returns **404 Not Found** (not 403) — this avoids revealing whether the task exists at all, which is a small security best practice.

## Error Handling

| Status | Meaning                                                    |
|--------|-------------------------------------------------------------|
| 401    | Missing/invalid/expired token, or wrong login credentials   |
| 404    | Task not found, or belongs to another user                  |
| 409    | Signup email already registered                             |
| 422    | Invalid request body (e.g. missing title, bad email format) |

## Postman Collection

Import `Task_Manager_API.postman_collection.json` into Postman. Run **Signup**, then **Login** (the token is automatically saved to a collection variable), then all task requests will be authenticated automatically.

## Notes

- The JWT `SECRET_KEY` in `app/auth.py` is a placeholder for this assignment. In a real deployment, it must be loaded from an environment variable and kept secret.
- Optional/bonus features (refresh tokens, logout/token blacklist, email verification, forgot password, role-based access control, rate limiting, Docker) are **not included** in this submission, as per scope.
