---
description: Initialize the workspace for a new project — 9-question interview, archives the old project, writes project.config.json, scaffolds from templates/scaffold/.
argument-hint: (no arguments — interactive)
---

# /onboard — New Project Onboarding

Migrate this agentic workspace to a new project. $ARGUMENTS is ignored — the flow is interactive.

Core job: **generate `project.config.json`** (the single source of truth every script and agent
reads) and scaffold the workspace from `templates/scaffold/` via `scripts/scaffold.sh`.
The framework files (.agents/, .claude/commands/, scripts/, contracts) are never touched.

**Re-run behavior — idempotent.** If `project.config.json` already has `initialized: true`,
this is a re-onboard: nothing is blanket-overwritten. `scripts/scaffold.sh` (without `--force`)
diffs existing files and reports conflicts; show the user each conflicting file and get explicit
confirmation before re-running with `--force`.

---

## Pre-flight — block on active work

Read: `CLAUDE.md`, `project.config.json`, `knowledge/L3-session/active-context.md` (if present).

Check for active work:
- any ticket in `active-context.md` or `tasks/kanban.md` with status not done/closed
- an `active-context.md` that has real session content (not the fresh template)

If active work exists:

```
ONBOARD BLOCKED: Active work detected.
  [list tickets and their status; note un-archived active-context]
Complete the work, or run scripts/archive-active-context.sh <topic> --reset,
or reply `abandon` to discard in-progress work.
```

Wait for explicit resolution before continuing.

---

## Phase 1 — Interview (exactly 9 questions)

Tell the user: "I need to ask 9 questions. Answer all before I proceed." Ask all in one message:

```
1. Project name (full):            e.g. "POS System", "HR Platform"

2. Project short code (2-6 chars, UPPERCASE):  e.g. "POS", "HRP"
   → Used in per-module BR prefixes (BR-POS-…). Ticket/US/E2E IDs are GLOBAL
     (TICKET-NNN, US-NNN, TC-E-NNN via scripts/next-id.sh) — the short code does NOT prefix them.

3. Domain / industry:              e.g. "Point of Sale / Retail", "HR & Payroll"

4. Tech stack:
   a. Backend — pick one:
      1) NestJS + TypeScript + PostgreSQL              (pattern file ready)
      2) Next.js fullstack + TypeScript + PostgreSQL   (pattern file ready — single repo:
         API Routes + App Router + Prisma; answer "none" for 4b)
      3) Other (describe) — patterns start from knowledge/stacks/_TEMPLATE.md
         and are filled by SA after the first codebase scan
   b. Frontend (web) — pick one (or "none" if API-only, mobile-only, or Next.js fullstack):
      1) Next.js + shadcn/ui                           (pattern file ready)
      2) Other (describe) — patterns start from _TEMPLATE.md + SA scan
   c. Mobile — pick one (or "none"):
      1) React Native + Expo                           (pattern file ready)
      2) Other (describe) — patterns start from _TEMPLATE.md + SA scan

5. Backend repo name (folder on disk):   e.g. "pos-backend"
   (For Next.js fullstack this IS the app repo — e.g. "pos-web")

6. Frontend repo name (or "none"):       e.g. "pos-frontend"
   (Next.js fullstack → "none"; frontend lives in the BE repo)

7. Mobile repo name (or "none"):         e.g. "pos-mobile"

8. Initial modules (list, even rough):   e.g. "Product, Order, Customer, Staff"

9. Codebase state:
   a. Greenfield   b. Legacy (existing code, no/low spec)   c. Brownfield (existing code, some docs)
```

Wait for all 9 answers; ask only for missing/ambiguous ones. Then:
- Note which of the 4 existing stack files match (Q4): `knowledge/stacks/be/nestjs-ts-pg.md`,
  `be/nextjs-ts-pg.md`, `fe/nextjs-shadcn.md`, `mobile/react-native-expo.md`. Anything else → `_TEMPLATE.md` + SA scan.
- Check `templates/README.md` for a domain template matching Q3 (optional — offer in Phase 2).

---

