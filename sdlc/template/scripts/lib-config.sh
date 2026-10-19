#!/usr/bin/env bash
# lib-config.sh — shell access to project.config.json. Source this AFTER cd'ing
# to the workspace root:
#     source "$REPO_ROOT/scripts/lib-config.sh"
#
# Functions print nothing (and return success) when the config is missing —
# callers must handle the "not configured yet" case by skipping their check.

cfg_repo_names() {
    # One configured source-repo name per line (be, fe, mobile order).
    [[ -f project.config.json ]] || return 0
    python3 -c '
import json
try:
    cfg = json.load(open("project.config.json"))
except Exception:
    raise SystemExit(0)
for r in cfg.get("repos", {}).values():
    if r.get("name"):
        print(r["name"])
' 2>/dev/null || true
}

cfg_project_field() {
    # cfg_project_field name|short_code|language
    [[ -f project.config.json ]] || return 0
    python3 -c "
import json
try:
    cfg = json.load(open('project.config.json'))
except Exception:
    raise SystemExit(0)
print(cfg.get('project', {}).get('$1', ''))
" 2>/dev/null || true
}

cfg_initialized() {
    # Exit 0 when the workspace has been onboarded, 1 otherwise.
    [[ -f project.config.json ]] || return 1
    python3 -c '
import json, sys
try:
    cfg = json.load(open("project.config.json"))
except Exception:
    sys.exit(1)
sys.exit(0 if cfg.get("initialized") else 1)
' 2>/dev/null
}
