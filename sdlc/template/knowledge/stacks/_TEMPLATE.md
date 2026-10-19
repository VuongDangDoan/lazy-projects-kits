# [Stack Name] Patterns
> Stack: [framework] + [language] + [database/platform]
> Type: [be | fe | mobile]
> Slug: [filename without .md — used by /onboard to match]
>
> This file is a reusable pattern library for this stack.
> It is copied to knowledge/L0-global/[be|fe|mobile]-patterns.md during /onboard.
> Customize per-project after copying — the library file stays pristine.

## §index — Section Map

| §   | Topic | Load when |
|-----|-------|-----------|
| §1  | Stack invariants | ALWAYS |
| §2  | [Entity/Model] | [trigger] |
| §3  | [Service/Logic] | [trigger] |
| §4  | [Controller/Router] | [trigger] |
| §5  | [Module/App wiring] | [trigger] |
| §6  | [Auth/Permissions] | [trigger] |
| §7  | [Query/Filtering] | [trigger] |
| §8  | [Transactions] | [trigger] |
| §9  | [State machine] | [trigger] |
| §10 | [Migrations/Schema] | [trigger] |
| §11 | [Common scenarios] | [trigger] |
| §12/§15 | Anti-patterns | ALWAYS before writing code |

---

## §1 — Stack invariants

[Foundational rules that every developer on this stack must follow]
[Banned libraries / approaches]
[Required wrappers / utilities]

## §2 — [Entity/Model]

[How to define a data model in this stack]
[Required fields, base classes, decorators]
[Timestamp, PK, soft-delete conventions]

## §3 — [Service/Business logic]

[Service layer pattern]
[Dependency injection / IoC]
[Error type conventions]

## §4 — [Controller/Router]

[Route definition pattern]
[Request/response typing]
[Auth guard / middleware application]

## §5 — [Module/App wiring]

[How to register a new module]
[Import/export patterns]

## §6 — [Auth & Permissions]

[Auth decorator / middleware usage]
[Role/permission check location]

## §7 — [Query/Filtering]

[Query builder or ORM pattern]
[Pagination implementation]
[Sort and filter mapping]

## §8 — [Transactions]

[Transaction wrapper pattern]
[Rollback handling]

## §9 — [State machines]

[State enum and transition validation]
[Guard location]

## §10 — [Migrations/Schema changes]

[Migration tool and commands]
[Additive-only rules]

## §11 — [Common scenarios]

### File upload
[Pattern]

### Data export
[Pattern]

### Bulk operations
[Pattern]

## §12/§15 — Anti-patterns

[List banned patterns specific to this stack]
[Common mistakes developers make with this framework]
