"""Routing layer for external agent providers (Fetch.ai, JanitorAI, Wordware, Letta)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.services import ai_service

logger = logging.getLogger(__name__)

ProviderName = str


@dataclass
class AgentResult:
    provider: str
    model: Optional[str]
    output: str
    raw: Any
    used_fallback: bool = False


class ProviderConfigError(RuntimeError):
    pass


def _extract_text(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("response", "output", "text", "message", "content"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, list):
                return " ".join(str(v) for v in value if v)
            if isinstance(value, dict):
                nested = _extract_text(value)
                if nested:
                    return nested
    if isinstance(payload, list):
        return " ".join(_extract_text(item) for item in payload)
    if isinstance(payload, str):
        return payload
    return ""


class HTTPAgentProvider:
    def __init__(self, name: str, base_url: Optional[str], api_key: Optional[str], default_model: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model

    async def run(self, model: Optional[str], user_input: str, metadata: Optional[Dict[str, Any]]) -> AgentResult:
        if not self.base_url:
            raise ProviderConfigError(f"{self.name} base URL is not configured")
        payload: Dict[str, Any] = {"input": user_input}
        final_model = model or self.default_model
        if final_model:
            payload["model"] = final_model
        if metadata:
            payload["metadata"] = metadata

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=settings.AGENT_HTTP_TIMEOUT) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            text = _extract_text(data)
            if not text:
                text = json.dumps(data)
            return AgentResult(provider=self.name, model=final_model, output=text, raw=data)


def _fallback_response(user_input: str) -> AgentResult:
    todos = ai_service.generate_structured_todos(user_input)
    if not todos:
        text = "No tasks generated."
    else:
        lines: list[str] = []
        for idx, node in enumerate(todos, start=1):
            lines.append(f"{idx}. {node.title} — {node.reason or 'No reason provided.'}")
            for child_idx, child in enumerate(node.subitems, start=1):
                lines.append(f"  {idx}.{child_idx} {child.title}")
        text = "\n".join(lines)
    return AgentResult(provider="fallback", model=None, output=text, raw=[node.model_dump() for node in todos], used_fallback=True)


class AgentRouter:
    def __init__(self) -> None:
        self.providers: dict[str, HTTPAgentProvider] = {
            "fetchai": HTTPAgentProvider(
                name="fetchai",
                base_url=settings.FETCHAI_BASE_URL,
                api_key=settings.FETCHAI_API_KEY,
            ),
            "janitorai": HTTPAgentProvider(
                name="janitorai",
                base_url=settings.JANITORAI_BASE_URL,
                api_key=settings.JANITORAI_API_KEY,
            ),
            "wordware": HTTPAgentProvider(
                name="wordware",
                base_url=settings.WORDWARE_BASE_URL,
                api_key=settings.WORDWARE_API_KEY,
            ),
            "letta": HTTPAgentProvider(
                name="letta",
                base_url=settings.LETTA_BASE_URL,
                api_key=settings.LETTA_API_KEY,
            ),
        }

    async def run(self, provider: str, model: Optional[str], user_input: str, metadata: Optional[Dict[str, Any]]) -> AgentResult:
        normalized = provider.lower()
        handler = self.providers.get(normalized)
        if not handler:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported provider '{provider}'")
        try:
            return await handler.run(model, user_input, metadata)
        except ProviderConfigError as exc:
            logger.warning("%s", exc)
            if settings.AGENT_FALLBACK_ENABLED:
                return _fallback_response(user_input)
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
        except httpx.HTTPStatusError as exc:
            logger.exception("Agent provider %s returned error", provider)
            if settings.AGENT_FALLBACK_ENABLED:
                return _fallback_response(user_input)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
        except Exception as exc:
            logger.exception("Agent provider %s failed", provider)
            if settings.AGENT_FALLBACK_ENABLED:
                return _fallback_response(user_input)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


agent_router = AgentRouter()
