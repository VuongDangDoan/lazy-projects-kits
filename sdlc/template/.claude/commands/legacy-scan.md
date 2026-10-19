---
description: Interactive legacy scan ritual — documents existing behavior before Build touches legacy code
argument-hint: [module] [TICKET-ID?]
---

# /legacy-scan — Interactive Legacy Scan (Claude + Human)

Trigger: `/legacy-scan [module] [TICKET-ID?]` — the ticket is **optional**; pre-emptive scans
(before any ticket exists) are a normal use.

Output: `knowledge/L2-legacy/scans/[module]-legacy-scan.md`

## Purpose

Blocking gate before any Build work that touches existing code (Phase 4 Gate 1 in
`.agents/implementation-pass.md`). Documents legacy behavior so Build agents never infer or guess.
This is the one human-in-the-loop step inside Phase 4 — legacy understanding cannot be automated.

## Pre-flight

1. Read `knowledge/L3-session/active-context.md`
2. Read `.agents/contracts/legacy-scan.schema.md` — scan output contract
3. **Pick the repo(s) to scan** — the repo(s) the ticket/module actually touches: `be`, `fe`,
   and/or `mobile`, with names from `project.config.json` `repos`. A BE ticket scans the BE repo;
   a mobile ticket scans the mobile repo; a cross-layer ticket scans each touched repo.
   No ticket given → ask the human which layer(s) the upcoming work touches.
4. **Locate the module's code** in each `_source/<repo>/` via glob/grep on the module name —
   directory layout differs per stack (feature folders, `src/modules/`, package-per-domain, …).
   Never assume a layout; find it.

**Read the source first. Form your own understanding. Then confirm with the human.**
That is cheaper than asking the human to describe code you can read directly.

## Fast mode — small modules

If the located module code is **≤ 5 source files**, skip the section-by-section stops: read
everything, draft all 7 sections at once, and present a **single confirmation** to the human
("here is my full reading — corrections?"). One stop instead of seven.

## Execution — Interactive Ritual (default mode)

Read the module's legacy code first, then confirm each section from `legacy-scan.schema.md`
with the human, one at a time:

### Section 1 — Legacy Endpoints / Entry Points
"I can see the following endpoints (or screens/entry points, for FE/mobile) in `_source/<repo>/…`:
[list]. Are these all the legacy entry points relevant [to TICKET-ID]? Who currently calls each one?"

### Section 2 — Database Tables / Persisted State
"The legacy tables (or local stores/caches, for FE/mobile) I can see are: [tables + columns].
Are there columns in use I must not touch? Any storage not visible in this path?"

### Section 3 — Business Logic
"From reading the code, the current validation/business logic appears to be: [reading].
Accurate? Any behavior not visible in code (config-driven, DB-stored rules, undocumented side effects)?"

### Section 4 — Reverse Dependencies
"These appear to depend on the legacy path: [imports, callers, client references].
Other callers outside this codebase (external services, mobile app, scheduled jobs)?"

### Section 5 — Test Coverage
"I [found / did not find] existing tests at: [path or 'none']. Coverage elsewhere?"

### Section 6 — Risk and Rollback
"I assess breaking risk as [High/Medium/Low] because [reason]. What is the rollback plan?"

### Section 7 — Action Plan
Synthesize sections 1–6 into a concrete plan: exactly what Build must do and must NOT touch.
Human confirms or corrects.

## Output

After confirmation, write `knowledge/L2-legacy/scans/[module]-legacy-scan.md` following
`legacy-scan.schema.md` exactly (including the `**Scan date:**` header the freshness script reads).

## Re-scan Protocol — replace wholesale

When a scan for the module already exists (STALE, or the new work touches areas it doesn't cover):

1. **Archive the old scan first:** append its full content (with a dated separator header) to
   `knowledge/L2-legacy/scans/[module]-legacy-scan-archive.md`.
2. **Replace the scan file wholesale** with a fresh, schema-shaped scan from this ritual.

Never leave a patchwork of appended partial sections — the scan file is always one coherent,
schema-shaped document; history lives in the archive.

## Completion Signal

```
Legacy scan complete — [module][ / TICKET-ID]
File: knowledge/L2-legacy/scans/[module]-legacy-scan.md
Repos scanned: [names]
Breaking risk: [High | Medium | Low]
Action plan: §7 of the scan file

Build phase may resume[: /dev | /fe | /mobile TICKET-ID].
```

## Skip Conditions

Run `scripts/legacy-scan-freshness.sh [module]` first — `FRESH` (exit 0), `STALE` (1), `MISSING` (2).

**Safe to skip a fresh scan when:**
- Freshness returns `FRESH` AND the existing scan covers the exact endpoint(s)/table(s) the ticket touches
- The ticket is pure net-new code in a net-new module — no legacy intersection at all
  (confirm by locating the module in `_source/` once if uncertain)

**Never skip when:**
- The endpoint or table the ticket touches is NOT listed in the existing scan
- Freshness returns `STALE` or `MISSING`
- The ticket changes legacy response format, dual-write logic, or column types

When skipping, note in the ticket Dev Notes:
`Legacy scan: covered by existing [module]-legacy-scan.md (sections N, M).`
