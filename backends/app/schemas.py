#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   schemas.py
@Time    :   2025/10/25 15:56:21
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   Pydantic schemas shared across routes.
'''


from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

Priority = Literal["low", "medium", "high"]
Status = Literal["pending", "in-progress", "done"]


# todo base model.
class TodoBase(BaseModel):
    # defining the title for the todo item.
    title: str = Field(min_length=1, max_length=255)
    # defining the reason for the todo item.
    reason: Optional[str] = Field(default=None, max_length=1_000)
    # defining the priority for the todo item.
    priority: Priority = "medium"
    # defining the status for the todo item.
    status: Status = "pending"
    # defining the deadline for the todo item.
    deadline: Optional[datetime] = None
    # defining the parent id for the todo item.
    parent_id: Optional[int] = Field(default=None, ge=0)


# todo create model.
class TodoCreate(TodoBase):
    pass


# todo update model.
class TodoUpdate(BaseModel):
    # defining the title for the todo item.
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    # defining the reason for the todo item.
    reason: Optional[str] = Field(default=None, max_length=1_000)
    # defining the priority for the todo item.
    priority: Optional[Priority] = None
    # defining the status for the todo item.
    status: Optional[Status] = None
    # defining the deadline for the todo item.
    deadline: Optional[datetime] = None


# todo read model.
class TodoRead(TodoBase):
    # defining the id for the todo item.
    id: int
    # defining the created at timestamp.
    created_at: datetime
    # defining the updated at timestamp.
    updated_at: datetime

    model_config = {"from_attributes": True}


# todo tree node model.
class TodoTreeNode(BaseModel):
    # defining the id for the todo item.
    id: int
    # defining the title for the todo item.
    title: str
    # defining the reason for the todo item.
    reason: Optional[str] = None
    # defining the priority for the todo item.
    priority: Priority
    # defining the status for the todo item.
    status: Status
    # defining the deadline for the todo item.
    deadline: Optional[datetime] = None
    # defining the children for the todo item.
    children: List["TodoTreeNode"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# todo tree response model.
class TodoTreeResponse(BaseModel):
    todos: List[TodoTreeNode]


# ai generate request model.
class AIGenerateRequest(BaseModel):
    # defining the user input for the ai generate request.
    user_input: str = Field(min_length=4)
    # defining the save flag for the ai generate request.
    save: bool = True


# generated todo node model.
class GeneratedTodoNode(BaseModel):
    # defining the title for the generated todo node.
    title: str
    # defining the reason for the generated todo node.
    reason: Optional[str] = None
    # defining the priority for the generated todo node.
    priority: Priority = "medium"
    # defining the status for the generated todo node.
    status: Status = "pending"
    # defining the deadline for the generated todo node.
    deadline: Optional[str] = None
    # defining the subitems for the generated todo node.
    subitems: List["GeneratedTodoNode"] = Field(default_factory=list)

    # defining a validator for the deadline.
    @field_validator("deadline")
    @classmethod
    def normalize_deadline(cls, value: Optional[str]) -> Optional[str]:
        # if the deadline is empty, return None.
        if value == "":
            return None
        # otherwise, return the deadline.
        return value


# ai generate response model.
class AIGenerateResponse(BaseModel):
    # defining the todos for the ai generate response.
    todos: List[GeneratedTodoNode]
    # defining the persisted ids for the ai generate response.
    persisted_ids: List[int] = Field(default_factory=list)


# memory search request model.
class MemorySearchRequest(BaseModel):
    # defining the query for the memory search request.
    query: str = Field(min_length=2)


# memory search result model.
class MemorySearchResult(BaseModel):
    # defining the id for the memory search result.
    id: int
    # defining the title for the memory search result.
    title: str
    # defining the reason for the memory search result.
    reason: Optional[str]
    # defining the score for the memory search result.
    score: float


# memory search response model.
class MemorySearchResponse(BaseModel):
    # defining the results for the memory search response.
    results: List[MemorySearchResult] = Field(default_factory=list)


TodoTreeNode.model_rebuild()
GeneratedTodoNode.model_rebuild()
