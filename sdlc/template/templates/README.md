# Template Library
> Pre-built domain knowledge for common system types.
> Used by /quickstart to pre-populate L1-domain and brd.md.
> Templates are scaffolding only — zero runtime token cost.

---

## Available Templates

| Template | Keywords (auto-detected) | Modules included | RBAC roles |
|---|---|---|---|
| `hrm/` | nhân sự, HR, employee, chấm công, lương | Employee, Attendance, Leave, Payroll, Org | admin, hr_manager, manager, employee |
| `pos/` | bán hàng, POS, quầy, cashier, kho | Product, Category, Sale, Inventory, Report | admin, manager, cashier, warehouse |
| `ecommerce/` | shop, thương mại, order, sản phẩm, product | Product, Order, Customer, Payment, Shipping | admin, seller, customer, support |

### Planned — NOT yet shipped (no template files exist; /quickstart must not offer these)

| Template | Notes |
|---|---|
| `booking/` | Service, Appointment, Schedule, Notification — write brd.md + domain.md before listing it above |
| `crm/` | Lead, Contact, Deal, Activity, Report — write brd.md + domain.md before listing it above |

---

## How templates are applied (during /quickstart)

```
/quickstart detects domain from Q1 answer
    ↓
reads templates/[type]/brd.md
    → writes to docs/brd.md (pre-filled BRD)

reads templates/[type]/domain.md
    → splits into knowledge/L1-domain/[module]-domain.md per module
    → each file clearly marked "[TEMPLATE — review and adjust to your context]"

/onboard Phase 8 module list uses template's module list
```

Template content is a starting point, not a final spec.
BA Agent will refine during /ba runs based on actual user requirements.

---

## Adding a new template

1. Create `templates/[slug]/brd.md` — pre-filled BRD for the domain
2. Create `templates/[slug]/domain.md` — domain knowledge per module (use `## Module: [name]` headers)
3. Add a row to the table above
4. Add detection keywords to `/quickstart` Phase T keyword table