## Phase 2 — Confirm Scope (explicit `proceed` gate)

First COUNT what will actually be archived — run real commands, do not guess:

```bash
for d in tasks/tickets docs/user-stories docs/draft docs/srs docs/prototypes \
         knowledge/L1-domain knowledge/L2-legacy knowledge/L3-session \
         architecture/decisions architecture/feature-map architecture/db-schema \
         architecture/api-contracts architecture/component-contracts \
         tasks/reviews tasks/sprints tests/cases tests/security; do
  [ -d "$d" ] && echo "$d: $(find "$d" -type f | wc -l | tr -d ' ') files"
done
```

Then present the summary with the REAL counts and wait for explicit `proceed`:

```
## Onboard Scope Summary

New project
  Name / code:  [PROJECT_NAME] ([SHORT_CODE])   Domain: [DOMAIN]
  Stack:        BE [4a] · FE [4b] · Mobile [4c]
  Repos:        BE [Q5] · FE [Q6] · Mobile [Q7]  (via _source/ symlinks)
  Modules:      [Q8 list, with derived slugs + BR prefixes]
  State:        [Q9]

Will be ARCHIVED → _archive/[previous-slug]-[YYYY-MM-DD]/
  [one line per directory/file from the count above, with its real file count]
  plus: tasks/kanban.md, docs/brd.md, tests/regression-map.md (if present)

Will be WRITTEN
  project.config.json                    (initialized: true)
  CLAUDE.md, AGENTS.md                   (from templates/scaffold/ — replaces current)
  [N] scaffold files from templates/scaffold/ (knowledge, tasks, docs, architecture, tests shells)

Will be KEPT AS-IS (framework)
  .agents/**, .claude/commands/**, scripts/**, templates/**, knowledge/stacks/**,
  SECURITY.md, .mcp.json, .gitignore

Reply `proceed` to start, or correct anything above first.
```

If the user changes answers, re-present this summary and wait for `proceed` again.

---

## Phase 3 — Archive Previous Project Artifacts

Determine the previous project slug from the current `CLAUDE.md` §4 (or "workspace" if placeholder).
Run — NO error suppression; if any `mv` fails, report it honestly and stop to resolve:

```bash
PREV=[previous-slug]; DATE=$(date +%Y-%m-%d); DEST="_archive/${PREV}-${DATE}"
mkdir -p "$DEST"

for p in tasks/tickets tasks/sprints tasks/reviews tasks/kanban.md \
         docs/user-stories docs/srs docs/prototypes docs/brd.md docs/draft docs/audits \
         knowledge/L1-domain knowledge/L2-legacy knowledge/L3-session \
         architecture/decisions architecture/feature-map architecture/feature-map.md \
         architecture/db-schema architecture/api-contracts architecture/component-contracts \
         tests/cases tests/security tests/regression-map.md; do
  if [ -e "$p" ]; then mv "$p" "$DEST/$(echo "$p" | tr '/' '_')" || echo "ARCHIVE FAILED: $p"; fi
done

# Remove old _source symlinks ONLY (never real directories or their contents)
find _source -maxdepth 1 -type l -delete
mkdir -p _source
```

Report any `ARCHIVE FAILED` lines to the user before continuing. Directory shells are
recreated by the scaffold in Phase 5 (via `.gitkeep` files) — no manual `mkdir` list needed.

Confirm: `Archive complete → _archive/[previous-slug]-[DATE]/ ([N] files moved).`

---

## Phase 4 — Write project.config.json

Derive per module (from Q8): `slug` = kebab-case name; `name` = Title Case;
`br_prefix` = `BR-` + first 3 letters of the slug, uppercase, de-duplicated within the list.

Check commands per stack (used for `check_cmd`):

| Stack | check_cmd |
|---|---|
| NestJS / Next.js / React / React Native (TS) | `npx --no-install tsc --noEmit -p tsconfig.json` |
| Vue 3 | `npx vue-tsc --noEmit` |
| Django / Python | `python -m mypy src/ --ignore-missing-imports` |
| Laravel / PHP | `./vendor/bin/phpstan analyse src --level=5` |
| Go | `go vet ./...` |
| Spring Boot / Kotlin | `./gradlew compileKotlin` |
| Flutter | `flutter analyze` |

