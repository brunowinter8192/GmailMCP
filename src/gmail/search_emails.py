# INFRASTRUCTURE
from mcp.types import TextContent

from src.gmail.auth import get_gmail_service
from src.gmail.formatting import format_email_summary


# ORCHESTRATOR
def search_emails_workflow(query: str, max_results: int = 10) -> list[TextContent]:
    service = get_gmail_service()
    messages = fetch_message_list(service, query, max_results)

    if not messages:
        return [TextContent(type="text", text=f"No emails found for query: {query}")]

    summaries = fetch_message_summaries(service, messages)
    header = f"Found {len(summaries)} emails for: {query}\n"
    formatted = header + "\n".join(format_email_summary(m) for m in summaries)
    return [TextContent(type="text", text=formatted)]


# FUNCTIONS

def fetch_message_list(service, query: str, max_results: int) -> list[dict]:
    """Fetch message IDs matching a Gmail search query."""
    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    return result.get("messages", [])


def fetch_message_summaries(service, messages: list[dict]) -> list[dict]:
    """Fetch metadata for each message ID."""
    summaries = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["Subject", "From", "To", "Date"]
        ).execute()
        summaries.append(msg)
    return summaries
