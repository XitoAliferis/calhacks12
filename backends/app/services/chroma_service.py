#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   chroma_service.py
@Time    :   2025/10/25 16:20:57
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   Utilities for persisting and querying semantic task memory.
'''


from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import chromadb
from chromadb.api.models.Collection import Collection

try:  # sentence-transformers is an optional heavy dep; fail late with a clear error.
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - handled at runtime
    SentenceTransformer = None  # type: ignore

from app.config import settings
from app.models import TodoItem

logger = logging.getLogger(__name__)

# defining the collection name for the chroma service.
_COLLECTION_NAME = "todo_memory"
# defining the client for the chroma service.
_client: chromadb.PersistentClient | None = None
# defining the collection for the chroma service.
_collection: Collection | None = None
# defining the embedder for the chroma service.
_embedder: SentenceTransformer | None = None


# defining a function to get the collection for the chroma service.
def _get_collection() -> Collection:
    # getting the client and collection for the chroma service.
    global _client, _collection
    if _collection is None:
        # if the collection is not set, create the directory for the chroma service.
        Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        # creating the client for the chroma service.
        _client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        # creating the collection for the chroma service.
        _collection = _client.get_or_create_collection(name=_COLLECTION_NAME)
    # returning the collection.
    return _collection


# defining a function to get the embedder for the chroma service.
def _get_embedder() -> SentenceTransformer:
    # getting the embedder for the chroma service.
    global _embedder
    if _embedder is None:
        # if the embedder is not set, raise an error.
        if SentenceTransformer is None:  # pragma: no cover
            raise RuntimeError("sentence-transformers is not installed")
        # otherwise, set the embedder.
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    # returning the embedder.
    return _embedder


# defining a function to build the document for the chroma service.
def _build_document(todo: TodoItem) -> str:
    # getting the deadline for the todo item.
    deadline = todo.deadline.isoformat() if todo.deadline else "unscheduled"
    # returning the document.
    return f"{todo.title}\nReason: {todo.reason or 'n/a'}\nPriority: {todo.priority}\nDeadline: {deadline}"


# defining a function to index the todo for the chroma service.
def index_todo(todo: TodoItem) -> None:
    # if the todo id is not set, log a warning and return.
    if todo.id is None:
        logger.debug("skip indexing unsaved todo")
        return
    # getting the collection for the chroma service.
    collection = _get_collection()
    # getting the embedder for the chroma service.
    embedder = _get_embedder()
    # building the document for the chroma service.
    document = _build_document(todo)
    # encoding the document for the chroma service.
    embeddings = embedder.encode([document], convert_to_numpy=True)[0].tolist()
    # upserting the document for the chroma service.
    collection.upsert(
        ids=[str(todo.id)],
        documents=[document],
        metadatas=[
            {
                "title": todo.title,
                "priority": todo.priority,
                "status": todo.status,
                "reason": todo.reason or "",
            }
        ],
        embeddings=[embeddings],
    )


# defining a function to delete the todo for the chroma service.    
def delete_todo(todo_id: int) -> None:
    # getting the collection for the chroma service.
    collection = _get_collection()
    # deleting the todo for the chroma service.
    collection.delete(ids=[str(todo_id)])


# defining a function to search the memory for the chroma service.
def search_memory(query: str, limit: int = 5):
    # if the query is not set, return an empty list.
    if not query:
        return []
    # getting the collection for the chroma service.
    collection = _get_collection()
    # querying the memory for the chroma service.
    result = collection.query(query_texts=[query], n_results=limit)
    # getting the ids from the result.
    ids = result.get("ids", [[]])[0]
    # getting the documents from the result.
    docs = result.get("documents", [[]])[0]
    # getting the distances from the result.
    distances = result.get("distances", [[]])[0]
    # getting the metadatas from the result.
    metadatas = result.get("metadatas", [[]])[0]

    # formatting the result.
    formatted = []
    # iterating over the ids, documents, distances, and metadatas.
    for idx, doc, distance, metadata in zip(ids, docs, distances, metadatas):
        formatted.append(
            {
                "id": int(idx),
                "title": metadata.get("title") if metadata else doc.split("\n", 1)[0],
                "reason": metadata.get("reason") if metadata else None,
                "score": float(distance),
            }
        )
    return formatted


# defining a function to index many todos for the chroma service.   
def index_many(todos: List[TodoItem]) -> None:
    # iterating over the todos.
    for todo in todos:
        # indexing the todo for the chroma service.
        index_todo(todo)
