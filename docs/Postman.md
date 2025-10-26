# Testing the API with Postman

These steps assume you have Postman Desktop or Postman Web set up.

## 1. Create an Environment
1. Click **Environments → + New Environment**.
2. Add variables:
   - `base_url` = `http://127.0.0.1:8000`
   - `auth_token` (optional placeholder if auth is added later).
3. Save as `AI Todo Backend`.

## 2. Build a Collection
1. Click **Collections → + New Collection** named `AI Task Backend`.
2. Set the collection to use the `AI Todo Backend` environment.
3. Add the following requests:

### Health / Ready
- Method: `GET`
- URL: `{{base_url}}/health`
- Tests: `pm.response.code === 200`.

- Method: `GET`
- URL: `{{base_url}}/ready`
- Tests: ensure `pm.response.json().status === "ready"`.

### Generate Todos
- Method: `POST`
- URL: `{{base_url}}/ai/generate`
- Body: raw JSON
```json
{
  "user_input": "Plan my demo day",
  "save": true
}
```
- Tests: verify status `200` and `persisted_ids` array exists.

### Create Todo
- Method: `POST`
- URL: `{{base_url}}/todos`
- Body example:
```json
{
  "title": "Record trailer",
  "reason": "Marketing team needs footage",
  "priority": "high",
  "status": "pending",
  "deadline": null,
  "parent_id": null
}
```

### Update Todo
- Method: `PUT`
- URL: `{{base_url}}/todos/{id}`
- Body contains only the fields you want to change (e.g. `{ "status": "in-progress" }`).

### Delete Todo
- Method: `DELETE`
- URL: `{{base_url}}/todos/{id}`

### Complete Todo
- Method: `POST`
- URL: `{{base_url}}/todos/{id}/complete`
- No body required; sets the status to `done`.

### Get Todo Tree
- Method: `GET`
- URL: `{{base_url}}/todos/tree`
- Tests: ensure `pm.response.json().todos.length > 0`.

### Filter Todos
- Method: `GET`
- URL: `{{base_url}}/todos?status=pending&priority=high`
- Tests: `pm.response.code === 200`.

### Memory Search
- Method: `POST`
- URL: `{{base_url}}/memory/search`
- Body:
```json
{
  "query": "marketing"
}
```

## 3. Send Requests
1. Start the backend server (`uv run uvicorn app.main:app --reload`).
2. In Postman, select the environment, open a request, and click **Send**.
3. Use the **Console** to inspect logs/responses; errors will show stack traces from FastAPI.

## 4. Automate Testing (Optional)
- Use the **Runner** to execute the collection after each backend change.
- Export the collection/env (⋮ → Export) and commit the JSON under `docs/postman/` if you want to share with teammates.

## 5. Offline Mode
- Start the mock backend: `uv run python scripts/run_mock_server.py` (listens on port `8001`).
- Point the Postman environment `base_url` to `http://127.0.0.1:8001` to exercise deterministic fixtures with no LLM/DB dependencies.

## 6. Import Ready-Made Collection
- Copy the entire JSON from `docs/PostmanCollection.json` and import it directly in Postman (`Import → Raw text`).
- The collection ships with the same requests described above and defaults `base_url` to `http://127.0.0.1:8000`.
- Working with the MCP HTTP bridge? Import `docs/PostmanMCP.json`, set `mcp_base_url` (default `http://127.0.0.1:8766`), and start the bridge with `uv run python backends/app/mcp_server.py --transport http --port 8766`. Each request sends a JSON-RPC payload to `/mcp` (FastMCP’s HTTP endpoint) with `Accept: application/json, text/event-stream` to satisfy the protocol requirements before calling `ai_generate`, `todo_tree`, or `memory_search`.
