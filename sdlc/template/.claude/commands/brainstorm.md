---
description: Optional pre-Phase-1 exploration — 3 solution options, no files written, align direction before /ba.
argument-hint: [topic or requirement description]
---

# /brainstorm — Solution Exploration (optional, before Phase 1)

Topic: $ARGUMENTS

For where this sits in the pipeline, see `.agents/orchestration.md` §1 — do not restate the flow here.

---

## When to run / when to skip

Run only when at least ONE trigger is true (per orchestration §1 Phase 1):
- More than one viable approach and unclear which to pick
- Scope touches multiple modules with unclear ownership split
- No precedent pattern exists in the codebase
- High legacy risk — e.g. external-system dual-write, or a schema rename on a core module

**Skip rule:** skip when the approach is obvious or a precedent pattern exists — when in doubt, skip and let `/ba` Step 0 (inline brainstorm) catch it.

---

## Pre-flight

1. Read `knowledge/L3-session/active-context.md` — module + existing constraints.
   - **If missing:** recreate the fresh template (canonical in `scripts/archive-active-context.sh --reset`) or ask the human to run `/onboard` — never silently invent context.
2. Read `.agents/roles/brainstorm.md` — role identity and detailed workflow.
3. Read `.agents/contracts/brainstorm.schema.md` — the handoff-block output contract.

On-demand only: `knowledge/L1-domain/[module]-domain.summary.md`, `knowledge/L2-legacy/scans/[module]-legacy-scan.md`.

---

## Execution

Apply the Brainstorm Agent role. In short (details in the role file):
1. Clarify if needed — max 5 questions, in one message
2. Present 3 distinct solutions with trade-offs, effort, risk, legacy impact
3. Recommend one with reasoning
4. Wait for human agreement — do NOT proceed without it
5. Emit the handoff block per `brainstorm.schema.md`

---

## Output

**No files are written** — this is a thinking/alignment session only. The output is the handoff block:

```
Agreed solution: [Solution N — Name]
Key decisions: [list]
Constraints: [list]
Next command: /ba [refined description]
```

---

## Example triggers

```
/brainstorm sync entity status with an external system (dual-write risk)
/brainstorm this feature spans two modules — where should ownership sit?
/brainstorm first background-job pipeline in this codebase — no precedent
/brainstorm rename a core-module column that three clients consume
```
