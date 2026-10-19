#!/usr/bin/env bash
# archive-active-context.sh — copy active-context.md to history/<date>-<topic>.md.
#
# Use at natural archival points:
#   - finishing a feature / ticket / sprint
#   - before /switch-module (the switch-module command also calls this)
#   - whenever active-context.md grows past the 80-line cap
#
# Usage:
#   scripts/archive-active-context.sh <topic>             # archive (copy), keep original
#   scripts/archive-active-context.sh <topic> --reset     # archive then reset to a fresh template
#
# The embedded template below is the CANONICAL shape of active-context.md —
# it must stay in sync with .agents/contracts/active-context.schema.md.
# If no active-context exists yet, --reset creates one from the template.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/lib-config.sh"

ACTIVE="knowledge/L3-session/active-context.md"
HIST_DIR="knowledge/L3-session/history"

topic="${1:-}"
reset_flag="${2:-}"

if [[ -z "$topic" ]]; then
    echo "usage: $0 <topic> [--reset]" >&2
    echo "  topic: short slug for the archive filename (e.g. 'us-001', 'sprint-01-end')" >&2
    exit 2
fi

date_stamp="$(date +%Y-%m-%d)"

if [[ -f "$ACTIVE" ]]; then
    mkdir -p "$HIST_DIR"
    target="$HIST_DIR/${date_stamp}-${topic}.md"
    # Avoid overwriting same-day same-topic
    if [[ -e "$target" ]]; then
        target="$HIST_DIR/${date_stamp}-${topic}-$(date +%H%M%S).md"
    fi
    cp "$ACTIVE" "$target"
    echo "✓ archived: $target"
elif [[ "$reset_flag" != "--reset" ]]; then
    echo "no $ACTIVE to archive" >&2
    exit 1
fi

if [[ "$reset_flag" == "--reset" ]]; then
    mkdir -p "$(dirname "$ACTIVE")"
    project_name="$(cfg_project_field name)"
    language="$(cfg_project_field language)"
    cat > "$ACTIVE" <<EOF
# Active Session Context

> L3 — loaded by every agent at the start of a task. Hard cap: 80 lines.
> Overflow → move detail to a per-feature companion file and reference it here.
> Canonical shape: .agents/contracts/active-context.schema.md

## Session

| Field | Value |
|---|---|
| Project | ${project_name:-"(run /onboard)"} |
| Language | ${language:-vi} |
| Current phase / gate | (none — pipeline not started) |
| Module | (fill in) |

## In Progress

(none — list active US / TICKET refs here)

## Locked Decisions

> Append-only one-liners. Never re-litigate without human approval.

(none yet)

## Business Rules in Scope

**Business Rules in Scope:** None

## Legacy

**Legacy involved?** No

## Do NOT

(session-scoped prohibitions — none yet)

---
**Last updated:** ${date_stamp} · by: (fill in) · trigger: reset
EOF
    echo "✓ reset $ACTIVE to fresh template"
fi
