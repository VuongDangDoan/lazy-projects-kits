#!/usr/bin/env bash
# install-hooks.sh — symlink scripts/git-hooks/* into .git/hooks/
#
# Default mode: installs hooks in THIS workspace only.
# --include-source: also installs a thin secret-scan hook in every source repo
#                   configured in project.config.json (via the _source/ symlinks).
#
# Idempotent. Safe to re-run any time.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/lib-config.sh"

INCLUDE_SOURCE=0
if [[ "${1:-}" == "--include-source" ]]; then
    INCLUDE_SOURCE=1
fi

# ----------------------------------------------------------------------
# Phase 1 — workspace hooks (always)
# ----------------------------------------------------------------------

if [[ ! -d .git ]]; then
    echo "error: not a git repository (run from workspace root)" >&2
    exit 1
fi

mkdir -p .git/hooks

echo "── workspace hooks (this repo) ──"
for src in scripts/git-hooks/*; do
    [[ -f "$src" ]] || continue
    name="$(basename "$src")"
    # Skip the source-repo template — it's not a workspace hook
    [[ "$name" == "source-repo-pre-commit" ]] && continue
    target=".git/hooks/$name"

    chmod +x "$src"

    if [[ -L "$target" ]]; then
        existing="$(readlink "$target")"
        expected="../../$src"
        if [[ "$existing" != "$expected" ]]; then
            rm "$target"
            ln -s "$expected" "$target"
            echo "↻ updated symlink: $target → $expected"
        else
            echo "✓ already linked: $target"
        fi
    elif [[ -e "$target" ]]; then
        mv "$target" "${target}.backup.$(date +%Y%m%d-%H%M%S)"
        ln -s "../../$src" "$target"
        echo "↻ replaced existing $target (backup created)"
    else
        ln -s "../../$src" "$target"
        echo "✓ installed: $target → ../../$src"
    fi
done

# ----------------------------------------------------------------------
# Phase 2 — source-repo hooks (--include-source only)
# ----------------------------------------------------------------------

if (( INCLUDE_SOURCE != 1 )); then
    echo ""
    echo "Workspace hooks done. To also install in source repos:"
    echo "    scripts/install-hooks.sh --include-source"
    exit 0
fi

echo ""
echo "── source repo hooks (--include-source) ──"

WRAPPER="scripts/git-hooks/source-repo-pre-commit"
chmod +x "$WRAPPER"

install_source_hook() {
    local repo_label="$1"
    local repo_path="$2"

    if [[ ! -d "$repo_path/.git" && ! -L "$repo_path/.git" && ! -f "$repo_path/.git" ]]; then
        echo "  (skip $repo_label — not a git repo at $repo_path)"
        return
    fi

    # Detect husky (core.hooksPath redirect)
    local hooks_path
    hooks_path="$(git -C "$repo_path" config --get core.hooksPath 2>/dev/null || true)"

    if [[ -n "$hooks_path" && "$hooks_path" != ".git/hooks" ]]; then
        # husky-style — installing in .git/hooks won't fire
        echo "  ⚠ $repo_label uses core.hooksPath=$hooks_path (husky?)"
        echo "    .git/hooks/pre-commit would NOT run there. Manual setup required."
        echo "    To enable: add this line to ${repo_path}/${hooks_path}/pre-commit"
        echo "      \"\$(git rev-parse --show-toplevel)/../$(basename "$REPO_ROOT")/scripts/check-secrets.sh\""
        echo "    Then commit ${hooks_path}/pre-commit (it's tracked in source repo)."
        return
    fi

    # Plain .git/hooks/ — safe to install
    local target="$repo_path/.git/hooks/pre-commit"

    if [[ -e "$target" && ! -L "$target" ]]; then
        # Real file in the way — back it up unless it's already our wrapper
        if grep -q "Workspace-managed pre-commit hook" "$target" 2>/dev/null; then
            cp "$WRAPPER" "$target"
            chmod +x "$target"
            echo "  ↻ refreshed: $target"
        else
            mv "$target" "${target}.backup.$(date +%Y%m%d-%H%M%S)"
            cp "$WRAPPER" "$target"
            chmod +x "$target"
            echo "  ↻ replaced existing (backup): $target"
        fi
    elif [[ -L "$target" ]]; then
        rm "$target"
        cp "$WRAPPER" "$target"
        chmod +x "$target"
        echo "  ↻ replaced symlink with copy: $target"
    else
        cp "$WRAPPER" "$target"
        chmod +x "$target"
        echo "  ✓ installed: $target"
    fi
}

FOUND_REPO=0
while IFS= read -r repo; do
    [[ -n "$repo" ]] || continue
    FOUND_REPO=1
    install_source_hook "$repo" "_source/$repo"
done < <(cfg_repo_names)

if (( FOUND_REPO == 0 )); then
    echo "  (no repos configured in project.config.json — run /onboard first)"
fi

echo ""
echo "Done. Source repo hooks call back to this workspace's check-secrets.sh."
echo "If you move the workspace, set SDLC_WORKSPACE env var in your shell."
