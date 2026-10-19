#!/usr/bin/env python3
"""
validate-legacy-scan.py — check legacy scan files against legacy-scan.schema.md.

Required sections (per schema §1–§7):
  1. Legacy Endpoints Involved
  2. Legacy Database Tables Involved
  3. Legacy Business Logic to Preserve
  4. Reverse Dependencies
  5. Current Test Coverage
  6. Risk Assessment
  7. Action Plan for Dev Agent

Required header fields:
  - Module
  - Ticket
  - Scan date (YYYY-MM-DD)
  - Breaking risk

Schema rule: blank fields not acceptable — "None" must be written explicitly.
We can't fully verify "None vs blank" without parsing each table, but we
do check that Section 7 is non-empty (Dev Agent reads this directly).

Usage:
    scripts/validate-legacy-scan.py knowledge/L2-legacy/scans/production-legacy-scan.md
    scripts/validate-legacy-scan.py     # default: all scans
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = REPO_ROOT / "knowledge" / "L2-legacy" / "scans"

REQUIRED_HEADER_FIELDS = ["Module", "Ticket", "Scan date", "Breaking risk"]

REQUIRED_SECTIONS = [
    "Legacy Endpoints Involved",
    "Legacy Database Tables Involved",
    "Legacy Business Logic to Preserve",
    "Reverse Dependencies",
    "Current Test Coverage",
    "Risk Assessment",
    "Action Plan for Dev Agent",
]


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")

    # H1 must look like: # Legacy Scan — <Module> / TICKET-NNN
    if not re.search(r"^# Legacy Scan\b", text, re.MULTILINE):
        issues.append(("ERROR", "missing or malformed H1 — expected '# Legacy Scan — <Module> / TICKET-XXX'"))

    for field in REQUIRED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required header field: **{field}:**"))

    # Scan date format
    sd_match = re.search(r"^\*\*Scan date:\*\*\s+(\S+)", text, re.MULTILINE)
    if sd_match and not re.match(r"^\d{4}-\d{2}-\d{2}$", sd_match.group(1).strip()):
        issues.append(("ERROR", f"Scan date '{sd_match.group(1).strip()}' not in YYYY-MM-DD format"))

    # Breaking risk value — must START with High/Medium/Low/N/A; trailing prose ok
    br_match = re.search(r"^\*\*Breaking risk:\*\*\s+(\S.+)$", text, re.MULTILINE)
    if br_match:
        val = br_match.group(1).strip()
        first_token = re.split(r"[\s—,;:]", val, maxsplit=1)[0]
        if first_token not in {"High", "Medium", "Low", "N/A"}:
            issues.append(("ERROR", f"Breaking risk must start with High/Medium/Low/N/A — got '{first_token}'"))

    # Sections — match by header anywhere (allow numbered like "## 1. Legacy Endpoints...")
    for section in REQUIRED_SECTIONS:
        pattern = rf"^## (?:\d+\.\s+)?{re.escape(section)}\s*$"
        if not re.search(pattern, text, re.MULTILINE):
            issues.append(("ERROR", f"missing required section: ## {section}"))

    # Section 7 (Action Plan) must be non-empty
    ap_match = re.search(
        r"^## (?:\d+\.\s+)?Action Plan for Dev Agent\s*$(.*?)(?=^## |\Z)",
        text, re.MULTILINE | re.DOTALL,
    )
    if ap_match:
        body = ap_match.group(1).strip()
        if not body or len(body) < 30:
            issues.append(("ERROR", "Action Plan for Dev Agent section is empty or too short — Dev reads this directly"))

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        if SCAN_DIR.exists():
            paths = sorted(SCAN_DIR.glob("*-legacy-scan.md"))
        else:
            paths = []
        if not paths:
            print("✓ 0 legacy scans (no files yet)")
            return 0

    overall_errors = 0
    overall_warns = 0
    files_with_issues = 0

    for path in paths:
        issues = issues_for(path)
        errors = [i for i in issues if i[0] == "ERROR"]
        warns = [i for i in issues if i[0] == "WARN"]
        overall_errors += len(errors)
        overall_warns += len(warns)
        if issues:
            files_with_issues += 1
            try:
                rel = path.resolve().relative_to(REPO_ROOT)
            except ValueError:
                rel = path
            print(f"\n{rel}")
            for sev, msg in issues:
                print(f"  [{sev}] {msg}")

    total = len(paths)
    if files_with_issues == 0:
        print(f"✓ {total} legacy scan(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} scan(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
