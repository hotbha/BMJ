# BookMyJuice Bug Registry

> **Last Updated:** 2026-05-25  

> **Owner:** QA Engineering

## Severity Definitions

- 🔴 **Critical** = security breach, app down, auth bypass, data corruption, production outage
- 🟠 **Major** = core feature broken, checkout blocked, slot booking broken, subscription command broken
- 🟡 **Minor** = partial feature issue, incorrect message, non-blocking UX issue
- 🟢 **Trivial** = typo, spacing, cosmetic-only issue

## Bug Statuses

- 🆕 New
- 🔍 Investigating
- 🔨 In Fix
- ✅ Fixed
- 🔁 Regression
- 🚫 Won't Fix

---

## Open Bugs

_No open bugs. All reported bugs have been resolved._

---

## Resolved Bugs

| BUG-ID | Title | Module | Severity | Priority | Status | Fix Commit | Linked TC | Reported By | Fixed By |
|--------|-------|--------|----------|----------|--------|------------|-----------|-------------|----------|
| BUG-001 | IdempotencyService.java has duplicated/corrupt code at end of file | Webhook | 🟠 Major | High | ✅ Fixed | 73bd082 | TC-WEB-001 | Code Review | System |
| BUG-008 | Subscription service calls wrong endpoint path – `GET /api/subscriptions` causes 404 | SUBSCRIPTIONS (Flutter Service) | 🟠 Major | High | ✅ Fixed | Current | TC-XMOD-001 (Step 6) | Manual E2E | System |
| BUG-002 | auth_bloc_test.dart uses stale `googleSignIn_()` reference | AUTH (Flutter Test) | 🟡 Minor | Medium | ✅ Fixed | Current | TC-AUTH-BLOC-001 | Test Suite | System |
| BUG-003 | login_page_test.dart uses stale `toast_message`/`toast_heading` references | AUTH (Flutter Test) | 🟡 Minor | Medium | ✅ Fixed | Current | TC-LOGIN-PAGE-001 | Test Suite | System |
| BUG-004 | `VerifyOTP` event missing `phone` field — OTP verification fails in signup flow | AUTH (Phone OTP) | 🔴 Critical | High | ✅ Fixed | Current | TC-XMOD-001, TC-AUTH-SG-001 | Manual E2E (XMOD-001) | System |
| BUG-005 | Null cast crash in `address_entry_screen.dart` — null cast fails `as String` | AUTH (Signup Address) | 🟠 Major | High | ✅ Fixed | Current | TC-XMOD-001 | Manual E2E (XMOD-001) | System |
| BUG-006 | Signup doesn't save delivery address to `user_addresses` table — checkout can't find it | AUTH (Signup / Checkout) | 🟠 Major | High | ✅ Fixed | Current | TC-XMOD-001 | Manual E2E (XMOD-001) | System |
| BUG-007 | All subscription navigation points in dashboard redirect to deprecated Chargebee hosted pages (410 GONE) | UI (Dashboard / Navigation) | 🟠 Major | High | ✅ Fixed | Current | PHONE-006, XMOD-001 | Manual E2E (XMOD-001) | System |

**BUG-001 Details:**
- **Environment:** All (source code)
- **Platform:** Java 17 / Spring Boot
- **Steps to Reproduce:** Open IdempotencyService.java — observe duplicate `cleanupExpiredEvents()` method and broken `processedEvents` HashMap code after the closing brace of the `ProcessingStats` class.
- **Expected:** Clean file with no duplicate code.
- **Actual:** The file had orphan methods (`getTrackedEventCount()`, `clearAllEvents()`) duplicated after the closing brace of the class, referencing non-existent `processedEvents` field which was not declared at class level.
- **Root Cause:** Prior edits appended code after the class closing brace instead of integrating into the class body.
- **Resolution:** Rewrote entire file with `processedEvents` as a class-level `ConcurrentHashMap` and all methods properly scoped inside the class.

**BUG-002 Details:**
- **Environment:** Flutter test suite (lush/test/unit/bloc/auth_bloc_test.dart)
- **Platform:** Dart 3.x / Flutter
- **Steps to Reproduce:** Run `flutter test` — test file fails compilation at 5 references to `googleSignIn_()`.
- **Expected:** Tests compile and pass.
- **Actual:** Method `googleSignIn_()` was renamed to `googleSignIn()` in `user_repository.dart` during analyzer fixes (Phase 1.1), but test file references were not updated.
- **Root Cause:** Stale references in test file after rename operation in source file.
- **Resolution:** Updated all 5 occurrences of `googleSignIn_()` → `googleSignIn()` in auth_bloc_test.dart.

