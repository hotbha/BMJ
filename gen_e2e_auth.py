#!/usr/bin/env python3
"""Generate TC_E2E_AUTH.md - 60 E2E test cases for Authentication module"""
import os

tcs = []

def tc(tid, title, priority, severity, br, uc, steps, expected, preconditions, data, auto="❌ Manual"):
    return f"""
### {tid}: {title}

| Field | Value |
|-------|-------|
| **Module** | AUTH |
| **Type** | E2E (Black Box) |
| **Priority** | {priority} |
| **Severity** | {severity} |
| **Linked BR** | {br} |
| **Linked UC** | {uc} |
| **Auto** | {auto} |

**Preconditions:**
{preconditions}

**Test Steps:**
{steps}

**Expected Results:**
{expected}

**Test Data:**
{data}
"""

# ============ 1. Email-First Signup (15 TCs) ============

tcs.append(tc("TC-E2E-AUTH-001", "Complete email-first signup with valid data",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Open app → see login/signup screen
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
17. Tap "Create Account\"""",
    """1. Verification code sent to email within 30 seconds
2. OTP sent to phone via SMS within 30 seconds
3. All data validated without errors at each step
4. Account created successfully
5. User automatically logged in (JWT generated)
6. Redirected to Dashboard
7. Welcome message displayed""",
    """- [ ] Email inbox accessible: e2e-test-email@bookmyjuice.co.in
- [ ] Phone with SIM: 9876543210
- [ ] App on login/signup screen""",
    """- email: e2e-test-email@bookmyjuice.co.in
- phone: 9876543210
- password: TestPass123! (8+ chars, 1 uppercase, 1 lowercase, 2 numbers, 1 special)
- address: Flat A-101, Green Valley, Sector 12, Gurgaon, Haryana, 122001, India"""))

tcs.append(tc("TC-E2E-AUTH-002", "Invalid email format rejected during signup",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Open app → login/signup screen
2. Tap "Sign up with Email"
3. Enter invalid email: "not-an-email"
4. Tap "Continue\"""",
    """1. "Please enter a valid email" error shown immediately
2. "Continue" button remains disabled or returns error
3. User cannot proceed to next step""",
    """- [ ] App on email entry screen""",
    """- email: not-an-email (invalid format)"""))

tcs.append(tc("TC-E2E-AUTH-003", "Duplicate email shows error during signup",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Open app → login/signup screen
2. Tap "Sign up with Email"
3. Enter email of already-registered user: e2e-existing@bookmyjuice.co.in
4. Tap "Continue\"""",
    """1. System detects duplicate email
2. Error message: "Email is already registered"
3. "Login" button offered as option
4. User can navigate to login screen""",
    """- [ ] Account with e2e-existing@bookmyjuice.co.in already exists
- [ ] App on email entry screen""",
    """- email: e2e-existing@bookmyjuice.co.in (already registered)"""))

tcs.append(tc("TC-E2E-AUTH-004", "Wrong email verification code entered",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Enter valid email
2. Tap "Continue" → code sent to email
3. Enter wrong 6-digit code: "111111"
4. Tap "Verify Email\"""",
    """1. Error displayed: "Invalid or expired verification code"
2. User can re-enter correct code
3. Correct code accepted on retry""",
    """- [ ] Email inbox accessible""",
    """- email: e2e-test-email@bookmyjuice.co.in
- wrong code: 111111"""))

tcs.append(tc("TC-E2E-AUTH-005", "Expired verification code → resend new code",
    "P1-High", "S1-Major", "BR-001, UC-AUTH-007c", "UC-AUTH-001",
    """1. Enter valid email → tap "Continue"
2. Wait 10+ minutes (code expires)
3. Enter the original 6-digit code
4. Tap "Verify Email"
5. See "Code expired" error
6. Tap "Resend Code" (wait 30s cooldown)
7. Receive new code in email
8. Enter new 6-digit code
9. Tap "Verify Email\"""",
    """1. Expired code shows: "Code expired. Please request a new code."
2. Resend button disabled for 30 seconds (countdown shown)
3. After 30s, resend enabled
4. New code sent → old code invalidated
5. New code accepted""",
    """- [ ] Email inbox accessible""",
    """- email: e2e-test-email@bookmyjuice.co.in"""))

tcs.append(tc("TC-E2E-AUTH-006", "Max resend attempts reached for email verification",
    "P2-Medium", "S2-Minor", "BR-001", "UC-AUTH-001",
    """1. Enter valid email → tap "Continue"
2. Tap "Resend Code" → wait 30s → repeat 4 more times (total 5 resends)
3. Tap "Resend Code" a 6th time""",
    """1. Resend button disabled after 5 attempts
2. Message: "Maximum resend attempts reached. Please try again later."
3. User cannot send more codes""",
    """- [ ] Email inbox accessible""",
    """- email: e2e-test-email@bookmyjuice.co.in
- Max resends: 5"""))

