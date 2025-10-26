# AI Task Backend API

Base URL (local dev): `http://127.0.0.1:8000`
OpenAPI docs: `http://127.0.0.1:8000/docs`

Authentication: none (trusted local network). Add an auth layer before production.

## Health
- **GET** `/health`
- **Response** `200 OK`
```json
{"status":"ok","debug":"true"}
```
- **GET** `/ready`
- **Response** `200 OK` when DB + dependencies are reachable.
```json
{"status":"ready"}
```

## AI Generation
- **POST** `/ai/generate`
- **Body**
```json
{
  "user_input": "Help me plan finals week",
  "save": true
}
```
- **Response** `200 OK`
```json
{
  "todos": [
    {
      "title": "Map finals schedule",
      "reason": "See study load",
      "priority": "high",
      "status": "pending",
      "deadline": null,
      "subitems": [
        {"title": "List exam dates", "reason": null, "priority": "medium", "status": "pending", "deadline": null, "subitems": []}
      ]
    }
  ],
  "persisted_ids": [1, 2]
}
```
- When `save=false`, the todos list is returned without writing to SQLite/Chroma.

## Todos Collection
### Create Todo
- **POST** `/todos`
- **Body** matches `TodoCreate`
```json
{
  "title": "Write essay",
  "priority": "high",
  "status": "pending",
  "reason": "Due Friday",
  "deadline": "2024-10-20T18:00:00",
  "parent_id": null
}
```
- **Response** `201 Created` with stored todo.

### List Todos
- **GET** `/todos`
- **Query Params (optional)**:
  - `status` ∈ `pending|in-progress|done`
  - `priority` ∈ `low|medium|high`
  - `due_before` ISO timestamp filter (inclusive)
  - `due_after` ISO timestamp filter (inclusive)
- **Response** `200 OK` array of flat todos that match the filters.

### Update Todo
- **PUT** `/todos/{id}`
- Supply partial fields to update. Example body:
```json
{
  "status": "done"
}
```
- **Response** `200 OK` updated todo.

### Delete Todo
- **DELETE** `/todos/{id}`
- **Response** `204 No Content`

### Complete Todo
- **POST** `/todos/{id}/complete`
- Marks the task’s `status` as `done` and returns the updated record.
- **Response** `200 OK`

## Todo Tree
- **GET** `/todos/tree`
- Returns nested nodes keyed by `children` for building quest trees in Godot.
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Parent",
      "children": [
        {"id": 2, "title": "Child", "children": []}
      ]
    }
  ]
}
```

## Memory Search
- **POST** `/memory/search`
- **Body**
```json
{
  "query": "study"
}
```
- **Response** `200 OK`
```json
{
  "results": [
    {"id": 8, "title": "Study calculus", "reason": "Exam Monday", "score": 0.16}
  ]
}
```
- Results come from ChromaDB semantic similarity and can be used to surface related quests.

## Rate Limits
- Local/dev rate limiting is enabled (default 60 requests per 60 seconds per IP). Requests beyond the limit return `429 Too Many Requests`.
