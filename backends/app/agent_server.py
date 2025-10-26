"""Standalone FastAPI server to broker agent providers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services.agent_router import agent_router, AgentResult

class AgentRequest(BaseModel):
    provider: str = Field(pattern="^(fetchai|janitorai|wordware|letta)$", description="Target agent provider")
    model: Optional[str] = Field(default=None, description="Requested model identifier (provider-specific)")
    user_input: str = Field(min_length=1, description="Natural language prompt/intention")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra parameters")


class AgentResponse(BaseModel):
    provider: str
    model: Optional[str]
    output: str
    raw: Any
    used_fallback: bool = False

    @classmethod
    def from_result(cls, result: AgentResult) -> "AgentResponse":
        return cls(
            provider=result.provider,
            model=result.model,
            output=result.output,
            raw=result.raw,
            used_fallback=result.used_fallback,
        )


app = FastAPI(title="Agent Relay", version="0.1.0")


@app.post("/agents/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    result = await agent_router.run(
        provider=request.provider,
        model=request.model,
        user_input=request.user_input,
        metadata=request.metadata,
    )
    return AgentResponse.from_result(result)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
