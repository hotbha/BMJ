#!/usr/bin/env python3
"""Generate TC_E2E_CART.md - Cart E2E test cases."""
import os

OUTPUT = "docs/test-cases/TC_E2E_CART.md"
TOTAL = 16

content = """# CART Module - End-to-End (E2E) Black-Box Test Cases

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

"""

test_cases = [
    (
        "CART-001",
        "P1-High", "S1-Major", "BR-004, BR-020", "UC-01",
        "Add one-time item to cart as authenticated user",
        [
            "User logged in (TA-01)",
            "Cart is empty"
        ],
        [
            "Navigate to product detail",
            "Tap 'Add to Cart' for a one-time juice",
            "Observe cart icon/badge update",
            "Navigate to Cart screen",
        ],
        [
            "Item added with quantity 1",
            "Cart type = 'onetime'",
            "Cart badge shows count = 1",
            "Cart screen shows: item name, quantity, unit price, subtotal, tax, delivery_fee=0, grand_total",
            "Pricing: subtotal = quantity × unit_price (from bmjServer, not calculated locally)",
            "No subscription options visible in cart"
        ],
        "One-time juice product, e.g. charge_abc_200"
    ),
    (
        "CART-002",
        "P1-High", "S1-Major", "BR-004, BR-020", "UC-01",
        "Add subscription item to cart as authenticated user",
        [
            "User logged in (TA-02)",
            "Cart is empty"
        ],
        [
            "Navigate to product detail",
            "Select subscription plan (e.g. weekly)",
            "Tap 'Subscribe' or 'Add to Cart'",
            "Navigate to Cart screen",
        ],
        [
            "Subscription item added with billing frequency shown",
            "Cart type = 'subscription'",
            "Cart shows: plan name, frequency, price per period",
            "No one-time items visible in cart"
        ],
        "Subscription plan, e.g. plan_delight_200_weekly"
    ),
    (
        "CART-003",
        "P2-Medium", "S2-Minor", "BR-004", "UC-01",
        "Add multiple items to cart (same type)",
        [
            "User logged in (TA-03)",
            "Cart is empty or has same-type items"
        ],
        [
            "Add one-time item A to cart (quantity 1)",
            "Add one-time item B to cart (quantity 1)",
            "Navigate to Cart screen",
        ],
        [
            "Both items visible in cart",
            "Cart type remains 'onetime'",
            "Subtotal = sum of all item totals",
            "Tax and grand_total recalculated by server"
        ],
        "Two different one-time juice products"
    ),
    (
        "CART-004",
        "P1-High", "S1-Major", "BR-004, BR-008", "UC-01",
        "Guest adds item to cart — persisted with cart_id",
        [
            "Fresh install / logged out",
            "No existing cart_id"
        ],
        [
            "Browse products as guest",
            "Attempt to add item to cart",
            "Observe system response (should prompt login per PD-01)"
        ],
        [
            "Guest cannot add to cart directly (PD-01: Auth First)",
            "Login prompt displayed",
            "If user logs in immediately after, guest cart_id should be generated for merge"
        ],
        "N/A (guest cart flow per PD-01)"
    ),
    (
        "CART-005",
        "P1-High", "S1-Major", "BR-004, BR-021", "UC-01",
        "Pricing breakdown displayed correctly in cart",
        [
            "User logged in (TA-04)",
            "Cart has 2 one-time items (different prices)"
        ],
        [
            "Navigate to Cart screen",
            "Observe pricing section",
            "Verify subtotal, tax, delivery_fee, grand_total against API response",
        ],
        [
            "Subtotal displayed correctly (sum of item totals from server)",
            "Tax displayed (sourced from Chargebee, passthrough via bmjServer)",
            "Delivery fee = ₹0 (MVP, BR-023)",
            "Grand total = subtotal + tax + delivery_fee - discount (from server)",
            "Mobile app does NOT calculate any of these values — display only"
        ],
        "Cart with 2 one-time items of different prices"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(test_cases, 1):
    content += f"""### TC-E2E-CART-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | {pri} |
| **Severity** | {sev} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | ❌ Manual |

**Preconditions:**
"""
    for p in preconds:
        content += f"- [ ] {p}\n"
    content += f"""
**Test Steps:**
"""
    for i, s in enumerate(steps, 1):
        content += f"{i}. {s}\n"
    content += f"""
**Expected Results:**
"""
    for i, e in enumerate(expected, 1):
        content += f"{i}. {e}\n"
    content += f"""
**Test Data:**
- {test_data}

---

"""

# Section 2: Cart Single-Mode Enforcement
content += """## 2. Cart Single-Mode Enforcement

"""

single_mode_cases = [
    (
        "CART-006",
        "P1-High", "S1-Major", "BR-020", "UC-01",
        "Cannot mix one-time and subscription items — receive 409",
        [
            "User logged in (TA-05)",
            "Cart has one-time item (cart_type='onetime')"
        ],
        [
            "Navigate to a subscription plan",
            "Tap 'Subscribe' or 'Add to Cart'",
            "Observe error response",
        ],
        [
            "System returns 409 Conflict (or equivalent)",
            "Dialog/message: 'Your cart has one-time items. Would you like to switch to subscription?'",
            "User given option to clear cart and switch type, or cancel"
        ],
        "Cart with one-time item + attempt to add subscription plan"
    ),
    (
        "CART-007",
        "P1-High", "S1-Major", "BR-020", "UC-01",
        "Switch cart type from one-time to subscription (user confirms)",
        [
            "User logged in (TA-01)",
            "Cart has one-time item"
        ],
        [
            "Attempt to add subscription item → see 409 conflict",
            "Tap 'Switch to Subscription' / 'Clear & Add'",
            "Navigate to Cart screen",
        ],
        [
            "Previous one-time items cleared",
            "Subscription item added to cart",
            "Cart type = 'subscription'",
            "Only subscription item visible in cart"
        ],
        "One-time cart → confirm switch → subscription"
    ),
    (
        "CART-008",
        "P2-Medium", "S2-Minor", "BR-020", "UC-01",
        "Cancel switch — cart preserves original items",
        [
            "User logged in (TA-01)",
            "Cart has one-time items"
        ],
        [
            "Attempt to add subscription item → see conflict",
            "Tap 'Cancel' / 'Keep Current Cart'",
            "Navigate to Cart screen",
        ],
        [
            "Original one-time items preserved unchanged",
            "Cart type remains 'onetime'",
            "Subscription item NOT added"
        ],
        "One-time cart → cancel switch → original items intact"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(single_mode_cases, 6):
    content += f"""### TC-E2E-CART-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | {pri} |
| **Severity** | {sev} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | ❌ Manual |

**Preconditions:**
"""
    for p in preconds:
        content += f"- [ ] {p}\n"
    content += f"""
**Test Steps:"""
    for i, s in enumerate(steps, 1):
        content += f"""
{i}. {s}"""
    content += f"""
**Expected Results:"""
    for i, e in enumerate(expected, 1):
        content += f"""
{i}. {e}"""
    content += f"""
**Test Data:**
- {test_data}

---

"""

# Section 3: Cart Item Management
content += """## 3. Cart Item Management

"""

item_mgmt_cases = [
    (
        "CART-009",
        "P1-High", "S1-Major", "BR-004", "UC-01",
        "Update item quantity in cart",
        [
            "User logged in (TA-06)",
            "Cart has one-time item with quantity 1"
        ],
        [
            "On Cart screen, tap '+' to increase quantity to 3",
            "Observe pricing update",
            "Tap '-' to decrease quantity back to 1",
        ],
        [
            "Quantity updated to 3 → subtotal triples (server returns updated pricing)",
            "Loading indicator shown briefly during update",
            "Quantity cannot go below 1 (min quantity = 1)",
            "Max quantity = 99 (server-enforced)"
        ],
        "Cart item with initial qty=1"
    ),
    (
        "CART-010",
        "P1-High", "S1-Major", "BR-004", "UC-01",
        "Remove single item from cart",
        [
            "User logged in (TA-01)",
            "Cart has 2 items"
        ],
        [
            "On Cart screen, tap delete/remove icon on one item",
            "Confirm removal (if confirmation dialog shown)",
            "Observe cart",
        ],
        [
            "Item removed from cart",
            "Remaining items still present",
            "Cart type preserved if remaining items exist",
            "Pricing recalculated for remaining items"
        ],
        "Cart with 2 one-time items"
    ),
    (
        "CART-011",
        "P1-High", "S1-Major", "BR-004", "UC-01",
        "Remove last item — cart becomes empty",
        [
            "User logged in (TA-01)",
            "Cart has 1 item"
        ],
        [
            "Remove the only item from cart",
            "Observe cart screen",
        ],
        [
            "Cart screen shows empty state: 'Your cart is empty'",
            "No items in cart",
            "User can browse products to add more"
        ],
        "Cart with 1 item → remove → empty"
    ),
    (
        "CART-012",
        "P1-High", "S1-Major", "BR-004", "UC-01",
        "Clear entire cart",
        [
            "User logged in (TA-01)",
            "Cart has multiple items"
        ],
        [
            "On Cart screen, tap 'Clear Cart' / delete all button",
            "Confirm action",
            "Observe cart",
        ],
        [
            "All items removed",
            "Cart is empty",
            "Empty state displayed"
        ],
        "Cart with 3 items"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(item_mgmt_cases, 9):
    content += f"""### TC-E2E-CART-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | {pri} |
| **Severity** | {sev} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | ❌ Manual |

**Preconditions:**
"""
    for p in preconds:
        content += f"- [ ] {p}\n"
    content += f"""
**Test Steps:"""
    for i, s in enumerate(steps, 1):
        content += f"""
{i}. {s}"""
    content += f"""
**Expected Results:"""
    for i, e in enumerate(expected, 1):
        content += f"""
{i}. {e}"""
    content += f"""
**Test Data:**
- {test_data}

---

"""

# Section 4: Cart Merge
content += """## 4. Cart Merge

"""

merge_cases = [
    (
        "CART-013",
        "P1-High", "S1-Major", "BR-005", "UC-02",
        "Guest cart merges into authenticated cart — same type (auto-merge)",
        [
            "Guest has one-time items in cart (cart_id stored)",
            "Authenticated user already has one-time items in server cart",
            "Both carts have same cart_type='onetime'"
        ],
        [
            "User logs in with TA-01 credentials",
            "Mobile calls POST /api/v1/cart/merge with guest_cart_id",
            "Observe cart after merge",
        ],
        [
            "Items from both carts merged",
            "Duplicate items take higher quantity",
            "No conflict dialog (same types)",
            "Final cart has all items from both carts"
        ],
        "Guest cart: item A (qty=1), Auth cart: item A (qty=2), item B (qty=1)"
    ),
    (
        "CART-014",
        "P1-High", "S1-Major", "BR-005", "UC-02",
        "Guest cart merge — different types → user chooses which to keep",
        [
            "Guest has one-time items (cart_type='onetime')",
            "Authenticated user has subscription items (cart_type='subscription')"
        ],
        [
            "User logs in with TA-02 credentials",
            "Mobile calls POST /api/v1/cart/merge with guest_cart_id",
            "Observe 409 Conflict response with both cart types",
            "Dialog: 'Which cart would you like to keep?' shown",
            "Select 'Guest Cart' (one-time)",
            "Mobile calls merge again with { keep: 'guest' }",
        ],
        [
            "409 Conflict returned with guest + user cart types",
            "Dialog shows both cart types for user to choose",
            "After selecting guest → guest cart items kept, auth cart deleted",
            "Discarded cart permanently deleted from server"
        ],
        "Guest: one-time items, Auth: subscription items"
    ),
    (
        "CART-015",
        "P1-High", "S1-Major", "BR-005", "UC-02",
        "Guest cart merge — no existing auth cart → simple reassignment",
        [
            "Guest has one-time items in cart (cart_id stored)",
            "User has NO existing server cart (fresh login)"
        ],
        [
            "Login with TA-03 credentials (never added items)",
            "Mobile calls POST /api/v1/cart/merge",
            "Observe cart",
        ],
        [
            "Guest cart reassigned to authenticated user",
            "All guest items preserved exactly",
            "Cart is now linked to user_id"
        ],
        "Guest cart with 2 items, no auth cart"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(merge_cases, 13):
    content += f"""### TC-E2E-CART-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | {pri} |
| **Severity** | {sev} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | ❌ Manual |

**Preconditions:**
"""
    for p in preconds:
        content += f"- [ ] {p}\n"
    content += f"""
**Test Steps:"""
    for i, s in enumerate(steps, 1):
        content += f"""
{i}. {s}"""
    content += f"""
**Expected Results:"""
    for i, e in enumerate(expected, 1):
        content += f"""
{i}. {e}"""
    content += f"""
**Test Data:**
- {test_data}

---

"""

# Section 5: Edge Cases
content += """## 5. Edge Cases

"""

edge_cases = [
    (
        "CART-016",
        "P2-Medium", "S2-Minor", "BR-020, BR-021", "UC-01",
        "Network error during cart operations — retry works",
        [
            "User logged in (TA-01)",
            "Ability to toggle airplane mode"
        ],
        [
            "Toggle airplane mode ON",
            "Try to add item to cart",
            "Observe error",
            "Toggle airplane mode OFF",
            "Retry the operation",
        ],
        [
            "Error message: 'Network error. Please try again.' shown",
            "Item NOT added to cart (no optimistic UI)",
            "After restoring network, retry succeeds → item added"
        ],
        "N/A (network error test)"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(edge_cases, 16):
    content += f"""### TC-E2E-CART-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CART |
| **Type** | E2E (Black Box) |
| **Priority** | {pri} |
| **Severity** | {sev} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | ❌ Manual |

**Preconditions:**
"""
    for p in preconds:
        content += f"- [ ] {p}\n"
    content += f"""
**Test Steps:"""
    for i, s in enumerate(steps, 1):
        content += f"""
{i}. {s}"""
    content += f"""
**Expected Results:"""
    for i, e in enumerate(expected, 1):
        content += f"""
{i}. {e}"""
    content += f"""
**Test Data:**
- {test_data}

---

"""

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Written {TOTAL} test cases to {OUTPUT}")
print(f"Total file size: {len(content)} characters")
