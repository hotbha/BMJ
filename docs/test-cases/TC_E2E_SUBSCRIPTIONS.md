# SUBSCRIPTIONS Module - E2E Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-18
> **Module:** SUBSCRIPTIONS
> **Test Type:** E2E (End-to-End Black-Box)
> **Linked BR:** BR-040 to BR-047
> **Linked UC:** UC-05, UC-06, UC-07

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- Test accounts TA-04 (active), TA-06 (paused), TA-07 (cancelled), TA-09 (multiple sub) created
- 18 subscription plans configured: 3 categories x 3 sizes x 2 frequencies
- bmjServer deployed at staging-api.bookmyjuice.co.in
- System clock set to IST for 9 PM cutoff tests
- Chargebee test site accessible

---

## TC-E2E-SUB-001: View list of all subscriptions (multiple active)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-001 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has 2+ active subs (TA-09). User logged in with valid JWT. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-040, BR-047, UC-05 |

**Preconditions:**
- TA-09 (user with multiple subscriptions) exists
- TA-09 has at least 2 active subscriptions
- User logged into mobile app with TA-09 credentials
- JWT token is valid

**Test Steps:**
1. Launch the BookMyJuice mobile app
2. Log in with TA-09 credentials
3. Navigate to Dashboard / Subscriptions section
4. Wait for subscription list to load completely
5. Observe the list of displayed subscriptions
6. Tap on each subscription to view details

**Expected Results:**
1. Dashboard loads without errors; loading indicator shown
2. Login succeeds; user navigated to Dashboard
3. Subscriptions section displays all subscriptions of TA-09
4. Loading indicator appears and disappears; subscriptions displayed
5. At least 2 active subscriptions visible in list
6. Each card shows: Plan name, Status badge (Green), Billing period, Dates
7. Tapping navigates to Subscription Detail screen

**Test Data:**
- User: TA-09 (9876543212 / e2e-existing@bookmyjuice.co.in)
- Subscriptions: 2+ active in Chargebee synced to MySQL
- API: GET /api/v1/subscriptions

---

## TC-E2E-SUB-002: View single subscription details

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-002 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has at least one active subscription (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-040, UC-05 |

**Preconditions:**
- TA-04 (user with active subscription) exists
- Subscription has known chargebee_subscription_id, plan_id, status, dates
- User is logged into the mobile app

**Test Steps:**
1. Open the app and log in as TA-04
2. Navigate to the Subscriptions list
3. Tap on the active subscription card to open Subscription Detail screen
4. Verify all fields displayed on the detail screen

**Expected Results:**
1. App opens and login succeeds
2. Subscriptions list is displayed with at least one active subscription
3. Detail screen shows: Plan name, Category, Status (Green Active), Term dates, Next billing date, Amount, Items
4. All data matches GET /api/v1/subscriptions/:id

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- API: GET /api/v1/subscriptions/:id

---

## TC-E2E-SUB-003: Pause active subscription (before 9 PM) - success

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-003 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). Current time < 9 PM IST. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-041, BR-044, BR-045, BR-046, UC-05 |

**Preconditions:**
- TA-04 has at least one active subscription
- System clock set to IST, time before 9:00 PM
- User logged in with valid JWT

**Test Steps:**
1. Open the app and log in as TA-04
2. Navigate to Subscription Detail screen
3. Verify status badge shows Active (Green)
4. Tap the Pause Subscription button
5. Observe confirmation dialog
6. Verify dialog: Pause delivery starting [date]? You can resume anytime.
7. Tap Confirm (Yes, Pause)
8. Observe loading indicator during API call
9. Verify mobile calls POST /api/v1/subscriptions/:id/pause (not direct to Chargebee)
10. Observe mobile auto-calls GET /api/v1/subscriptions/:id to refetch
11. Verify status is now Paused (Orange badge)
12. Verify pause confirmation toast

