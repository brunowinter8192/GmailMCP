---
paths:
  - "src/**/*.py"
  - "server.py"
---

# MCP Tool Testing

**CRITICAL:** Test MCP tools by calling them directly via MCP tool calls, NOT via Python import.

**RIGHT:**
```
mcp__<server>__<tool_name>(param="value")
```

**WRONG:**
```bash
source .venv/bin/activate && python -c "from src.<domain>.<module> import ..."
```

**Rules:**
- The MCP server runs as a separate process - there is no local venv to activate
- Always use `mcp__<server>__<tool_name>(...)` to verify tool behavior
- Test both default parameters and new/changed parameters
- **After code changes:** MCP server must be restarted before tool calls reflect changes. Ask user to restart (`/mcp` in Claude Code) before running verification tests
- **After implementing new tools:** Test EVERY new tool via MCP call BEFORE moving to other work. Untested tools at session end = technical debt
- **Reading code is NOT verification.** Only an MCP tool call that returns correct output counts as tested
