# MCP Server Process

**Server name:** `reddit` (via plugin `reddit@brunowinter-plugins`)
**Process runs from:** `~/.claude/plugins/cache/brunowinter-plugins/reddit/1.0.0/`

**Find running server:**
```bash
ps aux | grep "fastmcp.*reddit" | grep -v grep
```

**Kill server (force restart):**
```bash
pkill -f "fastmcp.*reddit"
```

After kill: next CC session auto-starts the server with fresh code from cache.

**mcp-start.sh dependency sync:** The startup script checks if `requirements.txt` changed since last venv setup by diffing against a saved copy in `.venv/.requirements.sha`. If changed, it runs `pip install -q -r requirements.txt` automatically. This prevents "module not found" crashes when new dependencies are added.

# .mcp.json Integration

**CRITICAL:** Each MCP server needs .mcp.json for Claude Code registration.

```json
{
  "mcpServers": {
    "server_name": {
      "command": "/absolute/path/to/venv/bin/fastmcp",
      "args": ["run", "/absolute/path/to/server.py"],
      "env": {
        "API_TOKEN": "${API_TOKEN}"
      }
    }
  }
}
```

**Rules:**
- ALL paths MUST be absolute (no relative paths)
- command: Absolute path to fastmcp executable in venv
- args: ["run", "/absolute/path/to/server.py"]
- NO cwd field (unreliable in Claude Code)

**Environment Variables:**
- Use ${VAR_NAME} syntax for secrets
- Never hardcode tokens/keys

**Verification:**
```bash
claude mcp list
```
