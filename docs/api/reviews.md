# Reviews API: `/api/v1/reviews`

| Method | Path | Authentication | Description |
|---|---|---|---|
| POST | `/book/{book_uid}` | Access token (`get_current_user`) | Add a review to a book |

```json
// ReviewCreateModel
{ "rating": 5, "review_text": "A masterpiece." }
```

| Schema | Fields |
|---|---|
| `ReviewModel` | `uid`, `rating`, `review_text`, `user_uid?`, `book_uid?`, `created_at`, `updated_at` |
| `ReviewCreateModel` | `rating` (1 to 5), `review_text` |
