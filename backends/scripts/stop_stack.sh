#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT_DIR/.stack_pids"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No PID file found at $PID_FILE. Are the services running?" >&2
  exit 0
fi

# shellcheck disable=SC1090
source "$PID_FILE"

stop_process() {
  local name=$1
  local pid=$2
  if [[ -z "${pid:-}" ]]; then
    return
  fi
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping $name (pid $pid)..."
    kill "$pid" 2>/dev/null || true
    # Wait briefly for graceful shutdown
    for _ in {1..10}; do
      if kill -0 "$pid" 2>/dev/null; then
        sleep 0.5
      else
        break
      fi
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "$name did not exit gracefully; forcing kill" >&2
      kill -9 "$pid" 2>/dev/null || true
    fi
  else
    echo "$name (pid $pid) not running"
  fi
}

stop_process "MCP server" "${MCP_PID:-}"
stop_process "FastAPI" "${API_PID:-}"

rm -f "$PID_FILE"
echo "Stack stopped."
