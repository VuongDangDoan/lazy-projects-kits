# POS Domain Knowledge Template
> [TEMPLATE — split into per-module L1-domain files during /quickstart]
> Each "## Module:" section becomes knowledge/L1-domain/[slug]-domain.md

---

## Module: product
> Slug: product | Status: Planned (from template)

### 1. Overview
Quản lý danh mục sản phẩm và giá bán.

### 2. Entities

**Product**
- id, code (unique, auto or manual), name, description
- categoryId (FK), barcode (nullable, unique when set)
- sellingPrice (Decimal 12,2), costPrice (Decimal 12,2)
- unit: PCS | KG | LITER | BOX | PACK
- imageUrl (nullable), isActive (default: true)
- currentStock (denormalized — updated by inventory moves, source of truth is InventoryLog)
- lowStockThreshold (default: 10)
- createdAt, updatedAt, deletedAt

**Category**
- id, name, slug (unique), parentId (nullable), sortOrder

### 3. Business Rules
- BR-PRD-001: Product code auto-generated as PRD-NNNN if not manually provided
- BR-PRD-002: sellingPrice must be > 0; costPrice >= 0
- BR-PRD-003: Deleting a product is soft-delete only — historical sales are preserved
- BR-PRD-004: Product with currentStock = 0 can still appear in system but cannot be sold
- BR-PRD-005: Alert triggered when currentStock < lowStockThreshold

### 4. RBAC
| Action | admin | manager | cashier | warehouse |
|---|---|---|---|---|
| View products | ✅ | ✅ | ✅ | ✅ |
| Create/edit product | ✅ | ✅ | ❌ | ❌ |
| Set price | ✅ | ✅ | ❌ | ❌ |
| Delete product | ✅ | ❌ | ❌ | ❌ |

---

## Module: inventory
> Slug: inventory | Status: Planned (from template)

### 1. Overview
Theo dõi tồn kho và các biến động nhập/xuất kho.

### 2. Entities

**InventoryLog**
- id, productId (FK), type: PURCHASE | SALE | ADJUSTMENT | RETURN | DAMAGE
- quantity (positive = in, negative = out), unitCost (nullable)
- beforeStock, afterStock (snapshot at time of move)
- referenceId (nullable — saleId or purchaseId), referenceType
- notes, performedById (FK → User), createdAt

**StockAdjustment** (for manual corrections)
- id, productId (FK), reason, quantityDelta, performedById, approvedById, createdAt

### 3. Business Rules
- BR-INV-001: Every stock change must have an InventoryLog entry (immutable audit trail)
- BR-INV-002: Product.currentStock = sum of all InventoryLog quantities for that product
- BR-INV-003: Manual adjustments require a reason and manager approval
- BR-INV-004: Stock cannot go negative — SALE blocked if currentStock < requested quantity
- BR-INV-005: DAMAGE and ADJUSTMENT logs require notes; SALE and PURCHASE do not

### 4. RBAC
| Action | admin | manager | cashier | warehouse |
|---|---|---|---|---|
| View stock levels | ✅ | ✅ | ✅ | ✅ |
| Record purchase (incoming) | ✅ | ✅ | ❌ | ✅ |
| Stock adjustment | ✅ | ✅ (approve) | ❌ | ✅ (request) |
| View inventory log | ✅ | ✅ | ❌ | ✅ |

---

## Module: sale
> Slug: sale | Status: Planned (from template)

### 1. Overview
Giao dịch bán hàng tại quầy.

### 2. Entities

**Sale**
- id, code (unique, auto: SALE-YYYYMMDD-NNN), cashierId (FK → User)
- status: PENDING | COMPLETED | VOIDED
- subtotal, discountAmount, discountType: AMOUNT | PERCENT
- totalAmount, paymentMethod: CASH | BANK_TRANSFER | MIXED
- cashReceived (nullable), changeAmount (nullable)
- customerId (nullable FK → Customer), shiftId (FK → Shift)
- completedAt, voidedAt, voidReason, createdAt

**SaleItem**
- id, saleId (FK), productId (FK), productName (snapshot), unitPrice (snapshot)
- quantity, subtotal (unitPrice × quantity)

### 3. Business Rules
- BR-SAL-001: SaleItem.productName and unitPrice are snapshots — never change after sale completes
- BR-SAL-002: Sale cannot complete if any SaleItem.quantity > product.currentStock
- BR-SAL-003: Voiding a completed sale requires manager approval and restores stock
- BR-SAL-004: CASH payment: cashReceived >= totalAmount; change = cashReceived - totalAmount
- BR-SAL-005: A sale can only be voided on the same day it was created (next day → contact admin)

### 4. RBAC
| Action | admin | manager | cashier | warehouse |
|---|---|---|---|---|
| Create sale | ✅ | ✅ | ✅ | ❌ |
| Apply discount | ✅ | ✅ | ≤10% only | ❌ |
| Void sale | ✅ | ✅ | ❌ | ❌ |
| View sale history | ✅ | ✅ | Own shift | ❌ |

---

## Module: shift
> Slug: shift | Status: Planned (from template)

### 1. Overview
Quản lý ca làm việc và đối soát doanh thu cuối ca.

### 2. Entities

**Shift**
- id, cashierId (FK → User), openedAt, closedAt (nullable)
- status: OPEN | CLOSED
- openingCash, closingCash (nullable), expectedCash (computed)
- cashDifference (closingCash - expectedCash), notes

### 3. Business Rules
- BR-SHF-001: Only one OPEN shift per cashier at a time
- BR-SHF-002: expectedCash = openingCash + sum(CASH sales during shift)
- BR-SHF-003: Shift must be closed before cashier logs out
- BR-SHF-004: Cash difference > ±50,000 VND triggers a flag for manager review
- BR-SHF-005: Voided sales are excluded from expectedCash calculation
