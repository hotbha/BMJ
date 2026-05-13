# CART Module — Detailed Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-11

---

## TC-CART-001: Get cart for existing user

| Field | Value |
|-------|-------|
| **ID** | TC-CART-001 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock CartRepo |
| **Steps** | cartService.getCart(user) |
| **Expected** | Cart with ID 100 |
| **Auto** | ✅ Automated |

## TC-CART-002: Get cart creates empty cart for new user

| Field | Value |
|-------|-------|
| **ID** | TC-CART-002 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock CartRepo returns empty |
| **Steps** | cartService.getCart(user) |
| **Expected** | New cart with ID 200 |
| **Auto** | ✅ Automated |

## TC-CART-003: Add item with null priceId

| Field | Value |
|-------|-------|
| **ID** | TC-CART-003 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock CartRepo |
| **Steps** | cartService.addItem(user, null, 1) |
| **Expected** | RuntimeException |
| **Auto** | ✅ Automated |

## TC-CART-004: Add item invalid format

| Field | Value |
|-------|-------|
| **ID** | TC-CART-004 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock CartRepo |
| **Steps** | cartService.addItem(user, "invalid", 1) |
| **Expected** | IllegalArgumentException |
| **Auto** | ✅ Automated |

## TC-CART-005: Cart response structure

| Field | Value |
|-------|-------|
| **ID** | TC-CART-005 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock CartRepo |
| **Steps** | cartService.getCart(user) |
| **Expected** | All required fields present |
| **Auto** | ✅ Automated |

## TC-CART-006: Clear cart (existing cart) (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CART-006 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock CartRepo, cart exists |
| **Steps** | cartService.clearCart(user) |
| **Expected** | Success response |
| **Auto** | ✅ Automated |

## TC-CART-007: Clear cart (no cart) (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CART-007 |
| **Module** | CART |
| **Type** | Unit |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Preconditions** | Mock CartRepo returns empty |
| **Steps** | cartService.clearCart(user) |
| **Expected** | Already empty message |
| **Auto** | ✅ Automated |

## Total: 7 test cases (5 existing + 2 new)
