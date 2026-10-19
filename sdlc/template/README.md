# Agentic Workspace Framework

A reusable, project-agnostic workspace that brings a full team of AI agents (BA, SA, Planner, Dev, FE Dev, Mobile Dev, Review, QC, E2E) to any software project.
This repository contains no source code — it is the **intelligence layer** that orchestrates AI agents across the full SDLC.

> Initialize for any project in minutes with `/onboard` (tech users) or `/quickstart` (non-technical users).

---

## What This Repo Is

| This repo | Source code repos |
|---|---|
| Agent roles, contracts, knowledge base | `[BE_REPO]` — any backend stack |
| Orchestration rules, workflows | `[FE_REPO]` — any web frontend (optional) |
| BA / SA / Dev / Review / QC / Planner artifacts | `[MOBILE_REPO]` — any mobile stack (optional) |
| Sprint planning, tickets, reviews, test cases | — |

One workspace instance per project. Run `/onboard` to bind it to your repos.

---

## The Flow Model — 5 Phases, 5 Human Gates

The entire pipeline runs in **5 phases**. A human approves at each phase boundary (**Gates G1–G5**). **Inside a phase, agents chain automatically** — including the Build phase's implement → self-review → self-QC → fix loop, which runs with no human stop between steps.

```
PHASE 1 · BUSINESS ANALYSIS   /ba   (optional /brainstorm first)
  SRS section + User Stories + optional HTML prototype
──────────────────────────────── G1 ────────────────────────────────
PHASE 2 · ARCHITECTURE        /sa US-NNN
  API contract + entity design (+ state machine / ADR)
  SA does NOT write SQL migrations — Dev generates them in Phase 4
──────────────────────────────── G2 ────────────────────────────────
PHASE 3 · PLANNING            /planner US-NNN
  Tickets + kanban + sprint plan
──────────────────────────────── G3 ────────────────────────────────
PHASE 4 · BUILD (per ticket)  /dev | /fe | /mobile TICKET-NNN
  [legacy gate] → implement → typecheck → self-review → self-QC
  → fix loop (max 3 rounds) → Doc Sync Plan → single gate at the end
──────────────────────────────── G4 ────────────────────────────────
PHASE 5 · E2E                 /e2e-write → /e2e
  Live-system verification via Playwright MCP
──────────────────────────────── G5 ────────────────────────────────
```

Two escalation rules inside Phase 4 (see `.agents/implementation-pass.md`):

- **CODE defects** (bug, code-vs-contract mismatch, missing AC coverage) are fixed automatically and re-reviewed — each round appends to `tasks/reviews/TICKET-NNN-review.md`.
- **SPEC defects** (wrong AC, wrong contract, scope creep) **escalate to the human immediately** — spec work belongs to Phase 1/2 gates, never gets "fixed" inside Build. A fix loop that would need a 4th round also escalates.

IDs are **global** and sequential across the project: `US-NNN`, `TICKET-NNN`, `TC-E-NNN`, ADR numbers — always generated via `scripts/next-id.sh {us|ticket|e2e|adr|feature <module>}`.

---

## Repository Structure

