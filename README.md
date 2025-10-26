# Roominate - Gamified Task Tracker

enter same stuff from devpost here (like the elevator pitch)

This repo houses the Godot game plus Python services that:
- expose the quest-planning REST API (`uv run uvicorn app.main:app --reload`)
- expose the same capabilities over MCP (`uv run python backends/app/mcp_server.py --transport stdio`)
- add a lightweight agent-relay server that routes prompts to Fetch.ai, JanitorAI, Wordware, or Letta (`uv run uvicorn app.agent_server:app --port 8300 --reload`)

All details live in `backends/README.md`, `docs/API.md`, and `docs/MCPGuide.md`.
