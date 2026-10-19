#!/usr/bin/env bash
# lazy-init.sh — non-interactive onboarding for Lazy Bot factory mode.
#
# The factory copies this kit's template into a new project repo, writes .lazy/project.json
# (values the owner approved on the "Lập team" card) and runs this script from the repo root.
# It replaces the 9-question /onboard: writes project.config.json, runs scripts/scaffold.sh,
# overlays the stack pattern files, prepends the factory-mode rules to CLAUDE.md and creates
# _source/<name>/ (the code lives in this same repo — no symlinks).
#
# Runs without credentials and without network. Exit 0 = ready; anything else = the factory
# aborts the project creation and cleans up.
#
# .lazy/project.json:
#   { "name": "chi-tieu", "displayName": "Chi tiêu", "shortCode": "CTU", "description": "…",
#     "stack": "Next.js + PostgreSQL", "modules": ["Auth", "Giao dịch"], "language": "vi" }

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

[[ -f .lazy/project.json ]] || { echo "lazy-init: thiếu .lazy/project.json" >&2; exit 1; }

python3 scripts/lazy_init.py
# shellcheck disable=SC1091
source .lazy/.init.env && rm -f .lazy/.init.env

scripts/scaffold.sh --force DOMAIN="$DOMAIN" DATABASE="$DATABASE" CODEBASE_STATE=greenfield >/dev/null

for pair in $STACKS; do
    src="knowledge/stacks/${pair%%:*}"; dst="knowledge/L0-global/${pair##*:}"
    [[ -f "$src" ]] && cp "$src" "$dst"
done

# Factory-mode rules go first in CLAUDE.md so every session reads them before anything else.
if ! grep -q "LAZY-FACTORY-MODE" CLAUDE.md; then
    { cat templates/lazy/factory-mode.md | sed "s/{{NAME}}/$NAME/g"; echo; cat CLAUDE.md; } > CLAUDE.md.new && mv CLAUDE.md.new CLAUDE.md
fi

mkdir -p "_source/$NAME"
[[ -n "$(ls -A "_source/$NAME" 2>/dev/null)" ]] || : > "_source/$NAME/.gitkeep"

if grep -rIl '{{' CLAUDE.md AGENTS.md 2>/dev/null | head -1 | grep -q .; then
    echo "lazy-init: còn placeholder {{…}} chưa thay trong CLAUDE.md/AGENTS.md" >&2; exit 1
fi
echo "lazy-init: OK — dự án $NAME"