tcs.append(tc("TC-E2E-AUTH-007", "Code resend before 30s cooldown",
    "P2-Medium", "S2-Minor", "BR-001", "UC-AUTH-001",
    """1. Enter valid email → tap "Continue" → code sent
2. Immediately tap "Resend Code" (within 30s)""",
    """1. Resend button is disabled/greyed out
2. Countdown timer visible showing remaining seconds
3. Button becomes enabled after 30 seconds""",
    """- [ ] Email inbox accessible""",
    """- email: e2e-test-email@bookmyjuice.co.in"""))

tcs.append(tc("TC-E2E-AUTH-008", "Invalid phone format rejected during signup",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-001",
    """1. Complete email verification step
2. On phone entry screen, enter: "12345" (5 digits)
3. Tap "Send OTP\"""",
    """1. Error: "Please enter a valid 10-digit Indian number"
2. User cannot proceed with invalid phone
3. Valid 10-digit number accepted""",
    """- [ ] Email verified in current signup flow""",
    """- phone: 12345 (invalid - too short)"""))

tcs.append(tc("TC-E2E-AUTH-009", "Wrong OTP entered during signup",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-001",
    """1. Enter valid phone → tap "Send OTP"
2. Receive real OTP via SMS
3. Enter wrong 6-digit OTP: "999999"
4. Tap "Verify OTP\"""",
    """1. Error: "Invalid or expired OTP"
2. User can retry with correct OTP
3. Correct OTP accepted on retry""",
    """- [ ] Phone with SIM for OTP reception""",
    """- phone: 9876543210
- wrong OTP: 999999"""))

tcs.append(tc("TC-E2E-AUTH-010", "Expired OTP → resend new OTP",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-001",
    """1. Enter valid phone → tap "Send OTP"
2. Wait 10+ minutes (OTP expires)
3. Enter original OTP → see expiry error
4. Tap "Resend OTP" (wait 30s)
5. Receive new OTP via SMS
6. Enter new OTP
7. Tap "Verify OTP\"""",
    """1. "OTP expired" error shown
2. Resend disabled for 30s countdown
3. New OTP sent → old invalidated
4. New OTP accepted""",
    """- [ ] Phone with SIM""",
    """- phone: 9876543210"""))

tcs.append(tc("TC-E2E-AUTH-011", "Missing required address field during signup",
    "P1-High", "S1-Major", "BR-070", "UC-AUTH-001",
    """1. Complete email verification + phone OTP steps
2. On address entry screen, leave "City" field empty
3. Fill all other fields
4. Tap "Continue\"""",
    """1. "City" field highlighted/underlined in red
2. Error: "City is required" or equivalent
3. User cannot proceed
4. After filling city, tap Continue → proceeds""",
    """- [ ] Email + phone verified""",
    """- address: Flat A-101, Green Valley, (City empty), Haryana, 122001, India"""))

tcs.append(tc("TC-E2E-AUTH-012", "Weak password rejected during signup",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Complete email, phone, address steps
2. On password screen, enter: "weak"
3. Tap "Create Account\"""",
    """1. Password validator shows requirements in red
2. Submit button disabled
3. Requirements shown: 8+ chars, uppercase, lowercase, 2+ numbers, 1+ special
4. "weak" fails all checks""",
    """- [ ] Email + phone + address completed""",
    """- password: weak (fails: length < 8, no uppercase, no numbers, no special)"""))

tcs.append(tc("TC-E2E-AUTH-013", "Password mismatch during signup",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. On password screen, enter password: "TestPass123!"
2. In confirm field, enter: "DifferentPass456!"
3. Tap "Create Account\"""",
    """1. Error: "Passwords do not match"
2. User can correct and retry""",
    """- [ ] Email + phone + address completed""",
    """- password: TestPass123!
- confirm: DifferentPass456!"""))

tcs.append(tc("TC-E2E-AUTH-014", "User navigates back mid-signup flow",
    "P2-Medium", "S2-Minor", "BR-001", "UC-AUTH-001",
    """1. Start email-first signup
2. After email verification, tap phone back button
3. Confirm "Discard changes?" dialog
4. Tap "Yes"
5. Check current screen""",
    """1. Back button shows confirmation dialog: "Are you sure? Your progress will be lost."
2. "Yes" → returns to signup method selection screen
3. "No" → stays on current step""",
    """- [ ] App on phone entry screen during signup""",
    """- N/A (navigation test)"""))

