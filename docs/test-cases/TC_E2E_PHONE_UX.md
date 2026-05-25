# Phone UX Module - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-23
> **Module:** PHONE_UX
> **Test Type:** E2E (End-to-End Black-Box) — Phone-Specific Behavior
> **Total Test Cases:** 12
> **Linked BR:** BR-001, BR-006, BR-008, BR-011
> **Linked UC:** UC-AUTH-001 to UC-AUTH-007, UC-01

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- bmjServer deployed and accessible (running in Docker)
- Flutter debug APK installed on physical Android phone via `adb install`
- Phone connected via USB with USB debugging enabled
- Notification permission granted on the device
- SIM card with test phone number inserted
- Ability to toggle airplane mode, kill apps, and use Android back navigation

---

## Table of Contents

1. [App Kill & Resume During Auth Flows (PHONE-001 to PHONE-003)](#1-app-kill--resume-during-auth-flows)
2. [Network Toggle During Operations (PHONE-004 to PHONE-006)](#2-network-toggle-during-operations)
3. [Android Navigation & Multitasking (PHONE-007 to PHONE-009)](#3-android-navigation--multitasking)
4. [Permissions & Deep Links (PHONE-010 to PHONE-012)](#4-permissions--deep-links)

---

## 1. App Kill & Resume During Auth Flows

### TC-E2E-PHONE-PHONE-001: App kill during OTP verification — resume shows login

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh app install / logged out state
- [ ] Phone with SIM: 9876543210
- [ ] Email inbox accessible: e2e-phone-kill-test@bookmyjuice.co.in

**Test Steps:**
1. Open app → Sign Up tab → tap "Sign up with Email"
2. Enter email: e2e-phone-kill-test@bookmyjuice.co.in → complete email verification
3. On phone entry step, enter: 9876543210 → tap "Send OTP"
4. OTP is received via SMS — **DO NOT enter OTP yet**
5. **Kill app completely** (swipe from recents)
6. Reopen app
7. Observe the screen shown

**Expected Results:**
1. After app kill + reopen:
   - Login/Signup screen is shown (NOT Dashboard — no JWT exists)
   - The in-progress signup state is **lost** (no partial session restored)
2. User must start signup fresh from the beginning
3. Alternative acceptable behavior: App may restore to the OTP entry screen if signup state is cached locally — verify this behavior and document it
4. No crash on reopen — app loads cleanly

**Test Data:**
- email: e2e-phone-kill-test@bookmyjuice.co.in
- phone: 9876543210
- N/A (test does not complete signup)

---

### TC-E2E-PHONE-PHONE-002: App kill during checkout — verify no partial order

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-031 |
| **Linked UC** | UC-03, UC-04 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01 or TA-04)
- [ ] Cart has at least 2 one-time items
- [ ] Chargebee test site configured with hosted pages

**Test Steps:**
1. Navigate to Cart → tap "Checkout"
2. App opens Chargebee Hosted Page in WebView
3. Fill in payment details with test card: 4111 1111 1111 1111
4. **Before tapping "Pay", kill app completely** (swipe from recents)
5. Reopen app
6. Navigate to Orders screen
7. Check Cart screen

**Expected Results:**
1. App reopens to either Dashboard or Login screen (based on JWT state)
2. Auto-login succeeds (JWT still valid) → Dashboard shown
3. Orders screen: No new order created (checkout was not completed)
4. Cart screen: Items still present in cart (checkout session was abandoned before payment)
5. No partial order, no phantom charge on the card
6. User can proceed to checkout again

**Test Data:**
- Logged-in user with cart items
- Test card: 4111 1111 1111 1111

---

### TC-E2E-PHONE-PHONE-003: App kill during subscription action (pause/resume)

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-041, BR-042 |
| **Linked UC** | UC-05, UC-06 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with active subscription (TA-05)
- [ ] Before 9 PM IST cutoff

**Test Steps:**
1. Navigate to Subscriptions → select active subscription
2. Tap "Pause Subscription"
3. Confirmation dialog appears → tap "Confirm"
4. **Immediately kill app** (within 1 second of confirming)
5. Reopen app
6. Navigate to Subscriptions screen
7. Wait 10 seconds → pull-to-refresh

**Expected Results:**
1. App reopens → auto-login succeeds → Dashboard shown
2. Navigate to Subscriptions:
   - If the pause API call completed before kill: Subscription shows "Paused" status
   - If the API call didn't complete: Subscription still shows "Active"
3. No inconsistent state: Subscription is either fully paused or fully active
4. No "stuck" loading spinner or infinite loading state
5. User can try pause again if the first attempt didn't take effect

**Test Data:**
- User: TA-05 (active subscription)
- Action: Pause subscription

---

## 2. Network Toggle During Operations

### TC-E2E-PHONE-PHONE-004: Airplane mode during catalog browsing

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-008 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App open on Product Catalog screen (loaded successfully with products visible)
- [ ] Phone has internet connection initially

**Test Steps:**
1. Browse product catalog — verify products are loaded
2. **Toggle airplane mode ON** (disable all connectivity)
3. Scroll through the catalog
4. Tap on a product to view details
5. Try to add item to cart (if possible as guest)
6. Observe all behaviors
7. **Toggle airplane mode OFF** (restore connectivity)
8. Pull-to-refresh or navigate away and back

**Expected Results:**
1. While offline:
   - Already loaded products remain visible (cached list)
   - Tapping a product that was already loaded shows cached details
   - Attempting to add to cart shows: "Network error. Please try again." or similar
   - No blank screen, no crash, no infinite spinner
2. After restoring network:
   - Pull-to-refresh reloads products from server
   - Cart operations work again
3. App gracefully handles online/offline transitions

**Test Data:**
- N/A (network toggle test)

---

### TC-E2E-PHONE-PHONE-005: Airplane mode during cart-add operation

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-004 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart is empty
- [ ] Phone has internet connection

**Test Steps:**
1. Navigate to product detail page for a one-time juice
2. **Toggle airplane mode ON** (disable connectivity)
3. Tap "Add to Cart"
4. Observe the UI behavior
5. Wait 5 seconds
6. **Toggle airplane mode OFF**
7. Check the Cart screen

**Expected Results:**
1. With airplane mode ON:
   - Loading spinner appears briefly on the add-to-cart button
   - Error message: "Network error. Please check your connection." or similar toast/snackbar
   - The product page remains visible (no navigation away)
   - Button returns to its normal "Add to Cart" state
2. After restoring network:
   - Cart is still empty (item was NOT added optimistically)
3. User can tap "Add to Cart" again → succeeds
4. Cart shows the item after retry succeeds

**Test Data:**
- One-time juice product
- Network toggled during add-to-cart

---

### TC-E2E-PHONE-PHONE-006: Network loss during checkout — retry mechanism

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-030, BR-031 |
| **Linked UC** | UC-03 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in (TA-01)
- [ ] Cart has one-time items
- [ ] Chargebee test site configured

**Test Steps:**
1. Navigate to Cart → tap "Checkout" → Chargebee hosted page opens successfully
2. Fill in payment details with test card
3. **Toggle airplane mode ON**
4. Tap "Pay" / "Submit Payment"
5. Observe behavior
6. **Toggle airplane mode OFF**
7. Observe the page behavior

**Expected Results:**
1. With airplane mode ON during Chargebee payment:
   - Chargebee hosted page shows network error (this is a WebView, error handling depends on Chargebee's own implementation)
   - OR the page may appear stuck with a loading indicator
   - No crash or blank page
2. After restoring network:
   - If Chargebee retries: Payment may process — verify via Orders screen after returning to app
   - If Chargebee fails: User sees "Payment failed" on the hosted page
   - User can retry payment
3. No scenario where card is charged but no order is created (data consistency)

**Test Data:**
- Logged-in user with cart items
- Test card: 4111 1111 1111 1111

---

## 3. Android Navigation & Multitasking

### TC-E2E-PHONE-PHONE-007: Android back button navigation chain test

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App freshly opened to login/signup screen

**Test Steps:**
1. From Login screen → tap "Sign Up" tab
2. Tap "Sign up with Email"
3. Enter email and tap "Continue" → Email verification screen
4. **Press Android back button** — observe where it navigates
5. Re-enter email verification flow → verify email
6. Enter phone → send OTP → **Press Android back button** — observe
7. Enter OTP → verify → Address form appears → **Press Android back button** — observe
8. Fill address → Continue → Password screen → **Press Android back button** — observe
9. Enter password → Create Account → Dashboard
10. **Press Android back button** repeatedly — observe chain

**Expected Results:**
1. Back button at each step navigates to the PREVIOUS logical screen (not exit app)
2. At email verification → back → email entry screen (data preserved)
3. At OTP entry → back → phone entry screen (data preserved)
4. At address form → back → OTP entry screen (may require re-verification)
5. At password screen → back → address form (data preserved)
6. At Dashboard → back → app goes to background / exits (standard Android behavior)
7. No "double back to exit" where one back press shows a screen and the next exits
8. No app crash from rapid back-press spam

**Test Data:**
- email: e2e-back-nav@bookmyjuice.co.in
- phone: 9876543210
- password: BackNav1!

---

### TC-E2E-PHONE-PHONE-008: Multitasking switch (app switcher) during flow

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-001, BR-006 |
| **Linked UC** | UC-AUTH-001, UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App open on the OTP verification step (phone: 9876543210, OTP just sent)

**Test Steps:**
1. Open app → start email-first signup
2. Enter email → verify email → enter phone → tap "Send OTP"
3. **While OTP is received via SMS, switch to another app** (e.g., open SMS app, browser, or settings)
4. Read the OTP from SMS
5. **Switch back to BMJ app** (via app switcher / recents)
6. Observe the screen state
7. Enter the OTP and verify
8. Continue with address and password → complete signup

**Expected Results:**
1. After switching back to BMJ app:
   - App is on the same OTP entry screen (state preserved)
   - All entered data (phone number) is still visible
   - OTP timer/countdown (if any) is correct relative to elapsed time
   - No crash, no data loss, no auto-navigation away
2. OTP entry works normally after returning
3. Complete signup successfully

**Test Data:**
- email: e2e-multitask@bookmyjuice.co.in
- phone: 9876543210
- password: MultiTask1!

---

### TC-E2E-PHONE-PHONE-009: Concurrent login on two devices

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-04 exists (email: e2e-existing@bookmyjuice.co.in, password: TestPass123!)
- [ ] Two devices available (or one device + one browser/emulator)
- [ ] Device 1: Phone with BMJ app installed
- [ ] Device 2: Another phone/emulator OR Postman/curl

**Test Steps:**
1. **Device 1:** Log in with TA-04 credentials → Dashboard shown
2. **Device 2:** Log in with the SAME credentials → Dashboard shown
3. On Device 1: Navigate through app (catalog, cart, profile)
4. On Device 2: Add item to cart
5. On Device 1: Check if cart reflects changes
6. On Device 1: Kill app and reopen
7. On Device 2: Go to Profile → change display name
8. On Device 1: Refresh Profile screen

**Expected Results:**
1. Both devices can log in simultaneously with the same credentials
2. Each device has its own independent JWT token
3. Cart operations on one device do NOT affect the other device's cart (carts are user-specific but device-independent)
4. Actions on one device do not invalidate the other device's session
5. Profile changes on one device are reflected when the other device refreshes
6. No "logged in elsewhere" message or forced logout

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- password: TestPass123!
- Two devices/terminals

---

## 4. Permissions & Deep Links

### TC-E2E-PHONE-PHONE-010: Notification permission denied → then re-enabled

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-060 |
| **Linked UC** | UC-10 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install of BMJ app (or clear app data)
- [ ] Device running Android 13+ (notification permission required)

**Test Steps:**
1. Open BMJ app for the first time
2. When system dialog appears: "Allow BookMyJuice to send notifications?" → tap **"Deny"**
3. Complete signup/login
4. Go to Profile / Settings
5. Check if there's a notification settings option
6. Now go to Android Settings → Apps → BookMyJuice → Permissions → Notifications → **Enable**
7. Return to BMJ app
8. Place an order or trigger a notification event (via Firebase Console or backend)

**Expected Results:**
1. App handles "Deny" gracefully:
   - No crash, no repeated permission prompt
   - App continues to function normally
   - If there's a "notification status" indicator, it shows "disabled"
2. After re-enabling in system settings:
   - App picks up the new permission state
   - Notifications are received normally for subsequent events
3. FCM token is registered even if permission was initially denied (token registration is independent of permission)

**Test Data:**
- Fresh install / app data cleared
- Notification permission toggled

---

### TC-E2E-PHONE-PHONE-011: Deep link navigation from notification (app closed)

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-060, BR-062 |
| **Linked UC** | UC-10, UC-11 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in and has an existing order/subscription
- [ ] FCM token registered (device is receiving push notifications)
- [ ] Firebase Console accessible for sending test pushes

**Test Steps:**
1. **Kill the BMJ app completely** (swipe from recents — app not running at all)
2. Using Firebase Console → Cloud Messaging → Send test notification:
   - Title: "Order Status Update"
   - Body: "Your order #ORD-123 has been delivered"
   - Click action: Deep link to order detail (e.g., `bmjapp://orders/ORD-123`)
   - Target: FCM token of the test device
3. Observe notification appearing in system tray
4. **Tap the notification**
5. Observe what screen opens

**Expected Results:**
1. Notification appears in system tray with correct title and body
2. Tapping the notification:
   - App opens (cold start)
   - Auto-login occurs (JWT still valid) → splash → Dashboard
   - App navigates to the specific Order Detail screen (NOT just Dashboard)
   - OR if deep link navigation is not implemented: App opens to Dashboard (acceptable, but deep link is preferred)
3. Order detail shows the correct order information
4. If deep linking is NOT implemented, document this as a gap

**Test Data:**
- Existing order: ORD-123 (or any real order)
- FCM notification with deep link payload

---

### TC-E2E-PHONE-PHONE-012: Deep link navigation from notification (app backgrounded)

| Field | Value |
|-------|-------|
| **Module** | PHONE_UX |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-060, BR-062 |
| **Linked UC** | UC-10, UC-11 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in
- [ ] App is open in the background (press Home button, app still running)
- [ ] FCM token registered

**Test Steps:**
1. Open BMJ app → ensure user is logged in → **Press Home button** (app goes to background)
2. Using Firebase Console → Cloud Messaging → Send test notification:
   - Title: "Payment Successful"
   - Body: "Your payment of ₹199 for Order #ORD-456 was successful"
   - Click action: Deep link to order detail (`bmjapp://orders/ORD-456`)
3. Observe notification in system tray
4. **Tap the notification**
5. Observe what happens

**Expected Results:**
1. Notification appears in system tray
2. Tapping the notification:
   - App is brought to foreground (not cold started)
   - App navigates to the Order Detail screen for ORD-456
   - OR app navigates to Dashboard (acceptable fallback)
3. No data loss — the app state from before backgrounding is preserved where appropriate
4. No duplicate screens or navigation stack corruption
5. If deep linking is not implemented, document this as a gap

**Test Data:**
- Existing order: ORD-456
- FCM notification with deep link payload

---

## Document Control

- **Created:** 2026-05-23
- **Version:** 1.0
- **Total Test Cases:** 12
- **Status:** ✅ Complete — Ready for Execution