**Expected Results:**
1. Login succeeds; user on Dashboard
2. Subscription Detail screen shows all details
3. Status badge is Green Active
4. Pause Subscription button is tappable
5. Confirmation dialog appears with message
6. Dialog has Cancel and Confirm buttons
7. Loading indicator appears; button in progress state
8. Mobile calls POST to bmjServer - NOT Chargebee directly (BR-045)
9. Backend returns HTTP 202 Accepted
10. Mobile immediately calls GET to refetch (BR-046)
11. Status badge changes to Orange Paused
12. Toast shows: Subscription paused successfully

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- API: POST /api/v1/subscriptions/:id/pause
- Expected response: 202 Accepted
- Time: Before 21:00 IST

---

## TC-E2E-SUB-004: Pause active subscription (after 9 PM) - rejected

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-004 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). Current time >= 9 PM IST. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-041, BR-045, BR-046, UC-05 |

**Preconditions:**
- TA-04 has at least one active subscription
- System clock shows time at or after 9:00 PM IST
- User is logged in

**Test Steps:**
1. Open the app and log in as TA-04
2. Navigate to Subscription Detail screen
3. Tap Pause Subscription button
4. Confirm in the dialog
5. Observe API call response
6. Verify error message displayed
7. Verify status remains Active (Green)
8. Verify mobile does NOT refetch

**Expected Results:**
1. Login succeeds
2. Detail screen shows Active (Green)
3. Pause button is tappable
4. Dialog appears; user confirms
5. Mobile calls POST /api/v1/subscriptions/:id/pause
6. Backend returns 400 Bad Request - cutoff exceeded
7. Error: Actions available until 9 PM. Changes take effect next day.
8. Status badge remains Green Active
9. No refetch GET call made

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- Execution Time: >= 21:00 IST
- Expected error: Actions available until 9 PM. Changes will take effect next day.

---

## TC-E2E-SUB-005: Resume paused subscription (before 9 PM) - success

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-005 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has paused sub (TA-06). Current time < 9 PM IST. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-042, BR-044, BR-045, BR-046, UC-06 |

**Preconditions:**
- TA-06 (paused subscription user) exists
- Subscription status is paused in Chargebee and MySQL
- System clock shows time before 9:00 PM IST
- User is logged in

**Test Steps:**
1. Open the app and log in as TA-06
2. Navigate to Subscription Detail screen
3. Verify status badge shows Paused (Orange)
4. Tap Resume Subscription button
5. Observe confirmation dialog: Resume your subscription starting immediately?
6. Tap Confirm
7. Observe loading indicator during API call
8. Verify mobile calls POST /api/v1/subscriptions/:id/resume (not Chargebee)
9. Verify 202 Accepted response
10. Observe mobile calls GET /api/v1/subscriptions/:id to refetch
11. Verify status changed to Active (Green badge)
12. Verify success toast

**Expected Results:**
1. Login succeeds
2. Detail screen shows paused subscription
3. Status badge Orange with Paused text
4. Resume button is visible and tappable
5. Confirmation dialog: Resume your subscription starting immediately?
6. Dialog has Cancel and Confirm buttons
7. Loading indicator shown
8. Mobile calls POST to bmjServer (BR-045)
9. Backend returns 202 Accepted
10. Mobile auto-calls GET to refetch (BR-046)
11. Status badge updates to Green Active
12. Toast: Subscription resumed successfully

**Test Data:**
- User: TA-06 (paused subscription user)
- API: POST /api/v1/subscriptions/:id/resume
- Expected response: 202 Accepted
- Time: Before 21:00 IST

---

## TC-E2E-SUB-006: Resume paused subscription (after 9 PM) - rejected

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-006 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has paused sub (TA-06). Current time >= 9 PM IST. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-042, BR-045, BR-046, UC-06 |

**Preconditions:**
- TA-06 (paused subscription user) exists
- System clock shows time at or after 9:00 PM IST
- User is logged in

**Test Steps:**
1. Open the app and log in as TA-06
2. Navigate to Subscription Detail screen
3. Verify status badge shows Paused (Orange)
4. Tap Resume Subscription button
5. Confirm in the dialog
6. Observe API response
7. Verify error message
8. Verify status remains Paused

