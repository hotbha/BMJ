# E2E Black Box Testing — Prerequisites & Human Intervention Requirements

> **Document Version:** 1.0  
> **Last Updated:** 2026-05-18  
> **Purpose:** List ALL environment setup, accounts, data preparation, and manual steps required before any test case can be executed. These items **cannot** be automated and require human action.

---

## Section 1: Infrastructure & Environment

### 1.1 Backend Server (bmjServer)

| # | Item | Required For | Status | Owner |
|---|------|-------------|--------|-------|
| P-01 | bmjServer deployed to staging environment with public URL (e.g., `https://staging-api.bookmyjuice.co.in`) | ALL API tests | 🔴 Must Do | DevOps |
| P-02 | MySQL 8.0+ database running with Flyway migrations applied (V1→V5) | ALL tests | 🔴 Must Do | DevOps |
| P-03 | `.env` file configured on staging server with all secrets: `CHARGEBEE_SITE`, `CHARGEBEE_API_KEY`, `JWT_SECRET`, `MAIL_*`, `GOOGLE_CLIENT_ID`, `DB_*`, `WEBHOOK_*` | ALL tests | 🔴 Must Do | DevOps |
| P-04 | Redis server running (required for cache fallback tests) | CACHE, BILLING | 🟡 Nice to Have | DevOps |
| P-05 | SMTP mail server configured with verified sender email | AUTH (email verification) | 🔴 Must Do | Admin |
| P-06 | Health endpoint accessible: `GET /api/health` returns 200 | Smoke test | 🔴 Must Do | DevOps |

### 1.2 Chargebee Test Site

| # | Item | Required For | Status | Owner |
|---|------|-------------|--------|-------|
| P-07 | Chargebee test site created (e.g., `bookmyjuice-test`) | BILLING, SUBSCRIPTIONS, CART | 🔴 Must Do | Admin |
| P-08 | **18 subscription plans** configured in Chargebee:
  - Categories: Delight, Signature, Premium
  - Sizes: 200ml, 300ml, 500ml
  - Frequencies: Weekly, Monthly
  - Plan IDs: `plan_{category}_{size}_{weekly|monthly}`
  - Prices in cents (INR) | SUBSCRIPTIONS checkout | 🔴 Must Do | Admin |
| P-09 | **One-time items** configured in Chargebee:
  - Each juice as an Item (type=`charge`)
  - Item Price with amount in cents
  - Item IDs: `charge_{category}_{size}` | ONE-TIME checkout | 🔴 Must Do | Admin |
| P-10 | Chargebee **Hosted Pages** configured with:
  - Checkout page for items (`checkout_new_for_items`)
  - Return URL: `bmjapp://payment/callback`
  - Cancel URL: `bmjapp://payment/cancel`
  - Webhook URL: `https://staging-api.bookmyjuice.co.in/api/v1/webhooks/chargebee` | PAYMENT, WEBHOOK tests | 🔴 Must Do | Admin |
| P-11 | Webhook signing secret verified — `X-Chargebee-Webhook-Signature` header validation | WEBHOOK tests | 🔴 Must Do | Admin |
| P-12 | Chargebee API key with full permissions (test mode) | ALL billing tests | 🔴 Must Do | Admin |

### 1.3 Firebase Project

| # | Item | Required For | Status | Owner |
|---|------|-------------|--------|-------|
| P-13 | Firebase project created (e.g., `bookmyjuice-4c156`) | AUTH (Firebase Phone, Google) | 🔴 Must Do | Admin |
| P-14 | **Phone Auth** enabled in Firebase Authentication → Sign-in method | AUTH-007a, AUTH-007b | 🔴 Must Do | Admin |
| P-15 | **Google Sign-In** enabled in Firebase Authentication | AUTH (Google flow) | 🔴 Must Do | Admin |
| P-16 | Android app (`com.bookmyjuice.app`) registered in Firebase with correct SHA-1 fingerprint | GOOGLE SIGN-IN | 🔴 Must Do | Admin |
| P-17 | `google-services.json` downloaded from Firebase Console and placed at `lush/android/app/google-services.json` | APP BUILD | 🔴 Must Do | Admin |
| P-18 | Web app registered in Firebase (for browser testing) | WEB TESTS | 🟡 If testing web | Admin |
| P-19 | Firebase OAuth client IDs verified:
  - Android SHA-1: `B6:FF:C3:DE:5B:1A:80:3F:3D:3F:B8:F7:6C:60:7B:2C:51:F1:D2:E0`
  - Web client ID matching what's in code | GOOGLE SIGN-IN | 🔴 Must Do | Admin |

