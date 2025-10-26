from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, Session, create_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app import models
from app.services import chroma_service


@pytest.fixture()
def session(monkeypatch: pytest.MonkeyPatch) -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    # Avoid hitting the real vector DB in unit tests
    monkeypatch.setattr(chroma_service, "index_todo", lambda *args, **kwargs: None)
    monkeypatch.setattr(chroma_service, "delete_todo", lambda *args, **kwargs: None)

    with Session(engine) as session_obj:
        yield session_obj
