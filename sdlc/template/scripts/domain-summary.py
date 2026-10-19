#!/usr/bin/env python3
"""
domain-summary.py — regenerate <module>-domain.summary.md from <module>-domain.md.

The summary keeps the four sections agents look up most often:
  - Entities (Core Entities / Key Entities / etc.)
  - Business Rules (Key Business Rules / etc.)
  - Events Emitted
  - Events Consumed

Everything else (Domain Overview, State Machines with diagrams, Calculations,
API Endpoints, Roles & Permissions, Legacy Notes, References, Test Coverage)
stays in the full file. Agents load the summary first; load the full file only
when they need state machines or implementation context.

Usage:
    scripts/domain-summary.py production
    scripts/domain-summary.py --all
    scripts/domain-summary.py --check production
    scripts/domain-summary.py --check --all

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
DOMAIN_DIR = REPO_ROOT / "knowledge" / "L1-domain"


def classify_section_title(title_lower: str) -> str | None:
    """Map an H2 title (lowercased) to a known section kind, or None to skip."""
    # Order matters: more specific keywords first.
    if "events emitted" in title_lower:
        return "events_emitted"
    if "events consumed" in title_lower:
        return "events_consumed"
    if "business rule" in title_lower:  # matches "Business Rules", "Key Business Rules"
        return "business_rules"
    if "entit" in title_lower:  # matches "Entities", "Core Entities", "Key Entities"
        return "entities"
    return None


def extract_sections(text: str) -> dict[str, str]:
    """Walk H2 sections; return {kind: verbatim_section_text}."""
    lines = text.splitlines()

    h2_positions = [i for i, line in enumerate(lines) if line.startswith("## ")]
    h2_positions.append(len(lines))  # sentinel: end-of-file

    sections: dict[str, str] = {}
    for i in range(len(h2_positions) - 1):
        start = h2_positions[i]
        end = h2_positions[i + 1]
        title_line = lines[start]
        title_lower = title_line.lower()
        kind = classify_section_title(title_lower)
        if kind is None or kind in sections:
            continue
        body = "\n".join(lines[start:end]).rstrip()
        sections[kind] = body

    return sections


def render_summary(module: str, sections: dict[str, str]) -> str:
    out: list[str] = []
    title = module.replace("-", " ").title()
    out.append(f"# {title} Domain — Summary")
    out.append("")
    out.append(f"> Auto-generated from `{module}-domain.md` by `scripts/domain-summary.py`.")
    out.append("> DO NOT EDIT manually — the pre-commit hook regenerates this when the full file changes.")
    out.append(">")
    out.append("> Load THIS summary first to look up entities, BRs, or events.")
    out.append(f"> Load the full `{module}-domain.md` only when you need state machines,")
    out.append("> calculations, API endpoints, roles, or legacy notes.")
    out.append("")
    out.append(f"**Source:** `knowledge/L1-domain/{module}-domain.md`")
    out.append("")

    canonical = [
        ("entities", "Entities"),
        ("business_rules", "Business Rules"),
        ("events_emitted", "Events Emitted"),
        ("events_consumed", "Events Consumed"),
    ]
    found_any = False
    for kind, label in canonical:
        if kind in sections:
            out.append("---")
            out.append("")
            out.append(sections[kind])
            out.append("")
            found_any = True
        else:
            out.append("---")
            out.append("")
            out.append(f"## {label}")
            out.append("")
            out.append(f"_(no '{label}' section found in source)_")
            out.append("")

    if not found_any:
        return "\n".join(out)

    return "\n".join(out)


def generate(module: str, check_only: bool = False) -> tuple[int, str]:
    full_path = DOMAIN_DIR / f"{module}-domain.md"
    summary_path = DOMAIN_DIR / f"{module}-domain.summary.md"

    if not full_path.exists():
        return 1, f"✗ {module}: source not found ({full_path.relative_to(REPO_ROOT)})"

    text = full_path.read_text(encoding="utf-8")
    sections = extract_sections(text)
    new_content = render_summary(module, sections)

    if check_only:
        if not summary_path.exists():
            return 1, f"✗ {module}: summary missing — run scripts/domain-summary.py {module}"
        existing = summary_path.read_text(encoding="utf-8")
        if existing.rstrip("\n") != new_content.rstrip("\n"):
            return 1, f"✗ {module}: summary out of date — run scripts/domain-summary.py {module}"
        return 0, f"✓ {module}: summary up to date"

    summary_path.write_text(new_content, encoding="utf-8")
    sec_count = sum(1 for k in ("entities", "business_rules", "events_emitted", "events_consumed") if k in sections)
    size_bytes = len(new_content.encode("utf-8"))
    BUDGET_BYTES = 4000  # ~1K tokens. SA/BA load this first; full domain.md only on-demand.
    budget_warn = ""
    if size_bytes > BUDGET_BYTES:
        budget_warn = f"  ⚠ size {size_bytes}B > budget {BUDGET_BYTES}B — consider splitting {module}-domain.md or trimming entity tables"
    return 0, f"✓ {module}: regenerated {summary_path.relative_to(REPO_ROOT)} ({sec_count}/4 sections, {size_bytes}B){budget_warn}"


def discover_modules() -> list[str]:
    if not DOMAIN_DIR.exists():
        return []
    return sorted(
        p.stem.removesuffix("-domain") for p in DOMAIN_DIR.glob("*-domain.md")
        if not p.stem.endswith(".summary") and not p.stem.endswith("-domain.summary")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", nargs="?", help="Module name (e.g. 'production'). Omit with --all.")
    parser.add_argument("--all", action="store_true", help="Process every domain file under knowledge/L1-domain/")
    parser.add_argument("--check", action="store_true", help="Verify summary is up to date; do not write")
    args = parser.parse_args()

    if args.all:
        modules = discover_modules()
        if not modules:
            import sys as _s
            from pathlib import Path as _P
            _s.path.insert(0, str(_P(__file__).resolve().parent))
            from lib_config import is_initialized
            if not is_initialized():
                print("note: no domain files yet and workspace not onboarded — skipping (run /onboard)")
                return 0
            print("error: no -domain.md files found under knowledge/L1-domain/", file=sys.stderr)
            return 2
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
