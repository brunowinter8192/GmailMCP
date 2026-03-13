# Gmail MCP Server

Read-only Gmail access via MCP for Claude Code. Search, list, and read emails.

## Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| API | Gmail API v1 | Official Google API, full search syntax support |
| Client Library | google-api-python-client | Official Python SDK with auto-discovery |
| Auth | OAuth 2.0 (Desktop) | Secure user-scoped access, auto-refresh |
| MCP Framework | FastMCP | Consistent with other MCP servers |

## Installation

### As Plugin (recommended)

In a Claude Code session:

```
/plugin marketplace add brunowinter8192/claude-plugins
/plugin install gmail
```

Restart the session after installation.

### Manual (.mcp.json)

Add to your project's `.mcp.json` (all paths must be absolute):

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/gmail/mcp-start.sh",
      "args": []
    }
  }
}
```

## Plugin Components

| Component | Name | Description |
|-----------|------|-------------|
| **Skill** | `/gmail` | Search syntax, workflow patterns, tool selection guide |
| **MCP Server** | `gmail` | 3 tools: search, list, read emails (read-only) |

## MCP Tools

### search_emails

Search Gmail using Gmail's search syntax.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Gmail search query (e.g., `from:user@example.com subject:meeting`) |
| `max_results` | int | No | 10 | Max emails to return (1-50) |

```
mcp__plugin_gmail_gmail__search_emails(query="from:boss@company.com after:2026/01/01", max_results=5)
mcp__plugin_gmail_gmail__search_emails(query="subject:report has:attachment")
```

### read_email

Read the full content of an email by message ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | string | Yes | Gmail message ID (from search_emails or list_emails results) |

```
mcp__plugin_gmail_gmail__read_email(message_id="18e1a2b3c4d5e6f7")
```

### list_emails

List recent emails in a Gmail label/folder.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `label` | string | No | INBOX | Gmail label (e.g., `INBOX`, `SENT`, `STARRED`, `IMPORTANT`, `UNREAD`) |
| `max_results` | int | No | 20 | Max emails to return (1-50) |

```
mcp__plugin_gmail_gmail__list_emails(label="INBOX", max_results=10)
mcp__plugin_gmail_gmail__list_emails(label="SENT")
```

### Workflow

```
1. FIND — search_emails("query") or list_emails("INBOX") → get message IDs
2. READ — read_email(message_id) → get full email content
```

Always two steps: search/list returns summaries with IDs, then use `read_email` for full content.

## Prerequisites

- Python >= 3.10
- Google Cloud project with Gmail API enabled
- OAuth 2.0 Desktop client credentials

## Setup

### 1. Clone + Python

```bash
git clone https://github.com/brunowinter8192/gmail.git
cd gmail
python -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

The `mcp-start.sh` script auto-creates the venv if missing.

### 2. Google Cloud OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. APIs & Services → Credentials → Create OAuth client ID → Desktop app
4. Download the JSON file:

```bash
mkdir -p ~/.gmail-mcp
mv ~/Downloads/client_secret_xxx.json ~/.gmail-mcp/gcp-oauth.keys.json
```

### 3. Authorize

```bash
python3 auth/setup.py
```

Opens a browser for OAuth consent. Credentials saved to `~/.gmail-mcp/credentials.json`.

Token auto-refreshes on use. May need re-auth after extended inactivity.

## Directory Structure

```
gmail/
  .claude-plugin/          # Plugin manifest (plugin.json only)
  skills/gmail/            # Plugin skill (SKILL.md)
  auth/
    setup.py               # One-time OAuth setup script
  server.py                # MCP Entry Point (Claude Code)
  mcp-start.sh             # Venv bootstrap + server start
  requirements.txt         # Python dependencies
  src/gmail/               # Module implementations (see DOCS.md)
    auth.py                # OAuth credential loading + refresh
    search_emails.py       # Search orchestration
    list_emails.py         # List by label orchestration
    read_email.py          # Full message read orchestration
    formatting.py          # Email formatting (summary + full views)
```

**Module details:** [src/gmail/DOCS.md](src/gmail/DOCS.md)

## Gmail Search Syntax

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:john@example.com` | Emails from a sender |
| `to:` | `to:mary@example.com` | Emails to a recipient |
| `subject:` | `subject:"meeting notes"` | Subject text |
| `has:attachment` | `has:attachment` | Emails with attachments |
| `after:` | `after:2026/01/01` | After a date |
| `before:` | `before:2026/02/01` | Before a date |
| `is:` | `is:unread` | Email state |
| `label:` | `label:work` | Specific label |
| `newer_than:` | `newer_than:7d` | Last N days/months |
| `older_than:` | `older_than:1m` | Older than N days/months |

**Combine operators:** `from:john@example.com after:2026/01/01 has:attachment`

## Limitations

- **Read-only** — cannot send, delete, or modify emails (scope: `gmail.readonly`)
- **No attachment download** — attachment names listed but content not downloadable
- **HTML fallback** — prioritizes text/plain, falls back to stripped HTML