```
[WORKSPACE_FOLDER]/
│
├── AGENTS.md                          ← Codex entry point (auto-loaded)
├── CLAUDE.md                          ← Claude Code entry point (auto-loaded)
├── README.md                          ← This file
├── project.config.json                ← Single source of truth: project, repos, stacks,
│                                        check commands, modules — written by /onboard
├── .gitignore
│
├── _source/                           ← Symlinks to source repos (not committed)
│   ├── [BE_REPO]/                     → ../../[BE_REPO]
│   ├── [FE_REPO]/                     → ../../[FE_REPO]     (optional)
│   └── [MOBILE_REPO]/                 → ../../[MOBILE_REPO] (optional)
│
├── .claude/
│   └── commands/                      ← Custom slash commands for Claude Code
│
├── .agents/
│   ├── orchestration.md               ← Master flow — 5 phases, gates G1–G5
│   ├── implementation-pass.md         ← Shared Phase-4 Build spec (/dev, /fe, /mobile)
│   ├── roles/                         ← Agent system prompts
│   │   ├── brainstorm.md
│   │   ├── ba.md
│   │   ├── sa.md
│   │   ├── dev.md
│   │   ├── fe-dev.md
│   │   ├── mobile-dev.md
│   │   ├── review.md
│   │   ├── qc.md
│   │   ├── planner.md
│   │   └── e2e.md
│   └── contracts/                     ← Output schemas per agent
│       ├── srs.schema.md
│       ├── user-story.schema.md
│       ├── api-contract.schema.md
│       ├── task-ticket.schema.md
│       ├── test-case.schema.md
│       ├── legacy-scan.schema.md
│       ├── adr.schema.md
│       ├── e2e-case.schema.md
│       ├── e2e-result.schema.md
│       ├── brainstorm.schema.md
│       ├── active-context.schema.md
│       └── doc-sync.schema.md
│
├── knowledge/
│   ├── stacks/                        ← Pre-built pattern files per tech stack
│   │   ├── be/                        ← nestjs-ts-pg.md, nextjs-ts-pg.md
│   │   ├── fe/                        ← nextjs-shadcn.md
│   │   ├── mobile/                    ← react-native-expo.md
│   │   └── _TEMPLATE.md               ← for any stack not listed
│   ├── L0-global/                     ← Naming, stack, git rules, patterns (on-demand)
│   ├── L1-domain/                     ← Per module — business rules, domain context
│   ├── L2-legacy/                     ← Legacy scans, integration decisions
│   │   └── scans/
│   └── L3-session/                    ← Current sprint, active context (local only)
│
├── docs/                              ← Product + BA artifacts
│   ├── brd.md                         ← Business Requirements Document
│   ├── frd/                           ← Functional requirements index
│   ├── srs/                           ← SRS sections per module (BA output, Phase 1)
│   ├── user-stories/
│   └── prototypes/                    ← Optional low-fi HTML wireframes (BA output)
│
├── architecture/                      ← SA Agent artifacts
│   ├── feature-map.md                 ← Feature catalog index
│   ├── feature-map/                   ← Per-module feature maps
│   ├── api-contracts/
│   ├── db-schema/
│   │   ├── entities/                  ← Entity designs (SA) — Dev generates the actual
│   │   │                                migrations in _source/ during Phase 4
│   │   └── state-machines/
│   └── decisions/                     ← Architecture Decision Records (ADRs)
│
├── tasks/                             ← Planner + Build artifacts
│   ├── kanban.md
│   ├── sprints/
│   ├── tickets/
│   └── reviews/                       ← Per-ticket review artifacts (Phase 4 self-review)
│
├── templates/
│   ├── scaffold/                      ← Workspace scaffold copied by scripts/scaffold.sh
│   ├── devops/                        ← Parameterized CI/CD configs (4 shipped options)
│   ├── hrm/ · pos/ · ecommerce/      ← Industry templates used by /quickstart
│   └── README.md
│
├── scripts/                           ← Deterministic helpers (all read project.config.json)
│   ├── README.md
│   ├── next-id.sh                     ← Global IDs: {ticket|us|e2e|adr|feature <module>}
│   ├── scaffold.sh
│   ├── legacy-scan-freshness.sh
│   ├── feature-map-freshness.sh
│   ├── typecheck-source.sh
│   ├── audit.sh · check-secrets.sh · review-prep.sh · commit-message.sh
│   └── validate-*.py                  ← Schema validators (skip checks pre-onboard)
│
└── tests/                             ← QC + E2E Agent artifacts
    ├── cases/
    ├── e2e/
    │   ├── cases/
    │   ├── fixtures/
    │   └── results/
    ├── security/
    └── regression-map.md
```

---

## Workspace Capabilities

The single-page index of what this workspace can do. Detail lives in the linked files.

### Agents

| Agent | Command | Role file | Primary output | Output contract |
|---|---|---|---|---|
| Brainstorm | `/brainstorm [topic]` | `.agents/roles/brainstorm.md` | `active-context.md` Feature Brief | `brainstorm.schema.md` |
| BA (Phase 1) | `/ba [feature]` | `.agents/roles/ba.md` | `docs/srs/[module]-srs.md` § + `docs/user-stories/US-NNN.md` + optional `docs/prototypes/*.html` | `srs.schema.md`, `user-story.schema.md` (v2) |
| SA (Phase 2) | `/sa US-NNN` | `.agents/roles/sa.md` | API contract YAML + entity design (+ state machine / ADR) — **no SQL migrations** | `api-contract.schema.md`, `adr.schema.md` |
| Planner (Phase 3) | `/planner US-NNN` | `.agents/roles/planner.md` | `tasks/tickets/TICKET-NNN.md` + kanban | `task-ticket.schema.md` |
| Dev — BE (Phase 4) | `/dev TICKET-NNN` | `.agents/roles/dev.md` | BE code in `_source/[BE_REPO]/` incl. generated migrations + Doc Sync Plan | `.agents/implementation-pass.md`, `doc-sync.schema.md` |
| FE Dev (Phase 4) | `/fe TICKET-NNN` | `.agents/roles/fe-dev.md` | FE code in `_source/[FE_REPO]/` + Doc Sync Plan | `.agents/implementation-pass.md`, `doc-sync.schema.md` |
| Mobile Dev (Phase 4) | `/mobile TICKET-NNN` | `.agents/roles/mobile-dev.md` | Mobile code in `_source/[MOBILE_REPO]/` + Doc Sync Plan | `.agents/implementation-pass.md`, `doc-sync.schema.md` |
| Review | `/review TICKET-NNN` (auto-run inside Phase 4) | `.agents/roles/review.md` | `tasks/reviews/TICKET-NNN-review.md` — one `## Round N` per pass, incl. Security Gate | review checklist in role file |
| QC | `/qc TICKET-NNN` (auto-run inside Phase 4) | `.agents/roles/qc.md` | `tests/cases/<module>/TICKET-NNN-tests.md` + severity-scaled security review; verdict appended to the review artifact | `test-case.schema.md` |
| E2E Tester (Phase 5) | `/e2e-write TICKET-NNN`, `/e2e TC-E-NNN` | `.agents/roles/e2e.md` | `tests/e2e/cases/<module>/TC-E-NNN-*.md` + run results | `e2e-case.schema.md`, `e2e-result.schema.md` |

