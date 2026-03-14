"""Regression test for email body parsing.

Parses all test emails through extract_body + clean_body and checks
that expected content snippets are present in the output.

Usage:
    python dev/parsing_suite/02_test_parsing.py
"""
import sys
from datetime import datetime
from pathlib import Path

GMAIL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GMAIL_ROOT))

from src.gmail.auth import get_gmail_service
from src.gmail.formatting import extract_body, clean_body

SUITE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = SUITE_DIR / "02_reports"
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


def test_email(service, email: dict) -> dict:
    """Parse a single email and check for expected content."""
    msg = service.users().messages().get(
        userId="me", id=email["id"], format="full"
    ).execute()

    payload = msg.get("payload", {})
    raw_body = extract_body(payload)
    cleaned = clean_body(raw_body)

    has_expected = email["expected"].lower() in cleaned.lower() if email["expected"] else True

    return {
        "id": email["id"],
        "label": email["label"],
        "expected": email["expected"],
        "passed": has_expected,
        "body_length": len(cleaned),
        "preview": cleaned[:300],
    }


def format_report(results: list[dict]) -> str:
    """Build markdown report from test results."""
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed

    lines = [
        f"# Parsing Regression Test",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Results:** {passed} PASS / {failed} FAIL / {len(results)} total",
        "",
        "| Status | Label | Body Length | Expected Snippet |",
        "|--------|-------|-------------|------------------|",
    ]

    for r in results:
        status = "PASS" if r["passed"] else "**FAIL**"
        lines.append(f"| {status} | {r['label']} | {r['body_length']} | {r['expected'][:50]} |")

    lines.append("")

    for r in results:
        lines.append(f"## {r['label']} ({'PASS' if r['passed'] else 'FAIL'})")
        lines.append(f"- **ID:** {r['id']}")
        lines.append(f"- **Body length:** {r['body_length']}")
        lines.append(f"- **Expected:** `{r['expected']}`")
        lines.append(f"- **Found:** {'Yes' if r['passed'] else 'No'}")
        lines.append(f"\n```\n{r['preview']}\n```\n")

    return "\n".join(lines)


def main():
    service = get_gmail_service()
    emails = load_test_emails()

    results = []
    for email in emails:
        print(f"Testing: {email['label']}...", end=" ")
        result = test_email(service, email)
        results.append(result)
        print("PASS" if result["passed"] else "FAIL")

    report = format_report(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"parsing_{timestamp}.md"
    report_path.write_text(report)
    print(f"\nReport saved: {report_path}")

    if any(not r["passed"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
