#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   database.py
@Time    :   2025/10/25 15:53:48
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   database engine + session helpers.
'''


from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


# creating the engine for the database.
def _create_engine():
    connect_args = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}
    return create_engine(settings.DB_URL, echo=settings.DEBUG, connect_args=connect_args)


# exporting the engine for use in the application.
engine = _create_engine()


# creating the tables on startup.
def init_db() -> None:
    """Create tables on startup."""
    from app import models  # noqa: F401  # ensure models are registered

    SQLModel.metadata.create_all(engine)


# creating a session for the database.
@contextmanager
def session_scope() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# exporting the session for use in the application.
def get_session() -> Iterator[Session]:
    with session_scope() as session:
        yield session
