# Auth API: `/api/v1/auth`

| Method | Path | Authentication | Description |
|---|---|---|---|
| POST | `/signup` | None | Register a user |
| POST | `/admin/signup` | Admin | Create an admin account |
| GET | `/verify/{token}` | None | Verify an email address |
| POST | `/login` | None | Obtain access and refresh tokens |
| GET | `/refresh_token` | Refresh token | Issue a new access token |
| GET | `/me` | User or admin | Current user with books and reviews |
| GET | `/logout` | Access token | Revoke the current access token |
| POST | `/password-reset-request` | None | Request a reset email |
| POST | `/password-reset-confirm/{token}` | None | Set a new password |
| POST | `/send_mail` | Admin | Send a broadcast email |
| GET | `/users` | Admin | List all users |
| PATCH | `/users/{uid}/role` | Admin | Change a user's role |
| DELETE | `/users/{uid}` | Admin | Delete a user (returns `204`) |

## Behaviour notes

**`POST /signup`**

- If `admin_key` is present and equals `ADMIN_SECRET_KEY`, the account is created with role `admin` and `is_verified = true`.
- Otherwise the role is `user`, `is_verified = false`, and a verification email is queued through Celery.

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "username": "jane",
  "email": "jane@example.com",
  "password": "s3cretpass"
}
```

**`POST /admin/signup`** creates an account with role `admin` and `is_verified = true`; no email is sent. The caller must be an existing admin.

**`GET /verify/{token}`** decodes the URL-safe token, marks the user as verified, and returns 200. An invalid or expired token raises `InvalidToken`.

**`POST /login`**

```json
// Request
{ "email": "jane@example.com", "password": "s3cretpass" }

// Response
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "user": { "email": "jane@example.com", "uid": "b3c1...", "role": "user" }
}
```

**`GET /refresh_token`** reads the user from the database and issues a new access token.

**`GET /logout`** adds the token's `jti` to the Redis blocklist. The token is rejected on all later requests.

**`POST /password-reset-request`** queues a reset email if the account exists. It always returns 200, so the endpoint cannot be used to discover registered emails.

**`POST /password-reset-confirm/{token}`** validates the token and checks that the two passwords match before storing a new Argon2 hash.

**`PATCH /users/{uid}/role`** accepts `{ "role": "admin" }` or `{ "role": "user" }` and returns the updated `UserPublicModel`.

## Schemas (`src/auth/schemas.py`)

| Schema | Fields | Used for |
|---|---|---|
| `UserCreateModel` | `first_name`, `last_name`, `username` (max 8 chars), `email`, `password` (min 6 chars), `admin_key?` | `POST /signup` |
| `AdminCreateModel` | Inherits `UserCreateModel` | `POST /admin/signup` |
| `UserLoginModel` | `email`, `password` | `POST /login` |
| `UserModel` | All user fields, including `password_hash` | Internal use only |
| `UserPublicModel` | All user fields except `password_hash` | `GET /users`, role update |
| `UserBooksModel` | `UserModel` plus `books`, `reviews` | `GET /me` |
| `EmailModel` | `addresses: List[EmailStr]` | `POST /send_mail` |
| `PasswordResetRequestModel` | `email` | `POST /password-reset-request` |
| `PasswordResetConfirmModel` | `new_password`, `confirm_new_password` | `POST /password-reset-confirm/{token}` |
| `UserRoleUpdateModel` | `role`, matching `^(admin\|user)$` | `PATCH /users/{uid}/role` |
