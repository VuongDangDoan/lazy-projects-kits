# Agent Orchestration Protocol
> Defines who does what, when, with what input, and what output is expected.
> **Flow model: 5 phases, 5 human gates.** Human approves at phase boundaries (G1–G5).
> Inside a phase, agents chain automatically — including the Build phase's self-audit loop.

---

## 0. Setup Commands — run once per project (before any pipeline work)

```
/onboard          ← initialize workspace: interviews, archives old project, scaffolds new,
                    generates project.config.json (single source for modules/repos/stack)
/devops           ← configure CI/CD + deployment infrastructure (run after /onboard + repo symlinks)
```

These are not part of the feature pipeline — they configure the workspace itself.
`/devops` can be re-run at any time to change the deployment platform or add a new environment.

**`project.config.json`** (workspace root) is the single source of truth for: project name,
short code, language, module list + BR prefixes, repo names + stacks + typecheck commands.
All validators and scripts read it. Agents read it instead of hard-coding module or repo names.

---

## 0.1 Inputs — read before any agent runs

The agent pipeline assumes these are current:

| Input | Owner | Loaded by |
|---|---|---|
| `project.config.json` — modules, repos, stack, language | `/onboard` writes; human edits | All scripts + agents that need module/repo facts |
| `docs/brd.md` — Business Requirements (goals, KPIs, scope, stakeholders, deferrals) | PO | `/ba` on demand for stories that need PO-level context |
| `docs/frd/_index.md` — Functional requirements index | PO + BA | `/ba` and `/sa` on demand |
| `knowledge/L3-session/active-context.md` — current session state | Brainstorm/BA/SA/Planner update; reset by `/switch-module` | All agents at start of task |
| `knowledge/L1-domain/<module>-domain.summary.md` — module BRs/entities/events | SA writes; auto-summarized | All agents that need domain context |
| `architecture/feature-map/<module>.summary.md` — feature catalog | SA writes; auto-summarized | All agents before scanning `_source/` |

