# NOTIFICATIONS Module — End-to-End (E2E) Black Box Test Cases

> **Document Version:** 1.0  
> **Last Updated:** 2026-05-18  
> **Module:** NOTIFICATIONS  
> **Type:** E2E (Black Box)  
> **Automation Status:** ❌ Manual (requires real device for notifications)

---

## Prerequisites

Refer to **`TEST_PREREQUISITES.md`** for full environment setup. Key items for this module:
| # | Pre-Requisite | Status |
|---|---------------|--------|
| P-01 | bmjServer deployed to staging with public URL | 🔴 Must Do |
| P-13 | Firebase project created (bookmyjuice-4c156) | 🔴 Must Do |
| F-01 | Flutter APK built with API_BASE_URL=staging | 🔴 Must Do |
| F-03 | APK installed on physical Android device | 🔴 Must Do |
| F-05 | Notification permission granted on device | 🔴 Must Do |
| F-08 | Device has internet connection (WiFi or mobile data) | 🔴 Must Do |
| TA-04 | Existing registered user for authentication | 🔴 Must Do |
| BA-01 | User with fcm_token set in DB for FCM tests | 🔴 Must Insert |

**Linked BRs:** BR-060, BR-061, BR-062  
**Linked UCs:** UC-10, UC-11  
**MVP Note:** Local-only notifications using flutter_local_notifications. FCM infrastructure exists (FirebaseNotificationService + token endpoint) but NO FCM server push for MVP. Notifications triggered locally on webhook processing results.

---

## Test Cases

---

### TC-E2E-NOT-001: Payment failure → local notification displayed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-001 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-060 |
| **Linked UC** | UC-10 |

**Preconditions:**
- [ ] User is logged in with an active session
- [ ] User has a valid payment method saved in Chargebee
- [ ] Notification permission has been granted on the device (Android 13+)
- [ ] App is running in foreground or background
- [ ] User has an active subscription or pending order
- [ ] LocalNotificationService initialized at app startup**Test Steps:**
1. Log in as TA-04 on a physical Android device
2. Open the subscription management screen
3. Initiate a subscription checkout via Chargebee Hosted Pages
4. Complete checkout using Chargebee test card 4000 0000 0000 0002 (declined)
5. Wait for Chargebee to process payment and send payment_failed webhook
6. Trigger a state refresh from the app (pull-to-refresh)
7. Observe the system notification tray

**Expected Results:**
1. User successfully logs in and navigates to subscription management
2. Checkout WebView loads Chargebee Hosted Page
3. Payment is processed and declined by Chargebee
4. Chargebee sends payment_failed webhook - bmjServer processes and updates order status
5. App fetches confirmed state from bmjServer - detects payment_failed event
6. Local notification appears in tray with title containing Payment Failed
7. Notification body explains the payment failure with actionable message

**Test Data:**
- User: TA-04 (e2e-existing@bookmyjuice.co.in / 9876543212)
- Payment card: 4000 0000 0000 0002 (Chargebee declined test card)
- Notification channel ID: bookmyjuice_channel
- Notification title expected: contains Payment Failed
- Notification ID: derived from message ID or timestamp

---
### TC-E2E-NOT-002: Subscription paused → local notification displayed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-002 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-061 |
| **Linked UC** | UC-11 |

**Preconditions:**
- [ ] User is logged in with an active subscription (TA-05)
- [ ] Notification permission granted on device
- [ ] Current time is before 9 PM IST (cutoff)
- [ ] App is running and user is on subscription management screen
- [ ] LocalNotificationService initialized at app startup

**Test Steps:**
1. Log in as TA-05 (user with active subscription)
2. Navigate to subscription management screen
3. Locate the active subscription and tap the Pause button
4. Confirm the pause action in the confirmation dialog
5. Wait for bmjServer to process the pause request and call Chargebee API
6. Wait for Chargebee webhook callback (subscription_paused) to be processed by bmjServer
7. Trigger a state refresh from the app
8. Observe the notification tray

