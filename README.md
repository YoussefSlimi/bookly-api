# Bookly API

A REST API for a book review platform, built with FastAPI, PostgreSQL, Redis, and Celery.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![License](https://img.shields.io/badge/license-MIT-green)

## Table of Contents

- [Overview](#overview)
- [Documentation](#documentation)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Overview](#api-overview)
- [Background Tasks](#background-tasks)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [License](#license)

## Overview

Bookly lets users register, browse books, submit reviews, and organize books with tags. It supports two roles (`user` and `admin`), JWT authentication with refresh tokens, email verification, password reset, and a Redis-backed token blocklist for secure logout. Emails are sent asynchronously through Celery so they never block API responses.

## Documentation

| Resource | Description |
|---|---|
| [Backend technical docs](docs/README.md) | Backend only: architecture, auth, API reference, errors, data model, security |
| Swagger UI (`/docs`) | Interactive API explorer, available when the server is running |
| ReDoc (`/redoc`) | Readable API reference, available when the server is running |

## Features

- User registration with email verification
- JWT authentication (short-lived access token, long-lived refresh token)
- Secure logout via JTI blocklist in Redis
- Password reset by email link
- Role-based access control (`user`, `admin`)
- Admin tools: list users, change roles, delete accounts, send broadcast emails
- Book CRUD, reviews (1–5 stars), and tags (many-to-many)
- Asynchronous email delivery with Celery and Redis
- Request logging middleware with response-time tracking
- CORS preconfigured for local frontends (`localhost:3000`, `localhost:5173`)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.11+ |
| Database | PostgreSQL via `asyncpg` |
| ORM | SQLModel + SQLAlchemy (async) |
| Cache / Broker | Redis |
| Task queue | Celery (monitored with Flower) |
| Auth | JWT, Argon2 password hashing |
| Email | FastAPI-Mail (SMTP) |
| Migrations | Alembic |
| Server | Uvicorn |

## Project Structure

```
backend/
├── src/
│   ├── __init__.py          # App factory, lifespan, router registration
│   ├── config.py            # Environment-based settings (Pydantic)
│   ├── constants.py         # App-wide constants
│   ├── errors.py            # Custom exceptions and global handlers
│   ├── middleware.py        # CORS, TrustedHost, request logging
│   ├── mail.py              # FastAPI-Mail setup
│   ├── celery_tasks.py      # Celery app and email task
│   ├── auth/                # Users, tokens, roles
│   ├── books/               # Book CRUD
│   ├── reviews/             # Book reviews
│   ├── tags/                # Tags and book-tag association
│   ├── db/                  # Engine/session, models, Redis helpers
│   ├── templates/           # HTML email templates
│   └── tests/               # Pytest tests (auth, books)
├── docs/                    # Backend technical docs only (see docs/README.md)
├── migrations/              # Alembic scripts
├── alembic.ini
├── requirements.txt
├── .env.example             # Environment template (copy to .env)
└── .env                     # Local configuration (not committed)
```

See [Architecture](docs/architecture.md) for the layered design and the [data model](docs/data-model.md) for the entity-relationship diagram.

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | |
| PostgreSQL | 14+ | The database must exist before startup |
| Redis | 7+ | Celery broker and token blocklist |

### Installation

```bash
git clone <your-repository-url>
cd backend

python -m venv env
source env/bin/activate        # Windows: .\env\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env           # Windows: copy .env.example .env
```

Edit `.env` and set at least `DATABASE_URL`, `JWT_SECRET`, and any mail values you need. See [Configuration](#configuration).

Create the database:

```sql
CREATE DATABASE bookly_db;
```

### Running the services

Bookly needs four processes. Run each in its own terminal, with the virtual environment activated, from the `backend/` directory.

**1. Redis**

```bash
redis-server
```

On Windows, run Redis through WSL (`sudo service redis-server start`). If you do, set `REDIS_URL` to the WSL IP (find it with `hostname -I`). This IP can change after a reboot.

**2. Celery worker**

```bash
celery -A src.celery_tasks.c_app worker --loglevel=info
```

On Windows, add `-P solo`, since the default `prefork` pool is not supported there.

**3. Flower (optional, Celery monitoring)**

```bash
pip install flower
celery -A src.celery_tasks.c_app flower --port=5555
```

**4. API server**

```bash
uvicorn src:app --reload
```

| URL | Purpose |
|---|---|
| http://localhost:8000 | API base |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:5555 | Flower dashboard |

## Configuration

All settings are loaded from `backend/.env` (see `src/config.py`). Copy [`.env.example`](.env.example) to `.env` and replace placeholders. Required variables: `DATABASE_URL`, `JWT_SECRET`. Optional variables use the defaults shown in the example file.

Generate secrets with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

When using Gmail, create an [App Password](https://support.google.com/accounts/answer/185833) rather than using your account password. Never commit `.env`. The full list of settings and defaults is in [Configuration](docs/configuration.md).

## API Overview

The API is versioned under `/api/v1` and grouped into four resources:

| Resource | Base path | Purpose |
|---|---|---|
| Auth | `/api/v1/auth` | Signup, login, token refresh, logout, password reset, user administration |
| Books | `/api/v1/books` | Create, read, update, delete books |
| Reviews | `/api/v1/reviews` | Add reviews to books |
| Tags | `/api/v1/tags` | Manage tags and attach them to books |

Protected routes expect the header `Authorization: Bearer <access_token>`. Access tokens last 15 minutes and refresh tokens last 2 days. Two roles exist: `user` and `admin`. An admin account can be created by including `admin_key` (matching `ADMIN_SECRET_KEY`) in the `POST /signup` body, or by an existing admin calling `POST /admin/signup`.

For every endpoint, request and response examples, error codes, and the token lifecycle, see the [API reference](docs/api/README.md) and [authentication](docs/authentication.md) docs.

## Background Tasks

Celery handles email delivery using Redis as broker and result backend. Emails are triggered by user signup (verification link), password reset requests (reset link), and admin broadcasts (`POST /api/v1/auth/send_mail`).

[Flower](https://flower.readthedocs.io/) provides a live dashboard at http://localhost:5555 showing workers, queued and active tasks, runtimes, and results. It is useful for debugging email delivery.

| Task state | Meaning |
|---|---|
| `PENDING` | Queued, not yet picked up |
| `STARTED` | Being executed by a worker |
| `SUCCESS` | Completed |
| `FAILURE` | Raised an exception |
| `RETRY` | Failed and is being retried |

## Database Migrations

Migrations are managed with Alembic.

```bash
alembic revision --autogenerate -m "describe your change"   # create a migration
alembic upgrade head                                        # apply all migrations
alembic downgrade -1                                        # roll back one step
alembic current                                             # show current revision
```

When `ENV != production`, tables are created automatically at startup with `SQLModel.metadata.create_all`. In production, always use `alembic upgrade head`.

## Testing

Tests live in `src/tests/` and use **pytest** with mocked services and sessions (no running PostgreSQL or Redis required for the current suite).

```bash
pip install pytest
pytest src/tests
```

Coverage today is limited to **auth** and **books** routes; tags, reviews, and integration tests are not included yet.

## Known Limitations

- Any authenticated user can currently update or delete books and tags. Restricting this to owners and admins is recommended.
- Only the review-creation endpoint is exposed; reviews cannot yet be listed, edited, or deleted individually.
- No Docker or compose setup is included yet.

See [Security considerations](docs/security.md) for production recommendations.

## Contributing

1. Fork the repository and create a feature branch.
2. Make your changes, including a migration if models changed.
3. Update the relevant files under `docs/` if you change endpoints, schemas, errors, or configuration.
4. Open a pull request describing what changed and why.

## License

Released under the [MIT License](LICENSE).