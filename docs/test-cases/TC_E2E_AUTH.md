# AUTH Module - End-to-End (E2E) Black-Box Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-19
> **Module:** AUTHENTICATION
> **Test Type:** E2E (End-to-End Black-Box)
> **Total Test Cases:** 60
> **Linked BR:** BR-001 to BR-011
> **Linked UC:** UC-AUTH-001 to UC-AUTH-007c

---

## Test Environment Prerequisites

Before executing these tests, ensure:
- All prerequisites from TEST_PREREQUISITES.md Sections 1-5 are met
- Test accounts TA-01 through TA-10 are created (or creatable via signup)
- bmjServer deployed and accessible
- Firebase Phone Auth and Google Sign-In configured
- SMTP/email verification service running
- Test phone SIMs available or Firebase test OTPs configured

---

## Table of Contents

1. [Email-First Signup (TC-E2E-AUTH-001 to 015)](#1-email-first-signup)
2. [Phone-First Signup (TC-E2E-AUTH-016 to 020)](#2-phone-first-signup)
3. [Google Signup (TC-E2E-AUTH-021 to 024)](#3-google-signup)
4. [User Login (TC-E2E-AUTH-025 to 030)](#4-user-login)
5. [Auto-Login (TC-E2E-AUTH-031 to 034)](#5-auto-login)
6. [Google Sign-In (TC-E2E-AUTH-035 to 038)](#6-google-sign-in)
7. [Phone Sign-In (TC-E2E-AUTH-039 to 042)](#7-phone-sign-in)
8. [Firebase Phone Auth Signup (TC-E2E-AUTH-043 to 046)](#8-firebase-phone-auth-signup)
9. [Firebase Phone Auth Login (TC-E2E-AUTH-047 to 048)](#9-firebase-phone-auth-login)
10. [Password Reset (TC-E2E-AUTH-049 to 054)](#10-password-reset)
11. [Rate Limiting & Security (TC-E2E-AUTH-055 to 057)](#11-rate-limiting--security)
12. [Edge Cases (TC-E2E-AUTH-058 to 060)](#12-edge-cases)

---

### TC-E2E-AUTH-001: Complete email-first signup with valid data

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
- [ ] Email inbox accessible: e2e-test-email@bookmyjuice.co.in
- [ ] Phone with SIM: 9876543210
- [ ] App on login/signup screen

**Test Steps:**
1. Open app → see login/signup screen
2. Tap "Sign up with Email"
3. Enter valid email: e2e-test-email@bookmyjuice.co.in
4. Tap "Continue"
5. Open email inbox → note 6-digit verification code
6. Enter the 6-digit code
7. Tap "Verify Email"
8. Enter phone: 9876543210
9. Tap "Send OTP"
10. Receive SMS with 6-digit OTP
11. Enter the 6-digit OTP
12. Tap "Verify OTP"
13. Enter full address (flat, society, city, state, ZIP, country)
14. Tap "Continue"
15. Enter password: TestPass123! (meets requirements)
16. Confirm password
17. Tap "Create Account"

**Expected Results:**
1. Verification code sent to email within 30 seconds
2. OTP sent to phone via SMS within 30 seconds
3. All data validated without errors at each step
4. Account created successfully
5. User automatically logged in (JWT generated)
6. Redirected to Dashboard
7. Welcome message displayed

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in
- phone: 9876543210
- password: TestPass123! (8+ chars, 1 uppercase, 1 lowercase, 2 numbers, 1 special)
- address: Flat A-101, Green Valley, Sector 12, Gurgaon, Haryana, 122001, India

---

### TC-E2E-AUTH-002: Invalid email format rejected during signup

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
- [ ] App on email entry screen

**Test Steps:**
1. Open app → login/signup screen
2. Tap "Sign up with Email"
3. Enter invalid email: "not-an-email"
4. Tap "Continue"

**Expected Results:**
1. "Please enter a valid email" error shown immediately
2. "Continue" button remains disabled or returns error
3. User cannot proceed to next step

**Test Data:**
- email: not-an-email (invalid format)

---

### TC-E2E-AUTH-003: Duplicate email shows error during signup

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
- [ ] Account with e2e-existing@bookmyjuice.co.in already exists
- [ ] App on email entry screen

**Test Steps:**
1. Open app → login/signup screen
2. Tap "Sign up with Email"
3. Enter email of already-registered user: e2e-existing@bookmyjuice.co.in
4. Tap "Continue"

**Expected Results:**
1. System detects duplicate email
2. Error message: "Email is already registered"
3. "Login" button offered as option
4. User can navigate to login screen

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in (already registered)

---

### TC-E2E-AUTH-004: Wrong email verification code entered

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

**Test Steps:**
1. Enter valid email
2. Tap "Continue" → code sent to email
3. Enter wrong 6-digit code: "111111"
4. Tap "Verify Email"

**Expected Results:**
1. Error displayed: "Invalid or expired verification code"
2. User can re-enter correct code
3. Correct code accepted on retry

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in
- wrong code: 111111

---

### TC-E2E-AUTH-005: Expired verification code → resend new code

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001, UC-AUTH-007c |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email inbox accessible

**Test Steps:**
1. Enter valid email → tap "Continue"
2. Wait 10+ minutes (code expires)
3. Enter the original 6-digit code
4. Tap "Verify Email"
5. See "Code expired" error
6. Tap "Resend Code" (wait 30s cooldown)
7. Receive new code in email
8. Enter new 6-digit code
9. Tap "Verify Email"

**Expected Results:**
1. Expired code shows: "Code expired. Please request a new code."
2. Resend button disabled for 30 seconds (countdown shown)
3. After 30s, resend enabled
4. New code sent → old code invalidated
5. New code accepted

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in

---

### TC-E2E-AUTH-006: Max resend attempts reached for email verification

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
- [ ] Email inbox accessible

**Test Steps:**
1. Enter valid email → tap "Continue"
2. Tap "Resend Code" → wait 30s → repeat 4 more times (total 5 resends)
3. Tap "Resend Code" a 6th time

**Expected Results:**
1. Resend button disabled after 5 attempts
2. Message: "Maximum resend attempts reached. Please try again later."
3. User cannot send more codes

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in
- Max resends: 5

---

### TC-E2E-AUTH-007: Code resend before 30s cooldown

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
- [ ] Email inbox accessible

**Test Steps:**
1. Enter valid email → tap "Continue" → code sent
2. Immediately tap "Resend Code" (within 30s)

**Expected Results:**
1. Resend button is disabled/greyed out
2. Countdown timer visible showing remaining seconds
3. Button becomes enabled after 30 seconds

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in

---

### TC-E2E-AUTH-008: Invalid phone format rejected during signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email verified in current signup flow

**Test Steps:**
1. Complete email verification step
2. On phone entry screen, enter: "12345" (5 digits)
3. Tap "Send OTP"

**Expected Results:**
1. Error: "Please enter a valid 10-digit Indian number"
2. User cannot proceed with invalid phone
3. Valid 10-digit number accepted

**Test Data:**
- phone: 12345 (invalid - too short)

---

### TC-E2E-AUTH-009: Wrong OTP entered during signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM for OTP reception

**Test Steps:**
1. Enter valid phone → tap "Send OTP"
2. Receive real OTP via SMS
3. Enter wrong 6-digit OTP: "999999"
4. Tap "Verify OTP"

**Expected Results:**
1. Error: "Invalid or expired OTP"
2. User can retry with correct OTP
3. Correct OTP accepted on retry

**Test Data:**
- phone: 9876543210
- wrong OTP: 999999

---

### TC-E2E-AUTH-010: Expired OTP → resend new OTP

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM

**Test Steps:**
1. Enter valid phone → tap "Send OTP"
2. Wait 10+ minutes (OTP expires)
3. Enter original OTP → see expiry error
4. Tap "Resend OTP" (wait 30s)
5. Receive new OTP via SMS
6. Enter new OTP
7. Tap "Verify OTP"

**Expected Results:**
1. "OTP expired" error shown
2. Resend disabled for 30s countdown
3. New OTP sent → old invalidated
4. New OTP accepted

**Test Data:**
- phone: 9876543210

---

### TC-E2E-AUTH-011: Missing required address field during signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-070 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Email + phone verified

**Test Steps:**
1. Complete email verification + phone OTP steps
2. On address entry screen, leave "City" field empty
3. Fill all other fields
4. Tap "Continue"

**Expected Results:**
1. "City" field highlighted/underlined in red
2. Error: "City is required" or equivalent
3. User cannot proceed
4. After filling city, tap Continue → proceeds

**Test Data:**
- address: Flat A-101, Green Valley, (City empty), Haryana, 122001, India

---

### TC-E2E-AUTH-012: Weak password rejected during signup

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
- [ ] Email + phone + address completed

**Test Steps:**
1. Complete email, phone, address steps
2. On password screen, enter: "weak"
3. Tap "Create Account"

**Expected Results:**
1. Password validator shows requirements in red
2. Submit button disabled
3. Requirements shown: 8+ chars, uppercase, lowercase, 2+ numbers, 1+ special
4. "weak" fails all checks

**Test Data:**
- password: weak (fails: length < 8, no uppercase, no numbers, no special)

---

### TC-E2E-AUTH-013: Password mismatch during signup

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
- [ ] Email + phone + address completed

**Test Steps:**
1. On password screen, enter password: "TestPass123!"
2. In confirm field, enter: "DifferentPass456!"
3. Tap "Create Account"

**Expected Results:**
1. Error: "Passwords do not match"
2. User can correct and retry

**Test Data:**
- password: TestPass123!
- confirm: DifferentPass456!

---

### TC-E2E-AUTH-014: User navigates back mid-signup flow

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
- [ ] App on phone entry screen during signup

**Test Steps:**
1. Start email-first signup
2. After email verification, tap phone back button
3. Confirm "Discard changes?" dialog
4. Tap "Yes"
5. Check current screen

**Expected Results:**
1. Back button shows confirmation dialog: "Are you sure? Your progress will be lost."
2. "Yes" → returns to signup method selection screen
3. "No" → stays on current step

**Test Data:**
- N/A (navigation test)

---

### TC-E2E-AUTH-015: Network failure during email verification step

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
- [ ] Ability to toggle airplane mode

**Test Steps:**
1. Enter valid email → tap "Continue"
2. Enable airplane mode / disconnect network
3. Try to proceed

**Expected Results:**
1. Loading indicator shown briefly
2. Error: "Network error. Please check your connection."
3. Retry button available
4. After reconnecting network, retry succeeds

**Test Data:**
- email: e2e-test-email@bookmyjuice.co.in

---

### TC-E2E-AUTH-016: Complete phone-first signup with valid data

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543211
- [ ] Email inbox: e2e-test-phone@bookmyjuice.co.in

**Test Steps:**
1. Open app → login/signup screen
2. Tap "Sign up with Phone"
3. Enter phone: 9876543211
4. Tap "Send OTP" → receive SMS
5. Enter OTP → tap "Verify OTP"
6. Enter email: e2e-test-phone@bookmyjuice.co.in
7. Tap "Continue" → code sent to email
8. Enter email verification code
9. Enter full address
10. Enter password + confirm
11. Tap "Create Account"

**Expected Results:**
1. OTP sent to phone ✓
2. Email verification code sent ✓
3. Account created automatically
4. JWT generated, logged in
5. Redirected to Dashboard

**Test Data:**
- phone: 9876543211
- email: e2e-test-phone@bookmyjuice.co.in
- password: TestPass123!

---

### TC-E2E-AUTH-017: Phone-first with non-10-digit phone rejected

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App on phone entry screen

**Test Steps:**
1. Tap "Sign up with Phone"
2. Enter phone: "98765" (5 digits)
3. Tap "Send OTP"

**Expected Results:**
1. "Please enter a valid 10-digit Indian number" error
2. Cannot proceed

**Test Data:**
- phone: 98765

---

### TC-E2E-AUTH-018: Wrong OTP → retry → success (phone-first)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM

**Test Steps:**
1. Enter phone → send OTP
2. Enter wrong OTP → see error
3. Enter correct OTP from SMS
4. Tap "Verify OTP"

**Expected Results:**
1. Wrong OTP → error message
2. Correct OTP → proceeds to next step

**Test Data:**
- phone: 9876543211

---

### TC-E2E-AUTH-019: Email already registered during phone-first signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-001 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Account with that email exists

**Test Steps:**
1. Complete phone verification step
2. On email entry, enter: e2e-existing@bookmyjuice.co.in
3. Tap "Continue"

**Expected Results:**
1. "Email is already registered" error
2. "Login" button offered

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in

---

### TC-E2E-AUTH-020: Cancel mid-phone-first flow

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-002 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone verified

**Test Steps:**
1. Start phone-first signup → verify phone
2. On email step, press back
3. Confirm discard dialog
4. Check current screen

**Expected Results:**
1. Confirmation dialog shown
2. After confirm → returns to signup method selection

**Test Data:**
- N/A

---

### TC-E2E-AUTH-021: Complete Google signup as new user

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
- [ ] OAuth consent screen configured with test user
- [ ] google-services.json has non-empty oauth_client

**Test Steps:**
1. Open app → login/signup screen
2. Tap "Sign up with Google"
3. Select Google account from picker (e2e-google-test@gmail.com)
4. Verify pre-filled email (read-only) + name (editable)
5. Enter phone: 9876543210
6. Tap "Send OTP" → verify OTP
7. Enter address
8. Enter password + confirm
9. Tap "Create Account"

**Expected Results:**
1. Google auth returns verified email + name
2. Email pre-filled and read-only ✓
3. Name pre-filled and editable ✓
4. Phone verification still required ✓
5. Account created with Google email
6. Auto-logged in → Dashboard

**Test Data:**
- Google account: e2e-google-test@gmail.com
- phone: 9876543210
- password: TestPass123!

---

### TC-E2E-AUTH-022: Google auth cancelled by user

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
- [ ] Google account on device

**Test Steps:**
1. Tap "Sign up with Google"
2. When Google account picker appears, dismiss/cancel
3. Check current screen

**Expected Results:**
1. Returns to login/signup method selection screen
2. No error shown
3. User can try other signup methods

**Test Data:**
- N/A

---

### TC-E2E-AUTH-023: Google email already registered → login redirect

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-003, BR-010 |
| **Linked UC** | UC-AUTH-003, UC-AUTH-005 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Registered user with that Google email exists
- [ ] Google account on device

**Test Steps:**
1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account whose email is already registered
4. Observe system behavior

**Expected Results:**
1. Google auth succeeds
2. System finds user with matching email
3. User is logged in automatically (JWT generated)
4. Redirected to Dashboard

**Test Data:**
- Google account email already in system

---

### TC-E2E-AUTH-024: Phone already registered during Google signup

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
- [ ] Google account on device
- [ ] Phone 9876543212 already registered

**Test Steps:**
1. Complete Google auth → get to phone entry
2. Enter phone of existing user: 9876543212
3. Tap "Send OTP" → verify OTP
4. Check system response

**Expected Results:**
1. After phone verification, system detects phone in use
2. Error: "Phone number is already registered"
3. "Login" button offered
4. User redirected to login

**Test Data:**
- phone: 9876543212 (already registered)

---

### TC-E2E-AUTH-025: Login with valid email and password

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User e2e-existing@bookmyjuice.co.in exists
- [ ] Correct password known

**Test Steps:**
1. Open app → login screen
2. Enter email: e2e-existing@bookmyjuice.co.in
3. Enter password: TestPass123!
4. Tap "Login"

**Expected Results:**
1. Loading indicator shown
2. Login successful
3. JWT token stored in SharedPreferences
4. Redirected to Dashboard
5. User name/email visible on profile

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- password: TestPass123!

---

### TC-E2E-AUTH-026: Login with wrong password

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User exists with known password

**Test Steps:**
1. Open app → login screen
2. Enter email: e2e-existing@bookmyjuice.co.in
3. Enter password: WrongPass123!
4. Tap "Login"

**Expected Results:**
1. Error: "Invalid email or password"
2. User stays on login screen
3. Can retry with correct password

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- password: WrongPass123!

---

### TC-E2E-AUTH-027: Login with unregistered email

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App on login screen

**Test Steps:**
1. Open app → login screen
2. Enter email: unknown@example.com
3. Enter password: SomePass123!
4. Tap "Login"

**Expected Results:**
1. Error: "Invalid email or password" (generic, doesn't reveal existence)
2. User stays on login screen

**Test Data:**
- email: unknown@example.com (not registered)
- password: SomePass123!

---

### TC-E2E-AUTH-028: Login with phone as username and password

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006, PD-AUTH-001 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User with phone 9876543212 exists

**Test Steps:**
1. Open app → login screen
2. Enter phone: 9876543212 (as username)
3. Enter password: TestPass123!
4. Tap "Login"

**Expected Results:**
1. Login successful (username=phone field works)
2. JWT generated
3. Redirected to Dashboard

**Test Data:**
- username/phone: 9876543212
- password: TestPass123!

---

### TC-E2E-AUTH-029: Empty fields validation on login

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App on login screen

**Test Steps:**
1. Open app → login screen
2. Leave email field empty
3. Leave password field empty
4. Tap "Login"

**Expected Results:**
1. "Please enter email" validation shown
2. "Please enter password" validation shown
3. Form not submitted

**Test Data:**
- email: (empty)
- password: (empty)

---

### TC-E2E-AUTH-030: Account locked after 5 failed login attempts

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
- [ ] User exists with known password

**Test Steps:**
1. Open app → login screen
2. Enter valid email
3. Enter wrong password → submit (1st attempt)
4. Repeat step 3 four more times (total 5 failures)
5. Enter correct password this time

**Expected Results:**
1. First 4 failures: "Invalid email or password"
2. After 5th failure (or threshold): "Account locked. Reset password?" or rate limit message
3. Even correct password rejected
4. "Reset Password" option offered

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in

---

### TC-E2E-AUTH-031: Auto-login with valid JWT token

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in with valid JWT stored

**Test Steps:**
1. Log in successfully (JWT stored)
2. Kill app completely (swipe from recents)
3. Reopen app

**Expected Results:**
1. Splash screen shown briefly
2. App checks JWT in SharedPreferences
3. Validates token with server (GET /api/auth/me)
4. Auto-login succeeds → Dashboard shown directly
5. NO login screen shown

**Test Data:**
- N/A (auto-login flow)

---

### TC-E2E-AUTH-032: Auto-login with expired JWT → Dashboard public mode with toast

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Expired JWT in storage

**Test Steps:**
1. Log in successfully
2. Manually expire/modify JWT to be expired (or wait 30 days)
3. Kill app
4. Reopen app

**Expected Results:**
1. App immediately shows Dashboard (public mode) with catalog preview and "Sign In" prompt
2. Background auto-login checks JWT → finds expired token
3. Clears expired token from SharedPreferences
4. Dashboard stays in public mode, shows toast notification: "Session expired. Please sign in again."
5. User can browse products and catalog without signing in

**Test Data:**
- Expired JWT token

---

### TC-E2E-AUTH-033: Auto-login with missing token → Dashboard public mode

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Fresh install or cleared app data

**Test Steps:**
1. Clear app data / fresh install
2. Open app

**Expected Results:**
1. No JWT in SharedPreferences
2. Dashboard (public mode) displayed with catalog preview, promotions, subscription plans, and a "Sign In" prompt
3. User can browse products and plans without signing in
4. "Sign In" button visible to navigate to login/signup selection screen

**Test Data:**
- No token

---

### TC-E2E-AUTH-034: Auto-login NEVER triggers Google or Phone OAuth

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-010, BR-011 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Previously logged in via Google
- [ ] Valid JWT stored

**Test Steps:**
1. Log in with Google Sign-In previously
2. Kill app
3. Reopen app
4. Observe auto-login behavior

**Expected Results:**
1. Auto-login checks ONLY JWT token validity
2. Does NOT invoke Google Sign-In or Google account picker
3. Does NOT invoke Phone OTP
4. If token valid → Dashboard directly
5. If token expired → Login screen (NO automatic Google/Phone)

**Test Data:**
- N/A

---

### TC-E2E-AUTH-035: Google Sign-In for existing user

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-AUTH-005 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Existing user linked to Google account
- [ ] Google account on device

**Test Steps:**
1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account linked to existing user
4. Observe

**Expected Results:**
1. Google auth succeeds
2. System finds existing user by Google ID/email
3. JWT generated → stored
4. Redirected to Dashboard

**Test Data:**
- Google account linked to user in system

---

### TC-E2E-AUTH-036: Google Sign-In → new user → signup flow

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-AUTH-005 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account not registered in system
- [ ] Google account on device

**Test Steps:**
1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account NOT linked to any user
4. Observe

**Expected Results:**
1. Google auth succeeds with verified email + name
2. System finds NO matching user
3. Redirected to signup flow
4. Email pre-filled (read-only), Name pre-filled (editable)
5. Phone verification required
6. Complete signup → account created

**Test Data:**
- New Google account

---

### TC-E2E-AUTH-037: Google Sign-In cancelled by user

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-AUTH-005 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account on device

**Test Steps:**
1. Tap "Sign in with Google"
2. When account picker appears, tap outside to cancel
3. Observe

**Expected Results:**
1. Returns to login screen
2. No error shown
3. User can try other methods

**Test Data:**
- N/A

---

### TC-E2E-AUTH-038: Google Sign-In network failure → retry

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S1-Major |
| **Linked BR** | BR-010 |
| **Linked UC** | UC-AUTH-005 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Google account on device
- [ ] Ability to toggle network

**Test Steps:**
1. Enable airplane mode
2. Tap "Sign in with Google"
3. Observe
4. Disable airplane mode
5. Tap "Sign in with Google" again

**Expected Results:**
1. Google auth fails with network error
2. Error toast/message displayed
3. Google sign-in button remains available
4. After network restored, sign-in succeeds

**Test Data:**
- N/A

---

### TC-E2E-AUTH-039: Phone Sign-In for existing user

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-006 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543212
- [ ] User registered with this phone

**Test Steps:**
1. Open app → login screen
2. Tap "Sign in with Phone"
3. Enter phone: 9876543212
4. Tap "Send OTP" → receive SMS
5. Enter correct OTP
6. Tap "Verify OTP"

**Expected Results:**
1. OTP sent via SMS
2. OTP verified
3. System finds user by phone → JWT generated
4. Redirected to Dashboard

**Test Data:**
- phone: 9876543212

---

### TC-E2E-AUTH-040: Phone Sign-In → new user → signup flow

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-006 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM: 9876543214
- [ ] Phone not registered

**Test Steps:**
1. Tap "Sign in with Phone"
2. Enter unregistered phone: 9876543214
3. Send OTP → verify OTP
4. Observe

**Expected Results:**
1. OTP verified
2. System finds NO user with this phone
3. Redirected to signup flow
4. Phone pre-filled (read-only)
5. Complete email → address → password → account created

**Test Data:**
- phone: 9876543214 (unregistered)

---

### TC-E2E-AUTH-041: Wrong OTP during phone sign-in → retry

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-006 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM

**Test Steps:**
1. Enter phone → send OTP
2. Enter wrong OTP → see error
3. Enter correct OTP
4. Tap "Verify"

**Expected Results:**
1. Wrong OTP → "Invalid or expired OTP"
2. Correct OTP → proceeds to login

**Test Data:**
- phone: 9876543212

---

### TC-E2E-AUTH-042: Phone not registered → signup redirect

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-006 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM (unregistered)

**Test Steps:**
1. Tap "Sign in with Phone"
2. Enter phone not in system → verify OTP
3. Observe redirect

**Expected Results:**
1. OTP verified
2. "User not found" → redirect to signup
3. Phone pre-filled

**Test Data:**
- phone: 9876543210 (if not pre-registered)

---

### TC-E2E-AUTH-043: Firebase Phone verification during signup

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-007a |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth enabled in console
- [ ] Phone with SIM: 9876543213
- [ ] App built with google-services.json

**Test Steps:**
1. Start signup flow (email-first or phone-first)
2. On phone entry screen
3. Enter phone: 9876543213
4. Tap "Verify via Firebase" button
5. Firebase initiates verification → SMS sent
6. Enter 6-digit SMS code
7. Observe

**Expected Results:**
1. "Verify via Firebase" button visible and blue (OutlinedButton.icon)
2. SMS received from Firebase
3. Phone verified via Firebase
4. Toast: "Phone Verified via Firebase"
5. Proceeds to next signup step

**Test Data:**
- phone: 9876543213

---

### TC-E2E-AUTH-044: Firebase OTP timeout → resend

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-007a |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth working

**Test Steps:**
1. Enter phone → tap "Verify via Firebase"
2. Wait 60+ seconds without entering code
3. See timeout message
4. Tap "Resend"
5. New SMS received → enter code

**Expected Results:**
1. Timeout notification after 60s
2. Resend button enabled
3. New SMS sent
4. Code accepted after resend

**Test Data:**
- phone: 9876543213

---

### TC-E2E-AUTH-045: Wrong Firebase OTP → retry

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-007a |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth working

**Test Steps:**
1. Enter phone → tap "Verify via Firebase"
2. SMS received
3. Enter wrong code
4. Observe → re-enter correct code

**Expected Results:**
1. Error toast: "Invalid verification code"
2. User can retry
3. Correct code accepted

**Test Data:**
- phone: 9876543213

---

### TC-E2E-AUTH-046: Firebase auth network failure → fallback to backend OTP

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S1-Major |
| **Linked BR** | BR-002 |
| **Linked UC** | UC-AUTH-007a |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth configured
- [ ] Ability to toggle network

**Test Steps:**
1. Enable airplane mode
2. Enter phone → tap "Verify via Firebase"
3. Observe error
4. Disable airplane mode
5. Check if "Send OTP" (backend) button is available

**Expected Results:**
1. Firebase auth fails with network error
2. Error toast displayed
3. Backend "Send OTP" button still available
4. User can use backend OTP as fallback

**Test Data:**
- phone: 9876543213

---

### TC-E2E-AUTH-047: Firebase verified phone → existing user login

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-007b |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth enabled
- [ ] User exists with phone 9876543212
- [ ] Phone with SIM

**Test Steps:**
1. On login screen → tap "Sign in with Phone"
2. Enter phone of existing user: 9876543212
3. Tap "Verify via Firebase"
4. Complete Firebase verification
5. Observe

**Expected Results:**
1. Firebase verification succeeds
2. System finds existing user
3. JWT generated → logged in
4. Redirected to Dashboard

**Test Data:**
- phone: 9876543212

---

### TC-E2E-AUTH-048: Firebase verified phone → no user → signup redirect

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-011 |
| **Linked UC** | UC-AUTH-007b |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Firebase Phone Auth enabled
- [ ] Phone not in system

**Test Steps:**
1. On login screen → tap "Sign in with Phone"
2. Enter unregistered phone
3. Tap "Verify via Firebase"
4. Complete verification
5. Observe

**Expected Results:**
1. Firebase verification succeeds
2. System finds NO matching user
3. Redirected to signup flow
4. Phone pre-filled

**Test Data:**
- phone: 9876543210 (unregistered)

---

### TC-E2E-AUTH-049: Reset password via mobile OTP → success

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User exists with phone 9876543212
- [ ] Phone with SIM

**Test Steps:**
1. On login screen → tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter phone: 9876543212
4. Tap "Send OTP" → receive SMS
5. Enter OTP → tap "Verify"
6. Enter new password: NewPass123!
7. Confirm password
8. Tap "Reset Password"
9. Navigate to login → login with new password

**Expected Results:**
1. OTP sent to phone
2. OTP verified
3. Password reset successful (BCrypt hash updated)
4. Old sessions invalidated
5. Login with new password succeeds
6. Login with old password fails

**Test Data:**
- phone: 9876543212
- new password: NewPass123!
- old password: TestPass123!

---

### TC-E2E-AUTH-050: Reset password via email code → success

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User exists with email
- [ ] Email inbox accessible

**Test Steps:**
1. On login screen → tap "Forgot Password?"
2. Select "Reset via Email OTP"
3. Enter email: e2e-existing@bookmyjuice.co.in
4. Tap "Send Code" → receive email
5. Enter 6-digit code → tap "Verify"
6. Enter new password: ResetPass123!
7. Confirm
8. Tap "Reset Password"
9. Login with new password

**Expected Results:**
1. Code sent to email
2. Code verified
3. Password reset successful
4. New password works for login

**Test Data:**
- email: e2e-existing@bookmyjuice.co.in
- new password: ResetPass123!

---

### TC-E2E-AUTH-051: Reset password with unregistered phone/email

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App on forgot password screen

**Test Steps:**
1. Tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter unregistered phone: 9999999999
4. Tap "Send OTP"

**Expected Results:**
1. Error: "Phone number not registered" or equivalent
2. User cannot proceed with unregistered phone

**Test Data:**
- phone: 9999999999 (not registered)

---

### TC-E2E-AUTH-052: Reset password → weak password rejected

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Code verified

**Test Steps:**
1. Verify OTP/email code successfully
2. On new password screen, enter: "weak"
3. Tap "Reset Password"

**Expected Results:**
1. Password requirements shown in red
2. Submit disabled
3. Weak password rejected

**Test Data:**
- password: weak

---

### TC-E2E-AUTH-053: Reset password → old sessions invalidated

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-009 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in on Device 1
- [ ] Access to reset on Device 2

**Test Steps:**
1. User A is logged in on Device 1
2. On Device 2, reset password for User A
3. On Device 1, try to use the app (trigger API call)

**Expected Results:**
1. Device 1's JWT is invalidated
2. Device 1 gets 401 on next API call
3. Device 1 redirects to login screen

**Test Data:**
- User A credentials

---

### TC-E2E-AUTH-054: Rate limited OTP reset attempts

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P2-Medium |
| **Severity** | S1-Major |
| **Linked BR** | BR-009, NFR-011 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] Phone with SIM

**Test Steps:**
1. Tap "Forgot Password?" → enter phone
2. Send OTP → wrong OTP → retry → repeat 4 more times (5 total)
3. Try one more time

**Expected Results:**
1. Maximum 3 verification attempts per OTP enforced
2. After max attempts, "Maximum attempts reached. Request new OTP."
3. Rate limit: 5 attempts per hour per phone

**Test Data:**
- phone: 9876543212

---

### TC-E2E-AUTH-055: OTP rate limit enforced (10 attempts/5min per IP)

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | NFR-011 |
| **Linked UC** | UC-AUTH-001 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] App can send OTP repeatedly

**Test Steps:**
1. Send OTP for phone: 9876543210
2. Repeat step 1 nine more times within 5 minutes (total 10)
3. Try 11th OTP send

**Expected Results:**
1. First 10 OTP requests succeed (SMS sent or rate limit token consumed)
2. 11th request: "Too many requests. Please try again later."
3. Rate limit resets after 5 minutes

**Test Data:**
- phone: 9876543210

---

### TC-E2E-AUTH-056: JWT token contains valid claims

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] User logged in

**Test Steps:**
1. Log in successfully → capture JWT token
2. Decode JWT (base64 decode the payload)
3. Verify claims

**Expected Results:**
1. JWT has 3 segments (header.payload.signature)
2. Payload contains: sub (user identifier), iat (issued at), exp (expiry)
3. exp = iat + 30 days (2592000 seconds)
4. Signature is valid

**Test Data:**
- JWT captured from API response

---

### TC-E2E-AUTH-057: API rejects requests without JWT for protected endpoints

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Linked BR** | BR-006 |
| **Linked UC** | UC-AUTH-004 |
| **Auto** | ❌ Manual |

**Preconditions:**
- [ ] API running

**Test Steps:**
1. Call GET /api/v1/orders (authenticated endpoint) WITHOUT Authorization header
2. Call GET /api/v1/cart/merge (authenticated) WITHOUT JWT

**Expected Results:**
1. 401 Unauthorized returned
2. Error: "Authentication required" or "Full authentication is required"
3. No data returned

**Test Data:**
- No JWT token in request

---

### TC-E2E-AUTH-058: Concurrent duplicate signup requests

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
- [ ] Fresh email not in system

**Test Steps:**
1. Prepare signup data for new email
2. Submit two signup requests simultaneously (rapid double-tap)
3. Observe

**Expected Results:**
1. First request succeeds (user created)
2. Second request fails with duplicate error
3. No duplicate user created in database

**Test Data:**
- email: unique-test@bookmyjuice.co.in

---

### TC-E2E-AUTH-059: Special characters in name/address fields

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
- [ ] App in signup flow

**Test Steps:**
1. During signup, enter name: "John O'Brien-Smith"
2. Address: "123 Main St., Apt #4B"
3. Complete signup
4. View profile

**Expected Results:**
1. Special characters accepted
2. Name displayed correctly in profile
3. Address fields saved correctly

**Test Data:**
- name: John O'Brien-Smith
- address: 123 Main St., Apt #4B

---

### TC-E2E-AUTH-060: Very long input fields (boundary testing)

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
- [ ] App in signup flow

**Test Steps:**
1. During signup, enter name with 255 characters
2. Enter address lines with 500 characters each
3. Attempt to proceed

**Expected Results:**
1. Fields accept reasonable input lengths
2. Database constraints enforced (VARCHAR limits)
3. No crash or data truncation error

**Test Data:**
- Very long text strings

---

## Document Control

- **Created:** 2026-05-19
- **Version:** 1.0
- **Total Test Cases:** 60
- **Status:** ✅ Complete