tcs.append(tc("TC-E2E-AUTH-015", "Network failure during email verification step",
    "P2-Medium", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Enter valid email → tap "Continue"
2. Enable airplane mode / disconnect network
3. Try to proceed""",
    """1. Loading indicator shown briefly
2. Error: "Network error. Please check your connection."
3. Retry button available
4. After reconnecting network, retry succeeds""",
    """- [ ] Ability to toggle airplane mode""",
    """- email: e2e-test-email@bookmyjuice.co.in"""))

# ============ 2. Phone-First Signup (5 TCs) ============

tcs.append(tc("TC-E2E-AUTH-016", "Complete phone-first signup with valid data",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-002",
    """1. Open app → login/signup screen
2. Tap "Sign up with Phone"
3. Enter phone: 9876543211
4. Tap "Send OTP" → receive SMS
5. Enter OTP → tap "Verify OTP"
6. Enter email: e2e-test-phone@bookmyjuice.co.in
7. Tap "Continue" → code sent to email
8. Enter email verification code
9. Enter full address
10. Enter password + confirm
11. Tap "Create Account\"""",
    """1. OTP sent to phone ✓
2. Email verification code sent ✓
3. Account created automatically
4. JWT generated, logged in
5. Redirected to Dashboard""",
    """- [ ] Phone with SIM: 9876543211
- [ ] Email inbox: e2e-test-phone@bookmyjuice.co.in""",
    """- phone: 9876543211
- email: e2e-test-phone@bookmyjuice.co.in
- password: TestPass123!"""))

tcs.append(tc("TC-E2E-AUTH-017", "Phone-first with non-10-digit phone rejected",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-002",
    """1. Tap "Sign up with Phone"
2. Enter phone: "98765" (5 digits)
3. Tap "Send OTP\"""",
    """1. "Please enter a valid 10-digit Indian number" error
2. Cannot proceed""",
    """- [ ] App on phone entry screen""",
    """- phone: 98765"""))

tcs.append(tc("TC-E2E-AUTH-018", "Wrong OTP → retry → success (phone-first)",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-002",
    """1. Enter phone → send OTP
2. Enter wrong OTP → see error
3. Enter correct OTP from SMS
4. Tap "Verify OTP\"""",
    """1. Wrong OTP → error message
2. Correct OTP → proceeds to next step""",
    """- [ ] Phone with SIM""",
    """- phone: 9876543211"""))

tcs.append(tc("TC-E2E-AUTH-019", "Email already registered during phone-first signup",
    "P1-High", "S1-Major", "BR-001", "UC-AUTH-002",
    """1. Complete phone verification step
2. On email entry, enter: e2e-existing@bookmyjuice.co.in
3. Tap "Continue\"""",
    """1. "Email is already registered" error
2. "Login" button offered""",
    """- [ ] Account with that email exists""",
    """- email: e2e-existing@bookmyjuice.co.in"""))

tcs.append(tc("TC-E2E-AUTH-020", "Cancel mid-phone-first flow",
    "P2-Medium", "S2-Minor", "BR-002", "UC-AUTH-002",
    """1. Start phone-first signup → verify phone
2. On email step, press back
3. Confirm discard dialog
4. Check current screen""",
    """1. Confirmation dialog shown
2. After confirm → returns to signup method selection""",
    """- [ ] Phone verified""",
    """- N/A"""))

# ============ 3. Google Signup (4 TCs) ============

tcs.append(tc("TC-E2E-AUTH-021", "Complete Google signup as new user",
    "P1-High", "S1-Major", "BR-003", "UC-AUTH-003",
    """1. Open app → login/signup screen
2. Tap "Sign up with Google"
3. Select Google account from picker (e2e-google-test@gmail.com)
4. Verify pre-filled email (read-only) + name (editable)
5. Enter phone: 9876543210
6. Tap "Send OTP" → verify OTP
7. Enter address
8. Enter password + confirm
9. Tap "Create Account\"""",
    """1. Google auth returns verified email + name
2. Email pre-filled and read-only ✓
3. Name pre-filled and editable ✓
4. Phone verification still required ✓
5. Account created with Google email
6. Auto-logged in → Dashboard""",
    """- [ ] Google account e2e-google-test@gmail.com on device
- [ ] OAuth consent screen configured with test user
- [ ] google-services.json has non-empty oauth_client""",
    """- Google account: e2e-google-test@gmail.com
- phone: 9876543210
- password: TestPass123!"""))

