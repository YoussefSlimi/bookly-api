# Configuration and Constants

## Settings (`src/config.py`)

Settings are loaded from `backend/.env` using `pydantic-settings` and exposed as the singleton `Config`.

```python
from src.config import Config
redis_url = Config.REDIS_URL
```

| Field | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `str` | required | PostgreSQL async connection string |
| `JWT_SECRET` | `str` | required | Secret used to sign JWTs |
| `JWT_ALGORITHM` | `str` | `HS256` | JWT signing algorithm |
| `REDIS_URL` | `str` | `redis://localhost:6379/0` | Redis connection URL |
| `MAIL_USERNAME` | `str` | `""` | SMTP username |
| `MAIL_PASSWORD` | `str` | `""` | SMTP password or app password |
| `MAIL_FROM` | `str` | `""` | Sender address |
| `MAIL_FROM_NAME` | `str` | `Bookly` | Sender display name |
| `MAIL_SERVER` | `str` | `smtp.localhost` | SMTP host |
| `MAIL_PORT` | `int` | `587` | SMTP port |
| `MAIL_STARTTLS` | `bool` | `True` | Use STARTTLS |
| `MAIL_SSL_TLS` | `bool` | `False` | Use SSL/TLS |
| `USE_CREDENTIALS` | `bool` | `True` | Authenticate with the SMTP server |
| `VALIDATE_CERTS` | `bool` | `True` | Validate TLS certificates |
| `DOMAIN` | `str` | `localhost` | Domain used to build email links |
| `APP_SCHEME` | `str` | `http` | `http` or `https` |
| `ADMIN_SECRET_KEY` | `str` | `""` | Key enabling self-service admin registration |

**Celery settings.** The module also defines the following values, which Celery reads through `c_app.config_from_object('src.config')`:

```python
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
```

## Constants (`src/constants.py`)

| Constant | Value | Description |
|---|---|---|
| `ACCESS_TOKEN_EXPIRY_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRY_DAYS` | `2` | Refresh token lifetime |
| `ACCESS_TOKEN_EXPIRY_SECONDS` | `900` | `15 * 60` |
| `REFRESH_TOKEN_EXPIRY_SECONDS` | `172800` | `2 * 24 * 60 * 60` |
| `JTI_BLOCKLIST_EXPIRY_SECONDS` | `172800` | Redis TTL for blocklisted JTIs; equals the refresh token lifetime |
| `EMAIL_TOKEN_MAX_AGE_SECONDS` | `3600` | Validity of verification and password-reset links (1 hour) |
