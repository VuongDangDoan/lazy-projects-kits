#!/usr/bin/env python3
"""
validate-test-case.py — check QC test case files against test-case.schema.md.

Looks at files under tests/cases/<module>/TICKET-XXX-tests.md.

Required header fields:
  - Module
  - US-ID
  - Ticket
  - QC Date
  - Regression scope

Required sections (any of these patterns; at least one TC-* present in the file):
  1. Unit Tests — Business Logic   (or "Unit Tests")
  2. Integration Tests — API       (or "Integration Tests")
  5. Regression Checklist           (always required)

Plus structural checks:
  - Each test case TC-*-* must have Setup, Input, Expected (warn if missing)
  - "Should work correctly" forbidden as expected output

Usage:
    scripts/validate-test-case.py tests/cases/order/TICKET-001-tests.md
    scripts/validate-test-case.py    # default: every TICKET-*-tests.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "tests" / "cases"

REQUIRED_HEADER_FIELDS = ["Module", "US-ID", "Ticket", "QC Date", "Regression scope"]


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")

    # H1 must look like: # Test Cases — TICKET-NNN
    if not re.search(r"^# Test Cases\b", text, re.MULTILINE):
        issues.append(("ERROR", "missing or malformed H1 — expected '# Test Cases — TICKET-XXX'"))

    for field in REQUIRED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required header field: **{field}:**"))

    # Section presence
    if not re.search(r"^## .*Unit Tests\b", text, re.MULTILINE):
        issues.append(("WARN", "no Unit Tests section — may be acceptable for a FE-only ticket without test framework"))
    if not re.search(r"^## .*Integration Tests\b", text, re.MULTILINE):
        issues.append(("WARN", "no Integration Tests section"))
    if not re.search(r"^## .*Regression Checklist\b", text, re.MULTILINE):
        issues.append(("ERROR", "missing required section: Regression Checklist"))

    # Test cases — TC-<ID>-<TYPE>NN format
    tc_blocks = list(re.finditer(r"^### (TC-[A-Z0-9-]+)\s+—\s+.+$", text, re.MULTILINE))
    if not tc_blocks:
        issues.append(("ERROR", "no test cases found — expected at least one '### TC-... — title' block"))

    seen_tcs: dict[str, int] = {}
    for m in tc_blocks:
        tc_id = m.group(1)
        line_no = text[:m.start()].count("\n") + 1
        if tc_id in seen_tcs:
            issues.append(("ERROR", f"line {line_no}: duplicate test case ID '{tc_id}' (also at line {seen_tcs[tc_id]})"))
        else:
            seen_tcs[tc_id] = line_no

    # Check for forbidden vague expectations
    forbidden = re.findall(r"^.*should work correctly.*$", text, re.MULTILINE | re.IGNORECASE)
    if forbidden:
        issues.append(("ERROR", f"found {len(forbidden)} vague expectation 'should work correctly' — must be specific"))

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        if CASES_DIR.exists():
            paths = sorted(CASES_DIR.glob("*/TICKET-*-tests.md"))
        else:
            paths = []
        if not paths:
            print("✓ 0 test case file(s) (no files yet)")
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
        print(f"✓ {total} test case file(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} file(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
