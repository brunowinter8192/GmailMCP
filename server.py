# INFRASTRUCTURE
from fastmcp import FastMCP
from mcp.types import TextContent

from src.gmail.search_emails import search_emails_workflow
from src.gmail.read_email import read_email_workflow
from src.gmail.list_emails import list_emails_workflow

mcp = FastMCP("Gmail")


# TOOLS

@mcp.tool
def search_emails(query: str, max_results: int = 10) -> list[TextContent]:
    """Search Gmail."""
    return search_emails_workflow(query, min(max_results, 50))


@mcp.tool
def read_email(message_id: str) -> list[TextContent]:
    """Read email by message ID."""
    return read_email_workflow(message_id)


@mcp.tool
def list_emails(label: str = "INBOX", max_results: int = 20) -> list[TextContent]:
    """List emails in a label."""
    return list_emails_workflow(label, min(max_results, 50))


if __name__ == "__main__":
    mcp.run()