**BUG-003 Details:**
- **Environment:** Flutter test suite (lush/test/widget/screens/login_page_test.dart)
- **Platform:** Dart 3.x / Flutter
- **Steps to Reproduce:** Run `flutter test` — test file fails compilation due to `toast_message` and `toast_heading` references.
- **Expected:** Tests compile and pass.
- **Actual:** Properties `toast_message` and `toast_heading` were renamed to `toastMessage` and `toastHeading` during analyzer fixes, but test file references were not updated.
- **Root Cause:** Stale references in test file after rename operation in source file (login_page.dart).
- **Resolution:** Updated `toast_message` → `toastMessage` and `toast_heading` → `toastHeading` in login_page_test.dart.

**BUG-004 Details:**
- **Environment:** Flutter app on Android (OnePlus) against local Docker backend
- **Platform:** Dart 3.x / Flutter (phone_otp_verification_screen.dart → auth_bloc.dart → user_repository.dart)
- **Steps to Reproduce:**
  1. Open app → Navigate to Sign Up tab → Select "Sign up with Email"
  2. Enter email → Verify email code successfully
  3. Enter 10-digit phone number → OTP sent successfully (backend log shows 200)
  4. Enter correct 6-digit OTP received via SMS → Tap "Verify OTP"
  5. ⚠️ OTP verification fails with generic error toast
- **Expected:** OTP verification succeeds, user proceeds to address entry screen
- **Actual:** Backend returns 400 BAD_REQUEST with `"Phone number is required"` because the phone field is empty in the request body
- **Root Cause (3-layer gap):**
  1. `VerifyOTP` event class (`auth_events.dart:97-104`) only has `otp: String` — missing `phone` field entirely
  2. `phone_otp_verification_screen.dart:125-127` dispatches `VerifyOTP(otp: otp)` without phone — even though `_phone` is available locally
  3. `auth_bloc.dart:158` calls `userRepository.verifyOTP(event.otp)` without phone — falls back to `userRepository.user.getPhone` which is empty in signup flow
- **Resolution:** Added `phone` field to `VerifyOTP` event class, passed it from the screen, and used it in the BLoC handler.

**BUG-005 Details:**
- **Environment:** Flutter app on Android (OnePlus) against local Docker backend
- **Platform:** Dart 3.x / Flutter (phone_otp_verification_screen.dart → address_entry_screen.dart)
- **Steps to Reproduce:**
  1. Open app → Navigate to Sign Up tab → Select "Sign up with Email"
  2. Enter email → Verify email code
  3. Enter 10-digit phone number → Receive OTP → Enter OTP → Tap "Verify OTP"
  4. OTP succeeds ("Phone Verified" toast appears)
  5. ⚠️ App immediately crashes with red screen and error: `type 'Null' is not a subtype of type 'String' in the cast`
- **Expected:** After OTP verification, user navigates to address entry screen to enter shipping address and password.
- **Actual:** App crashes during navigation to `/address-entry`.
- **Root Cause:** `phone_otp_verification_screen.dart` passes `'firstName': null, 'lastName': null` in route arguments (lines 265-266) for non-Google signup flows. `address_entry_screen.dart` does hard casts with `args['email'] as String` (line 44-47), which throws `'Null' is not a subtype of type 'String'` when the value is null.
- **Resolution (applied):** Changed `as String` to `as String?` on `_email`, `_phone`, `_firstName`, and `_lastName` assignments in `address_entry_screen.dart`. APK rebuilt and installed.
- **Workaround:** Use Google Sign-In which provides non-null firstName/lastName.

**BUG-006 Details:**
- **Environment:** Backend (bmjServer) running in Docker against MySQL 8.0
- **Platform:** Java 17 / Spring Boot 3.x / JPA (Hibernate)
- **Steps to Reproduce:**
  1. Complete a full signup via `POST /api/auth/unified-signup` with valid address fields
  2. Backend returns 200 OK, user is created in `users` table
  3. Check `user_addresses` table — no row exists for the newly created user
  4. Attempt checkout — the checkout flow queries `user_addresses` for delivery address and finds none, causing checkout failure
