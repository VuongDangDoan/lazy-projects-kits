#!/usr/bin/env python3
"""
validate-us.py — check a US-NNN.md against user-story.schema.md v2.0

v2.0 dropped Epic/Priority/Status headers, verbose Legacy Notes, and the
Estimated Complexity section (SA owns complexity via x-dev-notes).

Usage:
    scripts/validate-us.py docs/user-stories/US-001.md
    scripts/validate-us.py docs/user-stories/US-*.md

Exit: 0 = all valid, 1 = at least one US has issues, 2 = usage error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import module_slugs

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = [
    "User Story",
    "Business Rule Refs",
    "Acceptance Criteria",
    "SA Handoff Notes",
    "Legacy",
]

REQUIRED_HEADER_FIELDS = ["Module"]


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")

    # H2 (per template): ## US-NNN — Title
    h_match = re.search(r"^## (US-(\d{3,}))\s+—\s+.+$", text, re.MULTILINE)
    if not h_match:
        issues.append(("ERROR", "missing or malformed heading — expected '## US-NNN — Short Title'"))
    else:
        us_id = h_match.group(1)
        if path.stem != us_id:
            issues.append(("ERROR", f"filename {path.name} does not match heading id {us_id}"))

    # Required header fields
    for field in REQUIRED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required header field: **{field}:**"))

    known_modules = module_slugs()
    module_m = re.search(r"^\*\*Module:\*\*\s+(\S.+)$", text, re.MULTILINE)
    if module_m and known_modules and module_m.group(1).strip() not in known_modules:
        issues.append(("WARN", f"Module '{module_m.group(1).strip()}' not in project.config.json modules {sorted(known_modules)}"))

    # Required sections (### level in US schema)
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^### {re.escape(section)}\s*$", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required section: ### {section}"))

    # User Story sentence pattern: As a ... I want ... so that ...
    us_block = _section_text(text, "User Story")
    if us_block is not None:
        if not re.search(r"\bAs a\b.+\bI want\b.+\bso that\b", us_block, re.IGNORECASE | re.DOTALL):
            issues.append(("WARN", "User Story doesn't match 'As a ... I want ... so that ...' pattern"))

    # AC: 2–6, each must have GIVEN/WHEN/THEN
    ac_block = _section_text(text, "Acceptance Criteria")
    if ac_block is not None:
        ac_count = len(re.findall(r"^\*\*AC\d+\b", ac_block, re.MULTILINE))
        if ac_count < 2:
            issues.append(("ERROR", f"need at least 2 ACs (found {ac_count})"))
        if ac_count > 6:
            issues.append(("WARN", f"more than 6 ACs ({ac_count}) — consider splitting the story"))
        for given_match in re.finditer(r"^\*\*AC(\d+).*?(?=^\*\*AC|\Z)", ac_block, re.MULTILINE | re.DOTALL):
            chunk = given_match.group(0)
            if not (re.search(r"\bGIVEN\b", chunk) and re.search(r"\bWHEN\b", chunk) and re.search(r"\bTHEN\b", chunk)):
                issues.append(("ERROR", f"AC{given_match.group(1)} missing GIVEN/WHEN/THEN"))

    # SA Handoff Notes — Entities sub-block required; events sub-block recommended
    sa_block = _section_text(text, "SA Handoff Notes")
    if sa_block is not None:
        if not re.search(r"\*\*Entities", sa_block):
            issues.append(("ERROR", "SA Handoff Notes missing **Entities involved:** sub-block"))
        if not re.search(r"\*\*Inter-module events", sa_block):
            issues.append(("WARN", "SA Handoff Notes missing **Inter-module events:** sub-block (write it even if empty/None)"))

    # Legacy — one-line boolean + ref
    legacy_block = _section_text(text, "Legacy")
    if legacy_block is not None:
        touch_m = re.search(r"\*\*Touches legacy\?\*\*\s+(\S.*)$", legacy_block, re.MULTILINE)
        if not touch_m:
            issues.append(("ERROR", "Legacy section missing '**Touches legacy?** [No | Yes — see scan ref]' line"))
        elif touch_m.group(1).strip().lower().startswith("yes") and "legacy-scan" not in legacy_block:
            issues.append(("WARN", "Touches legacy = Yes but no legacy-scan reference given"))

    return issues


def _section_text(text: str, header: str) -> str | None:
    pattern = rf"^### {re.escape(header)}\s*$(.*?)(?=^### |\Z)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate-us.py <US-NNN.md>...", file=sys.stderr)
        return 2

    overall_errors = 0
    overall_warns = 0
    files_with_issues = 0

    for arg in argv[1:]:
        path = Path(arg)
        issues = issues_for(path)
        errors = [i for i in issues if i[0] == "ERROR"]
        warns = [i for i in issues if i[0] == "WARN"]
        overall_errors += len(errors)
        overall_warns += len(warns)
        if issues:
            files_with_issues += 1
            print(f"\n{path}")
            for sev, msg in issues:
                print(f"  [{sev}] {msg}")

    total = len(argv) - 1
    if files_with_issues == 0:
        print(f"✓ {total} user story/stories valid")
        return 0
    print(f"\n{files_with_issues}/{total} user story/stories have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
