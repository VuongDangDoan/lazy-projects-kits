# Ecommerce Domain Knowledge Template
> [TEMPLATE — split into per-module L1-domain files during /quickstart]
> Each "## Module:" section becomes knowledge/L1-domain/[slug]-domain.md

---

## Module: product
> Slug: product | Status: Planned (from template)

### 1. Overview
Quản lý danh mục sản phẩm, biến thể và tồn kho.

### 2. Entities

**Product**
- id, slug (unique, SEO-friendly), name, description (rich text)
- categoryId (FK), tags (string[])
- basePrice (Decimal 12,2), compareAtPrice (nullable — for "sale" display)
- status: DRAFT | ACTIVE | ARCHIVED
- imageUrls (string[]), thumbnailUrl
- isFeatured, sortOrder
- createdAt, updatedAt, deletedAt

**ProductVariant** (for size/color options)
- id, productId (FK), sku (unique), name (e.g. "Red / XL")
- attributes (JSON: {color: "Red", size: "XL"})
- price (nullable — overrides product.basePrice if set)
- stock (int, default: 0), lowStockThreshold

**Category**
- id, name, slug (unique), parentId (nullable), imageUrl, sortOrder

### 3. Business Rules
- BR-PRD-001: slug auto-generated from name (lowercase, hyphens) + unique suffix if collision
- BR-PRD-002: DRAFT products not visible to customers (admin/seller only)
- BR-PRD-003: ARCHIVED products not visible to customers; historical orders reference them
- BR-PRD-004: If variants exist, stock tracked per variant — not on product level
- BR-PRD-005: compareAtPrice must be > price (to prevent fake discounts)
- BR-PRD-006: At least one image required before product can be set ACTIVE

### 4. RBAC
| Action | admin | seller | customer | support |
|---|---|---|---|---|
| View active products | ✅ | ✅ | ✅ | ✅ |
| View draft/archived | ✅ | ✅ | ❌ | ❌ |
| Create/edit product | ✅ | ✅ | ❌ | ❌ |
| Archive product | ✅ | ❌ | ❌ | ❌ |

---

## Module: order
> Slug: order | Status: Planned (from template)

### 1. Overview
Quản lý đơn hàng từ lúc đặt đến khi giao thành công.

### 2. Entities

**Order**
- id, code (unique, auto: ORD-YYYYMMDD-NNNN)
- customerId (FK → User, nullable for guest checkout in v2)
- status: PENDING | CONFIRMED | PROCESSING | SHIPPED | DELIVERED | CANCELLED | REFUNDED
- shippingAddress (JSON: {name, phone, address, city, province})
- paymentMethod: COD | BANK_TRANSFER
- paymentStatus: UNPAID | PAID | REFUNDED
- subtotal, shippingFee, discountAmount, totalAmount
- notes (customer note), adminNote
- shippedAt, deliveredAt, cancelledAt, cancelReason
- createdAt

**OrderItem**
- id, orderId (FK), productId (FK), variantId (nullable FK)
- productName (snapshot), variantName (snapshot), sku (snapshot)
- unitPrice (snapshot), quantity, subtotal

**OrderStatusHistory**
- id, orderId (FK), fromStatus, toStatus, note, changedById (FK → User), createdAt

### 3. Business Rules
- BR-ORD-001: OrderItem fields are snapshots — never mutate after order creation
- BR-ORD-002: Stock decremented atomically when order moves PENDING → CONFIRMED (use transaction)
- BR-ORD-003: Cancellation allowed: PENDING by customer; PENDING or CONFIRMED by admin/seller
- BR-ORD-004: Stock restored when order CANCELLED (if it was CONFIRMED or beyond)
- BR-ORD-005: Customer can only view their own orders; admin/seller/support can view all
- BR-ORD-006: Every status change logged in OrderStatusHistory
- BR-ORD-007: COD orders: paymentStatus → PAID when status → DELIVERED

### 4. RBAC
| Action | admin | seller | customer | support |
|---|---|---|---|---|
| Place order | ✅ | ✅ | ✅ | ❌ |
| View order | ✅ | ✅ | Own only | ✅ |
| Update status | ✅ | ✅ | ❌ | Support states only |
| Cancel order | ✅ | ✅ | Own PENDING | ❌ |
| Process refund | ✅ | ❌ | ❌ | ❌ |

### 5. State machine

```
PENDING → CONFIRMED (seller confirms stock available)
        → CANCELLED (customer or admin cancels)

CONFIRMED → PROCESSING (seller is packing)
          → CANCELLED (admin only)

PROCESSING → SHIPPED (tracking number added)

SHIPPED → DELIVERED (confirmed receipt)
        → CANCELLED (returned to sender — admin only)

DELIVERED → REFUNDED (admin-initiated refund)

CANCELLED → [terminal]
REFUNDED  → [terminal]
```

---

## Module: customer
> Slug: customer | Status: Planned (from template)

### 1. Overview
Tài khoản khách hàng và lịch sử mua hàng.

### 2. Entities

**User** (shared with auth module)
- id, email (unique), passwordHash, name, phone
- role: ADMIN | SELLER | CUSTOMER | SUPPORT
- isVerified, verificationToken, createdAt

**CustomerProfile** (extends User for CUSTOMER role)
- userId (FK, PK), defaultAddressId (nullable FK → Address)
- totalOrders, totalSpent (denormalized for display)

**Address**
- id, userId (FK), label (e.g. "Nhà riêng", "Công ty")
- recipientName, phone, addressLine, ward, district, city, province
- isDefault

### 3. Business Rules
- BR-CST-001: Customer can have multiple saved addresses; one marked as default
- BR-CST-002: Customer can only view and edit their own profile and addresses
- BR-CST-003: Email must be unique across all users (all roles)
- BR-CST-004: Soft-delete only — never hard-delete a customer with order history

### 4. RBAC
| Action | admin | seller | customer | support |
|---|---|---|---|---|
| View customer list | ✅ | ✅ | ❌ | ✅ |
| View customer detail | ✅ | ✅ | Self only | ✅ |
| Edit customer | ✅ | ❌ | Self only | ❌ |
| Delete customer | ✅ | ❌ | ❌ | ❌ |
