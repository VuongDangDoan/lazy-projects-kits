#!/usr/bin/env python3
"""
validate-e2e-case.py — check E2E case files under tests/e2e/cases/<module>/.

Required header fields:
  - Module
  - Linked ticket
  - Linked AC
  - Created
  - Owner
  - Browser
  - Auth as
  - Environment
  - Tags

Required sections:
  1. Preconditions      (≥1 item)
  2. Steps              (each step has Action AND Expected; total ≤15)
  3. Cleanup            (one strategy chosen)

Filename:
  - tests/e2e/cases/<module>/TC-E-NNN-<slug>.md
  - NNN is zero-padded
  - module dir matches one of the allowed modules

Usage:
    scripts/validate-e2e-case.py tests/e2e/cases/order/TC-E-001-create-order.md
    scripts/validate-e2e-case.py    # default: every TC-E-*.md under cases/
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import module_slugs

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "tests" / "e2e" / "cases"

REQUIRED_HEADER_FIELDS = [
    "Module", "Linked ticket", "Linked AC", "Created",
    "Owner", "Browser", "Auth as", "Environment", "Tags",
]
MAX_STEPS = 15


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    # Filename: TC-E-NNN-<slug>.md
    if not re.match(r"^TC-E-\d{3,}-[a-z0-9-]+\.md$", path.name):
        issues.append(("ERROR", f"filename '{path.name}' doesn't match TC-E-NNN-<slug>.md"))

    # Parent dir = module
    known_modules = module_slugs()
    if known_modules and path.parent.name not in known_modules:
        issues.append(("WARN", f"parent dir '{path.parent.name}' not in project.config.json modules {sorted(known_modules)}"))

    text = path.read_text(encoding="utf-8")

    # H1 with TC-E-NNN
    if not re.search(r"^# E2E Test Case — TC-E-\d{3,}", text, re.MULTILINE):
        issues.append(("ERROR", "missing or malformed H1 — expected '# E2E Test Case — TC-E-NNN — Title'"))

    for field in REQUIRED_HEADER_FIELDS:
        if not re.search(rf"^\*\*{re.escape(field)}:\*\*", text, re.MULTILINE):
            issues.append(("ERROR", f"missing required header field: **{field}:**"))

    # Section §1 Preconditions — at least 1 checkbox item
    pre_match = re.search(r"^## 1\..*Preconditions\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if pre_match:
        if not re.search(r"^\s*-\s*\[ ?[xX ]?\]", pre_match.group(1), re.MULTILINE):
            issues.append(("ERROR", "Preconditions section has no checklist items"))
    else:
        issues.append(("ERROR", "missing required section: ## 1. Preconditions"))

    # Section §2 Steps — each step has Action AND Expected; ≤15 steps
    steps_match = re.search(r"^## 2\..*Steps\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if steps_match:
        body = steps_match.group(1)
        step_headers = re.findall(r"^### Step (\d+)", body, re.MULTILINE)
        if not step_headers:
            issues.append(("ERROR", "Steps section has no '### Step N' blocks"))
        elif len(step_headers) > MAX_STEPS:
            issues.append(("ERROR", f"{len(step_headers)} steps — schema cap is {MAX_STEPS}; split this case"))

        # Each step block should mention Action and Expected
        for step_block in re.finditer(r"^### Step (\d+).*?(?=^### Step |\Z)", body, re.MULTILINE | re.DOTALL):
            chunk = step_block.group(0)
            step_num = step_block.group(1)
            if "**Action:**" not in chunk:
                issues.append(("ERROR", f"Step {step_num}: missing **Action:**"))
            if "**Expected:**" not in chunk:
                issues.append(("ERROR", f"Step {step_num}: missing **Expected:**"))
    else:
        issues.append(("ERROR", "missing required section: ## 2. Steps"))

    # Section §3 Cleanup
    if not re.search(r"^## 3\..*Cleanup\s*$", text, re.MULTILINE):
        issues.append(("WARN", "missing recommended section: ## 3. Cleanup"))

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        if CASES_DIR.exists():
            paths = sorted(CASES_DIR.glob("*/TC-E-*.md"))
        else:
            paths = []
        if not paths:
            print("✓ 0 e2e case file(s) (no files yet)")
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
        print(f"✓ {total} e2e case file(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} file(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
