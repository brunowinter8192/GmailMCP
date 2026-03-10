# INFRASTRUCTURE
import base64
from datetime import datetime


# FUNCTIONS

def get_header(headers: list, name: str) -> str:
    """Extract a header value by name from Gmail message headers."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def format_date(internal_date_ms: str) -> str:
    """Convert Gmail internalDate (ms since epoch) to readable date."""
    ts = int(internal_date_ms) / 1000
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M")


def extract_body(payload: dict) -> str:
    """Extract plain text body from Gmail message payload.

    Handles single-part and multi-part MIME structures.
    Prioritizes text/plain, falls back to text/html.
    """
    mime_type = payload.get("mimeType", "")

    # Single part
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    # Multipart — recurse into parts
    parts = payload.get("parts", [])
    plain_text = ""
    html_text = ""

    for part in parts:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                plain_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif part_mime == "text/html":
            data = part.get("body", {}).get("data", "")
            if data:
                html_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif part_mime.startswith("multipart/"):
            # Nested multipart — recurse
            nested = extract_body(part)
            if nested:
                return nested

    return plain_text or html_text or ""


def extract_attachments(payload: dict) -> list[str]:
    """Extract attachment filenames from Gmail message payload."""
    attachments = []
    parts = payload.get("parts", [])
    for part in parts:
        filename = part.get("filename", "")
        if filename:
            size = part.get("body", {}).get("size", 0)
            size_str = f"{size / 1024:.0f} KB" if size > 0 else "unknown size"
            attachments.append(f"{filename} ({size_str})")
        # Recurse into nested multipart
        if part.get("parts"):
            attachments.extend(extract_attachments(part))
    return attachments


def format_email_summary(msg: dict) -> str:
    """Format a Gmail message (metadata) into a compact summary line."""
    headers = msg.get("payload", {}).get("headers", [])
    subject = get_header(headers, "Subject") or "(no subject)"
    sender = get_header(headers, "From")
    date = format_date(msg.get("internalDate", "0"))
    snippet = msg.get("snippet", "")
    msg_id = msg.get("id", "")

    return (
        f"---\n"
        f"ID: {msg_id}\n"
        f"Date: {date}\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Snippet: {snippet}"
    )


def format_email_full(msg: dict) -> str:
    """Format a Gmail message (full) into readable text."""
    headers = msg.get("payload", {}).get("headers", [])
    subject = get_header(headers, "Subject") or "(no subject)"
    sender = get_header(headers, "From")
    to = get_header(headers, "To")
    cc = get_header(headers, "Cc")
    date = format_date(msg.get("internalDate", "0"))

    body = extract_body(msg.get("payload", {}))
    attachments = extract_attachments(msg.get("payload", {}))

    lines = [
        f"Subject: {subject}",
        f"From: {sender}",
        f"To: {to}",
    ]
    if cc:
        lines.append(f"Cc: {cc}")
    lines.append(f"Date: {date}")
    lines.append(f"ID: {msg.get('id', '')}")
    lines.append("")
    lines.append(body.strip() if body else "(no body)")

    if attachments:
        lines.append("")
        lines.append(f"Attachments ({len(attachments)}):")
        for att in attachments:
            lines.append(f"  - {att}")

    return "\n".join(lines)