If any of these are stale (e.g. BRD goals don't match current sprint), the human refreshes them BEFORE invoking the next agent. Agents do not edit the BRD.

---

## 1. Standard Flow — 5 Phases, 5 Gates

```
            ┌─────────────────────────────────────────────────────────────┐
            │  PHASE 1 · BUSINESS ANALYSIS        /ba  (optional /brainstorm first)  │
            │  SRS section + User Stories + Prototype (optional)          │
            └──────────────────────────── G1 ─────────────────────────────┘
            ┌─────────────────────────────────────────────────────────────┐
            │  PHASE 2 · ARCHITECTURE             /sa                     │
            │  API contract + entity design + state machine + ADR         │
            └──────────────────────────── G2 ─────────────────────────────┘
            ┌─────────────────────────────────────────────────────────────┐
            │  PHASE 3 · PLANNING                 /planner                │
            │  Tickets + kanban + sprint plan                             │
            └──────────────────────────── G3 ─────────────────────────────┘
            ┌─────────────────────────────────────────────────────────────┐
            │  PHASE 4 · BUILD (per ticket)       /dev | /fe | /mobile    │
            │  [legacy-scan if needed] → implement → self-review →        │
            │  self-QC → fix findings → loop until clean (max 3 rounds)   │
            │  → Doc Sync Plan. Agents chain WITHOUT human between steps. │
            └──────────────────────────── G4 ─────────────────────────────┘
            ┌─────────────────────────────────────────────────────────────┐
            │  PHASE 5 · E2E                      /e2e-write → /e2e       │
            │  Live-system verification via Playwright MCP                │
            └──────────────────────────── G5 ─────────────────────────────┘
```

### Phase 1 — Business Analysis (`/ba`, optional `/brainstorm` first)

> **Default: skip `/brainstorm`.** Only run it when at least ONE trigger is true:
> - >1 viable approach and unclear which to pick
> - Touches multiple modules with unclear scope split
> - No precedent pattern in the codebase
> - High legacy risk (external-system dual-write, core-module schema rename)
>
> If none apply → start at `/ba` directly. The BA agent has an inline-brainstorm Step 0.

```
[BA Agent]
    reads:   active-context + on-demand: brd, frd index, domain summary
    output:  docs/srs/[module]-srs.md           ← SRS section for the touched module (create or append)
             docs/user-stories/US-NNN.md        ← per user-story.schema.md v2
             docs/user-stories/_index.md        ← updated index
             docs/prototypes/[feature].html     ← OPTIONAL — low-fi clickable wireframe,
                                                  produced when the feature has non-obvious UI
    notify:  "Phase 1 artifacts ready: SRS §, US-NNN[, prototype]. Awaiting G1."
```

**GATE G1 — human approves:** SRS section correct, US acceptance criteria right, prototype direction OK.
Corrections loop back into `/ba`; approval unlocks Phase 2.

### Phase 2 — Architecture (`/sa US-NNN`)

```
[SA Agent]
    reads:   active-context + US Handoff Notes + on-demand: naming-conv, tech-stack,
             domain, integration-map + _source (read-only, if legacy)
    output:  architecture/api-contracts/v1/[feature].yaml   (with x-dev-notes block)
             architecture/db-schema/entities/[entity].entity.design.ts
             architecture/db-schema/state-machines/[entity]-states.md   (only if ≥3 states)
             architecture/decisions/[NNN]-[title].md                    (only if new pattern/dependency)
    note:    SA does NOT produce SQL migration files — Dev generates migrations
             from the entity design via the stack's CLI during Phase 4.
    notify:  "Phase 2 artifacts ready. Awaiting G2."
```

**GATE G2 — human approves:** contract shape, entity design, ADR decisions.
Every API/DB contract change in the project goes through this phase — no exceptions.

### Phase 3 — Planning (`/planner US-NNN`)

```
[Planner Agent]
    reads:   active-context + api-contract x-dev-notes + kanban
    output:  tasks/tickets/TICKET-NNN.md   (one per BE / FE / MOBILE slice, per task-ticket.schema.md)
             tasks/kanban.md updated
    notify:  "Phase 3: N tickets ready. Awaiting G3."
```

**GATE G3 — human approves:** ticket split, complexity, dependency order.

### Phase 4 — Build (`/dev` | `/fe` | `/mobile` per ticket) — self-auditing, one gate at the end

Inside this phase agents chain automatically. The human is NOT consulted between
implement → review → QC → fix. The single approval happens at G4.

```
[0. Legacy gate]   scripts/legacy-scan-freshness.sh [module]
                   MISSING/STALE → STOP, human runs /legacy-scan (interactive ritual, §3)
                   FRESH → proceed
    │
    ▼
[1. Implement]     Dev/FE/Mobile agent writes the full ticket into _source/<repo>/
                   then runs scripts/typecheck-source.sh — must pass before step 2
    │
    ▼
[2. Self-review]   Review pass per .agents/roles/review.md (proportional checklist)
                   writes tasks/reviews/TICKET-NNN-review.md  (round N appended)
    │
    ▼
[3. Self-QC]       QC pass per .agents/roles/qc.md — test cases + severity-scaled
                   security review; executes runnable tests where the stack allows
    │
    ▼
[4. Fix loop]      Findings classified:
                     - CODE defect (bug, contract mismatch in code, missing AC)
                          → agent fixes directly, re-run steps 1–3          ← auto
                     - SPEC defect (AC wrong, contract itself wrong, scope creep)
                          → STOP, escalate to human — belongs to G1/G2, not Build
                   Max 3 review rounds. Round 4 needed → STOP, escalate with findings.
    │
    ▼
[5. Doc Sync Plan] produced per doc-sync.schema.md (auto-approve tier applies
                   for trivial diffs — see the schema §Auto-approve)
    │
    ▼
GATE G4 — human reviews ONCE: code diff summary + review artifact (final round PASS)
          + QC verdict + Doc Sync Plan. Approve → docs sync + ticket → Done on kanban.
```

**Commits:** the human commits `_source/` changes after G4. Agents never auto-commit source repos.

### Phase 5 — E2E (`/e2e-write` → `/e2e`)

Mandatory when ANY trigger is true (else record "E2E: not mandatory — [reason]" at G4):
- Prod-impact AC (revenue, payment, audit, compliance-critical behavior)
- Critical user path changed (login, primary entity creation, multi-step flow)
- Legacy dual-write involved
- Cross-module flow changed (event triggers downstream UI state change)
- New permission gate added

```
[E2E Agent]  /e2e-write TICKET-NNN   → tests/e2e/cases/<module>/TC-E-NNN-[slug].md
             /e2e TC-E-NNN           → run against live env via Playwright MCP
             PASS → GATE G5: ticket closes
             FAIL → classify (Bug/Stale/Env/Flaky) → Bug goes back to Phase 4 (same ticket)
```

---

## 2. Lightweight Flows — skip phases safely

The §1 full pipeline is for new features. Most work doesn't need all 5 phases.
**Each protocol still upholds the hard quality gates in §2.4.**

### 2.1 Trivial change protocol — typo / CSS / copy / comment

```
[Human] writes 1-line ticket → Phase 4 only (implement → self-review → G4)
```
**Skipped:** Phases 1, 2, 3, 5; self-QC inside Phase 4 (review only)
**Applies when:** change does not alter behavior
**Quality kept:** review still runs on every `_source/` diff; Doc Sync auto-approve tier applies.

### 2.2 Bug-fix protocol — defect with no spec change

```
[Human] narrow bug ticket (repro steps) → Phase 4 (full self-audit loop, QC focused
on regression around the bug) → G4 → [Phase 5 only if critical user path]
```
**Skipped:** Phases 1–3 (bug report IS the spec)
**Quality kept:** legacy gate, full self-review, focused QC, optional E2E.

### 2.3 Schema-touch protocol — API/DB change without new business rules

```
Phase 2 (/sa, skip ADR if no new pattern) → Phase 3 → Phase 4 → [Phase 5 if FE consumes it]
```
**Skipped:** Phase 1 (existing US covers behavior — just shape changes)
**Quality kept:** SA still owns the contract; full Build self-audit chain.

### 2.4 Hard quality gates — apply to every protocol

1. Every `_source/` code change → self-review runs and writes `tasks/reviews/`
2. Every legacy table/endpoint touched → fresh-enough scan covers it
3. Every code change → Doc Sync Plan produced (auto-approve tier may resolve it without a human stop)
4. Every API/DB contract change → SA owns it (never let Build invent endpoint shape)
5. Every new business rule → lands in `domain.md` §4
6. Per-agent skip rules in each role file (`## Skip Conditions`) take precedence when more specific

---

## 3. Flow — Legacy Scan (interactive ritual)

The one human-in-the-loop step inside Phase 4, because legacy understanding cannot be inferred.

```
[Human] /legacy-scan [module] [TICKET-NNN]     (ticket optional for pre-emptive scans)
    │
    ▼
[Claude] reads _source/<be-repo>/… legacy code for the module FIRST
[Claude] then confirms each section from legacy-scan.schema.md with the human
    │
    ▼
[Claude] creates: knowledge/L2-legacy/scans/[module]-legacy-scan.md
[Claude] notify:  "Legacy scan complete. Action plan in section 7. Build phase may resume."
```

### 3.1 Freshness Rule (TTL)

A legacy scan is **fresh** when BOTH conditions are true:
- Age ≤ 30 days (from `date` field in scan file header)
- No commits to the module's `_source` path since the scan date

`scripts/legacy-scan-freshness.sh <module>` enforces this. Exit codes:
- `0 FRESH` — scan is valid, Build can proceed
- `1 STALE` — either expired or source changed — re-scan required
- `2 MISSING` — no scan file exists — scan required before any Build work

**The Build agent checks freshness at Phase 4 step 0 (before reading source).**

---

## 4. Context Loading Matrix

> **Default rule:** Every agent reads `active-context.md` first. It accumulates decisions from
> all prior agents. L0/L1 files load ON-DEMAND only when a specific lookup is needed.

| Agent | Always load | On-demand only | _source |
|---|---|---|---|
| Brainstorm | active-context | domain (BRs/entities), legacy scan | ❌ |
| BA | active-context | `docs/brd.md`, frd index, domain (BRs), integration-map | ❌ |
| SA | active-context + US Handoff Notes section | naming-conv, tech-stack, domain, integration-map | ✅ BE read-only if legacy |
| Planner | active-context + api-contract `x-dev-notes` | US (if SA decisions insufficient) | ❌ |
| Dev (BE) | active-context + ticket | legacy §7 (if flagged), api-contract yaml, be-patterns §s | ✅ via symlink (writes) |
| FE Dev | active-context + ticket | api-contract yaml, fe-patterns §s | ✅ via symlink (writes) |
| Mobile Dev | active-context + ticket | api-contract yaml, mobile-patterns §s | ✅ via symlink (writes) |
| Review | ticket + generated diff + review artifact (prior rounds) | api-contract yaml | ✅ read diff |
| QC | active-context + ticket + regression-map + review artifact | state-machine doc, legacy scan | ❌ |
| E2E | case file + fixtures + e2e schemas | feature-map summary, domain summary | ❌ |

---

## 5. Gate & Handoff Protocol

### Required output before each gate

| Gate | Producing phase | Required artifacts |
|---|---|---|
| G1 | Phase 1 (BA) | `docs/srs/[module]-srs.md` §, `docs/user-stories/US-NNN.md` per schema v2, index updated, optional prototype |
| G2 | Phase 2 (SA) | api-contract yaml (with `x-dev-notes`) + entity design (+ state machine / ADR when triggered) |
| G3 | Phase 3 (Planner) | `tasks/tickets/TICKET-NNN.md` per schema, kanban updated |
| G4 | Phase 4 (Build) | typecheck PASS + `tasks/reviews/TICKET-NNN-review.md` final round PASS + QC verdict + Doc Sync Plan |
| G5 | Phase 5 (E2E) | e2e result per `e2e-result.schema.md` with verdict PASS |

### A gate is blocked when

- Legacy task has no fresh scan → Phase 4 is blocked at step 0
- US has no SA Handoff Notes section filled → Phase 2 is blocked
- Ticket has no Acceptance Criteria → Phase 4 is blocked
- Review round 3 still FAIL, or a SPEC defect surfaced → Phase 4 escalates to human immediately
  (do not wait for G4 — the gate cannot approve what the loop could not converge)

---

## 6. Switch Module Protocol

When human runs `/switch-module [module]`:

```
1. Archive current active-context.md
   → knowledge/L3-session/history/[YYYY-MM-DD]-[old-module].md
   (scripts/archive-active-context.sh [module] --reset does 1+2 in one step)

2. Reset active-context.md to the fresh template (script-owned — commands must not
   maintain a second copy of this template)

3. Check: does knowledge/L2-legacy/scans/[new-module]-legacy-scan.md exist?
   If not → notify: "No legacy scan found for [module].
   Run /legacy-scan [module] before starting Build work."

4. Confirm context switch complete
```

Valid module names come from `project.config.json` — never from a hard-coded list.

---

## 7. Immutable Rules

1. **Human gates sit at phase boundaries (G1–G5).** Inside a phase, agents chain
   automatically — the Build phase's implement → review → QC → fix loop runs without
   human stops. Agents never cross a phase boundary without gate approval.
2. **`_source/<repo>/` symlinks are the write path for implementation** — Build agents
   write through them within ticket scope; all other agents treat `_source/` as read-only.
   Humans commit; agents never auto-commit source repos.
3. **Never infer legacy behavior** — read `_source/` or run `/legacy-scan`
4. **Output contract is law** — missing field means output is not done
5. **Module switch resets context** — never carry over context from a previous module
6. **SPEC defects always escalate** — no agent "fixes" a requirement or contract on its own;
   that work belongs to Phase 1/2 and their gates.

---

## 8. Feedback Triage — workspace self-learning

Every time the human gives a correction, preference, or improvement feedback, the active agent MUST triage it into one of 3 buckets BEFORE moving on.

### 8.1 Triage buckets

| Bucket | When | Where it lands |
|---|---|---|
| **One-off** | Feedback only applies to this specific ticket / file / session | Apply inline. Nothing persisted. |
| **Personal preference / context** | About how the user collaborates, across all conversations | The assistant's persistent memory (per its own memory protocol) |
| **Systemic agent / code rule** | Should change agent behavior on every future run | Edit the relevant file: `.agents/roles/*.md`, `knowledge/L0-global/*-patterns.md`, `.claude/commands/*.md`, `.agents/orchestration.md`, or `.agents/contracts/*.md` |

### 8.2 Mandatory persistence ack

After applying any feedback, the agent's response MUST end with a 1-line persistence ack:

```
📝 Persisted: <bucket> → <file>:<line>  (or "📝 No persist — one-off")
```

If the bucket is "Systemic", also append a 1-line entry to `knowledge/L0-global/feedback-log.md`:

```
- YYYY-MM-DD · <category> · <one-line what changed> · landed: <file>
```

Categories: `agent-behavior`, `code-convention`, `output-format`, `skip-rule`, `naming`, `anti-pattern`, `review-check`.

### 8.3 Triage skip conditions

Skip the triage entirely (no ack needed) when the user message is:
- Pure acknowledgment / approval: "ok", "got it", "good", "approve", "agreed", "yes"
- A new task request (not feedback on prior work)
- A question (not a correction)
- A confirmation of plan / suggestion the agent just made

### 8.4 Revert protocol

If the user says the persisted rule was wrong:
1. Revert the file edit
2. Remove the matching line from `feedback-log.md`
3. Confirm with: `🗑️ Reverted: <file>:<old-line>`

### 8.5 Reading the feedback log

`knowledge/L0-global/feedback-log.md` is **NOT auto-loaded** by any agent. Load on-demand only when:
- The human asks "what has the workspace learned recently?"
- An agent suspects a relevant rule may exist for an edge case (grep by category)
- Periodic audit (quarterly) to consolidate similar entries into pattern docs

---

## 9. Cross-Module Event Protocol

When a user story creates a new event or modifies an existing event payload:

### 9.1 SA must lock the event shape BEFORE Planner splits tickets

1. SA adds the event to `knowledge/L1-domain/module-integration-map.md §Event Catalogue` with full payload schema
2. SA marks it as "Locked — agreed [YYYY-MM-DD], producing module: [M], consuming modules: [M2, M3]"
3. G2 is blocked until the event shape is in the integration-map

### 9.2 Tickets that span multiple modules

If US A produces an event and US B consumes it:
- BA must note the dependency in both user stories: `Depends on: US-NNN (event shape)`
- Planner creates two tickets — they must reference each other in Dev Notes
- The producing ticket must implement the event with the agreed payload, even if the consuming ticket is in a future sprint

### 9.3 Enforcement (inside Phase 4)

```
Build agent encounters an event in the ticket:
    ├── Event "Locked" in module-integration-map.md → proceed
    └── Event absent or "Draft" → STOP, escalate: "Event [name] has no locked shape.
        SA must lock the payload (Phase 2) before Build implements."
```

### 9.4 Changing an existing event (breaking change)

Any change to a published event payload → treat as a breaking change (§10 below).
SA must amend the integration-map AND create an ADR before Build implements.

---

## 10. Breaking Change Protocol

A change is **breaking** when it removes, renames, or incompatibly changes a field, endpoint, event payload, or behavior that existing callers depend on.

### 10.1 Detection

Breaking when ANY of the following are true:
- `x-dev-notes.breaking_changes: "Yes — ..."` in the api-contract yaml
- An existing API field is removed or renamed
- An existing event payload field is removed or type-changed
- A DB column is dropped, renamed, or type-changed with active callers
- An endpoint HTTP method or URL is changed

### 10.2 Protocol — required before Build implements

1. **SA creates an ADR** in `architecture/decisions/[NNN]-[title].md` per `adr.schema.md` — including the Breaking Change Detail block
2. **SA marks the old behavior deprecated** in the api-contract yaml: `deprecated: true` + `x-sunset-date: [YYYY-MM-DD]`
3. **Planner creates a backward-compat ticket** (separate from the feature ticket):
   - Old endpoint/behavior stays live for N sprints (human agrees on N)
   - Client tickets (FE, Mobile) to migrate created in backlog
   - The feature ticket is blocked on this backward-compat ticket being created first

### 10.3 Enforcement gate (inside Phase 4)

```
Build agent reads ticket x-dev-notes.breaking_changes field:
    ├── "No" → proceed normally
    └── "Yes — [describe]" → STOP before writing any code
            ADR with Breaking Change Detail block exists → proceed
            No ADR → escalate: "Breaking change requires ADR first (Phase 2)."
```
