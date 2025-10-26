#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   ai_service.py
@Time    :   2025/10/25 16:19:44
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   Wrapper around Claude via OpenRouter to create structured todos.
'''


from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, status
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app import schemas

logger = logging.getLogger(__name__)

# defining the system prompt for the ai service.
_SYSTEM_PROMPT = (
    "You are an assistant that converts natural language goals into a hierarchical todo JSON. "
    "Return strictly valid JSON following this schema: {\"todos\": [ {\"title\": str, \"reason\": str?, \"priority\": one of ['low','medium','high'], \"status\": one of ['pending','in-progress','done'], \"deadline\": ISO8601 string or null, \"subitems\": [] } ] }."
)

# defining the client for the ai service.
_client: OpenAI | None = None


# defining a function to mock the todos for the ai service.
def _mock_todos() -> Optional[List[schemas.GeneratedTodoNode]]:
    # getting the mock file for the ai service.
    mock_file = settings.MOCK_AI_RESPONSES_FILE
    # if the mock file is not set, return None.
    if not mock_file:
        return None
    # getting the path for the mock file.
    path = Path(mock_file)
    # if the path does not exist, log a warning and return None.
    if not path.exists():
        logger.warning("Mock AI file %s not found", mock_file)
        return None
    # loading the data from the mock file.
    data = json.loads(path.read_text())
    # if the data is a list, pick the first payload that contains todos.
    if isinstance(data, list):
        # if file stores a list of responses, pick the first payload that contains todos
        for candidate in data:
            if isinstance(candidate, dict) and "todos" in candidate:
                data = candidate
                break
    # if the data is a dictionary and contains todos, get the todos.
    if isinstance(data, dict) and "todos" in data:
        todos_raw = data["todos"]
    # if the data is a list, get the todos.
    elif isinstance(data, list):
        todos_raw = data
    # otherwise, raise an error.
    else:
        raise ValueError("Mock AI file must contain either {\"todos\": [...]} or a list of nodes")
    # logging the serving of the ai todos from the mock file.
    logger.info("Serving AI todos from mock file %s", mock_file)
    # returning the todos.
    return [schemas.GeneratedTodoNode(**item) for item in todos_raw]


# defining a function to get the client for the ai service.
def _get_client() -> OpenAI:
    # getting the client for the ai service.
    global _client
    if _client is None:
        # if the client is not set, raise an error.
        if not settings.OPENROUTER_API_KEY:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OPENROUTER_API_KEY missing")
        # otherwise, set the client.
        _client = OpenAI(api_key=settings.OPENROUTER_API_KEY, base_url=settings.OPENROUTER_BASE_URL)
    # returning the client.
    return _client


# defining a function to get the raw completion for the ai service.
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _raw_completion(user_input: str) -> str:
    # getting the client for the ai service.
    client = _get_client()
    # getting the response from the ai service.
    response = client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    # getting the content from the response.
    content = response.choices[0].message.content
    # if the content is empty, raise an error.
    if not content:
        raise RuntimeError("Claude returned empty content")
    # returning the content.
    return content


# defining a function to generate the structured todos for the ai service.
def _strip_code_fence(payload: str) -> str:
    """Remove markdown fences (```json ... ```) often returned by models."""
    cleaned = payload.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # drop first fence line
        lines = lines[1:]
        # drop trailing fence if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def generate_structured_todos(user_input: str) -> List[schemas.GeneratedTodoNode]:
    # getting the mock response for the ai service.
    mock_response = _mock_todos()
    # if the mock response is not None, return the mock response.
    if mock_response is not None:
        return mock_response
    try:
        # getting the payload from the ai service.
        payload = _strip_code_fence(_raw_completion(user_input))
        # loading the data from the payload.
        data = json.loads(payload)
        # getting the todos from the data.
        todos_raw = data.get("todos", [])
        return [schemas.GeneratedTodoNode(**item) for item in todos_raw]
    except HTTPException:
        # if the exception is an HTTP exception, raise it.
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        # if the exception is not an HTTP exception, log the exception and raise an HTTP exception.
        logger.exception("AI generation failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
