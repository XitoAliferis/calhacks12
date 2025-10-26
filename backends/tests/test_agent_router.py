from __future__ import annotations

import pytest

from app.services.agent_router import agent_router
import asyncio


def test_agent_router_fallback(monkeypatch):
    monkeypatch.setattr(agent_router.providers["fetchai"], "base_url", None)
    result = asyncio.run(agent_router.run("fetchai", model=None, user_input="Test fallback", metadata=None))
    assert result.used_fallback is True
    assert "Test" in result.output
