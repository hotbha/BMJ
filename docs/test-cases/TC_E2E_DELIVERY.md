# DELIVERY Module - E2E Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-18
> **Module:** DELIVERY
> **Test Type:** E2E (End-to-End Black-Box)
> **Linked BR:** BR-070 to BR-073
> **Linked UC:** UC-04, UC-10

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- Test accounts TA-01 (new user signup), TA-04 (existing user), TA-10 (saved address) created
- Pincode serviceability API configured: Serviceable=400001,400002,110001; Non-serviceable=999999,111111; Invalid=12,12345
- Delivery addresses mapped to subscriptions in MySQL
- Day-wise delivery schedule data configured for test subscriptions
- Delivery fee sourced from Chargebee pricing data

---

## TC-E2E-DEL-001: Enter valid delivery address during signup (all fields)

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-001 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User is in signup flow (TA-01). Address capture step before plan selection (BR-070). |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-070, UC-04 |

**Preconditions:**
- TA-01 is fresh install / new user, not completed signup
- User has entered OTP and verified
- Address capture screen displayed before plan selection

**Test Steps:**
1. Launch BookMyJuice app as new user (TA-01)
2. Enter mobile number (fresh not registered)
3. Enter OTP for verification
4. After OTP, observe address capture screen
5. Enter valid address:
   - Flat/House No: A-101
   - Society/Area: Sunshine Apartments, Andheri West
   - City: Mumbai
   - State: Maharashtra (dropdown)
   - Pincode: 400001 (serviceable)
6. Tap Next / Continue
7. Observe address saved, navigating to plan selection

**Expected Results:**
1. App launches, shows welcome/phone entry
2. Mobile entry works, OTP sent
3. OTP verified; user navigated to address screen
4. Address screen shows all required fields: Flat/House, Society/Area, City, State (dropdown), Pincode (6-digit numeric)
5. All fields accept valid input with proper keyboard types
6. Tapping Next triggers POST /api/v1/address
7. Address saved; user navigated to Plan Selection
8. Address stored in MySQL linked to user account (BR-070)

**Test Data:**
- User: TA-01 (fresh phone number)
- Address: Flat=A-101, Area=Sunshine Apartments, City=Mumbai, State=Maharashtra, Pincode=400001
- API: POST /api/v1/address
- Expected: 201 Created with address_id

---

## TC-E2E-DEL-002: Missing required address field - validation error

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-002 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User is in signup flow (TA-01). Address capture screen displayed. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-070, UC-04 |

**Preconditions:**
- TA-01 at address capture step
- User completed OTP verification

**Test Steps:**
1. Launch app, complete OTP as TA-01
2. On address screen, leave Flat/House No empty
3. Fill all other fields correctly
4. Tap Next / Continue
5. Observe validation error
6. Repeat for each required field (Area, City, State, Pincode)

**Expected Results:**
1. App launches; OTP verified; address screen shown
2. Flat/House No left empty
3. Other fields filled correctly
4. Tapping Next triggers client-side validation BEFORE API call
5. Error: Flat/House No is required
6. Field highlighted with red border
7. API call NOT made (client-side validation fires first)
8. Each required field shows respective error when empty
9. User can fix errors and proceed

**Test Data:**
- User: TA-01
- Missing fields tested one at a time: flat_no, area, city, state, pincode
- Expected: Client-side validation, no POST /api/v1/address call

---

## TC-E2E-DEL-003: Serviceable pincode - delivery available

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-003 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User in signup flow (TA-01). Pincode serviceability API configured. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-071, UC-04 |

**Preconditions:**
- TA-01 at address capture screen
- Serviceable test pincodes: 400001, 400002, 110001

**Test Steps:**
1. Launch app, complete OTP as TA-01
2. On address screen, locate Pincode field
3. Enter serviceable pincode: 400001
4. Tap outside field or wait for complete entry
5. Observe serviceability check indicator
6. Note visual feedback (checkmark, message)

