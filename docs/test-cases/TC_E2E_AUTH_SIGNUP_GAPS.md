# AUTH Module - Signup Gaps E2E Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-23
> **Module:** AUTHENTICATION — Signup Gap Coverage
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 15
> **Linked BR:** BR-001, BR-002, BR-003, BR-006, BR-007, BR-009
> **Linked UC:** UC-AUTH-001, UC-AUTH-002, UC-AUTH-003, UC-AUTH-004

## Purpose

This document covers **signup-specific E2E test scenarios NOT covered** by the existing TC-E2E-AUTH-001 to 060 test suite. These tests fill the gap analysis findings related to:

1. Google signup → persistence and edge cases
2. OTP brute force and security hardening
3. Account enumeration via forgot-password
4. JWT tampering detection
5. Boundary/unicode/edge case input handling
6. Concurrent signup race conditions
7. App restart/Kill scenarios in middle of signup flows

## Prerequisites

- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- Test accounts TA-01 through TA-10 are created (or creatable via signup)
- bmjServer deployed and accessible
- Google Sign-In configured with test account: e2e-google-test@gmail.com
- Phone SIM: 9876543210 (for OTP tests)

---

### TC-E2E-AUTH-SG-001: Google signup → app kill → auto-login persistence

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-003, BR-006 |
| **Linked UC** | UC-AUTH-003, UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account e2e-google-test@gmail.com on device
- [ ] This Google account NOT previously registered in BMJ
- [ ] OAuth consent screen configured with test user

**Test Steps:**
1. Open app → login/signup screen
2. Tap "Sign up with Google" under Sign Up tab
3. Select Google account (e2e-google-test@gmail.com) from picker
4. Verify email is pre-filled and read-only, name is pre-filled
5. Enter phone: 9876543210 → Send OTP → verify OTP
6. Enter full address (flat, city, state, ZIP, country)
7. Enter password: GglAuto1! → confirm → tap "Create Account"
8. Verify: Account created → auto-logged in → Dashboard shown
9. **Kill app completely** (swipe from recents)
10. Reopen app

**Expected Results:**
1. Google signup completes successfully (steps 1-8)
2. After app kill + reopen (step 10):
   - Splash screen shown briefly (1-2 seconds)
   - Auto-login validates stored JWT via GET /api/auth/autologin
   - Auto-login succeeds → Dashboard shown directly
   - **NO login screen shown** (user is automatically logged in)
3. JWT token is the same valid token stored during signup

**Test Data:**
- Google account: e2e-google-test@gmail.com
- phone: 9876543210
- password: GglAuto1!
- address: Flat B-202, Lake View, Sector 15, Gurgaon, Haryana, 122002, India

---

### TC-E2E-AUTH-SG-002: Google signup with missing Google profile fields

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-003 |
| **Linked UC** | UC-AUTH-003 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account with ONLY email + given_name configured (no family name, no photo)
- [ ] This Google account NOT previously registered

**Test Steps:**
1. Open app → Sign Up tab → tap "Sign up with Google"
2. Select a Google account that has minimal profile (only email + given_name, no family_name/photo)
3. Observe the signup form that appears after Google auth

**Expected Results:**
1. Google auth returns at minimum: email, given_name (firstName)
2. Email field pre-filled and read-only
3. First name field pre-filled from given_name
4. Last name field is **empty** (not showing "null" or crash) — user can manually enter
5. No crash or error when lastName or photoUrl are missing/null from Google response
6. User can manually enter lastName, phone, address, password and complete signup

**Test Data:**
- Google account with minimal profile data
- phone: 9876543210
- last name: (enter manually) "Smith"
- password: GglMin1!

---

### TC-E2E-AUTH-SG-003: Google signup → OTP verification is required (cannot bypass phone)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-003 |
| **Linked UC** | UC-AUTH-003 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account e2e-google-test@gmail.com on device

**Test Steps:**
1. Open app → Sign Up tab → tap "Sign up with Google"
2. Complete Google auth → reach the Google signup form
3. Observe that phone field is present and required
4. Try to tap any "Skip" button or navigate away without entering phone
5. Try to submit/save without entering phone

**Expected Results:**
1. Google auth does NOT bypass phone verification
2. Phone field is visible, mandatory, and shows 10-digit validation
3. No "Skip phone" button exists
4. User cannot proceed without entering valid phone + OTP verification
5. This enforces BR-002 (phone verification) even for Google signup

**Test Data:**
- Google account: e2e-google-test@gmail.com
- N/A (verification test)

---

