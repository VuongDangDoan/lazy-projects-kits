# API Contract Schema v2.0
> SA Agent output MUST include every section below.
> v2.0: tiered state-machine/ADR output (skip when not needed), added `x-dev-notes` block for Planner, stack-agnostic (no ORM or framework assumptions).

---

## Required Output Files

### File 1: API Spec — `architecture/api-contracts/v1/[feature].yaml`
OpenAPI 3.0 format. Each endpoint must have:

```yaml
# Checklist per endpoint:
# - summary + description
# - request body schema with validation rules
# - response schemas: 200, 400, 404, 500
# - security: bearerAuth
# - tags by module
# - x-business-rules: list of BR-IDs applied
# - route prefix is always "v1/[resource]"
# - pagination uses "page" + "limit" (not pageSize)
# - list response shape: { data: [], message, total, limit, page }
# - single response shape: { data: {}, message }
# - error response shape: { message, statusCode }

# Validation error response:
# HTTP 400 — shape per the stack's validation pipeline, documented in
# knowledge/L0-global/be-patterns.md §Validation. Frontend must handle the
# documented shape (some stacks return message as string[], not string).
```

**MANDATORY: Decision Summary block (≤ 15 lines) as a YAML comment header at the top of the file** — format per `roles/sa.md` Step 3. G2 cannot approve a contract without it.

### File 2: Entity Design — `architecture/db-schema/entities/[entity].entity.design.[ext]`
Primary DB artifact. Dev Agent uses this to generate the actual migration via the stack's CLI.
Entity-design conventions (base entity, status enum, FK rules, external-sync ID, indexes) live in `knowledge/L0-global/be-patterns.md` §Entities — do not duplicate here.

> **SQL migration files are NOT produced by SA.** Dev generates the migration from the entity design file via the stack CLI (be-patterns.md §10). SA only outputs the entity design.

### File 3: Planner Handoff — embedded as `dev_notes` block at the end of api-contract yaml

> Token-saving rule: Planner copies this block verbatim into ticket Dev Notes.
> Do NOT also write it as a separate message — it lives inside the yaml.

Append at the bottom of `architecture/api-contracts/v1/[feature].yaml`:

```yaml
# === Ticket-ready dev_notes (Planner copies verbatim into ticket Dev Notes) ===
x-dev-notes:
  us_id: US-XXX
  summary: "[1-2 lines: what is being built and why — distilled from US]"
  endpoints_to_implement:
    - "[METHOD] /v1/resource — [purpose]"
  entities_to_create:
    - "[EntityName] — [table_name] — [PK type, key columns]"
  tables_modified:
    - "[table_name] — [what changed]"     # omit if none
  state_transitions:
    - "[ENTITY]: [FROM] → [TO] (BR-XXX)"  # omit if none
  legacy_touches:
    - "[file or table] — [dual-write?] — [external-sync id?]"  # omit if none
  new_dependencies:
    - "[npm package@version — reason]"   # omit if none
  estimated_dev_tasks:
    - layer: BE
      title: "[short]"
      complexity: S | M | L
    - layer: FE
      title: "[short]"
      complexity: S | M | L
  breaking_changes: "No" | "Yes — [describe]"
```

Planner Step 5 reads ONLY this block + active-context. Does NOT re-distill the yaml.

---

## API Endpoint Template

```yaml
/[module]/[resource]:
  post:
    summary: "[Verb] [resource]"
    description: |
      [Business context description. Why this endpoint exists.]
    tags:
      - [module-name]
    security:
      - bearerAuth: []
    x-business-rules:
      - BR-[ID]: "[Description of rule applied]"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [field1, field2]
            properties:
              field1:
                type: string
                description: "[Description]"
                example: "VALUE"
              field2:
                type: integer
                minimum: 1
                description: "[Description]"
    responses:
      '200':
        description: "[Success — describe specifically]"
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/[ResourceResponse]'
      '400':
        description: "Invalid request"
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
      '422':
        description: "Business rule violation — [list the cases]"
      '404':
        description: "[Resource] not found"
      '500':
        description: "Internal server error"
```

---

## Entity Design — minimal contract

> Full entity-design conventions live in `knowledge/L0-global/be-patterns.md` §Entities. Do not duplicate here.

SA must produce one `[entity-name].entity.design.[ext]` per new entity, with:

- Table name in the project's naming convention, using the stack's base-entity pattern (per be-patterns.md §Entities)
- Every business column: type, nullable, length/precision
- Status enum (if applicable) — soft-delete strategy per be-patterns.md §Entities
- FK relations per the stack's FK convention (be-patterns.md §Entities)
- External-sync ID field only if the entity syncs to an external system (per legacy scan / integration map)
- Index hints in comments for frequently queried columns

If unsure on a pattern, link to the relevant section in `be-patterns.md` rather than re-stating the pattern in the design file.

---

## State Machine Template (for entities with status)

File: `architecture/db-schema/state-machines/[entity]-states.md`

```markdown
# [Entity] State Machine

## States
| State | Description | Terminal? |
|---|---|---|
| DRAFT | Newly created, not yet confirmed | No |
| CONFIRMED | Confirmed and accepted | No |
| IN_PROGRESS | Currently being processed | No |
| COMPLETED | Successfully finished | Yes |
| CANCELLED | Cancelled | Yes |

## Valid Transitions
| From | To | Condition | Business Rule |
|---|---|---|---|
| DRAFT | CONFIRMED | [condition] | BR-XXX |
| CONFIRMED | IN_PROGRESS | [condition] | BR-XXX |
| IN_PROGRESS | COMPLETED | [condition] | BR-XXX |
| [any non-terminal] | CANCELLED | [condition] | BR-XXX |

## Invalid Transitions (must throw error)
- COMPLETED → any state
- CANCELLED → any state
- IN_PROGRESS → DRAFT

## DB Constraint
```sql
ALTER TABLE [table] ADD CONSTRAINT chk_[entity]_status
CHECK (status IN ('DRAFT','CONFIRMED','IN_PROGRESS','COMPLETED','CANCELLED'));
```
```

---

## Validation Checklist — SA self-checks before handoff

- [ ] Decision Summary block (≤ 15 lines) present at the top of the yaml — **G2 requires it**
- [ ] Every endpoint has `x-business-rules`, route is `v1/[resource]`, pagination uses `page`+`limit` (not `pageSize`)
- [ ] Response shapes: list `{ data: [], message, total, limit, page }` · single `{ data: {}, message }` · error `{ message, statusCode }`
- [ ] Entity design follows be-patterns.md §Entities (base entity, status enum, FK convention, external-sync ID only when needed)
- [ ] State-machine.md produced ONLY if ≥3 states or invalid-transition rule (otherwise skip — note "skipped: pure CRUD")
- [ ] ADR produced ONLY if new pattern/dependency/non-obvious trade-off (otherwise skip — note "skipped: conventional")
- [ ] `x-dev-notes` block appended to yaml (Planner reads this verbatim)
- [ ] Legacy compatibility decision noted (external-system dual-write, no DROP/RENAME)
