#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   routes_todos.py
@Time    :   2025/10/25 15:45:48
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   routes for todo CRUD endpoints.
'''

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session

from app.database import get_session
from app import schemas
from app.services import todo_service

router = APIRouter(prefix="/todos", tags=["Todos"])

# create todo
@router.post("", response_model=schemas.TodoRead, status_code=201)
def create_todo(todo: schemas.TodoCreate, session: Session = Depends(get_session)):
    return todo_service.create_todo(todo, session)

# list todos
@router.get("", response_model=List[schemas.TodoRead])
def list_todos(
    status: Optional[schemas.Status] = Query(default=None),
    priority: Optional[schemas.Priority] = Query(default=None),
    due_before: Optional[datetime] = Query(default=None),
    due_after: Optional[datetime] = Query(default=None),
    session: Session = Depends(get_session),
):
    return todo_service.list_todos(
        session,
        status_filter=status,
        priority_filter=priority,
        due_before=due_before,
        due_after=due_after,
    )

# get todo tree
@router.get("/tree", response_model=schemas.TodoTreeResponse)
def get_tree(session: Session = Depends(get_session)):
    return schemas.TodoTreeResponse(todos=todo_service.get_tree(session))

# update todo
@router.put("/{todo_id}", response_model=schemas.TodoRead)
def update_todo(todo_id: int, payload: schemas.TodoUpdate, session: Session = Depends(get_session)):
    return todo_service.update_todo(todo_id, payload, session)

# delete todo
@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo_service.delete_todo(todo_id, session)
    return Response(status_code=204)


@router.post("/{todo_id}/complete", response_model=schemas.TodoRead)
def complete_todo(todo_id: int, session: Session = Depends(get_session)):
    return todo_service.complete_todo(todo_id, session)
