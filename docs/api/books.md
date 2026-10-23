# Books API: `/api/v1/books`

All routes require a valid access token and the role `user` or `admin`.

| Method | Path | Description |
|---|---|---|
| GET | `/` | List all books (newest first) |
| GET | `/user/{user_uid}` | List books submitted by a user (oldest first) |
| POST | `/` | Create a book; `user_uid` is taken from the token |
| GET | `/{book_uid}` | Book details including reviews and tags |
| PATCH | `/{book_uid}` | Partial update; refreshes `updated_at` |
| DELETE | `/{book_uid}` | Delete a book |

An unknown `book_uid` raises `BookNotFound` (404).

```json
// POST /books  (BookCreateModel)
{
  "title": "Dune",
  "author": "Frank Herbert",
  "publisher": "Chilton Books",
  "language": "English"
}
```

| Schema | Fields | Used for |
|---|---|---|
| `BookModel` | `uid`, `title`, `author`, `publisher`, `language`, `created_at`, `updated_at` | Embedded in `UserBooksModel` |
| `BookDetailModel` | `BookModel` plus `reviews`, `tags` | `GET /{book_uid}` |
| `BookCreateModel` | `title`, `author`, `publisher`, `language` | `POST /` |
| `UpdateBookModel` | Same fields, all optional | `PATCH /{book_uid}` |
| `BookResponseModel` | Same as `BookModel`, `from_attributes=True` | `GET /`, `POST /` |