**Expected Results:**
1. Login succeeds
2. Detail screen shows paused subscription
3. Status badge Orange Paused
4. Resume button is visible
5. Dialog appears; user confirms
6. Mobile calls POST /api/v1/subscriptions/:id/resume to bmjServer (BR-045)
7. Backend returns 400 Bad Request - cutoff exceeded
8. Error: Actions available until 9 PM. Changes will take effect next day.
9. Status remains Paused
10. No refetch call made

**Test Data:**
- User: TA-06 (paused subscription user)
- Execution Time: >= 21:00 IST
- Expected error: Actions available until 9 PM. Changes will take effect next day.

---

## TC-E2E-SUB-007: Cancel subscription (end of term)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-007 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-043, BR-045, BR-046, UC-07 |

**Preconditions:**
- TA-04 has at least one active subscription
- Subscription has known current_term_end date
- User logged in with valid JWT

**Test Steps:**
1. Open the app and log in as TA-04
2. Navigate to Subscription Detail screen
3. Tap Cancel Subscription button
4. Observe cancel options dialog: Immediately, End of Term, Specific Date
5. Select End of Term
6. Observe confirmation showing term end date
7. Tap Confirm Cancellation
8. Observe loading indicator
9. Verify POST /api/v1/subscriptions/:id/cancel (cancel_option=end_of_term)
10. Verify 202 Accepted response
11. Observe mobile calls GET to refetch
12. Verify scheduled cancellation banner displayed
13. Verify toast: Cancellation scheduled for end of term

**Expected Results:**
1. Login succeeds
2. Subscription Detail screen shown
3. Cancel Subscription button is tappable
4. Cancel options dialog with 3 options
5. End of Term selected
6. Confirmation shows term end date
7. User confirms
8. Loading indicator appears
9. API call to bmjServer with end_of_term (BR-045)
10. Backend returns 202 Accepted
11. Mobile refetches via GET (BR-046)
12. UI: Cancellation scheduled for DD/MM/YYYY + Remove button
13. Toast: Cancellation scheduled for end of term

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- Body: cancel_option = end_of_term
- Expected: 202 Accepted

---

## TC-E2E-SUB-008: Cancel subscription (immediately)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-008 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-043, BR-045, BR-046, UC-07 |

**Preconditions:**
- TA-04 has at least one active subscription
- User is logged in

**Test Steps:**
1. Open the app and log in as TA-04
2. Navigate to Subscription Detail screen
3. Tap Cancel Subscription button
4. In cancel options dialog, select Immediately
5. Observe confirmation warning about immediate effects
6. Tap Confirm Cancellation
7. Observe loading indicator
8. Verify POST with cancel_option=immediately
9. Verify 202 Accepted
10. Observe mobile refetches via GET
11. Verify status is Cancelled (Red badge)
12. Verify toast: Subscription cancelled immediately

**Expected Results:**
1. Login succeeds
2. Detail screen shown
3. Cancel button tappable
4. Immediately selected
5. Confirmation with warning
6. User confirms
7. Loading indicator
8. API call to bmjServer (BR-045)
9. 202 Accepted
10. Refetch via GET (BR-046)
11. Status badge Red Cancelled
12. Toast: Subscription cancelled immediately
13. Action buttons update (New Subscription shown)

**Test Data:**
- User: TA-04
- Body: cancel_option = immediately
- Expected: 202 Accepted

---

## TC-E2E-SUB-009: Cancel subscription (specific date)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-009 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). Future cancellation date available. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-043, BR-045, BR-046, UC-07 |

**Preconditions:**
- TA-04 has at least one active subscription
- A future cancellation date is available (within current term)
- User is logged in

**Test Steps:**
1. Open app, log in as TA-04
2. Navigate to Subscription Detail
3. Tap Cancel Subscription
4. Select Specific Date
5. Date picker appears
6. Select a future date
7. Tap Confirm Cancellation
8. Observe loading indicator
9. Verify POST with cancel_option=specific_date + cancellation_date
10. Verify 202 Accepted
11. Observe refetch via GET
12. Verify scheduled cancellation banner with selected date
13. Verify Remove button visible

