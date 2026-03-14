---
paths:
  - "server.py"
  - "src/**/*.py"
---

# server.py Pattern

**CRITICAL:** server.py is the orchestrator. Only imports and tool definitions.

```python
# INFRASTRUCTURE
from typing import Literal
from fastmcp import FastMCP

from src.domain.tool_one import tool_one_workflow

mcp = FastMCP("ServerName")


# TOOLS

@mcp.tool
def tool_one(
    param: str,
    option: Literal["opt_a", "opt_b"] = "opt_a"
) -> list[TextContent]:
    """Use when user asks for X. Good for Y, Z use cases."""
    return tool_one_workflow(param, option)


if __name__ == "__main__":
    mcp.run()
```

**Rules:**
- NO business logic in server.py
- Each tool delegates to module orchestrator
- Lean tool definitions (see tool-design rule)

# Module Pattern

**CRITICAL:** Each module follows INFRASTRUCTURE → ORCHESTRATOR → FUNCTIONS

## Starter Pattern (1-3 modules)

Define constants directly in each module:

```python
# INFRASTRUCTURE
import requests
from mcp.types import TextContent

API_BASE = "https://api.example.com"
RESULTS_LIMIT = 20


# ORCHESTRATOR
def tool_name_workflow(param: str, option: str = "default") -> list[TextContent]:
    raw_data = fetch_data(param, option)
    return [TextContent(type="text", text=format_response(raw_data))]


# FUNCTIONS

# Fetch data from external API
def fetch_data(param: str, option: str) -> dict:
    response = requests.get(f"{API_BASE}/endpoint", params={"q": param})
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
