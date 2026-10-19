#!/usr/bin/env bash
# feature-map-freshness.sh — refresh §2 Maintenance fields in architecture/feature-map.md
# with current short SHAs of every repo configured in project.config.json, plus today's date.
#
# Usage:
#   scripts/feature-map-freshness.sh           # update in place
#   scripts/feature-map-freshness.sh --check   # print current vs target, no write
#
# Exits 0 with a note when no repos are configured yet (pre-/onboard workspace).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/lib-config.sh"

MAP="architecture/feature-map.md"

if [[ ! -f "$MAP" ]]; then
    echo "error: $MAP not found" >&2
    exit 1
fi

REPOS=()
while IFS= read -r r; do [[ -n "$r" ]] && REPOS+=("$r"); done < <(cfg_repo_names)

if (( ${#REPOS[@]} == 0 )); then
    echo "note: no repos configured in project.config.json — nothing to refresh (run /onboard first)"
    exit 0
fi

resolve_sha() {
    local repo_dir="$1"
    if [[ ! -d "$repo_dir" && ! -L "$repo_dir" ]]; then
        echo "MISSING"
        return
    fi
    git -C "$repo_dir" rev-parse --short HEAD 2>/dev/null || echo "UNREADABLE"
}

TODAY="$(date +%Y-%m-%d)"

# Read the current value of a "| <label> | <value> |" row (fixed-string match on label).
current_row_value() {
    local label="$1"
    awk -F'|' -v lbl=" ${label} " '
        $2 == lbl { gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3; exit }
    ' "$MAP"
}

if [[ "${1:-}" == "--check" ]]; then
    echo "current  →  target"
    cur_date="$(current_row_value "Last reviewed (date)")"
    echo "  date : ${cur_date:-?}  →  $TODAY"
    for repo in "${REPOS[@]}"; do
        sha="$(resolve_sha "_source/$repo")"
        cur="$(current_row_value "Last reviewed against $repo commit")"
        echo "  $repo : ${cur:-?}  →  $sha"
    done
    exit 0
fi

# Rewrite rows with awk (fixed-string label matching — no regex pitfalls).
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

cp "$MAP" "$TMP"

update_row() {
    # Upsert: update the row when present, otherwise insert it right after
    # the "Last reviewed (date)" row (so scaffolds start without repo rows).
    local label="$1" value="$2"
    local out
    out="$(mktemp)"
    if awk -F'|' -v lbl=" ${label} " '$2 == lbl { found=1 } END { exit !found }' "$TMP"; then
        awk -F'|' -v lbl=" ${label} " -v val="$value" -v OFS='|' '
            $2 == lbl { $3 = " " val " " }
            { print }
        ' "$TMP" > "$out"
    else
        awk -F'|' -v lbl="$label" -v val="$value" '
            { print }
            $2 == " Last reviewed (date) " { printf "| %s | %s |\n", lbl, val }
        ' "$TMP" > "$out"
    fi
    mv "$out" "$TMP"
}

update_row "Last reviewed (date)" "$TODAY"
echo "updated $MAP §2 Maintenance:"
echo "  date → $TODAY"
for repo in "${REPOS[@]}"; do
    sha="$(resolve_sha "_source/$repo")"
    update_row "Last reviewed against $repo commit" "$sha"
    echo "  $repo → $sha"
done

mv "$TMP" "$MAP"
trap - EXIT