### 1.4 Google Cloud Console

| # | Item | Required For | Status | Owner |
|---|------|-------------|--------|-------|
| P-20 | Google Cloud project linked to Firebase | GOOGLE SIGN-IN | 🔴 Must Do | Admin |
| P-21 | **OAuth consent screen** configured (Testing status, add test user emails) | GOOGLE SIGN-IN | 🔴 Must Do | Admin |
| P-22 | **People API** enabled | GOOGLE SIGN-IN | 🔴 Must Do | Admin |
| P-23 | **Android OAuth client ID** created with correct SHA-1 | GOOGLE SIGN-IN | 🔴 Must Do | Admin |
| P-24 | **Web OAuth client ID** created — used as `serverClientId` in Flutter code | GOOGLE SIGN-IN | 🔴 Must Do | Admin |

---

## Section 2: Test Accounts & Test Data

### 2.1 Authentication Test Accounts

| # | Account | Purpose | Credentials | Status |
|---|---------|---------|-------------|--------|
| TA-01 | **Email-First User** — Fresh account for email-first signup | UC-AUTH-001 | email: `e2e-test-email@bookmyjuice.co.in`, phone: `9876543210` | 🔴 Must Create |
| TA-02 | **Phone-First User** — Fresh account for phone-first signup | UC-AUTH-002 | phone: `9876543211`, email: `e2e-test-phone@bookmyjuice.co.in` | 🔴 Must Create |
| TA-03 | **Google User** — Google account for signup/login testing | UC-AUTH-003, UC-AUTH-005 | Google account: `e2e-google-test@gmail.com` (test user in OAuth consent) | 🔴 Must Create |
| TA-04 | **Existing Registered User** — Pre-created with email+phone+password | UC-AUTH-004, Login tests | email: `e2e-existing@bookmyjuice.co.in`, phone: `9876543212`, password: `TestPass123!` | 🔴 Must Create |
| TA-05 | **User with Active Subscription** — For pause/resume/cancel testing | UC-05, UC-06, UC-07 | Same as TA-04 with Chargebee subscription | 🔴 Must Create |
| TA-06 | **User with Paused Subscription** — For resume testing | UC-06 | Same as TA-04, subscription in paused state | 🔴 Must Create |
| TA-07 | **User with Cancelled Subscription** — For history testing | UC-07 | Same as TA-04, subscription cancelled | 🔴 Must Create |
| TA-08 | **User without any orders** — Edge case for order history | UC-08 | Fresh TA-01 account, no orders | 🔴 Must Create |
| TA-09 | **User with multiple subscriptions** — For multi-subscription testing | BR-047 | TA-04 with 2+ active subscriptions | 🔴 Must Create |
| TA-10 | **Firebase Phone Auth User** — Registered via Firebase Phone | UC-AUTH-007a, UC-AUTH-007b | phone: `9876543213` (with physical SIM for OTP) | 🔴 Must Create |

### 2.2 Test Phone Numbers (Physical or Virtual)

| # | Phone | Used For | Method | Status |
|---|-------|----------|--------|--------|
| TEL-01 | `9876543210` | Email-First signup OTP, Login OTP, password reset mobile | Backend OTP (SMS) | 🔴 Need SIM |
| TEL-02 | `9876543211` | Phone-First signup OTP | Backend OTP (SMS) | 🔴 Need SIM |
| TEL-03 | `9876543212` | Existing user login, password reset | Backend OTP (SMS) | 🔴 Need SIM |
| TEL-04 | `9876543213` | Firebase Phone Auth E2E (actual SMS from Firebase) | Firebase Phone Auth | 🔴 Need SIM |
| TEL-05 | `9876543214` | Non-registered phone → signup redirect | Backend OTP (SMS) | 🔴 Need SIM |

