# CHECKOUT Module - End-to-End (E2E) Black-Box Test Cases

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

### TC-E2E-CHK-CHK-001: Successful one-time checkout — full flow

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-031 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has 2 one-time items
- [ ] Chargebee test card available: 4242424242424242

**Test Steps:
1. Navigate to Cart screen
2. Tap 'Proceed to Checkout'
3. Mobile calls POST /api/v1/checkout/initiate with cart items
4. bmjServer returns checkout_session_id + hosted_page_url
5. Mobile opens Payment WebView with the URL
6. On Chargebee hosted page, enter test card 4242 4242 4242 4242, future expiry, any CVV
7. Complete payment on Chargebee page
8. Chargebee redirects to redirect_url with ?id=hp_xxx&state=succeeded
9. Mobile calls POST /api/v1/checkout/complete { checkout_session_id, hosted_page_id }
10. Mobile calls GET /api/v1/orders/{order_id} to refetch confirmed state
**Expected Results:
1. POST /api/v1/checkout/initiate returns 200 with hosted_page_url and checkout_session_id
2. Payment WebView loads Chargebee hosted page successfully
3. Test card payment succeeds (sandbox)
4. Return URL intercepted and checkout complete called
5. Order created with status='pending' or 'confirmed'
6. Cart cleared after successful checkout
7. Mobile refetches order state — confirms status
8. Navigated to Order Confirmation screen
9. No optimistic UI — all state from bmjServer
**Test Data:**
- TA-01, cart with 2 items, card: 4242424242424242

---

### TC-E2E-CHK-CHK-002: Checkout complete endpoint returns order with correct details

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-032 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-02)
- [ ] Cart has 1 one-time item

**Test Steps:
1. Complete checkout per CHK-001
2. Capture response from POST /api/v1/checkout/complete
3. Verify order details match cart items
**Expected Results:
1. Order ID returned
2. Order status: 'pending' or 'confirmed'
3. Order items match cart items (name, quantity, price)
4. Subtotal, tax, delivery_fee, grand_total match cart pricing
5. Shipping address matches user's saved address
6. payment_status: 'paid' or 'not_paid' initially
**Test Data:**
- TA-02, cart with 1 item, chargebee_order_id + chargebee_invoice_id returned

---

### TC-E2E-CHK-CHK-003: Checkout initiation fails with empty cart

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-031 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-03)
- [ ] Cart is empty

**Test Steps:
1. Navigate to Cart screen (empty state)
2. Check if 'Proceed to Checkout' button exists
3. If button exists, tap it
**Expected Results:
1. Proceed to Checkout button should be disabled or hidden when cart is empty
2. If enabled and tapped → error: 'Cart is empty' or 400 Bad Request
3. No hosted page created
**Test Data:**
- Empty cart, TA-03

---

### TC-E2E-CHK-CHK-004: User cancels payment on Chargebee hosted page

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-04)
- [ ] Cart has items

**Test Steps:
1. Initiate checkout → hosted page opens in WebView
2. On hosted page, click back/browser back/Cancel button
3. Observe redirect URL or WebView close
**Expected Results:
1. Chargebee returns to redirect_url with state=cancelled or user closes WebView
2. Cart NOT cleared (items still present)
3. No order created
4. User returns to Cart screen
5. User can retry checkout
**Test Data:**
- TA-04, cart with items, cancellation on hosted page

---

### TC-E2E-CHK-CHK-005: Hosted page loaded over HTTPS

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, NFR-004 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-05)
- [ ] Cart has items

**Test Steps:
1. Initiate checkout
2. Inspect hosted_page_url before opening in WebView
**Expected Results:
1. hosted_page_url starts with https://
2. URL domain is *.chargebee.com or custom Chargebee domain
3. SSL certificate valid
**Test Data:**
- hosted_page_url from initiate response

---

### TC-E2E-CHK-CHK-006: Checkout initiate response time < 2 seconds

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-031, NFR-001 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-06)
- [ ] Cart has items

**Test Steps:
1. Start timer
2. Call POST /api/v1/checkout/initiate
3. Stop timer when response received
**Expected Results:
1. Response received within 2 seconds (excluding external Chargebee latency)
2. Note: Chargeebe API call may add latency; acceptable up to 5 seconds
**Test Data:**
- Timer measurement

---

### TC-E2E-CHK-CHK-007: Checkout complete — payment failed scenario

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-07)
- [ ] Cart has items
- [ ] Test declined card: 4000000000000002

**Test Steps:
1. Initiate checkout
2. On hosted page, enter declined card: 4000 0000 0000 0002
3. Complete payment
4. Observe result
**Expected Results:
1. Chargebee hosted page shows payment failure message
2. Cart NOT cleared
3. No order created (or order with payment_status='failed')
4. User can retry with different card
**Test Data:**
- TA-07, declined card: 4000000000000002

---

### TC-E2E-CHK-CHK-008: Refetch confirms order state after checkout (no optimistic UI)

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-032 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-08)
- [ ] Cart has items

**Test Steps:
1. Complete successful checkout per CHK-001
2. Do NOT trust the initial response from checkout/complete
3. Call GET /api/v1/orders/{order_id} to refetch
**Expected Results:
1. Refetched order state matches (or is more recent than) checkout complete response
2. Status, payment_status, items all confirmed from MySQL (synced via webhook)
3. No discrepancy between checkout complete response and refetched data
**Test Data:**
- TA-08, successful payment, refetch comparison