- **Expected:** After successful signup with address fields, a corresponding row should exist in `user_addresses` table for the user.
- **Actual:** `unifiedSignup()` in `AuthController.java` saves the user to the `users` table (including address columns) but never creates a `UserAddressEntity` row. The checkout flow depends on the `user_addresses` table for delivery addresses.
- **Root Cause:** The `unifiedSignup()` method (lines 455-690) handles address fields from the request and stores them on the `User` entity, but never syncs to the `user_addresses` table. This is a separate table with its own `UserAddressEntity` repository used by the checkout module.
- **Resolution:** Added code block at lines 662-684 in `AuthController.java` that creates a `UserAddressEntity` with label "Home", the user's full name, phone, and all address fields from the request. Saved via `userAddressRepository.save()`. If this save fails, it logs a warning but does not fail the signup (non-blocking — user can add addresses later).
- **Backend deployment:** Container already running — fix is in the source code; requires container rebuild to take effect.

**BUG-007 Details:**
- **Environment:** Flutter app (lush) — all screens that navigate to subscription-related pages
- **Platform:** Dart 3.x / Flutter (dashboard.dart, subscription_management_screen.dart)
- **Steps to Reproduce (4 navigation points):**
  1. Open app → Dashboard loads subscription info card → Tap "Manage" button → ⚠️ Routes to Chargebee WebView (410 GONE)
  2. Open drawer → Tap "Subscriptions" → ⚠️ Routes to Chargebee WebView (410 GONE)
  3. Open bottom nav bar → Tap "Plans" → ⚠️ Routes to Chargebee WebView (410 GONE)
  4. Tap "Special Offer" promotion card "Get Now" button → ⚠️ Routes to Chargebee WebView (410 GONE)
- **Expected:** All subscription-related navigation should redirect to the native subscription management screen at `/manage-subscriptions`.
- **Actual:** All 4 navigation points redirect to `subscription_screen.dart` (deprecated Chargebee hosted pricing page WebView) which returns 410 GONE from Chargebee.
- **Root Cause:** The Chargebee hosted pricing page URL (`https://bookmyjuice-test.chargebee.com/hosted_pages/plans`) returns 410 GONE because the product catalog is managed natively. Per `NATIVE_BILLING_FLOW.md`: all plan discovery and management is native — only payment is Chargebee hosted checkout.
- **Resolution:** Updated all 4 navigation points in `dashboard.dart`:
  1. `_navigateToSubscriptions()` method → now calls `Navigator.pushNamed(context, '/manage-subscriptions')`
  2. `onManageTap` callback in SubscriptionInfoCard → now calls `Navigator.pushNamed(context, '/manage-subscriptions')`
  3. Drawer "Subscriptions" item → now calls `Navigator.pushNamed(context, '/manage-subscriptions')`
  4. Bottom nav bar "Plans" item → now calls `Navigator.pushNamed(context, '/manage-subscriptions')`
- **Note:** APK has not been rebuilt yet with this fix. The source changes are applied but not deployed to the phone.

**BUG-008 Details:**
- **Environment:** Flutter app (lush) — subscription_management_screen.dart calls subscription_service.dart
- **Platform:** Dart 3.x / Flutter (subscription_service.dart → subscription_management_screen.dart)
- **Steps to Reproduce:**
  1. Complete signup flow → Dashboard loads → Tap "Plans" or subscription "Manage" button
  2. Native "My Subscriptions" screen opens with heading "My Subscriptions"
  3. ⚠️ Center of screen shows error: `Error: Failed to load subscriptions: 404` with a Retry button
- **Expected:** Screen shows list of user's subscriptions (or "No active subscriptions" message with Browse Plans button)
- **Actual:** 404 error displayed because the service calls `GET /api/subscriptions` but backend only responds to `GET /api/subscriptions/my`
- **Root Cause (2 issues):**
  1. `subscription_service.dart:50` calls `GET /api/subscriptions` — backend endpoint is `@GetMapping("/my")` → full path is `GET /api/subscriptions/my`
  2. `subscription_service.dart:56` parses `data['data']` — backend returns data under the `data['subscriptions']` key
- **Resolution:**
  1. Changed URL from `$baseUrl/api/subscriptions` → `$baseUrl/api/subscriptions/my`
  2. Changed response parsing from `data['data']` → `data['subscriptions']`
- **Note:** APK rebuild required to deploy this fix to the phone.

---

## Known Non-Bugs

| Issue | Rationale |
|-------|-----------|
| AuthController signup returns 500 in unit test | Expected — Chargebee static methods can't be mocked in simple JUnit tests. Integration tests with real/mocked Chargebee resolve this. |
| CheckoutController returns 400 in unit tests | Expected — Chargebee HostedPage static methods require live or mocked API. |

## Bug Metrics

- **Total reported:** 8
- **Open:** 0
- **Fixed:** 8
- **Won't Fix:** 0
- **Critical:** 1
- **Major:** 5
- **Minor:** 2
