#!/usr/bin/env bash
# lazy-gate.sh <brief|draft|edit|check> — gate of the content kit. Lazy Bot factory runs it
# after each stage, before asking the owner (see .lazy/kit.yaml). Exit 0 = the stage's files are
# there and complete; anything else = the stage is redone with this output (last 200 lines).
# Runs in the task worktree, without credentials or network, and writes nothing.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 -B scripts/kit_check.py "$@"