> **Note:** If using Firebase test phone numbers (with Test OTP codes), configure them in Firebase Console → Authentication → Sign-in method → Phone → Add test phone numbers. This avoids needing physical SIM cards.

### 2.3 Test Email Accounts

| # | Email | Used For | Status |
|---|-------|----------|--------|
| EM-01 | `e2e-test-email@bookmyjuice.co.in` | Email verification code reception | 🔴 Must Create |
| EM-02 | `e2e-test-phone@bookmyjuice.co.in` | Phone-first flow email verification | 🔴 Must Create |
| EM-03 | `e2e-existing@bookmyjuice.co.in` | Existing user email verification resend | 🔴 Must Create |
| EM-04 | `e2e-invalid-format` | Invalid email format validation | No setup needed |

> **Note:** For automated testing, SMTP should be configured to not require real delivery — use a service that captures outgoing emails (like Mailtrap, Papercut, or a local SMTP server) to avoid needing real inbox access.

### 2.4 Chargebee Test Payment Cards

| # | Card Number | Expiry | CVV | Purpose | Status |
|---|-------------|--------|-----|---------|--------|
| CB-01 | `4111 1111 1111 1111` | Any future date | Any 3 digits | Successful payment (Visa) | ✅ Always works in test mode |
| CB-02 | `4242 4242 4242 4242` | Any future date | Any 3 digits | Successful payment (Visa alt) | ✅ Always works |
| CB-03 | `4000 0000 0000 0002` | Any future date | Any 3 digits | Declined payment | ✅ Always works |
| CB-04 | `5555 5555 5555 4444` | Any future date | Any 3 digits | Successful payment (Mastercard) | ✅ Always works |
| CB-05 | `3782 822463 10005` | Any future date | Any 3 digits | Successful payment (Amex) | ✅ Always works |

> **Note:** These are Chargebee/Stripe test card numbers that always work in test mode. No real money involved.

### 2.5 Backend-Only Test Accounts (Direct DB or API)

| # | Account | How to Create | Used For | Status |
|---|---------|--------------|----------|--------|
| BA-01 | User with `fcm_token` set in DB | `UPDATE users SET fcm_token='test_token' WHERE id='x'` | FCM notification tests | 🔴 Must Insert |
| BA-02 | User with expired JWT in SharedPrefs equivalent | Create user, let 30 days pass, or manually expire | Auto-login expiry test | 🔴 Must Create |
| BA-03 | User who triggered rate limit | Attempt 10+ OTP requests in 5 min | Rate limiting tests | 🔴 Must Create |

---

## Section 3: Flutter App Build Configuration

### 3.1 APK / Web Build

| # | Item | Command / Details | Status | Owner |
|---|------|------------------|--------|-------|
| F-01 | Build Android APK pointing to staging backend | `cd lush && flutter build apk --debug --dart-define=API_BASE_URL=https://staging-api.bookmyjuice.co.in` | 🔴 Must Build | Developer |
| F-02 | Build Flutter Web pointing to staging backend | `cd lush && flutter build web --dart-define=API_BASE_URL=https://staging-api.bookmyjuice.co.in` | 🟡 If testing web | Developer |
| F-03 | Install APK on physical Android device | `adb install build/app/outputs/flutter-apk/app-debug.apk` | 🔴 Must Install | Tester |
| F-04 | Ensure Google Play Services are up to date on device | Settings → Google → Play Services → Update | 🔴 For Google Sign-In | Tester |
| F-05 | Grant notification permission when app prompts | Allow "BookMyJuice" to send notifications | 🔴 For FCM tests | Tester |
| F-06 | Verify `google-services.json` has non-empty `oauth_client` array | Check `lush/android/app/google-services.json` | 🔴 Must Verify | Developer |
| F-07 | Ensure `android/app/build.gradle` has correct `applicationId = "com.bookmyjuice.app"` | Check `defaultConfig.applicationId` | 🔴 Must Verify | Developer |