**Expected Results:**
1. Login succeeds
2. Detail screen shown
3. Cancel button tappable
4. Specific Date selected
5. Date picker displayed
6. Future date selected (past dates disabled)
7. User confirms
8. Loading indicator
9. API call to bmjServer with date (BR-045)
10. 202 Accepted
11. Refetch via GET (BR-046)
12. Banner: Cancellation scheduled for DD/MM/YYYY
13. Remove button visible

**Test Data:**
- User: TA-04
- Body: cancel_option=specific_date, cancellation_date=2026-06-15
- Expected: 202 Accepted

---

## TC-E2E-SUB-010: Cancel already cancelled subscription - error

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-010 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has cancelled sub (TA-07). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-043, UC-07 |

**Preconditions:**
- TA-07 (cancelled subscription user) exists
- Subscription status is cancelled in Chargebee and MySQL
- User is logged in

**Test Steps:**
1. Open app, log in as TA-07
2. Navigate to Subscription Detail for cancelled sub
3. Verify status badge shows Cancelled (Red)
4. Verify Cancel button is NOT visible or is disabled
5. If present but disabled, tap and observe

**Expected Results:**
1. Login succeeds
2. Detail screen shows cancelled subscription
3. Status badge Red Cancelled
4. Cancel button: Not visible (preferred) or Disabled with tooltip
5. No cancel action possible
6. Appropriate buttons for cancelled state shown (New Subscription)

**Test Data:**
- User: TA-07 (cancelled subscription user)
- Expected cancel action: Disabled or hidden

---