tcs.append(tc("TC-E2E-AUTH-022", "Google auth cancelled by user",
    "P2-Medium", "S2-Minor", "BR-003", "UC-AUTH-003",
    """1. Tap "Sign up with Google"
2. When Google account picker appears, dismiss/cancel
3. Check current screen""",
    """1. Returns to login/signup method selection screen
2. No error shown
3. User can try other signup methods""",
    """- [ ] Google account on device""",
    """- N/A"""))

tcs.append(tc("TC-E2E-AUTH-023", "Google email already registered → login redirect",
    "P1-High", "S1-Major", "BR-003, BR-010", "UC-AUTH-003, UC-AUTH-005",
    """1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account whose email is already registered
4. Observe system behavior""",
    """1. Google auth succeeds
2. System finds user with matching email
3. User is logged in automatically (JWT generated)
4. Redirected to Dashboard""",
    """- [ ] Registered user with that Google email exists
- [ ] Google account on device""",
    """- Google account email already in system"""))

tcs.append(tc("TC-E2E-AUTH-024", "Phone already registered during Google signup",
    "P1-High", "S1-Major", "BR-003", "UC-AUTH-003",
    """1. Complete Google auth → get to phone entry
2. Enter phone of existing user: 9876543212
3. Tap "Send OTP" → verify OTP
4. Check system response""",
    """1. After phone verification, system detects phone in use
2. Error: "Phone number is already registered"
3. "Login" button offered
4. User redirected to login""",
    """- [ ] Google account on device
- [ ] Phone 9876543212 already registered""",
    """- phone: 9876543212 (already registered)"""))

# ============ 4. User Login (6 TCs) ============

tcs.append(tc("TC-E2E-AUTH-025", "Login with valid email and password",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Open app → login screen
2. Enter email: e2e-existing@bookmyjuice.co.in
3. Enter password: TestPass123!
4. Tap "Login\"""",
    """1. Loading indicator shown
2. Login successful
3. JWT token stored in SharedPreferences
4. Redirected to Dashboard
5. User name/email visible on profile""",
    """- [ ] User e2e-existing@bookmyjuice.co.in exists
- [ ] Correct password known""",
    """- email: e2e-existing@bookmyjuice.co.in
- password: TestPass123!"""))

tcs.append(tc("TC-E2E-AUTH-026", "Login with wrong password",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Open app → login screen
2. Enter email: e2e-existing@bookmyjuice.co.in
3. Enter password: WrongPass123!
4. Tap "Login\"""",
    """1. Error: "Invalid email or password"
2. User stays on login screen
3. Can retry with correct password""",
    """- [ ] User exists with known password""",
    """- email: e2e-existing@bookmyjuice.co.in
- password: WrongPass123!"""))

tcs.append(tc("TC-E2E-AUTH-027", "Login with unregistered email",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Open app → login screen
2. Enter email: unknown@example.com
3. Enter password: SomePass123!
4. Tap "Login\"""",
    """1. Error: "Invalid email or password" (generic, doesn't reveal existence)
2. User stays on login screen""",
    """- [ ] App on login screen""",
    """- email: unknown@example.com (not registered)
- password: SomePass123!"""))

tcs.append(tc("TC-E2E-AUTH-028", "Login with phone as username and password",
    "P1-High", "S1-Major", "BR-006, PD-AUTH-001", "UC-AUTH-004",
    """1. Open app → login screen
2. Enter phone: 9876543212 (as username)
3. Enter password: TestPass123!
4. Tap "Login\"""",
    """1. Login successful (username=phone field works)
2. JWT generated
3. Redirected to Dashboard""",
    """- [ ] User with phone 9876543212 exists""",
    """- username/phone: 9876543212
- password: TestPass123!"""))

tcs.append(tc("TC-E2E-AUTH-029", "Empty fields validation on login",
    "P2-Medium", "S2-Minor", "BR-006", "UC-AUTH-004",
    """1. Open app → login screen
2. Leave email field empty
3. Leave password field empty
4. Tap "Login\"""",
    """1. "Please enter email" validation shown
2. "Please enter password" validation shown
3. Form not submitted""",
    """- [ ] App on login screen""",
    """- email: (empty)
- password: (empty)"""))

tcs.append(tc("TC-E2E-AUTH-030", "Account locked after 5 failed login attempts",
    "P1-High", "S1-Major", "BR-006, NFR-011", "UC-AUTH-004",
    """1. Open app → login screen
2. Enter valid email
3. Enter wrong password → submit (1st attempt)
4. Repeat step 3 four more times (total 5 failures)
5. Enter correct password this time""",
    """1. First 4 failures: "Invalid email or password"
2. After 5th failure (or threshold): "Account locked. Reset password?" or rate limit message
3. Even correct password rejected
4. "Reset Password" option offered""",
    """- [ ] User exists with known password""",
    """- email: e2e-existing@bookmyjuice.co.in"""))