### 3.2 Network Configuration

| # | Item | Details | Status | Owner |
|---|------|---------|--------|-------|
| F-08 | Device has internet connection (WiFi or mobile data) | Required for all API calls | 🔴 Must Have | Tester |
| F-09 | Device can resolve staging API domain | `nslookup staging-api.bookmyjuice.co.in` or test `curl` from device | 🔴 Must Verify | DevOps |
| F-10 | Chargebee hosted pages not blocked by firewall or ad-blocker | Test URL: `https://bookmyjuice-test.chargebee.com` | 🔴 Must Verify | Tester |
| F-11 | No proxy interfering with HTTPS traffic (or configure proxy rules) | If using Charles/Proxyman, add SSL cert | 🟡 If debugging | Tester |

### 3.3 WebView Configuration

| # | Item | Details | Status | Owner |
|---|------|---------|--------|-------|
| F-12 | Flutter WebView plugin supports JavaScript | `javascriptMode: JavascriptMode.unrestricted` in webview code | 🔴 Must Verify | Developer |
| F-13 | WebView has no popup blockers that break Chargebee redirect | Check Chargebee redirects work in `payment_screen.dart` | 🔴 Must Verify | Developer |

---

## Section 4: API Testing Tools (Postman / Bruno / Curl)

### 4.1 Setup

| # | Item | Details | Status | Owner |
|---|------|---------|--------|-------|
| T-01 | Postman (or Bruno/Hoppscotch) installed | Download from postman.com | 🔴 Must Install | Tester |
| T-02 | Postman collection created with ALL endpoints (see API.md) | ~40+ API endpoints | 🔴 Must Create | Tester |
| T-03 | Postman environment configured for staging:
  - `base_url` = `https://staging-api.bookmyjuice.co.in/api/v1`
  - `auth_token` = auto-populated from login response | ALL API tests | 🔴 Must Create | Tester |
| T-04 | Pre-request script for JWT token management:
  - Extract JWT from login/signup response
  - Store in environment variable `auth_token`
  - Set `Authorization: Bearer {{auth_token}}` header globally | Authenticated endpoints | 🔴 Must Create | Tester |
| T-05 | Collection runner configured for bulk test execution | Regression runs | 🟡 Nice to Have | Tester |

### 4.2 Manual Test Helper Tools

| # | Tool | Used For | Status |
|---|------|----------|--------|
| T-06 | **Charles Proxy** or **Proxyman** | Inspect network traffic between Flutter app and bmjServer | 🟡 If debugging |
| T-07 | **Android Debug Bridge (adb)** | Capture Flutter logs: `adb logcat -s flutter` | 🟡 For debugging |
| T-08 | **Flutter DevTools** | Inspect widget tree, network calls, memory usage | 🟡 For UI debugging |
| T-09 | **Chargebee Admin Console** | Verify subscription/order/invoice data directly in Chargebee | BILLING, SUBSCRIPTIONS |
| T-10 | **MySQL client** (DBeaver, MySQL Workbench, or CLI) | Verify database state after webhook processing | WEBHOOK, DATA INTEGRITY |
| T-11 | **Firebase Console → Authentication** | Verify phone/Google auth events | AUTH |
| T-12 | **SMTP test service** (Mailtrap, Papercut, or Mailhog) | Capture email verification codes without real delivery | AUTH email verification |

---

## Section 5: Test Data Seeding

### 5.1 Database Seed Data

