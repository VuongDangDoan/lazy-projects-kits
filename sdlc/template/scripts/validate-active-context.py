#!/usr/bin/env python3
"""
validate-active-context.py — cross-validate BR-IDs in active-context.md against
the canonical Business Rules tables in knowledge/L1-domain/<module>-domain.md §4.

Catches the silent-drift case where SA writes "BR-O42 in scope" but BR-O42 was
never defined in order-domain.md — every downstream agent then enforces a rule
that does not exist.

Exit codes:
  0 — all BR-IDs in active-context resolve to a domain rule
  1 — one or more BR-IDs are missing or unparseable

Usage:
  scripts/validate-active-context.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import br_prefix_map

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVE_CTX = REPO_ROOT / "knowledge/L3-session/active-context.md"
DOMAIN_DIR = REPO_ROOT / "knowledge/L1-domain"

# BR prefix → domain file, from project.config.json modules[].br_prefix.
# Empty when the workspace isn't onboarded yet → fall back to scanning all domain files.
PREFIX_MAP = br_prefix_map()

BR_PATTERN = re.compile(r"\bBR-[A-Z]+\d+\b")


def load_known_brs() -> dict[str, set[str]]:
    """Return {domain_filename: {BR-IDs found in §4 table}}."""
    known: dict[str, set[str]] = {}
    for domain_path in DOMAIN_DIR.glob("*-domain.md"):
        text = domain_path.read_text()
        # Extract §4 Business Rules section (until next ## heading)
        m = re.search(r"^## 4\. Business Rules\s*$(.*?)(?=^## )", text, re.M | re.S)
        if not m:
            known[domain_path.name] = set()
            continue
        section = m.group(1)
        known[domain_path.name] = set(BR_PATTERN.findall(section))
    return known


def domain_for_br(br: str) -> str | None:
    """Map a BR-ID to its expected domain filename. Longest prefix wins."""
    for prefix in sorted(PREFIX_MAP, key=len, reverse=True):
        if br.startswith(prefix):
            return PREFIX_MAP[prefix]
    return None


def find_in_scope_blocks(text: str) -> list[tuple[int, str]]:
    """
    Return (line_number, line_text) for every line that contains
    "Business Rules in Scope:" or "Business Rules:" — these are the lines
    where SA declares which BRs apply to the active feature.
    """
    matches = []
    for i, line in enumerate(text.splitlines(), start=1):
        # Match: **Business Rules in Scope:** ...   OR   **Business Rules:** ...
        # (colon may appear inside the bold or right after the closing **)
        if re.search(r"\*\*Business Rules?\b[^*]*\*\*\s*:?", line, re.I):
            matches.append((i, line))
    return matches


def main() -> int:
    if not ACTIVE_CTX.exists():
        print(f"⚠ {ACTIVE_CTX} not found — nothing to validate", file=sys.stderr)
        return 0

    text = ACTIVE_CTX.read_text()
    known = load_known_brs()

    in_scope_lines = find_in_scope_blocks(text)
    if not in_scope_lines:
        print("⚠ no 'Business Rules in Scope' line found in active-context.md")
        print("  (this is OK for non-domain refactors — skipping)")
        return 0

    failures: list[str] = []
    total_checked = 0

    for line_no, line in in_scope_lines:
        # Skip "None" declarations (colon may be inside bold: "**Business Rules in Scope:** None")
        if re.search(r":\s*\**\s*None\b", line, re.I):
            print(f"  ✓ line {line_no}: 'None' (no BR validation needed)")
            continue
        brs = BR_PATTERN.findall(line)
        if not brs:
            failures.append(
                f"line {line_no}: 'Business Rules in Scope' line has no parseable BR-IDs "
                f"and is not 'None' — write 'None' or list IDs explicitly\n"
                f"     {line.strip()}"
            )
            continue
        for br in brs:
            total_checked += 1
            domain_file = domain_for_br(br)
            if domain_file is None:
                # No prefix mapping — accept the BR if it exists in ANY domain file
                if any(br in br_set for br_set in known.values()):
                    print(f"  ✓ line {line_no}: {br} (resolved by full scan)")
                    continue
                failures.append(
                    f"line {line_no}: {br} — unknown prefix and not found in any domain file; "
                    f"add the module's br_prefix to project.config.json"
                )
                continue
            if domain_file not in known:
                failures.append(
                    f"line {line_no}: {br} should live in {domain_file} but that file is missing"
                )
                continue
            if br not in known[domain_file]:
                failures.append(
                    f"line {line_no}: {br} not found in {domain_file} §4 Business Rules table"
                )
            else:
                print(f"  ✓ line {line_no}: {br} → {domain_file}")

    if failures:
        print()
        print(f"✗ {len(failures)} BR validation issue(s):")
        for f in failures:
            print(f"  - {f}")
        return 1

    if total_checked == 0:
        print("  (no BR-IDs to check — only 'None' declarations)")
    else:
        print(f"\n✓ all {total_checked} BR-ID(s) resolve to a domain rule")
    return 0


if __name__ == "__main__":
    sys.exit(main())
