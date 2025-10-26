# Godot Integration Notes

Use `HTTPRequest` (or `HTTPClient`) to communicate with the FastAPI backend running at `http://127.0.0.1:8000`.

## Endpoints Recap
- `POST /ai/generate` — convert player text into hierarchical todos (see `docs/API.md`). Set `save=false` to preview quests without mutating backend state.
- `GET /todos/tree` — fetch nested quest trees for rendering.
- `POST /memory/search` — semantic recall for contextual suggestions.
- `GET /health`, `GET /ready` — lightweight health/readiness checks for boot gating.

## Example: Fetch Todo Tree
```gdscript
@onready var http := $HTTPRequest

func _ready():
    http.request_completed.connect(_on_tree)
    http.request("http://127.0.0.1:8000/todos/tree")

func _on_tree(result, response_code, _headers, body):
    if response_code != 200:
        push_error("Backend error %s" % response_code)
        return
    var payload = JSON.parse_string(body.get_string_from_utf8())
    render_tree(payload["todos"])
```

## Offline / Mock Workflow
- Run the real backend with `MOCK_AI_RESPONSES_FILE` set (default points to `backends/mocks/ai_generate_sample.json`). This lets `/ai/generate` respond without calling OpenRouter.
- Alternatively, start the lightweight mock server: `uv run python scripts/run_mock_server.py` (serves on port 8001).
- Load demo data via `uv run python scripts/load_demo_data.py data/demo_tasks.json --reset` to ensure the tree endpoint returns useful content.

## Error Handling Tips
- Non-200 responses will include `{ "detail": ... }`; surface these in-game for debugging.
- Use the `/ready` endpoint during Godot startup to ensure the backend has finished booting/migrations before sending gameplay-critical requests.