| # | Data | SQL / Command | Used For | Status |
|---|------|--------------|----------|--------|
| SD-01 | **Serviceable pincodes** in `service_areas` table | `INSERT INTO service_areas (pincode, city, state, cutoff_time, lead_hours, active) VALUES ('122001', 'Gurgaon', 'Haryana', '18:00', 24, true), ('560001', 'Bangalore', 'Karnataka', '18:00', 24, true), ('400001', 'Mumbai', 'Maharashtra', '18:00', 24, true), ('110001', 'Delhi', 'Delhi', '18:00', 24, true)` | DELIVERY tests | 🔴 Must Insert |
| SD-02 | **Non-serviceable pincode** for negative tests | `INSERT INTO service_areas (pincode, active) VALUES ('999999', false)` — then test with this pincode expecting rejection | DELIVERY negative tests | 🔴 Must Insert |
| SD-03 | **Test user with known cart state** (one-time cart with items) | Create via API: `POST /api/v1/cart/items` x3 items | CART merge, checkout tests | 🔴 Must Create |
| SD-04 | **Test user with subscription cart** (plan items in cart) | Create via API: `POST /api/v1/cart/items` with plan item | SUBSCRIPTION checkout | 🔴 Must Create |
| SD-05 | **Test user with empty cart** | Fresh user, no items | CART edge cases | 🔴 Must Create |
| SD-06 | **Guest cart** stored in system (cart_id in SharedPrefs) | `POST /api/v1/cart/items` without auth | CART merge (guest) | 🔴 Must Create |
| SD-07 | **Chargebee items/plans synced to local DB** | Trigger Chargebee sync or seed products table manually | PRODUCT CATALOG | 🔴 Must Seed |

### 5.2 Manual Pre-Condition Actions (Run Before Test Session)

| # | Action | Scheduled? | Status |
|---|--------|-----------|--------|
| SC-01 | Verify bmjServer is running: `curl https://staging-api.bookmyjuice.co.in/api/health` | Every test session | 🔴 Must Check |
| SC-02 | Verify MySQL is accessible: `mysql -h staging-db -u bmj -p bmj_db -e "SELECT 1"` | Every test session | 🔴 Must Check |
| SC-03 | Clear test user data for fresh accounts (if re-running tests): `DELETE FROM users WHERE email LIKE 'e2e-%'` | Before each full test run | 🔴 Must Do |
| SC-04 | Reset Chargebee test site state (if possible) — clear subscriptions, orders | Before billing tests | 🟡 If Possible |
| SC-05 | Verify Chargebee test site is accessible: `curl -u "$CHARGEBEE_API_KEY:" https://bookmyjuice-test.chargebee.com/api/v2/items` | Before billing tests | 🔴 Must Check |
| SC-06 | Verify Firebase Auth is accessible (test sign-in from device) | Before auth tests | 🔴 Must Check |
| SC-07 | Set timezone to IST (Asia/Kolkata) for 9 PM cutoff tests | Before subscription tests | 🔴 Must Set |
| SC-08 | Clear localStorage / app data between tests | Between each full test run | 🔴 Must Do |

---

## Section 6: Manual Test Execution Requirements

### 6.1 Tests That Require a Human in the Loop

These test cases **cannot** be fully automated and need manual execution:

| Test Area | Reason | Estimated Human Time |
|-----------|--------|---------------------|
| **Google Sign-In/Signup** | Requires tapping Google account picker (OS-level dialog, cannot be automated in Flutter integration tests) | 5 min per test |
| **Firebase Phone Auth** | Requires receiving actual SMS from Firebase and entering 6-digit code | 3 min per test |
| **Phone OTP receipt & entry** | SMS delivery depends on network, needs human to read and type | 2 min per test |
| **Email verification code** | User must open email, read code, enter in app | 2 min per test |
| **Chargebee Hosted Page checkout** | Payment UI is a WebView hosted by Chargebee — cannot be automated | 3 min per payment |
| **App cold start / auto-login** | Human must kill and relaunch app to observe auto-login behavior | 1 min per test |
| **FCM push notification (foreground)** | Requires sending push from Firebase Console and observing system tray | 3 min per test |
| **FCM push notification (background)** | App must be in background — human must minimize app | 2 min per test |
| **9 PM cutoff testing** | Must test before/after 9 PM IST (or mock system clock) | Session timing |
| **Network error handling** | Human must toggle airplane mode or disconnect WiFi at specific steps | 1 min per test |

### 6.2 Estimated Total Manual Testing Effort

