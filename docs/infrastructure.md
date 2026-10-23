# Infrastructure Modules

## Application entry point (`src/__init__.py`)

**`life_span(app)`** is an async context manager.

| Phase | Action |
|---|---|
| Startup | Calls `init_db()` when `ENV != production` |
| Shutdown | Logs a stop message |

**`app`** is the FastAPI instance (title `Bookly`, version `v1`, license MIT, docs at `/docs` and `/redoc`).

| Router | Prefix | Tag |
|---|---|---|
| `book_router` | `/api/v1/books` | books |
| `auth_router` | `/api/v1/auth` | auth |
| `review_router` | `/api/v1/reviews` | review |
| `tags_router` | `/api/v1/tags` | tags |

## Middleware (`src/middleware.py`)

`register_middleware(app)` attaches three layers:

| Middleware | Behaviour |
|---|---|
| Request logger | Logs `METHOD - /path - STATUS completed after X.XXXs` through the `uvicorn.access` logger |
| CORS | Allows `localhost` and `127.0.0.1` (bare, `:3000`, `:5173`). If `Config.DOMAIN` is set, its `http://` and `https://` forms are added. All methods and headers are allowed; credentials are permitted. |
| TrustedHost | Rejects requests whose `Host` header is not `localhost`, `127.0.0.1`, or the hostname in `Config.DOMAIN` |

## Mail (`src/mail.py`)

- `mail` is the `FastMail` instance initialized from `Config`.
- `create_message(recipients, subject, body)` returns an HTML `MessageSchema`.

| Parameter | Type | Description |
|---|---|---|
| `recipients` | `list[str]` | Recipient addresses |
| `subject` | `str` | Subject line |
| `body` | `str` | HTML body |

## Background tasks (`src/celery_tasks.py`)

`c_app = Celery()` is configured from `src.config`. The task `send_email(recipients, subject, body)` runs the async `mail.send_message()` inside the synchronous worker using `asgiref.sync.async_to_sync`.

```python
send_email.delay(["user@example.com"], "Subject", "<h1>Body</h1>")
```

| Trigger | Email |
|---|---|
| Signup | Verification link |
| Password reset request | Reset link |
| `POST /auth/send_mail` | Admin broadcast |

## Database engine and session (`src/db/main.py`)

| Item | Description |
|---|---|
| `engine` | `create_async_engine(Config.DATABASE_URL)`, an async SQLAlchemy engine using `asyncpg` |
| `init_db()` | Creates all tables from `SQLModel.metadata` |
| `get_session()` | FastAPI dependency yielding an `AsyncSession` per request, with `expire_on_commit=False` |

```python
async def endpoint(session: AsyncSession = Depends(get_session)):
    ...
```

## Redis (`src/db/redis.py`)

| Item | Description |
|---|---|
| `token_blocklist` | Async Redis client (`aioredis.from_url(Config.REDIS_URL)`) used only for the JTI blocklist |
| `add_jti_to_blocklist(jti)` | Stores the JTI with a TTL of `JTI_BLOCKLIST_EXPIRY_SECONDS` (48 hours); called on logout |
| `token_in_blocklist(jti) -> bool` | Returns `True` if the JTI is present; called on every authenticated request |
