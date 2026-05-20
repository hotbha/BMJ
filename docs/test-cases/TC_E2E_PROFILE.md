# PROFILE Module — End-to-End (E2E) Black Box Test Cases

> **Document Version:** 1.0  
> **Last Updated:** 2026-05-18  
> **Module:** PROFILE  
> **Type:** E2E (Black Box)  
> **Automation Status:** ❌ Manual  

---

## Prerequisites

Refer to **`TEST_PREREQUISITES.md`** for full environment setup. Key items for this module:

| # | Pre-Requisite | Status |
|---|---------------|--------|
| P-01 | bmjServer deployed to staging with public URL | 🔴 Must Do |
| F-01 | Flutter APK built with API_BASE_URL=staging | 🔴 Must Do |
| F-03 | APK installed on physical device or emulator | 🔴 Must Do |
| TA-04 | Existing registered user for authentication | 🔴 Must Do |
| TA-08 | User with address history for address update tests | 🔴 Must Insert |

**Linked BRs:** BR-006, BR-007  
**Linked UCs:** UC-01, UC-05, UC-08  
**Key Rules:** JWT token managed in SharedPreferences (BR-006). Username=phone rule enforced (BR-006). ChargebeeSyncService for background sync with startup sync disabled by default. Profile data includes name, email, phone, and delivery address.

---

## Test Cases

---
### TC-E2E-PRO-001: View profile details (name, email, phone, address)

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-001 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-01, UC-05 |

**Preconditions:**
- [ ] User is registered with full profile: name, email, phone, delivery address saved
- [ ] User is logged in via OTP flow
- [ ] JWT token stored in SharedPreferences
- [ ] App is on the home/dashboard screen

**Test Steps:**
1. Log in as TA-04 using OTP verification
2. From the home screen, tap on the profile icon or navigate to Profile screen
3. Observe the displayed profile information
4. Verify name field shows correct value
5. Verify email field shows correct value
6. Verify phone field shows correct value
7. Verify delivery address section shows saved address (if any)
8. Navigate back and return to Profile - verify data persists

**Expected Results:**
1. User logs in successfully - navigates to home
2. Profile screen opens with all fields populated from backend
3-6. Name, email, and phone match the DB record for TA-04
7. Address section displays saved address or shows a placeholder if none set
8. Profile data persists across navigation - no flickering or blank fields

**Test Data:**
- User: TA-04 (e2e-existing@bookmyjuice.co.in / 9876543212)
- Expected name: John Doe (or as configured in seed data)
- Expected email: e2e-existing@bookmyjuice.co.in
- Expected phone: 9876543212
- API: GET /api/v1/users/me

---
### TC-E2E-PRO-002: Update profile name → persisted

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-002 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-05 |

**Preconditions:**
- [ ] User is logged in as TA-04
- [ ] JWT token stored in SharedPreferences
- [ ] Profile screen is accessible

**Test Steps:**
1. Log in as TA-04
2. Navigate to Profile screen
3. Tap on the name field or Edit button
4. Change the name to a new value (e.g., Jane Doe)
5. Tap Save / Submit
6. Observe success feedback (toast, snackbar, or confirmation)
7. Navigate away from Profile screen (e.g., to Home)
8. Return to Profile screen
9. Verify name field now shows the updated name
10. Log out and log back in as TA-04
11. Navigate to Profile screen
12. Verify name persists - still shows Jane Doe

**Expected Results:**
1-2. User logged in, Profile screen displayed
3. Name field is editable (text field)
4. New name entered successfully
5. App sends PATCH/PUT to /api/v1/users/me - receives 200 OK
6. Success feedback displayed (green snackbar: Profile updated)
7-9. Name persists after navigation (cached in app state)
10-12. Name persists after logout and re-login (stored in DB)

**Test Data:**
- User: TA-04 (9876543212)
- Original name: John Doe (or seed default)
- New name: Jane Doe
- API: PATCH /api/v1/users/me with body {"name": "Jane Doe"}

---
### TC-E2E-PRO-003: Update delivery address → persisted

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-003 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-08 |

**Preconditions:**
- [ ] User is logged in as TA-04
- [ ] User has address management enabled in app
- [ ] JWT token stored in SharedPreferences
- [ ] Profile screen with address section is accessible

**Test Steps:**
1. Log in as TA-04
2. Navigate to Profile screen
3. Locate the delivery address section
4. Tap Edit Address or Add Address button
5. Fill in new address details:
   - Line 1: 123 MG Road
   - City: Mumbai
   - State: Maharashtra
   - Pincode: 400001
6. Tap Save address
7. Observe success feedback
8. Navigate away and return to Profile
9. Verify address displays correctly
10. Log out and log back in
11. Navigate to Profile - verify address still present

**Expected Results:**
1-2. User logged in, Profile screen displayed
3. Address section visible with current address or Add button
4. Address form opens (inline or modal)
5. All address fields can be entered
6. App sends PATCH/PUT to /api/v1/users/me/address - 200 OK
7. Success feedback: green snackbar - Address updated
8-9. Address persists after navigation
10-11. Address persists after logout and re-login (persisted in DB)