| Module | Automated Tests | Manual Tests | Total Tests | Est. Manual Time |
|--------|----------------|--------------|-------------|-----------------|
| AUTH | ~40 | ~20 | ~60 | 90 min |
| PRODUCT CATALOG | ~8 | ~2 | ~10 | 10 min |
| CART | ~12 | ~3 | ~15 | 15 min |
| CHECKOUT / BILLING | ~8 | ~8 | ~16 | 30 min |
| SUBSCRIPTIONS | ~10 | ~6 | ~16 | 25 min |
| ORDERS | ~8 | ~2 | ~10 | 10 min |
| DELIVERY | ~8 | ~2 | ~10 | 10 min |
| NOTIFICATIONS | ~4 | ~6 | ~10 | 20 min |
| PROFILE | ~5 | ~1 | ~6 | 5 min |
| NFR (Security/Cache/Webhook) | ~15 | ~4 | ~19 | 20 min |
| **TOTAL** | **~118** | **~54** | **~172** | **~4 hours** |

---

## Section 7: Environment Checklist (Pre-Flight)

Use this checklist before **every** test session:

```
[ ] 1. bmjServer running → GET /api/health returns 200
[ ] 2. MySQL accessible → SELECT 1 returns 1
[ ] 3. Chargebee test site reachable → curl to Chargebee API works
[ ] 4. SMTP server running → email verification codes can be sent
[ ] 5. Firebase project accessible → Google Sign-In test from device works
[ ] 6. Test APK installed on device with correct API_BASE_URL
[ ] 7. Device has internet and can reach staging backend
[ ] 8. Test phone numbers have SIM inserted for OTP reception
[ ] 9. Test email inboxes accessible (or SMTP capture service running)
[ ] 10. Test user accounts exist (or can be created via signup flow)
[ ] 11. google-services.json present and correct at lush/android/app/
[ ] 12. WebView can load Chargebee hosted pages
[ ] 13. Notification permission granted on device
[ ] 14. System clock set to IST (Asia/Kolkata)
[ ] 15. Previous test data cleaned up (users, carts, etc.)
```

---

## Section 8: Summary of Human Actions Needed

### 🔴 CRITICAL (Must Do Before Any Testing)

| Priority | Action | Depends On |
|----------|--------|-----------|
| **1** | Deploy bmjServer to staging with .env configured | — |
| **2** | Configure Chargebee test site with 18 plans + items + hosted pages + webhooks | #1 |
| **3** | Configure Firebase project with Phone Auth + Google Sign-In enabled | — |
| **4** | Download `google-services.json` and place in Flutter project | #3 |
| **5** | Build Flutter APK with `--dart-define=API_BASE_URL=<staging-url>` | #1 |
| **6** | Create Google OAuth consent screen with test user emails | #3 |
| **7** | Create test user accounts (TA-01 through TA-10) | #1 |
| **8** | Install APK on physical Android device with Play Services | #5 |
| **9** | Ensure test phone numbers have working SIM (or configure Firebase test OTPs) | — |
| **10** | Set up Postman collection with JWT management scripts | #1 |

### 🟡 HIGH (Strongly Recommended)

| Priority | Action | Depends On |
|----------|--------|-----------|
| 11 | Seed database with serviceable pincodes | #1 |
| 12 | Set up SMTP capture service (Mailtrap) for email testing | #1 |
| 13 | Seed test data (users with carts, subscriptions, orders) | #1, #2 |
| 14 | Install Charles/Proxyman for network debugging | — |
| 15 | Create Postman environment with pre-request scripts | #1 |

### 🟢 NICE TO HAVE

| Priority | Action |
|----------|--------|
| 16 | Set up CI/CD pipeline to deploy staging on push to main |
| 17 | Configure Redis for cache testing |
| 18 | Build Patrol/E2E flutter integration tests for full automation |
| 19 | Set up Chargebee webhook simulator for offline testing |

---

**Document Control:**
- **Created:** 2026-05-18
- **Version:** 1.0
- **Status:** ✅ For Review

Next Step → Proceed to build detailed E2E test cases for each module.
