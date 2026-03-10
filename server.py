# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from mcp.types import TextContent

from src.gmail.search_emails import search_emails_workflow
from src.gmail.read_email import read_email_workflow
from src.gmail.list_emails import list_emails_workflow

mcp = FastMCP("Gmail")


# TOOLS

@mcp.tool
def search_emails(
    query: Annotated[str, Field(description="Gmail search query (e.g., 'from:user@example.com', 'subject:meeting after:2024/01/01', 'has:attachment')")],
    max_results: Annotated[int, Field(description="Max emails to return (1-50)")] = 10
) -> list[TextContent]:
    """Search Gmail using Gmail's search syntax. Returns matching emails with subject, sender, date, snippet, and message ID. Use the message ID with read_email to get the full content."""
    return search_emails_workflow(query, min(max_results, 50))


@mcp.tool
def read_email(
    message_id: Annotated[str, Field(description="Gmail message ID (from search_emails or list_emails results)")]
) -> list[TextContent]:
    """Read the full content of a specific email by its message ID. Returns subject, sender, recipients, date, body text, and attachment names."""
    return read_email_workflow(message_id)


@mcp.tool
def list_emails(
    label: Annotated[str, Field(description="Gmail label (e.g., 'INBOX', 'SENT', 'STARRED', 'IMPORTANT', 'UNREAD')")] = "INBOX",
    max_results: Annotated[int, Field(description="Max emails to return (1-50)")] = 20
) -> list[TextContent]:
    """List recent emails in a Gmail label/folder. Returns emails with subject, sender, date, snippet, and message ID. Use message ID with read_email to get full content."""
    return list_emails_workflow(label, min(max_results, 50))


if __name__ == "__main__":
    mcp.run()
