#!/usr/bin/env python3
"""Load demo todos into the local SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from sqlmodel import delete

from app import models, schemas
from app.database import session_scope, init_db
from app.services import todo_service


def load_payload(path: Path) -> list[schemas.GeneratedTodoNode]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text())
    nodes = data.get("todos", []) if isinstance(data, dict) else data
    return [schemas.GeneratedTodoNode(**node) for node in nodes]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo tasks into SQLite")
    parser.add_argument("payload", type=Path, help="Path to demo JSON (see data/demo_tasks.json)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing todos before inserting demo data",
    )
    args = parser.parse_args()

    init_db()
    nodes = load_payload(args.payload)
    with session_scope() as session:
        if args.reset:
            session.exec(delete(models.TodoItem))
            session.commit()
        todo_service.save_generated_tree(nodes, session)
    print(f"Inserted {len(nodes)} root tasks from {args.payload}")


if __name__ == "__main__":
    main()