**Expected Results:**
1. App launches; OTP verified; address screen shown
2. Pincode field is numeric input (6 digits)
3. User enters 400001
4. After entry, app calls GET /api/v1/serviceability?pincode=400001
5. API returns: serviceable:true, message:Delivery available in your area
6. UI: Green checkmark, text: Delivery available in your area
7. User can proceed with Next

**Test Data:**
- User: TA-01
- Serviceable pincode: 400001
- API: GET /api/v1/serviceability?pincode=400001
- Expected: serviceable: true

---

## TC-E2E-DEL-004: Non-serviceable pincode - delivery unavailable

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-004 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User in signup flow (TA-01). Pincode serviceability API configured. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-071, UC-04 |

**Preconditions:**
- TA-01 at address capture screen
- Non-serviceable test pincodes: 999999, 111111

**Test Steps:**
1. Launch app, complete OTP as TA-01
2. On address screen, enter non-serviceable pincode: 999999
3. Tap outside field or wait for complete entry
4. Observe serviceability check indicator
5. Note visual feedback (cross, error message)
6. Verify Next button disabled or form not submittable

**Expected Results:**
1. App launches; OTP verified; address screen shown
2. User enters 999999
3. After entry, app calls GET /api/v1/serviceability?pincode=999999
4. API returns: serviceable:false, message:Sorry, we do not deliver to this area yet
5. UI: Red cross, text: Sorry, we do not deliver to this area yet
6. Next/Continue button is disabled
7. User can try different pincode; check re-fires on change

**Test Data:**
- User: TA-01
- Non-serviceable pincode: 999999
- API: GET /api/v1/serviceability?pincode=999999
- Expected: serviceable: false

---

## TC-E2E-DEL-005: Day-wise schedule selection (Mon-Sat selectable, Sunday disabled as Holiday)

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-005 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User selected a plan during signup (TA-01). Day-wise schedule screen displayed. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-072, UC-10 |

**Preconditions:**
- TA-01 in signup flow, selected a subscription plan
- Day-wise delivery schedule component visible
- Catalogue of juices loaded

**Test Steps:**
1. Complete address, proceed to plan selection
2. Select a plan (e.g. Delight 200ml Weekly)
3. Navigate to Day-wise Delivery Schedule screen
4. Observe 7-day grid: Mon, Tue, Wed, Thu, Fri, Sat, Sun
5. Verify Mon-Sat have active selection UI (dropdown/picker)
6. Verify Sunday is Holiday (greyed out, non-interactive)
7. Attempt to tap/interact with Sunday
8. Select a juice for Monday from available options