Ticket `Layer` is one of `BE | FE | MOBILE | BE+FE | MOBILE+BE | BE+FE+MOBILE` — mobile is a first-class layer, and `/mobile` is fully symmetric with `/dev` and `/fe`.

Each agent role file has `## Skip Conditions` documenting when it can be skipped and when it MUST run.

### Setup & utility commands

| Command | Purpose | Output |
|---|---|---|
| `/onboard` | Initialize workspace (9 technical questions) | `project.config.json` + scaffold from `templates/scaffold/` via `scripts/scaffold.sh` |
| `/quickstart` | Nontech setup — 1 language question + 3 plain questions; industry templates: hrm / pos / ecommerce | Same engine as `/onboard`, stack auto-selected |
| `/build [description]` | Nontech orchestrator — runs Phases 1→2→3 with plain-language checkpoints at G1, G2, G3 | BA + SA + Planner artifacts |
| `/status` | Plain-language progress dashboard (read-only) | Current phase, gate, tickets, next command |
| `/devops` | CI/CD + deployment setup — copies parameterized configs from `templates/devops/` | CI/CD config in the app repo |
| `/release TICKET-NNN` | Post-G4 helper — audit + secret scan + review-prep; drafts commit message + PR body. **Never commits or pushes `_source/`** | Printed commit message + PR description |
| `/legacy-scan [module] TICKET-NNN` | Interactive Claude+Human ritual — the one human-in-the-loop step inside Phase 4 | `knowledge/L2-legacy/scans/<module>-legacy-scan.md` |
| `/switch-module [module]` | Reset session context when changing modules | Archived `active-context.md` + fresh template |

### Output contracts (12 schemas)

| Schema | Defines | Owner |
|---|---|---|
| `srs.schema.md` | SRS section format per module | BA |
| `user-story.schema.md` (v2) | US format: ACs, BRs, SA Handoff Notes, Legacy Notes | BA |
| `api-contract.schema.md` | OpenAPI spec + entity design + Planner Handoff (`x-dev-notes`) | SA |
| `adr.schema.md` | Architecture Decision Record format + breaking-change ADR block | SA |
| `task-ticket.schema.md` | Ticket format: Input, ACs, DoD, Layer, SA Summary, Dev Notes | Planner |
| `test-case.schema.md` | Test case format + security review template + checklist | QC |
| `e2e-case.schema.md` | E2E test case markdown format | E2E (write mode) |
| `e2e-result.schema.md` | E2E run result format with failure classification | E2E (run mode) |
| `legacy-scan.schema.md` | Legacy scan format: 7 sections from endpoints to action plan | `/legacy-scan` ritual |
| `brainstorm.schema.md` | Feature Brief required fields + handoff block | Brainstorm |
| `active-context.schema.md` | L3 session state format (target ≤ 80 lines) | All agents / `/switch-module` |
| `doc-sync.schema.md` | Code-change → doc-update mapping + **auto-approve tier** for trivial propagation + full-plan protocol for everything else | Dev / FE Dev / Mobile Dev / SA |

Examples (filled samples) live in `.agents/contracts/examples/`.

### project.config.json — single source of truth

Written by `/onboard` (or `/quickstart`), edited by humans. Holds: project name, short code, working language, repo names + stacks + per-repo `check_cmd` (typecheck command), and the module list with BR prefixes. **All scripts, validators, and agents read facts from here — nothing is hard-coded elsewhere.** While `initialized: false`, validators skip module/prefix checks so a fresh clone stays green.

### Deterministic scripts

**Generators / refreshers:**
- `next-id.sh {ticket|us|e2e|adr|feature <module>}` — next global sequential ID
- `scaffold.sh` — copy `templates/scaffold/` into place (run by `/onboard` / `/quickstart`)
- `feature-map-freshness.sh [--check]` — refresh `feature-map.md` §2 SHA stamp
- `feature-map-summary.py` / `domain-summary.py` — regenerate skinny summaries
- `legacy-scan-freshness.sh <module>` — `FRESH`/`STALE`/`MISSING` (exit 0/1/2; 30-day TTL + SHA check)
- `doc-sync-diff.py [--base REF]` — generate starter Doc Sync Plan from git diff
- `archive-active-context.sh <topic> [--reset]` — move L3 to history/
- `typecheck-source.sh [REPO]` — static-analysis gate (`check_cmd` from `project.config.json`)

