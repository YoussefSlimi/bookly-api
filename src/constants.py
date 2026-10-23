"""Application-wide constants — single source of truth for magic numbers."""

ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 2
ACCESS_TOKEN_EXPIRY_SECONDS = ACCESS_TOKEN_EXPIRY_MINUTES * 60
REFRESH_TOKEN_EXPIRY_SECONDS = REFRESH_TOKEN_EXPIRY_DAYS * 24 * 60 * 60

# JTI blocklist TTL must cover the longest token it protects
JTI_BLOCKLIST_EXPIRY_SECONDS = REFRESH_TOKEN_EXPIRY_SECONDS

# Email verification & password-reset link validity
EMAIL_TOKEN_MAX_AGE_SECONDS = 3600
