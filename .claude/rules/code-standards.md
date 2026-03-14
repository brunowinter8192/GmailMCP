---
paths:
  - "src/**/*.py"
  - "server.py"
---

# Code Standards

- NO comments inside function bodies (only function header comments + section markers)
- NO test files in root (ONLY in debug/ folders - root or per-module)
- NO debug/ or logs/ folders in version control (MUST be in .gitignore)
- NO emojis in production code, READMEs, DOCS.md, logs
- ALWAYS keep script console output concise

**Type hints:** RECOMMENDED but optional

**Fail-Fast:** Let exceptions fly. No try-catch that silently swallows errors affecting business logic. Script must fail if it cannot fulfill its purpose.

# Error Handling

## When to use try-catch
**ALLOWED:**
- Retry logic with exponential backoff
- Graceful degradation with explicit logging
- Resource cleanup (files, connections)
- Converting exceptions to domain errors

**PROHIBITED:**
- Silently swallowing errors
- Generic `except Exception: pass`
- Hiding failures that affect business logic

## API Error Pattern
```python
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raises on 4xx/5xx
return response.json()
```

FastMCP handles exceptions and communicates errors to client.

# Naming Conventions

**server.py:** Always named server.py
**Domain folders:** src/domain_name/ (snake_case, descriptive)
**Modules:** src/domain/tool_name.py (snake_case, matches tool name)
**Package markers:** src/__init__.py and src/domain/__init__.py (required for imports)
**Orchestrator function:** tool_name_workflow()
**MCP tool function:** @mcp.tool def tool_name()
**Documentation:** src/domain/DOCS.md (one per domain)

**Examples:**
- src/scraper/search_web.py → search_web_workflow() → @mcp.tool def search_web()
- src/scraper/scrape_urls.py → scrape_urls_workflow() → @mcp.tool def scrape_urls()
