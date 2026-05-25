# ORDERS Module - E2E Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-18
> **Module:** ORDERS
> **Test Type:** E2E (End-to-End Black-Box)
> **Linked BR:** BR-050 to BR-054
> **Linked UC:** UC-08, UC-09

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- Test accounts TA-04 (5+ orders) and TA-08 (0 orders) are created
- Orders stored in MySQL and synced via Chargebee webhooks
- bmjServer deployed at staging-api.bookmyjuice.co.in
- Chargebee test site accessible with invoice URLs
- Test payment cards for various payment statuses

---

## TC-E2E-ORD-001: View order history (user with 5+ orders)

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-001 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has 5+ orders in history (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, BR-052, UC-08 |

**Preconditions:**
- TA-04 has at least 5 orders in various statuses in MySQL
- Orders synced from Chargebee webhooks
- User logged in with valid JWT

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Orders / Order History screen
3. Wait for order list to load
4. Observe list of displayed orders
5. Verify each order card: Order ID, Status badge, Date, Grand total
6. Scroll through the list
7. Tap on an order to navigate to Order Detail

**Expected Results:**
1. Login succeeds
2. Order History screen opens with order list
3. Loading indicator during fetch, then disappears
4. At least 5 orders visible
5. Each card: Order ID, Status badge (colored), Date (DD/MM/YYYY), Grand total (Rs.X), Items count
6. Tapping navigates to Order Detail
7. All data matches MySQL records (BR-050)

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- Expected: 5+ orders
- API: GET /api/v1/orders

---

## TC-E2E-ORD-002: Pagination - page 1 returns 20, scroll fetches page 2

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-002 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has 25+ orders (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-052, UC-08 |

**Preconditions:**
- TA-04 has at least 25 orders in MySQL
- User logged in with valid JWT
- Network inspector running to capture API calls

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History screen
3. Observe first page loading
4. Count displayed orders
5. Scroll to bottom of list
6. Observe loading indicator for page 2
7. Observe next batch loading
8. Verify total count
9. Capture API call parameters

**Expected Results:**
1. Login succeeds
2. Order History loads
3. First page: exactly 20 orders (per_page=20)
4. API: GET /api/v1/orders?page=1&per_page=20
5. Scroll triggers auto-fetch of page 2
6. Loading indicator at bottom
7. Page 2 loads additional orders
8. API: GET /api/v1/orders?page=2&per_page=20
9. Total displayed = 25+
10. No duplicates between pages
11. Orders sorted newest first

**Test Data:**
- User: TA-04 with 25+ orders
- API: GET /api/v1/orders?page=N&per_page=20
- Expected: Page 1 = 20, Page 2 = remaining

---

## TC-E2E-ORD-003: View order details (items, pricing, shipping, status timeline)

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-003 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has an order with full details (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-053, UC-08 |

**Preconditions:**
- TA-04 has at least one order with known items, pricing, shipping, status history
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History
3. Tap on specific order to open Order Detail
4. Verify sections:
   a. Order header (Order ID, Status, Date)
   b. Items (names, quantities, unit prices, totals)
    c. Pricing (subtotal, tax, discount, grand total — delivery fee sourced from Chargebee)
   d. Shipping address (full address)
   e. Payment status
   f. Status timeline (if implemented)
   g. Invoice button (if available)

**Expected Results:**
1. Login succeeds
2. Order History loads
3. Order Detail opens
4. Sections display:
   a. Header: Order ID, Status badge, Date (DD/MM/YYYY)
   b. Items: name, qty, unit price, line total
   c. Pricing: Subtotal, Tax, Discount, Grand total (delivery fee sourced from Chargebee)
   d. Shipping: Flat, Area, City, State, Pincode, Country
   e. Payment status: Paid/Failed/Refunded
   f. Timeline: Pending -> Confirmed -> Preparing -> Shipped -> Delivered
   g. Invoice button if invoice exists
5. All pricing matches GET /api/v1/orders/:id
6. No local price calculation (BR-021)

**Test Data:**
- User: TA-04
- API: GET /api/v1/orders/:id
- Expected fields: id, status, payment_status, items[], subtotal, tax, discount, grand_total, shipping_address, created_at (delivery fee is not a separate field — sourced from Chargebee)

---

## TC-E2E-ORD-004: View invoice - opens Chargebee URL

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-004 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has order with invoice available (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-054, UC-09 |

**Preconditions:**
- TA-04 has order with chargebee_invoice_id set
- Invoice available in Chargebee
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order Detail for order with invoice
3. Tap View Invoice button
4. Observe URL opened
5. Verify URL is Chargebee-hosted (https://[site].chargebee.com/invoices/...)
6. Verify invoice page loads correctly

**Expected Results:**
1. Login succeeds
2. Order Detail shows View Invoice button
3. Tapping triggers GET /api/v1/orders/:id/invoice
4. API returns: invoice_url, invoice_id, amount, generated_at
5. Mobile opens invoice_url in in-app browser/WebView
6. URL format: https://bookmyjuice-test.chargebee.com/invoices/inv_xxx
7. Chargebee invoice page loads with proper details
8. No direct Chargebee API calls from mobile for invoice data

**Test Data:**
- User: TA-04
- API: GET /api/v1/orders/:id/invoice
- Expected: invoice_url (Chargebee URL), invoice_id, amount, generated_at

---

## TC-E2E-ORD-005: Order history with 0 orders - empty state

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-005 |
| Module | ORDERS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has 0 orders (TA-08: new user). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, UC-08 |

**Preconditions:**
- TA-08 (new user with 0 orders) exists
- TA-08 has 0 orders in MySQL
- User is logged in

**Test Steps:**
1. Open app, login as TA-08
2. Navigate to Order History screen
3. Observe the empty state UI

**Expected Results:**
1. Login succeeds
2. Order History loads
3. Empty state displayed: illustration/icon, Text: No orders yet, CTA: Start your first subscription, No loading indicator
4. API: GET /api/v1/orders -> returns empty array []
5. No errors or crash

**Test Data:**
- User: TA-08 (new user, no orders)
- API response: []

---

## TC-E2E-ORD-006: Order status badges correct (all statuses)

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-006 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has orders in all 6 statuses (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, BR-053, UI-002 |

**Preconditions:**
- TA-04 has at least one order in each: pending, confirmed, preparing, shipped, delivered, cancelled
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History
3. Scroll through orders, observe each status badge
4. For each status: note text, background color, icon
5. Tap one order of each status to verify badge matches on Detail screen

**Expected Results:**
1. Login succeeds; Order History loads
2. Six statuses with badges:
   - pending: Yellow/Amber (#FFC107), text: Pending
   - confirmed: Blue (#2196F3), text: Confirmed
   - preparing: Orange (#FF9800), text: Preparing
   - shipped: Purple (#9C27B0), text: Shipped
   - delivered: Green (#4CAF50), text: Delivered
   - cancelled: Red (#F44336), text: Cancelled
3. Colors consistent between List and Detail
4. Sufficient contrast (WCAG 2.1 AA, 4.5:1)

**Test Data:**
- User: TA-04
- Expected: pending, confirmed, preparing, shipped, delivered, cancelled
- API: GET /api/v1/orders

---

## TC-E2E-ORD-007: Verify order data matches refetched confirmed state (no optimism)

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-007 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has confirmed order (TA-04). Network inspector running. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, UC-08 |

**Preconditions:**
- TA-04 has a confirmed order with known data
- Network inspector active
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History
3. Tap confirmed order to open Order Detail
4. Capture all API calls
5. Observe app fetches data fresh (no client-side state reuse)
6. Compare displayed values vs API response

**Expected Results:**
1. Login succeeds; Order History loads
2. Tapping confirmed order navigates to Detail
3. Network trace: GET /api/v1/orders/:id - no cached/stale data
4. No optimistic or locally computed data displayed
5. All values (status, price, items, date) match API response exactly
6. Detail always shows latest server-side state (no optimism)

**Test Data:**
- User: TA-04
- API: GET /api/v1/orders/:id (fresh fetch on detail)

---

## TC-E2E-ORD-008: Order detail with failed payment status

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-008 |
| Module | ORDERS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S1-Major |
| Preconditions | User has order with payment_status=failed (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, BR-053, UC-08 |

**Preconditions:**
- TA-04 has at least one order where payment_status=failed
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order Detail for failed payment order
3. Observe payment status section
4. Check for error/warning indicators
5. Verify retry payment option (if implemented)
6. Observe overall order status

**Expected Results:**
1. Login succeeds
2. Order Detail opens
3. Payment status: Failed (Red badge/indicator)
4. Warning: Payment Failed label/visual indicator
5. Retry Payment button present (if implemented) and tappable
6. Order status separate from payment status
7. Retry opens payment flow

**Test Data:**
- User: TA-04
- Test card: 4000 0000 0000 0341 (Chargebee failure card) or equivalent
- Expected payment_status: failed

---

## TC-E2E-ORD-009: Invoice URL for order that has no invoice yet

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-009 |
| Module | ORDERS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has order without invoice (pending/failed payment). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-054, UC-09 |

**Preconditions:**
- TA-04 has at least one order where invoice NOT yet generated
- This could be pending or failed payment order
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order Detail for order without invoice
3. Observe invoice section/button
4. If button present, tap and observe response

**Expected Results:**
1. Login succeeds
2. Order Detail opens
3. View Invoice button: Disabled/greyed with Invoice not yet available, OR Not displayed
4. If tapped: toast: Invoice will be available once payment is processed
5. API: GET /api/v1/orders/:id/invoice returns invoice_id:null or 404
6. App handles missing invoice gracefully without crash

**Test Data:**
- User: TA-04
- Expected invoice: null/not available
- Expected UI: Invoice button disabled or hidden

---

## TC-E2E-ORD-010: Network error during order fetch - error state + retry

| Field | Value |
|-------|-------|
| ID | TC-E2E-ORD-010 |
| Module | ORDERS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has orders (TA-04). User logged in. Device can be put in Airplane mode. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-050, REQ-SYS-012 |

**Preconditions:**
- TA-04 has at least one order
- User logged in
- Ability to disable/enable network (Airplane mode / Charles breakpoint)

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History
3. While loading, disable network (Airplane mode)
4. Observe error state after timeout
5. Verify error message
6. Tap Retry button (or pull-to-refresh)
7. Re-enable network
8. Observe orders load successfully

**Expected Results:**
1. Login succeeds
2. Order History initiates fetch
3. Network error: Request timeout or connection failed
4. Error state: Illustration, Text: Unable to load orders. Retry button visible
5. Loading indicator dismissed
6. App does NOT crash or show blank screen
7. Retry initiates fresh GET /api/v1/orders
8. After network restored, orders load successfully
9. Error state leaves no stale/cached data

**Test Data:**
- User: TA-04
- Network: Working -> Disable -> Enable for retry
- Expected error UI: Illustration + text + retry button

---

## Summary of Test Cases

| ID | Description | Priority | Requirement |
|----|-------------|----------|-------------|
| TC-E2E-ORD-001 | View order history (5+ orders) | P1-High | BR-050, BR-052 |
| TC-E2E-ORD-002 | Pagination - page 1 returns 20, scroll fetches page 2 | P1-High | BR-052 |
| TC-E2E-ORD-003 | View order details (items, pricing, shipping) | P1-High | BR-053 |
| TC-E2E-ORD-004 | View invoice - opens Chargebee URL | P1-High | BR-054 |
| TC-E2E-ORD-005 | Order history with 0 orders - empty state | P2-Medium | BR-050 |
| TC-E2E-ORD-006 | Order status badges correct (all statuses) | P1-High | BR-050, BR-053 |
| TC-E2E-ORD-007 | Order data matches refetched confirmed state (no optimism) | P1-High | BR-050 |
| TC-E2E-ORD-008 | Order detail with failed payment status | P2-Medium | BR-050, BR-053 |
| TC-E2E-ORD-009 | Invoice URL for order with no invoice yet | P2-Medium | BR-054 |
| TC-E2E-ORD-010 | Network error during order fetch - error state + retry | P1-High | BR-050 |

## BR Coverage Traceability

| BR ID | Requirement | Test Cases |
|-------|-------------|------------|
| BR-050 | Order history from MySQL | ORD-001, ORD-005, ORD-006, ORD-007, ORD-010 |
| BR-051 | Chargebee is upstream via webhooks | ORD-001 (implied), ORD-007 |
| BR-052 | Pagination: 20/page | ORD-001, ORD-002 |
| BR-053 | Order details with items, pricing, shipping | ORD-003, ORD-006, ORD-008 |
| BR-054 | Invoice via Chargebee URL | ORD-004, ORD-009 |

## Document Control

- **Created:** 2026-05-18
- **Version:** 1.0
- **Status:** For Review
- **Total Test Cases:** 10
