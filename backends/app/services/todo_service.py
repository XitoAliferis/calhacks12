#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   todo_service.py
@Time    :   2025/10/25 16:21:45
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   Business logic for todo CRUD + tree operations.
'''


from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app import models, schemas
from app.services import chroma_service


# defining a function to coerce the deadline for the todo service.
def _coerce_deadline(raw: Optional[str | datetime]) -> Optional[datetime]:
    # if the raw is None or empty, return None.
    if raw is None or raw == "":
        return None
    # if the raw is a datetime, return it.
    if isinstance(raw, datetime):
        return raw
    # try to convert the raw to a datetime.
    try:
        # returning the datetime.
        return datetime.fromisoformat(raw)
    except ValueError as exc:  # pragma: no cover - validation should catch
        # raising an HTTP exception.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


# defining a function to create a todo for the todo service.
def create_todo(payload: schemas.TodoCreate, session: Session) -> models.TodoItem:
    # creating the todo for the todo service.
    todo = models.TodoItem(**payload.model_dump())
    # adding the todo to the session.
    session.add(todo)
    # committing the session.
    session.commit()
    # refreshing the todo.
    session.refresh(todo)
    # indexing the todo for the chroma service.
    chroma_service.index_todo(todo)
    return todo


# defining a function to update a todo for the todo service.
def update_todo(todo_id: int, payload: schemas.TodoUpdate, session: Session) -> models.TodoItem:
    # getting the todo for the todo service.
    todo = session.get(models.TodoItem, todo_id)
    if not todo:
        # raising an HTTP exception.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    # getting the update data for the todo service.
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # if the field is the deadline, coerce the deadline.
        if field == "deadline":
            value = _coerce_deadline(value)
        setattr(todo, field, value)
    # touching the todo.
    todo.touch()
    # adding the todo to the session.
    session.add(todo)
    # committing the session.
    session.commit()
    # refreshing the todo.
    session.refresh(todo)
    # indexing the todo for the chroma service.
    chroma_service.index_todo(todo)
    return todo


# defining a function to delete a todo for the todo service.
def delete_todo(todo_id: int, session: Session) -> None:
    # getting the todo for the todo service.
    todo = session.get(models.TodoItem, todo_id)
    if not todo:
        # raising an HTTP exception.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    # deleting the todo from the session.
    session.delete(todo)
    # committing the session.
    session.commit()
    # deleting the todo from the chroma service.
    chroma_service.delete_todo(todo_id)


def complete_todo(todo_id: int, session: Session) -> models.TodoItem:
    """Mark the given todo as done."""
    payload = schemas.TodoUpdate(status="done")
    return update_todo(todo_id, payload, session)


# defining a function to list todos for the todo service.
def list_todos(
    session: Session,
    *,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
) -> List[models.TodoItem]:
    # creating the statement for the todo service.
    statement = select(models.TodoItem)
    # if the status filter is set, add the status filter to the statement.
    if status_filter:
        statement = statement.where(models.TodoItem.status == status_filter)
    # if the priority filter is set, add the priority filter to the statement.
    if priority_filter:
        statement = statement.where(models.TodoItem.priority == priority_filter)
    # if the due before is set, add the due before to the statement.
    if due_before:
        statement = statement.where(models.TodoItem.deadline <= due_before)
    # if the due after is set, add the due after to the statement.
    if due_after:
        statement = statement.where(models.TodoItem.deadline >= due_after)
    # returning the list of todos.
    return list(session.exec(statement))


# defining a function to get the tree for the todo service.
def get_tree(session: Session) -> List[schemas.TodoTreeNode]:
    # getting the list of todos for the todo service.
    todos = list(session.exec(select(models.TodoItem)))
    # creating the nodes for the todo service.
    nodes: dict[int, schemas.TodoTreeNode] = {}
    for todo in todos:
        # creating the node for the todo service.
        nodes[todo.id] = schemas.TodoTreeNode(
            id=todo.id,
            title=todo.title,
            reason=todo.reason,
            priority=todo.priority,  # type: ignore[arg-type]
            status=todo.status,  # type: ignore[arg-type]
            deadline=todo.deadline,
        )

    # creating the roots for the todo service.
    roots: List[schemas.TodoTreeNode] = []
    # iterating over the todos.
    for todo in todos:
        # getting the node for the todo service.
        node = nodes[todo.id]
        # if the parent id is not None and the parent id is in the nodes, add the node to the parent's children.
        if todo.parent_id is not None and todo.parent_id in nodes:
            nodes[todo.parent_id].children.append(node)
        # otherwise, add the node to the roots.
        else:
            roots.append(node)
    return roots


# defining a function to save a generated tree for the todo service.
def save_generated_tree(nodes: Iterable[schemas.GeneratedTodoNode], session: Session) -> List[models.TodoItem]:
    # creating the list of created todos for the todo service.
    created: List[models.TodoItem] = []
    # defining a function to walk the nodes for the todo service.

    def _walk(node: schemas.GeneratedTodoNode, parent_id: Optional[int]) -> None:
        todo = models.TodoItem(
            title=node.title,
            reason=node.reason,
            priority=node.priority,
            status=node.status,
            deadline=_coerce_deadline(node.deadline),
            parent_id=parent_id,
        )
        session.add(todo)
        session.flush()
        created.append(todo)
        for child in node.subitems:
            _walk(child, todo.id)

    # iterating over the nodes.
    for node in nodes:
        # walking the nodes.
        _walk(node, None)
    # committing the session.
    session.commit()
    # iterating over the created todos.
    for todo in created:
        session.refresh(todo)
        # indexing the todo for the chroma service.
        chroma_service.index_todo(todo)
    # returning the created todos.
    return created
