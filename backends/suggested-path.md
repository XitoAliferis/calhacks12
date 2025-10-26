Here’s a complete developer documentation for your AI Task Manager backend, ready to send to another engineer to implement using uv, FastAPI, SQLModel, ChromaDB, and OpenRouter.

⸻

🧠 AI Task Manager Backend — Developer Documentation

Goal:
Provide a modular, extensible backend service that transforms user text into a structured, hierarchical to-do list using an LLM (Claude via OpenRouter), stores it persistently in SQLite, embeds it in ChromaDB for semantic memory, and exposes a clean REST API that the Godot front-end can consume.

⸻

🚀 1. Tech Stack

Component	Technology	Purpose
Runtime & Env Mgmt	uv (Astral)	Fast Python environment manager & runner
Web Framework	FastAPI	REST API endpoints
ORM / DB	SQLModel (SQLite)	Task persistence with schema enforcement
Config	pydantic-settings	Environment configuration & secrets
LLM Access	OpenAI SDK via OpenRouter	Use Claude 3.5 Haiku or any model
Vector DB	ChromaDB + SentenceTransformer	Embedding-based memory and search
Front-end Client	Godot HTTPRequest	Communicates with this API


⸻

⚙️ 2. Directory Structure

backends/
│
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Env vars via pydantic-settings
│   ├── database.py          # SQLModel engine + init
│   ├── models.py            # TodoItem (recursive model)
│   ├── schemas.py           # Pydantic schemas for I/O
│   │
│   ├── services/
│   │   ├── ai_service.py      # LLM calls through OpenRouter
│   │   ├── todo_service.py    # CRUD + tree reconstruction
│   │   └── chroma_service.py  # Vector embeddings + search
│   │
│   ├── api/
│   │   ├── routes_todos.py    # /todos endpoints
│   │   ├── routes_ai.py       # /ai/generate endpoint
│   │   └── routes_memory.py   # /memory/search endpoint
│   │
│   └── __init__.py
│
├── data/                  # Demo prompts + seed payloads
├── mocks/                 # Static responses for offline testing
├── scripts/               # CLI helpers (seed, eval, mock server)
├── migrations/            # Alembic config for SQLModel schema changes
├── tests/                 # Pytest suite for services
├── .env.template
├── pyproject.toml
└── README.md


⸻

🔧 3. Environment Variables (.env.template)

Everything configurable lives here — no hard-coding in code.

# LLM / API
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-haiku

# Database
DB_URL=sqlite:///todos.db

# Embeddings
CHROMA_DIR=./chroma_data
EMBEDDING_MODEL=all-MiniLM-L6-v2

# App mode
DEBUG=true


⸻

🧠 4. Key Modules and What They Do

config.py

Loads all variables using pydantic-settings.

from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    DEFAULT_MODEL: str
    DB_URL: str
    CHROMA_DIR: str
    EMBEDDING_MODEL: str
    DEBUG: bool = True
    class Config: env_file = ".env"
settings = Settings()


⸻

database.py

Initializes the SQLModel engine.

from sqlmodel import SQLModel, create_engine
from app.config import settings

engine = create_engine(settings.DB_URL, echo=settings.DEBUG)
def init_db():
    from app.models import TodoItem
    SQLModel.metadata.create_all(engine)


⸻

models.py (Recursive Todo Schema)

Defines a self-referential task model for tree structure.

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TodoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = "Untitled Task"
    reason: Optional[str] = None
    priority: str = "medium"     # high | medium | low
    status: str = "pending"      # pending | in-progress | done
    deadline: Optional[datetime] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="todoitem.id")


⸻

schemas.py

Defines I/O formats.

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TodoCreate(BaseModel):
    title: str
    reason: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    deadline: Optional[datetime] = None
    parent_id: Optional[int] = None

class TodoRead(TodoCreate):
    id: int
    subitems: List["TodoRead"] = []


⸻

ai_service.py

Connects to OpenRouter using OpenAI SDK grammar:

from openai import OpenAI
from app.config import settings
import json

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)

def generate_todos(prompt: str):
    """Ask Claude via OpenRouter to return structured JSON tasks."""
    system = (
        "You are a productivity planner. Return valid JSON:\n"
        '{"summary":"","todos":[{"title":"","reason":"","priority":"","status":"","deadline":null,"subitems":[]}]}'
    )
    completion = client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)


⸻

chroma_service.py

Adds memory via embeddings.

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import settings

client = chromadb.Client(Settings(persist_directory=settings.CHROMA_DIR))
collection = client.get_or_create_collection("todos")
embedder = SentenceTransformer(settings.EMBEDDING_MODEL)

def add_task(todo_id: int, title: str, reason: str | None):
    doc = f"{title}. {reason or ''}"
    vec = embedder.encode([doc])[0].tolist()
    collection.add(ids=[str(todo_id)], documents=[doc], embeddings=[vec])

def search_memory(query: str, n_results=5):
    qv = embedder.encode([query])[0].tolist()
    return collection.query(query_embeddings=[qv], n_results=n_results)


⸻

todo_service.py

CRUD logic and recursive builder.

