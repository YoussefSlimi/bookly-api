# Introduction

This is the **backend-only** technical reference for Bookly (Python/FastAPI under `backend/`). Client UI, routing, and state in `frontend/` are out of scope.

Use the [documentation map](README.md#documentation-map) in the index to jump to a topic.

## Conventions

- Paths in the API reference are relative to `/api/v1` unless stated otherwise.
- All request and response bodies are JSON.
- UIDs are UUIDs. Timestamps are ISO 8601 strings.
- "Access token" and "refresh token" refer to JWTs sent as `Authorization: Bearer <token>`.