**Expected Results:**
1. User successfully logs in and sees active subscription
2. Pause button is visible and tappable
3. Confirmation dialog appears - user confirms
4. App sends POST to /api/v1/subscriptions/:id/pause - receives 202 Accepted
5. bmjServer calls Chargebee pause API - Chargebee processes
6. Chargebee sends subscription_paused webhook - bmjServer updates DB
7. App fetches confirmed state - subscription status changes to paused
8. Local notification appears with title containing Subscription Paused, body explains pause

**Test Data:**
- User: TA-05 (user with active subscription)
- Subscription status before: active - after: paused
- Notification title expected: contains Paused
- Action executed before 9 PM IST cutoff

---
### TC-E2E-NOT-003: Subscription resumed → local notification displayed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-003 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-061 |
| **Linked UC** | UC-11 |

**Preconditions:**
- [ ] User is logged in with a paused subscription (TA-06)
- [ ] Notification permission granted on device
- [ ] Current time is before 9 PM IST (cutoff)
- [ ] App is running and user is on subscription management screen
- [ ] LocalNotificationService initialized at app startup

**Test Steps:**
1. Log in as TA-06 (user with paused subscription)
2. Navigate to subscription management screen
3. Locate the paused subscription and tap the Resume button
4. Confirm the resume action in the confirmation dialog
5. Wait for bmjServer to process the resume and call Chargebee API
6. Wait for Chargebee webhook callback (subscription_resumed)
7. Trigger a state refresh from the app
8. Observe the notification tray

**Expected Results:**
1. User successfully logs in and sees paused subscription with status Paused
2. Resume button is visible and tappable
3. Confirmation dialog appears - user confirms
4. App sends POST to /api/v1/subscriptions/:id/resume - receives 202 Accepted
5. bmjServer calls Chargebee resume API - Chargebee processes
6. Chargebee sends subscription_resumed webhook - bmjServer updates DB
7. App fetches confirmed state - subscription status becomes active
8. Local notification appears with title Subscription Resumed, body explains next delivery date

**Test Data:**
- User: TA-06 (user with paused subscription)
- Subscription status before: paused - after: active
- Notification title expected: contains Resumed
- Action executed before 9 PM IST cutoff

---

### TC-E2E-NOT-004: Subscription cancelled → local notification displayed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-004 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-061 |
| **Linked UC** | UC-11 |

**Preconditions:**
- [ ] User is logged in with an active subscription (TA-05)
- [ ] Notification permission granted on device
- [ ] Current time is before 9 PM IST (cutoff)
- [ ] App is running and user is on subscription management screen
- [ ] LocalNotificationService initialized at app startup

**Test Steps:**
1. Log in as TA-05 (active subscription)
2. Navigate to subscription management
3. Tap Cancel button on active subscription
4. Select cancellation option: End of current term
5. Confirm the cancellation action
6. Wait for bmjServer to process cancel and call Chargebee API
7. Wait for Chargebee subscription_cancelled webhook callback
8. Trigger a state refresh
9. Observe the notification tray

**Expected Results:**
1. User logs in and sees active subscription
2. Cancel button visible and tappable
3. Cancellation options dialog appears (immediately/end of term/specific date)
4. User selects End of current term and confirms
5. App sends POST to /api/v1/subscriptions/:id/cancel - 202 Accepted
6. bmjServer calls Chargebee cancel API - Chargebee processes
7. Chargebee sends subscription_cancelled webhook - bmjServer updates DB
8. App fetches confirmed state - status becomes cancelled or non_renewing
9. Local notification with title Subscription Cancelled, body explains end date

**Test Data:**
- User: TA-05 (user with active subscription)
- Status before: active - after: cancelled or non_renewing
- Cancel option: end_of_term
- Notification title expected: contains Cancelled

---
### TC-E2E-NOT-005: Order delivered → local notification displayed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-005 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-062 |
| **Linked UC** | UC-11 |

**Preconditions:**
- [ ] User is logged in with a confirmed order in shipped status
- [ ] Notification permission granted on device
- [ ] App is running (foreground or background)
- [ ] LocalNotificationService initialized at app startup
- [ ] Chargebee test site has order in shipped status ready for delivery update
- [ ] Backend webhook endpoint configured and accessible

