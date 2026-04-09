# BookMyJuice - Test Cases Document

**Document Version:** 3.0  
**Date:** March 29, 2026  
**Linked to:** BRD_Business_Requirements.md, ADR-003-chargebee-integration-strategy.md, ADR-004-unified-signup-flow.md  
**Updated For:** Unified Signup Flow Implementation

---

## Architecture Notes (IMPORTANT)

### System Boundaries

**Chargebee (Source of Truth):**
- Products, Plans, Pricing, Categories
- Subscriptions, Invoices, Orders, Payments
- Customer billing details

**bmjServer (Source of Truth):**
- User Authentication (ONLY)
- JWT tokens, User roles
- Email/Phone verification codes (dev: in-memory, prod: Redis)

**Sync Strategy:**
- User ↔ Customer: One-to-one mapping (ADR-003)
- All Chargebee data synced to local MySQL via webhooks
- Local cache for fast retrieval (avoid Chargebee API calls)

### Unified Signup Flow (ADR-004)

**Three Entry Points:**
1. **Email-First:** Email → Verify Email → Phone → Verify OTP → Address → Password
2. **Phone-First:** Phone → Verify OTP → Email → Verify Email → Address → Password
3. **Google:** Google Auth (email verified) → Phone → Verify OTP → Address → Password

**Test Implications:**
- **25+ new test cases** for unified signup flow
- See `../UNIFIED_SIGNUP_TEST_CASES.md` for complete test suite
- Automated tests in `../lush/integration_test/physical_device_template_test.dart`

### Test Implications

- **Backend Tests:** Mock Chargebee API for write operations, test email/phone verification
- **Frontend Tests:** All reads from local cache (fast), test 11 new signup screens
- **Integration Tests:** Test webhook handlers, sync service, unified signup API
- **E2E Tests:** Real Chargebee test environment, physical device testing (25053PC47I)

---

## Test Case Naming Convention

```
TC-{MODULE}-{NNN}
Where:
  TC = Test Case
  MODULE = AUTH, PROD, CART, CHK, ORD, SUB, PERF, SEC
  NNN = Sequential number (001, 002, ...)
  SUFFIX = -EF (Email-First), -PF (Phone-First), -GS (Google Signup), -AE (Address), -PC (Password)
```

**Examples:**
- `TC-AUTH-001` = Authentication Module, Test Case 001 (legacy)
- `TC-AUTH-EF-001` = Email-First Signup Flow, Test Case 001
- `TC-AUTH-PF-001` = Phone-First Signup Flow, Test Case 001
- `TC-AUTH-GS-001` = Google Signup Flow, Test Case 001

---

## Test Case Status Definitions

| Status | Meaning |
|--------|---------|
| ⏳ Pending | Not yet executed |
| ✅ Pass | All assertions passed |
| ❌ Fail | One or more assertions failed |
| ⚠️ Blocked | Cannot execute due to dependency/M dependency |
| 🔄 Retest | Failed, fixed, needs re-testing |

---

## Test Priority Definitions

| Priority | Definition |
|----------|------------|
| P0 - Critical | Blocking feature, must pass before release |
| P1 - High | Major feature, should pass |
| P2 - Medium | Important feature, nice to have |
| P3 - Low | Minor feature, can defer |

---

# SECTION 1: AUTHENTICATION TEST CASES

## TC-AUTH-001: Email Registration - Valid Data

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-001 |
| **Linked Requirements** | BR-001, FR-AUTH-001, UC-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Backend running, database accessible |
| **Test Data** | Email: test001@test.com, Password: Test123!, Name: John Doe, Phone: 9876543210 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signup with valid data | HTTP 200 OK | ⬜ |
| 2 | Verify response contains user ID | User ID present in response | ⬜ |
| 3 | Verify user created in database | User record exists in users table | ⬜ |
| 4 | Verify Chargebee customer created | Customer exists in Chargebee | ⬜ |
| 5 | Verify password is hashed | Password is not plain text in DB | ⬜ |

### Pass Criteria
- All 5 steps pass
- Response time < 2 seconds
- No exceptions in backend logs