**Validators** (all read `project.config.json`): `validate-ticket.py`, `validate-us.py`, `validate-feature-map.py`, `validate-api-contract.py`, `validate-domain.py`, `validate-e2e-case.py`, `validate-test-case.py`, `validate-legacy-scan.py`, `validate-active-context.py`.

**Release & aggregation:**
- `audit.sh` — full workspace health check (freshness, drift, validators). Single PASS/FAIL exit.
- `check-secrets.sh` — secret scan; `review-prep.sh <repo>` — pre-PR gates; `commit-message.sh TICKET-NNN` — conventional commit draft (all three driven by `/release`)
- `git-hooks/pre-commit` + `install-hooks.sh` — validates staged files, auto-regenerates summaries

See `scripts/README.md` for full usage.

### Quality wall (auto-enforcement)

- **Pre-commit hook**: blocks commits with malformed tickets/US/feature-maps; auto-regenerates summaries; warns on freshness drift.
- **`audit.sh`**: multi-section health check with a single PASS/FAIL exit.
- **`typecheck-source.sh`**: Phase 4 cannot reach self-review until this passes — it is a precondition, not a review finding.
- **Self-review artifact**: every `_source/` change writes `tasks/reviews/TICKET-NNN-review.md`; QC appends its verdict there.
- **Doc Sync**: every code-touching pass produces a Doc Sync Plan. Trivial propagation-only diffs (≤ 20 lines, no contract/domain/BR content) sit in the **auto-approve tier** — applied by the agent and listed in the G4 report; anything larger waits for approval at the gate.
- **SPEC-defect escalation**: agents never fix a requirement or contract on their own — SPEC defects stop the Build pass and go back to the human (Phase 1/2).
- **Breaking Change Protocol**: any breaking API/DB/event change requires an ADR before Build implements.
- **Legacy Scan TTL**: 30 days + SHA check. Build is blocked at Phase 4 step 0 on STALE or MISSING.
- **E2E mandatory gates**: 5 conditions that require `/e2e` to run and pass before ticket closes (see below).

### Workflow patterns

- **Full pipeline** (new feature): Phase 1 → G1 → Phase 2 → G2 → Phase 3 → G3 → Phase 4 (per ticket) → G4 → Phase 5 → G5. See "Standard Workflow for a New Feature" below.
- **3 lightweight protocols**: Trivial / Bug-fix / Schema-touch. See `.agents/orchestration.md` §2.
- **Use case decision matrix**: see "Use Cases — Pick the Right Workflow" below.

### Stack library — what actually ships

| Tier | Shipped pattern files |
|---|---|
| Backend | `be/nestjs-ts-pg.md` (NestJS + TypeScript + PostgreSQL) · `be/nextjs-ts-pg.md` (Next.js full-stack + Prisma + PostgreSQL) |
| Frontend | `fe/nextjs-shadcn.md` (Next.js + shadcn/ui + Tailwind) |
| Mobile | `mobile/react-native-expo.md` (React Native + Expo) |

**Any other stack** is supported via `knowledge/stacks/_TEMPLATE.md`: `/onboard` copies the template and the SA agent fills it by scanning your repo's actual conventions. `/onboard` copies the chosen file into `knowledge/L0-global/[tier]-patterns.md`.

### DevOps templates — 4 shipped options

`/devops` copies parameterized configs from `templates/devops/`:

| Option | Directory |
|---|---|
| GitHub Actions + Railway | `templates/devops/github-actions-railway/` |
| GitLab CI + Railway | `templates/devops/gitlab-ci-railway/` |
| GitHub Actions + Vercel | `templates/devops/vercel/` |
| GitHub Actions + Docker VPS | `templates/devops/vps-docker/` |

Every shipped CI pipeline runs a **typecheck/lint job before deploy**. Other platforms (Fly.io, AWS ECS, GCP Cloud Run, …) are supported manually on request — no shipped template.

**Secrets rule (absolute):** secrets are never pasted into the chat. Git auth happens via `gh auth login` or SSH in the user's terminal; deploy secrets are set in the platform dashboard or via `gh secret set` run by the user themselves. Commands only tell you *which* secrets to set and *where*.

### Knowledge layers (4)

