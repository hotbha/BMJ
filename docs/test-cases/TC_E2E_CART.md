# CART Module - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-19
> **Module:** CART
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 16
> **Linked BR:** BR-004, BR-005, BR-020 to BR-024
> **Linked UC:** UC-01, UC-02

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- bmjServer deployed and accessible
- Test accounts TA-01 to TA-10 created and accessible
- Products seeded with both one-time and subscription pricing
- Guest cart_id mechanism verified (SharedPreferences + server with user_id=NULL)

---

## Table of Contents

1. [Add Items to Cart (CART-001 to CART-005)](#1-add-items-to-cart)
2. [Cart Single-Mode Enforcement (CART-006 to CART-008)](#2-cart-single-mode-enforcement)
3. [Cart Item Management (CART-009 to CART-012)](#3-cart-item-management)
4. [Cart Merge (CART-013 to CART-015)](#4-cart-merge)
5. [Edge Cases (CART-016)](#5-edge-cases)

---

## 1. Add Items to Cart

### TC-E2E-CART-CART-001: Add one-time item to cart as authenticated user

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004, BR-020 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart is empty

**Test Steps:**
1. Navigate to product detail
2. Tap 'Add to Cart' for a one-time juice
3. Observe cart icon/badge update
4. Navigate to Cart screen

**Expected Results:**
1. Item added with quantity 1
2. Cart type = 'onetime'
3. Cart badge shows count = 1
4. Cart screen shows: item name, quantity, unit price, subtotal, tax, grand_total (delivery fee sourced from Chargebee)
5. Pricing: subtotal = quantity × unit_price (from bmjServer, not calculated locally)
6. No subscription options visible in cart

**Test Data:**
- One-time juice product, e.g. charge_abc_200

---

### TC-E2E-CART-CART-002: Add subscription item to cart as authenticated user

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004, BR-020 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-02)
- [ ] Cart is empty

**Test Steps:**
1. Navigate to product detail
2. Select subscription plan (e.g. weekly)
3. Tap 'Subscribe' or 'Add to Cart'
4. Navigate to Cart screen

**Expected Results:**
1. Subscription item added with billing frequency shown
2. Cart type = 'subscription'
3. Cart shows: plan name, frequency, price per period
4. No one-time items visible in cart

**Test Data:**
- Subscription plan, e.g. plan_delight_200_weekly

---

### TC-E2E-CART-CART-003: Add multiple items to cart (same type)

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-03)
- [ ] Cart is empty or has same-type items

**Test Steps:**
1. Add one-time item A to cart (quantity 1)
2. Add one-time item B to cart (quantity 1)
3. Navigate to Cart screen

**Expected Results:**
1. Both items visible in cart
2. Cart type remains 'onetime'
3. Subtotal = sum of all item totals
4. Tax and grand_total recalculated by server

**Test Data:**
- Two different one-time juice products

---

### TC-E2E-CART-CART-004: Guest adds item to cart — persisted with cart_id

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004, BR-008 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install / logged out
- [ ] No existing cart_id

**Test Steps:**
1. Browse products as guest
2. Attempt to add item to cart
3. Observe system response (should prompt login per PD-01)

**Expected Results:**
1. Guest cannot add to cart directly (PD-01: Auth First)
2. Login prompt displayed
3. If user logs in immediately after, guest cart_id should be generated for merge

**Test Data:**
- N/A (guest cart flow per PD-01)

---

### TC-E2E-CART-CART-005: Pricing breakdown displayed correctly in cart

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004, BR-021 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-04)
- [ ] Cart has 2 one-time items (different prices)

**Test Steps:**
1. Navigate to Cart screen
2. Observe pricing section
3. Verify subtotal, tax, grand_total against API response

**Expected Results:**
1. Subtotal displayed correctly (sum of item totals from server)
2. Tax displayed (sourced from Chargebee, passthrough via bmjServer)
3. Delivery fee not displayed as separate line item — sourced from Chargebee pricing data (BR-023)
4. Grand total = subtotal + tax - discount (from server; delivery fee included in Chargebee pricing)
5. Mobile app does NOT calculate any of these values — display only

**Test Data:**
- Cart with 2 one-time items of different prices

---

## 2. Cart Single-Mode Enforcement

### TC-E2E-CART-CART-006: Cannot mix one-time and subscription items — receive 409

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-020 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-05)
- [ ] Cart has one-time item (cart_type='onetime')

**Test Steps:
1. Navigate to a subscription plan
2. Tap 'Subscribe' or 'Add to Cart'
3. Observe error response
**Expected Results:
1. System returns 409 Conflict (or equivalent)
2. Dialog/message: 'Your cart has one-time items. Would you like to switch to subscription?'
3. User given option to clear cart and switch type, or cancel
**Test Data:**
- Cart with one-time item + attempt to add subscription plan

---

### TC-E2E-CART-CART-007: Switch cart type from one-time to subscription (user confirms)

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-020 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has one-time item

**Test Steps:
1. Attempt to add subscription item → see 409 conflict
2. Tap 'Switch to Subscription' / 'Clear & Add'
3. Navigate to Cart screen
**Expected Results:
1. Previous one-time items cleared
2. Subscription item added to cart
3. Cart type = 'subscription'
4. Only subscription item visible in cart
**Test Data:**
- One-time cart → confirm switch → subscription

---

### TC-E2E-CART-CART-008: Cancel switch — cart preserves original items

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-020 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has one-time items

**Test Steps:
1. Attempt to add subscription item → see conflict
2. Tap 'Cancel' / 'Keep Current Cart'
3. Navigate to Cart screen
**Expected Results:
1. Original one-time items preserved unchanged
2. Cart type remains 'onetime'
3. Subscription item NOT added
**Test Data:**
- One-time cart → cancel switch → original items intact

---

## 3. Cart Item Management

### TC-E2E-CART-CART-009: Update item quantity in cart

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-06)
- [ ] Cart has one-time item with quantity 1

