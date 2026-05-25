# BookMyJuice - Use Case Specifications

**Document Version:** 1.0 (Consolidated)
**Date:** April 11, 2026
**Linked to:** BRD_Business_Requirements.md, FUNCTIONAL_SPEC.md
**Status:** ✅ Approved for Development

---

## Table of Contents

1. [Overview](#1-overview)
2. [Actors](#2-actors)
3. [Use Cases - Authentication](#3-use-cases---authentication)
4. [Use Cases - Cart & Browsing](#4-use-cases---cart--browsing)
5. [Use Cases - Checkout](#5-use-cases---checkout)
6. [Use Cases - Subscription Management](#6-use-cases---subscription-management)
7. [Use Cases - Order Management](#7-use-cases---order-management)
8. [Use Cases - Notifications](#8-use-cases---notifications)
9. [Screen Flow Map](#9-screen-flow-map)

---

## 1. Overview

This document provides detailed use case specifications for the BookMyJuice platform. Each use case describes the interaction between actors and the system to achieve a specific goal.

### Use Case Categories

| Category | Use Cases | Description |
|----------|-----------|-------------|
| Authentication | UC-AUTH-001 to UC-AUTH-007c | User registration and login flows (incl. Firebase Phone Auth) |
| Cart & Browsing | UC-01 to UC-02 | Product browsing and cart management |
| Checkout | UC-03 to UC-04 | One-time and subscription checkout |
| Subscription | UC-05 to UC-07 | Subscription pause, resume, cancel |
| Order Management | UC-08 to UC-09 | Order history and invoice viewing |
| Notifications | UC-10, UC-11 | Push notification handling (incl. FCM) |

---

## 2. Actors

### Primary Actors

| Actor | Description |
|-------|-------------|
| **Guest User** | Unauthenticated user browsing products |
| **Registered User** | Authenticated user with account |
| **Google User** | User signing up with Google account |

### Secondary Actors

| Actor | Description |
|-------|-------------|
| **Email Service** | Sends verification codes (future: SendGrid, SES) |
| **SMS Service** | Sends OTP via SMS (future: Twilio, MSG91) |
| **Google Auth** | Provides OAuth authentication |
| **bmjServer** | Backend API handling all requests |
| **Chargebee** | Customer management and billing system |
| **FCM Push Server** | Sends push notifications to mobile app |

---

## 3. Use Cases - Authentication

### UC-AUTH-001: Email-First Signup

**Goal:** Create account starting with email verification

**Actor:** New User with email preference

**Preconditions:**
- User has valid email address
- User has valid 10-digit phone number
- User is not already registered

**Main Success Scenario (Updated for Dashboard-First):**

1. User opens app and sees **Dashboard (public mode)** with promotions, plans, juice catalog preview, and a "Sign In" prompt
2. User taps "Sign In" on Dashboard
3. System shows login/signup screen
4. User taps "Sign up with Email"
5. System displays email entry screen
>>>>>>> after
Wait, this won't work because the SEARCH text needs to exactly match. Let me re-read the file and craft precise replacements.<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="read_file">
4. User enters email address
5. User taps "Continue"
6. System sends 6-digit verification code to email
7. System displays code entry screen
8. User enters 6-digit code
9. User taps "Verify Email"
10. System validates code
11. System displays phone entry screen
12. User enters 10-digit phone number
13. User taps "Send OTP"
14. System sends 6-digit OTP to phone
15. System displays OTP entry screen
16. User enters 6-digit OTP
17. User taps "Verify OTP"
18. System validates OTP
19. System displays address entry screen
20. User enters all address fields (flat/house, society, area, city, state, ZIP, country)
21. User taps "Continue"
22. System displays password creation screen
23. User enters password meeting requirements
24. User confirms password
25. User taps "Create Account"
26. System validates all data
27. System creates user in database with BCrypt password hash
28. System creates Chargebee customer
29. System generates JWT token (30-day expiry)
30. System logs user in automatically
31. System navigates to dashboard with welcome message

**Extensions:**

- **5a. Invalid email format:**
  - System shows error: "Please enter a valid email"
  - User re-enters email → Resume at step 5

- **5b. Email already registered:**
  - System shows error: "Email is already registered"
  - System offers "Login" button
  - User can navigate to login or try different email

- **9a. Wrong verification code:**
  - System shows error: "Invalid or expired verification code"
  - User can retry or resend → Resume at step 8

- **9b. Code expired (10 minutes):**
  - System shows error: "Code expired"
  - User taps "Resend Code" (available after 30 seconds)
  - System sends new code, old code invalidated → Resume at step 8

- **17a. Wrong OTP:** Similar to 9a
- **20a. Missing required address field:** System highlights empty field with error message
- **25a. Password doesn't meet requirements:** Password validator shows failed requirements in red, submit disabled
- **25b. Passwords don't match:** System shows error: "Passwords do not match"
- **27a. Database error:** System logs error, shows "Failed to create account. Please try again."
- **28a. Chargebee customer creation fails:** System rolls back user creation, shows error

**Special Requirements:**
- Email verification code: 6 digits, 10-minute expiry
- Phone OTP: 6 digits, 10-minute expiry
- Resend available after 30 seconds
- Password: 8+ chars, uppercase, lowercase, 2 numbers, special char
- All data transmitted over HTTPS
- Maximum 5 resend attempts per email/phone

---

### UC-AUTH-002: Phone-First Signup

**Goal:** Create account starting with phone verification

**Actor:** New User with phone preference

**Main Success Scenario:**

1. User opens app and sees Dashboard (public mode) with promotions, plans, and a "Sign In" prompt
2. User taps "Sign In" on Dashboard, then taps "Sign up with Phone"
>>>>>>> after
Wait, this still doesn't match. Let me look at line 163.<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="read_file">
3. System displays phone entry screen
4. User enters 10-digit phone number
5. User taps "Send OTP"
6. System sends 6-digit OTP to phone
7. System displays OTP entry screen
8. User enters 6-digit OTP
9. User taps "Verify OTP"
10. System validates OTP
11. System displays email entry screen
12. User enters email address
13. User taps "Continue"
14. System sends 6-digit verification code to email
15. System displays code entry screen
16. User enters 6-digit code
17. User taps "Verify Email"
18. System validates code
19. System displays address entry screen
20. User enters all address fields
21. User enters password and confirms
22. System creates account, Chargebee customer, generates JWT
23. System logs user in, navigates to dashboard

**Extensions:** Similar to UC-AUTH-001, with phone/email order reversed

---

### UC-AUTH-003: Google Signup

**Goal:** Create account using Google authentication

**Actor:** New User with Google account

**Preconditions:**
- User has valid Google account
- User has valid 10-digit phone number
- User is not already registered with this email

**Main Success Scenario:**

1. User opens app and sees Dashboard (public mode) with promotions, plans, and a "Sign In" prompt
2. User taps "Sign In" on Dashboard, then taps "Sign up with Google"
3. System opens Google authentication
4. User selects Google account
5. Google returns verified email, name, and picture
6. System displays phone entry screen
7. System shows pre-filled email (read-only)
8. System shows pre-filled first name (editable)
9. System shows pre-filled last name (editable)
10. User enters 10-digit phone number
11. User taps "Send OTP"
12. System sends 6-digit OTP to phone
13. System displays OTP entry screen
14. User enters 6-digit OTP
15. User taps "Verify OTP"
16. System validates OTP
17. System displays address entry screen
18. User enters all address fields
19. User enters password and confirms
20. User taps "Create Account"
21. System creates account with Google email
22. System creates Chargebee customer
23. System generates JWT token
24. System logs user in, navigates to dashboard

**Extensions:**

- **3a. Google auth cancelled:** User cancels → System returns to signup method selection
- **4a. No Google account on device:** User adds Google account → Resume at step 4
- **10a. Phone already registered:** System shows error, offers "Login" button

**Special Requirements:**
- Google Sign-In plugin configured
- Email from Google is pre-verified (no email verification needed)
- Phone verification still required
- Name from Google is pre-filled but editable

---

### UC-AUTH-004: User Login

**Goal:** Authenticate user with email/password

**Actor:** Registered User

**Main Success Scenario:**

1. User opens app and sees Dashboard (public mode) with promotions, plans, and a "Sign In" prompt
2. User taps "Sign In" on Dashboard
3. System shows login screen
4. User enters email and password
5. User taps "Login"
6. System validates credentials (find user, verify BCrypt hash)
7. System generates JWT token (30-day expiry)
8. System stores token in SharedPreferences
9. System navigates to dashboard
10. On subsequent launches, auto-login checks token validity ONLY (no Google/phone)

**Note:** Username for login is the user's 10-digit phone number. The phone number serves as both the login identifier and the `username` field in the database.

**Extensions:**

- **4a. Invalid credentials:** System shows "Invalid email or password"
- **4b. Account locked (5 failed attempts):** System shows "Account locked, reset password"
- **8a. Token expired:** System clears token, shows Dashboard in public mode with toast notification: "Session expired. Please sign in again."

---

### UC-AUTH-005: Google Sign-In (Login Flow)

**Goal:** Sign in or start signup using Google account. Triggered ONLY when user taps Google button on login screen.

**Actor:** Guest User with Google account

**Preconditions:**
- User is on login screen (no valid JWT token)
- User has Google account configured on device

**Main Success Scenario (Existing User):**

1. User taps "Sign in with Google" button on login screen
2. System shows Google account picker dialog
3. User selects a Google account
4. Google returns verified email, name, and Google ID
5. System searches for user with matching Google ID or email
6. **User found:** System generates JWT token, stores in SharedPreferences, navigates to dashboard

**Alternate Flow (New User — Signup):**

5a. **User NOT found with Google ID or email:**
  5a1. System starts signup flow with pre-filled data
  5a2. System navigates to signup screen with:
    - Email pre-filled from Google (read-only)
    - First name pre-filled from Google (editable)
    - Last name pre-filled from Google (editable)
    - Google photo URL stored
  5a3. User continues signup: enters phone → verifies OTP → enters address → creates password
  5a4. System creates account, links Google ID, generates JWT
  5a5. System navigates to dashboard

**Extensions:**

- **3a. Google auth cancelled:** User dismisses picker → System stays on login screen
- **4a. No Google account on device:** User adds Google account → Resume at step 3
- **6a. Google login fails (network error):** System shows error → User retries or uses other login methods

**Special Requirements:**
- Google Sign-In plugin configured with correct SHA-1 and client ID
- Email from Google is pre-verified (no email verification needed during signup)
- Phone verification still required for new users
- Name from Google is pre-filled but editable

---

### UC-AUTH-006: Phone Sign-In (Login Flow)

**Goal:** Sign in or start signup using phone number. Triggered ONLY when user taps Phone button on login screen.

**Actor:** Guest User

**Preconditions:**
- User is on login screen (no valid JWT token)
- User has a valid 10-digit Indian phone number

**Main Success Scenario (Existing User):**

1. User taps "Sign in with Phone" button on login screen
2. System displays phone number entry screen
3. User enters 10-digit phone number
4. User taps "Send OTP"
5. System sends 6-digit OTP to phone
6. System displays OTP entry screen
7. User enters 6-digit OTP
8. User taps "Verify OTP"
9. System validates OTP
10. System searches for user with matching verified phone number
11. **User found:** System generates JWT token, stores in SharedPreferences, navigates to dashboard

**Alternate Flow (New User — Signup):**

10a. **User NOT found with verified phone:**
  10a1. System starts signup flow with pre-filled data
  10a2. System navigates to signup screen with:
    - Phone pre-filled from verified OTP (read-only)
  10a3. User continues signup: enters email → verifies email code → enters address → creates password
  10a4. System creates account, generates JWT
  10a5. System navigates to dashboard

**Extensions:**

- **4a. Invalid phone format:** System shows "Please enter a valid 10-digit Indian number" → User re-enters
- **8a. Invalid OTP:** System shows "Invalid or expired OTP" → User retries or resends
- **8b. OTP expired (10 minutes):** System shows "OTP expired" → User requests new OTP
- **10a. Phone already registered:** See Alternate Flow above
- **11a. Phone login fails (network error):** System shows error → User retries

**Special Requirements:**
- OTP: 6 digits, 10-minute expiry
- Resend available after 30 seconds
- Maximum 5 resend attempts per phone
- Maximum 3 verification attempts per OTP
- Phone format: 10-digit Indian number

---

### UC-AUTH-007a: Firebase Phone Auth — Alternative Phone Verification (Signup)

**Goal:** Verify phone number using Firebase Phone Auth as an alternative to backend OTP during signup

**Actor:** New User

**Preconditions:**
- User has selected phone signup flow
- User has valid 10-digit Indian phone number
- Firebase Authentication is configured with Phone sign-in method enabled

**Main Success Scenario:**

1. User enters phone number on Phone Entry screen
2. User taps "Verify via Firebase" button (OutlinedButton.icon, blue)
3. System formats phone to E.164 format (+919876543210)
4. System calls `FirebasePhoneAuth.instance.initiatePhoneVerification()`
5. Firebase sends SMS with 6-digit verification code
6. System navigates to OTP Verification screen with `isFirebaseAuth: true` and `verificationId`
7. User enters 6-digit SMS code
8. System calls `FirebasePhoneAuth.instance.verifyPhoneOtp(code)`
9. Firebase verifies code successfully
10. System dispatches `VerifyFirebaseOtp` event to BLoC
11. BLoC emits `FirebasePhoneVerified` state
12. System displays "Phone Verified via Firebase" toast
13. If email-first flow: system navigates to Address Entry screen
14. If phone-first flow: system navigates to Email Entry screen

**Extensions:**

- **4a. Firebase Auth network error:** System shows error toast, user retries or uses backend OTP
- **6a. SMS delivery timeout (60s):** System shows timeout toast, user taps "Resend" to retry
- **8a. Invalid/expired verification code:** System shows error toast, user re-enters code
- **10a. Firebase verification fails:** BLoC emits `FirebasePhoneVerificationFailed`, error toast shown

**Special Requirements:**
- Phone must be in E.164 format (+91XXXXXXXXXX) for Firebase
- Firebase Phone Auth operates independently from backend OTP
- Backend authentication still occurs via `POST /api/auth/login-otp` for login flow
- No Chargebee or backend changes needed for Firebase Phone verification itself

---

### UC-AUTH-007b: Firebase Phone Auth — Alternative Phone Verification (Login)

**Goal:** Verify phone number using Firebase Phone Auth during login flow, then authenticate via backend

**Actor:** Registered User

**Preconditions:**
- User is on Phone Login screen
- User has a registered account with the given phone number
- Firebase Authentication is configured with Phone sign-in method enabled

**Main Success Scenario:**

1. User enters phone number on Phone Login screen
2. User taps "Verify via Firebase" button
3. System formats phone to E.164 and initiates Firebase verification
4. Firebase sends SMS with verification code via `initiatePhoneVerification()`
5. System navigates to OTP Verification screen with `isFirebaseAuth: true`, `isLoginFlow: true`
6. User enters SMS code
7. On successful Firebase verification, BLoC emits `FirebasePhoneVerified`
8. System shows "Phone Verified" toast, navigates back to login screen
9. User enters email/password to authenticate via backend

**Alternate Flow (User not found):**
- Firebase phone verification succeeds
- System calls `POST /api/auth/login-otp` to check if phone exists
- Backend returns `user_not_found`
- System redirects to signup flow with pre-filled phone

---

### UC-AUTH-007c: Resend Verification Code

**Goal:** Request new verification code when original is lost/expired

**Actor:** User in signup flow

**Preconditions:**
- User has requested verification code
- 30 seconds have elapsed since last code sent

**Main Success Scenario:**

1. User is on verification code entry screen
2. User waits for code (doesn't arrive)
3. User sees "Resend Code" button (enabled after 30 seconds)
4. User taps "Resend Code"
5. System invalidates old code
6. System generates new 6-digit code
7. System sends new code to email/phone
8. System shows success message: "Verification code resent"
9. User enters new code
10. User taps "Verify"
11. System validates new code
12. User proceeds to next step

**Extensions:**

- **4a. User taps resend before 30 seconds:** Button disabled, countdown timer shows remaining seconds
- **11a. New code also fails:** After 3 failed attempts, suggest different email/phone

---

## 4. Use Cases - Cart & Browsing

### UC-01: Guest Browsing & Cart Building

**Actor:** Guest User

**Precondition:** None

**Main Success Scenario:**

1. Guest opens app → browses product catalog on Home screen
2. Guest taps product → views Product Detail screen
3. Guest taps "Add to Cart" → item added with quantity 1
4. Guest adds more items → cart type locked to first item type (one-time or subscription)
5. Guest opens Cart screen → sees items + pricing breakdown (subtotal, tax, delivery fee from Chargebee, grand_total)
6. Guest modifies quantities or removes items

**Postcondition:** Guest cart persisted in SharedPreferences + bmjServer with `user_id = NULL`

**Alternate Flow:** Guest tries to add opposite-type item → `409` returned → mobile prompts to clear cart and switch type → guest confirms → cart cleared, new item added

---

### UC-02: Guest Login & Cart Merge

**Actor:** Registered User (was guest)

**Precondition:** Guest has items in cart; user has an existing server-side cart

**Main Success Scenario:**

1. Guest taps "Login" → enters credentials → receives JWT
2. Mobile calls `POST /api/v1/cart/merge` with `{ "guest_cart_id": "cart_guest_123" }`
3. bmjServer detects both guest and auth carts exist with **different types**
4. bmjServer returns `409 Conflict` with `{ "user_cart_type": "subscription", "guest_cart_type": "onetime" }`
5. Mobile shows dialog: "You have items in both your guest cart and saved cart. Which would you like to keep?"
6. User selects "Guest Cart"
7. Mobile calls `POST /api/v1/cart/merge` again with `{ "guest_cart_id": "cart_guest_123", "keep": "guest" }`
8. bmjServer deletes auth cart, reassigns guest cart items to user
9. Mobile navigates to Cart screen showing guest cart items

**Postcondition:** User has single cart of chosen type; discarded cart deleted

**Alternate Flows:**
- Same cart types → items merged automatically; duplicates take higher quantity
- No existing auth cart → guest cart simply reassigned

---

## 5. Use Cases - Checkout

### UC-03: One-Time Purchase Checkout

**Actor:** Authenticated User

**Precondition:** Cart has one-time items, user is logged in

**Main Success Scenario:**

1. User taps "Proceed to Checkout" on Cart screen
2. Mobile calls `POST /api/v1/checkout/initiate` with cart contents
3. bmjServer calls Chargebee `POST /api/v2/hosted_pages/checkout_new_for_items` with `subscription_items` (charge-type items only)
4. Chargebee returns `{ hosted_page: { id: "hp_xxx", url: "https://..." } }`
5. bmjServer creates checkout session, returns `{ checkout_session_id: "cs_xxx", hosted_page_url: "https://..." }`
6. Mobile opens Payment WebView with the URL
7. User completes payment on Chargebee-hosted page
8. Chargebee redirects to `redirect_url?id=hp_xxx&state=succeeded`
9. Mobile calls `POST /api/v1/checkout/complete { checkout_session_id: "cs_xxx", hosted_page_id: "hp_xxx" }`
10. bmjServer retrieves hosted page from Chargebee, syncs order/invoice/payment to MySQL
11. bmjServer clears user's cart, returns `{ order_id: "ord_xxx", status: "pending" }`
12. Mobile navigates to Order Confirmation screen
13. Mobile calls `GET /api/v1/orders/ord_xxx` to fetch confirmed state
14. Mobile displays confirmed order details

**Postcondition:** Order created in MySQL; cart cleared; push notification sent on payment failure (if any)

---

### UC-04: Subscription Purchase Checkout

**Actor:** Authenticated User

**Precondition:** Cart has subscription items, user is logged in, no conflicting active subscription for same plan

**Main Success Scenario:** Same as UC-03, but:
- `subscription_items` includes a `plan`-type item at index 0
- After checkout complete, bmjServer creates both order AND subscription records
- Response includes `{ order_id: "ord_xxx", subscription_id: "sub_xxx", status: "active" }`
- Mobile navigates to Order Confirmation → shows subscription info: "Your subscription is active. Next delivery: [date]"

**Postcondition:** Order + subscription created in MySQL; cart cleared

---

## 6. Use Cases - Subscription Management

### UC-05: Pause Subscription

**Actor:** Authenticated User

**Precondition:** User has an active subscription; current time < 9 PM local

**Main Success Scenario:**

1. User opens Subscription Detail screen
2. User taps "Pause Subscription" button
3. Mobile shows confirmation dialog: "Pause delivery starting [date]? You can resume anytime."
4. User confirms
5. Mobile calls `POST /api/v1/subscriptions/:id/pause`
6. bmjServer checks time — it's before 9 PM → proceeds
7. bmjServer calls Chargebee `POST /api/v2/subscriptions/{cb_sub_id}/pause` with `{ "pause_date": "<next_delivery_utc>", "billing_cycles": 1 }`
8. Chargebee returns `200 OK` with updated subscription
9. bmjServer updates MySQL subscription record → status = `paused`
10. bmjServer returns `202 Accepted { "message": "Pause scheduled. Refetch subscription status." }`
11. Mobile calls `GET /api/v1/subscriptions/:id` → receives confirmed `paused` status
12. Mobile updates UI: status badge changes to orange "Paused"
13. bmjServer sends push notification: "Your [plan] subscription has been paused."

**Postcondition:** Subscription paused in Chargebee + MySQL; push notification sent

**Alternate Flow:** Time >= 9 PM → bmjServer returns `400` → mobile shows "Actions available until 9 PM. Changes will take effect next day."

---

### UC-06: Resume Subscription

**Actor:** Authenticated User

**Precondition:** User has a paused subscription; current time < 9 PM local

**Main Success Scenario:**

1. User opens Subscription Detail screen → sees "Paused" status
2. User taps "Resume Subscription" button
3. Mobile shows confirmation dialog: "Resume your subscription starting immediately?"
4. User confirms
5. Mobile calls `POST /api/v1/subscriptions/:id/resume`
6. bmjServer checks time — before 9 PM → proceeds
7. bmjServer calls Chargebee `POST /api/v2/subscriptions/{cb_sub_id}/resume` with `{ "resume_option": "immediately", "charges_handling": "add_to_unbilled_charges" }`
8. Chargebee returns `200 OK` with updated subscription
9. bmjServer updates MySQL → status = `active`
10. bmjServer returns `202 Accepted`
11. Mobile calls `GET /api/v1/subscriptions/:id` → receives confirmed `active` status
12. Mobile updates UI: status badge changes to green "Active"
13. bmjServer sends push notification: "Your [plan] subscription is active again."

**Postcondition:** Subscription resumed in Chargebee + MySQL; push notification sent

---

### UC-07: Cancel Subscription

**Actor:** Authenticated User

**Precondition:** User has an active or paused subscription

**Main Success Scenario:**

1. User opens Subscription Detail screen
2. User taps "Cancel Subscription" button
3. Mobile shows dialog with cancel options: "Immediately", "End of Term", "Specific Date"
4. User selects "End of Term" → confirms
5. Mobile calls `POST /api/v1/subscriptions/:id/cancel { "cancel_option": "end_of_term" }`
6. bmjServer calls Chargebee `POST /api/v2/subscriptions/{cb_sub_id}/cancel_for_items` with `{ "cancel_option": "end_of_term" }`
7. Chargebee returns `200 OK` with `cancelled_at` set to end of current term
8. bmjServer updates MySQL → status updated, `scheduled_cancellation_at` set
9. bmjServer returns `202 Accepted`
10. Mobile calls `GET /api/v1/subscriptions/:id` → receives confirmed state with cancellation scheduled
11. Mobile shows "Cancellation scheduled for [date]" banner + "Remove Scheduled Cancellation" button
12. When Chargebee processes cancellation → webhook `subscription_cancelled` fires → bmjServer updates status to `cancelled` → push notification sent

**Postcondition:** Cancellation scheduled in Chargebee + MySQL; push notification sent when cancellation executes

**Alternate Flow:** User taps "Remove Scheduled Cancellation" → `POST /api/v1/subscriptions/:id/remove-scheduled-cancellation` → cancellation removed → banner disappears

---

## 7. Use Cases - Order Management

### UC-08: View Order History

**Actor:** Authenticated User

**Precondition:** User has placed at least one order

**Main Success Scenario:**

1. User opens Order History screen
2. Mobile calls `GET /api/v1/orders?page=1&per_page=20`
3. bmjServer queries MySQL → returns paginated order list
4. Mobile displays orders as scrollable list with status badges (pending, confirmed, shipped, delivered, cancelled)
5. User scrolls down → mobile calls `GET /api/v1/orders?page=2` for next batch
6. User taps an order → navigates to Order Detail screen

**Postcondition:** Orders displayed with confirmed status from MySQL

---

### UC-09: View Invoice

**Actor:** Authenticated User

**Precondition:** User has a delivered order with an invoice

**Main Success Scenario:**

1. User opens Order Detail screen for a delivered order
2. User taps "View Invoice" button
3. Mobile calls `GET /api/v1/orders/:id/invoice`
4. bmjServer returns `{ "invoice_url": "https://[site].chargebee.com/invoices/inv_xxx", "invoice_id": "inv_xxx", "amount": 3776, "generated_at": "2026-04-08T10:30:00Z" }`
5. Mobile opens the Chargebee URL in in-app browser

**Postcondition:** Invoice displayed via Chargebee-hosted page

---

## 8. Use Cases - Notifications

### UC-10: Push Notification Deep Link

**Actor:** Authenticated User (app in background or closed)

**Precondition:** User has registered FCM token

**Main Success Scenario:**

1. Chargebee webhook `payment_failed` arrives at bmjServer
2. bmjServer processes webhook → updates payment record → looks up user's FCM tokens
3. bmjServer sends FCM push: `{ title: "Payment Failed", body: "Your payment of ₹37.76 could not be processed.", data: { type: "payment_failed", order_id: "ord_xxx" } }`
4. User taps notification → mobile app opens
5. Mobile reads deep-link data → navigates to Order Detail screen for `ord_xxx`
6. Mobile calls `GET /api/v1/orders/ord_xxx` → displays confirmed order state with `payment_status: failed`

**Postcondition:** User sees failed order details and can retry payment or contact support

### UC-11: FCM Foreground Notification Display

**Goal:** Display FCM push notifications as local notifications when app is in foreground

**Actor:** Authenticated User (app in foreground)

**Precondition:**
- User is logged in and app is open
- User has granted notification permission
- FCM token has been registered and optionally uploaded to backend

**Main Success Scenario:**

1. Server sends FCM push notification to user's device
2. `FirebaseMessaging.onMessage` fires in the app with the notification payload
3. `FirebaseNotificationService` receives the remote message
4. Service extracts `notification.title`, `notification.body`, and `data` payload
5. Service checks if `notification` is non-null
6. Service displays notification using `LocalNotificationService`
7. Flutter `flutter_local_notifications` plugin shows the notification in the system tray
8. User taps the notification → app reads `data` payload for deep-link navigation
9. If `data` contains `type` and relevant IDs, app navigates to the appropriate screen

**Extensions:**

- **4a. Notification payload has no title/body:** Service falls back to a default message: "New update from BookMyJuice"
- **4b. No data payload:** Notification is displayed as a generic notification without deep-link capability
- **7a. User taps notification while app is in foreground:** App handles the tap and can navigate based on data payload
- **8a. Notification permission not granted:** Service requests permission again on next app launch

**Special Requirements:**
- FCM is a secondary layer on top of the existing `flutter_local_notifications` setup
- `FirebaseMessaging.onBackgroundMessage` handler is registered at app startup for background notifications
- FCM token is refreshed via `onTokenRefresh` stream and stored locally
- Backend integration for `uploadTokenToServer()` is a placeholder for future FCM token sync
- Notification permission is requested with `alert: true, badge: true, sound: true` for iOS

---

## 9. Screen Flow Map

```
┌─────────────────────┐
│  Splash Screen      │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────┐
│  Dashboard (Public Mode)         │
│  ├─ Promotions / Catalog Preview │
│  ├─ Subscription Plans           │
│  ├─ Juice Catalog                │
│  └─ [Sign In] prompt             │
└──────┬──────────────────────┬────┘
       │                      │
       │ Tap "Sign In"        │ Auto-login succeeds
       ▼                      ▼
┌──────────────────┐  ┌─────────────────────┐
│ Login / Signup   │  │  Dashboard          │
│ Selection Screen │  │  (Full/Authenticated)│
└──────┬───────────┘  ├─ Subscription       │
       │              ├─ Quick Actions      │
       │              └─ Navigation         │
       │                  │                 │
    ┌──┼──┐               │                 │
    │  │  │               │                 │
    ▼  ▼  ▼               │                 │
┌────┐┌──┐┌────┐         │                 │
│Email││Ph││Google│        │                 │
│Signp││ne││Signup│       │                 │
│     ││Sg││      │       │                 │
└──┬──┘│np│└──┬───┘       │                 │
   │   │up│    │           │                 │
   │   └──┘    │           │                 │
   ▼          ▼           │                 │
   ┌──────────────┐       │                 │
   │OTP / Code    │       │                 │
   │ Verification │       │                 │
   └──────┬───────┘       │                 │
          │               │                 │
          ▼               │                 │
   ┌──────────────┐       │                 │
   │ Address+Pwd  │       │                 │
   │ Entry        │       │                 │
   └──────┬───────┘       │                 │
          │               │                 │
          ▼               ▼                 │
   ┌──────────────────────────────────┐     │
   │  Dashboard (Full/Authenticated)  │◄────┘
   │  ├─ Subscription                 │
   │  ├─ Quick Actions                │
   │  └─ Navigation                   │
   └──────┬───────────────────────────┘
          │
   ┌──────┼────────┬─────────────┐
   │      │        │             │
   ▼      ▼        ▼             ▼
┌──────┐ ┌──────┐ ┌────────┐ ┌────────┐
│Home/ │ │ Cart │ │ Orders │ │ Profile│
│Menu  │ │      │ │        │ │        │
└──┬───┘ └──┬───┘ └───┬────┘ └────────┘
   │        │         │
   ▼        ▼         ▼
┌────────┐ ┌────────┐ ┌──────────┐
│Product │ │Checkout│ │Order     │
│Detail  │ │WebView │ │Detail    │
└────────┘ └────────┘ └──────────┘
```

---

**Document Control:**
- **Created:** April 11, 2026 (Consolidated from UNIFIED_SIGNUP_USE_CASES.md and BOOKMYJUICE_SPECIFICATION.md)
- **Updated:** May 25, 2026 (Dashboard-First Landing: Updated UC-AUTH-001/002/003/004 flow steps and Screen Flow Map)
- **Version:** 1.2
- **Status:** ✅ Updated for Dashboard-First Flow