**Expected Results:**
1. Signup proceeds to plan configuration
2. Plan selected successfully
3. Day-wise schedule screen displayed with 7 rows
4. Mon-Sat: Dropdown/picker to select juice (active, tappable)
5. Sun: Displayed as Holiday - greyed out (#E0E0E0), non-interactive
6. Tapping Sunday produces no response
7. Monday selection shows available juices matching plan category
8. Selection reflected in UI

**Test Data:**
- User: TA-01
- Plan: Delight 200ml Weekly
- Sunday: Holiday (disabled, greyed)
- Mon-Sat: Active with juice dropdown

---

## TC-E2E-DEL-006: Same juice everyday checkbox - one selection maps to all 6 days

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-006 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User configuring delivery schedule (TA-01). Same juice everyday checkbox visible. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-072, UC-10 |

**Preconditions:**
- TA-01 at day-wise schedule configuration screen
- Same juice everyday checkbox present

**Test Steps:**
1. Navigate to delivery schedule config screen
2. Observe Same juice everyday checkbox
3. Tap checkbox to enable it
4. Observe day-wise grid changes
5. Select a juice from single dropdown that appears
6. Verify all 6 days (Mon-Sat) show selected juice
7. Tap checkbox again to disable
8. Observe grid returns to independent selection mode

**Expected Results:**
1. Schedule screen displayed
2. Checkbox unchecked by default
3. After check: Grid collapses to single selector, text: Select juice for all days
4. User selects juice (e.g. Green Detox)
5. All 6 days (Mon-Sat) auto-populate with Green Detox
6. Sunday remains Holiday
7. After uncheck: Single selector disappears, 6 independent dropdowns return
8. All 6 days still show previously selected juice as default
9. User can independently change per day after unchecking

**Test Data:**
- User: TA-01
- Selected juice: Green Detox (or any matching plan)
- Expected: Check collapses 6 selectors to 1; one selection maps to all 6 days

---

## TC-E2E-DEL-007: Different juice per day (unchecked) - independent selection per day

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-007 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User configuring delivery schedule (TA-01). Same juice everyday unchecked. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-072, UC-10 |

**Preconditions:**
- TA-01 at schedule config screen
- Same juice everyday unchecked
- 6 independent selectors visible
- At least 6 different juices available

**Test Steps:**
1. Ensure Same juice everyday unchecked
2. Mon: select Green Detox
3. Tue: select Beetroot Boost
4. Wed: select Tropical Green
5. Thu: select Immunity Shot
6. Fri: select Protein Power
7. Sat: select Berry Blast
8. Verify each day shows its independent selection
9. Verify schedule summary reflects all 6 different selections

**Expected Results:**
1. Grid shows 6 independent dropdowns (Mon-Sat)
2. Mon: Green Detox
3. Tue: Beetroot Boost
4. Wed: Tropical Green
5. Thu: Immunity Shot
6. Fri: Protein Power
7. Sat: Berry Blast
8. Each day independent - changing one does NOT affect others
9. Sunday remains Holiday

**Test Data:**
- User: TA-01
- Mon: Green Detox, Tue: Beetroot Boost, Wed: Tropical Green, Thu: Immunity Shot, Fri: Protein Power, Sat: Berry Blast
- Sun: Holiday (fixed)

---

## TC-E2E-DEL-008: View/update saved delivery address

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-008 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has saved delivery address (TA-10). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-070, UC-10 |

**Preconditions:**
- TA-10 (existing user with saved address) exists
- Saved address: Flat=A-101, Area=Sunshine Apartments, City=Mumbai, State=Maharashtra, Pincode=400001
- User logged in

**Test Steps:**
1. Open app, login as TA-10
2. Navigate to Profile / Account Settings / My Address
3. Observe saved delivery address displayed
4. Verify all fields match known saved values
5. Tap Edit / Update button
6. Modify Flat to A-202
7. Tap Save / Update
8. Observe API call and response
9. Verify updated address displayed correctly

**Expected Results:**
1. Login succeeds
2. Profile / Account settings accessible
3. Current address displayed with all fields
4. All fields match saved address in MySQL
5. Edit button enables editing mode
6. User modifies Flat to A-202
7. Save triggers PUT /api/v1/address/:id
8. API returns 200 OK with updated address
9. Updated address shows A-202
10. Other fields unchanged

**Test Data:**
- User: TA-10
- Original: Flat=A-101, Area=Sunshine Apartments, City=Mumbai, State=Maharashtra, Pincode=400001
- Updated: Flat=A-202
- API: PUT /api/v1/address/:id

---

## TC-E2E-DEL-009: Delivery fee not returned in cart/order response — sourced from Chargebee

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-009 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has an order (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-073, UC-08 |

**Preconditions:**
- TA-04 has at least one order
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Order History
3. Tap any order to open Order Detail
4. Locate pricing/fee breakdown section
5. Verify NO delivery fee field is displayed
6. Check across multiple orders
7. Verify cart API response does not include delivery_fee key
8. Verify order API response does not include delivery_fee key

**Expected Results:**
1. Login succeeds
2. Order History loads
3. Order Detail opens
4. Pricing: Subtotal: Rs.X, Tax: Rs.X, Grand Total: Rs.X
5. No delivery_fee line item present in order display
6. Across all orders: no delivery_fee field in response
7. Cart GET /api/v1/cart response does NOT include delivery_fee in summary
8. Grand total = subtotal + tax (delivery fee from Chargebee)
9. Delivery fee is not calculated or returned by the app/backend — it is sourced from Chargebee pricing data

**Test Data:**
- User: TA-04
- Expected: delivery_fee NOT present in cart or order API responses
- Delivery fee sourced from Chargebee pricing data per BR-073

---

## TC-E2E-DEL-010: Invalid pincode format - validation

| Field | Value |
|-------|-------|
| ID | TC-E2E-DEL-010 |
| Module | DELIVERY |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User in signup flow (TA-01). Address capture screen displayed. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-071, UC-04 |

**Preconditions:**
- TA-01 at address capture screen
- Pincode field visible

**Test Steps:**
1. Launch app, complete OTP as TA-01
2. On address screen, locate Pincode field
3. Enter invalid pincode with fewer than 6 digits: 123
4. Tap outside field
5. Observe validation error
6. Clear, enter 5-digit: 12345
7. Observe validation
8. Clear, enter alphabetic: ABCDEF
9. Observe validation
10. Clear, enter 6-digit mixed: 12AB34
11. Observe validation

**Expected Results:**
1. App launches; OTP verified; address screen shown
2. Pincode field uses numeric keyboard (digits only)
3. Entering 3 digits: error or auto-reject
4. Error for <6 digits: Please enter a valid 6-digit pincode
5. 12345 -> error (must be exactly 6 digits)
6. Alphabetic: numeric keyboard prevents entry (or error: must contain only numbers)
7. Serviceability API NOT called for invalid formats
8. Next/Continue disabled until valid 6-digit entered

**Test Data:**
- User: TA-01
- Invalid pincodes: 123 (short), 12345 (5 digits), ABCDEF (alpha), 12AB34 (mixed)
- Expected: Client-side validation, no API call
- Error: Please enter a valid 6-digit pincode

---

## Summary of Test Cases

| ID | Description | Priority | Requirement |
|----|-------------|----------|-------------|
| TC-E2E-DEL-001 | Enter valid delivery address during signup (all fields) | P1-High | BR-070 |
| TC-E2E-DEL-002 | Missing required address field - validation error | P1-High | BR-070 |
| TC-E2E-DEL-003 | Serviceable pincode - delivery available | P1-High | BR-071 |
| TC-E2E-DEL-004 | Non-serviceable pincode - delivery unavailable | P1-High | BR-071 |
| TC-E2E-DEL-005 | Day-wise schedule (Mon-Sat selectable, Sun disabled) | P1-High | BR-072 |
| TC-E2E-DEL-006 | Same juice everyday checkbox - one selection maps to all 6 days | P1-High | BR-072 |
| TC-E2E-DEL-007 | Different juice per day - independent selection | P2-Medium | BR-072 |
| TC-E2E-DEL-008 | View/update saved delivery address | P1-High | BR-070 |
| TC-E2E-DEL-009 | Delivery fee not returned in cart/order response — sourced from Chargebee | P2-Medium | BR-073 |
| TC-E2E-DEL-010 | Invalid pincode format - validation | P2-Medium | BR-071 |

## BR Coverage Traceability

| BR ID | Requirement | Test Cases |
|-------|-------------|------------|
| BR-070 | Address captured during signup | DEL-001, DEL-002, DEL-008 |
| BR-071 | Pincode serviceability check | DEL-003, DEL-004, DEL-010 |
| BR-072 | Day-wise delivery schedule Mon-Sat, Sunday holiday | DEL-005, DEL-006, DEL-007 |
| BR-073 | Delivery fee sourced from Chargebee pricing data | DEL-009 |

## Document Control

- **Created:** 2026-05-18
- **Version:** 1.0
- **Status:** For Review
- **Total Test Cases:** 10