| Layer | Path | Loaded | Notes |
|---|---|---|---|
| L0 global | `knowledge/L0-global/` | On demand | tech-stack, naming, glossary, git-workflow, crud-page-pattern, be/fe/mobile-patterns |
| L1 domain | `knowledge/L1-domain/` | Per-module | `<module>-domain.md` + auto-generated summary (load summary first) |
| L2 legacy | `knowledge/L2-legacy/scans/` | When `Legacy: Yes` | `<module>-legacy-scan.md`. Freshness check via script. |
| L3 session | `knowledge/L3-session/` | Always (start of task) | `active-context.md` per `active-context.schema.md` (target ≤ 80 lines). |

### Architecture artifacts

| Artifact | Path | Owner |
|---|---|---|
| Feature catalog | `architecture/feature-map.md` (index) + `feature-map/<module>.md` | SA |
| API contracts | `architecture/api-contracts/v1/<feature>.yaml` | SA |
| Entity designs | `architecture/db-schema/entities/<entity>.entity.design.ts` | SA — Dev generates the actual migration from this in `_source/` (Phase 4) |
| State machines | `architecture/db-schema/state-machines/<entity>-states.md` | SA (only if ≥ 3 states) |
| Architectural decisions | `architecture/decisions/NNN-<title>.md` (Nygard format) | SA |
| Component contracts | `architecture/component-contracts/v1/<feature>.md` | SA / FE Dev |
| Review artifacts | `tasks/reviews/TICKET-NNN-review.md` | Review (Phase 4 self-review) |

---

## How the Agent System Works

This workspace uses **10 AI roles**, each with a defined responsibility and output contract:

```
Brainstorm Agent  →  Explore solution space, align on direction (3 options + recommendation)
BA Agent          →  Analyzes requirements, writes SRS section + user stories (+ prototype)
SA Agent          →  Designs API contracts, entity designs, state machines, ADRs
Planner Agent     →  Breaks stories into BE/FE/Mobile tickets, manages kanban
Dev Agent         →  Implements full BE ticket: entities, migrations, DTOs, services, tests
FE Dev Agent      →  Implements full web FE ticket: types, services, hooks, pages, forms
Mobile Dev Agent  →  Implements full mobile ticket: screens, navigation, API integration
Review Agent      →  Proportional code review + Security Gate → tasks/reviews/
QC Agent          →  Test cases per AC + severity-scaled security review
E2E Tester        →  Writes/runs live-system E2E checks via Playwright MCP
```

**Golden rule:** humans approve at the 5 phase gates (G1–G5). **Inside a phase, agents chain automatically** — the Build phase runs implement → self-review → self-QC → fix without stopping. Agents never cross a gate without your approval, and SPEC defects always escalate to you immediately.

---

## Standard Workflow for a New Feature

```
0.  /brainstorm [topic]        ← optional — skip if approach is already clear

1.  /ba [describe the feature]                                        PHASE 1
        → SRS section (docs/srs/) + user story (docs/user-stories/US-NNN.md)
        → optional clickable HTML prototype (docs/prototypes/)

    G1  Review: SRS correct? ACs right? Prototype direction OK?

2.  /sa US-NNN                                                        PHASE 2
        → API contract + entity design (+ state machine / ADR)
        → No SQL — Dev generates migrations from the entity design later

    G2  Review: contract shape, entity design, ADR decisions

3.  /planner US-NNN                                                   PHASE 3
        → tasks/tickets/TICKET-NNN.md per layer (BE / FE / MOBILE) + kanban

    G3  Review: ticket split, complexity, dependency order

4.  /legacy-scan [module] TICKET-NNN   ← only if the ticket touches legacy code
        → Build is blocked at step 0 until the scan is fresh

5.  /dev TICKET-NNN   (or /fe, /mobile per ticket Layer)              PHASE 4
        → ONE command runs the whole loop: implement → typecheck →
          self-review → self-QC → fix (max 3 rounds) → Doc Sync Plan
        → /review and /qc remain available standalone, but Build runs
          them for you inside the pass

    G4  Review ONCE: diff summary + tasks/reviews/TICKET-NNN-review.md
        (final round PASS) + QC verdict + Doc Sync Plan
        → approve → docs sync + ticket → Done

6.  /release TICKET-NNN        ← optional post-G4 helper
        → audit + secret scan + review-prep + drafts commit message & PR body
        → YOU commit and push _source/ — agents never do

7.  /e2e-write TICKET-NNN      ← when a mandatory E2E trigger applies  PHASE 5
    /e2e TC-E-NNN              ← runs against the live system

    G5  PASS → ticket closes. FAIL → classified; a Bug goes back to Phase 4.
```

---

## E2E Mandatory Gates

The following conditions require `/e2e` to run and pass before a ticket closes (else "E2E: not mandatory — [reason]" is recorded at G4):

| Trigger | Example |
|---|---|
| Prod-impact AC | Payment, audit trail, compliance-critical behavior |
| Critical user path changed | Login flow, primary entity creation, multi-step workflow |
| Legacy dual-write involved | User-visible outcome after write-path change |
| Cross-module flow changed | Event in module A triggers visible behavior in module B |
| New permission gate added | Page or action became role-restricted |

