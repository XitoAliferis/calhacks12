# Backend & Integration TODOs

## 🔥 Immediate (Backend Foundations)
- [x] Finalize `backends/app` FastAPI scaffold with config + dependency metadata (pyproject)
- [x] Define SQLModel schema for hierarchical todos plus CRUD service layer
- [x] Implement ChromaDB persistence utilities (client init, add/update/delete, search API)
- [x] Ship initial `/ai/generate`, `/todos`, `/memory/search` routes wired to services
- [x] Provide `.env.template` and bootstrap README for local setup instructions (uv + uvicorn)

## 🤖 AI & Semantics
- [x] Implement OpenRouter Claude client helper with retry/backoff + request/response logging
- [x] Design prompt template that outputs deterministic hierarchical task JSON
- [x] Persist AI generations into SQL + Chroma when `save=true`
- [x] Add evaluation script/examples for prompt + response validation (`scripts/eval_prompt.py` + `data/sample_prompts.json`)

## 🧠 Data & Persistence
- [x] Migrate existing demo data (if any) into SQLite using SQLModel fixtures (`scripts/load_demo_data.py`)
- [x] Expose `/todos/tree` endpoint that reconstructs nested subtasks efficiently
- [x] Add search filters (status, priority, deadline) layered over SQL queries
- [x] Create Alembic or lightweight migration story (optional if schema churn expected) (`alembic.ini` + `migrations/`)

## 🎮 Godot Integration
- [x] Document REST contracts (request/response JSON) for Godot team (`docs/API.md`, `docs/GodotIntegration.md`)
- [x] Build mock server responses or fixtures for frontend testing without LLM (`mocks/`, `scripts/run_mock_server.py`)
- [x] Add CORS + rate limiting config for local dev hot reload (CORS + custom middleware)

## 🧪 Tooling & Ops
- [x] Unit tests for services (todo_service, ai_service, chroma_service)
- [x] Healthcheck + readiness endpoints for game runtime (`/health`, `/ready`)
- [x] Containerize backend (Dockerfile) for deployment handoff
- [x] CI workflow (GitHub Actions) running tests + lint + type checks
