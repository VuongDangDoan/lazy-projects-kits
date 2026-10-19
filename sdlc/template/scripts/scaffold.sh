#!/usr/bin/env bash
# scaffold.sh — copy templates/scaffold/** into the workspace, substituting
# {{PLACEHOLDER}} markers from project.config.json.
#
# Used by /onboard (Phase 5) and /quickstart. Idempotent:
#   - identical file already in place  → "unchanged", no write
#   - file differs and no --force      → reported as CONFLICT, NOT overwritten (exit 2)
#   - file differs and --force         → overwritten
#
# Placeholders substituted (from project.config.json unless overridden):
#   {{PROJECT_NAME}} {{SHORT_CODE}} {{LANGUAGE}}
#   {{BE_REPO}} {{FE_REPO}} {{MOBILE_REPO}}
#   {{STACK_BE}} {{STACK_FE}} {{STACK_MOBILE}}
#   {{MODULES_TABLE}} {{MODULES_TABLE_FEATUREMAP}} {{MODULES_LIST}} {{DATE}}
#   plus any KEY=VALUE pairs passed on the command line, e.g.:
#       scripts/scaffold.sh --force DOMAIN="Retail / POS" CODEBASE_STATE=greenfield DATABASE=PostgreSQL
#
# Per-module expansion: a template path containing "__MODULE__" is written once per
# module in project.config.json (extra placeholders {{MODULE_NAME}} {{MODULE_SLUG}} {{BR_PREFIX}}).
#
# Extra behaviors:
#   - knowledge/L0-global/fe-patterns.md is skipped when repos.fe.name is empty ("none")
#   - knowledge/L0-global/mobile-patterns.md is skipped when repos.mobile.name is empty
#   - tests/e2e/fixtures/test-users.example.json is copied to test-users.json when missing
#   - scripts/.check-config.yml gains a "<repo>: <check_cmd>" line per configured repo
#   - after writing, files are scanned for leftover "{{" markers (reported as WARN)
#
# Exit codes: 0 = OK, 1 = config missing/invalid, 2 = conflicts skipped (re-run with --force)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f project.config.json ]]; then
    echo "scaffold: project.config.json not found — run /onboard first" >&2
    exit 1
fi
if [[ ! -d templates/scaffold ]]; then
    echo "scaffold: templates/scaffold/ not found" >&2
    exit 1
fi

python3 - "$@" <<'PYEOF'
import json, sys, shutil
from datetime import date
from pathlib import Path

root = Path(".")
src_root = root / "templates" / "scaffold"

force = False
overrides = {}
for arg in sys.argv[1:]:
    if arg == "--force":
        force = True
    elif "=" in arg:
        k, v = arg.split("=", 1)
        overrides[k.strip()] = v
    else:
        print(f"scaffold: unknown argument: {arg}", file=sys.stderr)
        sys.exit(1)

try:
    cfg = json.loads((root / "project.config.json").read_text(encoding="utf-8"))
except Exception as e:
    print(f"scaffold: cannot parse project.config.json: {e}", file=sys.stderr)
    sys.exit(1)

proj = cfg.get("project", {})
repos = cfg.get("repos", {})
modules = cfg.get("modules", [])

def repo(key, field, default=""):
    return (repos.get(key) or {}).get(field, "") or default

be_name = repo("be", "name")
fe_name = repo("fe", "name")
mobile_name = repo("mobile", "name")

if not proj.get("name") or not be_name:
    print("scaffold: project.name or repos.be.name empty in project.config.json — fill the config first", file=sys.stderr)
    sys.exit(1)

def modules_table():
    rows = [f"| {m.get('name', m.get('slug',''))} | `knowledge/L1-domain/{m.get('slug','')}-domain.md` | Planned |" for m in modules]
    return "\n".join(rows) if rows else "| (none yet — edit project.config.json) | — | — |"

def modules_table_featuremap():
    rows = [f"| {m.get('name', m.get('slug',''))} | `architecture/feature-map/{m.get('slug','')}.md` | Planned |" for m in modules]
    return "\n".join(rows) if rows else "| (none yet) | — | — |"

subs = {
    "PROJECT_NAME": proj.get("name", ""),
    "SHORT_CODE": proj.get("short_code", ""),
    "LANGUAGE": proj.get("language", "en"),
    "BE_REPO": be_name,
    "FE_REPO": fe_name or "none",
    "MOBILE_REPO": mobile_name or "none",
    "STACK_BE": repo("be", "stack", "—"),
    "STACK_FE": repo("fe", "stack", "none"),
    "STACK_MOBILE": repo("mobile", "stack", "none"),
    "MODULES_TABLE": modules_table(),
    "MODULES_TABLE_FEATUREMAP": modules_table_featuremap(),
    "MODULES_LIST": ", ".join(m.get("name", m.get("slug", "")) for m in modules),
    "DATE": date.today().isoformat(),
    # Overridable extras with safe defaults:
    "WORKSPACE_FOLDER": root.resolve().name,
    "DOMAIN": "[DOMAIN — pass DOMAIN=... to scaffold.sh]",
    "DATABASE": "[DATABASE — pass DATABASE=... to scaffold.sh]",
    "CODEBASE_STATE": "[CODEBASE_STATE — pass CODEBASE_STATE=... to scaffold.sh]",
}
subs.update(overrides)

