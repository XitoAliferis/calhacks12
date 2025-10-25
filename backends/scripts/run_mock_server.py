#!/usr/bin/env python3
"""Serve static responses that mirror the real backend for frontend prototyping."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
MOCK_DIR = ROOT / "mocks"

app = FastAPI(title="Mock AI Task Backend")


def _load(name: str) -> dict:
    path = MOCK_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "mock"}


@app.post("/ai/generate")
def mock_ai_generate():
    return _load("ai_generate_sample.json")


@app.get("/todos/tree")
def mock_tree():
    return _load("todo_tree_sample.json")


@app.get("/todos")
def mock_todos():
    tree = _load("todo_tree_sample.json")
    flat = []
    stack = tree["todos"]
    while stack:
        node = stack.pop(0)
        flat.append({k: v for k, v in node.items() if k != "children"})
        stack.extend(node.get("children", []))
    return flat


@app.post("/memory/search")
def mock_memory_search():
    return _load("memory_search_sample.json")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