### TC-E2E-AUTH-SG-004: Email-first signup → duplicate phone number at final submission

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001, BR-002 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone 9876543210 is already registered to an existing user
- [ ] Fresh email NOT in system: e2e-dup-phone-test@bookmyjuice.co.in

**Test Steps:**
1. Open app → Sign Up tab → tap "Sign up with Email"
2. Enter fresh email: e2e-dup-phone-test@bookmyjuice.co.in
3. Complete email verification (code sent to email → verify)
4. On phone entry, enter phone: **9876543210** (already registered to another user)
5. Send OTP → verify OTP (OTP will send because phone exists but is just SIM verification)
6. Enter address → enter password → tap "Create Account"

**Expected Results:**
1. Email verification succeeds (email is fresh)
2. OTP is sent and verified (phone OTP is independent of user registration)
3. At final submission (unified-signup API call), backend detects phone is already registered
4. Error message returned: "Error: Phone number is already registered!"
5. Account is NOT created
6. User stays on signup screen with error message displayed

**Test Data:**
- email: e2e-dup-phone-test@bookmyjuice.co.in
- phone: 9876543210 (already registered to another existing user)
- password: DupPhone1!

---

### TC-E2E-AUTH-SG-005: Phone-first signup → email already registered at email entry step

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002, BR-001 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543210 (or test phone)
- [ ] Email e2e-existing@bookmyjuice.co.in is already registered in system
- [ ] Fresh phone NOT in system (use phone unique for this test)

**Test Steps:**
1. Open app → Sign Up tab → tap "Sign up with Phone"
2. Enter fresh phone (not in system)
3. Send OTP → verify OTP successfully
4. On email entry screen, enter: **e2e-existing@bookmyjuice.co.in** (already registered)
5. Tap "Continue" to send email verification code

**Expected Results:**
1. Phone OTP sent and verified successfully
2. When email is entered and "Continue" tapped:
   - Backend's /api/auth/send-email-verification endpoint detects duplicate email
   - Error: "Error: Email is already registered!"
   - User is shown this error on screen
   - User can go back and enter a different email
   - OR "Login" option is offered (navigate to Sign In tab)

**Test Data:**
- phone: (use a fresh test phone — note the SIM number used)
- email: e2e-existing@bookmyjuice.co.in

---

### TC-E2E-AUTH-SG-006: OTP brute force — multiple wrong OTP attempts during signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002, NFR-011 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543210
- [ ] App in email-first signup, on phone entry step

**Test Steps:**
1. Enter phone: 9876543210 → tap "Send OTP"
2. Receive OTP via SMS
3. Enter wrong OTP: "000000" → tap "Verify" → see error
4. Repeat step 3 three more times (total 4 wrong attempts with same OTP)
5. On 5th wrong attempt, observe behavior
6. Now enter the **correct** OTP from SMS

**Expected Results:**
1. First 2-3 wrong OTP attempts: "Invalid or expired OTP" error shown
2. After max verification attempts (likely 3-5 per OTP):
   - "Maximum OTP verification attempts reached" or OTP is invalidated
   - OR OTP is automatically invalidated after threshold
3. Even if correct OTP is entered after threshold, it should fail
4. User must tap "Resend OTP" to get a new OTP and retry
5. Rate limiting for OTP send (10 per 5 min per IP) also applies

**Test Data:**
- phone: 9876543210
- wrong OTPs: 000000, 111111, 222222, 333333, 444444

---

### TC-E2E-AUTH-SG-007: Account enumeration via forgot-password (unregistered vs registered)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | NFR-011, BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User exists with phone 9876543212
- [ ] User exists with email e2e-existing@bookmyjuice.co.in
- [ ] A non-registered phone: 9999999999
- [ ] A non-registered email: unknown@example.com

**Test Steps:**
1. Open app → login screen → tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter **unregistered** phone: 9999999999
4. Tap "Send OTP"
5. Note the error message
6. Go back → enter **registered** phone: 9876543212
7. Tap "Send OTP"
8. Compare the two responses
9. Repeat for email method:
10. Select "Reset via Email Code"
11. Enter **unregistered** email: unknown@example.com → tap "Send Code"
12. Note the error message
13. Enter **registered** email: e2e-existing@bookmyjuice.co.in → tap "Send Code"
14. Compare the two email responses

