#!/usr/bin/env python3
"""
validate-domain.py — check L1 domain files against the section pattern
that domain-summary.py expects to extract.

Required sections (any title containing the keyword):
  - "Entit"          (Core Entities / Key Entities / Entities)
  - "Business Rule"  (Business Rules / Key Business Rules)

Soft-recommended sections (warn if missing — needed for cross-module wiring):
  - "Events Emitted"
  - "Events Consumed"

Plus structural checks:
  - File starts with H1
  - All BR-IDs (BR-X##) are unique within the file
  - At least one BR-ID present in the Business Rules section

Usage:
    scripts/validate-domain.py knowledge/L1-domain/order-domain.md
    scripts/validate-domain.py                 # default: every <module>-domain.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import is_initialized

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = REPO_ROOT / "knowledge" / "L1-domain"


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or not lines[0].startswith("# "):
        issues.append(("ERROR", "missing H1 header on line 1"))

    # H2 sections
    h2_titles = [line[3:].strip().lower() for line in lines if line.startswith("## ")]

    if not any("entit" in t for t in h2_titles):
        # Some modules legitimately have no entities (e.g. reporting modules).
        # Domain-summary.py handles missing sections gracefully.
        issues.append(("WARN", "no '## Entities' / 'Core Entities' / 'Key Entities' section — domain-summary will show '(no section found)'"))
    if not any("business rule" in t for t in h2_titles):
        issues.append(("ERROR", "no '## Business Rules' section found — required by domain-summary.py"))

    if not any("events emitted" in t for t in h2_titles):
        issues.append(("WARN", "no '## Events Emitted' section — module may not participate in cross-module events"))
    if not any("events consumed" in t for t in h2_titles):
        issues.append(("WARN", "no '## Events Consumed' section"))

    # BR-IDs: only DEFINITIONS (table rows starting with | BR-X## |) must be unique.
    # References in other tables/prose may repeat freely.
    defined_br_ids: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = re.match(r"^\|\s*(BR-[A-Z0-9]+)\s*\|", line)
        if m:
            bid = m.group(1)
            if bid in defined_br_ids:
                issues.append(("ERROR", f"line {i+1}: duplicate BR-ID definition '{bid}' (also defined at line {defined_br_ids[bid]+1})"))
            else:
                defined_br_ids[bid] = i

    # Try to find BR-IDs specifically inside the Business Rules section
    br_section_start = None
    br_section_end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("## ") and "business rule" in line.lower():
            br_section_start = i
        elif br_section_start is not None and line.startswith("## "):
            br_section_end = i
            break
    if br_section_start is not None:
        br_block = "\n".join(lines[br_section_start:br_section_end])
        if not re.search(r"\bBR-[A-Z0-9]+\b", br_block):
            issues.append(("WARN", "Business Rules section has no BR-IDs (BR-X##) — agents won't have rules to cite"))

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        paths = sorted(p for p in DOMAIN_DIR.glob("*-domain.md") if not p.stem.endswith(".summary"))
        if not paths:
            if not is_initialized():
                print("note: no domain files yet and workspace not onboarded — skipping (run /onboard)")
                return 0
            print("error: no <module>-domain.md files under knowledge/L1-domain/", file=sys.stderr)
            return 2

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
        print(f"✓ {total} domain file(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} domain file(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
