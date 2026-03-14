"""Inspect raw MIME structure of Gmail messages.

Usage:
    python dev/parsing_suite/01_inspect_structure.py <message_id>
    python dev/parsing_suite/01_inspect_structure.py --all
"""
import sys
from datetime import datetime
from pathlib import Path

GMAIL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GMAIL_ROOT))

from src.gmail.auth import get_gmail_service
from src.gmail.formatting import get_header, format_date

SUITE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = SUITE_DIR / "01_reports"
TEST_EMAILS = SUITE_DIR / "test_emails.txt"


def load_test_emails() -> list[dict]:
    """Load test emails from test_emails.txt."""
    emails = []
    for line in TEST_EMAILS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        emails.append({
            "id": parts[0],
            "label": parts[1],
            "expected": parts[2] if len(parts) > 2 else "",
        })
    return emails


def inspect_message(service, msg_id: str) -> dict:
    """Fetch and analyze MIME structure of a message."""
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    info = {
        "id": msg_id,
        "subject": get_header(headers, "Subject"),
        "from": get_header(headers, "From"),
        "date": format_date(msg.get("internalDate", "0")),
        "top_mime": payload.get("mimeType", ""),
        "parts": [],
    }

    def walk_parts(parts, depth=0):
        for i, part in enumerate(parts):
            mime = part.get("mimeType", "")
            body_size = part.get("body", {}).get("size", 0)
            has_data = bool(part.get("body", {}).get("data", ""))
            nested = part.get("parts", [])
            info["parts"].append({
                "depth": depth,
                "index": i,
                "mime": mime,
                "size": body_size,
                "has_data": has_data,
                "nested_count": len(nested),
            })
            if nested:
                walk_parts(nested, depth + 1)

    walk_parts(payload.get("parts", []))
    return info


def format_report(results: list[dict]) -> str:
    """Build markdown report from inspection results."""
    lines = [
        f"# MIME Structure Inspection",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Emails inspected:** {len(results)}",
        "",
    ]

    for r in results:
        lines.append(f"## {r['subject']}")
        lines.append(f"- **From:** {r['from']}")
        lines.append(f"- **Date:** {r['date']}")
        lines.append(f"- **ID:** {r['id']}")
        lines.append(f"- **Top-level MIME:** {r['top_mime']}")
        lines.append("")

        if r["parts"]:
            lines.append("| Depth | # | MIME Type | Size | Has Data | Nested |")
            lines.append("|-------|---|----------|------|----------|--------|")
            for p in r["parts"]:
                indent = "  " * p["depth"]
                lines.append(
                    f"| {indent}{p['depth']} | {p['index']} | {p['mime']} "
                    f"| {p['size']:,} | {p['has_data']} | {p['nested_count']} |"
                )
        else:
            lines.append("*Single-part message (no MIME parts)*")
        lines.append("")

    return "\n".join(lines)


def main():
    service = get_gmail_service()

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        emails = load_test_emails()
        msg_ids = [(e["id"], e["label"]) for e in emails]
    elif len(sys.argv) > 1:
        msg_ids = [(sys.argv[1], "single")]
    else:
        print("Usage: 01_inspect_structure.py <message_id> | --all")
        sys.exit(1)

    results = []
    for msg_id, label in msg_ids:
        print(f"Inspecting: {label} ({msg_id})")
        results.append(inspect_message(service, msg_id))

    report = format_report(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"structure_{timestamp}.md"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
