# Tags API: `/api/v1/tags`

All routes require a valid access token and the role `user` or `admin`.

| Method | Path | Description |
|---|---|---|
| GET | `/` | List all tags (newest first) |
| POST | `/` | Create a tag; `TagAlreadyExists` if the name is taken |
| POST | `/book/{book_uid}/tags` | Attach tags to a book (tags are created if missing) |
| PUT | `/{tag_uid}` | Rename a tag |
| DELETE | `/{tag_uid}` | Delete a tag (returns `204`) |

```json
// POST /tags/book/{book_uid}/tags  (TagAddModel)
{ "tags": [ { "name": "science-fiction" }, { "name": "classic" } ] }
```

| Schema | Fields |
|---|---|
| `TagModel` | `uid`, `name`, `created_at` |
| `TagCreateModel` | `name` |
| `TagAddModel` | `tags: List[TagCreateModel]` |
