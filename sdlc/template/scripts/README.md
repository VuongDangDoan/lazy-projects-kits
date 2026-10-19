# scripts/

Deterministic helpers that agents call to avoid re-deriving things from scratch. Run any of them from the workspace root.

## Inventory

### Generators / refreshers (deterministic data)

| Script | Purpose | Used by |
|---|---|---|
| `next-id.sh` | Print the next sequential **global** ID: `ticket` → TICKET-NNN, `us` → US-NNN, `e2e` → TC-E-NNN, `adr` → NNN, `feature <module>` → per-module prefix | `/planner`, `/ba`, `/e2e-write`, `/sa` |
| `scaffold.sh` | Copy `templates/scaffold/**` into the workspace, substituting `{{PLACEHOLDER}}` markers from `project.config.json` (per-module expansion, idempotent diff-before-overwrite) | `/onboard`, `/quickstart` |
| `feature-map-freshness.sh` | Refresh `architecture/feature-map.md` §2 Maintenance with current `_source/` SHAs + today's date | `/sa`, `/dev`, `/fe` (Doc Sync) |
| `feature-map-summary.py` | Regenerate `<module>.summary.md` (skinny ID+Name+Status) from full module file. Auto-run by pre-commit hook. | pre-commit hook, `/sa` |
| `domain-summary.py` | Regenerate `<module>-domain.summary.md` keeping only Entities + Business Rules + Events sections. Auto-run by pre-commit hook. | pre-commit hook, `/sa`, `/ba`, `/dev`, `/fe` |
| `archive-active-context.sh` | Copy `active-context.md` to `L3-session/history/<date>-<topic>.md`. With `--reset`, also writes a fresh template. | `/switch-module`, end-of-feature housekeeping |
| `commit-message.sh` | Generate a conventional-commit message from a ticket file (auto-detects type from title verb, preserves acronyms, includes Layer + US-ID + Ref footer). Pipe into `git commit -m "$(...)"`. | After `/dev` or `/fe` finishes |
| `legacy-scan-freshness.sh` | Report `MISSING / STALE / FRESH` for a module's legacy scan | `/legacy-scan` Skip Conditions, `/dev`, `/fe` |
| `doc-sync-diff.py` | Generate a starter Doc Sync Plan from a list of changed files | `/dev`, `/fe`, `/sa` |

### Config access (shared libraries)

| Script | Purpose | Used by |
|---|---|---|
| `lib_config.py` | Python loader for `project.config.json` — module slugs, BR-prefix map, repo names, `is_initialized()` | every `validate-*.py` |
| `lib-config.sh` | Shell accessors for `project.config.json` — `cfg_repo_names`, `cfg_project_field`, `cfg_initialized` | shell scripts that need repo/project facts |

Validators read module names, BR prefixes, and repo names from `project.config.json` — never
from hard-coded lists. Before `/onboard` sets `initialized: true`, module/prefix checks are
**skipped** (there is nothing to validate against yet).

### Validators (quality wall)

| Script | Purpose | Used by |
|---|---|---|
| `validate-ticket.py` | Check `tasks/tickets/TICKET-*.md` against `task-ticket.schema.md` | pre-commit hook, `/planner`, `audit.sh` |
| `validate-us.py` | Check `docs/user-stories/US-*.md` against `user-story.schema.md` | pre-commit hook, `/ba`, `audit.sh` |
| `validate-feature-map.py` | Check feature-map index + per-module files for structural errors | pre-commit hook, `/sa`, `audit.sh` |
| `validate-domain.py` | Check `knowledge/L1-domain/<module>-domain.md` for required sections + unique BR-ID definitions | pre-commit hook, `/sa`, `audit.sh` |
| `validate-legacy-scan.py` | Check `knowledge/L2-legacy/scans/<module>-legacy-scan.md` against `legacy-scan.schema.md` (7 sections + Action Plan non-empty) | pre-commit hook, `/legacy-scan`, `audit.sh` |
| `validate-api-contract.py` | Check `architecture/api-contracts/v1/*.yaml` for OpenAPI 3.x structure + project rules (`/v1/` prefix, `page+limit`, no `pageSize`) | pre-commit hook, `/sa`, `audit.sh` |
| `validate-test-case.py` | Check `tests/cases/<module>/TICKET-*-tests.md` against `test-case.schema.md` | pre-commit hook, `/qc`, `audit.sh` |
| `validate-e2e-case.py` | Check `tests/e2e/cases/<module>/TC-E-*.md` against `e2e-case.schema.md` (incl. ≤15 steps, Action+Expected per step) | pre-commit hook, `/e2e-write`, `audit.sh` |

### Security guards

| Script | Purpose | Used by |
|---|---|---|
| `check-secrets.sh` | Scan for AWS / GitHub / GitLab / OpenAI / Anthropic / Slack tokens, private keys, JWTs, DB connection strings with passwords. Allowlist via placeholder words on the same line (`example`, `your-key`, `<TOKEN>`, `XXXX`, `placeholder`, `fake`, `sample`, `REPLACE`, `TODO`). | pre-commit hook (staged files), `audit.sh` (all tracked files), manual |

