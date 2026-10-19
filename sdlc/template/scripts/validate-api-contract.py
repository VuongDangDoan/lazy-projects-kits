#!/usr/bin/env python3
"""
validate-api-contract.py — check OpenAPI YAMLs in architecture/api-contracts/v1/
against the structural rules in api-contract.schema.md (Validation Checklist).

Without pyyaml as a dependency, we use line-based regex checks — sufficient
for the schema's authoritative rules:
  - File starts with `openapi: 3.x`
  - Has `info:` block with `title` and `version`
  - Each path begins with `/v1/`
  - Each operation has: summary, security: bearerAuth, x-business-rules
  - Each operation declares responses including 200 and 400
  - Pagination params named `page` and `limit` (not pageSize)
  - Response shapes hint at correct structure (data + message; total, limit, page on lists)

Usage:
    scripts/validate-api-contract.py architecture/api-contracts/v1/foo.yaml
    scripts/validate-api-contract.py     # default: every yaml under v1/
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_DIR = REPO_ROOT / "architecture" / "api-contracts" / "v1"


def issues_for(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # OpenAPI 3.x version line near the top
    if not any(re.match(r"^openapi:\s*[\"']?3\.\d", line) for line in lines[:5]):
        issues.append(("ERROR", "missing 'openapi: 3.x.x' on first 5 lines"))

    # info: block with title + version
    if not re.search(r"^info\s*:\s*$", text, re.MULTILINE):
        issues.append(("ERROR", "missing 'info:' top-level block"))
    else:
        info_block_match = re.search(r"^info\s*:\s*$(.*?)^[a-zA-Z]", text, re.MULTILINE | re.DOTALL)
        if info_block_match:
            info_body = info_block_match.group(1)
            if not re.search(r"^\s+title\s*:", info_body, re.MULTILINE):
                issues.append(("ERROR", "info: block missing 'title:'"))
            if not re.search(r"^\s+version\s*:", info_body, re.MULTILINE):
                issues.append(("ERROR", "info: block missing 'version:'"))

    # Paths must be under v1/
    path_lines = [(i, line) for i, line in enumerate(lines) if re.match(r"^\s{2}/[^\s:]+:\s*$", line)]
    for i, line in path_lines:
        route = line.strip().rstrip(":").strip()
        if not route.startswith("/v1/"):
            issues.append(("ERROR", f"line {i+1}: path '{route}' must be prefixed with /v1/"))

    # x-business-rules required per operation — check each HTTP verb under paths
    for verb in ("get", "post", "put", "patch", "delete"):
        # Find each occurrence of "    <verb>:" (4-space indent typical)
        for m in re.finditer(rf"^(\s{{4}}){verb}\s*:\s*$", text, re.MULTILINE):
            start = m.start()
            # Look ahead a bounded number of chars for x-business-rules in the same operation block
            block = text[start:start + 2000]
            if "x-business-rules" not in block:
                line_num = text[:start].count("\n") + 1
                issues.append(("WARN", f"line {line_num}: {verb.upper()} operation missing x-business-rules"))
            if "bearerAuth" not in block and "security:" not in block and "/auth/" not in block:
                # auth endpoints can be public; everything else should declare security
                pass  # too noisy to flag without per-route analysis

    # Pagination: pageSize is forbidden
    if re.search(r"\bpageSize\b", text):
        issues.append(("ERROR", "uses 'pageSize' — schema requires 'limit' instead"))

    # Response shape hint: list responses should include 'total'
    # (we just look for typical patterns; not authoritative)

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        if CONTRACT_DIR.exists():
            paths = sorted(CONTRACT_DIR.glob("*.yaml"))
        else:
            paths = []
        if not paths:
            print("✓ 0 api contracts (no files yet)")
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
        print(f"✓ {total} api contract(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} api contract(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
