# Gmail MCP Server

Gmail API integration for reading and searching emails.

## Sources

| Source | Purpose |
|--------|---------|
| Gmail API Ref | Endpoints, parameters, response schemas |
| Existing Code | Currently used fields, patterns |

## Project Structure

```
gmail/
├── server.py
├── mcp-start.sh
├── requirements.txt
├── README.md                       → [Setup & External Docs](README.md)
├── auth/
│   └── setup.py                    One-time OAuth setup
├── src/
│   └── gmail/                      → [DOCS.md](src/gmail/DOCS.md)
```
