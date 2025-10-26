# MCP Bridge Guide

This document explains how to run and use the FastMCP bridge that exposes the AI Task backend as MCP tools.

## When to use it
- Let Creao or any MCP-aware agent call the same task APIs the Godot client uses.
- Script complex workflows (e.g., auto-generate goals, push them into the DB, perform semantic search) without bespoke HTTP wrappers.

## Starting the Bridge
```bash
cd backends
# stdio transport (agents launched locally)
uv run python -m app.mcp_server --transport stdio

# HTTP transport for Postman/curl testing
uv run python -m app.mcp_server --transport http --host 127.0.0.1 --port 8766
```

> The HTTP transport expects `Content-Type: application/json` and `Accept: application/json, text/event-stream` headers.

## Tool Catalog
| Tool | Description | Arguments |
| ---- | ----------- | ---------- |
| `health` | Returns health status | — |
| `ai_generate` | Calls Claude via OpenRouter, optional persistence | `user_input: str`, `save: bool = False` |
| `create_todo` | Create one todo | `todo: TodoCreate schema` |
| `list_todos` | Filtered list | `status`, `priority`, `due_before`, `due_after` |
| `update_todo` | Update by id | `todo_id`, `fields: TodoUpdate schema` |
| `delete_todo` | Delete by id | `todo_id` |
| `complete_todo` | Mark as `done` | `todo_id` |
| `todo_tree` | Hierarchical todos | — |
| `memory_search` | Chroma recall | `query: str`, `limit: int = 5` |

Schemas mirror `app/schemas.py`.

## Sample Curl (HTTP transport)
```bash
curl http://127.0.0.1:8766/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Call `ai_generate`:
```bash
curl http://127.0.0.1:8766/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
        "jsonrpc":"2.0",
        "id":2,
        "method":"tools/call",
        "params":{
          "name":"ai_generate",
          "arguments":{"user_input":"Plan my finals week","save":false}
        }
      }'
```

## Postman
1. Start the HTTP bridge (`uv run python -m app.mcp_server --transport http --port 8766`).
2. Import `docs/PostmanMCP.json`.
3. Set `{{mcp_base_url}}` to `http://127.0.0.1:8766`.

## Integrating with Claude Desktop

1. **Locate your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Copy the template:**
   ```bash
   cp docs/claude_desktop_config.template.json /path/to/claude_desktop_config.json
   ```

3. **Update the configuration:**
   - Set `cwd` to your actual `backends` directory path
   - Replace `your-api-key-here` with your OpenRouter API key
   - Adjust other environment variables as needed

4. **Restart Claude Desktop** to load the MCP server

5. **Verify connection:**
   - The MCP server should appear in Claude Desktop's integrations
   - You can now use tools like `ai_generate`, `todo_tree`, and `memory_search`

See `docs/claude_desktop_config.template.json` for the full configuration example.

## Integrating with Other Agents
- Register the stdio command (`uv run python -m app.mcp_server --transport stdio`) in Creao or any MCP client.
- The bridge advertises resources:
  - `mcp://docs/api` – REST contract (`docs/API.md`).
  - `mcp://docs/mcp-guide` – this guide.

Use those resources as in-agent help text so the AI understands available tools and payloads.