# ============ 5. Auto-Login (4 TCs) ============

tcs.append(tc("TC-E2E-AUTH-031", "Auto-login with valid JWT token",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Log in successfully (JWT stored)
2. Kill app completely (swipe from recents)
3. Reopen app""",
    """1. Splash screen shown briefly
2. App checks JWT in SharedPreferences
3. Validates token with server (GET /api/auth/me)
4. Auto-login succeeds → Dashboard shown directly
5. NO login screen shown""",
    """- [ ] User logged in with valid JWT stored""",
    """- N/A (auto-login flow)"""))

tcs.append(tc("TC-E2E-AUTH-032", "Auto-login with expired JWT → login screen",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Log in successfully
2. Manually expire/modify JWT to be expired (or wait 30 days)
3. Kill app
4. Reopen app""",
    """1. App checks JWT → finds expired token
2. Clears expired token from SharedPreferences
3. Shows login screen
4. User must re-authenticate""",
    """- [ ] Expired JWT in storage""",
    """- Expired JWT token"""))

tcs.append(tc("TC-E2E-AUTH-033", "Auto-login with missing token → login screen",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Clear app data / fresh install
2. Open app""",
    """1. No JWT in SharedPreferences
2. Login screen displayed directly
3. Signup/Login options available""",
    """- [ ] Fresh install or cleared app data""",
    """- No token"""))

tcs.append(tc("TC-E2E-AUTH-034", "Auto-login NEVER triggers Google or Phone OAuth",
    "P1-High", "S1-Major", "BR-010, BR-011", "UC-AUTH-004",
    """1. Log in with Google Sign-In previously
2. Kill app
3. Reopen app
4. Observe auto-login behavior""",
    """1. Auto-login checks ONLY JWT token validity
2. Does NOT invoke Google Sign-In or Google account picker
3. Does NOT invoke Phone OTP
4. If token valid → Dashboard directly
5. If token expired → Login screen (NO automatic Google/Phone)""",
    """- [ ] Previously logged in via Google
- [ ] Valid JWT stored""",
    """- N/A"""))

# ============ 6. Google Sign-In (4 TCs) ============

tcs.append(tc("TC-E2E-AUTH-035", "Google Sign-In for existing user",
    "P1-High", "S1-Major", "BR-010", "UC-AUTH-005",
    """1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account linked to existing user
4. Observe""",
    """1. Google auth succeeds
2. System finds existing user by Google ID/email
3. JWT generated → stored
4. Redirected to Dashboard""",
    """- [ ] Existing user linked to Google account
- [ ] Google account on device""",
    """- Google account linked to user in system"""))

tcs.append(tc("TC-E2E-AUTH-036", "Google Sign-In → new user → signup flow",
    "P1-High", "S1-Major", "BR-010", "UC-AUTH-005",
    """1. Open app → login screen
2. Tap "Sign in with Google"
3. Select Google account NOT linked to any user
4. Observe""",
    """1. Google auth succeeds with verified email + name
2. System finds NO matching user
3. Redirected to signup flow
4. Email pre-filled (read-only), Name pre-filled (editable)
5. Phone verification required
6. Complete signup → account created""",
    """- [ ] Google account not registered in system
- [ ] Google account on device""",
    """- New Google account"""))

tcs.append(tc("TC-E2E-AUTH-037", "Google Sign-In cancelled by user",
    "P2-Medium", "S2-Minor", "BR-010", "UC-AUTH-005",
    """1. Tap "Sign in with Google"
2. When account picker appears, tap outside to cancel
3. Observe""",
    """1. Returns to login screen
2. No error shown
3. User can try other methods""",
    """- [ ] Google account on device""",
    """- N/A"""))

tcs.append(tc("TC-E2E-AUTH-038", "Google Sign-In network failure → retry",
    "P2-Medium", "S1-Major", "BR-010", "UC-AUTH-005",
    """1. Enable airplane mode
2. Tap "Sign in with Google"
3. Observe
4. Disable airplane mode
5. Tap "Sign in with Google" again""",
    """1. Google auth fails with network error
2. Error toast/message displayed
3. Google sign-in button remains available
4. After network restored, sign-in succeeds""",
    """- [ ] Google account on device
- [ ] Ability to toggle network""",
    """- N/A"""))

# ============ 7. Phone Sign-In (4 TCs) ============

tcs.append(tc("TC-E2E-AUTH-039", "Phone Sign-In for existing user",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-006",
    """1. Open app → login screen
2. Tap "Sign in with Phone"
3. Enter phone: 9876543212
4. Tap "Send OTP" → receive SMS
5. Enter correct OTP
6. Tap "Verify OTP\"""",
    """1. OTP sent via SMS
2. OTP verified
3. System finds user by phone → JWT generated
4. Redirected to Dashboard""",
    """- [ ] Phone with SIM: 9876543212
- [ ] User registered with this phone""",
    """- phone: 9876543212"""))

