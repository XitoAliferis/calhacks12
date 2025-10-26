# AI Task Backend

Backend services that turn free-form intents into hierarchical quests, persist them with SQLModel/SQLite + ChromaDB, and expose both REST + MCP interfaces for Godot, Creao, and agent flows.

---

## 1. Setup & Installation
1. **Prereqs**
   - Python 3.10+
   - [uv](https://docs.astral.sh/uv/) package manager
2. **Install deps**
   ```bash
   cd backends
   uv sync  # installs runtime + dev extras
   ```
3. **Configure env**
   ```bash
   cp .env.template .env
   $EDITOR .env  # fill OPENROUTER_API_KEY, DB path, rate limits, etc.
   ```
   > FastAPI loads `.env` automatically; only `set -a; source .env; set +a` if you need the vars in your shell.

Directory highlights:
```
app/        # FastAPI + MCP code
scripts/    # CLI helpers (seed/eval/mock/stack)
data/       # Demo payloads
mocks/      # Static responses for frontend-only testing
tests/      # pytest suite
```

---

## 2. FastAPI Service (REST)
- Launch: `uv run uvicorn app.main:app --reload` (docs at http://127.0.0.1:8000/docs).
- Seed demo data: `uv run python scripts/load_demo_data.py data/demo_tasks.json --reset`.
- Mock AI without OpenRouter: set `MOCK_AI_RESPONSES_FILE` or run `uv run python scripts/run_mock_server.py`.
- Reference contracts + Postman flows live in `docs/API.md`, `docs/Postman.md`, and `docs/PostmanCollection.json`.

Core endpoints: `/ai/generate`, `/todos`, `/todos/tree`, `/memory/search`, `/health`, `/ready`.

---

## 3. MCP Bridge (Agents)
- Stdio (agent runtimes): `uv run python -m app.mcp_server --transport stdio`.
- HTTP (curl/Postman): `uv run python -m app.mcp_server --transport http --host 127.0.0.1 --port 8766` then send JSON-RPC POSTs to `http://127.0.0.1:8766/mcp` with:
  - `Content-Type: application/json`
  - `Accept: application/json, text/event-stream`

Docs & tool catalog: `docs/MCPGuide.md` (also exposed as `mcp://docs/mcp-guide`). `docs/PostmanMCP.json` imports directly into Postman.

Available tools mirror the REST surface (`health`, `ai_generate`, `create_todo`, `list_todos`, `update_todo`, `delete_todo`, `todo_tree`, `memory_search`). Resources also expose `docs/API.md` for agent reference.

Try it interactively with the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector uv run python -m app.mcp_server --transport stdio
```

---

## 4. One-Command Stack Scripts
Located under `scripts/`:
- `start_stack.sh` – runs FastAPI (`uv run uvicorn ...`) + MCP HTTP (`uv run python -m app.mcp_server --transport http --port 8766`) simultaneously, logs to `.logs/`, stores PIDs in `.stack_pids`.
- `stop_stack.sh` – reads `.stack_pids`, stops both processes cleanly.

Use these from the `backends/` directory:
```bash
cd backends
scripts/start_stack.sh
# ...
scripts/stop_stack.sh
```

---

## 5. Testing & Tooling
- Unit tests: `uv run pytest` (see `tests/` for service coverage).
- Lint: `uv run ruff check`.
- Type checking: `uv run mypy app`.
- Alembic migrations: `uv run alembic revision --autogenerate -m "msg"` / `uv run alembic upgrade head`.
- Postman: import `docs/PostmanCollection.json` (REST) or `docs/PostmanMCP.json` (MCP) per `docs/Postman.md`.

---

## 6. Integration Notes
- Godot clients hit the REST interface (`docs/GodotIntegration.md`).
- Agents / Creao connect through MCP via stdio or HTTP.
- For offline demos, rely on mock data + `MOCK_AI_RESPONSES_FILE`.

Further architecture details live in `backends/suggested-path.md` and `docs/MCPGuide.md`.
