# Parsing Suite

Test suite for evaluating and tuning Gmail email body parsing quality.

## test_emails.txt

**Purpose:** Test corpus of Gmail message IDs with expected content snippets.

Format: `message_id|label|expected_content_snippet` (one per line, `#` comments).

Add new test emails when encountering parsing issues with new email types (newsletters, LinkedIn notifications, transactional emails, etc.).

## 01_inspect_structure.py

**Purpose:** Inspect raw MIME structure of Gmail messages. Shows part types, sizes, and nesting — essential for debugging why `extract_body` picks the wrong part.
**Input:** Single message ID (CLI arg) or `--all` for entire test corpus.
**Output:** Markdown report in `01_reports/` with MIME part table per email.

```bash
python dev/parsing_suite/01_inspect_structure.py 19ce2f980b31a595
python dev/parsing_suite/01_inspect_structure.py --all
```

### inspect_message()

Fetches full message via Gmail API, walks MIME parts recursively, collects depth/mime/size/data presence per part.

### format_report()

Builds markdown with per-email MIME structure tables.

## 02_test_parsing.py

**Purpose:** Regression test for body parsing. Runs all test emails through `extract_body` + `clean_body` and checks that expected content snippets appear in output.
**Input:** test_emails.txt (automatic).
**Output:** Markdown report in `02_reports/` with PASS/FAIL per email + body preview.

```bash
python dev/parsing_suite/02_test_parsing.py
```

Exits with code 1 if any test fails. Expected snippets are case-insensitive substring matches.

### test_email()

Fetches full message, runs through `extract_body` → `clean_body` pipeline (same as MCP `read_email` tool), checks for expected snippet.

### format_report()

Summary table (PASS/FAIL counts) + per-email section with body preview (first 300 chars).

## Workflow

1. Encounter parsing issue with a new email type
2. Add message ID + label + expected snippet to `test_emails.txt`
3. Run `01_inspect_structure.py --all` to understand MIME structure
4. Fix parsing logic in `src/gmail/formatting.py`
5. Run `02_test_parsing.py` to verify fix + no regressions
6. Read report in `02_reports/`