Write the full config (repos the user answered "none" for keep `"name": ""`):

```json
{
  "$comment": "Single source of truth for project facts. Written by /onboard, edited by humans. All scripts, validators, and agents read module/repo/stack facts from HERE.",
  "initialized": true,
  "project": { "name": "[Q1]", "short_code": "[Q2]", "language": "[vi|en — ask if unclear from conversation]" },
  "repos": {
    "be":     { "name": "[Q5]", "stack": "[Q4a]", "check_cmd": "[from table]" },
    "fe":     { "name": "[Q6 or empty]", "stack": "[Q4b or empty]", "check_cmd": "[or empty]" },
    "mobile": { "name": "[Q7 or empty]", "stack": "[Q4c or empty]", "check_cmd": "[or empty]" }
  },
  "modules": [ { "slug": "product", "name": "Product", "br_prefix": "BR-PRO" } ]
}
```

Validate: `python3 -c "import json; json.load(open('project.config.json'))" && echo OK`

---

## Phase 5 — Scaffold from templates/scaffold/

```bash
scripts/scaffold.sh --force \
  DOMAIN="[Q3]" DATABASE="[from Q4a]" CODEBASE_STATE="[Q9]"
```

(`--force` is authorized by the Phase 2 `proceed`. On a RE-onboard, run first WITHOUT
`--force`, walk the user through each reported conflict with a diff, then `--force` only
after confirmation.)

The scaffold creates: CLAUDE.md, AGENTS.md, all knowledge/ shells (L0 files, one
`[slug]-domain.md` per module, integration map, active-context), tasks/ (kanban + tickets/
sprints/ reviews/ shells), docs/ (brd, user-stories/_index, srs/, prototypes/),
architecture/ (feature-map + dir shells), tests/ (e2e index, regression-map, cases/, security/),
copies `tests/e2e/fixtures/test-users.example.json → test-users.json` (tell the user:
**fill real credentials there — the file is gitignored**), and appends repo entries to
`scripts/.check-config.yml`.

**Stack pattern overlay** — after scaffold, for each Phase 1 match:

- BE match → copy `knowledge/stacks/be/[slug].md` over `knowledge/L0-global/be-patterns.md`
- FE match → copy `knowledge/stacks/fe/nextjs-shadcn.md` over `fe-patterns.md`
- Mobile match → copy `knowledge/stacks/mobile/react-native-expo.md` over `mobile-patterns.md`
- **Next.js fullstack special case:** copy BOTH `be/nextjs-ts-pg.md` → `be-patterns.md` AND
  `fe/nextjs-shadcn.md` → `fe-patterns.md` (create it even though FE repo is "none" — the two
  files cover different concerns of the same repo).
- No match → the scaffold's empty template stands; SA fills it from `_TEMPLATE.md` + first codebase scan.

**Domain template (optional, from Phase 2):** if the user accepted a `templates/[type]/` match:
read `templates/[type]/brd.md` → `docs/brd.md`; split `templates/[type]/domain.md` by
`## Module:` headers into `knowledge/L1-domain/[slug]-domain.md` (overwriting scaffold shells).

---

## Phase 6 — Verify Generated Files

CLAUDE.md and AGENTS.md were generated from `templates/scaffold/` in Phase 5 — never write
them inline. Verify by scanning for unreplaced markers (NOT by grepping for old project names):

```bash
grep -rn '{{' CLAUDE.md AGENTS.md knowledge/ tasks/ docs/ architecture/ tests/*.md 2>/dev/null | head
grep -rn '\[PLACEHOLDER\]\|\[PROJECT_NAME\]\|\[SHORT_CODE\]' CLAUDE.md AGENTS.md | head
```

Both must return nothing. If markers remain, re-run Phase 5 with the missing `KEY=VALUE` pairs.

---

## Phase 7 — Brownfield / Legacy Bootstrap (only if Q9 = brownfield or legacy)