### Fail Criteria
- Any step fails
- HTTP status != 200
- User not created in database
- Chargebee customer not created

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-002: Email Registration - Duplicate Email

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-002 |
| **Linked Requirements** | BR-001, FR-AUTH-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User test001@test.com already exists |
| **Test Data** | Email: test001@test.com (duplicate) |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signup with existing email | HTTP 400 Bad Request | ⬜ |
| 2 | Verify error message | Message contains "already taken" | ⬜ |
| 3 | Verify no duplicate user created | Only 1 user with email exists | ⬜ |

### Pass Criteria
- HTTP 400 returned
- Appropriate error message shown
- No duplicate records

### Fail Criteria
- HTTP 200 returned
- Duplicate user created
- No error message

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-003: Email Registration - Invalid Password

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-003 |
| **Linked Requirements** | BR-001, FR-AUTH-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | None |
| **Test Data** | Password: weak (fails complexity) |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signup with password "weak" | HTTP 400 Bad Request | ⬜ |
| 2 | Verify error message | Message indicates password requirements | ⬜ |
| 3 | Verify no user created | No user record in database | ⬜ |

### Pass Criteria
- HTTP 400 returned
- Error message explains password requirements
- No user created

### Fail Criteria
- HTTP 200 returned
- User created with weak password
- No error message

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-004: Email Login - Valid Credentials

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-004 |
| **Linked Requirements** | BR-001, FR-AUTH-002, UC-002 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User test001@test.com exists with password Test123! |
| **Test Data** | Email: test001@test.com, Password: Test123! |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signin with valid credentials | HTTP 200 OK | ⬜ |
| 2 | Verify JWT token in response | Token present, valid JWT format | ⬜ |
| 3 | Verify refresh token in response | Refresh token present | ⬜ |
| 4 | Verify user profile in response | User details present | ⬜ |
| 5 | Verify token expiry is 15 minutes | exp claim = iat + 900 seconds | ⬜ |

### Pass Criteria
- HTTP 200 returned
- Valid JWT token with 15 min expiry
- User profile data correct

### Fail Criteria
- HTTP status != 200
- Token missing or invalid
- Wrong user data

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-005: Email Login - Invalid Credentials

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-005 |
| **Linked Requirements** | BR-001, FR-AUTH-002 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User exists |
| **Test Data** | Email: test001@test.com, Password: WrongPass123 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signin with wrong password | HTTP 401 Unauthorized | ⬜ |
| 2 | Verify error message | Message "Invalid credentials" | ⬜ |
| 3 | Verify no token returned | Token field absent or null | ⬜ |
| 4 | Verify login attempt logged | Entry in security logs | ⬜ |

### Pass Criteria
- HTTP 401 returned
- Appropriate error message
- No token issued

