# Valid Example — User Story (schema v2.0)

> Reference example for `user-story.schema.md` v2.0. Loaded on demand only when format reproduction help is needed.
> Note v2.0 has NO Epic/Priority/Status headers, NO Estimated Complexity section, and a one-line Legacy section.

```markdown
## US-001 — Create Production Order from Sales Order

**Module:** production

---

### User Story
As a **Production Planner**, I want to **automatically create a production order when a sales order is confirmed** so that **no manual entry is required and no orders are missed**.

---

### Business Rule Refs
- BR-P01: A production order may only be created when Order status = CONFIRMED
- BR-P02: targetQty must equal orderQty minus available stock

---

### Acceptance Criteria

**AC1 — Happy path:**
GIVEN Order ORD-001 has status = CONFIRMED and orderQty = 100
WHEN the system receives the order.confirmed event
THEN create a ProductionOrder with targetQty = 100 - currentStock, status = PENDING

**AC2 — Sufficient stock:**
GIVEN Order ORD-002 has orderQty = 50 and currentStock = 60
WHEN the system receives the order.confirmed event
THEN do NOT create a ProductionOrder, log reason = "Stock sufficient"

**AC3 — Order not confirmed:**
GIVEN Order ORD-003 has status = DRAFT
WHEN the API to create a ProductionOrder is called manually
THEN return 422 with message "Order must be CONFIRMED"

---

### SA Handoff Notes

**Entities involved:**
- ProductionOrder: create
- Order: read (fetch orderQty, productId)
- Inventory: read (fetch currentStock)

**Business logic SA must know:**
- targetQty = orderQty - currentStock (floor at 0; if 0, do not create PO)
- If targetQty = 0 → skip PO creation, emit event production.skipped

**Inter-module events:**
- Receives from Order Module: event `order.confirmed` with payload {orderId, productId, orderQty}
- Emits to Material Module: event `production.created` with payload {productionOrderId, materialList}

---

### Legacy
**Touches legacy?** Yes — see `knowledge/L2-legacy/scans/production-legacy-scan.md`
```
