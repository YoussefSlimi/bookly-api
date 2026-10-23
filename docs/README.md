# Bookly Backend: Technical Documentation

> **Scope:** This folder documents the **backend only** — the FastAPI service under `backend/src/`, its API, database, Redis, Celery, and mail. It does **not** describe the frontend app in `frontend/`.

| | |
|---|---|
| **Component** | Bookly backend (REST API) |
| **API version** | v1 (`/api/v1`) |
| **Code covered** | `backend/src/` |
| **Audience** | Backend developers, maintainers, and API integrators |
| **Run & install** | [Backend README](../README.md) |
| **Frontend** | Not documented here |

## Documentation map

| Topic | Document |
|---|---|
| Conventions and how to use these docs | [Introduction](introduction.md) |
| Layers, request lifecycle, package layout | [Architecture](architecture.md) |
| Environment settings and constants | [Configuration](configuration.md) |
| JWTs, roles, dependencies | [Authentication](authentication.md) |
| HTTP endpoints | [API overview](api/README.md) |
| Error JSON shape and exception codes | [Error handling](error-handling.md) |
| Tables, relationships, migrations | [Data model](data-model.md) |
| App factory, middleware, mail, Celery, DB, Redis | [Infrastructure](infrastructure.md) |
| Service classes and methods | [Service layer](service-layer.md) |
| Production security notes | [Security](security.md) |

## Where to start

| If you want to... | Read |
|---|---|
| Integrate a client with the API | [API overview](api/README.md), [Error handling](error-handling.md) |
| Understand login, tokens, and roles | [Authentication](authentication.md) |
| Modify or extend the code | [Architecture](architecture.md), [Infrastructure](infrastructure.md), [Service layer](service-layer.md) |
| Change the database schema | [Data model](data-model.md) |
| Review security posture | [Security](security.md) |
