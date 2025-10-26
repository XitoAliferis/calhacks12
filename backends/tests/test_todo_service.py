from __future__ import annotations

from datetime import datetime

from app import schemas
from app.services import todo_service


def test_create_and_filter(session):
    todo_service.create_todo(
        schemas.TodoCreate(
            title="Write pitch",
            status="pending",
            priority="high",
            deadline=datetime(2024, 10, 20, 18, 0, 0),
        ),
        session,
    )
    todo_service.create_todo(
        schemas.TodoCreate(
            title="Polish UI",
            status="done",
            priority="low",
        ),
        session,
    )

    pending = todo_service.list_todos(session, status_filter="pending")
    assert len(pending) == 1
    assert pending[0].title == "Write pitch"

    high_priority = todo_service.list_todos(session, priority_filter="high")
    assert len(high_priority) == 1
    assert high_priority[0].status == "pending"

    due_before = todo_service.list_todos(session, due_before=datetime(2024, 10, 21))
    assert len(due_before) == 1

    due_after = todo_service.list_todos(session, due_after=datetime(2024, 10, 21))
    assert len(due_after) == 0


def test_tree_reconstruction(session):
    payload = [
        schemas.GeneratedTodoNode(
            title="Parent",
            reason=None,
            priority="medium",
            status="pending",
            subitems=[
                schemas.GeneratedTodoNode(
                    title="Child",
                    reason=None,
                    priority="low",
                    status="pending",
                    subitems=[],
                )
            ],
        )
    ]
    todo_service.save_generated_tree(payload, session)

    tree = todo_service.get_tree(session)
    assert len(tree) == 1
    assert tree[0].children
    assert tree[0].children[0].title == "Child"


def test_complete_todo(session):
    todo = todo_service.create_todo(
        schemas.TodoCreate(title="Complete me", status="pending"),
        session,
    )
    updated = todo_service.complete_todo(todo.id, session)
    assert updated.status == "done"