tcs.append(tc("TC-E2E-AUTH-040", "Phone Sign-In → new user → signup flow",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-006",
    """1. Tap "Sign in with Phone"
2. Enter unregistered phone: 9876543214
3. Send OTP → verify OTP
4. Observe""",
    """1. OTP verified
2. System finds NO user with this phone
3. Redirected to signup flow
4. Phone pre-filled (read-only)
5. Complete email → address → password → account created""",
    """- [ ] Phone with SIM: 9876543214
- [ ] Phone not registered""",
    """- phone: 9876543214 (unregistered)"""))

tcs.append(tc("TC-E2E-AUTH-041", "Wrong OTP during phone sign-in → retry",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-006",
    """1. Enter phone → send OTP
2. Enter wrong OTP → see error
3. Enter correct OTP
4. Tap "Verify\"""",
    """1. Wrong OTP → "Invalid or expired OTP"
2. Correct OTP → proceeds to login""",
    """- [ ] Phone with SIM""",
    """- phone: 9876543212"""))

tcs.append(tc("TC-E2E-AUTH-042", "Phone not registered → signup redirect",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-006",
    """1. Tap "Sign in with Phone"
2. Enter phone not in system → verify OTP
3. Observe redirect""",
    """1. OTP verified
2. "User not found" → redirect to signup
3. Phone pre-filled""",
    """- [ ] Phone with SIM (unregistered)""",
    """- phone: 9876543210 (if not pre-registered)"""))

# ============ 8. Firebase Phone Auth Signup (4 TCs) ============

tcs.append(tc("TC-E2E-AUTH-043", "Firebase Phone verification during signup",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-007a",
    """1. Start signup flow (email-first or phone-first)
2. On phone entry screen
3. Enter phone: 9876543213
4. Tap "Verify via Firebase" button
5. Firebase initiates verification → SMS sent
6. Enter 6-digit SMS code
7. Observe""",
    """1. "Verify via Firebase" button visible and blue (OutlinedButton.icon)
2. SMS received from Firebase
3. Phone verified via Firebase
4. Toast: "Phone Verified via Firebase"
5. Proceeds to next signup step""",
    """- [ ] Firebase Phone Auth enabled in console
- [ ] Phone with SIM: 9876543213
- [ ] App built with google-services.json""",
    """- phone: 9876543213"""))

tcs.append(tc("TC-E2E-AUTH-044", "Firebase OTP timeout → resend",
    "P2-Medium", "S2-Minor", "BR-002", "UC-AUTH-007a",
    """1. Enter phone → tap "Verify via Firebase"
2. Wait 60+ seconds without entering code
3. See timeout message
4. Tap "Resend"
5. New SMS received → enter code""",
    """1. Timeout notification after 60s
2. Resend button enabled
3. New SMS sent
4. Code accepted after resend""",
    """- [ ] Firebase Phone Auth working""",
    """- phone: 9876543213"""))

tcs.append(tc("TC-E2E-AUTH-045", "Wrong Firebase OTP → retry",
    "P1-High", "S1-Major", "BR-002", "UC-AUTH-007a",
    """1. Enter phone → tap "Verify via Firebase"
2. SMS received
3. Enter wrong code
4. Observe → re-enter correct code""",
    """1. Error toast: "Invalid verification code"
2. User can retry
3. Correct code accepted""",
    """- [ ] Firebase Phone Auth working""",
    """- phone: 9876543213"""))

tcs.append(tc("TC-E2E-AUTH-046", "Firebase auth network failure → fallback to backend OTP",
    "P2-Medium", "S1-Major", "BR-002", "UC-AUTH-007a",
    """1. Enable airplane mode
2. Enter phone → tap "Verify via Firebase"
3. Observe error
4. Disable airplane mode
5. Check if "Send OTP" (backend) button is available""",
    """1. Firebase auth fails with network error
2. Error toast displayed
3. Backend "Send OTP" button still available
4. User can use backend OTP as fallback""",
    """- [ ] Firebase Phone Auth configured
- [ ] Ability to toggle network""",
    """- phone: 9876543213"""))