When none of these apply, E2E is optional (see `.agents/roles/e2e.md §Skip Conditions`).

---

## Lightweight Workflows — most work doesn't need all 5 phases

**Trivial protocol — typo / CSS / copy / comment**
```
1-line ticket → Phase 4 only (/dev or /fe: implement → self-review, QC skipped) → G4
```
Skips: Phases 1, 2, 3, 5. Use when the change does not alter behavior. Doc Sync auto-approve tier usually covers the doc side.

**Bug-fix protocol — defect with no spec change**
```
[/legacy-scan if applicable] → narrow bug ticket (repro steps) →
Phase 4 full self-audit loop (QC focused on regression) → G4 → [Phase 5 if critical path]
```
Skips: Phases 1–3 (the bug report IS the spec).

**Schema-touch protocol — API/DB shape change without new business rules**
```
Phase 2 (/sa, skip ADR if no new pattern) → G2 → Phase 3 → G3 → Phase 4 → G4 → [Phase 5 if FE consumes it]
```
Skips: Phase 1 (existing US covers behavior — only shapes change).

Hard quality gates hold in every protocol (`.agents/orchestration.md` §2.4): every `_source/` change gets a self-review in `tasks/reviews/`; every legacy touch needs a fresh scan; every code change produces a Doc Sync Plan; every contract change goes through `/sa`.

---

## Use Cases — Pick the Right Workflow

Four guiding questions:

1. **Does it change user-visible BEHAVIOR?** → Phase 1 (BA) needed
2. **Does it change API or DB SHAPE?** → Phase 2 (SA) needed
3. **Does it touch LEGACY code?** → `/legacy-scan` first
4. **Does it touch SECURITY / AUTH / PERMISSIONS?** → self-QC is mandatory, never skip

### Quick decision matrix

| What you're doing | Protocol | Command chain |
|---|---|---|
| Brand-new feature, no existing pattern | Full pipeline | `/brainstorm` → `/ba` →G1→ `/sa` →G2→ `/planner` →G3→ `/dev`/`/fe`/`/mobile` →G4→ `/e2e` →G5 |
| Brand-new feature, pattern exists | Full pipeline (skip brainstorm) | `/ba` →G1→ `/sa` →G2→ `/planner` →G3→ `/dev`/`/fe` →G4 |
| Add column / endpoint / pagination — no new business rule | Schema-touch | `/sa` →G2→ `/planner` →G3→ `/dev`/`/fe` →G4 |
| Behavior bug — API/DB shape unchanged | Bug-fix | `[/legacy-scan]` → ticket → `/dev` or `/fe` (full loop) →G4 |
| Fix typo / label / CSS / copy | Trivial | ticket → `/dev` or `/fe` (review-only) →G4 |
| Pure refactor with green tests | Trivial | ticket → `/dev` or `/fe` (review-only) →G4 |
| Permission / auth / security change | Full pipeline (**QC + E2E never skipped**) | `/ba` →G1→ `/sa` →G2→ `/planner` →G3→ `/dev` →G4→ `/e2e` →G5 |
| Cross-module event added | Full pipeline | `/ba` →G1→ `/sa` (locks event shape) →G2→ `/planner` →G3→ `/dev` per ticket →G4→ `/e2e` →G5 |
| Breaking API/DB/event change | Full pipeline + **ADR required** | SA produces ADR first → Planner adds backward-compat ticket → full pipeline |
| Legacy bug with dual-write logic | Bug-fix + mandatory legacy-scan | `/legacy-scan` → ticket → `/dev` →G4→ `/e2e` (dual-write trigger) |
| New module from scratch | Full pipeline (no legacy-scan needed) | `/brainstorm` → `/ba` →G1→ `/sa` →G2→ `/planner` →G3→ `/dev` →G4 |

### Worked examples

**Case 1 — New feature, full pipeline**

```
/brainstorm "Auto-notify warehouse when stock drops below reorder threshold"
   → 3 options: synchronous check vs event-driven vs scheduled job
   → Agreed: emit inventory.low event from stock module

/ba "Send low-stock notification when inventory drops below threshold"
   → docs/srs/inventory-srs.md § updated
   → docs/user-stories/US-001.md
   G1: approve SRS + ACs

/sa US-001
   → architecture/api-contracts/v1/inventory-alert.yaml
   → architecture/db-schema/entities/alert.entity.design.ts
   → architecture/db-schema/state-machines/alert-states.md
   → knowledge/L1-domain/module-integration-map.md — event shape LOCKED
   G2: approve contract + entity design (no SQL here — Dev generates it)

/planner US-001
   → tasks/tickets/TICKET-001.md (BE: event emitter + handler)
   → tasks/tickets/TICKET-002.md (FE: alert list page)
   G3: approve split

/legacy-scan inventory TICKET-001    ← legacy stock table involvement

/dev TICKET-001
   → one run: implement (incl. generated migration) → typecheck →
     self-review → self-QC → fix loop → Doc Sync Plan
   G4: approve once (review artifact in tasks/reviews/TICKET-001-review.md)

/fe TICKET-002   → same loop → G4

/release TICKET-001              ← drafts commit message + PR body; you push
/e2e-write TICKET-002  →  /e2e TC-E-001    ← critical user path trigger
   G5: PASS → close
```

