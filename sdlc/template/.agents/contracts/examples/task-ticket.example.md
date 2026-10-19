# Valid Example — Task Ticket

> Reference example for `task-ticket.schema.md`. Loaded on demand only when format reproduction help is needed.

```markdown
# TICKET-001 — Create ProductionOrder from order.confirmed event

**US-ID:** US-001
**Module:** production
**Layer:** BE
**Status:** Todo
**Complexity:** M

> Note: `production` here is an example module slug — real slugs come from `project.config.json`.
> Sprint and Assignee are optional fields — omitted in this example.

---

## Task Description

Implement a backend event handler that listens for the `order.confirmed` event from the Order Module.
Compute targetQty based on orderQty and currentStock, then create a new ProductionOrder.
Dual-write to the legacy `work_orders` table to avoid breaking the legacy frontend.

---

## Input — Dev Agent must read

| Type | File | Notes |
|---|---|---|
| API Contract | `architecture/api-contracts/v1/production-order.yaml` | POST /production/orders |
| Entity Design | `architecture/db-schema/entities/production-order.entity.design.ts` | Dev generates the migration from this via the stack CLI |
| Domain Knowledge | `knowledge/L1-domain/production-domain.md` | Section: Business Rules |
| Legacy Scan | `knowledge/L2-legacy/scans/production-legacy-scan.md` | Required |
| Business Rules | BR-P01, BR-P02 | |

---

## Acceptance Criteria

**AC1:**
GIVEN order.confirmed event with {orderId: 1, productId: 5, orderQty: 100}
WHEN currentStock = 30
THEN create ProductionOrder with targetQty = 70, status = PENDING

**AC2:**
GIVEN order.confirmed event with orderQty = 50
WHEN currentStock = 60
THEN do NOT create ProductionOrder, emit production.skipped

---

## Definition of Done

- [ ] Static-analysis gate passes (`scripts/typecheck-source.sh [BE_REPO]`)
- [ ] Unit tests: targetQty calculation (3 cases: normal, stock sufficient, stock = 0)
- [ ] Integration test: event handler receives and processes correctly
- [ ] Dual-write to work_orders runs without error
- [ ] Generated migration runs clean
- [ ] Review artifact final round PASS (`tasks/reviews/TICKET-001-review.md`)

---

## Dependencies

**Must be completed first:** None (first ticket in this module)

**Can run in parallel:**
- TICKET-002 (Inventory check service) — no conflict

---

## Dev Notes

Legacy table `work_orders` has column `wo_code` VARCHAR(50) NOT NULL.
Format: `WO-[YYYYMMDD]-[orderId]`. Generate this in the service layer — never leave it null.
```
