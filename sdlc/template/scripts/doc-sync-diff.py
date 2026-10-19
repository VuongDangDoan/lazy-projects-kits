#!/usr/bin/env python3
"""
doc-sync-diff.py — produce a starter Doc Sync Plan from a list of changed files.

Walks the mapping in .agents/contracts/doc-sync.schema.md §3 and emits a
markdown plan listing every doc that's likely affected. The agent / human
finalizes the plan (drops false positives, adds context) before showing it
to the human for approval.

Usage:
    # From a git diff (default: HEAD against working tree)
    git diff --name-only HEAD -- _source/ | scripts/doc-sync-diff.py

    # From explicit paths
    scripts/doc-sync-diff.py _source/<be-repo>/src/modules/<module>/<file>.ts

    # From a specific git range
    scripts/doc-sync-diff.py --base HEAD~1
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import repo_names

REPO_ROOT = Path(__file__).resolve().parent.parent

# Path → category classifier. Repo names come from project.config.json;
# fall back to matching any _source/<repo>/ when nothing is configured yet.
_repos = repo_names()
_REPO_ALT = "|".join(re.escape(r) for r in _repos) if _repos else r"[^/]+"
RE_SRC_MODULE = re.compile(rf"_source/({_REPO_ALT})/src/(?:modules|pages)/([^/]+)/")
RE_SRC_MIGRATION = re.compile(rf"_source/({_REPO_ALT})/src/migrations/")
RE_API_CONTRACT = re.compile(r"architecture/api-contracts/v1/([^/]+)\.yaml")
RE_DB_MIGRATION = re.compile(r"architecture/db-schema/migrations/")
RE_STATE_MACHINE = re.compile(r"architecture/db-schema/state-machines/")
RE_DOMAIN = re.compile(r"knowledge/L1-domain/([^/]+)-domain\.md")
RE_LEGACY_SCAN = re.compile(r"knowledge/L2-legacy/scans/([^/]+)-legacy-scan\.md")


def read_paths_from_args_or_stdin(paths: list[str], base: str | None) -> list[str]:
    """Resolve the set of changed paths from CLI args, --base, or stdin."""
    if paths:
        return paths
    if base:
        try:
            out = subprocess.check_output(
                ["git", "diff", "--name-only", base, "--", "_source/"],
                cwd=REPO_ROOT,
                text=True,
            )
            return [p for p in out.splitlines() if p.strip()]
        except subprocess.CalledProcessError as e:
            print(f"error: git diff failed: {e}", file=sys.stderr)
            sys.exit(1)
    if not sys.stdin.isatty():
        return [p.strip() for p in sys.stdin if p.strip()]
    return []


def classify(path: str) -> dict:
    """Return a dict describing what category the path falls into."""
    info: dict = {"path": path, "matches": []}

    if m := RE_SRC_MODULE.search(path):
        info["matches"].append(("src_module", (m.group(1), m.group(2))))
    if m := RE_SRC_MIGRATION.search(path):
        info["matches"].append(("src_migration", m.group(1)))
    if m := RE_API_CONTRACT.search(path):
        info["matches"].append(("api_contract", m.group(1)))
    if RE_DB_MIGRATION.search(path):
        info["matches"].append(("db_migration", None))
    if RE_STATE_MACHINE.search(path):
        info["matches"].append(("state_machine", None))
    if m := RE_DOMAIN.search(path):
        info["matches"].append(("domain", m.group(1)))
    if m := RE_LEGACY_SCAN.search(path):
        info["matches"].append(("legacy_scan", m.group(1)))

    if not info["matches"]:
        info["matches"].append(("other", None))
    return info


def affected_docs(classifications: Iterable[dict]) -> dict[str, set[str]]:
    """
    Build the set of suspected docs that need updating.
    Keys are doc paths, values are the reasons (one or more).
    """
    docs: dict[str, set[str]] = {}

    def add(path: str, reason: str) -> None:
        docs.setdefault(path, set()).add(reason)

    changed_repos: set[str] = set()

    for c in classifications:
        for kind, val in c["matches"]:
            src = c["path"]
            if kind == "src_module":
                repo, module = val
                changed_repos.add(repo)
                add(f"architecture/feature-map/{module}.md", f"code changed: {src}")
                add(f"knowledge/L1-domain/{module}-domain.md", f"code changed: {src}")
            elif kind == "src_migration":
                changed_repos.add(val)
                add("architecture/db-schema/", f"new/changed migration: {src}")
            elif kind == "api_contract":
                add(f"architecture/api-contracts/v1/{val}.yaml", f"contract changed: {src}")
            elif kind == "state_machine":
                add(src, "state machine artifact changed")
            elif kind == "domain":
                pass  # doc itself, not propagation
            elif kind == "legacy_scan":
                add(src, "legacy scan artifact changed")

    # Always-touched: feature-map.md §2 Maintenance freshness header
    if changed_repos:
        add(
            "architecture/feature-map.md (§2 Maintenance)",
            " + ".join(f"{r} SHA refresh" for r in sorted(changed_repos)),
        )

    return docs


def render_plan(paths: list[str], docs: dict[str, set[str]]) -> str:
    lines: list[str] = []
    lines.append("=== STARTER DOC SYNC PLAN (review before sending to human) ===")
    lines.append("")
    lines.append("Code changes detected:")
    if not paths:
        lines.append("  - (none — pipe `git diff --name-only` or pass paths)")
    else:
        for p in paths:
            lines.append(f"  - {p}")
    lines.append("")
    lines.append("Documentation updates suspected:")
    if not docs:
        lines.append("  (none matched — review the doc-sync mapping in .agents/contracts/doc-sync.schema.md §3 manually)")
    else:
        for i, (doc, reasons) in enumerate(sorted(docs.items()), start=1):
            lines.append(f"  [{i}] {doc}")
            for r in sorted(reasons):
                lines.append(f"      reason: {r}")
    lines.append("")
    lines.append("Notes:")
    lines.append("  - This is a STARTER plan generated mechanically. Verify each item before requesting approval.")
    lines.append("  - Add domain/integration-map updates if BRs or events changed (script can't detect that).")
    lines.append("  - Refresh `Last reviewed` SHAs via: scripts/feature-map-freshness.sh")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Changed paths (or pipe via stdin)")
    parser.add_argument("--base", help="Git ref to diff against (e.g. HEAD~1)")
    args = parser.parse_args()

    paths = read_paths_from_args_or_stdin(args.paths, args.base)
    classifications = [classify(p) for p in paths]
    docs = affected_docs(classifications)
    print(render_plan(paths, docs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