**Test Data:**
- User: TA-04 (9876543212)
- New address: 123 MG Road, Mumbai, Maharashtra - 400001
- API: PATCH /api/v1/users/me/address
- Verification: GET /api/v1/users/me returns updated address

---
### TC-E2E-PRO-004: Logout → JWT cleared → redirected to login

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-004 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P0 — Critical |
| **Severity** | S0 — Blocker |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-01 |

**Preconditions:**
- [ ] User is logged in as TA-04 with JWT stored in SharedPreferences
- [ ] App is on any authenticated screen (e.g., Home, Profile)

**Test Steps:**
1. Log in as TA-04 via OTP verification
2. Navigate to Profile screen
3. Tap the Logout button in settings/profile menu
4. Confirm logout action in the confirmation dialog
5. Observe the screen navigation
6. Check that the app redirects to Login/Phone input screen
7. Attempt to access a protected screen (e.g., manually type profile URL or navigate via drawer)
8. Use a tool or script to check SharedPreferences for JWT token

**Expected Results:**
1-2. User logged in, Profile screen displayed
3. Logout button visible and tappable
4. Confirmation dialog: Are you sure you want to log out? - Tap Yes
5. App sends POST /api/v1/auth/logout (optional) and clears local session
6. User redirected to Login screen (phone input for OTP)
7. Protected routes redirect to Login - user cannot access authenticated screens
8. SharedPreferences JWT token removed or set to empty string

**Test Data:**
- User: TA-04 (9876543212)
- SharedPreferences key: jwt_token or auth_token
- Protected endpoint: GET /api/v1/users/me should return 401 after logout

---
### TC-E2E-PRO-005: Logout → guest cart still accessible

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-005 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P2 — Medium |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-01, UC-03 |

**Preconditions:**
- [ ] User is logged in as TA-04
- [ ] Guest cart feature is enabled
- [ ] User has at least one item in their cart
- [ ] Cart is associated with the user session

**Test Steps:**
1. Log in as TA-04
2. Add a juice product to cart
3. Navigate to Profile screen
4. Tap Logout and confirm
5. Verify app redirects to Login screen
6. Navigate to Cart screen (via bottom navigation or menu - if accessible)
7. Verify that the previously added item is still visible in cart
8. Clear app data or note the item count
9. Log in again as TA-04
10. Navigate to Cart
11. Verify cart items persist (if backend persists cart for user)

**Expected Results:**
1-2. User logged in and adds item to cart
3-4. Logout completes - JWT cleared, redirected to Login
5. User on Login screen (unauthenticated state)
6. Cart screen loads (guest cart mode)
7. Cart items remain visible (guest cart uses local storage)
8-9. User logs back in - cart syncs
10-11. Cart items present after re-login (either from local or backend sync)

**Test Data:**
- User: TA-04 (9876543212)
- Product: any juice product from catalog
- Cart storage: local (SharedPreferences) or backend (DB)
- Expected: cart does not get wiped on logout

---
### TC-E2E-PRO-006: Delete account → user data removed

| Field | Value |
|-------|-------|
| **ID** | TC-E2E-PRO-006 |
| **Module** | PROFILE |
| **Type** | E2E (Black Box) |
| **Priority** | P1 — High |
| **Severity** | S1 — Major |
| **Automation Status** | ❌ Manual |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-01, UC-05 |

**Preconditions:**
- [ ] User is logged in as TA-04 with full profile (name, email, address)
- [ ] User has at least one completed order in history
- [ ] Delete account option is visible in Profile settings
- [ ] Backend supports DELETE /api/v1/users/me endpoint

**Test Steps:**
1. Log in as TA-04
2. Navigate to Profile screen
3. Tap Settings or Account menu
4. Locate and tap Delete Account option
5. Read the warning dialog explaining consequences (data loss)
6. Confirm deletion by typing DELETE or tapping Confirm
7. Observe the app behavior
8. Verify app redirects to Login/Registration screen
9. Attempt to log in again using TA-04 credentials (phone number)
10. Check backend DB to verify user data anonymization/removal
11. Re-register with same phone number
12. Verify new account creation works

**Expected Results:**
1-2. User logged in, Profile screen displayed
3. Account menu accessible
4. Delete Account option visible in settings (often with red color)
5. Warning dialog explains: This action cannot be undone. All personal data will be removed.
6. App sends DELETE /api/v1/users/me with JWT auth - receives 200 OK
7. Local session cleared - JWT removed from SharedPreferences
8. App navigates to Login screen (unauthenticated)
9. OTP flow returns new user flow or indicates account not found
10. DB shows user record soft-deleted or anonymized (fields like email/name cleared)
11-12. Same phone number can be used to create a fresh account

**Test Data:**
- User: TA-04 (9876543212 / e2e-existing@bookmyjuice.co.in)
- API: DELETE /api/v1/users/me
- DB check: users table - deleted_at set or personal data fields nullified
- Expected: Account deletion removes PII but may retain order records for analytics

---