**Expected Results:**
1. For **security best practice**: The error message for registered vs unregistered phone/email should be **identical/generic**
2. Acceptable behavior: "If this account exists, an OTP/code has been sent"
3. **VULNERABILITY if**: Unregistered returns "Phone number not registered" and registered returns "OTP sent" — this leaks user existence
4. Backend endpoint /reset-password-mobile checks: OTP verification happens first, then user lookup — so OTP is sent regardless (OTP doesn't leak existence)
5. Backend endpoint /reset-password-email checks: verification code is sent only if email exists? Check the flow

**Test Data:**
- registered phone: 9876543212
- unregistered phone: 9999999999
- registered email: e2e-existing@bookmyjuice.co.in
- unregistered email: unknown@example.com

---

### TC-E2E-AUTH-SG-008: JWT token tampering detection on /api/auth/autologin

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006, NFR-011 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with a valid JWT token (obtain from app logs or intercept)

**Test Steps:**
1. Log in successfully via email/password
2. Capture the JWT token (from app logs, Charles proxy, or Flutter debug)
3. Decode the JWT payload (Base64 decode the 2nd segment)
4. Modify a claim in the payload (e.g., change sub/user identifier)
5. Re-encode the JWT with the modified payload (keeping original signature)
6. Call GET /api/auth/autologin with the tampered JWT in Authorization header
7. Also test: Remove last character of the token
8. Also test: Change one character in the signature part

**Expected Results:**
1. Original valid JWT: GET /api/auth/autologin returns 200 "ok"
2. Tampered payload JWT: Returns 400 "Error: Invalid JWT token!" (signature validation fails)
3. Truncated JWT: Returns 400 "Error: Invalid JWT token!"
4. Modified signature JWT: Returns 400 "Error: Invalid JWT token!"
5. All tampered tokens are rejected — server verifies signature integrity
6. Auto-login on app also validates and would reject tampered JWT

**Test Data:**
- Use proxy/interceptor to capture JWT
- Modified JWT for testing

---

### TC-E2E-AUTH-SG-009: Signup with email containing plus addressing (+)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible for: e2e+test-signup@bookmyjuice.co.in (or plus-addressing compatible)
- [ ] Phone with SIM: 9876543210

**Test Steps:**
1. Open app → Sign Up with Email
2. Enter email: **e2e+test-signup@bookmyjuice.co.in** (plus addressing)
3. Tap "Continue" → email verification code sent
4. Check email inbox (for bmj, if using SendGrid/own SMTP, plus part may be included)
5. Enter the 6-digit code → verify
6. Complete phone, address, password signup

**Expected Results:**
1. The `+` character is accepted by email validation on frontend
2. Email verification code is sent to the full address including the `+` part
3. Verification succeeds
4. Signup completes successfully
5. User can log in using the full plus-addressed email

**Test Data:**
- email: e2e+test-signup@bookmyjuice.co.in
- phone: 9876543210
- password: PlusAdd1!

---

### TC-E2E-AUTH-SG-010: Signup flow killed mid-way → reopen starts fresh

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible
- [ ] Phone with SIM

**Test Steps:**
1. Open app → start email-first signup
2. Enter email → verify email code successfully
3. Enter phone → send OTP → verify OTP successfully
4. Enter address → tap "Continue"
5. **Before entering password, kill app completely** (swipe from recents)
6. Reopen app

**Expected Results:**
1. After app kill + reopen:
   - No JWT exists (signup was not completed)
   - Login screen is shown (NOT Dashboard)
2. Signup state is completely reset:
   - No partial signup data is preserved
   - User is NOT auto-logged in
3. User must start signup fresh from beginning
4. The previously used email is now registered (if verification code was consumed and OTP was consumed), so re-using same email shows "Email is already registered"

**Test Data:**
- email: e2e-abort-test@bookmyjuice.co.in
- phone: 9876543210
- N/A for password (signup not completed)

---

### TC-E2E-AUTH-SG-011: Signup with very long input values (boundary testing)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible
- [ ] Phone with SIM

**Test Steps:**
1. Open app → Sign Up with Email
2. Enter email: e2e-long-inputs@bookmyjuice.co.in → verify
3. On phone entry, enter valid 10-digit phone: 9876543210 → OTP → verify
4. On address screen:
   - First name: Enter 50-character name "AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDDEEEEEEEEEE"
   - Last name: Enter 50-character name "FFFFFFFFSSSSSSSSSSTTTTTTTTTTUUUUUUUUUUVVVVVVVVVV"
   - Address: Enter 255 characters of "A" repeated
   - Extended address: Enter 255 characters of "B" repeated
   - Extended addr2: Enter 255 characters of "C" repeated
   - City: Enter 100-character city name
   - State: Enter 100-character state name
   - ZIP: Enter 20-character ZIP (alphanumeric)
   - Country: Enter 100-character country name
5. Tap "Continue"
6. Enter password (strong) → confirm → "Create Account"

**Expected Results:**
1. Frontend should accept these reasonable input lengths (trim would be ideal)
2. OR frontend shows character limit validation with max lengths indicated
3. If frontend accepts and sends to backend:
   - Backend MySQL VARCHAR limits should not be exceeded (typically VARCHAR(255))
   - If data exceeds column limit, backend should return a clear validation error
   - NO database constraint violation error (the "Data truncation" type 500 errors)
4. Ideally: Both frontend and backend enforce reasonable limits gracefully

**Test Data:**
- email: e2e-long-inputs@bookmyjuice.co.in
- phone: 9876543210
- first/last name: 50 chars each
- address lines: 255 chars each
- password: LongPass123!

---

### TC-E2E-AUTH-SG-012: Signup with non-ASCII/Unicode characters in name and address

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-007 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible
- [ ] Phone with SIM

**Test Steps:**
1. Open app → Sign Up with Email
2. Enter email: e2e-unicode-test@bookmyjuice.co.in → verify
3. Phone → OTP → verify
4. On address screen:
   - First name: "José" (e with accent)
   - Last name: "Müller" (u with umlaut)
   - Address: "Calle de la Constitución 123, Piso 3°B" (Spanish with special chars)
   - City: "München" (German umlaut)
   - State: "São Paulo" (Portuguese tilde)
   - Country: "India"
5. Complete → enter password → "Create Account"

**Expected Results:**
1. Unicode characters are accepted in all text fields (no frontend validation rejecting them)
2. Account is created successfully
3. User can log in with the email
4. On profile page, Unicode characters display correctly (not garbled/mojibake)
5. Backend MySQL stores UTF-8 characters correctly

**Test Data:**
- email: e2e-unicode-test@bookmyjuice.co.in
- phone: 9876543210
- unicode name/address strings as above
- password: Unicode1!

---

### TC-E2E-AUTH-SG-013: Email-first signup → email verified → network loss at OTP step

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S1-Major |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible
- [ ] Phone with SIM
- [ ] Ability to toggle airplane mode

**Test Steps:**
1. Open app → Sign Up with Email
2. Enter email: e2e-net-loss@bookmyjuice.co.in → verify email code
3. On phone entry step: **Enable airplane mode / disconnect network**
4. Enter phone: 9876543210 → tap "Send OTP"
5. Observe behavior
6. **Disable airplane mode** (restore network)
7. Tap "Send OTP" again or tap retry button
8. Complete OTP → address → password → signup

**Expected Results:**
1. When network is lost and "Send OTP" is tapped:
   - Loading indicator appears briefly
   - Error: "Network error. Please check your connection." or similar
   - User stays on phone entry screen
   - App does NOT crash
2. After network is restored and retry:
   - OTP sent successfully
   - Complete flow works
3. This tests the InternetIssue state from auth_bloc

**Test Data:**
- email: e2e-net-loss@bookmyjuice.co.in
- phone: 9876543210
- password: NetLoss1!

---

### TC-E2E-AUTH-SG-014: Concurrent duplicate signup rapid double-tap (race condition)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible: e2e-race-test@bookmyjuice.co.in (fresh, not in system)
- [ ] Phone with SIM: 9876543210

**Test Steps:**
1. Open app → Sign Up with Email
2. Complete email verification, phone OTP, address entry steps
3. On the "Create Account" screen (password entry):
   - Enter password: RaceCond1!
   - Enter confirm password
4. **Rapidly double-tap** the "Create Account" button (within <500ms)

**Expected Results:**
1. Frontend BLoC `_isSendingOTP` guard (BUG FIX 11) prevents duplicate OTP sending, but there is no similar guard for signup submission
2. If no frontend guard exists:
   - First tap → dispatches CompleteSignup event → calls userRepository.signUp()
   - Second tap → dispatches another CompleteSignup event → another signUp() call
3. Backend unified-signup has DB-level validation (`existsByEmail` + `existsByUsername`) which are checked sequentially
4. First request: Creates user + Chargebee customer → success
5. Second request: Detects duplicate email → returns "Error: Email is already registered!"
6. **Critical check**: Ensure no duplicate user is created in database (no race condition bypass of the duplicate checks)

**Test Data:**
- email: e2e-race-test@bookmyjuice.co.in
- phone: 9876543210
- password: RaceCond1!

---

### TC-E2E-AUTH-SG-015: Auto-login after password change (token version invalidation)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006, BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User exists with phone 9876543212 and email e2e-existing@bookmyjuice.co.in
- [ ] User is logged in on the device (JWT stored in SecureStorage)

**Test Steps:**
1. Log in with existing user: email: e2e-existing@bookmyjuice.co.in, password: TestPass123!
2. Verify: Dashboard shown, JWT stored
3. **Kill app** completely
4. Reopen app → verify auto-login succeeds → Dashboard shown (token still valid)
5. Now go to Forgot Password → reset password via mobile OTP to: ResetTok1!
6. **Kill app** completely
7. Reopen app

**Expected Results:**
1. Step 4: Auto-login succeeds with original JWT (token version = X)
2. Step 5: Password reset succeeds → server calls `user.invalidateAllTokens()` → token version increments to X+1
3. Step 7: Auto-login fails because:
   - The old JWT (with token version X) is now invalid
   - Server auto-login endpoint validates token version against DB
   - Returns 401 / error → app clears token → shows login screen
4. User must log in again with new password: ResetTok1!
5. Login with new password succeeds → new JWT with token version X+1

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- old password: TestPass123!
- new password: ResetTok1!

---

### TC-E2E-AUTH-SG-016: Password reset → old password cannot be reused immediately

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-04 exists (email: e2e-existing@bookmyjuice.co.in, phone: 9876543212, password: TestPass123!)
- [ ] User is logged out
- [ ] Phone with SIM: 9876543212

**Test Steps:**
1. Open app → Sign In tab → tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter phone: 9876543212 → Send OTP → verify OTP
4. Enter new password: ResetTok1! → confirm → Reset Password
5. Verify success message
6. Go to Sign In → try logging in with OLD password: TestPass123!
7. Observe error: "Invalid username or password!"
8. Log in with NEW password: ResetTok1! → success → Dashboard
9. Go to Profile → try to change password BACK to TestPass123!
10. If password history is enforced, verify old password is rejected with message: "Password was used recently. Please choose a different password."

**Expected Results:**
1. Password reset succeeds (step 4-5)
2. Old password rejected immediately after reset (step 6-7)
3. New password works for login (step 8)
4. If password history is enforced (step 9-10):
   - Changing back to the most recent password is rejected
   - User must choose a password not used in the last N iterations
5. If no password history: Changing to old password succeeds

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- phone: 9876543212
- old password: TestPass123!
- new password: ResetTok1!

---

### TC-E2E-AUTH-SG-017: Email change → old email unlinked from account

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-001, BR-007 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User TA-04 exists (email: e2e-existing@bookmyjuice.co.in, password: TestPass123!)
- [ ] User is logged in
- [ ] Fresh email inbox accessible: e2e-changed@bookmyjuice.co.in

**Test Steps:**
1. Log in with TA-04 (e2e-existing@bookmyjuice.co.in)
2. Navigate to Profile → Account Settings
3. Locate "Change Email" option (if available)
4. Enter new email: e2e-changed@bookmyjuice.co.in
5. Verify new email via verification code sent to new address
6. Confirm email change
7. Observe confirmation message
8. Log out → try to log in with OLD email (e2e-existing@bookmyjuice.co.in)
9. Observe error message
10. Log in with NEW email (e2e-changed@bookmyjuice.co.in) and password TestPass123!

**Expected Results:**
1. Email change flow exists in Profile (step 3)
2. New email verification requires code sent to new address (step 5)
3. After change, old email is unlinked from account (step 8-9):
   - Login with old email fails: "Invalid username or password!" or "Account not found"
4. Login with new email succeeds (step 10)
5. All account data (orders, subscriptions, cart) preserved under new email

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in (old)
- email: e2e-changed@bookmyjuice.co.in (new)
- password: TestPass123!

---

### TC-E2E-AUTH-SG-018: Email verification code expiry after signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible: e2e-code-expiry@bookmyjuice.co.in
- [ ] Phone with SIM: 9876543210

**Test Steps:**
1. Open app → Sign Up with Email
2. Enter email: e2e-code-expiry@bookmyjuice.co.in → tap "Continue"
3. Email verification code is sent — **DO NOT enter it**
4. Wait 10+ minutes (or until code expires — typically 5-10 min TTL)
5. Now enter the original verification code
6. Observe error message
7. Tap "Resend Code" or request a new verification code
8. Enter the new code → verify
9. Complete signup (phone OTP → address → password)

**Expected Results:**
1. Expired code shows error: "Invalid or expired verification code!" (step 5-6)
2. "Resend Code" button/option is available (step 7)
3. New verification code is sent and works (step 8)
4. Signup completes successfully with new code (step 9)
5. Code expiry is independent of OTP expiry (different TTLs)

**Test Data:**
- email: e2e-code-expiry@bookmyjuice.co.in
- phone: 9876543210
- password: CodeExp1!

---

## Document Control

- **Created:** 2026-05-23
- **Updated:** 2026-05-23
- **Version:** 1.1
- **Total Test Cases:** 18
- **Status:** ✅ Complete
