# INFRASTRUCTURE
import base64
import re
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
    if mime_type in ("text/plain", "text/html"):
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


def strip_html(html: str) -> str:
    """Convert HTML email body to plain text."""
    # Replace <br> variants with newlines
    text = re.sub(r'<br\s*/?\s*>', '\n', html, flags=re.IGNORECASE)
    # Replace block elements with newlines
    text = re.sub(r'</(p|div|tr|li|h[1-6])>', '\n', text, flags=re.IGNORECASE)
    # Remove style/script blocks entirely
    text = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove HTML comments (including Outlook conditionals)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode common HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')
    return text


def clean_body(text: str) -> str:
    """Remove tracking URLs, footers, and noise from email body."""
    if not text:
        return text

    # Strip HTML if body contains HTML tags
    if '<html' in text.lower() or '<body' in text.lower() or '<div' in text.lower():
        text = strip_html(text)

    # Remove zero-width spaces
    text = text.replace("\u034F", "").replace("\u200B", "").replace("\u200C", "").replace("\u200D", "")

    # Cut at common footer markers
    footer_markers = [
        "Abbestellen:",
        "Unsubscribe:",
        "Diese E-Mail ist an",
        "This email was intended for",
        "© LinkedIn",
        "© 20",
    ]
    for marker in footer_markers:
        idx = text.find(marker)
        if idx > 0:
            text = text[:idx].rstrip("-— \n")

    # Replace long tracking URLs (>120 chars) with [link]
    text = re.sub(r'https?://\S{120,}', '[link]', text)

    # Strip trailing whitespace per line, then collapse blank lines to max 2
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)

    return text.strip()


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
    body = clean_body(body)
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
