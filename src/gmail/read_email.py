# INFRASTRUCTURE
from mcp.types import TextContent

from src.gmail.auth import get_gmail_service
from src.gmail.formatting import format_email_full


# ORCHESTRATOR
def read_email_workflow(message_id: str) -> list[TextContent]:
    service = get_gmail_service()
    msg = fetch_full_message(service, message_id)
    formatted = format_email_full(msg)
    return [TextContent(type="text", text=formatted)]


# FUNCTIONS

def fetch_full_message(service, message_id: str) -> dict:
    """Fetch a full Gmail message by ID."""
    return service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()
