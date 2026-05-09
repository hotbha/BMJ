# BookMyJuice - Test Cases

**Document Version:** 2.0 (Consolidated)
**Date:** April 11, 2026
**Linked to:** BRD_Business_Requirements.md, USE_CASES.md, FUNCTIONAL_SPEC.md
**Status:** ⏳ Ready for Execution

---

## Table of Contents

1. [Test Strategy](#1-test-strategy)
2. [Test Environment](#2-test-environment)
3. [Test Data](#3-test-data)
4. [Authentication Test Cases](#4-authentication-test-cases)
5. [Product Catalog Test Cases](#5-product-catalog-test-cases)
6. [Shopping Cart Test Cases](#6-shopping-cart-test-cases)
7. [Checkout Test Cases](#7-checkout-test-cases)
8. [Subscription Test Cases](#8-subscription-test-cases)
9. [Order Management Test Cases](#9-order-management-test-cases)
10. [Performance Test Cases](#10-performance-test-cases)
11. [Security Test Cases](#11-security-test-cases)
12. [Test Execution Log](#12-test-execution-log)

---

## 1. Test Strategy

### 1.1 Testing Levels

| Level | Target | Framework | Coverage Target | Execution |
|-------|--------|-----------|-----------------|-----------|
| Unit | Individual functions, methods, classes | JUnit 5 (Backend), flutter_test (Frontend) | 80% line coverage | On every commit |
| Integration | Module interactions, API endpoints | Spring Boot Test, integration_test | All critical paths | Nightly |
| E2E | Complete user flows | Flutter integration_test | All use cases | Before release |
| UAT | Business requirements validation | Beta users | All BRs met | 2-week beta |

### 1.2 Test Case Naming Convention

```
TC-{MODULE}-{NNN}
Where:
  TC = Test Case
  MODULE = AUTH, PROD, CART, CHK, ORD, SUB, PERF, SEC
  NNN = Sequential number (001, 002, ...)
  SUFFIX = -EF (Email-First), -PF (Phone-First), -GS (Google Signup)
```

### 1.3 Test Priority Definitions

| Priority | Definition | Release Impact |
|----------|------------|----------------|
| P0 - Critical | Blocking feature, must pass before release | Blocks release |
| P1 - High | Major feature, should pass | Should fix before release |
| P2 - Medium | Important feature, nice to have | Can defer to post-MVP |
| P3 - Low | Minor feature, cosmetic | Low priority |

### 1.4 Test Status Definitions

| Status | Meaning |
|--------|---------|
| ⏳ Pending | Not yet executed |
| ✅ Pass | All assertions passed |
| ❌ Fail | One or more assertions failed |
| ⚠️ Blocked | Cannot execute due to dependency |
| 🔄 Retest | Failed, fixed, needs re-testing |

---

## 2. Test Environment

### 2.1 Environments

| Environment | Purpose | Access | URL |
|-------------|---------|--------|-----|
| Local Dev | Development | Developers | `http://localhost:8080` |
| Staging | Integration testing | QA, Product | `https://staging-api.bookmyjuice.co.in` |
| Production | Beta users | Beta testers | `https://api.bookmyjuice.co.in` |

### 2.2 Backend Setup
- **Framework:** Spring Boot 3.1.0
- **Database:** MySQL 8.0 (Docker)
- **Test Database:** H2 (Unit tests), Testcontainers (Integration)
- **Chargebee:** Test Site (`bookmyjuice-test`)

### 2.3 Frontend Setup
- **Framework:** Flutter 3.x
- **Test Frameworks:** flutter_test, mockito, bloc_test, patrol
- **Test Device:** Android 16 (API 36), ARM64

---

## 3. Test Data

### 3.1 Test Users

| Email | Password | Role | Notes |
|-------|----------|------|-------|
| test_user_1@test.com | Test123! | USER | Standard user |
| test_user_2@test.com | Test123! | USER | Standard user |
| google_user@test.com | N/A | USER | Google Sign-In |

### 3.2 Test Products

| Category | Sizes | One-Time Price | Subscription Price |
|----------|-------|----------------|-------------------|
| Delight | 200ml, 300ml, 500ml | ₹75, ₹100, ₹150 | ₹400/wk, ₹1500/mo |
| Signature | 200ml, 300ml, 500ml | ₹100, ₹150, ₹200 | ₹600/wk, ₹2200/mo |
| Premium | 200ml, 300ml, 500ml | ₹150, ₹200, ₹300 | ₹800/wk, ₹3000/mo |

### 3.3 Test Payment
- **Mode:** Chargebee Test Mode (no real charges)
- **Test Cards:** Provided by Chargebee documentation
- **Success Scenarios:** Payment succeeds, webhook fires
- **Failure Scenarios:** Card declined, insufficient funds

---

## 4. Authentication Test Cases

### TC-AUTH-001: Email Registration - Valid Data
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-001, FR-AUTH-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Backend running, database accessible |
| **Test Data** | Email: test001@test.com, Password: Test123!, Name: John Doe, Phone: 9876543210 |

**Test Steps:**
1. POST /api/auth/signup with valid data → HTTP 200 OK
2. Verify response contains user ID → User ID present
3. Verify user created in database → User record exists
4. Verify Chargebee customer created → Customer exists in Chargebee
5. Verify password is hashed → Password not plain text in DB

**Pass Criteria:** All 5 steps pass, Response time < 2 seconds, No exceptions
**Fail Criteria:** Any step fails, HTTP status != 200, User not created

---

### TC-AUTH-002: Email Registration - Duplicate Email
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-001, FR-AUTH-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User test001@test.com already exists |

**Test Steps:**
1. POST /api/auth/signup with existing email → HTTP 400 Bad Request
2. Verify error message → Message contains "already taken"
3. Verify no duplicate user created → Only 1 user with email exists

**Pass Criteria:** HTTP 400 returned, Appropriate error message, No duplicate records

---

### TC-AUTH-003: Email Login - Valid Credentials
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-001, FR-AUTH-002 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User test001@test.com exists with password Test123! |

**Test Steps:**
1. POST /api/auth/signin with valid credentials → HTTP 200 OK
2. Verify JWT token in response → Token present, valid JWT format
3. Verify refresh token in response → Refresh token present
4. Verify user profile in response → User details present
5. Verify token expiry is 30 days → exp claim = iat + 2592000 seconds

**Pass Criteria:** HTTP 200 returned, Valid JWT token with 30-day expiry, User profile data correct

---

### TC-AUTH-004: Email Login - Invalid Credentials
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-001, FR-AUTH-002 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |

**Test Steps:**
1. POST /api/auth/signin with wrong password → HTTP 401 Unauthorized
2. Verify error message → Message "Invalid credentials"
3. Verify no token returned → Token field absent or null
4. Verify login attempt logged → Entry in security logs

**Pass Criteria:** HTTP 401 returned, Appropriate error message, No token issued

---

### TC-AUTH-005: Auto-Login - Valid Token
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-006, FR-AUTH-004 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User has valid JWT token stored in SharedPreferences |

**Test Steps:**
1. Launch app with stored token → App initiates auto-login
2. Auto-login calls ONLY `GET /api/v1/auth/me` with token (no Google/phone invocations)
3. GET /api/v1/auth/me with token → HTTP 200 OK
4. Verify response message → Message = "ok"
5. Verify navigation to dashboard → Dashboard screen displayed
6. Verify NO Google Sign-In was triggered → No Google account picker shown
7. Verify NO phone OTP was sent → No OTP screen shown

**Pass Criteria:** Auto-login completes via token only, User navigated to dashboard, No Google/phone flows triggered

---

### TC-AUTH-006: Auto-Login - Expired Token
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-006, FR-AUTH-004 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | User has expired token stored (> 30 days old) |

**Test Steps:**
1. Launch app with expired token → App initiates auto-login
2. GET /api/v1/auth/me with expired token → HTTP 401
3. Verify error response → Token expired error
4. Verify navigation to login screen → Login screen displayed (NOT Google picker, NOT phone OTP)
5. Verify stored token cleared → SharedPreferences cleared

**Pass Criteria:** Expired token rejected, User redirected to login screen, No Google/phone flows triggered, Stored token cleared

---

### TC-AUTH-007: Google Sign-In - Account Picker Shows (Login Flow)
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-010, FR-AUTH-003 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User is on login screen, NO valid JWT, Google accounts configured on device |

**Test Steps:**
1. User taps "Sign in with Google" button → Google account picker dialog appears
2. User selects a Google account → Account selected
3. Google returns verified email, name, Google ID
4. System searches backend for user with matching Google ID or email
5. **User found:** Backend returns JWT token
6. Verify JWT stored in SharedPreferences → Token present
7. Verify navigation to dashboard → Dashboard screen displayed

**Pass Criteria:** Account picker shown, Google auth completes, User found → JWT returned → Dashboard shown

---

### TC-AUTH-008: Google Sign-In - New User (Signup Flow Triggered)
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-010, BR-003 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User is on login screen, NO valid JWT, Google account NOT registered in system |

**Test Steps:**
1. User taps "Sign in with Google" button → Google account picker appears
2. User selects Google account → Google returns email, name, Google ID
3. System searches backend → User NOT found
4. System starts signup flow → Navigates to signup screen
5. Verify email is pre-filled from Google → Email field shows Google email (read-only)
6. Verify first name is pre-filled → First name editable
7. Verify last name is pre-filled → Last name editable
8. User continues signup: enters phone → verifies OTP → enters address → creates password
9. Verify account created → User record in database with Google ID linked
10. Verify JWT returned → Token stored
11. Verify navigation to dashboard → Dashboard displayed

**Pass Criteria:** Signup triggered with pre-filled Google data, Account created with Google ID, JWT returned, Dashboard shown

---

### TC-AUTH-009: Phone Sign-In - OTP Verification (Login Flow)
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-011, FR-AUTH-002 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User is on login screen, NO valid JWT, registered user with phone exists |

**Test Steps:**
1. User taps "Sign in with Phone" button → Phone number entry screen appears
2. User enters registered 10-digit phone number → Phone accepted
3. User taps "Send OTP" → 6-digit OTP sent to phone
4. User enters valid OTP → OTP entry screen
5. User taps "Verify OTP" → System validates OTP
6. System searches backend for user with matching verified phone → User found
7. Backend returns JWT token → Token stored in SharedPreferences
8. Verify navigation to dashboard → Dashboard screen displayed

**Pass Criteria:** Phone entry shown, OTP sent, OTP verified, User found → JWT returned → Dashboard shown

---

### TC-AUTH-010: Phone Sign-In - New User (Signup Flow Triggered)
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-011, BR-002 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User is on login screen, NO valid JWT, phone number NOT registered |

**Test Steps:**
1. User taps "Sign in with Phone" button → Phone number entry screen
2. User enters new 10-digit phone number → Phone accepted
3. User taps "Send OTP" → 6-digit OTP sent
4. User enters valid OTP → OTP verified
5. System searches backend → User NOT found with verified phone
6. System starts signup flow → Navigates to signup screen
7. Verify phone is pre-filled from OTP → Phone field shows verified number (read-only)
8. User continues signup: enters email → verifies email → enters address → creates password
9. Verify account created → User record in database
10. Verify JWT returned → Token stored
11. Verify navigation to dashboard → Dashboard displayed

**Pass Criteria:** Signup triggered with pre-filled verified phone, Account created, JWT returned, Dashboard shown

---

### TC-AUTH-EF-001 to TC-AUTH-EF-010: Email-First Signup Flow
| Test ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| TC-AUTH-EF-001 | Email entry - valid format | P0 | ⏳ Pending |
| TC-AUTH-EF-002 | Email entry - invalid format | P0 | ⏳ Pending |
| TC-AUTH-EF-003 | Email verification code sent | P0 | ⏳ Pending |
| TC-AUTH-EF-004 | Email verification code - valid | P0 | ⏳ Pending |
| TC-AUTH-EF-005 | Email verification code - invalid | P0 | ⏳ Pending |
| TC-AUTH-EF-006 | Email verification code - expired | P0 | ⏳ Pending |
| TC-AUTH-EF-007 | Resend code - before 30s (disabled) | P1 | ⏳ Pending |
| TC-AUTH-EF-008 | Resend code - after 30s (enabled) | P1 | ⏳ Pending |
| TC-AUTH-EF-009 | Email already registered | P0 | ⏳ Pending |
| TC-AUTH-EF-010 | Rate limiting (5 per hour) | P1 | ⏳ Pending |

---

### TC-AUTH-PF-001 to TC-AUTH-PF-010: Phone-First Signup Flow
| Test ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| TC-AUTH-PF-001 | Phone entry - valid 10-digit | P0 | ⏳ Pending |
| TC-AUTH-PF-002 | Phone entry - invalid format | P0 | ⏳ Pending |
| TC-AUTH-PF-003 | OTP sent to phone | P0 | ⏳ Pending |
| TC-AUTH-PF-004 | OTP verification - valid | P0 | ⏳ Pending |
| TC-AUTH-PF-005 | OTP verification - invalid | P0 | ⏳ Pending |
| TC-AUTH-PF-006 | OTP verification - expired | P0 | ⏳ Pending |
| TC-AUTH-PF-007 | Resend OTP - before 30s | P1 | ⏳ Pending |
| TC-AUTH-PF-008 | Resend OTP - after 30s | P1 | ⏳ Pending |
| TC-AUTH-PF-009 | Phone already registered | P0 | ⏳ Pending |
| TC-AUTH-PF-010 | Rate limiting (5 per hour) | P1 | ⏳ Pending |

---

### TC-AUTH-GS-001 to TC-AUTH-GS-005: Google Signup Flow
| Test ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| TC-AUTH-GS-001 | Google auth success | P0 | ⏳ Pending |
| TC-AUTH-GS-002 | Google auth cancelled | P1 | ⏳ Pending |
| TC-AUTH-GS-003 | Phone OTP after Google | P0 | ⏳ Pending |
| TC-AUTH-GS-004 | Email pre-filled (read-only) | P1 | ⏳ Pending |
| TC-AUTH-GS-005 | Name pre-filled (editable) | P1 | ⏳ Pending |

---

## 5. Product Catalog Test Cases

### TC-PROD-001: List Products - Successful Retrieval
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-010, FR-PROD-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Backend running, Chargebee items synced |

**Test Steps:**
1. GET /api/v1/products with auth → HTTP 200 OK
2. Verify response is array → Response body is JSON array
3. Verify products have required fields → id, name, description, prices present
4. Verify prices array not empty → Each product has at least 1 price
5. Verify product count → Count matches Chargebee items

**Pass Criteria:** HTTP 200 returned, Products list populated, All required fields present

---

### TC-PROD-002: List Products - Unauthorized Access
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-010, FR-PROD-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P1 - High |

**Test Steps:**
1. GET /api/v1/products without auth → HTTP 200 (Optional auth endpoint)
2. Verify response contains products → Products returned (guest can browse)

**Pass Criteria:** Products returned without auth (guest browsing allowed)

---

### TC-PROD-003: Product Details - Display Information
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-010, FR-PROD-002 |
| **Test Type** | UI Test (Frontend) |
| **Priority** | P1 - High |

**Test Steps:**
1. Tap on product from list → Product detail screen opens
2. Verify product name displayed → Name matches list
3. Verify product image displayed → Image visible
4. Verify description displayed → Description text present
5. Verify size options displayed → All size variants shown with prices
6. Verify "Add to Cart" button visible → Button enabled

**Pass Criteria:** All product information displayed, Size options visible, Add to Cart button enabled

---

## 6. Shopping Cart Test Cases

### TC-CART-001: Add to Cart - New Item
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-020, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P0 - Critical |
| **Preconditions** | Cart is empty |

**Test Steps:**
1. Select product and size → Product detail screen
2. Tap "Add to Cart" → Item added event triggered
3. Verify cart state updated → Cart contains 1 item
4. Verify cart badge updated → Badge shows "1"
5. Verify cart saved to storage → SharedPreferences updated

**Pass Criteria:** Item added to cart, Cart count updated, Cart persisted

---

### TC-CART-002: Add to Cart - Existing Item Same Size
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-020, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A (200ml) |

**Test Steps:**
1. Add same product with same size → Add to Cart tapped
2. Verify quantity incremented → Quantity = 2
3. Verify no duplicate item → Cart still has 1 item entry
4. Verify total price updated → Total = ₹200

**Pass Criteria:** Quantity incremented (not new item), Total price correct, No duplicates

---

### TC-CART-003: Add to Cart - Existing Item Different Size
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-020, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A (200ml) |

**Test Steps:**
1. Add same product with different size (300ml) → Add to Cart tapped
2. Verify new item added → Cart has 2 items
3. Verify items are separate → 200ml and 300ml are separate entries
4. Verify total calculated correctly → Total = price(200ml) + price(300ml)

**Pass Criteria:** New item added (not quantity increment), Different sizes are separate, Total correct

---

### TC-CART-004 to TC-CART-010: Additional Cart Tests
| Test ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| TC-CART-004 | Update cart quantity - increase | P1 | ⏳ Pending |
| TC-CART-005 | Update cart quantity - decrease to zero (remove) | P1 | ⏳ Pending |
| TC-CART-006 | Calculate cart total - with tax and delivery | P1 | ⏳ Pending |
| TC-CART-007 | Calculate cart total - free delivery | P2 | ⏳ Pending |
| TC-CART-008 | Remove item from cart | P1 | ⏳ Pending |
| TC-CART-009 | Clear entire cart | P1 | ⏳ Pending |
| TC-CART-010 | Cart persistence (app restart) | P0 | ⏳ Pending |

---

## 7. Checkout Test Cases

### TC-CHK-001: One-Time Checkout - Generate Hosted Page
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-030, FR-CHK-001 |
| **Test Type** | Integration Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Cart has items, user authenticated |

**Test Steps:**
1. POST /api/v1/checkout/initiate with cart items → HTTP 200 OK
2. Verify response contains URL → hosted_page.url present
3. Verify URL is valid Chargebee URL → URL starts with https://bookmyjuice-test.chargebee.com
4. Verify URL expiry → URL valid for 1 hour

**Pass Criteria:** HTTP 200 returned, Valid Chargebee URL provided, URL accessible

---

### TC-CHK-002: One-Time Checkout - Complete Payment Flow
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-030, FR-CHK-001 |
| **Test Type** | E2E Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Checkout URL obtained |

**Test Steps:**
1. Open checkout URL in WebView → Chargebee page loads
2. Enter test card details → Card form filled
3. Submit payment → Payment processing
4. Verify payment success → Success page displayed
5. Verify return to app → App receives success callback
6. Verify order confirmation shown → Order confirmation screen
7. Verify cart cleared → Cart empty after order

**Pass Criteria:** Payment completes successfully, Order confirmation shown, Cart cleared

---

### TC-CHK-003: Subscription Checkout - Generate Plan URL
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-030, FR-CHK-002 |
| **Test Type** | Integration Test (Backend) |
| **Priority** | P0 - Critical |

**Test Steps:**
1. POST /api/v1/checkout/initiate with subscription cart → HTTP 200 OK
2. Verify response contains URL → hosted_page.url present
3. Verify URL includes plan → Plan ID in hosted page params
4. Verify URL is valid Chargebee URL → URL valid

**Pass Criteria:** HTTP 200 returned, Valid Chargebee subscription URL provided

---

### TC-CHK-004: Subscription Checkout - Complete Payment
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-030, FR-CHK-002 |
| **Test Type** | E2E Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. Open subscription checkout URL in WebView → Chargebee page loads
2. Enter test card details → Card form filled
3. Submit payment → Payment processing
4. Verify payment success → Success page displayed
5. Verify subscription created → Subscription record in MySQL
6. Verify subscription visible in app → GET /api/v1/subscriptions returns new subscription

**Pass Criteria:** Payment completes, Subscription created in Chargebee + MySQL, Visible in app

---

## 8. Subscription Test Cases

### TC-SUB-001: List Subscriptions - User Has Active
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-040, FR-SUB-001 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. GET /api/v1/subscriptions → HTTP 200 OK
2. Verify response is array → Response contains subscriptions
3. Verify subscription details → id, status, plan_id, billing_period present
4. Verify status is "active" → Status badge shows "Active"

**Pass Criteria:** HTTP 200 returned, Subscriptions list populated, Details correct

---

### TC-SUB-002: Pause Subscription - Before 9 PM
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-041, FR-SUB-003 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Active subscription, time < 9 PM |

**Test Steps:**
1. POST /api/v1/subscriptions/:id/pause → HTTP 202 Accepted
2. Verify response message → "Pause scheduled. Refetch subscription status."
3. GET /api/v1/subscriptions/:id → Status = "paused"
4. Verify UI updated → Status badge shows orange "Paused"

**Pass Criteria:** HTTP 202 returned, Subscription status updated to paused, UI updated

---

### TC-SUB-003: Pause Subscription - After 9 PM
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-041, FR-SUB-003 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | Active subscription, time >= 9 PM |

**Test Steps:**
1. POST /api/v1/subscriptions/:id/pause → HTTP 400 Bad Request
2. Verify error message → "Actions available until 9 PM. Changes will take effect next day."
3. Verify subscription not paused → Status remains "active"

**Pass Criteria:** HTTP 400 returned, Appropriate error message, Subscription not paused

---

### TC-SUB-004: Resume Subscription
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-042, FR-SUB-004 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Paused subscription, time < 9 PM |

**Test Steps:**
1. POST /api/v1/subscriptions/:id/resume → HTTP 202 Accepted
2. GET /api/v1/subscriptions/:id → Status = "active"
3. Verify UI updated → Status badge shows green "Active"

**Pass Criteria:** HTTP 202 returned, Subscription status updated to active, UI updated

---

### TC-SUB-005: Cancel Subscription - End of Term
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-043, FR-SUB-005 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. POST /api/v1/subscriptions/:id/cancel { "cancel_option": "end_of_term" } → HTTP 202 Accepted
2. GET /api/v1/subscriptions/:id → scheduled_cancellation_at set
3. Verify UI shows "Cancellation scheduled for [date]" banner
4. Verify "Remove Scheduled Cancellation" button visible

**Pass Criteria:** HTTP 202 returned, Cancellation scheduled, UI shows banner

---

### TC-SUB-006 to TC-SUB-010: Additional Subscription Tests
| Test ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| TC-SUB-006 | Cancel subscription - immediately | P0 | ⏳ Pending |
| TC-SUB-007 | Remove scheduled cancellation | P1 | ⏳ Pending |
| TC-SUB-008 | Multiple active subscriptions | P1 | ⏳ Pending |
| TC-SUB-009 | Delivery schedule view | P1 | ⏳ Pending |
| TC-SUB-010 | Subscription status refetch after action | P0 | ⏳ Pending |

---

## 9. Order Management Test Cases

### TC-ORD-001: View Order History - Paginated
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-052, FR-ORD-001 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. GET /api/v1/orders?page=1&per_page=20 → HTTP 200 OK
2. Verify response is paginated → Response contains orders array + pagination info
3. Verify orders sorted by date → Newest first
4. Verify status badges displayed → pending, confirmed, shipped, delivered, cancelled
5. Scroll down → GET /api/v1/orders?page=2 → Next batch returned

**Pass Criteria:** HTTP 200 returned, Orders paginated, Sorted by date, Status badges correct

---

### TC-ORD-002: View Order Details
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-053, FR-ORD-002 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. GET /api/v1/orders/:id → HTTP 200 OK
2. Verify order details → id, status, items, pricing, shipping_address present
3. Verify line items → item_name, quantity, unit_price, total for each item
4. Verify pricing breakdown → subtotal, tax, delivery_fee, grand_total correct

**Pass Criteria:** HTTP 200 returned, All order details present, Pricing correct

---

### TC-ORD-003: View Invoice
| Field | Value |
|-------|-------|
| **Linked Requirements** | BR-054, FR-ORD-003 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | Delivered order with invoice |

**Test Steps:**
1. GET /api/v1/orders/:id/invoice → HTTP 200 OK
2. Verify response contains invoice_url → URL present
3. Verify URL is Chargebee-hosted → URL starts with https://[site].chargebee.com
4. Open URL in browser → Invoice PDF displayed

**Pass Criteria:** HTTP 200 returned, Valid invoice URL, Chargebee page loads

---

## 10. Performance Test Cases

### TC-PERF-001: API Response Time - 95th Percentile
| Field | Value |
|-------|-------|
| **Linked Requirements** | NFR-001 |
| **Test Type** | Performance Test |
| **Priority** | P1 - High |

**Test Steps:**
1. Send 1000 requests to GET /api/v1/products
2. Measure response times
3. Calculate 95th percentile
4. Verify p95 < 2000ms

**Pass Criteria:** p95 response time < 2000ms

---

### TC-PERF-002: App Cold Start Time
| Field | Value |
|-------|-------|
| **Linked Requirements** | NFR-002 |
| **Test Type** | Performance Test |
| **Priority** | P1 - High |

**Test Steps:**
1. Kill app completely
2. Launch app
3. Measure time to dashboard displayed
4. Verify time < 3000ms

**Pass Criteria:** App cold start < 3 seconds

---

## 11. Security Test Cases

### TC-SEC-001: JWT Token Expiry
| Field | Value |
|-------|-------|
| **Linked Requirements** | NFR-006 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. Login and receive JWT token
2. Decode token, verify exp claim = iat + 2592000 seconds (30 days)
3. Wait for token to expire (or manipulate time)
4. Use expired token for API call → HTTP 401 returned

**Pass Criteria:** Token expires after 30 days, Expired token rejected

---

### TC-SEC-002: Password Storage - BCrypt Hash
| Field | Value |
|-------|-------|
| **Linked Requirements** | NFR-005 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. Create user with password "Test123!"
2. Query database for user record
3. Verify password_hash field is BCrypt format (starts with $2a$, $2b$, or $2y$)
4. Verify password_hash is not plain text

**Pass Criteria:** Password stored as BCrypt hash, Not plain text

---

### TC-SEC-003: Webhook Signature Validation
| Field | Value |
|-------|-------|
| **Linked Requirements** | NFR-007 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |

**Test Steps:**
1. POST /api/v1/webhooks/chargebee with invalid signature → HTTP 401 returned
2. POST /api/v1/webhooks/chargebee with valid signature → HTTP 200 returned
3. Verify webhook processed → Event logged in webhook_events table

**Pass Criteria:** Invalid signatures rejected, Valid signatures processed, Events logged

---

## 12. Test Execution Log

### Test Summary

| Module | Total Tests | Passed | Failed | Blocked | Pending |
|--------|-------------|--------|--------|---------|---------|
| Authentication | 33 | 0 | 0 | 0 | 33 |
| Product Catalog | 3 | 0 | 0 | 0 | 3 |
| Shopping Cart | 10 | 0 | 0 | 0 | 10 |
| Checkout | 4 | 0 | 0 | 0 | 4 |
| Subscription | 10 | 0 | 0 | 0 | 10 |
| Order Management | 3 | 0 | 0 | 0 | 3 |
| Performance | 2 | 0 | 0 | 0 | 2 |
| Security | 3 | 0 | 0 | 0 | 3 |
| **TOTAL** | **68** | **0** | **0** | **0** | **68** |

### Execution History

| Date | Executed By | Test Suite | Result | Notes |
|------|-------------|------------|--------|-------|
| | | | ⏳ Pending | Ready for execution |

### Defects Found

| Defect ID | Test Case ID | Description | Severity | Status |
|-----------|--------------|-------------|----------|--------|
| | | | | |

---

## Appendix A: Test Data Management

### Cleanup Procedures
- After each test run, clean up test users from database
- Reset Chargebee test site to baseline
- Clear SharedPreferences on test device

### Data Refresh
- Sync Chargebee items to MySQL before test execution
- Verify test products and plans exist
- Verify test user accounts created

---

**Document Control:**
- **Created:** March 27, 2026
- **Last Updated:** April 11, 2026 (Consolidated)
- **Version:** 2.0
- **Status:** ⏳ Ready for Execution
