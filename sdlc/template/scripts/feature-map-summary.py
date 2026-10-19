#!/usr/bin/env python3
"""
feature-map-summary.py — regenerate <module>.summary.md from <module>.md.

The summary is a 3-column (ID + Feature + Status) skinny index that agents
load FIRST when they only need to look up a feature ID. The full per-module
file is loaded only when row-level detail is needed (endpoints, FE pages,
permissions, dependencies, legacy flag, notes).

The summary is a derived artifact. Never edit it by hand — run this script
(or rely on the pre-commit hook, which regenerates automatically when the
full file is staged).

Usage:
    scripts/feature-map-summary.py production
    scripts/feature-map-summary.py --all                # regenerate every module
    scripts/feature-map-summary.py --check production   # exit 1 if summary is out of date
    scripts/feature-map-summary.py --check --all        # check all modules

Exit:
    0 = success / no drift
    1 = drift detected (in --check mode) or generation failure
    2 = usage error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PER_MODULE_DIR = REPO_ROOT / "architecture" / "feature-map"


def parse_full_file(path: Path) -> tuple[list[tuple[str, str, str]], str | None]:
    """Return (rows, error). rows = [(id, feature, status), ...].
    Walks every feature table inside the '## Features' H2 section.
    Tables under '## Cross-module touchpoints' (or any other H2) are
    excluded — those rows reference OTHER modules' feature IDs and
    don't belong in this module's summary."""
    if not path.exists():
        return [], f"file not found: {path}"

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Locate '## Features' section bounds: from that line until the next H2 (or EOF)
    features_start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Features":
            features_start = i + 1
            break
    if features_start is None:
        return [], f"no '## Features' section found in {path}"

    features_end = len(lines)
    for i in range(features_start, len(lines)):
        if lines[i].startswith("## "):
            features_end = i
            break

    # Find table headers WITHIN the Features section
    header_positions = [
        i for i in range(features_start, features_end)
        if lines[i].startswith("|") and "| ID " in lines[i] and "| Feature " in lines[i]
    ]
    if not header_positions:
        return [], f"no feature table found in '## Features' section of {path}"

    rows: list[tuple[str, str, str]] = []

    for header_idx in header_positions:
        header_cols = [c.strip() for c in lines[header_idx].strip("|").split("|")]
        try:
            idx_id = header_cols.index("ID")
            idx_feature = header_cols.index("Feature")
            idx_status = header_cols.index("Status")
        except ValueError:
            continue

        # Skip header + separator line, collect rows until non-pipe or end of section
        for j in range(header_idx + 2, features_end):
            line = lines[j].rstrip()
            if not line.startswith("|"):
                break
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) <= max(idx_id, idx_feature, idx_status):
                continue
            rows.append((cols[idx_id], cols[idx_feature], cols[idx_status]))

    return rows, None


def render_summary(module: str, rows: list[tuple[str, str, str]]) -> str:
    title = module.replace("-", " ").title()
    lines: list[str] = []
    lines.append(f"# {title} — Feature Summary")
    lines.append("")
    lines.append(f"> Auto-generated from `{module}.md` by `scripts/feature-map-summary.py`.")
    lines.append("> DO NOT EDIT manually — the pre-commit hook regenerates this when the full file changes.")
    lines.append(">")
    lines.append("> Load THIS summary first when you only need to find a feature ID or status.")
    lines.append(f"> Load the full `{module}.md` only when you need row-level detail")
    lines.append("> (endpoints, FE pages, permissions, dependencies, legacy flag, notes).")
    lines.append("")
    lines.append(f"**Total features:** {len(rows)}")
    lines.append("")
    lines.append("| ID | Feature | Status |")
    lines.append("|---|---|---|")
    for fid, name, status in rows:
        lines.append(f"| {fid} | {name} | {status} |")
    lines.append("")
    return "\n".join(lines)


def generate(module: str, check_only: bool = False) -> tuple[int, str]:
    """Returns (exit_code, message)."""
    full_path = PER_MODULE_DIR / f"{module}.md"
    summary_path = PER_MODULE_DIR / f"{module}.summary.md"

    rows, err = parse_full_file(full_path)
    if err:
        return 1, f"✗ {module}: {err}"

    new_content = render_summary(module, rows)

    if check_only:
        if not summary_path.exists():
            return 1, f"✗ {module}: summary missing — run scripts/feature-map-summary.py {module}"
        existing = summary_path.read_text(encoding="utf-8")
        if existing.rstrip("\n") != new_content.rstrip("\n"):
            return 1, f"✗ {module}: summary out of date — run scripts/feature-map-summary.py {module}"
        return 0, f"✓ {module}: summary up to date ({len(rows)} features)"

    summary_path.write_text(new_content, encoding="utf-8")
    return 0, f"✓ {module}: regenerated {summary_path.relative_to(REPO_ROOT)} ({len(rows)} features)"


def discover_modules() -> list[str]:
    if not PER_MODULE_DIR.exists():
        return []
    return sorted(
        p.stem for p in PER_MODULE_DIR.glob("*.md")
        if not p.stem.endswith(".summary")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", nargs="?", help="Module name (e.g. 'production'). Omit with --all.")
    parser.add_argument("--all", action="store_true", help="Process every module under architecture/feature-map/")
    parser.add_argument("--check", action="store_true", help="Verify summary is up to date; do not write")
    args = parser.parse_args()

    if args.all:
        modules = discover_modules()
        if not modules:
            # No per-module feature-map files yet (fresh workspace, SA hasn't run) — nothing to check.
            print("note: no modules under architecture/feature-map/ yet — skipping (SA creates them on first touch)")
            return 0
    elif args.module:
        modules = [args.module]
    else:
        parser.print_usage(file=sys.stderr)
        return 2

    overall = 0
    for m in modules:
        code, msg = generate(m, check_only=args.check)
        print(msg)
        if code != 0:
            overall = code
    return overall


if __name__ == "__main__":
    sys.exit(main())