**Test Steps:**
1. Log in as TA-04 on a physical Android device
2. Navigate to order history - confirm at least one order exists
3. Using Chargebee Admin Console, change an order from shipped to delivered
4. Wait for Chargebee to send order_delivered webhook to bmjServer
5. From the app, navigate to order history and pull-to-refresh
6. Observe the notification tray
7. Tap on the notification

**Expected Results:**
1. User logs in and navigates to order history
2. Orders visible with status badges
3. Chargebee order status updated to delivered - webhook triggered
4. bmjServer receives webhook - validates signature, processes idempotently, updates DB
5. App fetches confirmed state - order status shows Delivered (green badge)
6. Local notification appears with title Order Delivered, body includes order number
7. Tapping notification opens order detail screen for the delivered order

**Test Data:**
- User: TA-04 (e2e-existing@bookmyjuice.co.in / 9876543212)
- Order status before: shipped - after: delivered
- Notification title expected: contains Delivered
- Deep link payload: order ID or order detail route

---
### TC-E2E-NOT-006: Notification permission denied → app handles gracefully

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-006 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-060, BR-061, BR-062 |

**Preconditions:**
- [ ] Fresh app install or app data cleared
- [ ] Device running Android 13+ (API 33+) - notification permission is runtime-granted
- [ ] App is launched for the first time

**Test Steps:**
1. Clear app data / fresh install the BookMyJuice APK
2. Launch the app
3. When OS notification permission prompt appears, tap Deny
4. Complete login flow as existing user (TA-04)
5. After login, trigger a notification event (subscription pause per NOT-002)
6. Observe app behavior - check for crash, error dialog, or silent failure
7. Navigate to the notifications screen within the app (if available)
8. Close and re-launch the app - verify it works normally

**Expected Results:**
1. App launches successfully
2. OS dialog: Allow BookMyJuice to send notifications? - Deny/Allow
3. User taps Deny - permission denied
4. Login flow completes without notification-related errors
5. Subscription pause succeeds via API - no local notification in system tray
6. App does NOT crash, show error dialogs, or enter infinite loop
7. Notifications screen shows empty state or in-app list (not system notifications)
8. On re-launch, app starts normally without re-requesting permission

**Test Data:**
- User: TA-04 (e2e-existing@bookmyjuice.co.in)
- Android: 13+ (API 33+)
- Permission: POST_NOTIFICATIONS - denied
- Expected: Graceful degradation - app functions without system notifications

---
### TC-E2E-NOT-007: Notification tap → deep link to relevant screen (verify navigation)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-007 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-060, BR-061, BR-062 |
| **Linked UC** | UC-10, UC-11 |

**Preconditions:**
- [ ] User is logged in with an active subscription (TA-05)
- [ ] Notification permission granted on device
- [ ] LocalNotificationService initialized with onNotificationTap callback configured
- [ ] App is running in foreground mode
- [ ] Deep link navigation is configured for notification payload types

**Test Steps:**
1. Log in as TA-05 (active subscription)
2. Navigate to subscription management screen
3. Pause the subscription (per NOT-002)
4. Wait for local notification in system tray
5. Do NOT open app - pull down notification shade
6. Tap on the notification in system tray
7. Observe the screen that opens in the app

**Expected Results:**
1. User logs in successfully
2-4. Subscription pause completes - notification appears in tray
5. Notification shade shows BookMyJuice notification with title and body
6. Tapping notification opens app and navigates to relevant screen
7. Deep link navigates to correct contextual screen:
   - For subscription_paused - subscription detail management screen
   - Notification payload (type field) maps to correct route

**Test Data:**
- User: TA-05 (active subscription)
- Notification type payload: subscription_paused
- Expected navigation: /manage-subscriptions or subscription detail screen
- Deep link scheme: based on notification payload parameter

---
### TC-E2E-NOT-008: FCM token generated on app start

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-008 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual (requires real device) |
| **Linked BR** | BR-060, BR-062 |