def render(text, extra=None):
    table = dict(subs)
    if extra:
        table.update(extra)
    for k, v in table.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text

written, unchanged, conflicts, skipped = [], [], [], []

def place(dest: Path, content: str):
    if dest.exists():
        if dest.read_text(encoding="utf-8") == content:
            unchanged.append(str(dest)); return
        if not force:
            conflicts.append(str(dest)); return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    written.append(str(dest))

for src in sorted(src_root.rglob("*")):
    if not src.is_file():
        continue
    rel = src.relative_to(src_root)
    rel_str = str(rel)

    # Optional-repo pattern files
    if rel.name == "fe-patterns.md" and not fe_name:
        skipped.append(rel_str + "  (no FE repo)"); continue
    if rel.name == "mobile-patterns.md" and not mobile_name:
        skipped.append(rel_str + "  (no mobile repo)"); continue

    if src.name == ".gitkeep":
        dest = root / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.touch()
            written.append(str(dest))
        else:
            unchanged.append(str(dest))
        continue

    text = src.read_text(encoding="utf-8")

    if "__MODULE__" in rel_str:
        if not modules:
            skipped.append(rel_str + "  (no modules configured)")
            continue
        for m in modules:
            slug = m.get("slug", "")
            if not slug:
                continue
            extra = {
                "MODULE_SLUG": slug,
                "MODULE_NAME": m.get("name", slug.title()),
                "BR_PREFIX": m.get("br_prefix", f"BR-{slug[:3].upper()}"),
            }
            place(root / Path(rel_str.replace("__MODULE__", slug)), render(text, extra))
        continue

    place(root / rel, render(text))

# test-users fixture: copy example → real (gitignored) when missing
example = root / "tests/e2e/fixtures/test-users.example.json"
real = root / "tests/e2e/fixtures/test-users.json"
if example.exists() and not real.exists():
    shutil.copyfile(example, real)
    written.append(str(real) + "  (fill real credentials — file is gitignored)")

# scripts/.check-config.yml — one line per configured repo
check_cfg = root / "scripts/.check-config.yml"
existing = check_cfg.read_text(encoding="utf-8") if check_cfg.exists() else ""
added = []
for key in ("be", "fe", "mobile"):
    name, cmd = repo(key, "name"), repo(key, "check_cmd")
    if name and cmd and not any(line.split(":")[0].strip() == name for line in existing.splitlines() if ":" in line):
        added.append(f"{name}: {cmd}")
if added:
    new = existing.rstrip("\n") + ("\n" if existing.strip() else "") + "\n".join(added) + "\n"
    check_cfg.write_text(new, encoding="utf-8")
    written.append(str(check_cfg) + f"  (+{len(added)} repo entr{'y' if len(added)==1 else 'ies'})")

# Leftover-marker scan on files we just wrote
warn = []
for f in written:
    p = Path(f.split("  (")[0])
    if p.suffix in (".md", ".json", ".yml", ".yaml") and p.exists() and "{{" in p.read_text(encoding="utf-8"):
        warn.append(str(p))

print(f"scaffold: {len(written)} written, {len(unchanged)} unchanged, {len(conflicts)} conflicts, {len(skipped)} skipped")
for f in written:
    print(f"  + {f}")
for f in skipped:
    print(f"  ~ skipped {f}")
if conflicts:
    print("\nCONFLICTS — existing files differ from template output (NOT overwritten).")
    print("Diff each one, then re-run with --force to overwrite:")
    for f in conflicts:
        print(f"  ! {f}")
if warn:
    print("\nWARN — unreplaced {{PLACEHOLDER}} markers remain in:")
    for f in warn:
        print(f"  ? {f}")
    print("Pass the missing KEY=VALUE pairs (e.g. DOMAIN=..., DATABASE=..., CODEBASE_STATE=...) and re-run.")

sys.exit(2 if conflicts else 0)
PYEOF
PY_EXIT=$?

# Post-steps (only when the copy phase succeeded):
#   - generate the *-domain.summary.md files the agents load first
#   - add per-repo commit rows to feature-map.md §Maintenance
if [[ $PY_EXIT -eq 0 ]]; then
    scripts/domain-summary.py --all >/dev/null 2>&1 || true
    scripts/feature-map-freshness.sh >/dev/null 2>&1 || true
    echo "scaffold: post-steps done (domain summaries + feature-map repo rows)"
fi

exit $PY_EXIT
