# 📚 Bookly — Backend API

> A production-ready **REST API** for a book review platform, built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
  - [Running the Services](#running-the-services)
- [Authentication Flow](#authentication-flow)
- [Role-Based Access Control](#role-based-access-control)
- [Background Tasks (Celery)](#background-tasks-celery)
- [Flower Monitoring](#flower-monitoring)
- [Database Migrations](#database-migrations)

---

## Overview

**Bookly** is a full-featured book review web service. Users can register, browse books, submit reviews, and manage tags. The platform supports two roles — `user` and `admin` — with JWT-based authentication, email verification, password reset flows, and a Redis-backed token blocklist for secure logouts.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.138 |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL (via `asyncpg`) |
| **ORM** | [SQLModel](https://sqlmodel.tiangolo.com/) + SQLAlchemy (async) |
| **Cache / Broker** | Redis |
| **Task Queue** | Celery |
| **Auth** | JWT (access + refresh tokens) |
| **Password Hashing** | Argon2 (`argon2-cffi`) + Passlib |
| **Email** | FastAPI-Mail (SMTP / Gmail) |
| **Migrations** | Alembic |
| **Server** | Uvicorn |

---

## Project Structure

```
backend/
├── src/
│   ├── __init__.py          # FastAPI app factory, lifespan, router registration
│   ├── config.py            # Pydantic settings (env-based configuration)
│   ├── constants.py         # App-wide constants (token expiry, etc.)
│   ├── errors.py            # Custom exception classes & global error handlers
│   ├── middleware.py        # CORS, TrustedHost, request logging middleware
│   ├── mail.py              # FastAPI-Mail setup & message factory
│   ├── celery_tasks.py      # Celery app + async email task
│   ├── auth/
│   │   ├── routers.py       # All auth endpoints
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── service.py       # User CRUD operations
│   │   ├── dependencies.py  # JWT bearer dependencies, role checker
│   │   └── utils.py         # Token creation, hashing, URL-safe tokens
│   ├── books/
│   │   ├── routes.py        # Book CRUD endpoints
│   │   ├── schemas.py       # Book Pydantic models
│   │   └── service.py       # Book business logic
│   ├── reviews/
│   │   ├── routes.py        # Review endpoints
│   │   ├── schemas.py       # Review Pydantic models
│   │   └── service.py       # Review business logic
│   ├── tags/
│   │   ├── routes.py        # Tag CRUD endpoints
│   │   ├── schemas.py       # Tag Pydantic models
│   │   └── service.py       # Tag business logic
│   ├── db/
│   │   ├── main.py          # Async engine, session factory, DB init
│   │   ├── models.py        # SQLModel table definitions
│   │   └── redis.py         # Redis client, JWT blocklist helpers
│   └── templates/           # HTML email templates
├── migrations/              # Alembic migration scripts
├── alembic.ini              # Alembic configuration
├── requirements.txt
└── .env                     # Environment variables (not committed)
```

---

## Features

- ✅ **User registration** with email verification (via secure URL-safe token)
- ✅ **JWT authentication** — access token (short-lived) + refresh token (long-lived)
- ✅ **Secure logout** — JTI-based token blocklist stored in Redis
- ✅ **Password reset** — request & confirm flow via email link
- ✅ **Role-based access control** — `user` and `admin` roles
- ✅ **Admin management** — list users, update roles, delete accounts
- ✅ **Book CRUD** — create, read, update, delete books
- ✅ **Reviews** — authenticated users can submit reviews (1–5 stars)
- ✅ **Tags** — create tags and associate them with books
- ✅ **Async email delivery** via Celery + Redis (non-blocking)
- ✅ **Request logging middleware** with response time tracking
- ✅ **CORS** configured for local frontend dev (`localhost:3000`, `localhost:5173`)
- ✅ **Interactive API docs** at `/docs` (Swagger) and `/redoc`

---

## API Endpoints

### 🔐 Auth — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/signup` | ❌ | Register a new user (sends verification email) |
| `POST` | `/admin/signup` | ✅ Admin | Create an admin account |
| `GET` | `/verify/{token}` | ❌ | Verify email address |
| `POST` | `/login` | ❌ | Login, returns access & refresh tokens |
| `GET` | `/refresh_token` | ✅ Refresh | Get a new access token |
| `GET` | `/me` | ✅ User | Get current user profile (with books) |
| `GET` | `/logout` | ✅ User | Revoke access token (adds JTI to blocklist) |
| `POST` | `/password-reset-request` | ❌ | Request a password reset email |
| `POST` | `/password-reset-confirm/{token}` | ❌ | Confirm and set new password |
| `POST` | `/send_mail` | ✅ Admin | Send a broadcast email |
| `GET` | `/users` | ✅ Admin | List all users |
| `PATCH` | `/users/{uid}/role` | ✅ Admin | Update a user's role |
| `DELETE` | `/users/{uid}` | ✅ Admin | Delete a user account |

### 📖 Books — `/api/v1/books`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | ✅ User | List all books |
| `POST` | `/` | ✅ User | Create a new book |
| `GET` | `/{book_uid}` | ✅ User | Get book details (with reviews & tags) |
| `PATCH` | `/{book_uid}` | ✅ User | Update a book |
| `DELETE` | `/{book_uid}` | ✅ User | Delete a book |
| `GET` | `/user/{user_uid}` | ✅ User | Get all books by a specific user |

### ⭐ Reviews — `/api/v1/reviews`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/book/{book_uid}` | ✅ User | Add a review to a book |

### 🏷️ Tags — `/api/v1/tags`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | ✅ User | List all tags |
| `POST` | `/` | ✅ User | Create a new tag |
| `POST` | `/book/{book_uid}/tags` | ✅ User | Attach tags to a book |
| `PUT` | `/{tag_uid}` | ✅ User | Update a tag |
| `DELETE` | `/{tag_uid}` | ✅ User | Delete a tag |

---

## Data Models

```
User ──< Book ──< Review
  │
  └──< Review

Book >──< Tag  (many-to-many via BookTag)
```

| Model | Key Fields |
|---|---|
| `User` | `uid`, `username`, `email`, `role`, `is_verified`, `password_hash` |
| `Book` | `uid`, `title`, `author`, `publisher`, `language`, `user_uid` |
| `Review` | `uid`, `rating` (1–5), `review_text`, `user_uid`, `book_uid` |
| `Tag` | `uid`, `name` |
| `BookTag` | `book_id`, `tag_id` (join table) |

---

## Getting Started

### Prerequisites

Make sure the following are installed and running:

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | |
| PostgreSQL | 14+ | Database must exist before running |
| Redis | 7+ | Used as Celery broker and token blocklist |
| pip | latest | |

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/bookly_db

# JWT
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256

# Redis
REDIS_URL=redis://localhost:6379/0

# Mail (Gmail example)
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your@gmail.com
MAIL_FROM_NAME=Bookly
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# App
DOMAIN=localhost:8000
APP_SCHEME=http
ADMIN_SECRET_KEY=your-admin-secret
```

> **Gmail tip**: Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your real password.

### Installation

```powershell
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv env
.\env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Services

You need **5 services** running simultaneously. Open a **separate terminal** for each:

#### 1. 🐘 PostgreSQL
Start via pgAdmin or Windows Services. Ensure the database exists:
```sql
CREATE DATABASE bookly_db;
```

#### 2. 🔴 Redis
**Via WSL (recommended on Windows):**
```bash
sudo service redis-server start
```
**Natively on Windows:**
```powershell
redis-server
```

> **Note:** If using WSL, the `REDIS_URL` in `.env` must point to the WSL IP (e.g., `redis://172.x.x.x:6379/0`). This IP can change after a reboot — check with `hostname -I` inside WSL.

#### 3. ⚙️ Celery Worker
```powershell
# In backend/ with venv activated
celery -A src.celery_tasks.c_app worker --loglevel=info -P solo
```
> `-P solo` is **required on Windows** since Celery does not support the default `prefork` pool on Windows.

#### 4. 🌸 Flower (Celery Monitor)
```powershell
# In backend/ with venv activated
celery -A src.celery_tasks.c_app flower --port=5555
```

Flower dashboard will be available at: **http://localhost:5555**

> Install if not present: `pip install flower`

#### 5. 🚀 FastAPI (Uvicorn)
```powershell
# In backend/ with venv activated
uvicorn src:app --reload
```

| URL | Description |
|---|---|
| http://localhost:8000 | API base |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:5555 | Flower (Celery monitor) |

---

## Authentication Flow

```
1. POST /signup                        → Account created, verification email sent (async)
2. GET  /verify/{token}                → Email confirmed, is_verified = true
3. POST /login                         → Returns { access_token, refresh_token }
4. GET  /me                            → Bearer <access_token> in Authorization header
5. GET  /refresh_token                 → Bearer <refresh_token> → new access_token
6. GET  /logout                        → JTI blocklisted in Redis, token invalidated
```

All protected routes require:
```
Authorization: Bearer <access_token>
```

---

## Role-Based Access Control

| Role | Permissions |
|---|---|
| `user` | Browse books, create/update/delete books, submit reviews, manage tags |
| `admin` | All user permissions + list/delete users, update roles, send broadcast emails |

**Creating an admin account:**
- Pass `admin_key` equal to `ADMIN_SECRET_KEY` in the `POST /signup` body (auto-verified), **or**
- An existing admin calls `POST /admin/signup`

---

## Background Tasks (Celery)

Email delivery is handled **asynchronously** by Celery so it never blocks HTTP responses.

**Triggered automatically for:**
| Trigger | Email |
|---|---|
| User signup | Email verification link |
| Password reset request | Password reset link |
| Admin broadcast | Custom message via `/send_mail` |

**Celery configuration** (in `src/config.py`):
```python
broker_url = Config.REDIS_URL          # Redis as message broker
result_backend = Config.REDIS_URL      # Redis for task results
broker_connection_retry_on_startup = True
```

---

## Flower Monitoring

[Flower](https://flower.readthedocs.io/) is a real-time **web-based monitoring dashboard** for Celery workers and tasks.

### Start Flower

```powershell
# In backend/ with venv activated
celery -A src.celery_tasks.c_app flower --port=5555
```

Access the dashboard at: **http://localhost:5555**

### What Flower Shows

| Panel | Information |
|---|---|
| **Dashboard** | Active workers, task rate, processed/failed counts |
| **Tasks** | Live list of all tasks with state, runtime, arguments, result |
| **Workers** | Worker status, concurrency, heartbeat, registered tasks |
| **Broker** | Redis broker queue stats (active, reserved, scheduled messages) |

### Task States

| State | Meaning |
|---|---|
| `PENDING` | Task queued, not yet picked up by a worker |
| `STARTED` | Worker is executing the task |
| `SUCCESS` | Task completed successfully |
| `FAILURE` | Task raised an exception |
| `RETRY` | Task failed and is being retried |

### Install Flower

If not already installed:
```powershell
pip install flower
```

Or add it to `requirements.txt`:
```
flower
```

> **Tip:** Flower is optional but highly recommended during development to debug email delivery tasks and monitor worker health.

---

## Database Migrations

Migrations are managed with **Alembic**.

```powershell
# Generate a new migration from model changes
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# View current migration state
alembic current
```

> In **development** (`ENV != production`), the app auto-creates all tables on startup via `SQLModel.metadata.create_all`.  
> In **production**, always use `alembic upgrade head` instead.

---

## License

This project is licensed under the **MIT License**.
