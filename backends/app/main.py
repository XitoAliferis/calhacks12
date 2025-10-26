#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   main.py
@Time    :   2025/10/25 15:55:18
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   FastAPI bootstrapper.
'''


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from app import models
from app.config import settings
from app.database import init_db, session_scope
from app.middleware import RateLimiterMiddleware
from app.api import routes_ai, routes_memory, routes_todos

# creating the FastAPI app.
app = FastAPI(title="AI Task Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimiterMiddleware,
    limit=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)
# including the routes.
app.include_router(routes_todos.router)
app.include_router(routes_ai.router)
app.include_router(routes_memory.router)


# initializing the database on startup.
@app.on_event("startup")
def _startup() -> None:
    init_db()


# healthcheck endpoint.
@app.get("/health", tags=["Health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "debug": str(settings.DEBUG).lower()}


# readiness endpoint.
@app.get("/ready", tags=["Health"])
def readiness() -> dict[str, str]:
    try:
        with session_scope() as session:
            session.exec(select(models.TodoItem.id).limit(1))
    except Exception as exc:  # pragma: no cover - surfaces infra bugs
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}