## TC-E2E-SUB-011: Remove scheduled cancellation

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-011 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub with scheduled cancellation (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-043, BR-045, BR-046, UC-07 |

**Preconditions:**
- TA-04 sub has scheduled cancellation (end_of_term or specific_date)
- Detail screen shows cancellation banner and Remove button
- User is logged in

**Test Steps:**
1. Open app, log in as TA-04
2. Navigate to Subscription Detail
3. Verify cancellation banner displayed
4. Verify Remove Scheduled Cancellation button visible
5. Tap Remove Scheduled Cancellation
6. Confirm: Remove the scheduled cancellation?
7. Tap Confirm
8. Observe loading indicator
9. Verify POST /api/v1/subscriptions/:id/remove-scheduled-cancellation
10. Verify 202 Accepted
11. Observe refetch via GET
12. Verify banner is gone
13. Verify status back to Active (Green)
14. Verify Cancel button available again

**Expected Results:**
1. Login succeeds
2. Detail screen shows cancellation banner
3. Banner: Cancellation scheduled for DD/MM/YYYY
4. Remove button is tappable
5. Confirmation dialog appears
6. User confirms
7. Loading indicator
8. API call to bmjServer (BR-045)
9. 202 Accepted
10. Refetch via GET (BR-046)
11. Banner removed
12. Status badge Green Active
13. Cancel button available with all options

**Test Data:**
- User: TA-04
- API: POST /api/v1/subscriptions/:id/remove-scheduled-cancellation
- Expected: 202 Accepted

---

## TC-E2E-SUB-012: Pause already paused subscription - error

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-012 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has paused sub (TA-06). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-041, BR-044, UC-05 |

**Preconditions:**
- TA-06 (paused) exists
- Subscription paused in Chargebee and MySQL
- User is logged in

**Test Steps:**
1. Open app, log in as TA-06
2. Navigate to Subscription Detail
3. Verify status badge Paused (Orange)
4. Verify Pause button NOT visible or disabled
5. Observe available action buttons

**Expected Results:**
1. Login succeeds
2. Detail screen shows paused
3. Status badge Orange Paused
4. Pause button: Not visible or Disabled
5. Resume Subscription button is shown (primary action)

**Test Data:**
- User: TA-06
- Expected pause action: Disabled or hidden

---

## TC-E2E-SUB-013: Multiple pause/resume cycles (5+ cycles)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-013 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has active sub (TA-04). Time < 9 PM. User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-041, BR-042, BR-044, BR-045, BR-046 |

**Preconditions:**
- TA-04 has active subscription
- System clock before 9:00 PM IST
- User logged in

**Test Steps (repeat 5+ times):**
1. Navigate to Subscription Detail
2. Perform pause (per TC-SUB-003 steps)
3. Verify status changes to Paused (Orange)
4. Perform resume (per TC-SUB-005 steps)
5. Verify status back to Active (Green)
6. Record cycle number

**Expected Results:**
1. Each pause succeeds (202), status -> Paused
2. Each resume succeeds (202), status -> Active
3. All 5+ cycles complete without error
4. No rate limiting (BR-044: unlimited cycles)
5. Each action: bmjServer (BR-045) + refetch (BR-046)
6. UI correctly reflects status after each cycle

**Test Data:**
- User: TA-04
- Cycles: 5+
- Per cycle: POST pause->202->GET->Paused->POST resume->202->GET->Active

---

## TC-E2E-SUB-014: POST returns 202 - mobile refetches - confirmed state

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-014 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P1-High |
| Severity | S1-Major |
| Preconditions | User has active sub (TA-04). Time < 9 PM. Network inspector running. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-045, BR-046, UC-05 |

**Preconditions:**
- TA-04 has active subscription
- System clock before 9:00 PM IST
- User logged in
- Charles Proxy / adb logcat running

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Subscription Detail
3. Initiate pause (tap Pause + Confirm)
4. Capture network sequence of API calls
5. Verify call order and status codes
6. Verify mobile does NOT update UI before refetched data

**Expected Results:**
1. Login succeeds; detail screen shown
2. Pause action triggered
3. Network trace:
   - Call 1: POST /api/v1/subscriptions/:id/pause -> 202 Accepted
   - Call 2: GET /api/v1/subscriptions/:id -> 200 OK status:paused
4. Mobile does NOT show Paused optimistically after Call 1
5. Mobile waits for Call 2 before updating UI
6. UI updates to Paused (Orange) ONLY after Call 2 confirms
7. No direct Chargebee calls from mobile (BR-045)

**Test Data:**
- User: TA-04
- Sequence: POST->202->GET->200 (confirmed)
- No optimistic UI updates permitted

---

## TC-E2E-SUB-015: Subscription status color coding (UI)

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-015 |
| Module | SUBSCRIPTIONS |
| Type | E2E (Visual) |
| Priority | P2-Medium |
| Severity | S3-Trivial |
| Preconditions | Users TA-04 (Active), TA-06 (Paused), TA-07 (Cancelled). User logged in. |
| Automation Status | To Be Automated (screenshot comparison) |
| Linked BR/UC | BR-040, UI-003 |

**Preconditions:**
- TA-04 (Active), TA-06 (Paused), TA-07 (Cancelled) exist
- User logged in

**Test Steps:**
1. Login as TA-04, navigate to Subscriptions list
2. Observe Active status badge color
3. Logout, login as TA-06
4. Observe Paused badge color
5. Logout, login as TA-07
6. Observe Cancelled badge color
7. Record hex/RGB values

**Expected Results:**
1. Active badge: Green (e.g. #4CAF50) with Active text
2. Paused badge: Orange (e.g. #FF9800) with Paused text
3. Cancelled badge: Red (e.g. #F44336) with Cancelled text
4. Sufficient contrast (WCAG 2.1 AA, 4.5:1)
5. Badges on list and detail screens

**Test Data:**
- Users: TA-04 (Active), TA-06 (Paused), TA-07 (Cancelled)
- Expected: Active=Green, Paused=Orange, Cancelled=Red

---

## TC-E2E-SUB-016: View delivery schedule for subscription

| Field | Value |
|-------|-------|
| ID | TC-E2E-SUB-016 |
| Module | SUBSCRIPTIONS |
| Type | E2E |
| Priority | P2-Medium |
| Severity | S2-Minor |
| Preconditions | User has active sub with delivery schedule (TA-04). User logged in. |
| Automation Status | To Be Automated |
| Linked BR/UC | BR-040, BR-072 |

**Preconditions:**
- TA-04 has active sub with delivery schedule in metadata
- Schedule JSON: Mon-Sat juice selections, Sunday holiday
- User logged in

**Test Steps:**
1. Open app, login as TA-04
2. Navigate to Subscription Detail
3. Locate Delivery Schedule section
4. Verify Mon-Sat displayed with assigned juices
5. Verify Sunday shown as Holiday (greyed out)
6. Verify each day shows correct juice name
7. Tap schedule for full details (if expandable)

**Expected Results:**
1. Login succeeds
2. Detail screen shown
3. Delivery Schedule section visible
4. Mon-Sat: each with juice name, Sunday: Holiday (greyed)
5. Juice names match subscription metadata
6. Schedule matches stored JSON

**Test Data:**
- User: TA-04
- Expected: 6 days with juices, Sunday = Holiday
- API: GET /api/v1/subscriptions/:id/delivery-schedule

---

## Summary of Test Cases

| ID | Description | Priority | Requirement |
|----|-------------|----------|-------------|
| TC-E2E-SUB-001 | View list of all subscriptions (multiple active) | P1-High | TA-09 |
| TC-E2E-SUB-002 | View single subscription details | P1-High | TA-04 |
| TC-E2E-SUB-003 | Pause active subscription (before 9 PM) success | P1-High | TA-04, time < 9PM |
| TC-E2E-SUB-004 | Pause active subscription (after 9 PM) rejected | P1-High | TA-04, time >= 9PM |
| TC-E2E-SUB-005 | Resume paused subscription (before 9 PM) success | P1-High | TA-06, time < 9PM |
| TC-E2E-SUB-006 | Resume paused subscription (after 9 PM) rejected | P1-High | TA-06, time >= 9PM |
| TC-E2E-SUB-007 | Cancel subscription (end of term) | P1-High | TA-04 |
| TC-E2E-SUB-008 | Cancel subscription (immediately) | P1-High | TA-04 |
| TC-E2E-SUB-009 | Cancel subscription (specific date) | P1-High | TA-04 |
| TC-E2E-SUB-010 | Cancel already cancelled subscription error | P1-High | TA-07 |
| TC-E2E-SUB-011 | Remove scheduled cancellation | P1-High | TA-04 with scheduled cancel |
| TC-E2E-SUB-012 | Pause already paused subscription error | P2-Medium | TA-06 |
| TC-E2E-SUB-013 | Multiple pause/resume cycles (5+ cycles) | P2-Medium | TA-04, time < 9PM |
| TC-E2E-SUB-014 | POST returns 202 -> mobile refetches | P1-High | TA-04, network trace |
| TC-E2E-SUB-015 | Subscription status color coding (UI) | P2-Medium | TA-04, TA-06, TA-07 |
| TC-E2E-SUB-016 | View delivery schedule for subscription | P2-Medium | TA-04 with schedule |

## BR Coverage Traceability

| BR ID | Requirement | Test Cases |
|-------|-------------|------------|
| BR-040 | View all subscriptions (multiple simultaneous allowed) | SUB-001, SUB-002, SUB-015, SUB-016 |
| BR-041 | Pause before 9 PM IST for next-day skip | SUB-003, SUB-004, SUB-012, SUB-013 |
| BR-042 | Resume before 9 PM IST for next-day activation | SUB-005, SUB-006, SUB-013 |
| BR-043 | Cancel (immediately/end of term/specific date) | SUB-007, SUB-008, SUB-009, SUB-010, SUB-011 |
| BR-044 | Unlimited pause/resume cycles | SUB-003, SUB-005, SUB-013 |
| BR-045 | Mobile -> bmjServer -> Chargebee (no direct) | SUB-003, SUB-005, SUB-007, SUB-014 |
| BR-046 | Always refetch after action POST | SUB-003, SUB-005, SUB-007, SUB-014 |
| BR-047 | Multiple active subscriptions allowed | SUB-001 |

## Document Control

- **Created:** 2026-05-18
- **Version:** 1.0
- **Status:** For Review
- **Total Test Cases:** 16
