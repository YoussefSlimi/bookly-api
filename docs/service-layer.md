# Service Layer

Services are stateless classes that receive an `AsyncSession` and contain all database logic.

## `UserService` (`src/auth/service.py`)

| Method | Description |
|---|---|
| `get_user_by_email(email, session)` | Select by email; `User` or `None` |
| `get_user_by_uid(uid, session)` | Select by UUID; `User` or `None` |
| `user_exists(email, session)` | `True` if the email is taken |
| `create_user(user_data, session, role, is_verified)` | Hashes the password, removes `admin_key`, inserts the user |
| `update_user(user, user_data, session)` | Applies a dict of field updates |
| `get_all_users(session)` | All users, newest first |
| `delete_user(user, session)` | Hard-deletes the user |

## `BookService` (`src/books/service.py`)

| Method | Description |
|---|---|
| `get_all_books(session)` | All books, newest first |
| `get_user_books(user_uid, session)` | A user's books, oldest first |
| `get_book(book_uid, session)` | One book or `None` |
| `create_book(book_data, user_uid, session)` | Inserts a book owned by `user_uid` |
| `update_book(book_uid, update_data, session)` | Partial update (`exclude_unset=True`), refreshes `updated_at` |
| `delete_book(book_uid, session)` | Hard-deletes; returns `True` or `None` |

## `ReviewService` (`src/reviews/service.py`)

`add_review_to_book(user_email, book_uid, review_data, session)`:

1. Fetches the book; raises HTTP 404 if missing.
2. Fetches the user; raises HTTP 404 if missing.
3. Creates a `Review` linked to both, commits, and returns it.
4. Any unexpected exception is logged and re-raised as HTTP 500.

## `TagService` (`src/tags/service.py`)

| Method | Description |
|---|---|
| `get_tags(session)` | All tags, newest first |
| `get_tag_by_uid(tag_uid, session)` | One tag or `None` |
| `add_tag(tag_data, session)` | Creates a tag; raises `TagAlreadyExists` if the name is taken |
| `add_tags_to_book(book_uid, tag_data, session)` | For each name, finds or creates the tag and appends it to `book.tags`; raises `BookNotFound` if the book is missing |
| `update_tag(tag_uid, tag_update_data, session)` | Renames a tag; raises `TagNotFound` |
| `delete_tag(tag_uid, session)` | Deletes a tag; raises `TagNotFound` |
