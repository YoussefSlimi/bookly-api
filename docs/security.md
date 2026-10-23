# Security Considerations

| Area | Current behaviour |
|---|---|
| Password storage | Argon2 hashes via Passlib; `password_hash` is excluded from serialization and from public schemas |
| Token revocation | Logout blocklists the token's `jti` in Redis for 48 hours, which covers the refresh token lifetime |
| Token separation | Access and refresh tokens are not interchangeable; each bearer class rejects the other type |
| Email enumeration | `POST /password-reset-request` always returns 200 |
| Email links | Signed, salted, and valid for 1 hour |
| Account verification | Role checks require a verified email |
| Network | `TrustedHostMiddleware` restricts `Host` headers; CORS origins are an explicit allow-list |
| Secrets | `JWT_SECRET` and `ADMIN_SECRET_KEY` come from environment variables and must never be committed |

## Recommendations for production

- Use long random values for `JWT_SECRET` and `ADMIN_SECRET_KEY`, and rotate them if exposed.
- Serve the API over HTTPS only and set `APP_SCHEME=https`.
- Apply rate limiting on `/login`, `/signup`, and `/password-reset-request` (not currently implemented).
- Restrict book and tag modification to owners and admins; at present any authenticated user can modify any record.
- Run `alembic upgrade head` as part of deployment rather than relying on `init_db()`.
