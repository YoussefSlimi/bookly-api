from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import UUID

from src.auth.schemas import UserCreateModel
from src.auth import routers as auth_routes


AUTH_PREFIX = "/api/v1/auth"


def test_user_creation(client, fake_session, fake_user_service, monkeypatch):
    signup_data = {
        "username": "tstuse20",
        "first_name": "test20",
        "last_name": "user20",
        "email": "test20@gmail.com",
        "password": "test120",
    }
    created_user = {
        "uid": str(UUID("5a4f1871-cb6f-4da0-85c4-655d4e3f73e8")),
        "username": signup_data["username"],
        "first_name": signup_data["first_name"],
        "last_name": signup_data["last_name"],
        "email": signup_data["email"],
        "role": "user",
        "is_verified": False,
    }
    fake_user_service.user_exists = AsyncMock(return_value=False)
    fake_user_service.create_user = AsyncMock(return_value=created_user)
    send_email = Mock()
    monkeypatch.setattr(auth_routes, "send_email", send_email)

    response = client.post(f"{AUTH_PREFIX}/signup", json=signup_data)

    assert response.status_code == 201
    assert response.json()["message"] == "Account Created! Check email to verify your account"
    fake_user_service.user_exists.assert_awaited_once_with(
        signup_data["email"], fake_session
    )
    fake_user_service.create_user.assert_awaited_once_with(
        UserCreateModel(**signup_data),
        fake_session,
        role="user",
        is_verified=False,
    )
    send_email.delay.assert_called_once()


def test_user_login(client, fake_session, fake_user_service, monkeypatch):
    user = SimpleNamespace(
        email="reader@example.com",
        password_hash="hashed-password",
        role="user",
        uid=UUID("5a4f1871-cb6f-4da0-85c4-655d4e3f73e8"),
    )
    fake_user_service.get_user_by_email = AsyncMock(return_value=user)
    monkeypatch.setattr(auth_routes, "verify_password", Mock(return_value=True))
    create_access_token = Mock(side_effect=["access-token", "refresh-token"])
    monkeypatch.setattr(auth_routes, "create_access_token", create_access_token)

    response = client.post(
        f"{AUTH_PREFIX}/login",
        json={"email": user.email, "password": "reader-password"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "access-token"
    assert response.json()["refresh_token"] == "refresh-token"
    assert response.json()["user"] == {
        "email": user.email,
        "uid": str(user.uid),
        "role": user.role,
    }
    fake_user_service.get_user_by_email.assert_awaited_once_with(
        user.email, fake_session
    )
    auth_routes.verify_password.assert_called_once_with(
        "reader-password", user.password_hash
    )
    assert create_access_token.call_count == 2
