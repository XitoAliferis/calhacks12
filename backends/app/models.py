#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   models.py
@Time    :   2025/10/25 15:55:58
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   SQLModel table definitions.
'''


from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


# todo item model.
class TodoItem(SQLModel, table=True):
    # defining the table name.
    __tablename__ = "todo_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    # defining the foreign key for the parent id.
    parent_id: Optional[int] = Field(default=None, foreign_key="todo_items.id", index=True)

    title: str = Field(default="Untitled Task", max_length=255)
    # defining the reason for the todo item.
    reason: Optional[str] = Field(default=None, max_length=1_000)
    # defining the priority for the todo item.
    priority: str = Field(default="medium", max_length=16)
    # defining the status for the todo item.
    status: str = Field(default="pending", max_length=32)
    deadline: Optional[datetime] = Field(default=None, description="ISO timestamp supplied by AI or user")

    # defining the created at timestamp.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    # defining the updated at timestamp.
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # defining a method to touch the updated at timestamp.
    def touch(self) -> None:
        # updating the updated at timestamp.
        self.updated_at = datetime.now(timezone.utc)
