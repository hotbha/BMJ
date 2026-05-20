#!/usr/bin/env python3
"""Generate TC_E2E_CHECKOUT.md - Checkout E2E test cases."""
import os

OUTPUT = "docs/test-cases/TC_E2E_CHECKOUT.md"
TOTAL = 16

content = """# CHECKOUT Module - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-19
> **Module:** CHECKOUT
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 16
> **Linked BR:** BR-030 to BR-033
> **Linked UC:** UC-03, UC-04

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- bmjServer deployed and accessible
- Chargebee test site configured with hosted pages enabled
- Test credit cards from Chargebee test mode available
- Test accounts TA-01 to TA-10 with valid addresses
- Products seeded with both one-time and subscription pricing
- Cart functional and populated with items before each test

---

## Table of Contents

1. [One-Time Checkout (CHK-001 to CHK-008)](#1-one-time-checkout)
2. [Subscription Checkout (CHK-009 to CHK-014)](#2-subscription-checkout)
3. [Edge Cases (CHK-015 to CHK-016)](#3-edge-cases)

---

## 1. One-Time Checkout

"""

test_cases = [
    (
        "CHK-001",
        "P1-High", "S1-Major", "BR-030, BR-031", "UC-03",
        "Successful one-time checkout — full flow",
        [
            "User logged in (TA-01)",
            "Cart has 2 one-time items",
            "Chargebee test card available: 4242424242424242"
        ],
        [
            "Navigate to Cart screen",
            "Tap 'Proceed to Checkout'",
            "Mobile calls POST /api/v1/checkout/initiate with cart items",
            "bmjServer returns checkout_session_id + hosted_page_url",
            "Mobile opens Payment WebView with the URL",
            "On Chargebee hosted page, enter test card 4242 4242 4242 4242, future expiry, any CVV",
            "Complete payment on Chargebee page",
            "Chargebee redirects to redirect_url with ?id=hp_xxx&state=succeeded",
            "Mobile calls POST /api/v1/checkout/complete { checkout_session_id, hosted_page_id }",
            "Mobile calls GET /api/v1/orders/{order_id} to refetch confirmed state",
        ],
        [
            "POST /api/v1/checkout/initiate returns 200 with hosted_page_url and checkout_session_id",
            "Payment WebView loads Chargebee hosted page successfully",
            "Test card payment succeeds (sandbox)",
            "Return URL intercepted and checkout complete called",
            "Order created with status='pending' or 'confirmed'",
            "Cart cleared after successful checkout",
            "Mobile refetches order state — confirms status",
            "Navigated to Order Confirmation screen",
            "No optimistic UI — all state from bmjServer"
        ],
        "TA-01, cart with 2 items, card: 4242424242424242"
    ),
    (
        "CHK-002",
        "P1-High", "S1-Major", "BR-032", "UC-03",
        "Checkout complete endpoint returns order with correct details",
        [
            "User logged in (TA-02)",
            "Cart has 1 one-time item"
        ],
        [
            "Complete checkout per CHK-001",
            "Capture response from POST /api/v1/checkout/complete",
            "Verify order details match cart items",
        ],
        [
            "Order ID returned",
            "Order status: 'pending' or 'confirmed'",
            "Order items match cart items (name, quantity, price)",
            "Subtotal, tax, delivery_fee, grand_total match cart pricing",
            "Shipping address matches user's saved address",
            "payment_status: 'paid' or 'not_paid' initially"
        ],
        "TA-02, cart with 1 item, chargebee_order_id + chargebee_invoice_id returned"
    ),
    (
        "CHK-003",
        "P1-High", "S1-Major", "BR-030, BR-031", "UC-03",
        "Checkout initiation fails with empty cart",
        [
            "User logged in (TA-03)",
            "Cart is empty"
        ],
        [
            "Navigate to Cart screen (empty state)",
            "Check if 'Proceed to Checkout' button exists",
            "If button exists, tap it",
        ],
        [
            "Proceed to Checkout button should be disabled or hidden when cart is empty",
            "If enabled and tapped → error: 'Cart is empty' or 400 Bad Request",
            "No hosted page created"
        ],
        "Empty cart, TA-03"
    ),
    (
        "CHK-004",
        "P1-High", "S1-Major", "BR-030", "UC-03",
        "User cancels payment on Chargebee hosted page",
        [
            "User logged in (TA-04)",
            "Cart has items"
        ],
        [
            "Initiate checkout → hosted page opens in WebView",
            "On hosted page, click back/browser back/Cancel button",
            "Observe redirect URL or WebView close",
        ],
        [
            "Chargebee returns to redirect_url with state=cancelled or user closes WebView",
            "Cart NOT cleared (items still present)",
            "No order created",
            "User returns to Cart screen",
            "User can retry checkout"
        ],
        "TA-04, cart with items, cancellation on hosted page"
    ),
    (
        "CHK-005",
        "P1-High", "S1-Major", "BR-030, NFR-004", "UC-03",
        "Hosted page loaded over HTTPS",
        [
            "User logged in (TA-05)",
            "Cart has items"
        ],
        [
            "Initiate checkout",
            "Inspect hosted_page_url before opening in WebView",
        ],
        [
            "hosted_page_url starts with https://",
            "URL domain is *.chargebee.com or custom Chargebee domain",
            "SSL certificate valid"
        ],
        "hosted_page_url from initiate response"
    ),
    (
        "CHK-006",
        "P2-Medium", "S2-Minor", "BR-031, NFR-001", "UC-03",
        "Checkout initiate response time < 2 seconds",
        [
            "User logged in (TA-06)",
            "Cart has items"
        ],
        [
            "Start timer",
            "Call POST /api/v1/checkout/initiate",
            "Stop timer when response received",
        ],
        [
            "Response received within 2 seconds (excluding external Chargebee latency)",
            "Note: Chargeebe API call may add latency; acceptable up to 5 seconds"
        ],
        "Timer measurement"
    ),
    (
        "CHK-007",
        "P1-High", "S1-Major", "BR-030", "UC-03",
        "Checkout complete — payment failed scenario",
        [
            "User logged in (TA-07)",
            "Cart has items",
            "Test declined card: 4000000000000002"
        ],
        [
            "Initiate checkout",
            "On hosted page, enter declined card: 4000 0000 0000 0002",
            "Complete payment",
            "Observe result",
        ],
        [
            "Chargebee hosted page shows payment failure message",
            "Cart NOT cleared",
            "No order created (or order with payment_status='failed')",
            "User can retry with different card"
        ],
        "TA-07, declined card: 4000000000000002"
    ),
    (
        "CHK-008",
        "P1-High", "S1-Major", "BR-032", "UC-03",
        "Refetch confirms order state after checkout (no optimistic UI)",
        [
            "User logged in (TA-08)",
            "Cart has items"
        ],
        [
            "Complete successful checkout per CHK-001",
            "Do NOT trust the initial response from checkout/complete",
            "Call GET /api/v1/orders/{order_id} to refetch",
        ],
        [
            "Refetched order state matches (or is more recent than) checkout complete response",
            "Status, payment_status, items all confirmed from MySQL (synced via webhook)",
            "No discrepancy between checkout complete response and refetched data"
        ],
        "TA-08, successful payment, refetch comparison"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(test_cases, 1):
    content += f"""### TC-E2E-CHK-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
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

# Section 2: Subscription Checkout
content += """## 2. Subscription Checkout

"""

sub_cases = [
    (
        "CHK-009",
        "P1-High", "S1-Major", "BR-030, BR-031, BR-045", "UC-04",
        "Successful subscription checkout — full flow",
        [
            "User logged in (TA-01)",
            "Cart has subscription item (e.g. plan_delight_200_weekly)",
            "User has delivery address saved",
            "Test card: 4242424242424242"
        ],
        [
            "Navigate to Cart screen → see subscription item",
            "Tap 'Proceed to Checkout'",
            "Complete checkout per CHK-001 flow",
            "After checkout complete, capture response",
        ],
        [
            "Initiate returns hosted_page_url and checkout_session_id",
            "Payment succeeds on Chargebee hosted page",
            "Checkout complete returns: order_id, subscription_id, status='active'",
            "Both order AND subscription created",
            "Cart cleared after checkout"
        ],
        "TA-01, subscription cart, card: 4242424242424242"
    ),
    (
        "CHK-010",
        "P1-High", "S1-Major", "BR-031, BR-045", "UC-04",
        "Subscription checkout — order confirmation shows subscription info",
        [
            "User logged in (TA-02)",
            "Subscription checkout completed"
        ],
        [
            "After subscription checkout, navigate to Order Confirmation screen",
            "Observe subscription information section",
        ],
        [
            "Order Confirmation shows: 'Your subscription is active'",
            "Subscription ID displayed",
            "Next delivery date shown",
            "Plan name, frequency, billing amount visible"
        ],
        "TA-02, subscription_order data"
    ),
    (
        "CHK-011",
        "P1-High", "S1-Major", "BR-031, BR-045", "UC-04",
        "Subscription appears in subscriptions list after checkout",
        [
            "User logged in (TA-03)",
            "Subscription checkout completed for TA-03"
        ],
        [
            "After successful subscription purchase",
            "Navigate to Subscriptions screen",
            "Verify new subscription appears in list",
        ],
        [
            "New subscription visible in the list",
            "Status = 'active' (or 'in_trial')",
            "Plan name matches purchased plan",
            "Billing info correct"
        ],
        "TA-03, new subscription via checkout"
    ),
    (
        "CHK-012",
        "P2-Medium", "S2-Minor", "BR-031, BR-045", "UC-04",
        "Delivery schedule sent to server during subscription checkout",
        [
            "User logged in (TA-04)",
            "Cart has subscription item"
        ],
        [
            "During subscription purchase, navigate to delivery schedule screen",
            "Select specific days (e.g. Mon, Wed, Fri)",
            "Tap 'Same juice everyday' checkbox → verify behavior",
            "Complete checkout",
        ],
        [
            "Day-wise schedule JSON sent to bmjServer during initiate",
            "Schedule stored as metadata in Chargebee subscription",
            "After subscription created, verify delivery schedule visible in subscription details"
        ],
        "TA-04, subscription with day-wise schedule: Mon/Wed/Fri selected"
    ),
    (
        "CHK-013",
        "P2-Medium", "S2-Minor", "BR-032", "UC-04",
        "Refetch subscription state after subscription checkout",
        [
            "User logged in (TA-05)",
            "Subscription checkout completed"
        ],
        [
            "After checkout complete, call GET /api/v1/subscriptions/{subscription_id}",
            "Verify subscription state",
        ],
        [
            "Refetched subscription status matches expected 'active'",
            "Plan details, billing info, schedule all correct",
            "No optimistic UI — state confirmed from MySQL synced via Chargebee webhook"
        ],
        "TA-05, subscription ID from checkout"
    ),
    (
        "CHK-014",
        "P1-High", "S1-Major", "BR-030, BR-033", "UC-04",
        "Chargebee webhook creates subscription record in MySQL",
        [
            "User logged in (TA-06)",
            "Subscription checkout completed"
        ],
        [
            "Complete subscription purchase",
            "Wait for Chargebee webhook to be processed (up to 10 seconds)",
            "Query database or check subscription via API",
        ],
        [
            "Webhook received and processed by bmjServer",
            "Subscription record created in MySQL",
            "webhook_events table has subscription_created event",
            "No duplicate processing (idempotent)"
        ],
        "TA-06, subscription checkout, webhook verification"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(sub_cases, 9):
    content += f"""### TC-E2E-CHK-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
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

# Section 3: Edge Cases
content += """## 3. Edge Cases

"""

edge_cases = [
    (
        "CHK-015",
        "P2-Medium", "S2-Minor", "BR-032", "UC-03",
        "Network error during checkout — retry recovers gracefully",
        [
            "User logged in (TA-09)",
            "Cart has items",
            "Ability to toggle airplane mode"
        ],
        [
            "Initiate checkout successfully → get hosted_page_url",
            "Toggle airplane mode ON",
            "Complete payment on hosted page (or simulate)",
            "Call POST /api/v1/checkout/complete → network error",
            "Toggle airplane mode OFF",
            "Retry checkout complete with same session_id",
        ],
        [
            "First complete call fails with network error",
            "Cart NOT cleared (no optimistic UI)",
            "Retry succeeds → order created",
            "Checkout session still valid (idempotent)",
            "No duplicate order created"
        ],
        "TA-09, network interruption during checkout complete"
    ),
    (
        "CHK-016",
        "P2-Medium", "S2-Minor", "BR-031", "UC-03",
        "Checkout session status polling returns correct state",
        [
            "User logged in (TA-10)",
            "Checkout initiated and in progress"
        ],
        [
            "Initiate checkout → get checkout_session_id",
            "Poll GET /api/v1/checkout/status/{checkout_session_id} before payment",
            "Complete payment on hosted page",
            "Poll status again after payment",
        ],
        [
            "Before payment: status = 'pending' or 'in_progress'",
            "After payment: status = 'completed' or 'succeeded'",
            "Session ID remains valid until order created"
        ],
        "TA-10, checkout session polling"
    ),
]

for idx, (tid, pri, sev, br, uc, title, preconds, steps, expected, test_data) in enumerate(edge_cases, 15):
    content += f"""### TC-E2E-CHK-{tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
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
