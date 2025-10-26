# AI Task Backend

FastAPI backend that turns free-form player intents into hierarchical to-do trees using Claude via OpenRouter, persists tasks in SQLite via SQLModel, and stores embeddings in ChromaDB for semantic recall.

## Quickstart

```bash
# 0. From repo root, drop into the backend workspace
cd backends

# 1. Ensure uv is installed (https://docs.astral.sh/uv/)
uv sync  # installs deps declared in pyproject

# 2. Provide secrets
cp .env.template .env && $EDITOR .env
# (don't execute `.env`; FastAPI reads it automatically. If you need the vars in your shell, run `set -a; source .env; set +a`.)

# 3. Run the API
uv run uvicorn app.main:app --reload
```

Docs are available at http://127.0.0.1:8000/docs when the server is running.

## Project Layout

```
app/
  api/            # REST routes grouped by concern
  services/       # LLM, todo, chroma helpers
  config.py       # Settings loader (.env)
  database.py     # SQLModel engine + session helpers
  main.py         # FastAPI bootstrapper + rate limiting/health
data/             # Demo prompts + seed todos
mocks/            # Static responses for frontend testing
scripts/          # CLI helpers (seeding, evaluation, mock server)
tests/            # Pytest suite
```

## Helpful Commands
- Seed demo data: `uv run python scripts/load_demo_data.py data/demo_tasks.json --reset`
- Evaluate prompts: `uv run python scripts/eval_prompt.py data/sample_prompts.json`
- Serve mock backend (no DB/LLM): `uv run python scripts/run_mock_server.py`
- Run tests: `uv run pytest`
- Lint: `uv run ruff check`
- Generate migrations: `uv run alembic revision --autogenerate -m "message"`
- Apply migrations: `uv run alembic upgrade head`

## Docker
Build and run the backend in a containerized environment:

```bash
docker build -f backends/Dockerfile -t ai-backend ./backends
docker run --env-file backends/.env -p 8000:8000 ai-backend
```

## Integration Notes
- Godot should call `/ai/generate` to turn prompts into tasks (set `save=false` for dry-run previews).
- `/todos/tree` returns a nested structure suitable for recursive UI rendering.
- `/memory/search` exposes ChromaDB semantic matches for contextual quest suggestions.
- When testing without OpenRouter access, set `MOCK_AI_RESPONSES_FILE` (defaults to `./mocks/ai_generate_sample.json`) or run the mock server script.

See `backends/suggested-path.md` for the full architecture rationale.


## Repo Layout
- `scenes/`, `scripts/`, `assets/` – Godot project files (see `project.godot`).
- `backends/` – FastAPI service (`app/`, `pyproject.toml`, `.env.template`).
- `docs/` – Additional documentation (`API.md`, `Postman.md`, sponsor info).

## Backend Setup & Run
1. **Install prerequisites**
   - Python 3.10+
   - [uv](https://docs.astral.sh/uv/) (fast package manager)
2. **Install dependencies**
   ```bash
   cd backends
   uv sync
   ```
3. **Configure environment**
   ```bash
   cp .env.template .env
   $EDITOR .env  # set OPENROUTER_API_KEY, etc.
   ```
4. **Launch the API**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
5. **Validate**: open http://127.0.0.1:8000/docs or hit `/health`.

## Frontend (Godot) Integration
- Use `HTTPRequest` nodes to call backend endpoints documented in `docs/API.md`.
- For local testing, keep the FastAPI server running and point HTTP requests to `http://127.0.0.1:8000`.

## Testing APIs
- Follow `docs/Postman.md` for a ready-to-run Postman collection setup.
- Automated tests (pytest/mocks) are planned; see `backends/TODO.md`.

## Contributing
1. Create a feature branch.
2. Make changes (respecting existing Godot and backend structures).
3. Run backend/unit tests (when available) and manual API checks.
4. Submit a PR referencing relevant TODO items.
