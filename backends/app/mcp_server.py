"""MCP server exposing AI Task backend capabilities for Creao + agent integrations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import fastmcp
from fastmcp import FastMCP

from app import models, schemas
from app.config import settings
from app.database import session_scope
from app.services import ai_service, chroma_service, todo_service


def _todo_to_dict(todo: models.TodoItem) -> dict[str, Any]:
    """Normalize SQLModel row into JSON-safe dict."""
    payload = schemas.TodoRead.model_validate(todo)
    return payload.model_dump(mode="json")


def _tree_to_dict(tree: list[schemas.TodoTreeNode]) -> list[dict[str, Any]]:
    return [node.model_dump(mode="json") for node in tree]


def _generated_to_dict(nodes: list[schemas.GeneratedTodoNode]) -> list[dict[str, Any]]:
    return [node.model_dump(mode="json") for node in nodes]


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

# Configure FastMCP HTTP transport for simple JSON responses + stateless requests
fastmcp.settings.json_response = True
fastmcp.settings.stateless_http = True


mcp = FastMCP(
    name="ai-task-backend",
    version="0.1.0",
    instructions=(
        "Expose AI Task backend operations (todo CRUD, AI generation, semantic search) as MCP tools. "
        "Use these tools to orchestrate task planning flows across Godot, Creao, or any MCP-compatible agent."
    ),
)


def health() -> dict[str, str]:
    return {"status": "ok", "debug": str(settings.DEBUG).lower()}


def ai_generate(user_input: str, save: bool = False) -> dict[str, Any]:
    todos = ai_service.generate_structured_todos(user_input)
    persisted: list[int] = []
    if save:
        with session_scope() as session:
            created = todo_service.save_generated_tree(todos, session)
            persisted = [todo.id for todo in created]
    return {
        "todos": _generated_to_dict(todos),
        "persisted_ids": persisted,
    }


def create_todo(todo: dict[str, Any]) -> dict[str, Any]:
    payload = schemas.TodoCreate(**todo)
    with session_scope() as session:
        record = todo_service.create_todo(payload, session)
        return _todo_to_dict(record)


def list_todos(
    status: schemas.Status | None = None,
    priority: schemas.Priority | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
) -> list[dict[str, Any]]:
    parsed_before = schemas.TodoUpdate(deadline=due_before).deadline if due_before else None
    parsed_after = schemas.TodoUpdate(deadline=due_after).deadline if due_after else None
    with session_scope() as session:
        records = todo_service.list_todos(
            session,
            status_filter=status,
            priority_filter=priority,
            due_before=parsed_before,
            due_after=parsed_after,
        )
        return [_todo_to_dict(record) for record in records]


def update_todo(todo_id: int, fields: dict[str, Any]) -> dict[str, Any]:
    payload = schemas.TodoUpdate(**fields)
    with session_scope() as session:
        record = todo_service.update_todo(todo_id, payload, session)
        return _todo_to_dict(record)


def delete_todo(todo_id: int) -> dict[str, Any]:
    with session_scope() as session:
        todo_service.delete_todo(todo_id, session)
    return {"status": "deleted", "id": todo_id}


def todo_tree() -> list[dict[str, Any]]:
    with session_scope() as session:
        tree = todo_service.get_tree(session)
        return _tree_to_dict(tree)


def memory_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    results = chroma_service.search_memory(query, limit=limit)
    return results


mcp.tool(description="Health probe mirroring FastAPI /health")(health)
mcp.tool(description="Generate hierarchical todos via Claude/OpenRouter")(ai_generate)
mcp.tool(description="Create a single todo node")(create_todo)
mcp.tool(description="List todos with optional filters")(list_todos)
mcp.tool(description="Update a todo by id")(update_todo)
mcp.tool(description="Delete a todo by id")(delete_todo)
mcp.tool(description="Return the nested todo tree")(todo_tree)
mcp.tool(description="Semantic task search backed by ChromaDB embeddings")(memory_search)


@mcp.resource("mcp://docs/api", description="REST contract for the AI Task backend")
def api_docs() -> str:
    path = REPO_ROOT / "docs" / "API.md"
    return path.read_text(encoding="utf-8")


@mcp.resource("mcp://docs/mcp-guide", description="How to run and use the MCP bridge")
def mcp_guide() -> str:
    path = REPO_ROOT / "docs" / "MCPGuide.md"
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI Task MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol. Use stdio for local agents, http for remote clients.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transports")
    parser.add_argument("--port", type=int, default=8766, help="Port for HTTP transports")
    args = parser.parse_args()

    transport_kwargs: dict[str, Any] = {}
    if args.transport != "stdio":
        transport_kwargs.update({"host": args.host, "port": args.port})

    mcp.run(transport=args.transport, **transport_kwargs)


if __name__ == "__main__":
    main()
