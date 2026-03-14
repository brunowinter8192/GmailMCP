---
paths:
  - "server.py"
  - "src/**/*.py"
---

# Tool Parameter Design

**CRITICAL:** Keep tool definitions lean. Documentation belongs in SKILL.md.

## Lean Tools + Skill Pattern

Tool definitions stay minimal to save context tokens. Detailed descriptions go in SKILL.md.

**server.py (lean):**
```python
@mcp.tool
def search_repos(
    query: str,
    sort_by: Literal["stars", "forks", "updated", "best_match"] = "best_match"
) -> list[TextContent]:
    """Search repos. Use to find projects, libraries, or frameworks."""
    return search_repos_workflow(query, sort_by)
```

**SKILL.md (detailed):**
```markdown
### search_repos
| Parameter | Description |
|-----------|-------------|
| query | Search query with GitHub qualifiers (e.g., "fastapi stars:>1000") |
| sort_by | Sort by: stars (popularity), forks, updated, best_match (relevance) |
```

**Rules:**
- NO `Annotated[str, Field(description="...")]` in tool definitions
- Docstring: One sentence (what + when)
- Parameter details: Only in SKILL.md
- Literal for enum-like choices with clear descriptions
- Provide sensible defaults
- Keep options limited (3-5 max)

# Tool Output Design

**CRITICAL:** Output must enable direct tool chaining

**Principles:**
- Include all fields needed for next tool call
- Avoid nested structures when possible
- Consistent field names across tools
- Human-readable + machine-parseable

## Large Response Handling

When responses exceed context limits:

```python
MAX_CHARS = 1000

def format_response(data: dict) -> dict:
    formatted = transform(data)

    if len(str(formatted)) > MAX_CHARS:
        truncated = truncate_to_safe_size(formatted)
        return {
            "data": truncated,
            "truncated": True,
            "warning": "Response truncated. Use pagination or filters to narrow results."
        }

    return {
        "data": formatted,
        "truncated": False,
        "warning": None
    }
```

# Tool Separation Principle

**CRITICAL:** One tool = One responsibility. No multi-mode tools.

**Rationale:**
- LLM makes intuitive choice based on task
- No ambiguity about tool purpose
- Each tool has focused parameters
- Easier to maintain and test

**EXCEPTION:** Do NOT create a new tool when an existing tool can cover the use case with a new parameter. Parameters extend tools; new tools serve new responsibilities.

**Merge-First:** Before adding a new tool, check if an existing tool can absorb the functionality via an additional parameter. Fewer tools = less context overhead for the model.
