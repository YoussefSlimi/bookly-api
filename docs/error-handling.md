# Error Handling

## Response format

Every custom exception returns the same JSON structure:

```json
{
  "message": "Human-readable description",
  "error_code": "machine_readable_code",
  "resolution": "Optional advice"
}
```

## Error reference

All custom exceptions extend `BooklyException`.

| Exception | `error_code` | HTTP | When raised |
|---|---|---|---|
| `InvalidToken` | `invalid_token` | 401 | Token is malformed, expired, or blocklisted |
| `RevokedToken` | `token_revoked` | 401 | Defined for explicitly revoked tokens |
| `AccessTokenRequired` | `access_token_required` | 401 | A refresh token was sent where an access token is required |
| `RefreshTokenRequired` | `refresh_token_required` | 403 | An access token was sent to the refresh endpoint |
| `InvalidCredentials` | `invalid_email_or_password` | 400 | Wrong email or password |
| `InsufficientPermission` | `insufficient_permissions` | 401 | Role not allowed for this action |
| `AccountNotVerified` | `account_not_verified` | 403 | Email not yet verified |
| `UserAlreadyExists` | `user_exists` | 403 | Email already registered |
| `UserNotFound` | `user_not_found` | 404 | No user matches the email or UID |
| `BookNotFound` | `book_not_found` | 404 | No book matches the UID |
| `TagNotFound` | `tag_not_found` | 404 | No tag matches the UID |
| `TagAlreadyExists` | `tag_exists` | 403 | Tag name already used |
| (unhandled / `SQLAlchemyError`) | `server_error` | 500 | Unexpected failure |

## Implementation (`src/errors.py`)

- `create_exception_handler(status_code, initial_detail)` is a factory that returns a FastAPI exception handler.
- `register_all_errors(app)` registers a handler for each exception above, plus handlers for HTTP 500 and `SQLAlchemyError`. Both return `{"message": "Oops! Something went wrong", "error_code": "server_error"}`; the `SQLAlchemyError` handler also logs the exception with `exc_info=True`.