---

## 2. Subscription Checkout

### TC-E2E-CHK-CHK-009: Successful subscription checkout — full flow

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-031, BR-045 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has subscription item (e.g. plan_delight_200_weekly)
- [ ] User has delivery address saved
- [ ] Test card: 4242424242424242

**Test Steps:
1. Navigate to Cart screen → see subscription item
2. Tap 'Proceed to Checkout'
3. Complete checkout per CHK-001 flow
4. After checkout complete, capture response
**Expected Results:
1. Initiate returns hosted_page_url and checkout_session_id
2. Payment succeeds on Chargebee hosted page
3. Checkout complete returns: order_id, subscription_id, status='active'
4. Both order AND subscription created
5. Cart cleared after checkout
**Test Data:**
- TA-01, subscription cart, card: 4242424242424242

---

### TC-E2E-CHK-CHK-010: Subscription checkout — order confirmation shows subscription info

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-031, BR-045 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-02)
- [ ] Subscription checkout completed

**Test Steps:
1. After subscription checkout, navigate to Order Confirmation screen
2. Observe subscription information section
**Expected Results:
1. Order Confirmation shows: 'Your subscription is active'
2. Subscription ID displayed
3. Next delivery date shown
4. Plan name, frequency, billing amount visible
**Test Data:**
- TA-02, subscription_order data

---

### TC-E2E-CHK-CHK-011: Subscription appears in subscriptions list after checkout

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-031, BR-045 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-03)
- [ ] Subscription checkout completed for TA-03

**Test Steps:
1. After successful subscription purchase
2. Navigate to Subscriptions screen
3. Verify new subscription appears in list
**Expected Results:
1. New subscription visible in the list
2. Status = 'active' (or 'in_trial')
3. Plan name matches purchased plan
4. Billing info correct
**Test Data:**
- TA-03, new subscription via checkout

---

### TC-E2E-CHK-CHK-012: Delivery schedule sent to server during subscription checkout

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-031, BR-045 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-04)
- [ ] Cart has subscription item

**Test Steps:
1. During subscription purchase, navigate to delivery schedule screen
2. Select specific days (e.g. Mon, Wed, Fri)
3. Tap 'Same juice everyday' checkbox → verify behavior
4. Complete checkout
**Expected Results:
1. Day-wise schedule JSON sent to bmjServer during initiate
2. Schedule stored as metadata in Chargebee subscription
3. After subscription created, verify delivery schedule visible in subscription details
**Test Data:**
- TA-04, subscription with day-wise schedule: Mon/Wed/Fri selected

---

### TC-E2E-CHK-CHK-013: Refetch subscription state after subscription checkout

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-032 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-05)
- [ ] Subscription checkout completed

**Test Steps:
1. After checkout complete, call GET /api/v1/subscriptions/{subscription_id}
2. Verify subscription state
**Expected Results:
1. Refetched subscription status matches expected 'active'
2. Plan details, billing info, schedule all correct
3. No optimistic UI — state confirmed from MySQL synced via Chargebee webhook
**Test Data:**
- TA-05, subscription ID from checkout

---

### TC-E2E-CHK-CHK-014: Chargebee webhook creates subscription record in MySQL

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-033 |
| **Linked UC** | UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-06)
- [ ] Subscription checkout completed

**Test Steps:
1. Complete subscription purchase
2. Wait for Chargebee webhook to be processed (up to 10 seconds)
3. Query database or check subscription via API
**Expected Results:
1. Webhook received and processed by bmjServer
2. Subscription record created in MySQL
3. webhook_events table has subscription_created event
4. No duplicate processing (idempotent)
**Test Data:**
- TA-06, subscription checkout, webhook verification

---

## 3. Edge Cases

### TC-E2E-CHK-CHK-015: Network error during checkout — retry recovers gracefully

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-032 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-09)
- [ ] Cart has items
- [ ] Ability to toggle airplane mode

**Test Steps:
1. Initiate checkout successfully → get hosted_page_url
2. Toggle airplane mode ON
3. Complete payment on hosted page (or simulate)
4. Call POST /api/v1/checkout/complete → network error
5. Toggle airplane mode OFF
6. Retry checkout complete with same session_id
**Expected Results:
1. First complete call fails with network error
2. Cart NOT cleared (no optimistic UI)
3. Retry succeeds → order created
4. Checkout session still valid (idempotent)
5. No duplicate order created
**Test Data:**
- TA-09, network interruption during checkout complete

---

### TC-E2E-CHK-CHK-016: Checkout session status polling returns correct state

| Field | Value |
|-------|-------|
| **Module** | CHECKOUT |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-031 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-10)
- [ ] Checkout initiated and in progress

**Test Steps:
1. Initiate checkout → get checkout_session_id
2. Poll GET /api/v1/checkout/status/{checkout_session_id} before payment
3. Complete payment on hosted page
4. Poll status again after payment
**Expected Results:
1. Before payment: status = 'pending' or 'in_progress'
2. After payment: status = 'completed' or 'succeeded'
3. Session ID remains valid until order created
**Test Data:**
- TA-10, checkout session polling

---

