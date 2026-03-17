---
name: gmail
description: Gmail MCP tools — search and read emails (read-only)
---

# Gmail MCP Tools — Usage Guide

## Tools Overview

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_emails` | Find emails by Gmail search syntax | `query`, `max_results` |
| `read_email` | Read full email content by ID | `message_id` |
| `list_emails` | List recent emails in a label | `label`, `max_results` |

## Workflow

### Find → Read Pattern

```
1. FIND — search_emails("query") or list_emails("INBOX") → get message IDs
2. READ — read_email(message_id) → get full email content
```

**Always two steps:** Search/list returns summaries with IDs. Use `read_email` to get the full body.

### Search Modes

- **Targeted search** (user wants specific email):
  Use `search_emails` with precise Gmail query syntax.
  Example: `search_emails(query="from:boss@company.com subject:report after:2026/01/01")`

- **Browsing** (user wants to see recent emails):
  Use `list_emails` with a label.
  Example: `list_emails(label="INBOX", max_results=10)`

- **Label-based** (user wants emails from a specific folder):
  Use `list_emails` with the label name.
  Labels: `INBOX`, `SENT`, `STARRED`, `IMPORTANT`, `UNREAD`, `DRAFT`, `SPAM`, `TRASH`

## Gmail Search Syntax (for search_emails)

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:john@example.com` | Emails from a specific sender |
| `to:` | `to:mary@example.com` | Emails sent to a specific recipient |
| `subject:` | `subject:"meeting notes"` | Emails with specific subject text |
| `has:attachment` | `has:attachment` | Emails with attachments |
| `after:` | `after:2026/01/01` | Emails after a date |
| `before:` | `before:2026/02/01` | Emails before a date |
| `is:` | `is:unread` | Emails with a specific state |
| `label:` | `label:work` | Emails with a specific label |
| `newer_than:` | `newer_than:7d` | Emails from last N days/months |
| `older_than:` | `older_than:1m` | Emails older than N days/months |

**Combine operators:** `from:john@example.com after:2026/01/01 has:attachment`

## Tool Selection

| Goal | Tool |
|------|------|
| Find emails matching criteria | `search_emails` |
| Read a specific email | `read_email` |
| Browse inbox / recent emails | `list_emails(label="INBOX")` |
| Check sent emails | `list_emails(label="SENT")` |
| See starred/important emails | `list_emails(label="STARRED")` |
| Find unread emails | `search_emails(query="is:unread")` |
| Find emails with attachments | `search_emails(query="has:attachment")` |

## Result Limits

- `search_emails`: Default 10, max 50
- `list_emails`: Default 20, max 50
- For large result sets: use date filters to narrow scope

## Job Application Email Check

When checking for job application updates, run TWO searches to avoid blind spots:

**Search 1 — By company name:**
```
search_emails(query="Company1 OR Company2 OR Company3 after:YYYY/MM/DD", max_results=30)
```
Use the earliest application date as `after:` — not today's date.

**Search 2 — By subject keywords (catches emails where company name is missing):**
```
search_emails(query="subject:Bewerbung OR subject:application OR subject:interview OR subject:Einladung OR subject:Absage OR subject:rejection OR subject:next steps after:YYYY/MM/DD", max_results=30)
```

**Why two searches:** Recruiting platforms (Greenhouse, Lever, Workable, Ashby) sometimes send emails without the company name in subject/body. Search 1 alone would miss those. Search 2 catches generic recruiting emails.

**After search:** If any email looks like a real update (not just Eingangsbestaetigung), use `read_email` to get the full content before reporting to user.

**Known senders for recruiting platforms:**
- `no-reply@msg.join.com` — join.com (kiresult, cinify, Endo Health)
- `no-reply@ashbyhq.com` — Ashby (Swans)
- `workday@docmorris.com` — Workday (DocMorris)
- `jobs-noreply@linkedin.com` — LinkedIn Easy Apply
- `*.recruitee.com` — Recruitee (celver)

## Known Limitations

- **Read-only** — cannot send, delete, or modify emails (scope: `gmail.readonly`)
- **No attachment download** — attachment names are listed but cannot be downloaded
- **OAuth token refresh** — token auto-refreshes, but may need re-auth after 7 days of inactivity
- **HTML emails** — body extracted as plain text when available, falls back to HTML
