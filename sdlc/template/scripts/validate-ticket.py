#!/usr/bin/env python3
"""
validate-ticket.py — check a TICKET-XXX.md against task-ticket.schema.md

Usage:
    scripts/validate-ticket.py tasks/tickets/TICKET-001.md
    scripts/validate-ticket.py tasks/tickets/TICKET-*.md

Exit: 0 = all valid, 1 = at least one ticket has issues, 2 = usage error.

Severity:
    ERROR    — schema violation, blocks downstream agents
    WARN     — recommended but not blocking
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import module_slugs

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = [
    "Task Description",
    "Input — Dev Agent must read",
    "Acceptance Criteria",
    "Definition of Done",
    "Dependencies",
    "SA Summary",
    "Dev Notes",
]

REQUIRED_HEADER_FIELDS = ["US-ID", "Module", "Layer", "Status", "Complexity"]
RECOMMENDED_HEADER_FIELDS = ["Sprint", "Assignee"]

VALID_LAYERS = {"BE", "FE", "MOBILE", "BE+FE", "MOBILE+BE", "BE+FE+MOBILE"}
VALID_STATUSES = {"Todo", "In Progress", "In Review", "Done"}
VALID_COMPLEXITY = {"XXS", "XS", "S", "M", "L", "XL"}


def issues_for(path: Path) -> list[tuple[str, str]]:
    """Return (severity, message) tuples for any problems found in this ticket."""
    issues: list[tuple[str, str]] = []

    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")

    # H1 must look like: # TICKET-NNN — Short Title
    h1_match = re.search(r"^# (TICKET-(\d{3,}))\s+—\s+.+$", text, re.MULTILINE)
    if not h1_match:
        issues.append(("ERROR", "missing or malformed H1 — expected '# TICKET-NNN — Short Title'"))
    else:
        ticket_id = h1_match.group(1)
        # Filename should match
        if path.stem != ticket_id:
            issues.append(("ERROR", f"filename {path.name} does not match H1 id {ticket_id}"))

    # Required header fields
    for field in REQUIRED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required header field: **{field}:**"))
    for field in RECOMMENDED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("WARN", f"missing recommended header field: **{field}:**"))

    # Layer / Status / Complexity values
    layer_m = re.search(r"^\*\*Layer:\*\*\s+(\S.+)$", text, re.MULTILINE)
    if layer_m and layer_m.group(1).strip() not in VALID_LAYERS:
        issues.append(("ERROR", f"Layer '{layer_m.group(1).strip()}' not in {sorted(VALID_LAYERS)}"))

    status_m = re.search(r"^\*\*Status:\*\*\s+(\S.+)$", text, re.MULTILINE)
    if status_m and status_m.group(1).strip() not in VALID_STATUSES:
        issues.append(("ERROR", f"Status '{status_m.group(1).strip()}' not in {sorted(VALID_STATUSES)}"))

    cx_m = re.search(r"^\*\*Complexity:\*\*\s+(\S+)", text, re.MULTILINE)
    if cx_m and cx_m.group(1).strip() not in VALID_COMPLEXITY:
        issues.append(("ERROR", f"Complexity '{cx_m.group(1).strip()}' not in {sorted(VALID_COMPLEXITY)}"))

    known_modules = module_slugs()
    module_m = re.search(r"^\*\*Module:\*\*\s+(\S.+)$", text, re.MULTILINE)
    if module_m and known_modules and module_m.group(1).strip() not in known_modules:
        issues.append(("WARN", f"Module '{module_m.group(1).strip()}' not in project.config.json modules {sorted(known_modules)}"))

    # US-ID referenced should exist
    us_m = re.search(r"^\*\*US-ID:\*\*\s+(US-\d{3,})", text, re.MULTILINE)
    if us_m:
        us_path = REPO_ROOT / "docs" / "user-stories" / f"{us_m.group(1)}.md"
        if not us_path.exists():
            issues.append(("WARN", f"referenced US file does not exist: {us_path.relative_to(REPO_ROOT)}"))

    # Required sections
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^## {re.escape(section)}\s*$", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required section: ## {section}"))

    # Acceptance Criteria must contain at least one GIVEN/WHEN/THEN block
    ac_block = _section_text(text, "Acceptance Criteria")
    if ac_block is not None:
        if not (re.search(r"\bGIVEN\b", ac_block) and re.search(r"\bWHEN\b", ac_block) and re.search(r"\bTHEN\b", ac_block)):
            issues.append(("ERROR", "Acceptance Criteria has no GIVEN/WHEN/THEN block"))

    # SA Summary must mention Endpoints (with or without (s)) and Legacy flag
    sa_block = _section_text(text, "SA Summary")
    if sa_block is not None:
        if not re.search(r"\*\*Endpoints?(\(s\))?", sa_block):
            issues.append(("WARN", "SA Summary missing **Endpoint(s):** / **Endpoints:** sub-field"))
        if not re.search(r"\*\*Legacy flag", sa_block):
            issues.append(("WARN", "SA Summary missing **Legacy flag:** sub-field"))

    # Definition of Done should contain at least one checklist item
    dod = _section_text(text, "Definition of Done")
    if dod is not None and not re.search(r"^\s*-\s*\[ ?[xX ]?\]", dod, re.MULTILINE):
        issues.append(("WARN", "Definition of Done has no checklist items"))

    return issues


def _section_text(text: str, header: str) -> str | None:
    """Return the text of the section under '## <header>' up to the next '## ' or EOF."""
    pattern = rf"^## {re.escape(header)}\s*$(.*?)(?=^## |\Z)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate-ticket.py <TICKET-XXX.md>...", file=sys.stderr)
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
        print(f"✓ {total} ticket(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} ticket(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
