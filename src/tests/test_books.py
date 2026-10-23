from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

from src.books.schemas import BookCreateModel


BOOKS_PREFIX = "/api/v1/books"


def test_get_all_books(client, fake_book_service, fake_session):
    fake_book_service.get_all_books = AsyncMock(return_value=[])

    response = client.get(BOOKS_PREFIX)

    assert response.status_code == 200
    assert response.json() == []
    fake_book_service.get_all_books.assert_awaited_once_with(fake_session)


def test_create_book(client, fake_book_service, fake_session):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "language": "English",
    }
    now = datetime.now(timezone.utc).isoformat()
    created_book = {
        "uid": str(UUID("5a4f1871-cb6f-4da0-85c4-655d4e3f73e8")),
        **book_data,
        "created_at": now,
        "updated_at": now,
    }
    fake_book_service.create_book = AsyncMock(return_value=created_book)

    response = client.post(BOOKS_PREFIX, json=book_data)

    assert response.status_code == 201
    assert response.json()["title"] == book_data["title"]
    assert response.json()["author"] == book_data["author"]
    fake_book_service.create_book.assert_awaited_once_with(
        BookCreateModel(**book_data), "test-user-uid", fake_session
    )