# ============ 9. Firebase Phone Auth Login (2 TCs) ============

tcs.append(tc("TC-E2E-AUTH-047", "Firebase verified phone → existing user login",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-007b",
    """1. On login screen → tap "Sign in with Phone"
2. Enter phone of existing user: 9876543212
3. Tap "Verify via Firebase"
4. Complete Firebase verification
5. Observe""",
    """1. Firebase verification succeeds
2. System finds existing user
3. JWT generated → logged in
4. Redirected to Dashboard""",
    """- [ ] Firebase Phone Auth enabled
- [ ] User exists with phone 9876543212
- [ ] Phone with SIM""",
    """- phone: 9876543212"""))

tcs.append(tc("TC-E2E-AUTH-048", "Firebase verified phone → no user → signup redirect",
    "P1-High", "S1-Major", "BR-011", "UC-AUTH-007b",
    """1. On login screen → tap "Sign in with Phone"
2. Enter unregistered phone
3. Tap "Verify via Firebase"
4. Complete verification
5. Observe""",
    """1. Firebase verification succeeds
2. System finds NO matching user
3. Redirected to signup flow
4. Phone pre-filled""",
    """- [ ] Firebase Phone Auth enabled
- [ ] Phone not in system""",
    """- phone: 9876543210 (unregistered)"""))

# ============ 10. Password Reset (6 TCs) ============

tcs.append(tc("TC-E2E-AUTH-049", "Reset password via mobile OTP → success",
    "P1-High", "S1-Major", "BR-009", "UC-AUTH-004",
    """1. On login screen → tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter phone: 9876543212
4. Tap "Send OTP" → receive SMS
5. Enter OTP → tap "Verify"
6. Enter new password: NewPass123!
7. Confirm password
8. Tap "Reset Password"
9. Navigate to login → login with new password""",
    """1. OTP sent to phone
2. OTP verified
3. Password reset successful (BCrypt hash updated)
4. Old sessions invalidated
5. Login with new password succeeds
6. Login with old password fails""",
    """- [ ] User exists with phone 9876543212
- [ ] Phone with SIM""",
    """- phone: 9876543212
- new password: NewPass123!
- old password: TestPass123!"""))

tcs.append(tc("TC-E2E-AUTH-050", "Reset password via email code → success",
    "P1-High", "S1-Major", "BR-009", "UC-AUTH-004",
    """1. On login screen → tap "Forgot Password?"
2. Select "Reset via Email OTP"
3. Enter email: e2e-existing@bookmyjuice.co.in
4. Tap "Send Code" → receive email
5. Enter 6-digit code → tap "Verify"
6. Enter new password: ResetPass123!
7. Confirm
8. Tap "Reset Password"
9. Login with new password""",
    """1. Code sent to email
2. Code verified
3. Password reset successful
4. New password works for login""",
    """- [ ] User exists with email
- [ ] Email inbox accessible""",
    """- email: e2e-existing@bookmyjuice.co.in
- new password: ResetPass123!"""))

tcs.append(tc("TC-E2E-AUTH-051", "Reset password with unregistered phone/email",
    "P1-High", "S1-Major", "BR-009", "UC-AUTH-004",
    """1. Tap "Forgot Password?"
2. Select "Reset via Mobile OTP"
3. Enter unregistered phone: 9999999999
4. Tap "Send OTP\"""",
    """1. Error: "Phone number not registered" or equivalent
2. User cannot proceed with unregistered phone""",
    """- [ ] App on forgot password screen""",
    """- phone: 9999999999 (not registered)"""))

tcs.append(tc("TC-E2E-AUTH-052", "Reset password → weak password rejected",
    "P1-High", "S1-Major", "BR-009", "UC-AUTH-004",
    """1. Verify OTP/email code successfully
2. On new password screen, enter: "weak"
3. Tap "Reset Password\"""",
    """1. Password requirements shown in red
2. Submit disabled
3. Weak password rejected""",
    """- [ ] Code verified""",
    """- password: weak"""))

tcs.append(tc("TC-E2E-AUTH-053", "Reset password → old sessions invalidated",
    "P1-High", "S1-Major", "BR-009", "UC-AUTH-004",
    """1. User A is logged in on Device 1
2. On Device 2, reset password for User A
3. On Device 1, try to use the app (trigger API call)""",
    """1. Device 1's JWT is invalidated
2. Device 1 gets 401 on next API call
3. Device 1 redirects to login screen""",
    """- [ ] User logged in on Device 1
- [ ] Access to reset on Device 2""",
    """- User A credentials"""))

