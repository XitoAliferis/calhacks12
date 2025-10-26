# CalHacks12 Task Game

This repo houses the Godot game plus a Python backend that turns player intents into structured quest trees powered by Claude via OpenRouter.

## Repo Layout
- `scenes/`, `scripts/`, `assets/` – Godot project files (see `project.godot`).
- `backends/` – FastAPI service (`app/`, `pyproject.toml`, `.env.template`).
- `docs/` – Additional documentation (`API.md`, `Postman.md`, sponsor info).

## Backend Setup & Run
1. **Install prerequisites**
   - Python 3.10+
   - [uv](https://docs.astral.sh/uv/)
2. **Install dependencies**
   ```bash
   cd backends
   uv sync --extra dev
   ```
3. **Configure environment**
   ```bash
   cp .env.template .env
   $EDITOR .env  # set OPENROUTER_API_KEY, rate limit prefs, optional mock file
   ```
   > Tip: you do **not** run `.env` as a command—either trust FastAPI to load it automatically or run `set -a; source .env; set +a` if you need the vars in your shell session.
4. **Optional helpers**
   - Seed demo data: `uv run python scripts/load_demo_data.py data/demo_tasks.json --reset`
   - Evaluate prompts: `uv run python scripts/eval_prompt.py data/sample_prompts.json`
   - Serve mock-only backend: `uv run python scripts/run_mock_server.py`
5. **Launch the API**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
6. **Validate**: open http://127.0.0.1:8000/docs or hit `/ready`.

## Frontend (Godot) Integration
- Use `HTTPRequest` nodes to call backend endpoints documented in `docs/API.md`.
- For local testing, keep the FastAPI server running and point HTTP requests to `http://127.0.0.1:8000`.

## Testing APIs
- Follow `docs/API.md` for endpoint contracts and `docs/Postman.md` for a ready-to-run Postman collection setup.
- `docs/GodotIntegration.md` shows sample GDScript for hitting the backend (plus mock workflow notes).
- Run `uv run pytest` inside `backends/` to execute the growing unit-test suite.

## Backend via Docker
```bash
cd backends
docker build -t ai-backend .
docker run --env-file .env -p 8000:8000 ai-backend
```

## Contributing
1. Create a feature branch.
2. Make changes (respecting existing Godot and backend structures).
3. Run backend/unit tests (when available) and manual API checks.
4. Submit a PR referencing relevant TODO items.
- Need something instant? Import `docs/PostmanCollection.json` into Postman to get all endpoints wired to `{{base_url}}`.