from sqlmodel import Session, select
from app.models import TodoItem
from app.database import engine
from app.services import chroma_service

def create(todo: TodoItem):
    with Session(engine) as s:
        s.add(todo); s.commit(); s.refresh(todo)
        chroma_service.add_task(todo.id, todo.title, todo.reason)
        return todo

def read_tree():
    with Session(engine) as s:
        rows = s.exec(select(TodoItem)).all()
    tree = {}
    for r in rows:
        tree.setdefault(r.parent_id, []).append(r)
    def build(node):
        return {
            "id": node.id, "title": node.title, "status": node.status,
            "priority": node.priority, "deadline": node.deadline,
            "subitems": [build(c) for c in tree.get(node.id, [])],
        }
    return [build(r) for r in tree.get(None, [])]


⸻

api/routes_todos.py

REST routes for CRUD.

from fastapi import APIRouter
from app.services import todo_service
from app.models import TodoItem

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.get("/tree")
def get_tree(): return {"todos": todo_service.read_tree()}

@router.post("/")
def create(todo: dict): return todo_service.create(TodoItem(**todo))


⸻

api/routes_ai.py

Endpoint for AI generation.

from fastapi import APIRouter
from app.services.ai_service import generate_todos

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/generate")
def generate(req: dict):
    """
    Body: { "user_input": "...", "model": "optional", "save": true }
    """
    return generate_todos(req.get("user_input", ""))


⸻

api/routes_memory.py

Endpoint for Chroma search.

from fastapi import APIRouter
from app.services import chroma_service

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.post("/search")
def search(req: dict):
    return chroma_service.search_memory(req.get("query", ""))


⸻

main.py

Bootstraps everything.

from fastapi import FastAPI
from app.database import init_db
from app.api import routes_todos, routes_ai, routes_memory

app = FastAPI(title="AI Task Backend")
app.include_router(routes_todos.router)
app.include_router(routes_ai.router)
app.include_router(routes_memory.router)

@app.on_event("startup")
def on_startup(): init_db()


⸻

🌐 5. REST API Design

Endpoint	Method	Description	Example
/ai/generate	POST	Convert natural language → structured to-do list	{ "user_input": "Plan my finals week", "save": true }
/todos	POST	Create new task	{ "title": "Write essay", "priority": "high" }
/todos/tree	GET	Get nested tasks	→ { "todos": [ { "title":..., "subitems":[] } ] }
/todos/{id}	PUT	Update	{ "status": "done" }
/todos/{id}	DELETE	Delete by id	—
/memory/search	POST	Semantic search	{ "query": "study tasks" }


⸻

🎮 6. Godot Connection Guide (Frontend Integration)

Your teammate only needs to use Godot’s HTTPRequest node to call these REST endpoints.

Example: Fetch task tree

@onready var http = $HTTPRequest

func _ready():
    http.request_completed.connect(_on_done)
    http.request("http://127.0.0.1:8000/todos/tree")

func _on_done(result, code, headers, body):
    if code != 200: return
    var data = JSON.parse_string(body.get_string_from_utf8())
    var todos = data["todos"]
    # Render tasks recursively

Example: Generate tasks with Claude

func ai_generate(prompt: String):
    var headers = ["Content-Type: application/json"]
    var body = {"user_input": prompt, "save": true}
    http.request("http://127.0.0.1:8000/ai/generate", headers, HTTPClient.METHOD_POST, JSON.stringify(body))

Example: Mark task as done

func mark_done(id: int):
    var headers = ["Content-Type: application/json"]
    var body = {"status": "done"}
    http.request("http://127.0.0.1:8000/todos/%d" % id, headers, HTTPClient.METHOD_PUT, JSON.stringify(body))


⸻

🧩 7. Design Choices Recap

Aspect	Choice	Reason
Environment manager	uv	Lightweight, fast dependency management
Framework	FastAPI	Easy async REST + OpenAPI docs
Config system	pydantic-settings	Strong typing, automatic .env parsing
Database	SQLModel (SQLite)	Minimal local persistence
Vector memory	ChromaDB	Local embedding search
LLM Provider	OpenRouter (Claude 3.5 Haiku default)	Flexibility across models
API style	REST	Simpler for Godot integration
Recursion	parent_id links	Easy to build nested tree of tasks
JSON Schema	Hierarchical with subitems	AI-compatible and UI-friendly


⸻

🧭 8. Run Instructions

# 1. Install deps
uv add fastapi uvicorn sqlmodel pydantic-settings openai chromadb sentence-transformers

# 2. Run server
uv run uvicorn app.main:app --reload

# 3. Open docs
http://127.0.0.1:8000/docs


⸻

✅ 9. Summary

This backend provides:
	•	LLM-driven to-do generation (Claude via OpenRouter)
	•	Hierarchical task storage (SQLite)
	•	Semantic memory search (ChromaDB)
	•	Clean REST API (FastAPI)
	•	Fully configurable via .env
	•	Ready-to-use with Godot HTTPRequest

It’s modular, simple to extend, and follows the REST-first, local-first, agent-ready design we defined earlier.
