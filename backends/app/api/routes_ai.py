#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   routes_ai.py
@Time    :   2025/10/25 15:44:38
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   routes for LLM-powered endpoints.
'''


from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app import schemas
from app.database import get_session
from app.services import ai_service, todo_service

router = APIRouter(prefix="/ai", tags=["AI"])


# generate todos
@router.post("/generate", response_model=schemas.AIGenerateResponse)
def generate_todos(payload: schemas.AIGenerateRequest, session: Session = Depends(get_session)):
    todos = ai_service.generate_structured_todos(payload.user_input)
    persisted_ids: list[int] = []
    if payload.save:
        created = todo_service.save_generated_tree(todos, session)
        persisted_ids = [todo.id for todo in created]
    return schemas.AIGenerateResponse(todos=todos, persisted_ids=persisted_ids)
