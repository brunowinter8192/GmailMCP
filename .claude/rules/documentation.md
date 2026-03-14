---
paths:
  - "**/*.md"
  - "**/DOCS.md"
  - "**/README.md"
---

# Documentation Hierarchy

Every directory level has either a README.md or a DOCS.md.

## README.md

**Audience:** External user.
**Purpose:** Setup, installation, how to use, what is this project.
**Scope:** Only documents the level it lives on. Tree shows root-level files only, with one branch pointing to the DOCS.md.

**Required Sections:**
1. Title + one-liner description
2. Directory tree (root-level only, link to DOCS.md)
3. Setup / Installation
4. Environment Variables (if applicable)

**Rule:** README stops where DOCS begins. No redundancy.

## DOCS.md

**Audience:** Developer (human or AI).
**Purpose:** Documents everything on the level it lives on.
**Scope:** All modules, files, and structures in that directory.

**Module-level format:**
```markdown
## module_name.py

**Purpose:** What this module does.
**Input:** What it takes.
**Output:** What it returns.
```

**Subdirectory-level format (if applicable):**
Tables with Function | Description columns.

**Rules:**
- NO function-level documentation at module level (only Purpose/Input/Output)
- Describe WHAT not HOW
- Subdirectories with own depth get their own DOCS.md

## dev/ Suites

Every dev/ suite directory MUST have a DOCS.md.

**Pattern:** Numbered scripts (01_, 02_) with numbered report directories (01_reports/, 02_reports/).

**DOCS.md content:**
- Purpose of the suite
- Table: Script | Purpose
- Usage examples (how to run from project root)