**Case 2 — Schema-touch: add a status column**

```
/sa "Add status enum column to orders table, expose in list endpoint"
   → updates order.yaml + order.entity.design.ts
   → no ADR needed — additive pattern, no behavior change
   G2: approve

/planner US-NNN
   → BE ticket (column + DTO + mapping) · FE ticket (table column + filter)
   G3: approve

/dev TICKET-NNN     ← generates the migration + implements; full self-audit loop → G4
/fe TICKET-NNN      → G4

Skipped: /brainstorm (additive), Phase 1 (no new user-visible behavior)
```

**Case 3 — Bug fix: list doesn't refresh after update**

```
Write narrow bug ticket:
   Title: "[Module] list doesn't refresh after edit"
   Repro: edit record → save → list still shows old value until reload
   Scope: FE only — missing cache invalidation in mutation handler

/fe TICKET-NNN
   → implement fix → self-review → self-QC (focused regression:
     list refreshes after edit) → G4

Skipped: Phases 1–3 (bug report IS the spec), Phase 5 (not a critical path)
```

**Case 4 — Trivial: copy fix**

```
Write 1-line ticket: "Fix label typo on [Page] — 'Recieve' → 'Receive'"

/fe TICKET-NNN     ← implement → self-review only (QC skipped per Trivial protocol) → G4

Skipped: everything else.
Doc Sync: auto-approve tier — feature-map SHA refresh applied and listed in the G4 report.
```

**Case 5 — Security: restrict DELETE endpoint to admin only**

```
/ba "Only admin role can delete [entity] records"
   → new business rule in [module]-domain.md §4 → G1

/sa US-NNN                ← permission update on existing endpoint → G2
/planner US-NNN           → G3
/dev TICKET-NNN           ← role guard on controller; self-QC MANDATORY:
                            admin can delete; non-admin → 403; no token → 401
                          → G4
/e2e-write TICKET-NNN  →  /e2e TC-E-NNN   ← MANDATORY: new permission gate → G5

Skipped: /brainstorm. NEVER skip QC or E2E on security/permission changes.
```

**Case 6 — Breaking change: rename API field**

```
/sa "Rename response field 'userId' → 'user_id' across all [module] endpoints"
   → ADR required (breaking consumer contract)
   → architecture/decisions/001-rename-userId-to-user_id.md
   → old field marked deprecated + x-sunset-date in the yaml
   G2: approve ADR + deprecation plan

/planner US-NNN
   → TICKET-A: add new field, keep old (dual-output)
   → TICKET-B: remove old field after migration window
   G3: approve

/dev TICKET-A   → full loop → G4
[migration window]
/dev TICKET-B   → full loop → G4
```

**Case 7 — Cross-module event: module A triggers action in module B**

```
/brainstorm "When [entity] is confirmed, auto-create [downstream entity]"
   → Agreed: event-driven, publish via internal event bus

/ba [feature]              ← new BR: trigger rule + payload spec → G1
/sa US-NNN                 ← locks event shape in module-integration-map.md FIRST
                             G2 is blocked until the event is Locked
/planner US-NNN            ← emitter ticket + handler ticket, cross-referenced → G3
/dev TICKET-A              ← module A: emit event → G4
/dev TICKET-B              ← module B: handle event → G4
/e2e TC-E-NNN              ← MANDATORY: cross-module flow trigger → G5
```

---

## Switching Between Modules

When you move from one module to another, always reset context:

```
/switch-module [module-name]
```

This archives the current session context and loads the correct domain knowledge for the new module. Valid module names come from `project.config.json` — set at `/onboard` time.

---

## Working with Legacy Code

Any task that touches existing code requires a legacy scan first:

```
/legacy-scan [module] TICKET-NNN
```

The scan documents existing endpoints, tables, state machines, and known issues.
**The Build phase is blocked at step 0 until the scan file exists and is fresh (≤ 30 days + SHA unchanged).** This is the one human-in-the-loop step inside Phase 4 — legacy understanding cannot be inferred.

---

## Starting From Scratch

### Step 1 — Clone the workspace

```bash
git clone https://github.com/your-org/[WORKSPACE_FOLDER].git
cd [WORKSPACE_FOLDER]
```

### Step 2 — Open Claude Code from the workspace root

```bash
claude
```

Claude Code auto-loads `CLAUDE.md` at startup.

