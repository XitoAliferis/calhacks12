from __future__ import annotations

from app import models
from app.services import chroma_service


class DummyVector(list):
    def tolist(self):
        return list(self)


class DummyEmbedder:
    def encode(self, docs, **_kwargs):
        return [DummyVector([0.0 for _ in docs])]


class DummyCollection:
    def __init__(self) -> None:
        self.upserts = []

    def upsert(self, **kwargs) -> None:
        self.upserts.append(kwargs)

    def delete(self, **_kwargs) -> None:
        return None

    def query(self, **_kwargs):
        return {
            "ids": [["1"]],
            "documents": [["doc"]],
            "distances": [[0.1]],
            "metadatas": [[{"title": "Match", "reason": "Context"}]],
        }


def test_index_and_search(monkeypatch):
    dummy_collection = DummyCollection()
    monkeypatch.setattr(chroma_service, "_get_collection", lambda: dummy_collection)
    monkeypatch.setattr(chroma_service, "_get_embedder", lambda: DummyEmbedder())

    todo = models.TodoItem(id=1, title="Study", priority="high", status="pending")
    chroma_service.index_todo(todo)
    assert dummy_collection.upserts

    results = chroma_service.search_memory("study")
    assert results[0]["id"] == 1
    assert results[0]["title"] == "Match"