tcs.append(tc("TC-E2E-AUTH-054", "Rate limited OTP reset attempts",
    "P2-Medium", "S1-Major", "BR-009, NFR-011", "UC-AUTH-004",
    """1. Tap "Forgot Password?" → enter phone
2. Send OTP → wrong OTP → retry → repeat 4 more times (5 total)
3. Try one more time""",
    """1. Maximum 3 verification attempts per OTP enforced
2. After max attempts, "Maximum attempts reached. Request new OTP."
3. Rate limit: 5 attempts per hour per phone""",
    """- [ ] Phone with SIM""",
    """- phone: 9876543212"""))

# ============ 11. Rate Limiting & Security (3 TCs) ============

tcs.append(tc("TC-E2E-AUTH-055", "OTP rate limit enforced (10 attempts/5min per IP)",
    "P1-High", "S1-Major", "NFR-011", "UC-AUTH-001",
    """1. Send OTP for phone: 9876543210
2. Repeat step 1 nine more times within 5 minutes (total 10)
3. Try 11th OTP send""",
    """1. First 10 OTP requests succeed (SMS sent or rate limit token consumed)
2. 11th request: "Too many requests. Please try again later."
3. Rate limit resets after 5 minutes""",
    """- [ ] App can send OTP repeatedly""",
    """- phone: 9876543210"""))

tcs.append(tc("TC-E2E-AUTH-056", "JWT token contains valid claims",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Log in successfully → capture JWT token
2. Decode JWT (base64 decode the payload)
3. Verify claims""",
    """1. JWT has 3 segments (header.payload.signature)
2. Payload contains: sub (user identifier), iat (issued at), exp (expiry)
3. exp = iat + 30 days (2592000 seconds)
4. Signature is valid""",
    """- [ ] User logged in""",
    """- JWT captured from API response"""))

tcs.append(tc("TC-E2E-AUTH-057", "API rejects requests without JWT for protected endpoints",
    "P1-High", "S1-Major", "BR-006", "UC-AUTH-004",
    """1. Call GET /api/v1/orders (authenticated endpoint) WITHOUT Authorization header
2. Call GET /api/v1/cart/merge (authenticated) WITHOUT JWT""",
    """1. 401 Unauthorized returned
2. Error: "Authentication required" or "Full authentication is required"
3. No data returned""",
    """- [ ] API running""",
    """- No JWT token in request"""))

# ============ 12. Edge Cases (3 TCs) ============

tcs.append(tc("TC-E2E-AUTH-058", "Concurrent duplicate signup requests",
    "P2-Medium", "S1-Major", "BR-001", "UC-AUTH-001",
    """1. Prepare signup data for new email
2. Submit two signup requests simultaneously (rapid double-tap)
3. Observe""",
    """1. First request succeeds (user created)
2. Second request fails with duplicate error
3. No duplicate user created in database""",
    """- [ ] Fresh email not in system""",
    """- email: unique-test@bookmyjuice.co.in"""))

tcs.append(tc("TC-E2E-AUTH-059", "Special characters in name/address fields",
    "P2-Medium", "S2-Minor", "BR-007", "UC-AUTH-001",
    """1. During signup, enter name: "John O'Brien-Smith"
2. Address: "123 Main St., Apt #4B"
3. Complete signup
4. View profile""",
    """1. Special characters accepted
2. Name displayed correctly in profile
3. Address fields saved correctly""",
    """- [ ] App in signup flow""",
    """- name: John O'Brien-Smith
- address: 123 Main St., Apt #4B"""))

tcs.append(tc("TC-E2E-AUTH-060", "Very long input fields (boundary testing)",
    "P3-Low", "S3-Trivial", "BR-007", "UC-AUTH-001",
    """1. During signup, enter name with 255 characters
2. Enter address lines with 500 characters each
3. Attempt to proceed""",
    """1. Fields accept reasonable input lengths
2. Database constraints enforced (VARCHAR limits)
3. No crash or data truncation error""",
    """- [ ] App in signup flow""",
    """- Very long text strings"""))


# ============ WRITE FILE ============
content = """# AUTH Module - End-to-End (E2E) Black-Box Test Cases

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
"""

for t in tcs:
    content += t + "\n---\n"

content += "\n## Document Control\n\n- **Created:** 2026-05-19\n- **Version:** 1.0\n- **Total Test Cases:** 60\n- **Status:** ✅ Complete\n"

with open("x:/BMJ/docs/test-cases/TC_E2E_AUTH.md", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Written {len(tcs)} test cases to TC_E2E_AUTH.md")
print(f"Total file size: {len(content)} characters")