### Step 3 — Run `/onboard` (or `/quickstart` for non-technical users)

```
/onboard
```

The Onboard Agent asks 9 questions about your project (name, stack, modules, repos, greenfield vs. legacy), then:

- writes `project.config.json` — the single source of truth all scripts and agents read
- scaffolds the workspace from `templates/scaffold/` via `scripts/scaffold.sh`
- copies the right stack pattern files from `knowledge/stacks/` (or `_TEMPLATE.md` + an SA scan of your repo for unlisted stacks)
- outputs symlink instructions and, for brownfield projects, per-module legacy-scan commands

Non-technical users run `/quickstart` instead: 1 language question + 3 plain questions; stack auto-selected; industry template applied (hrm / pos / ecommerce).

### Step 4 — Create symlinks to your source repos

After `/onboard` completes, it outputs the exact `ln -s` commands for your repos. Run them from the workspace root:

```bash
ln -s ../../[BE_REPO] _source/[BE_REPO]
ln -s ../../[FE_REPO] _source/[FE_REPO]          # if applicable
ln -s ../../[MOBILE_REPO] _source/[MOBILE_REPO]  # if applicable
```

Verify:

```bash
ls -la _source/
ls _source/[BE_REPO]/src/
```

### Step 5 — Configure CI/CD (optional) and install git hooks

```
/devops                      ← pick one of 4 shipped CI/CD options
```
```bash
scripts/install-hooks.sh
```

Secrets (git auth, deploy tokens) are set by you in your own terminal or platform dashboard — never pasted into the chat.

### Step 6 — Start working

**Greenfield project:**
```
/ba [describe your first feature]      (or /brainstorm first if direction is unclear)
```

**Legacy/brownfield project** — run legacy scans first:
```
/legacy-scan [first-module]
```

Follow the standard workflow from there.

---

## Team Onboarding Checklist

For each new team member:

- [ ] Clone workspace repo + all source repos into the same parent folder
- [ ] Read `project.config.json` (or run `/onboard` if the workspace is uninitialized)
- [ ] Create symlinks per `/onboard` output (Step 4 above)
- [ ] Run `scripts/install-hooks.sh`
- [ ] Read `CLAUDE.md` and `.agents/orchestration.md` before starting — especially the 5-phase / 5-gate model
- [ ] Open Claude Code from the workspace root, not a source repo
- [ ] Never commit directly to `_source/<repo>/` — humans control source-repo commits (use `/release` to draft the commit/PR)

---

## Troubleshooting

**Claude does not load project context**
→ Confirm `CLAUDE.md` is at the workspace root, not inside a subdirectory
→ Open Claude Code from `[WORKSPACE_FOLDER]/`, not a parent or source folder

**`/onboard` was run but placeholders still appear**
→ `/onboard` replaces placeholders in place — confirm the command ran to completion
→ Check `project.config.json`: `initialized` must be `true`
→ Check `knowledge/L3-session/active-context.md` for the onboard session summary

**Validators pass on obviously wrong files**
→ While `project.config.json` has `initialized: false`, validators skip module/prefix checks by design — run `/onboard` first

**Symlink not working on macOS**
→ Confirm source repos are in the same parent folder as the workspace
→ Run `ls -la _source/` to verify symlink targets resolve correctly

**Build pass blocked — no legacy scan**
→ Run `/legacy-scan [module] [TICKET-ID]` first
→ Confirm the scan file exists at `knowledge/L2-legacy/scans/[module]-legacy-scan.md`

**Build pass blocked — legacy scan is STALE**
→ Run `/legacy-scan [module] [TICKET-ID]` to refresh
→ The scan is stale after 30 days or if the source repo HEAD SHA has changed

**`typecheck-source.sh` fails**
→ The per-repo check command is `repos.<key>.check_cmd` in `project.config.json`
→ Phase 4 cannot proceed to self-review until it passes

**Build pass stopped mid-loop and asked me a question**
→ That's a SPEC defect (wrong AC / wrong contract) or a 4th fix round — both escalate by design.
→ Fix the spec via `/ba` or `/sa` (Phases 1/2), then re-run the Build pass.

**Context feels stale after switching tasks**
→ Run `/switch-module [module]` when changing modules
→ Keep `knowledge/L3-session/active-context.md` ≤ 80 lines

---

## Telegram Channel Setup (optional — remote Claude Code access)

```bash
/plugin install telegram@claude-plugins-official
/reload-plugins
/telegram:configure <bot-token>
```

Run multiple bots on one machine by pointing `TELEGRAM_STATE_DIR` at a different directory per instance:

```bash
claude --channels plugin:telegram@claude-plugins-official
/telegram:access pair <code>
```

> Bot tokens are secrets — never commit them to the repo and never paste them into a shared chat. Store in `~/.claude/channels/telegram/.env` or a password manager.
