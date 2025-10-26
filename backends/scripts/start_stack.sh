#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT_DIR/.stack_pids"
LOG_DIR="$ROOT_DIR/.logs"

mkdir -p "$LOG_DIR"

if [[ -f "$PID_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$PID_FILE"
  if [[ -n "${MCP_PID:-}" ]] && kill -0 "$MCP_PID" 2>/dev/null; then
    echo "MCP server already running (pid $MCP_PID). Stop it before starting again." >&2
    exit 1
  fi
  if [[ -n "${API_PID:-}" ]] && kill -0 "$API_PID" 2>/dev/null; then
    echo "FastAPI server already running (pid $API_PID). Stop it before starting again." >&2
    exit 1
  fi
  if [[ -n "${AGENT_PID:-}" ]] && kill -0 "$AGENT_PID" 2>/dev/null; then
    echo "Agent server already running (pid $AGENT_PID). Stop it before starting again." >&2
    exit 1
  fi
fi

cd "$ROOT_DIR"
uv run python -m app.mcp_server --transport http --host 0.0.0.0 --port 8766 \
  > "$LOG_DIR/mcp.log" 2>&1 &
MCP_PID=$!

echo "MCP server started (pid $MCP_PID). Logs: $LOG_DIR/mcp.log"

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
  > "$LOG_DIR/api.log" 2>&1 &
API_PID=$!

echo "FastAPI server started (pid $API_PID). Logs: $LOG_DIR/api.log"

uv run uvicorn app.agent_server:app --host 0.0.0.0 --port 8300 --reload \
  > "$LOG_DIR/agent.log" 2>&1 &
AGENT_PID=$!

echo "Agent relay server started (pid $AGENT_PID). Logs: $LOG_DIR/agent.log"

cat > "$PID_FILE" <<PIDS
MCP_PID=$MCP_PID
API_PID=$API_PID
AGENT_PID=$AGENT_PID
PIDS

echo "Stack running. Use scripts/stop_stack.sh to stop all services."