**Test Steps:
1. On Cart screen, tap '+' to increase quantity to 3
2. Observe pricing update
3. Tap '-' to decrease quantity back to 1
**Expected Results:
1. Quantity updated to 3 → subtotal triples (server returns updated pricing)
2. Loading indicator shown briefly during update
3. Quantity cannot go below 1 (min quantity = 1)
4. Max quantity = 99 (server-enforced)
**Test Data:**
- Cart item with initial qty=1

---

### TC-E2E-CART-CART-010: Remove single item from cart

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has 2 items

**Test Steps:
1. On Cart screen, tap delete/remove icon on one item
2. Confirm removal (if confirmation dialog shown)
3. Observe cart
**Expected Results:
1. Item removed from cart
2. Remaining items still present
3. Cart type preserved if remaining items exist
4. Pricing recalculated for remaining items
**Test Data:**
- Cart with 2 one-time items

---

### TC-E2E-CART-CART-011: Remove last item — cart becomes empty

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has 1 item

**Test Steps:
1. Remove the only item from cart
2. Observe cart screen
**Expected Results:
1. Cart screen shows empty state: 'Your cart is empty'
2. No items in cart
3. User can browse products to add more
**Test Data:**
- Cart with 1 item → remove → empty

---

### TC-E2E-CART-CART-012: Clear entire cart

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has multiple items

**Test Steps:
1. On Cart screen, tap 'Clear Cart' / delete all button
2. Confirm action
3. Observe cart
**Expected Results:
1. All items removed
2. Cart is empty
3. Empty state displayed
**Test Data:**
- Cart with 3 items

---

## 4. Cart Merge

### TC-E2E-CART-CART-013: Guest cart merges into authenticated cart — same type (auto-merge)

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-005 |
| **Linked UC** | UC-02 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest has one-time items in cart (cart_id stored)
- [ ] Authenticated user already has one-time items in server cart
- [ ] Both carts have same cart_type='onetime'

**Test Steps:
1. User logs in with TA-01 credentials
2. Mobile calls POST /api/v1/cart/merge with guest_cart_id
3. Observe cart after merge
**Expected Results:
1. Items from both carts merged
2. Duplicate items take higher quantity
3. No conflict dialog (same types)
4. Final cart has all items from both carts
**Test Data:**
- Guest cart: item A (qty=1), Auth cart: item A (qty=2), item B (qty=1)

---

### TC-E2E-CART-CART-014: Guest cart merge — different types → user chooses which to keep

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-005 |
| **Linked UC** | UC-02 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest has one-time items (cart_type='onetime')
- [ ] Authenticated user has subscription items (cart_type='subscription')

**Test Steps:
1. User logs in with TA-02 credentials
2. Mobile calls POST /api/v1/cart/merge with guest_cart_id
3. Observe 409 Conflict response with both cart types
4. Dialog: 'Which cart would you like to keep?' shown
5. Select 'Guest Cart' (one-time)
6. Mobile calls merge again with { keep: 'guest' }
**Expected Results:
1. 409 Conflict returned with guest + user cart types
2. Dialog shows both cart types for user to choose
3. After selecting guest → guest cart items kept, auth cart deleted
4. Discarded cart permanently deleted from server
**Test Data:**
- Guest: one-time items, Auth: subscription items

---

### TC-E2E-CART-CART-015: Guest cart merge — no existing auth cart → simple reassignment

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-005 |
| **Linked UC** | UC-02 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest has one-time items in cart (cart_id stored)
- [ ] User has NO existing server cart (fresh login)

**Test Steps:
1. Login with TA-03 credentials (never added items)
2. Mobile calls POST /api/v1/cart/merge
3. Observe cart
**Expected Results:
1. Guest cart reassigned to authenticated user
2. All guest items preserved exactly
3. Cart is now linked to user_id
**Test Data:**
- Guest cart with 2 items, no auth cart

---

## 5. Edge Cases

### TC-E2E-CART-CART-016: Network error during cart operations — retry works

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-020, BR-021 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Ability to toggle airplane mode

**Test Steps:
1. Toggle airplane mode ON
2. Try to add item to cart
3. Observe error
4. Toggle airplane mode OFF
5. Retry the operation
**Expected Results:
1. Error message: 'Network error. Please try again.' shown
2. Item NOT added to cart (no optimistic UI)
3. After restoring network, retry succeeds → item added
**Test Data:**
- N/A (network error test)

---

