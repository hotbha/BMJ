# Cross-Module Integrated Flow - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-23
> **Module:** CROSS_MODULE (Integrated Flows)
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 12
> **Linked BR:** BR-001 to BR-073 (cross-module coverage)
> **Linked UC:** UC-AUTH-001 to UC-11 (integrated flows)

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- bmjServer deployed and accessible (running in Docker)
- Chargebee test site configured with hosted pages and webhooks
- Firebase project with Phone Auth + Google Sign-In enabled
- All test accounts (TA-01 to TA-10) created
- Phone with SIM for OTP reception
- Email inboxes accessible for verification codes

---

## Table of Contents

1. [Full Happy Path — Guest to Order (XMOD-001 to XMOD-003)](#1-full-happy-path--guest-to-order)
2. [Subscription Lifecycle (XMOD-004 to XMOD-006)](#2-subscription-lifecycle)
3. [Cross-Session & Data Integrity (XMOD-007 to XMOD-009)](#3-cross-session--data-integrity)
4. [Security & Edge Cases (XMOD-010 to XMOD-012)](#4-security--edge-cases)

---

## 1. Full Happy Path — Guest to Order

### TC-E2E-XMOD-XMOD-001: Guest → Browse → Cart → Signup → Checkout → Order (Full Happy Path)

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P0-Critical |
| **Severity** | S1-Major |
| **Linked BR** | BR-001, BR-002, BR-004, BR-008, BR-010, BR-030, BR-050 |
| **Linked UC** | UC-AUTH-001, UC-01, UC-03, UC-08 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install / logged out (guest state)
- [ ] Email inbox accessible: e2e-full-flow@bookmyjuice.co.in
- [ ] Phone with SIM: 9876543210
- [ ] Chargebee hosted pages configured
- [ ] Test card: 4111 1111 1111 1111

**Test Steps:**
1. Open app → observe Login/Signup screen (guest state)
2. Tap "Browse Products" or navigate to Catalog (guest browsing)
3. Scroll through products — verify images, names, prices load correctly
4. Tap a product to view details — verify one-time and subscription pricing shown
5. Tap "Add to Cart" → observe "Please login to add items to cart" prompt (PD-01)
6. Tap "Sign Up" from the prompt → navigate to Sign Up tab
7. Sign up with Email:
   - Enter: e2e-full-flow@bookmyjuice.co.in → verify email code
   - Enter phone: 9876543210 → Send OTP → verify OTP
   - Enter address: "Flat 101, Lake View Apartments, Sector 15, Gurgaon, Haryana, 122002, India"
   - Enter password: FullFlow1! → confirm → "Create Account"
8. Verify: Account created → auto-logged in → Dashboard shown
9. Navigate to Cart → the previously browsed item should be present (via guest cart merge)
10. Add a second one-time item to cart
11. Navigate to Cart → verify both items, pricing breakdown (subtotal, tax, grand total)
12. Tap "Checkout" → Chargebee hosted page opens in WebView
13. Enter test card: 4111 1111 1111 1111, any future expiry, any CVV
14. Complete payment → observe redirect back to app
15. App shows Order Confirmation screen with order details
16. Navigate to Orders screen → verify the new order appears with correct status
17. Tap the order → verify order details (items, pricing, shipping address, status badge)

**Expected Results:**
1. **Guest Browsing:** Products load without auth, images/prices visible (steps 2-3)
2. **Auth First Enforcement:** Guest cannot add to cart — login prompt shown (step 5)
3. **Signup:** Completes successfully with email verification + phone OTP + address + password (step 7)
4. **Auto-Login:** After signup, user is automatically logged in → Dashboard (step 8)
5. **Cart Merge:** Guest browsing intent → if cart_id was generated, items merge on login (step 9)
6. **Add Items:** Authenticated user can add items to cart (step 10)
7. **Cart Display:** Correct pricing breakdown from server (step 11)
8. **Checkout:** Chargebee hosted page loads, payment completes (steps 12-14)
9. **Order Confirmation:** Confirmation screen shown with order details (step 15)
10. **Order History:** Order appears in Orders list with correct status (step 16)
11. **Order Detail:** All details correct including shipping address from signup (step 17)

**Test Data:**
- email: e2e-full-flow@bookmyjuice.co.in
- phone: 9876543210
- address: Flat 101, Lake View, Sector 15, Gurgaon, 122002, India
- password: FullFlow1!
- card: 4111 1111 1111 1111

---

### TC-E2E-XMOD-XMOD-002: Guest → Browse → Login → Checkout (Existing User Flow)

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P0-Critical |
| **Severity** | S1-Major |
| **Linked BR** | BR-004, BR-005, BR-006, BR-008, BR-030 |
| **Linked UC** | UC-AUTH-004, UC-01, UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install / logged out (guest state)
- [ ] Existing user TA-04 exists (email: e2e-existing@bookmyjuice.co.in, password: TestPass123!)
- [ ] TA-04 has NO items in cart initially
- [ ] Chargebee test site configured

**Test Steps:**
1. Open app as guest → browse to product catalog
2. Add one-time item to cart → observe login prompt
3. Tap "Login" → navigate to Sign In tab
4. Enter email: e2e-existing@bookmyjuice.co.in, password: TestPass123! → tap "Sign In"
5. Verify: Dashboard shown, JWT stored
6. Navigate to Cart → observe cart merge (if guest cart existed) or empty cart
7. Browse products → add 2 one-time items to cart
8. Navigate to Cart → verify items and pricing
9. Tap "Checkout" → Chargebee hosted page opens
10. Complete payment with test card
11. Observe redirect → Order Confirmation screen
12. Navigate to Orders → verify order exists
13. **Kill app** → reopen → verify auto-login → verify order still in history

**Expected Results:**
1. Guest → Login flow works seamlessly (steps 1-5)
2. Cart merge occurs on login if guest had items (step 6)
3. Authenticated cart operations work (steps 7-8)
4. Checkout completes successfully (steps 9-11)
5. Order persists in history (step 12)
6. Auto-login works after app kill, order history preserved (step 13)

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- password: TestPass123!
- card: 4111 1111 1111 1111

---

### TC-E2E-XMOD-XMOD-003: Subscribe → Verify Delivery Schedule → Receive Order Update

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-040, BR-070, BR-050 |
| **Linked UC** | UC-03, UC-05, UC-08 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart is empty
- [ ] Serviceable pincode in system (e.g., 122001 — Gurgaon)
- [ ] Chargebee test site configured with subscription plans

**Test Steps:**
1. Browse to subscription product (e.g., Delight 200ml Weekly)
2. Tap "Subscribe" → item added to cart (cart type = subscription)
3. Navigate to Cart → verify plan name, frequency, pricing displayed
4. Tap "Checkout" → Chargebee hosted page opens
5. Select delivery day preference on hosted page (if applicable)
6. Complete payment with test card 4111 1111 1111 1111
7. Observe redirect back to app → Subscription Confirmation screen
8. Navigate to Subscriptions → verify new subscription appears as "Active"
9. Navigate to Orders → verify initial order exists for this subscription
10. Navigate to Delivery screen → verify delivery schedule displayed
11. Verify delivery address is the one provided during signup
12. Trigger delivery update (simulate via webhook or wait for next billing cycle):
    - OR observe the delivery status changes over time

**Expected Results:**
1. Subscription product can be added to subscription cart (steps 1-2)
2. Cart correctly shows subscription details, not one-time pricing (step 3)
3. Checkout completes with subscription plan (steps 4-7)
4. Subscription appears as "Active" in subscriptions list (step 8)
5. Initial order for the subscription appears in orders (step 9)
6. Delivery schedule is shown with correct days (step 10)
7. Delivery address matches signup/registered address (step 11)

**Test Data:**
- User: TA-01
- Subscription plan: e.g., plan_delight_200_weekly
- Test card: 4111 1111 1111 1111
- Pincode: 122001

---

## 2. Subscription Lifecycle

### TC-E2E-XMOD-XMOD-004: Subscribe → Pause → Resume → Cancel → Verify Status

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-040, BR-041, BR-042, BR-043, BR-044 |
| **Linked UC** | UC-05, UC-06, UC-07 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with active subscription (TA-05)
- [ ] Before 9 PM IST cutoff
- [ ] Subscription is active

**Test Steps:**
1. Navigate to Subscriptions → verify active subscription is listed
2. Select the active subscription → view details
3. Tap "Pause Subscription" → confirm → verify status changes to "Paused"
4. Navigate away → return → pull-to-refresh → status remains "Paused"
5. Tap "Resume Subscription" → confirm → verify status changes to "Active"
6. Navigate away → return → pull-to-refresh → status remains "Active"
7. Tap "Cancel Subscription" → choose "End of term" cancellation
8. Confirm cancellation → verify status shows "Scheduled for cancellation"
9. Verify the cancellation date/end of term date is displayed

**Expected Results:**
1. Active subscription visible with correct details (step 1-2)
2. Pause → status shows "Paused", persists across navigation (steps 3-4)
3. Resume → status shows "Active", persists across navigation (steps 5-6)
4. Cancel (end of term) → status shows "Scheduled for cancellation" (steps 7-8)
5. End of term date displayed correctly (step 9)
6. All state changes are reflected after pull-to-refresh (server-side changes)
7. BR-044: Multiple pause/resume cycles work (test at least 2 cycles)

**Test Data:**
- User: TA-05 (active subscription)
- Action: Pause → Resume → Cancel

---

### TC-E2E-XMOD-XMOD-005: Expired subscription → Attempt to access premium content

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-040, BR-043 |
| **Linked UC** | UC-07 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-07 exists (cancelled/expired subscription)
- [ ] User is logged in on the device

**Test Steps:**
1. Log in with TA-07 credentials
2. Navigate to Subscriptions → verify subscription shows "Cancelled" / "Expired"
3. Try to access features normally gated behind an active subscription:
   - View subscription-only products/pricing
   - Try to place a new subscription order
   - Try to modify the cancelled subscription (pause/resume)
4. Observe behavior for each action
5. Browse to a subscription plan → try to checkout

**Expected Results:**
1. Cancelled/expired subscription is visible with correct status label (step 2)
2. Previously subscribed items may still be viewable but marked as "inactive"
3. Attempting to pause/resume a cancelled subscription shows appropriate error:
   - "Cannot modify a cancelled subscription" or similar
4. User CAN create a NEW subscription (subscribe again) from catalog (step 5)
5. No crash or confusing state when viewing expired subscription details

**Test Data:**
- User: TA-07 (cancelled subscription)
- email: e2e-existing@bookmyjuice.co.in
- password: TestPass123!

---

### TC-E2E-XMOD-XMOD-006: Multiple subscriptions management

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-047 |
| **Linked UC** | UC-05 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-09 exists with 2+ active subscriptions
- [ ] User is logged in

**Test Steps:**
1. Login with TA-09 credentials
2. Navigate to Subscriptions → list view
3. Observe how multiple subscriptions are displayed
4. Select Subscription A → view details → pause it
5. Go back to list → verify Subscription A shows "Paused", Subscription B shows "Active"
6. Select Subscription B → view details → verify it's still active
7. Go to Profile → verify subscription count/meta data
8. Return to Subscriptions list → verify both subscriptions listed with correct statuses

**Expected Results:**
1. Multiple subscriptions are displayed in a list/scrollable view (steps 2-3)
2. Each subscription has independent status (steps 4-5)
3. Pausing one subscription does NOT affect the other (step 5-6)
4. Profile may show subscription count (step 7)
5. After refresh, both subscriptions maintain correct independent states (step 8)

**Test Data:**
- User: TA-09 (multiple active subscriptions)

---

## 3. Cross-Session & Data Integrity

### TC-E2E-XMOD-XMOD-007: Cart persists across app kill/restart

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has 2 one-time items

**Test Steps:**
1. Log in with TA-01
2. Browse → add 2 one-time items to cart
3. Navigate to Cart → verify items and pricing
4. **Kill app completely** (swipe from recents)
5. Reopen app
6. Observe login state (auto-login)
7. Navigate to Cart screen
8. Observe cart contents

**Expected Results:**
1. Auto-login succeeds → Dashboard shown (JWT still valid)
2. Cart screen shows the same 2 items from before the kill
3. Cart type is preserved ("onetime")
4. Pricing is recalculated/refetched from server (may show slight loading)
5. No items lost — cart is server-persisted
6. User can proceed to checkout normally

**Test Data:**
- User: TA-01 with cart items
- Cart: 2 one-time items

---

### TC-E2E-XMOD-XMOD-008: Order cancellation → Verify refund/credit in profile

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-050, BR-054 |
| **Linked UC** | UC-08, UC-09 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with at least one completed order (TA-04 or similar)
- [ ] Order is in a cancellable state (not delivered/completed)
- [ ] Chargebee webhook processing is active

**Test Steps:**
1. Log in with TA-04
2. Navigate to Orders → select an order that can be cancelled
3. Tap "Cancel Order" / request cancellation
4. Observe confirmation dialog → confirm cancellation
5. Observe the order status update
6. Navigate to Orders list → verify order shows "Cancelled" status
7. Navigate to Invoices (if available) → check if credit note / refund invoice appears
8. Navigate to Profile → verify any credit balance if applicable

**Expected Results:**
1. Order cancellation flow is clear with confirmation dialog (steps 2-4)
2. Order status updates to "Cancelled" (step 5-6)
3. If refund is applicable (payment already collected):
   - Invoice/credit section shows credit note or refund entry (step 7)
   - OR there is a note that refund will be processed via Chargebee
4. Profile may show any outstanding credits/balance (step 8)
5. If order cannot be cancelled (e.g., already delivered), appropriate message shown

**Test Data:**
- User: TA-04 (has completed order)
- Pincode: 122001

---

### TC-E2E-XMOD-XMOD-009: Network failure during checkout — verify no partial order created

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-033 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has one-time items
- [ ] Chargebee test site configured
- [ ] Ability to quickly toggle airplane mode

**Test Steps:**
1. Log in with TA-01 → add items to cart
2. Navigate to Cart → tap "Checkout" → Chargebee hosted page opens
3. Fill in test card details (4111 1111 1111 1111)
4. **Toggle airplane mode ON** before tapping "Pay"
5. Tap "Pay" → observe behavior (Chargebee may show error or stuck loading)
6. Wait 10 seconds
7. **Toggle airplane mode OFF**
8. Observe the page — does it recover?
9. If page shows "Payment Failed" or similar, tap "Retry" or go back
10. Navigate to Orders → check if any order was created
11. Navigate to Cart → check cart state
12. Check Chargebee Admin Console to verify no charge was created

**Expected Results:**
1. Network loss during payment does NOT create a partial order (steps 4-6)
2. After network restore:
   - Chargebee page may show "Processing..." or "Failed" depending on its retry logic (step 7-8)
3. Orders screen: No order created for this transaction (step 10)
4. Cart: Items still present (checkout was not completed) (step 11)
5. Chargebee console: No charge recorded for this transaction (step 12)
6. User can go back to cart and try checkout again without issues

**Test Data:**
- User: TA-01 with cart items
- Test card: 4111 1111 1111 1111

---

## 4. Security & Edge Cases

### TC-E2E-XMOD-XMOD-010: Stale JWT with expired subscription — access control

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006, BR-040 |
| **Linked UC** | UC-AUTH-004, UC-05 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-04 exists (has active subscription)
- [ ] User is logged in on the device (JWT stored)
- [ ] Access to Chargebee Admin Console to cancel subscription

**Test Steps:**
1. Log in with TA-04 → verify Dashboard shown, subscription visible in Subscriptions
2. **Via Chargebee Admin Console**: Cancel the user's active subscription manually
3. Trigger the webhook to sync: Cancel → bmjServer processes cancellation
4. **On device** (without refresh/navigation): Try to access subscription-gated features
5. Pull-to-refresh on Subscriptions screen
6. Navigate to Orders → check if any new order was attempted

**Expected Results:**
1. Before webhook sync: App still shows subscription as "Active" (cached state)
2. After pull-to-refresh (step 5):
   - Subscription status updates to "Cancelled" or "Expired"
3. Attempting subscription actions (pause/resume) on the now-cancelled sub shows appropriate error
4. Auto-login still works after cancellation (JWT is independent of subscription status)
5. User can still browse catalog and access profile
6. User CAN create a new subscription if desired

**Test Data:**
- User: TA-04 → cancel subscription via Chargebee admin
- Then observe app behavior

---

### TC-E2E-XMOD-XMOD-011: OTP resend with rapid clicks (rate limiting UX)

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-002, NFR-011 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543210
- [ ] App open on signup phone entry step

**Test Steps:**
1. Open app → Sign Up with Email → enter email → verify email
2. On phone entry, enter: 9876543210
3. Tap "Send OTP" → OTP sent (first SMS)
4. **Immediately tap "Resend OTP" rapidly 5 times** (within 2 seconds)
5. Observe behavior — count how many OTP SMS are received
6. Continue tapping "Resend OTP" every 10 seconds for 1 minute (or until rate limited)
7. Observe the UI — countdown timer, resend button state
8. Note the error message when rate limited (if any)
9. Wait 5 minutes (or rate limit reset period)
10. Tap "Resend OTP" again

**Expected Results:**
1. First "Send OTP" sends SMS successfully (step 3)
2. Rapid taps on "Resend" (step 4):
   - Frontend _isSendingOTP guard (or similar) should prevent duplicate API calls
   - Only 1-2 actual OTP SMS received
   - Button may show countdown timer (e.g., "Resend in 30s")
3. After multiple resends (step 6):
   - Backend rate limiter kicks in after ~10 OTP sends per 5 min
   - UI shows clear message: "Too many OTP requests. Please try again in a few minutes."
   - Resend button is disabled during rate limit period
4. After waiting, resend works again (step 9-10)
5. No crash, no blank screen, no infinite loading

**Test Data:**
- phone: 9876543210
- Rapid resend test with OTP button

---

### TC-E2E-XMOD-XMOD-012: Password reset → Old password rejected → New password works

| Field | Value |
|-------|-------|
| **Module** | CROSS_MODULE |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009, BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-04 exists (email: e2e-existing@bookmyjuice.co.in, phone: 9876543212)
- [ ] User is logged out (or fresh install)
- [ ] Phone with SIM: 9876543212

**Test Steps:**
1. Open app → Sign In tab
2. Tap "Forgot Password?"
3. Select "Reset via Mobile OTP"
4. Enter phone: 9876543212 → tap "Send OTP"
5. Receive OTP via SMS → enter OTP → verify
6. Enter new password: ResetTok1! → confirm → tap "Reset Password"
7. Observe success message
8. Navigate to Sign In → try logging in with **OLD** password (TestPass123!)
9. Observe error message
10. Log in with **NEW** password (ResetTok1!) → verify success → Dashboard shown
11. **Kill app** → reopen → verify auto-login works with new password context
12. Go to Profile → change password back to TestPass123! via "Change Password" option

**Expected Results:**
1. Password reset flow works — OTP sent to phone, reset succeeds (steps 2-7)
2. Old password is REJECTED after reset (step 8-9):
   - Error: "Invalid username or password!"
3. New password works for login (step 10):
   - Success → Dashboard shown with JWT
4. Auto-login works after password reset:
   - If old token was invalidated (token version incremented): Auto-login fails → login screen shown (step 11)
   - User must log in with new password
   - After login, new JWT with updated token version stored
5. Password can be changed again via Profile → Change Password (step 12)

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- phone: 9876543212
- old password: TestPass123!
- new password: ResetTok1!
- final password (restore): TestPass123!

---

## Document Control

- **Created:** 2026-05-23
- **Version:** 1.0
- **Total Test Cases:** 12
- **Status:** ✅ Complete — Ready for Execution
