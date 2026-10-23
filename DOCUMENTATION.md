# Bookly Backend — Technical Documentation

This document is the complete technical reference for the Bookly backend.  
It covers every module, class, function, schema, error, and constant in the `src/` package.

---

## Table of Contents

1. [Application Entry Point — `src/__init__.py`](#1-application-entry-point)
2. [Configuration — `src/config.py`](#2-configuration)
3. [Constants — `src/constants.py`](#3-constants)
4. [Error Handling — `src/errors.py`](#4-error-handling)
5. [Middleware — `src/middleware.py`](#5-middleware)
6. [Mail — `src/mail.py`](#6-mail)
7. [Background Tasks — `src/celery_tasks.py`](#7-background-tasks)
8. [Database](#8-database)
   - [Engine & Session — `src/db/main.py`](#81-engine--session)
   - [Models — `src/db/models.py`](#82-models)
   - [Redis — `src/db/redis.py`](#83-redis)
9. [Auth Module — `src/auth/`](#9-auth-module)
   - [Utils — `src/auth/utils.py`](#91-utils)
   - [Schemas — `src/auth/schemas.py`](#92-schemas)
   - [Service — `src/auth/service.py`](#93-service)
   - [Dependencies — `src/auth/dependencies.py`](#94-dependencies)
   - [Routers — `src/auth/routers.py`](#95-routers)
10. [Books Module — `src/books/`](#10-books-module)
    - [Schemas — `src/books/schemas.py`](#101-schemas)
    - [Service — `src/books/service.py`](#102-service)
    - [Routes — `src/books/routes.py`](#103-routes)
11. [Reviews Module — `src/reviews/`](#11-reviews-module)
    - [Schemas — `src/reviews/schemas.py`](#111-schemas)
    - [Service — `src/reviews/service.py`](#112-service)
    - [Routes — `src/reviews/routes.py`](#113-routes)
12. [Tags Module — `src/tags/`](#12-tags-module)
    - [Schemas — `src/tags/schemas.py`](#121-schemas)
    - [Service — `src/tags/service.py`](#122-service)
    - [Routes — `src/tags/routes.py`](#123-routes)
13. [Error Reference](#13-error-reference)
14. [Token Lifecycle Diagram](#14-token-lifecycle-diagram)
15. [Database Schema Diagram](#15-database-schema-diagram)

---

## 1. Application Entry Point

**File:** `src/__init__.py`

The FastAPI application is created and configured here.

### `life_span(app)` — async context manager

Runs at startup and shutdown.

| Phase | Action |
|---|---|
| Startup | Calls `init_db()` when `ENV != production` to auto-create tables |
| Shutdown | Logs a stop message |

> In production, skip `init_db()` and use `alembic upgrade head` before starting.

### `app` — FastAPI instance

| Setting | Value |
|---|---|
| Title | Bookly |
| Version | v1 |
| Docs URL | `/docs` |
| ReDoc URL | `/redoc` |
| License | MIT |

### Router prefixes

| Router | Prefix | Tags |
|---|---|---|
| `book_router` | `/api/v1/books` | books |
| `auth_router` | `/api/v1/auth` | auth |
| `review_router` | `/api/v1/reviews` | review |
| `tags_router` | `/api/v1/tags` | tags |

---

## 2. Configuration

**File:** `src/config.py`

Settings are loaded by Pydantic from `backend/.env` using `pydantic-settings`.

### `Settings` class

| Field | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `str` | required | PostgreSQL async connection string |
| `JWT_SECRET` | `str` | required | Secret key for signing JWTs |
| `JWT_ALGORITHM` | `str` | `HS256` | JWT signing algorithm |
| `REDIS_URL` | `str` | `redis://localhost:6379/0` | Redis connection URL |
| `MAIL_USERNAME` | `str` | `""` | SMTP username |
| `MAIL_PASSWORD` | `str` | `""` | SMTP password or app password |
| `MAIL_FROM` | `str` | `""` | Sender email address |
| `MAIL_PORT` | `int` | `587` | SMTP port |
| `MAIL_SERVER` | `str` | `smtp.localhost` | SMTP server hostname |
| `MAIL_FROM_NAME` | `str` | `Bookly` | Sender display name |
| `MAIL_STARTTLS` | `bool` | `True` | Use STARTTLS |
| `MAIL_SSL_TLS` | `bool` | `False` | Use SSL/TLS |
| `USE_CREDENTIALS` | `bool` | `True` | Authenticate with SMTP server |
| `VALIDATE_CERTS` | `bool` | `True` | Validate TLS certificates |
| `DOMAIN` | `str` | `localhost` | Domain used for building email links |
| `APP_SCHEME` | `str` | `http` | `http` or `https` |
| `ADMIN_SECRET_KEY` | `str` | `""` | Secret key for self-service admin registration |

### Module-level Celery settings

These are read by Celery directly from this module when `c_app.config_from_object('src.config')` is called:

```python
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
```

### `Config` singleton

A single `Settings()` instance exported as `Config`. Import it as:

```python
from src.config import Config
value = Config.REDIS_URL
```

---

## 3. Constants

**File:** `src/constants.py`

Single source of truth for all magic numbers.

| Constant | Value | Description |
|---|---|---|
| `ACCESS_TOKEN_EXPIRY_MINUTES` | `15` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRY_DAYS` | `2` | Refresh token lifetime in days |
| `ACCESS_TOKEN_EXPIRY_SECONDS` | `900` | Computed: `15 * 60` |
| `REFRESH_TOKEN_EXPIRY_SECONDS` | `172800` | Computed: `2 * 24 * 60 * 60` |
| `JTI_BLOCKLIST_EXPIRY_SECONDS` | `172800` | Redis TTL for blocklisted JTIs; equals refresh token lifetime |
| `EMAIL_TOKEN_MAX_AGE_SECONDS` | `3600` | Validity window for email verification / password-reset links (1 hour) |

---

## 4. Error Handling

**File:** `src/errors.py`

### Exception Hierarchy

All custom exceptions extend `BooklyException(Exception)`.

| Exception | HTTP Status | `error_code` | Meaning |
|---|---|---|---|
| `InvalidToken` | 401 | `invalid_token` | Token is malformed, expired, or blocklisted |
| `RevokedToken` | 401 | `token_revoked` | Token was explicitly revoked |
| `AccessTokenRequired` | 401 | `access_token_required` | A refresh token was used where an access token is required |
| `RefreshTokenRequired` | 403 | `refresh_token_required` | An access token was used where a refresh token is required |
| `UserAlreadyExists` | 403 | `user_exists` | Email is already registered |
| `InvalidCredentials` | 400 | `invalid_email_or_password` | Wrong email or password |
| `InsufficientPermission` | 401 | `insufficient_permissions` | Role does not allow the action |
| `BookNotFound` | 404 | `book_not_found` | Book UID does not exist |
| `TagNotFound` | 404 | `tag_not_found` | Tag UID does not exist |
| `TagAlreadyExists` | 403 | `tag_exists` | Tag name is already used |
| `UserNotFound` | 404 | `user_not_found` | User email or UID does not exist |
| `AccountNotVerified` | 403 | `account_not_verified` | User has not clicked the verification link |

All exceptions return a JSON body:
```json
{
  "message": "<human-readable description>",
  "error_code": "<machine-readable code>",
  "resolution": "<optional advice>"
}
```

### `create_exception_handler(status_code, initial_detail)`

Factory function that returns a FastAPI exception handler.  
Used internally by `register_all_errors`.

### `register_all_errors(app)`

Registers all custom exception handlers on the FastAPI `app` instance.  
Also registers:
- **HTTP 500** handler → returns `{"message": "Oops! Something went wrong", "error_code": "server_error"}`
- **SQLAlchemyError** handler → same response + logs the error with `exc_info=True`

---

## 5. Middleware

**File:** `src/middleware.py`

### `register_middleware(app)`

Attaches three layers of middleware to the FastAPI app in this order:

#### Request Logger (custom)

Logs every request as:
```
METHOD - /path - STATUS_CODE completed after X.XXXs
```
Uses the `uvicorn.access` logger so output is formatted consistently with Uvicorn logs.

#### CORS Middleware

Pre-allowed origins:
- `http://localhost`
- `http://localhost:3000`  ← React default
- `http://localhost:5173`  ← Vite default
- `http://127.0.0.1`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

If `Config.DOMAIN` is set, both `http://` and `https://` variants of that domain are added automatically.

All methods and headers are allowed (`*`). Credentials are permitted (`allow_credentials=True`).

#### TrustedHostMiddleware

Blocks requests with a `Host` header not in the allowed list.  
Allowed hosts: `localhost`, `127.0.0.1`, and the hostname extracted from `Config.DOMAIN`.

---

## 6. Mail

**File:** `src/mail.py`

Configures FastAPI-Mail for sending transactional emails.

### `mail` — `FastMail` instance

Initialized from `Config` settings. Used directly or through Celery tasks.

### `create_message(recipients, subject, body)`

| Parameter | Type | Description |
|---|---|---|
| `recipients` | `list[str]` | List of recipient email addresses |
| `subject` | `str` | Email subject line |
| `body` | `str` | HTML body content |

Returns a `MessageSchema` with `subtype=MessageType.html`.

---

## 7. Background Tasks

**File:** `src/celery_tasks.py`

### `c_app` — Celery application

```python
c_app = Celery()
c_app.config_from_object('src.config')
```

Reads broker and backend URLs from `src/config.py` at startup.

### `send_email(recipients, subject, body)` — Celery task

| Parameter | Type | Description |
|---|---|---|
| `recipients` | `list[str]` | Email addresses to send to |
| `subject` | `str` | Subject line |
| `body` | `str` | HTML email body |

Uses `async_to_sync` from `asgiref` to run the async `mail.send_message()` inside the synchronous Celery worker.

**Usage (enqueue, non-blocking):**
```python
send_email.delay(["user@example.com"], "Subject", "<h1>Body</h1>")
```

---

## 8. Database

### 8.1 Engine & Session

**File:** `src/db/main.py`

#### `engine` — `AsyncEngine`

```python
engine = create_async_engine(Config.DATABASE_URL)
```

Async SQLAlchemy engine pointing at PostgreSQL via `asyncpg`.

#### `init_db()` — async function

Creates all tables defined in `SQLModel.metadata` using `metadata.create_all`.  
Called during lifespan startup in non-production environments.

#### `get_session()` — async generator (FastAPI dependency)

Yields an `AsyncSession` per request. Sessions are configured with `expire_on_commit=False` to allow accessing attributes after commit without re-querying.

```python
async def endpoint(session: AsyncSession = Depends(get_session)):
    ...
```

---

### 8.2 Models

**File:** `src/db/models.py`

All models use PostgreSQL-specific column types via `sqlalchemy.dialects.postgresql`.

#### `User`

Table: `users`

| Column | Type | Notes |
|---|---|---|
| `uid` | `UUID` | Primary key, auto-generated |
| `username` | `VARCHAR` | |
| `email` | `VARCHAR` | |
| `first_name` | `VARCHAR` | |
| `last_name` | `VARCHAR` | |
| `role` | `VARCHAR` | Default: `"user"` |
| `is_verified` | `BOOLEAN` | Default: `False` |
| `password_hash` | `VARCHAR` | Excluded from serialization |
| `created_at` | `TIMESTAMP` | Auto-set to `datetime.now()` |
| `updated_at` | `TIMESTAMP` | Auto-set to `datetime.now()` |

Relationships:
- `books` → `List[Book]` — eagerly loaded (`selectin`)
- `reviews` → `List[Review]` — eagerly loaded (`selectin`)

---

#### `Book`

Table: `books`

| Column | Type | Notes |
|---|---|---|
| `uid` | `UUID` | Primary key, auto-generated |
| `title` | `VARCHAR` | |
| `author` | `VARCHAR` | |
| `publisher` | `VARCHAR` | |
| `language` | `VARCHAR` | |
| `user_uid` | `UUID` | FK → `users.uid` (nullable) |
| `created_at` | `TIMESTAMP` | |
| `updated_at` | `TIMESTAMP` | |

Relationships:
- `user` → `Optional[User]`
- `reviews` → `List[Review]` — eagerly loaded
- `tags` → `List[Tag]` via `BookTag` — eagerly loaded

---

#### `Review`

Table: `reviews`

| Column | Type | Notes |
|---|---|---|
| `uid` | `UUID` | Primary key, auto-generated |
| `rating` | `INTEGER` | Constrained: `1 ≤ rating ≤ 5` |
| `review_text` | `VARCHAR` | |
| `user_uid` | `UUID` | FK → `users.uid` (nullable) |
| `book_uid` | `UUID` | FK → `books.uid` (nullable) |
| `created_at` | `TIMESTAMP` | |
| `updated_at` | `TIMESTAMP` | |

Relationships:
- `user` → `Optional[User]`
- `book` → `Optional[Book]`

---

#### `Tag`

Table: `tags`

| Column | Type | Notes |
|---|---|---|
| `uid` | `UUID` | Primary key, auto-generated |
| `name` | `VARCHAR` | |
| `created_at` | `TIMESTAMP` | |

Relationships:
- `books` → `List[Book]` via `BookTag` — eagerly loaded

---

#### `BookTag`

Table: `book_tags` (join table)

| Column | Type | Notes |
|---|---|---|
| `book_id` | `UUID` | FK → `books.uid`, composite PK |
| `tag_id` | `UUID` | FK → `tags.uid`, composite PK |

---

### 8.3 Redis

**File:** `src/db/redis.py`

#### `token_blocklist` — `aioredis.Redis`

```python
token_blocklist = aioredis.from_url(Config.REDIS_URL)
```

Async Redis client used exclusively for the JTI blocklist.

#### `add_jti_to_blocklist(jti)` — async

Stores `jti` in Redis with TTL = `JTI_BLOCKLIST_EXPIRY_SECONDS` (48 hours).  
Called on logout.

#### `token_in_blocklist(jti)` — async → `bool`

Returns `True` if `jti` exists in Redis (token is revoked).  
Called on every authenticated request before processing.

---

## 9. Auth Module

### 9.1 Utils

**File:** `src/auth/utils.py`

#### Password hashing

Uses Passlib with the Argon2 scheme.

| Function | Signature | Description |
|---|---|---|
| `generate_password_hash` | `(passwd: str) -> str` | Hash a plaintext password with Argon2 |
| `verify_password` | `(password: str, hashed_password: str) -> bool` | Verify a plaintext password against a hash |

#### JWT tokens

| Function | Description |
|---|---|
| `create_access_token(user_data, expiry, refresh)` | Creates a signed JWT. Payload includes `user`, `exp`, `jti` (UUID4), and `refresh` flag. |
| `decode_token(token)` | Decodes and verifies a JWT. Returns the payload dict or `None` on failure. |

**JWT payload structure:**
```json
{
  "user": { "email": "...", "user_uid": "...", "role": "..." },
  "exp": 1234567890,
  "jti": "uuid4-string",
  "refresh": false
}
```

#### URL-safe tokens (email links)

Uses `itsdangerous.URLSafeTimedSerializer` with `salt="email-configuration"`.

| Function | Description |
|---|---|
| `create_url_safe_token(data)` | Serializes `data` dict into a signed, URL-safe string |
| `decode_url_safe_token(token)` | Verifies signature and checks age against `EMAIL_TOKEN_MAX_AGE_SECONDS` (1 hour). Returns `None` on failure. |

---

### 9.2 Schemas

**File:** `src/auth/schemas.py`

| Schema | Fields | Used for |
|---|---|---|
| `UserCreateModel` | `first_name`, `last_name`, `username` (≤8), `email`, `password` (≥6), `admin_key?` | `POST /signup` request body |
| `AdminCreateModel` | Inherits `UserCreateModel` | `POST /admin/signup` request body |
| `UserModel` | All User fields including `password_hash` | Internal use |
| `UserPublicModel` | All fields except `password_hash` | Admin user listing |
| `UserBooksModel` | Extends `UserModel` + `books: list[BookModel]` + `reviews: list[ReviewModel]` | `GET /me` response |
| `UserLoginModel` | `email`, `password` | `POST /login` request |
| `EmailModel` | `addresses: List[EmailStr]` | `POST /send_mail` request |
| `PasswordResetRequestModel` | `email` | `POST /password-reset-request` request |
| `PasswordResetConfirmModel` | `new_password`, `confirm_new_password` | `POST /password-reset-confirm/{token}` request |
| `UserRoleUpdateModel` | `role` — must match `^(admin\|user)$` | `PATCH /users/{uid}/role` request |

---

### 9.3 Service

**File:** `src/auth/service.py`

`UserService` is a stateless class injected where needed.

| Method | Signature | Description |
|---|---|---|
| `get_user_by_email` | `(email, session) -> User \| None` | SELECT by email |
| `user_exists` | `(email, session) -> bool` | Returns `True` if the email is taken |
| `create_user` | `(user_data, session, role, is_verified) -> User` | Hashes password, strips `admin_key`, inserts user |
| `update_user` | `(user, user_data: dict, session) -> User` | Applies dict of field updates via `setattr` |
| `get_all_users` | `(session) -> list[User]` | All users ordered by `created_at` DESC |
| `get_user_by_uid` | `(uid, session) -> User \| None` | SELECT by UUID |
| `delete_user` | `(user, session)` | Hard-deletes the user row |

---

### 9.4 Dependencies

**File:** `src/auth/dependencies.py`

#### `TokenBearer(HTTPBearer)` — base class

On every request:
1. Extracts the `Bearer` token from the `Authorization` header
2. Calls `decode_token()` — raises `InvalidToken` if invalid
3. Checks JTI against Redis blocklist — raises `InvalidToken` if revoked
4. Calls `verify_token_data()` (subclass hook)

#### `AccessTokenBearer(TokenBearer)`

Raises `AccessTokenRequired` if the token's `refresh` flag is `True`.  
Use this for all regular protected routes.

#### `RefreshTokenBearer(TokenBearer)`

Raises `RefreshTokenRequired` if the token's `refresh` flag is `False`.  
Use this only on the `GET /refresh_token` endpoint.

#### `get_current_user(token_details, session)` — async dependency

1. Extracts `email` from the decoded access token
2. Fetches the user from the database
3. Raises `HTTP 404` if the user no longer exists
4. Returns the `User` ORM object

#### `RoleChecker(allowed_roles)`

A callable dependency class.

```python
role_checker = Depends(RoleChecker(["admin", "user"]))
```

1. Calls `get_current_user` internally
2. Raises `AccountNotVerified` if `user.is_verified` is `False`
3. Raises `InsufficientPermission` if the user's role is not in `allowed_roles`
4. Returns `True` on success

---

### 9.5 Routers

**File:** `src/auth/routers.py`  
Prefix: `/api/v1/auth`

#### Helper: `_auth_link(path, token)`

Builds an absolute URL for email links using `Config.APP_SCHEME` and `Config.DOMAIN`.

---

#### Endpoints

**`POST /signup`**
- Body: `UserCreateModel`
- If `admin_key` is provided and matches `ADMIN_SECRET_KEY` → role is `admin`, `is_verified=True`
- Otherwise → role is `user`, `is_verified=False`, verification email is queued via Celery

---

**`POST /admin/signup`**
- Auth: existing admin (`get_current_user`, role must be `admin`)
- Body: `AdminCreateModel`
- Creates account with `role=admin`, `is_verified=True`, no email sent

---

**`GET /verify/{token}`**
- Decodes URL-safe token, extracts email, sets `is_verified=True`
- Returns 200 on success, raises `InvalidToken` on bad/expired token

---

**`POST /login`**
- Body: `UserLoginModel`
- Verifies Argon2 hash
- Returns `{ access_token, refresh_token, user: { email, uid, role } }`
- Access token expires in **15 minutes**, refresh token in **2 days**

---

**`GET /refresh_token`**
- Auth: `RefreshTokenBearer` (must send refresh token)
- Fetches user from DB and issues a new access token

---

**`GET /me`**
- Auth: `AccessTokenBearer` + `RoleChecker(["admin","user"])`
- Returns `UserBooksModel` (user + their books + their reviews)

---

**`GET /logout`**
- Auth: `AccessTokenBearer`
- Adds JTI to Redis blocklist
- Token is immediately invalid for all future requests

---

**`POST /password-reset-request`**
- Body: `PasswordResetRequestModel`
- If user exists, queues a password-reset email via Celery
- Always returns 200 (intentionally vague to prevent email enumeration)

---

**`POST /password-reset-confirm/{token}`**
- Body: `PasswordResetConfirmModel`
- Validates token and that passwords match
- Updates `password_hash` with new Argon2 hash

---

**`POST /send_mail`**
- Auth: `admin_role_checker`
- Body: `EmailModel`
- Queues a broadcast email to the given list of addresses

---

**`GET /users`**
- Auth: admin
- Returns `list[UserPublicModel]` (all users, no password hashes)

---

**`PATCH /users/{uid}/role`**
- Auth: admin
- Body: `UserRoleUpdateModel`
- Updates `role` field on the target user
- Returns `UserPublicModel`

---

**`DELETE /users/{uid}`**
- Auth: admin
- Hard-deletes the user row
- Returns `204 No Content`

---

## 10. Books Module

### 10.1 Schemas

**File:** `src/books/schemas.py`

| Schema | Fields | Used for |
|---|---|---|
| `BookModel` | `uid`, `title`, `author`, `publisher`, `language`, `created_at`, `updated_at` | Embedded in `UserBooksModel` |
| `BookDetailModel` | Extends `BookModel` + `reviews`, `tags` | `GET /{book_uid}` response |
| `BookCreateModel` | `title`, `author`, `publisher`, `language` | `POST /` request body |
| `UpdateBookModel` | All fields optional | `PATCH /{book_uid}` request body |
| `BookResponseModel` | Same as `BookModel` + `from_attributes=True` | `POST /` and `GET /` response |

---

### 10.2 Service

**File:** `src/books/service.py`

`BookService` is a stateless class.

| Method | Description |
|---|---|
| `get_all_books(session)` | All books ordered by `created_at` DESC |
| `get_user_books(user_uid, session)` | Books belonging to a specific user, ordered ASC |
| `get_book(book_uid, session)` | Single book by UID, or `None` |
| `create_book(book_data, user_uid, session)` | Inserts a new book, sets `user_uid` from the token |
| `update_book(book_uid, update_data, session)` | Partial update using `exclude_unset=True`, updates `updated_at` |
| `delete_book(book_uid, session)` | Hard-deletes, returns `True` or `None` |

---

### 10.3 Routes

**File:** `src/books/routes.py`  
Prefix: `/api/v1/books`  
All routes require: `RoleChecker(["admin","user"])`

| Method | Path | Extra dependency | Action |
|---|---|---|---|
| `GET` | `/` | — | Returns all books |
| `GET` | `/user/{user_uid}` | — | Returns books by user |
| `POST` | `/` | `AccessTokenBearer` | Creates a book (uses token's `user_uid`) |
| `GET` | `/{book_uid}` | `AccessTokenBearer` | Returns `BookDetailModel` |
| `PATCH` | `/{book_uid}` | `AccessTokenBearer` | Updates a book |
| `DELETE` | `/{book_uid}` | `AccessTokenBearer` | Deletes a book |

Raises `BookNotFound` (→ 404) when the UID does not match any row.

---

## 11. Reviews Module

### 11.1 Schemas

**File:** `src/reviews/schemas.py`

| Schema | Fields | Used for |
|---|---|---|
| `ReviewModel` | `uid`, `rating`, `review_text`, `user_uid?`, `book_uid?`, `created_at`, `updated_at` | Embedded in `UserBooksModel` and `BookDetailModel` |
| `ReviewCreateModel` | `rating` (1–5), `review_text` | `POST /book/{book_uid}` request body |

---

### 11.2 Service

**File:** `src/reviews/service.py`

#### `ReviewService.add_review_to_book(user_email, book_uid, review_data, session)`

1. Fetches the book by `book_uid` — raises `HTTP 404` if missing
2. Fetches the user by `user_email` — raises `HTTP 404` if missing
3. Creates a `Review`, links it to both `user` and `book`
4. Commits and returns the new review
5. Catches all unexpected exceptions, logs them, and raises `HTTP 500`

---

### 11.3 Routes

**File:** `src/reviews/routes.py`  
Prefix: `/api/v1/reviews`

| Method | Path | Auth | Action |
|---|---|---|---|
| `POST` | `/book/{book_uid}` | `get_current_user` | Add a review to a book |

---

## 12. Tags Module

### 12.1 Schemas

**File:** `src/tags/schemas.py`

| Schema | Fields | Used for |
|---|---|---|
| `TagModel` | `uid`, `name`, `created_at` | Response body |
| `TagCreateModel` | `name` | Create / update request body |
| `TagAddModel` | `tags: List[TagCreateModel]` | `POST /book/{book_uid}/tags` request body |

---

### 12.2 Service

**File:** `src/tags/service.py`

`TagService` is a stateless class.

| Method | Description |
|---|---|
| `get_tags(session)` | All tags ordered by `created_at` DESC |
| `get_tag_by_uid(tag_uid, session)` | Single tag by UID, or `None` |
| `add_tag(tag_data, session)` | Creates a new tag. Raises `TagAlreadyExists` if name is taken |
| `add_tags_to_book(book_uid, tag_data, session)` | For each name in `tag_data.tags`: finds or creates the tag, then appends it to `book.tags`. Raises `BookNotFound` if book missing |
| `update_tag(tag_uid, tag_update_data, session)` | Updates tag name. Raises `TagNotFound` if UID missing |
| `delete_tag(tag_uid, session)` | Hard-deletes tag. Raises `TagNotFound` if UID missing |

---

### 12.3 Routes

**File:** `src/tags/routes.py`  
Prefix: `/api/v1/tags`  
All routes require: `RoleChecker(["user","admin"])`

| Method | Path | Action |
|---|---|---|
| `GET` | `/` | List all tags |
| `POST` | `/` | Create a tag |
| `POST` | `/book/{book_uid}/tags` | Attach tags to a book |
| `PUT` | `/{tag_uid}` | Update a tag |
| `DELETE` | `/{tag_uid}` | Delete a tag — returns 204 |

---

## 13. Error Reference

Quick lookup table for all error codes returned by the API:

| `error_code` | HTTP | When raised |
|---|---|---|
| `user_exists` | 403 | Email is already registered |
| `user_not_found` | 404 | Email or UID does not match any user |
| `book_not_found` | 404 | Book UID does not exist |
| `tag_not_found` | 404 | Tag UID does not exist |
| `tag_exists` | 403 | Tag name already used |
| `invalid_email_or_password` | 400 | Wrong credentials on login |
| `invalid_token` | 401 | Token malformed, expired, or blocklisted |
| `token_revoked` | 401 | Token was explicitly revoked (logout) |
| `access_token_required` | 401 | Refresh token sent to an access-token-only endpoint |
| `refresh_token_required` | 403 | Access token sent to the refresh endpoint |
| `insufficient_permissions` | 401 | User's role is not in the allowed list |
| `account_not_verified` | 403 | User has not verified their email |
| `server_error` | 500 | Unhandled exception or SQLAlchemy error |

---

## 14. Token Lifecycle Diagram

```
  Client                              API                         Redis
    │                                  │                            │
    │── POST /signup ─────────────────>│                            │
    │<─ 201 (email queued) ────────────│                            │
    │                                  │                            │
    │── GET /verify/{token} ──────────>│                            │
    │<─ 200 ──────────────────────────│                            │
    │                                  │                            │
    │── POST /login ──────────────────>│                            │
    │<─ { access_token, refresh_token }│                            │
    │                                  │                            │
    │── GET /me (Bearer access_token) >│── check jti in blocklist ->│
    │                                  │<─ not found (valid) ───────│
    │<─ UserBooksModel ────────────────│                            │
    │                                  │                            │
    │── GET /refresh_token ───────────>│                            │
    │   (Bearer refresh_token)         │                            │
    │<─ { access_token } ─────────────│                            │
    │                                  │                            │
    │── GET /logout ──────────────────>│── SET jti "" EX 172800 ──>│
    │<─ 200 ──────────────────────────│                            │
    │                                  │                            │
    │── GET /me (same token) ─────────>│── check jti in blocklist ->│
    │                                  │<─ found (revoked) ─────────│
    │<─ 401 invalid_token ────────────│                            │
```

---

## 15. Database Schema Diagram

```
┌──────────────────────────────┐
│           users              │
├──────────────────────────────┤
│ uid        UUID  PK          │
│ username   VARCHAR           │
│ email      VARCHAR           │
│ first_name VARCHAR           │
│ last_name  VARCHAR           │
│ role       VARCHAR           │
│ is_verified BOOLEAN          │
│ password_hash VARCHAR        │
│ created_at TIMESTAMP         │
│ updated_at TIMESTAMP         │
└───────────┬──────────────────┘
            │ 1
            │
            │ *
┌───────────▼──────────────────┐       ┌──────────────────────┐
│           books              │       │        tags           │
├──────────────────────────────┤       ├──────────────────────┤
│ uid        UUID  PK          │       │ uid        UUID  PK   │
│ title      VARCHAR           │       │ name       VARCHAR    │
│ author     VARCHAR           ├───────┤ created_at TIMESTAMP  │
│ publisher  VARCHAR           │  M:M  └──────────────────────┘
│ language   VARCHAR           │       (via book_tags join table)
│ user_uid   UUID  FK          │
│ created_at TIMESTAMP         │
│ updated_at TIMESTAMP         │
└───────────┬──────────────────┘
            │ 1
            │
            │ *
┌───────────▼──────────────────┐
│          reviews             │
├──────────────────────────────┤
│ uid        UUID  PK          │
│ rating     INTEGER (1–5)     │
│ review_text VARCHAR          │
│ user_uid   UUID  FK          │
│ book_uid   UUID  FK          │
│ created_at TIMESTAMP         │
│ updated_at TIMESTAMP         │
└──────────────────────────────┘
```
