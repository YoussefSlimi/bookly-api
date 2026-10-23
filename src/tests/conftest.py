from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

import src
from src import app
from src.auth import routers as auth_routes
from src.books import routes as book_routes
from src.db.main import get_session


@pytest.fixture
def fake_session():
    return Mock()


@pytest.fixture
def fake_user_service(monkeypatch):
    service = Mock()
    monkeypatch.setattr(auth_routes, "user_service", service)
    return service


@pytest.fixture
def client(fake_session, monkeypatch):
    monkeypatch.setattr(src, "init_db", AsyncMock())

    def get_mock_session():
        yield fake_session

    app.dependency_overrides.clear()
    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[book_routes.role_checker.dependency] = lambda: True
    app.dependency_overrides[book_routes.access_token_bearer] = lambda: {
        "user": {"user_uid": "test-user-uid"}
    }

    try:
        with TestClient(app, base_url="http://localhost") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def fake_book_service(monkeypatch):
    service = Mock()
    monkeypatch.setattr(book_routes, "book_service", service)
    return service