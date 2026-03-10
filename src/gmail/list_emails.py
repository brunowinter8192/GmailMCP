# INFRASTRUCTURE
from mcp.types import TextContent

from src.gmail.auth import get_gmail_service
from src.gmail.formatting import format_email_summary


# ORCHESTRATOR
def list_emails_workflow(label: str = "INBOX", max_results: int = 20) -> list[TextContent]:
    service = get_gmail_service()
    messages = fetch_messages_by_label(service, label, max_results)

    if not messages:
        return [TextContent(type="text", text=f"No emails in {label}.")]

    summaries = fetch_message_summaries(service, messages)
    header = f"{len(summaries)} emails in {label}:\n"
    formatted = header + "\n".join(format_email_summary(m) for m in summaries)
    return [TextContent(type="text", text=formatted)]


# FUNCTIONS

def fetch_messages_by_label(service, label: str, max_results: int) -> list[dict]:
    """Fetch message IDs from a Gmail label."""
    result = service.users().messages().list(
        userId="me", labelIds=[label], maxResults=max_results
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
