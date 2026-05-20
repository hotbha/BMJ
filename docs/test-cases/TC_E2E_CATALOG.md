# CATALOG Module - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-19
> **Module:** PRODUCT CATALOG
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 12
> **Linked BR:** BR-008 (guest browsing), BR-010 to BR-012 (product catalog)
> **Linked UC:** UC-01 (Guest Browsing)

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- bmjServer deployed and accessible
- Chargebee test site has 18 plans configured (3 categories × 3 sizes × 2 frequencies) + one-time charge items
- Product images hosted on CDN/cloud storage and accessible
- Test accounts TA-01 through TA-10 available for authenticated browsing tests

---

## Table of Contents

1. [Guest Product Browsing (CAT-001 to CAT-006)](#1-guest-product-browsing)
2. [Authenticated Product Browsing (CAT-007 to CAT-010)](#2-authenticated-product-browsing)
3. [Edge Cases (CAT-011 to CAT-012)](#3-edge-cases)

---

## 1. Guest Product Browsing

### TC-E2E-CAT-CAT-001: Guest user browses product catalog without authentication

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-008, BR-010 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install or logged-out state (no JWT)

**Test Steps:**
1. Open app → see Home/Dashboard screen
2. Verify no login prompt for browsing
3. Scroll through product list horizontally
4. Tap on a product card/view

**Expected Results:**
1. Product catalog loads without requiring authentication
2. Products display: name, image, category badge, price info
3. Categories visible: Delight, Signature, Premium
4. Product detail screen shows: image, name, description, one-time price, subscription plans (weekly/monthly)
5. Guest browsing permits all read operations

**Test Data:**
- N/A (guest browsing)

---

### TC-E2E-CAT-CAT-002: Product displays both one-time and subscription pricing

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-010, BR-011 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest on product detail screen

**Test Steps:**
1. Tap on a product to open detail screen
2. Observe pricing section

**Expected Results:**
1. One-time price displayed clearly (e.g. 'One-Time: ₹75')
2. Subscription pricing shown for weekly and monthly frequencies (e.g. 'Weekly: ₹400' and 'Monthly: ₹1,500')
3. All prices shown in INR with correct formatting (mobile divides cents by 100)
4. No duplicate or missing pricing options

**Test Data:**
- Any available product

---

### TC-E2E-CAT-CAT-003: Products filtered by category

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-012 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest on Home/category screen

**Test Steps:**
1. Locate category filter/tabs on Home screen
2. Tap 'Delight' category
3. Observe filtered products
4. Tap 'Signature' category
5. Tap 'Premium' category

**Expected Results:**
1. Category filter available and responsive
2. Delight filter shows only Delight-category products
3. Signature filter shows only Signature-category products
4. Premium filter shows only Premium-category products
5. Products correctly categorized (no cross-category leakage)

**Test Data:**
- All 3 categories: Delight, Signature, Premium

---

### TC-E2E-CAT-CAT-004: Guest cannot add to cart without authentication (PD-01)

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-008 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Guest browsing products
- [ ] Product detail screen open

**Test Steps:**
1. Tap 'Add to Cart' or equivalent button
2. Observe system response

**Expected Results:**
1. System prompts: 'Please log in or sign up to add items to cart' or equivalent
2. User is redirected to Login/Signup screen
3. Guest cannot proceed to cart operations without authentication
4. Product browsing still accessible after returning from login prompt

**Test Data:**
- N/A (auth enforcement)

---

### TC-E2E-CAT-CAT-005: Guest product browsing — network error handling

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-008, NFR-001 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Ability to toggle airplane mode

**Test Steps:**
1. Enable airplane mode
2. Open app and navigate to Home screen
3. Observe product list area

**Expected Results:**
1. Loading indicator shown initially
2. Error message: 'Network error. Unable to load products.' or similar
3. Retry button available
4. Disable airplane mode → tap Retry → products load successfully

**Test Data:**
- N/A (network error test)

---

### TC-E2E-CAT-CAT-006: Product catalog loads within 2 seconds (p95)

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-012, NFR-001 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**

**Test Steps:**
1. Clear app cache
2. Open app and navigate to Home screen
3. Start timer when product list starts loading
4. Stop timer when all products visible

**Expected Results:**
1. Products render within 2 seconds on stable connection
2. Lazy loading or pagination if many products (but MVP < 20 products expected)
3. No blank screen > 2 seconds

**Test Data:**
- N/A (performance test)

---

## 2. Authenticated Product Browsing

### TC-E2E-CAT-CAT-007: Authenticated user browses product catalog

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-008, BR-010 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with valid JWT

**Test Steps:**
1. Open app → Dashboard loads (auto-login)
2. Navigate to product listing (Home screen)
3. Browse products across all categories
4. Tap product for details

**Expected Results:**
1. Products load with authentication context
2. Same product data as guest browsing (no additional hidden products)
3. Add to Cart button available (not redirecting to login)

**Test Data:**
- TA-01 credentials, product catalog

---

### TC-E2E-CAT-CAT-008: Authenticated user views subscription plans per product

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-010, BR-011 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in

**Test Steps:**
1. Open product detail screen
2. Scroll to subscription pricing section
3. Verify 2 frequency options shown: Weekly and Monthly
4. Verify all 3 size variants accessible (200ml, 300ml, 500ml)

**Expected Results:**
1. Each product shows Weekly and Monthly subscription prices
2. Prices correctly displayed in ₹
3. Size variants correctly shown with their respective pricing

**Test Data:**
- Any product with subscription plans

---

### TC-E2E-CAT-CAT-009: One-time price correctly formatted (cents to rupees)

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Product detail screen open
- [ ] Access to raw API response for verification

**Test Steps:**
1. Call GET /api/v1/products and capture response
2. Note one_time_price.price value (in cents)
3. Compare displayed price on UI

**Expected Results:**
1. UI price = API price (cents) / 100, formatted as ₹X.XX
2. Example: API returns 7500 → UI shows '₹75' or '₹75.00'
3. No rounding errors or misplaced decimal

**Test Data:**
- API response for any product, e.g. one_time_price.price = 7500

---

### TC-E2E-CAT-CAT-010: Empty product category shows appropriate message

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-012 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in
- [ ] Ability to simulate empty category (or use test scenario)

**Test Steps:**
1. If a category has no products, navigate to that category tab/filter
2. Observe UI

**Expected Results:**
1. Empty state message: 'No products in this category yet' or similar
2. Suggest other categories to browse
3. No crash or blank screen

**Test Data:**
- Empty category simulation

---

## 3. Edge Cases

### TC-E2E-CAT-CAT-011: Product image fails to load — fallback displayed

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Product detail screen open

**Test Steps:**
1. Simulate network blocking image CDN (e.g. firewall rule or proxy)
2. Navigate to product detail screen
3. Observe image area

**Expected Results:**
1. Placeholder/fallback image displayed when CDN link fails
2. Product name and pricing still visible
3. No crash or blank card

**Test Data:**
- N/A (image failure test)

---

### TC-E2E-CAT-CAT-012: Very long product name displayed correctly

| Field | Value |
|-------|-------|
| **Module** | CATALOG |
| **Type** | E2E (Black Box) |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-01 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Product with long name exists (or can be seeded)

**Test Steps:**
1. Navigate to product with unusually long name
2. Observe product card and detail screen

**Expected Results:**
1. Long name truncated with ellipsis on product card (single line)
2. Full name visible on product detail screen (multi-line if needed)
3. No layout breakage or overflow

**Test Data:**
- Product with name > 30 characters

---