### Fail Criteria
- HTTP 200 returned
- Token issued for invalid login
- No error message

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-006: Auto-Login - Valid Token

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-006 |
| **Linked Requirements** | BR-001, FR-AUTH-004 |
| **Test Type** | Integration Test (Frontend + Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User logged in with "Remember Me", token stored |
| **Test Data** | Stored JWT token from previous login |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Launch app with stored token | App initiates auto-login | ⬜ |
| 2 | GET /api/auth/autologin with token | HTTP 200 OK | ⬜ |
| 3 | Verify response message | Message = "ok" | ⬜ |
| 4 | Verify navigation to dashboard | Dashboard screen displayed | ⬜ |

### Pass Criteria
- Auto-login completes successfully
- User navigated to dashboard
- No login screen shown

### Fail Criteria
- Auto-login fails
- User asked to login again
- Error message shown

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-007: Auto-Login - Expired Token

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-007 |
| **Linked Requirements** | BR-001, FR-AUTH-004 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | User has expired token stored (> 15 min old) |
| **Test Data** | Expired JWT token |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Launch app with expired token | App initiates auto-login | ⬜ |
| 2 | GET /api/auth/autologin with expired token | HTTP 400 or 401 | ⬜ |
| 3 | Verify error response | Token expired error | ⬜ |
| 4 | Verify navigation to login screen | Login screen displayed | ⬜ |
| 5 | Verify stored token cleared | SharedPreferences cleared | ⬜ |

### Pass Criteria
- Expired token rejected
- User redirected to login
- Stored token cleared

### Fail Criteria
- Expired token accepted
- User stuck on loading screen
- Token not cleared

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-AUTH-008: Google Sign-In - Valid Google Account

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-008 |
| **Linked Requirements** | BR-001, FR-AUTH-003 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | Google Sign-In configured, test Google account available |
| **Test Data** | Test Google account credentials |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Tap "Sign in with Google" button | Google Sign-In flow starts | ⬜ |
| 2 | Select Google account | Account selected | ⬜ |
| 3 | Verify Google authentication | Google returns ID token | ⬜ |
| 4 | Verify backend creates/finds user | User account exists | ⬜ |
| 5 | Verify JWT tokens returned | JWT and refresh token received | ⬜ |
| 6 | Verify navigation to dashboard | Dashboard displayed | ⬜ |

### Pass Criteria
- Google Sign-In completes
- User authenticated
- Dashboard displayed

### Fail Criteria
- Google Sign-In fails
- No user created
- Error message shown

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# SECTION 2: PRODUCT CATALOG TEST CASES

## TC-PROD-001: List Products - Successful Retrieval

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-PROD-001 |
| **Linked Requirements** | BR-002, FR-PROD-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Backend running, Chargebee items synced |
| **Test Data** | Valid authentication token |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | GET /api/test/charge-items with auth | HTTP 200 OK | ⬜ |
| 2 | Verify response is array | Response body is JSON array | ⬜ |
| 3 | Verify products have required fields | id, name, description, prices present | ⬜ |
| 4 | Verify prices array not empty | Each product has at least 1 price | ⬜ |
| 5 | Verify product count | Count matches Chargebee items | ⬜ |

### Pass Criteria
- HTTP 200 returned
- Products list populated
- All required fields present

### Fail Criteria
- HTTP status != 200
- Empty product list
- Missing required fields

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-PROD-002: List Products - Unauthorized Access

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-PROD-002 |
| **Linked Requirements** | BR-002, FR-PROD-001 |
| **Test Type** | Unit Test (Backend) |
| **Priority** | P1 - High |
| **Preconditions** | None |
| **Test Data** | No authentication token |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | GET /api/test/charge-items without auth | HTTP 401 or 403 | ⬜ |
| 2 | Verify error message | "Unauthorized" or similar | ⬜ |

### Pass Criteria
- Request rejected
- Appropriate HTTP status

### Fail Criteria
- Products returned without auth
- HTTP 200 returned

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-PROD-003: Product Details - Display Information

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-PROD-003 |
| **Linked Requirements** | BR-002, FR-PROD-002 |
| **Test Type** | UI Test (Frontend) |
| **Priority** | P1 - High |
| **Preconditions** | Product list loaded |
| **Test Data** | Any product from list |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Tap on product from list | Product detail screen opens | ⬜ |
| 2 | Verify product name displayed | Name matches list | ⬜ |
| 3 | Verify product image displayed | Image visible | ⬜ |
| 4 | Verify description displayed | Description text present | ⬜ |
| 5 | Verify size options displayed | All size variants shown with prices | ⬜ |
| 6 | Verify "Add to Cart" button visible | Button enabled | ⬜ |

### Pass Criteria
- All product information displayed
- Size options visible
- Add to Cart button enabled

### Fail Criteria
- Missing product info
- No size options
- Button disabled

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# SECTION 3: SHOPPING CART TEST CASES

## TC-CART-001: Add to Cart - New Item

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-001 |
| **Linked Requirements** | BR-003, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P0 - Critical |
| **Preconditions** | Cart is empty |
| **Test Data** | Product: Juice A, Size: 250ml, Price: ₹100 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Select product and size | Product detail screen | ⬜ |
| 2 | Tap "Add to Cart" | Item added event triggered | ⬜ |
| 3 | Verify cart state updated | Cart contains 1 item | ⬜ |
| 4 | Verify cart badge updated | Badge shows "1" | ⬜ |
| 5 | Verify cart saved to storage | SharedPreferences updated | ⬜ |

### Pass Criteria
- Item added to cart
- Cart count updated
- Cart persisted

### Fail Criteria
- Item not added
- Count not updated
- Cart not saved

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-002: Add to Cart - Existing Item Same Size

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-002 |
| **Linked Requirements** | BR-003, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A (250ml) |
| **Test Data** | Same product, same size |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Add same product with same size | Add to Cart tapped | ⬜ |
| 2 | Verify quantity incremented | Quantity = 2 | ⬜ |
| 3 | Verify no duplicate item | Cart still has 1 item entry | ⬜ |
| 4 | Verify total price updated | Total = ₹200 | ⬜ |

### Pass Criteria
- Quantity incremented (not new item)
- Total price correct
- No duplicates

### Fail Criteria
- New item created
- Quantity not updated
- Wrong total

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-003: Add to Cart - Existing Item Different Size

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-003 |
| **Linked Requirements** | BR-003, FR-CART-001 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A (250ml) |
| **Test Data** | Same product, different size (500ml) |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Add same product with different size | Add to Cart tapped | ⬜ |
| 2 | Verify new item added | Cart has 2 items | ⬜ |
| 3 | Verify items are separate | 250ml and 500ml are separate entries | ⬜ |
| 4 | Verify total calculated correctly | Total = price(250ml) + price(500ml) | ⬜ |

### Pass Criteria
- New item added (not quantity increment)
- Different sizes are separate
- Total correct

### Fail Criteria
- Quantity incremented instead of new item
- Items merged incorrectly
- Wrong total

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-004: Update Cart Quantity - Increase

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-004 |
| **Linked Requirements** | BR-003, FR-CART-002 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A |
| **Test Data** | Quantity change: +1 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Tap "+" button on cart item | Quantity increment event | ⬜ |
| 2 | Verify quantity updated | Quantity = 2 | ⬜ |
| 3 | Verify total recalculated | Total increased by item price | ⬜ |
| 4 | Verify cart saved | SharedPreferences updated | ⬜ |

### Pass Criteria
- Quantity incremented
- Total updated
- Cart persisted

### Fail Criteria
- Quantity not changed
- Total wrong
- Cart not saved

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-005: Update Cart Quantity - Decrease to Zero

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-005 |
| **Linked Requirements** | BR-003, FR-CART-002 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has 1x Juice A |
| **Test Data** | Quantity change: -1 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Tap "-" button when quantity = 1 | Remove item confirmation or direct remove | ⬜ |
| 2 | Verify item removed | Cart has 0 items | ⬜ |
| 3 | Verify cart badge updated | Badge shows "0" or hidden | ⬜ |
| 4 | Verify empty cart state shown | "Your cart is empty" message | ⬜ |

### Pass Criteria
- Item removed
- Cart empty state shown
- Badge updated

### Fail Criteria
- Item not removed
- Quantity goes negative
- Empty state not shown

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-006: Calculate Cart Total - With Tax and Delivery

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-006 |
| **Linked Requirements** | BR-003, FR-CART-004 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P1 - High |
| **Preconditions** | Cart has items totaling ₹400 |
| **Test Data** | Subtotal: ₹400, Tax rate: 18%, Delivery: ₹40 |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Calculate cart totals | Totals computed | ⬜ |
| 2 | Verify subtotal | Subtotal = ₹400 | ⬜ |
| 3 | Verify tax calculation | Tax = ₹72 (18% of 400) | ⬜ |
| 4 | Verify delivery fee | Delivery = ₹40 (below ₹500) | ⬜ |
| 5 | Verify grand total | Total = ₹400 + ₹72 + ₹40 = ₹512 | ⬜ |

### Pass Criteria
- All calculations correct
- Tax rate 18%
- Delivery fee applied correctly

### Fail Criteria
- Wrong subtotal
- Wrong tax calculation
- Wrong delivery fee
- Wrong grand total

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CART-007: Calculate Cart Total - Free Delivery

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CART-007 |
| **Linked Requirements** | BR-003, FR-CART-004 |
| **Test Type** | Unit Test (Frontend BLoC) |
| **Priority** | P2 - Medium |
| **Preconditions** | Cart has items totaling ₹600 |
| **Test Data** | Subtotal: ₹600, Tax rate: 18%, Delivery: ₹0 (free) |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Calculate cart totals | Totals computed | ⬜ |
| 2 | Verify subtotal | Subtotal = ₹600 | ⬜ |
| 3 | Verify tax calculation | Tax = ₹108 (18% of 600) | ⬜ |
| 4 | Verify delivery fee | Delivery = ₹0 (above ₹500) | ⬜ |
| 5 | Verify grand total | Total = ₹600 + ₹108 = ₹708 | ⬜ |

### Pass Criteria
- Free delivery applied
- Total correct

### Fail Criteria
- Delivery fee charged
- Total wrong

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# SECTION 4: CHECKOUT TEST CASES

## TC-CHK-001: One-Time Checkout - Generate Hosted Page

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-001 |
| **Linked Requirements** | BR-004, FR-CHK-001 |
| **Test Type** | Integration Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | Cart has items, user authenticated |
| **Test Data** | Cart items with itemPriceIds |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/test/cartCheckout with cart items | HTTP 200 OK | ⬜ |
| 2 | Verify response contains URL | hosted_page.url present | ⬜ |
| 3 | Verify URL is valid Chargebee URL | URL starts with https://bookmyjuice-test.chargebee.com | ⬜ |
| 4 | Verify URL expiry | URL valid for 1 hour | ⬜ |

### Pass Criteria
- HTTP 200 returned
- Valid Chargebee URL provided
- URL accessible

### Fail Criteria
- HTTP status != 200
- No URL or invalid URL
- URL expired

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CHK-002: One-Time Checkout - Complete Payment Flow

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-002 |
| **Linked Requirements** | BR-004, FR-CHK-001 |
| **Test Type** | E2E Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Checkout URL obtained |
| **Test Data** | Chargebee test card details |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Open checkout URL in WebView | Chargebee page loads | ⬜ |
| 2 | Enter test card details | Card form filled | ⬜ |
| 3 | Submit payment | Payment processing | ⬜ |
| 4 | Verify payment success | Success page displayed | ⬜ |
| 5 | Verify return to app | App receives success callback | ⬜ |
| 6 | Verify order confirmation shown | Order confirmation screen | ⬜ |
| 7 | Verify cart cleared | Cart empty after order | ⬜ |

### Pass Criteria
- Payment completes successfully
- Order confirmation shown
- Cart cleared

### Fail Criteria
- Payment fails
- No confirmation
- Cart not cleared

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CHK-003: Subscription Checkout - Generate Plan URL

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-003 |
| **Linked Requirements** | BR-005, FR-CHK-002 |
| **Test Type** | Integration Test (Backend) |
| **Priority** | P0 - Critical |
| **Preconditions** | User authenticated |
| **Test Data** | Plan IDs: Premium, Signature, Delight |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | GET /api/test/generate_pricing_page_session_url | HTTP 200 OK | ⬜ |
| 2 | Verify response has 3 plan URLs | premium, signature, delight URLs present | ⬜ |
| 3 | Verify URLs are valid | All URLs are valid Chargebee URLs | ⬜ |
| 4 | Verify expiry | URLs valid for configured duration | ⬜ |

### Pass Criteria
- HTTP 200 returned
- All 3 plan URLs present
- URLs valid

### Fail Criteria
- HTTP status != 200
- Missing plan URLs
- Invalid URLs

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-CHK-004: Subscription Purchase - Complete Flow

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHK-004 |
| **Linked Requirements** | BR-005, FR-CHK-002 |
| **Test Type** | E2E Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Subscription plan URL obtained |
| **Test Data** | Chargebee test card |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Select subscription plan | Plan selected | ⬜ |
| 2 | Open plan URL in WebView | Chargebee subscription page loads | ⬜ |
| 3 | Enter payment details | Card form filled | ⬜ |
| 4 | Submit payment | Payment processing | ⬜ |
| 5 | Verify subscription activation | Success page with subscription details | ⬜ |
| 6 | Verify webhook received | Backend receives subscription.created webhook | ⬜ |
| 7 | Verify subscription visible in app | Subscription shown in user profile | ⬜ |

### Pass Criteria
- Subscription purchased
- Webhook processed
- Subscription visible in app

### Fail Criteria
- Payment fails
- Webhook not received
- Subscription not visible

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# SECTION 5: ORDER MANAGEMENT TEST CASES

## TC-ORD-001: View Order History - With Orders

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ORD-001 |
| **Linked Requirements** | BR-006, FR-ORD-001 |
| **Test Type** | E2E Test |
| **Priority** | P1 - High |
| **Preconditions** | User has placed 2+ orders |
| **Test Data** | User with order history |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Navigate to Order History screen | Screen loads | ⬜ |
| 2 | GET /api/test/ordersByCustomerId | HTTP 200 OK | ⬜ |
| 3 | Verify orders displayed | All orders shown | ⬜ |
| 4 | Verify order sorting | Newest first | ⬜ |
| 5 | Verify order details | Order number, date, total visible | ⬜ |

### Pass Criteria
- Orders displayed correctly
- Sorted by date (newest first)
- All details visible

### Fail Criteria
- Orders missing
- Wrong sort order
- Details missing

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-ORD-002: View Order History - No Orders

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ORD-002 |
| **Linked Requirements** | BR-006, FR-ORD-001 |
| **Test Type** | E2E Test |
| **Priority** | P2 - Medium |
| **Preconditions** | User has no orders |
| **Test Data** | New user |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Navigate to Order History screen | Screen loads | ⬜ |
| 2 | GET /api/test/ordersByCustomerId | HTTP 200 OK with empty array | ⬜ |
| 3 | Verify empty state shown | "No orders yet" message | ⬜ |
| 4 | Verify CTA button shown | "Start Shopping" or similar button | ⬜ |

### Pass Criteria
- Empty state displayed
- Call-to-action button present

### Fail Criteria
- Error shown
- Blank screen
- No CTA button

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-ORD-003: View Order Details

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ORD-003 |
| **Linked Requirements** | BR-006, FR-ORD-002 |
| **Test Type** | E2E Test |
| **Priority** | P1 - High |
| **Preconditions** | User has at least 1 order |
| **Test Data** | Order ID |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Tap on order from history | Order detail screen opens | ⬜ |
| 2 | GET /api/orders/{orderId} | HTTP 200 OK | ⬜ |
| 3 | Verify order items | All items listed with quantities | ⬜ |
| 4 | Verify pricing | Subtotal, tax, total shown | ⬜ |
| 5 | Verify order status | Status badge displayed | ⬜ |
| 6 | Verify order timeline | Status history shown | ⬜ |

### Pass Criteria
- All order details displayed
- Items, pricing correct
- Status and timeline shown

### Fail Criteria
- Missing details
- Wrong pricing
- No status/timeline

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

---

# SECTION 8: CHARGEBEE INTEGRATION TEST CASES

## TC-CHG-001: User-Customer Mapping During Signup

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-001 |
| **Linked Requirements** | ADR-003, FR-AUTH-001 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Chargebee test site configured |
| **Test Data** | Valid signup data |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | POST /api/auth/signup with valid data | HTTP 200 OK | ⬜ |
| 2 | Verify user created in users table | User record exists | ⬜ |
| 3 | Verify chargebee_customer_id stored | Field not null | ⬜ |
| 4 | Verify customer created in Chargebee | Customer exists via API | ⬜ |
| 5 | Verify email matches | Same email in both systems | ⬜ |

### Pass Criteria
- User created with chargebee_customer_id
- Customer exists in Chargebee
- One-to-one mapping established

### Fail Criteria
- User created without customer_id
- Customer not created in Chargebee
- Email mismatch

---

## TC-CHG-002: Webhook - Subscription Created

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-002 |
| **Linked Requirements** | ADR-003, FR-CHK-002 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Webhook endpoint configured |
| **Test Data** | Chargebee subscription.created event |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Trigger subscription.created webhook | HTTP 200 OK | ⬜ |
| 2 | Verify subscription created in local DB | Record exists | ⬜ |
| 3 | Verify subscription status | Status = active | ⬜ |
| 4 | Verify customer_id mapped | Matches Chargebee customer | ⬜ |
| 5 | Verify plan details synced | Plan ID, price correct | ⬜ |

### Pass Criteria
- Subscription in local DB
- Status matches Chargebee
- Customer mapping correct

### Fail Criteria
- Subscription not created
- Wrong status
- Customer mismatch

---

## TC-CHG-003: Webhook - Invoice Paid

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-003 |
| **Linked Requirements** | ADR-003, FR-CHK-001 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Webhook endpoint configured |
| **Test Data** | Chargebee invoice.paid event |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Trigger invoice.paid webhook | HTTP 200 OK | ⬜ |
| 2 | Verify invoice created in local DB | Record exists | ⬜ |
| 3 | Verify payment status | Status = paid | ⬜ |
| 4 | Verify amount matches | Amount correct | ⬜ |
| 5 | Verify order linked | Order ID present | ⬜ |

### Pass Criteria
- Invoice in local DB
- Payment status = paid
- Amount correct

### Fail Criteria
- Invoice not created
- Wrong status
- Amount mismatch

---

## TC-CHG-004: Product Catalog Sync (Startup)

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-004 |
| **Linked Requirements** | ADR-003, FR-PROD-001 |
| **Test Type** | Integration Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Chargebee has products/plans |
| **Test Data** | N/A |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Start bmjServer application | Application starts | ⬜ |
| 2 | Verify ChargebeeSyncService runs | Logs show sync started | ⬜ |
| 3 | Verify items synced | Items table populated | ⬜ |
| 4 | Verify plans synced | Plans table populated | ⬜ |
| 5 | Verify item_prices synced | Prices table populated | ⬜ |
| 6 | Verify categories (Delight, Signature, Premium) | All 3 categories exist | ⬜ |
| 7 | Verify sizes (200ml, 300ml, 500ml) | All sizes exist | ⬜ |

### Pass Criteria
- All products synced
- All plans synced
- Categories correct
- Sizes correct

### Fail Criteria
- Missing products
- Missing plans
- Wrong categories/sizes

---

## TC-CHG-005: Fetch Products from Local Cache

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-005 |
| **Linked Requirements** | ADR-003, FR-PROD-001 |
| **Test Type** | Unit Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Products synced to local DB |
| **Test Data** | N/A |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | GET /api/test/charge-items | HTTP 200 OK | ⬜ |
| 2 | Verify response time | < 100ms | ⬜ |
| 3 | Verify no Chargebee API call | Logs show DB query only | ⬜ |
| 4 | Verify all items returned | Count matches DB | ⬜ |
| 5 | Verify categories (Delight, Signature, Premium) | All present | ⬜ |
| 6 | Verify sizes (200ml, 300ml, 500ml) | All present | ⬜ |

### Pass Criteria
- Fast response (< 100ms)
- No Chargebee API call
- All items returned

### Fail Criteria
- Slow response (> 500ms)
- Chargebee API called
- Missing items

---

## TC-CHG-006: Fetch Subscriptions from Local Cache

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-006 |
| **Linked Requirements** | ADR-003, FR-SUB-001 |
| **Test Type** | Unit Test |
| **Priority** | P0 - Critical |
| **Preconditions** | User has subscriptions in local DB |
| **Test Data** | Valid JWT token |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | GET /api/subscriptions/active with auth | HTTP 200 OK | ⬜ |
| 2 | Verify response time | < 100ms | ⬜ |
| 3 | Verify no Chargebee API call | Logs show DB query only | ⬜ |
| 4 | Verify subscription details | Matches local DB | ⬜ |
| 5 | Verify plan details included | Plan name, price | ⬜ |

### Pass Criteria
- Fast response (< 100ms)
- No Chargebee API call
- Subscription details correct

### Fail Criteria
- Slow response
- Chargebee API called
- Wrong details

---

## TC-CHG-007: Webhook Failure Handling

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-CHG-007 |
| **Linked Requirements** | ADR-003 |
| **Test Type** | Integration Test |
| **Priority** | P1 - High |
| **Preconditions** | Webhook endpoint configured |
| **Test Data** | Invalid webhook payload |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Send invalid webhook payload | HTTP 400 Bad Request | ⬜ |
| 2 | Verify error logged | Error in logs | ⬜ |
| 3 | Verify no DB update | Data unchanged | ⬜ |
| 4 | Send duplicate webhook | HTTP 200 (idempotent) | ⬜ |
| 5 | Verify no duplicate records | Count unchanged | ⬜ |

### Pass Criteria
- Invalid payload rejected
- Errors logged
- Idempotent handling

### Fail Criteria
- Invalid payload accepted
- No error logging
- Duplicate records

---

# SECTION 9: PERFORMANCE TEST CASES

## TC-PERF-001: API Response Time - Login

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-PERF-001 |
| **Linked Requirements** | NFR-001 |
| **Test Type** | Performance Test |
| **Priority** | P1 - High |
| **Preconditions** | Backend running, test user exists |
| **Test Data** | Valid credentials |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Send 100 login requests sequentially | All requests complete | ⬜ |
| 2 | Measure response times | Record all times | ⬜ |
| 3 | Calculate p50, p95, p99 | Statistical analysis | ⬜ |
| 4 | Verify p95 < 2000ms | Performance target met | ⬜ |

### Pass Criteria
- p95 response time < 2000ms
- All requests successful

### Fail Criteria
- p95 > 2000ms
- Request failures

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-PERF-002: App Cold Start Time

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-PERF-002 |
| **Linked Requirements** | NFR-002 |
| **Test Type** | Performance Test |
| **Priority** | P2 - Medium |
| **Preconditions** | App not running |
| **Test Data** | None |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Launch app from cold state | App starts | ⬜ |
| 2 | Measure time to first frame | Record time | ⬜ |
| 3 | Repeat 10 times | 10 measurements | ⬜ |
| 4 | Calculate average | Average < 3000ms | ⬜ |

### Pass Criteria
- Average cold start < 3 seconds

### Fail Criteria
- Average > 3 seconds

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# SECTION 7: SECURITY TEST CASES

## TC-SEC-001: Password Storage - BCrypt Hashing

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-SEC-001 |
| **Linked Requirements** | NFR-005 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |
| **Preconditions** | User registered |
| **Test Data** | User credentials |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Query database for user password | Password field retrieved | ⬜ |
| 2 | Verify password is hashed | Not plain text | ⬜ |
| 3 | Verify hash format | Starts with $2a$, $2b$, or $2y$ | ⬜ |
| 4 | Verify cost factor | Cost factor = 10 | ⬜ |

### Pass Criteria
- Password hashed with BCrypt
- Cost factor 10

### Fail Criteria
- Plain text password
- Wrong hashing algorithm
- Wrong cost factor

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-SEC-002: API Authentication - JWT Validation

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-SEC-002 |
| **Linked Requirements** | NFR-006 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Valid JWT token obtained |
| **Test Data** | JWT token |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Call protected endpoint with valid token | HTTP 200 OK | ⬜ |
| 2 | Call protected endpoint with expired token | HTTP 401 Unauthorized | ⬜ |
| 3 | Call protected endpoint with invalid token | HTTP 401 Unauthorized | ⬜ |
| 4 | Call protected endpoint without token | HTTP 401 Unauthorized | ⬜ |

### Pass Criteria
- Valid token accepted
- Invalid/expired/missing tokens rejected

### Fail Criteria
- Invalid token accepted
- Valid token rejected

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

## TC-SEC-003: HTTPS Enforcement

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-SEC-003 |
| **Linked Requirements** | NFR-004 |
| **Test Type** | Security Test |
| **Priority** | P0 - Critical |
| **Preconditions** | Backend running |
| **Test Data** | None |

### Test Steps

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Attempt HTTP (non-HTTPS) connection | Connection rejected or redirected | ⬜ |
| 2 | Verify all API endpoints use HTTPS | All URLs start with https:// | ⬜ |
| 3 | Inspect network traffic with proxy | All traffic encrypted | ⬜ |

### Pass Criteria
- HTTP rejected/redirected
- All traffic encrypted

### Fail Criteria
- HTTP accepted
- Unencrypted traffic

### Actual Results
| Execution Date | Executed By | Result | Notes |
|----------------|-------------|--------|-------|
| | | ⏳ Pending | |

---

# Test Summary

| Module | Total Tests | Pass | Fail | Pending | Blocked |
|--------|-------------|------|------|---------|---------|
| Authentication | 8 | 0 | 0 | 8 | 0 |
| Product Catalog | 3 | 0 | 0 | 3 | 0 |
| Shopping Cart | 7 | 0 | 0 | 7 | 0 |
| Checkout | 4 | 0 | 0 | 4 | 0 |
| Order Management | 3 | 0 | 0 | 3 | 0 |
| Performance | 2 | 0 | 0 | 2 | 0 |
| Security | 3 | 0 | 0 | 3 | 0 |
| **TOTAL** | **30** | **0** | **0** | **30** | **0** |

---

# Test Execution Schedule

| Week | Test Phase | Test Cases |
|------|------------|------------|
| Week 1 | Unit Tests (Backend) | TC-AUTH-001 to 005, TC-PROD-001 to 002, TC-CHK-001, TC-SEC-001 to 003 |
| Week 2 | Unit Tests (Frontend) | TC-CART-001 to 007, TC-PROD-003 |
| Week 3 | Integration Tests | TC-AUTH-006 to 008, TC-CHK-002 to 004, TC-ORD-001 to 003 |
| Week 4 | E2E Tests | Full user flow tests |
| Week 5 | Performance Tests | TC-PERF-001 to 002 |
| Week 6 | UAT with Beta Users | All critical paths |

---

**Document Control:**
- **Created:** March 27, 2026
- **Last Updated:** March 27, 2026
- **Version:** 1.0
- **Status:** Draft - Pending Execution