**Preconditions:**
- [ ] Flutter APK built with Firebase config (google-services.json)
- [ ] App installed on physical Android device
- [ ] Device has internet connectivity
- [ ] FirebaseNotificationService initialized in main.dart
- [ ] Device does NOT have existing FCM token cached

**Test Steps:**
1. Clear app data to remove cached FCM token
2. Launch the BookMyJuice app
3. Allow notification permission if prompted
4. Log in as TA-04
5. Connect device to computer and capture Flutter debug logs
6. Search logs for FCM token obtained or FCM token
7. Navigate to authenticated screen to trigger uploadTokenToServer()
8. Check users table in DB for user fcm_token field

**Expected Results:**
1. App data cleared - no cached FCM token
2-3. App launches, Firebase initializes, permission requested/granted
4. Login flow completes successfully
5-6. Logs show FCM token obtained: ...
7. uploadTokenToServer() called (placeholder returns true)
8. If endpoint implemented: DB fcm_token column updated. If placeholder: logs confirm token available.

**Test Data:**
- User: TA-04 (e2e-existing@bookmyjuice.co.in)
- DB table: users - column: fcm_token
- Expected token format: ~150-200 char alphanumeric string
- Log string to search: FCM token obtained:

---
### TC-E2E-NOT-009: Multiple notifications stack correctly in notification tray

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-009 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-060, BR-061, BR-062 |

**Preconditions:**
- [ ] User logged in with subscription (TA-05) and at least one order
- [ ] Notification permission granted
- [ ] App is running
- [ ] LocalNotificationService initialized
- [ ] Multiple notification events can be triggered sequentially

**Test Steps:**
1. Log in as TA-05
2. Trigger subscription pause (NOT-002) - wait for notification
3. Without dismissing, trigger subscription resume (NOT-003)
4. Wait for second notification
5. If possible, trigger third event (order update via Chargebee admin)
6. Open notification shade to view stacked notifications
7. Expand notification group (if grouped)

**Expected Results:**
1. User logs in successfully
2. First notification (Subscription Paused) appears
3. Second notification (Subscription Resumed) appears without replacing first
4. Both notifications visible simultaneously
5. Third notification appears alongside first two
6. Stacked chronologically (newest at bottom or top per OS)
7. Each notification has unique ID - no collisions
8. Tapping any individual notification navigates to correct deep-link screen

**Test Data:**
- User: TA-05 (active subscription)
- Notification IDs: unique per event (messageId.hashCode or timestamp)
- Expected: all visible simultaneously with distinct titles/bodies
- Notification channel: bookmyjuice_channel

---
### TC-E2E-NOT-010: App in foreground → notification appears but does not duplicate

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-NOT-010 |
| **Module** | NOTIFICATIONS |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S2 — Minor |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-060, BR-061, BR-062 |

**Preconditions:**
- [ ] User logged in with active subscription (TA-05)
- [ ] Notification permission granted
- [ ] FirebaseNotificationService and LocalNotificationService initialized
- [ ] App actively running and visible (foreground)
- [ ] FirebaseMessaging.onMessage listener active

**Test Steps:**
1. Log in as TA-05
2. Keep app open and visible on screen
3. Trigger subscription pause (NOT-002)
4. Observe notification tray immediately after event
5. Observe app UI - check for in-app banner or toast
6. Pull down notification shade - check exactly ONE notification exists
7. Tap notification to navigate
8. Return to app - verify no duplicate UI elements

**Expected Results:**
1. User logs in successfully
2. App remains in foreground
3. Subscription pause completes via API
4. Local notification appears in system tray
5. App UI stable - no duplicate in-app banners. If snackbar shown, exactly ONE.
6. Notification shade: exactly ONE notification for this event - no duplicate
7. Tap navigates to correct subscription screen
8. Returning shows no leftover duplicate UI elements

**Test Data:**
- User: TA-05 (active subscription)
- App state: foreground
- Expected: 1 notification in tray for subscription_paused event
- Edge case: showNotification() called only once per event (idempotent)

---