Skip entirely for greenfield. Otherwise:

1. **Mark L1 domain files as discovery-required.** Prepend to each `knowledge/L1-domain/[slug]-domain.md`:
   > Status: Needs discovery — brownfield project. Do NOT invent business rules.
   > Run `/legacy-scan [slug]` first; SA fills §1–§5 from the actual code.
2. **Mark pattern files.** Prepend to `be-patterns.md` / `fe-patterns.md`:
   > ⚠️ BROWNFIELD — DO NOT FILL FROM MEMORY. SA must scan `_source/[BE_REPO]/src/` first;
   > patterns here must match what is ACTUALLY in the codebase.
3. **Output the scan plan:** one `/legacy-scan [module]` command per module from Q8, with the note:
   "Scan only the module you'll work on first — you do NOT need all scans up front.
   Order: symlinks (Phase 8) → brd.md → `/legacy-scan [first-module]` → `/sa` (fills patterns) → only then `/ba` or Build."

---

## Phase 8 — Repository Symlinks

For each repo (BE, FE if any, Mobile if any) ask: **A)** skip for now, **B)** repo exists
locally — create symlink, or **C)** needs cloning from a remote.

**Option B** — output for the user to run (or run it if they ask):

```bash
cd [absolute-workspace-path]
ln -s ../../[REPO_NAME] _source/[REPO_NAME]      # or ln -s /custom/abs/path _source/[REPO_NAME]
ls -la _source/[REPO_NAME]
```

**Option C — clone.** NEVER ask the user to paste tokens, SSH keys, or any credential into
this chat, and never embed credentials in URLs. Instead, tell the user to authenticate in
their own terminal first:

```
Authenticate git in YOUR terminal (never paste secrets into this chat):
  GitHub:  run `gh auth login`  (or use an SSH key you already have: ssh -T git@github.com)
  GitLab:  run `glab auth login` or set up an SSH key per GitLab docs
Then run:
  cd [workspace-parent-directory]
  git clone [https-or-ssh-url] [REPO_NAME]
  cd [absolute-workspace-path]
  ln -s ../../[REPO_NAME] _source/[REPO_NAME]
```

---

## Phase 9 — Verification + Summary

```bash
python3 -c "import json; c=json.load(open('project.config.json')); print('config OK, initialized =', c['initialized'])"
ls _archive/ | tail -1
scripts/audit.sh || true          # pre-symlink failures on _source checks are expected
grep -rn '{{' CLAUDE.md AGENTS.md | head -3   # must be empty
```

Output:

```
## /onboard Complete — [PROJECT_NAME]                      ([DATE])

  [OK] Archived → _archive/[previous-slug]-[DATE]/ ([N] files)
  [OK] project.config.json written (initialized: true, [N] modules)
  [OK] Scaffolded [N] files from templates/scaffold/ (CLAUDE.md, AGENTS.md included)
  [OK] Patterns: BE [stack file | template — SA fills] · FE [...] · Mobile [...]
  [OK] tests/e2e/fixtures/test-users.json created — FILL REAL CREDENTIALS (gitignored)

Repos:  [per repo: symlink ready | clone instructions output | skipped]

Needs human input before /ba:
  docs/brd.md                        ← business goals, scope, KPIs
  knowledge/L0-global/tech-stack.md  ← exact versions from package.json etc.

Next steps:
  1. Symlinks (Phase 8 commands above)   2. Fill brd.md
  3. [brownfield/legacy] /legacy-scan [first-module]
     [greenfield]        /ba "Authentication & RBAC" — build the permission base first
  4. /devops — set up CI/CD when ready
```

---

## Error Handling

- **`mv` fails in Phase 3** → report the exact path and error; do not continue until resolved. Never suppress with `|| true`.
- **User wants to undo after Phase 3** → output the exact reverse `mv` commands; never auto-undo.
- **Source repos don't exist yet (greenfield)** → symlinks pending is fine; note it in the summary.
- **Scaffold conflicts on re-run** → `scripts/scaffold.sh` exits 2 and lists them; diff + confirm per file before `--force`.
