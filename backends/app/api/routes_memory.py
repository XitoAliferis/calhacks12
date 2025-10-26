#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   routes_memory.py
@Time    :   2025/10/25 15:45:29
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   routes for vector memory endpoints.
'''



from __future__ import annotations

from fastapi import APIRouter

from app import schemas
from app.services import chroma_service

router = APIRouter(prefix="/memory", tags=["Memory"])


# search memory
@router.post("/search", response_model=schemas.MemorySearchResponse)
def search_memory(payload: schemas.MemorySearchRequest):
    raw = chroma_service.search_memory(payload.query)
    results = [
        schemas.MemorySearchResult(
            id=item["id"],
            title=item["title"],
            reason=item.get("reason"),
            score=item["score"],
        )
        for item in raw
    ]
    return schemas.MemorySearchResponse(results=results)
