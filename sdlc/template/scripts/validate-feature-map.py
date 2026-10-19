#!/usr/bin/env python3
"""
validate-feature-map.py — check feature-map.md (index) and feature-map/<module>.md (per-module).

Validations on per-module files:
  - Standard table header present
  - Every row has 11 columns matching the header (delimiter count check)
  - Feature ID format: PREFIX-NNN; IDs unique within file
  - Status in {[ACTIVE], [WIP], [DEPRECATED], [REMOVED]}
  - Layer in {BE, FE, MOBILE and combinations}
  - Legacy Sync in {Yes, No}

Validations on index (architecture/feature-map.md):
  - §Maintenance present with required fields (Owner, Last reviewed (date),
    one "Last reviewed against <repo> commit" row per repo in project.config.json, Reviewer)
  - All per-module files referenced from §5 actually exist on disk

Usage:
    scripts/validate-feature-map.py architecture/feature-map.md architecture/feature-map/*.md
    scripts/validate-feature-map.py             # default: validate everything

Exit: 0 = valid, 1 = issues found, 2 = usage error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "architecture" / "feature-map.md"
PER_MODULE_DIR = REPO_ROOT / "architecture" / "feature-map"

VALID_LAYERS = {"BE", "FE", "MOBILE", "BE+FE", "MOBILE+BE", "BE+FE+MOBILE"}
VALID_STATUSES = {"[ACTIVE]", "[WIP]", "[DEPRECATED]", "[REMOVED]"}
VALID_LEGACY_SYNC = {"Yes", "No"}

EXPECTED_COLUMNS = ["ID", "Feature", "Layer", "BE Endpoint", "FE Page", "Permission", "Status", "Depends On", "Used By", "Legacy Sync", "Notes"]


def validate_summary_file(path: Path) -> list[tuple[str, str]]:
    """Validate a <module>.summary.md file: 3-column structure + IDs match full file.
    Note: the freshness check ('summary content matches what feature-map-summary.py
    would generate') is performed by feature-map-summary.py --check, invoked
    separately by audit.sh and the pre-commit hook."""
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    # Locate the matching full file: <module>.md
    module_name = path.stem.removesuffix(".summary")
    full_path = PER_MODULE_DIR / f"{module_name}.md"
    if not full_path.exists():
        return [("ERROR", f"summary references missing full file: {full_path.relative_to(REPO_ROOT)}")]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("|") and "| ID " in line and "| Feature " in line and "| Status " in line:
            header_idx = i
            break
    if header_idx is None:
        return [("ERROR", "no summary table found (expected | ID | Feature | Status |)")]

    header_cols = [c.strip() for c in lines[header_idx].strip("|").split("|")]
    if header_cols != ["ID", "Feature", "Status"]:
        issues.append(("ERROR", f"summary header should be ['ID', 'Feature', 'Status'], got {header_cols}"))

    summary_ids: set[str] = set()
    feature_id_pattern = re.compile(r"^[A-Z]+-\d{3,}$")
    for i in range(header_idx + 2, len(lines)):
        line = lines[i].rstrip()
        if not line.startswith("|"):
            break
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) != 3:
            issues.append(("ERROR", f"line {i+1}: summary row must have 3 columns, got {len(cols)}"))
            continue
        fid = cols[0]
        if not feature_id_pattern.match(fid):
            issues.append(("ERROR", f"line {i+1}: invalid feature ID '{fid}'"))
            continue
        if fid in summary_ids:
            issues.append(("ERROR", f"line {i+1}: duplicate ID '{fid}' in summary"))
        summary_ids.add(fid)

    # Cross-check IDs: every ID in summary must exist in the full file's
    # '## Features' section. Cross-module touchpoint rows reference other
    # modules' IDs and do NOT belong in this summary.
    full_text = full_path.read_text(encoding="utf-8")
    full_lines = full_text.splitlines()
    features_start = None
    for i, line in enumerate(full_lines):
        if line.strip() == "## Features":
            features_start = i + 1
            break
    features_end = len(full_lines)
    if features_start is not None:
        for i in range(features_start, len(full_lines)):
            if full_lines[i].startswith("## "):
                features_end = i
                break
        section_text = "\n".join(full_lines[features_start:features_end])
    else:
        section_text = full_text  # degraded mode: scan whole file
    full_ids = set(re.findall(r"^\| ([A-Z]+-\d{3,}) \|", section_text, re.MULTILINE))

    orphans = summary_ids - full_ids
    for o in sorted(orphans):
        issues.append(("ERROR", f"summary contains '{o}' but it's not in {full_path.name} — regenerate via scripts/feature-map-summary.py {module_name}"))

    missing = full_ids - summary_ids
    for m in sorted(missing):
        issues.append(("ERROR", f"summary missing '{m}' which is in {full_path.name} — regenerate via scripts/feature-map-summary.py {module_name}"))

    return issues


def validate_module_file(path: Path) -> list[tuple[str, str]]:
    """Validate every feature table in a module file. Some module files
    have one table per sub-module (e.g. production.md)."""
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    header_positions = [
        i for i, line in enumerate(lines)
        if line.startswith("|") and "| ID " in line and "| Feature " in line
    ]
    if not header_positions:
        issues.append(("ERROR", "no feature table found (expected | ID | Feature | ... |)"))
        return issues

    seen_ids: dict[str, int] = {}     # ID → line number where first seen (across all tables in this file)
    feature_id_pattern = re.compile(r"^[A-Z]+-\d{3,}$")

    for header_line_idx in header_positions:
        # Verify column header matches expected
        header_cols = [c.strip() for c in lines[header_line_idx].strip("|").split("|")]
        if header_cols != EXPECTED_COLUMNS:
            issues.append(("WARN", f"line {header_line_idx+1}: header columns differ from canonical {EXPECTED_COLUMNS} → got {header_cols}"))

        # Skip header line + separator line
        for i in range(header_line_idx + 2, len(lines)):
            line = lines[i].rstrip()
            if not line.startswith("|"):
                break  # end of THIS table
            cols = [c.strip() for c in line.strip("|").split("|")]

            if len(cols) != len(EXPECTED_COLUMNS):
                issues.append(("ERROR", f"line {i+1}: expected {len(EXPECTED_COLUMNS)} columns, got {len(cols)} — {line[:80]}"))
                continue

            row = dict(zip(EXPECTED_COLUMNS, cols))
            fid = row["ID"]

            if not feature_id_pattern.match(fid):
                issues.append(("ERROR", f"line {i+1}: invalid feature ID format '{fid}' (expected PREFIX-NNN)"))
            elif fid in seen_ids:
                issues.append(("ERROR", f"line {i+1}: duplicate feature ID '{fid}' (also at line {seen_ids[fid]+1})"))
            else:
                seen_ids[fid] = i

            # Status validated first — REMOVED rows can use '—' placeholders for other fields.
            if row["Status"] not in VALID_STATUSES:
                issues.append(("ERROR", f"line {i+1}: Status '{row['Status']}' not in {sorted(VALID_STATUSES)}"))
            is_removed = row["Status"] == "[REMOVED]"
            if not is_removed:
                if row["Layer"] not in VALID_LAYERS:
                    issues.append(("ERROR", f"line {i+1}: Layer '{row['Layer']}' not in {sorted(VALID_LAYERS)}"))
                if row["Legacy Sync"] not in VALID_LEGACY_SYNC:
                    issues.append(("WARN", f"line {i+1}: Legacy Sync '{row['Legacy Sync']}' not in {sorted(VALID_LEGACY_SYNC)}"))

    return issues


def validate_index_file(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not path.exists():
        return [("ERROR", f"file not found: {path}")]

    text = path.read_text(encoding="utf-8")

    # §2 Maintenance — must have these fields with non-empty values.
    # Repo rows come from project.config.json; skipped when no repos configured yet.
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_config import repo_names as _repo_names

    required_maint_fields = [
        ("Owner", r"^\| Owner \| .+ \|"),
        ("Last reviewed (date)", r"^\| Last reviewed \(date\) \| \d{4}-\d{2}-\d{2} \|"),
        ("Reviewer", r"^\| Reviewer \| .+ \|"),
    ]
    for _repo in _repo_names():
        required_maint_fields.append((
            f"Last reviewed against {_repo} commit",
            rf"^\| Last reviewed against {re.escape(_repo)} commit \| ([a-f0-9]{{7,40}}|MISSING|UNREADABLE)( \(.+\))? \|",
        ))
    for name, pattern in required_maint_fields:
        if not re.search(pattern, text, re.MULTILINE):
            issues.append(("ERROR", f"§2 Maintenance: missing or malformed '{name}' row"))

    # Cross-check that referenced module files exist.
    # Rows whose Status column is "Planned" are exempt — SA creates the per-module
    # file on first touch; a fresh /onboard legitimately references files that
    # don't exist yet.
    referenced_modules = set(re.findall(r"architecture/feature-map/([a-z\-]+)\.md", text))
    planned_modules = set(
        re.findall(r"^\|[^|]*\|\s*`architecture/feature-map/([a-z\-]+)\.md`\s*\|\s*Planned\s*\|", text, re.MULTILINE)
    )
    existing_modules: set[str] = set()
    if PER_MODULE_DIR.exists():
        existing_modules = {p.stem for p in PER_MODULE_DIR.glob("*.md") if not p.stem.endswith(".summary")}
    missing = referenced_modules - existing_modules - planned_modules
    for mod in sorted(missing):
        issues.append(("ERROR", f"index references architecture/feature-map/{mod}.md but file does not exist"))

    return issues


def main(argv: list[str]) -> int:
    paths: list[Path]
    if len(argv) > 1:
        paths = [Path(a) for a in argv[1:]]
    else:
        # default: index + every per-module file (full + summary)
        paths = [INDEX_PATH] if INDEX_PATH.exists() else []
        if PER_MODULE_DIR.exists():
            paths.extend(sorted(PER_MODULE_DIR.glob("*.md")))

    if not paths:
        print("usage: validate-feature-map.py [feature-map.md] [feature-map/<module>.md ...]", file=sys.stderr)
        return 2

    overall_errors = 0
    overall_warns = 0
    files_with_issues = 0

    for path in paths:
        if path.resolve() == INDEX_PATH.resolve():
            issues = validate_index_file(path)
        elif path.stem.endswith(".summary"):
            issues = validate_summary_file(path)
        else:
            issues = validate_module_file(path)

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
        print(f"✓ {total} feature-map file(s) valid")
        return 0
    print(f"\n{files_with_issues}/{total} feature-map file(s) have issues — {overall_errors} error(s), {overall_warns} warning(s)")
    return 1 if overall_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
