---
paths:
  - "server.py"
  - "src/**/*.py"
---

# server.py Pattern

**CRITICAL:** server.py is the orchestrator. Only imports and tool definitions.

## Tool Schema Philosophy

MCP tool schemas are loaded ON-DEMAND — only when a tool is called, not before. Every word in descriptions and parameter annotations costs context tokens at every call.

**Rules:**
- **Tool descriptions:** Minimal docstring (3-5 words). Skill provides all pre-call guidance.
- **Parameter descriptions:** NONE. Use plain parameters (`param: str`), not `Annotated[str, Field(description="...")]`. The MCP schema shows only name + type + default — that's enough.
- **Literal types** are self-documenting — no Field description needed.
- **NO business logic** in server.py — each tool delegates to module orchestrator.

```python
# INFRASTRUCTURE
from typing import Literal
from fastmcp import FastMCP
from mcp.types import TextContent

from src.domain.tool_one import tool_one_workflow

mcp = FastMCP("ServerName")


# TOOLS

@mcp.tool
def tool_one(
    param: str,
    option: Literal["opt_a", "opt_b"] = "opt_a",
    limit: int = 25
) -> list[TextContent]:
    """Brief tool purpose."""
    return tool_one_workflow(param, option, limit)


if __name__ == "__main__":
    mcp.run()
```

# Module Pattern

**CRITICAL:** Each module follows INFRASTRUCTURE → ORCHESTRATOR → FUNCTIONS

## Floor/Cap Pattern

Workflows enforce parameter boundaries. Agent can choose within range, server guarantees sane values.

```python
# ORCHESTRATOR
def tool_name_workflow(query: str, limit: int = 25) -> list[TextContent]:
    limit = max(limit, 10)   # Floor: agent can go higher, never lower
    limit = min(limit, 100)  # Cap: agent can go lower, never higher
    raw_data = fetch_data(query, limit)
    return [TextContent(type="text", text=format_response(raw_data))]
```

**When to use floors:** Parameters where low values produce incomplete results (limit, top_k, max_files, depth).
**When to use caps:** Parameters where high values waste resources or hit API limits.

## Starter Pattern (1-3 modules)

Define constants directly in each module:

```python
# INFRASTRUCTURE
import requests
from mcp.types import TextContent

API_BASE = "https://api.example.com"
MAX_LIMIT = 100


# ORCHESTRATOR
def tool_name_workflow(query: str, limit: int = 25) -> list[TextContent]:
    limit = max(limit, 10)  # Floor: agent can go higher, never lower
    raw_data = fetch_data(query, min(limit, MAX_LIMIT))
    return [TextContent(type="text", text=format_response(raw_data))]


# FUNCTIONS

# Fetch data from external API
def fetch_data(query: str, limit: int) -> dict:
    response = requests.get(f"{API_BASE}/endpoint", params={"q": query, "limit": limit})
    response.raise_for_status()
    return response.json()


# Format API response for output
def format_response(raw_data: dict) -> str:
    ...
```

## Scaled Pattern (4+ modules)

Extract shared infrastructure to `client.py`:

**client.py** (utility module, no ORCHESTRATOR):
```python
# INFRASTRUCTURE
import os

API_BASE = "https://api.example.com"
API_TOKEN = os.environ.get("API_TOKEN", "")
RESULTS_PER_PAGE = 20


# FUNCTIONS

# Build headers with optional auth token
def build_headers() -> dict:
    headers = {"Accept": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers
```

**Module using client.py:**
```python
# INFRASTRUCTURE
import requests
from mcp.types import TextContent
from src.domain.client import API_BASE, RESULTS_PER_PAGE, build_headers


# ORCHESTRATOR
def tool_name_workflow(query: str) -> list[TextContent]:
    raw_data = fetch_data(query)
    return [TextContent(type="text", text=format_response(raw_data))]


# FUNCTIONS

# Fetch data from API
def fetch_data(query: str) -> dict:
    response = requests.get(f"{API_BASE}/search", params={"q": query}, headers=build_headers())
    response.raise_for_status()
    return response.json()
```

**When to scale:** Refactor to client.py when 4+ modules duplicate constants/headers.