### Aggregator + git integration

| Script | Purpose |
|---|---|
| `audit.sh` | Run every freshness/drift/validator check and report a single PASS/FAIL summary |
| `git-hooks/pre-commit` | Block commits in THIS workspace with malformed staged tickets / US / feature-map files; runs secret scan; warns on freshness drift |
| `git-hooks/source-repo-pre-commit` | Wrapper installed in the source repos' `.git/hooks/` (repo names from `project.config.json`); calls back to this workspace's `check-secrets.sh` so source-repo commits also get a secret scan |
| `install-hooks.sh` | Symlink workspace hooks into `.git/hooks/`. With `--include-source`, also installs the wrapper in source repos. Idempotent. |

## Usage

```bash
# ── Generators ──
scripts/next-id.sh ticket           # → TICKET-004
scripts/next-id.sh us               # → US-002
scripts/next-id.sh e2e              # → TC-E-001
scripts/next-id.sh adr              # → 003 (next ADR number in architecture/decisions/)
scripts/next-id.sh feature order    # → ORD-036

scripts/scaffold.sh                 # report what would change (diff-safe, no overwrite)
scripts/scaffold.sh --force         # overwrite differing files (used by /onboard after `proceed`)
scripts/scaffold.sh DOMAIN="Retail" CODEBASE_STATE=greenfield   # extra KEY=VALUE substitutions

scripts/feature-map-freshness.sh --check    # show drift, no write
scripts/feature-map-freshness.sh            # write the update

scripts/feature-map-summary.py production   # regenerate <module>.summary.md from <module>.md
scripts/feature-map-summary.py --all        # regenerate every module
scripts/feature-map-summary.py --check production   # exit 1 if summary out of date

scripts/domain-summary.py production        # regenerate <module>-domain.summary.md
scripts/domain-summary.py --all             # all domains
scripts/domain-summary.py --check --all     # exit 1 if any out of date

scripts/archive-active-context.sh us-001            # copy active-context to history/, keep original
scripts/archive-active-context.sh us-001 --reset    # archive then reset to fresh template

scripts/commit-message.sh TICKET-001                # print a conventional commit message to stdout
scripts/commit-message.sh --type=fix TICKET-014     # override the auto-detected type
scripts/commit-message.sh --co-authored TICKET-001  # append Claude Co-Authored-By line
git commit -m "$(scripts/commit-message.sh TICKET-001)"   # typical usage

scripts/legacy-scan-freshness.sh production # FRESH (exit 0) | STALE (1) | MISSING (2)

git diff --name-only HEAD -- _source/ | scripts/doc-sync-diff.py
scripts/doc-sync-diff.py --base HEAD~1

# ── Validators ──
scripts/validate-ticket.py tasks/tickets/TICKET-001.md
scripts/validate-ticket.py tasks/tickets/TICKET-*.md       # batch
scripts/validate-us.py docs/user-stories/US-*.md
scripts/validate-feature-map.py                            # default: index + all per-module

# ── Workspace health ──
scripts/audit.sh                            # one-line PASS/FAIL summary; exit code reflects health

# ── Git hooks (one-time setup) ──
scripts/install-hooks.sh                    # symlinks .git/hooks/pre-commit
# After install, every commit runs validators on staged tickets/US/feature-maps.
# Bypass (not recommended): git commit --no-verify
```

## Why these are scripts, not LLM reasoning

- **next-id**: agents miscount when scanning many files; deterministic `find + sort` is correct every time.
- **feature-map-freshness**: requires `git -C _source/<repo> rev-parse --short HEAD` and exact in-place table edits — fiddly for the model.
- **legacy-scan-freshness**: powers the Skip Conditions in `legacy-scan.md` — agents check this before deciding to re-scan.
- **doc-sync-diff**: walks the doc-sync mapping mechanically; replaces the agent re-reading the schema each pass.
- **validators**: catch malformed output before downstream agents waste tokens reading bad input. Pre-commit hook prevents broken contracts from ever entering git.
- **audit**: one command, one exit code — cheap weekly health check that doesn't need an agent at all.

Each script is idempotent and safe to run repeatedly. They don't modify `_source/` (read-only) and they never silently update docs without the agent producing a Doc Sync Plan first.

## Severity levels (validators)

- **ERROR** — schema violation, blocks downstream agents and the pre-commit hook
- **WARN** — recommended but not blocking; pre-commit still allows the commit

## Compatibility

All shell scripts run on bash 3.2+ (macOS default). Python scripts run on Python 3.9+. No external pip dependencies.

Note: `audit.sh` currently runs 14 sections (1–11 plus 3b/3c/3d) — check the script itself for the authoritative list.
