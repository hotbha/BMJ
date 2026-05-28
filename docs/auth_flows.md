# Auth Flows — Code Reality Trace

> **Audit Date:** 2026-05-26  
> **Scope:** All authentication flows from UI through BLoC to backend API, traced from Dart/Flutter source code only.  
> **Methodology:** Read every auth-related `.dart` file exhaustively. No assumptions. No reference to backend Java code.

---

## ⚠️ Cleanup Required

All issues discovered during audit, organized by severity. Each flag links to the relevant flow section for context.

### FLAG-001 (Low) — `google_sign_in.dart:66` — Redundant null check

**File:** `lush/lib/views/models/google_sign_in.dart`  
**Code:**
```dart
final GoogleSignInAccount? account = await _googleSignIn.authenticate();
if (account != null) {  // ← null check always true
```

**Issue:** In `google_sign_in` package 7.x, `GoogleSignIn.authenticate()` returns non-nullable `GoogleSignInAccount`. The null check on line 66 can never be false. The file itself has `// ignore: unnecessary_null_comparison` confirming the team is aware.  
**Impact:** None at runtime — this is a static analysis warning only.  
**Recommendation:** Remove the `if (account != null)` guard and `// ignore` comment. Handle this as `if (account == null)` is dead code.

---

### FLAG-002 (Low) — `user_repository.dart:846` — `photoUrl` type mismatch

**File:** `lush/lib/UserRepository/user_repository.dart` (line ~846)  
**Code:**
```dart
'photoUrl': currentUser.photoUrl,  // photoUrl is Uri?, not String?
```

**Issue:** `GoogleSignInAccount.photoUrl` is a `Uri?` getter, not a `String?` property. It's already non-async (no `Future` involved). Two sub-issues:
1. The `await` keyword before a non-Future getter triggers a Dart `unnecessary_await` warning.
2. The value being assigned into a `Map<String, dynamic>` has type `Uri?` where downstream code likely expects `String?`.

**Impact:** The `Uri?` value is stored in the map. If the backend expects a string URL, serialization may produce `Uri(...)` string representation instead of a plain URL string.  
**Recommendation:** Change to `'photoUrl': currentUser.photoUrl?.toString()`.

---

### FLAG-003 (Medium) — `phone_signup_screen.dart` — Optimistic navigation (signup)

**File:** `lush/lib/views/screens/phone_signup_screen.dart` (lines ~43-58)  
**Code:**
```dart
_onContinue() {
  // dispatches SendOTP event
  context.read<AuthenticationBloc>().add(SendOTP(phone: _phoneController.text));
  // Immediately navigates without waiting for BLoC state
  Navigator.pushNamed(context, '/phone-otp-verification');
}
```

**Issue:** The `SendOTP` event is dispatched, but navigation to `/phone-otp-verification` happens immediately — before the BLoC confirms the OTP was actually sent (`OTPSent` state). If the API call fails, the user lands on the OTP screen with no way to know the send failed (the toast appears but they're already on a different screen).  
**Impact:** User confusion if backend is down — they're on an OTP input screen for an OTP that was never sent.  
**Recommendation:** Use a `BlocListener` to navigate only on `OTPSent` state, and stay on the current screen on error.

---

### FLAG-004 (Medium) — `phone_otp_verification_screen.dart` — Login OTP bypasses BLoC

**File:** `lush/lib/views/screens/phone_otp_verification_screen.dart` (line ~119)  
**Code:**
```dart
// In login flow path:
await _userRepository.loginViaPhoneOtp(phone, otp);
// BLoC is NOT involved — no state emitted for login-via-phone-OTP
```

**Issue:** When OTP is used for **login**, the code calls `userRepository.loginViaPhoneOtp()` directly, bypassing the BLoC entirely. This means:
- No `AuthenticationState` is emitted for this path.
- No loading/error state tracking through BLoC.
- Inconsistent with the signup path which goes through the BLoC (`VerifyOTP` event).
- The method `loginViaPhoneOtp()` saves the JWT token itself on success.

For **signup**, OTP verification goes through `VerifyOTP` → BLoC → `OTPVerificationSuccess` state → handles navigation.

**Impact:** Inconsistent architecture. Login-via-phone-OTP is not represented in the BLoC state machine. Any widget listening for authentication state transitions won't see this event.  
**Recommendation:** Create a dedicated `LoginViaPhoneOtp` event in the BLoC and route through it.

---

### FLAG-005 (Low) — `user_repository.dart` `getToken()` — Double `autoLogin()` call

**File:** `lush/lib/UserRepository/user_repository.dart` (lines ~781-795)  
**Code:**
```dart
Future<String?> getToken() async {
  await autoLogin();  // ← first call (line ~782)
  var token = await secureStorageService.getToken();
  if (token == null) {
    await autoLogin();  // ← second call (line ~789) if first didn't produce token
    token = await secureStorageService.getToken();
  }
  return token;
}
```

**Issue:** `autoLogin()` is called twice — once before the token check, then again if the token is still null. Since `autoLogin()` performs JWT decode (network-free), this is inefficient but not harmful.  
**Impact:** Duplicate work on every token retrieval.  
**Recommendation:** Call `autoLogin()` once, check token, return. Remove the second call.

---

### FLAG-006 (Info) — `FacebookSignUp` — STUB implementation

**File:** `lush/lib/bloc/AuthBloc/auth_bloc.dart` (FacebookSignUp handler, BUG FIX 21)  
**Code:**
```dart
class FacebookSignUp ...
  // handler emits: yield SignUpFailed(message: "Coming Soon")
```

**Issue:** Facebook sign-up is explicitly a stub — no real implementation exists. The event handler immediately yields `SignUpFailed` with a "Coming Soon" message.  
**Impact:** Users attempting Facebook sign-up see an error toast. Feature is explicitly listed as not implemented.  
**Recommendation:** Remove the stub or mark the UI entry point as disabled.

---

### FLAG-007 (Info) — Firebase Phone Auth login — Incomplete UX

**File:** `lush/lib/views/screens/phone_otp_verification_screen.dart` (Firebase + Login path)  
**Code flow:**
1. Firebase OTP verified successfully on device.
2. Navigation: `Navigator.pop(context)` twice → back to login page.
3. User must then sign in with email + password manually.

**Issue:** Firebase phone verification for login does NOT automatically sign the user in. After successful Firebase phone verification, the app returns the user to the login page where they must re-enter email + password. This is a conscious design choice (Firebase phone auth is used for identity verification, not as the login credential), but it's a poor UX — the user just verified their phone but still needs to type credentials.  
**Impact:** Confusing UX. The phone verification feels pointless to the user.  
**Recommendation:** If Firebase phone auth is meant for account recovery or MFA, communicate this clearly in the UI. Otherwise, complete the login flow after verification.

---

### FLAG-008 (Info) — Duplicate OTP verification screens

**Files:**
- `lush/lib/views/screens/phone_otp_verification_screen.dart` (407 lines) — **Active**, shared across login/signup/Google
- `lush/lib/views/screens/otp_sign_up_screen.dart` — **Legacy**, separate OTP screen (not referenced in current navigation)

**Issue:** Two OTP verification screens exist. The legacy `otp_sign_up_screen.dart` is not imported or routed in the current navigation graph. It's dead code.  
**Impact:** Code maintenance burden. Dead code increases cognitive load.  
**Recommendation:** Verify `otp_sign_up_screen.dart` is not referenced anywhere, then delete it.

---

### FLAG-009 (Info) — `google-services.json` / Firebase config dependency

**Context:** H18 in `HUMAN_INTERVENTION_REQUIRED.md` documents that OAuth client IDs were updated (from `434116959668-*` to `24122477606-*`). The current `google-services.json` may have empty `oauth_client` array entries.  
**Impact:** Google Sign-In and Firebase Phone Auth may fail if the Firebase project configuration or `google-services.json` / `GoogleService-Info.plist` is not correctly set up for the development environment.  
**Recommendation:** Verify `google-services.json` contains valid OAuth client entries for debug signing certificate SHA-1.

---

## Cross-Reference Analysis

### PHONE_DEBUG_CHECKPOINTS.md vs FUNCTIONAL_SPEC.md

| Aspect | PHONE_DEBUG_CHECKPOINTS.md | FUNCTIONAL_SPEC.md | Verdict |
|--------|---------------------------|-------------------|---------|
| **Purpose** | Operational/debugging workflow guide (Docker, VS Code, device setup) | Auth feature specification | Different domains — no contradiction |
| **Auto-login** | "Checks ONLY token validity" | "JWT token in SharedPreferences" | ✅ **Aligned** |
| **Auth flows** | Not defined — purely debug setup | Sections 3.1-3.6 define all flows | ✅ **No overlap** |
| **API endpoints** | Not listed | Section 3.2 defines endpoints | ✅ **No overlap** |

**Conclusion:** ✅ **No contradictions, no duplicates, no phantoms.** These documents serve completely different purposes. PHONE_DEBUG_CHECKPOINTS is a developer workflow guide; FUNCTIONAL_SPEC is a feature specification.

### HUMAN_INTERVENTION_REQUIRED.md vs FUNCTIONAL_SPEC.md

| Aspect | HUMAN_INTERVENTION_REQUIRED.md | FUNCTIONAL_SPEC.md | Verdict |
|--------|-------------------------------|-------------------|---------|
| **H18 — Firebase config** | OAuth client IDs changed to `24122477606-*` | No mention of Firebase Phone Auth | ⚠️ **Gap:** Firebase auth exists in code but not in spec |
| **H20 — JWT 30-day expiry** | ✅ Resolved — 30 days | Section 3.2: mentions JWT but no explicit expiry | ✅ **Aligned** |
| **H19 — Dashboard default** | ✅ Completed | Section 1.4: details Dashboard-first flow | ✅ **Aligned** |

**Conclusion:** The only notable finding is that **Firebase Phone Auth** (which exists in `firebase_phone_auth.dart` and is wired into both `phone_login_screen.dart` and `phone_signup_screen.dart`) is **not documented in FUNCTIONAL_SPEC.md**. This is a documentation gap.

---

## FLOW 1: Phone OTP — PARTIAL

### Existence: ✅ **YES** — Two distinct paths

#### Path 1A: Backend OTP (Primary)

**Entry Points:**
- **Login:** `login_page.dart` → "Phone OTP" button → `/phone-login` → `phone_login_screen.dart`
- **Signup:** `login_page.dart` Sign Up tab → Phone card → `/phone-signup` → `phone_signup_screen.dart`

**Step-by-step trace (Login):**

```
phone_login_screen.dart
  │  User enters 10-digit phone, presses "Send OTP via SMS"
  │  Validation: RegExp(r'^[6-9]\d{9}$')
  │  Calls: _userRepository.sendOTP(phone)
  │    → POST /api/auth/send-otp  { phone }
  │    → Returns "OTP_SENT" or "Error:..."
  │  On success: Navigator.pushNamed('/phone-otp-verification', arguments: {isLoginFlow: true})
  │
  ▼
phone_otp_verification_screen.dart
  │  User enters 6-digit OTP, presses "Verify"
  │  Calls: _attemptPhoneLogin(phone, otp)  [⚠️ FLAG-004: bypasses BLoC]
  │    → userRepository.loginViaPhoneOtp(phone, otp)
  │      → POST /api/auth/login-otp  { phone, otp }
  │      → On success: saves JWT via secureStorageService.saveToken(jwt)
  │      → Returns type: 'login_success' or 'signup_required'
  │  login_success: Navigator.pushReplacementNamed('/dashboard')
  │  signup_required: Navigator.pushReplacementNamed('/email-entry-after-phone')
  │
  ▼
Dashboard (login_success) or email_entry_after_phone (signup_required)
```

**Step-by-step trace (Signup):**

```
phone_signup_screen.dart
  │  User enters phone, presses "Continue"
  │  Dispatches: SendOTP(phone: phone)
  │  Navigator.pushNamed('/phone-otp-verification') IMMEDIATELY  [⚠️ FLAG-003]
  │
  ▼  (BLoC processes SendOTP)
auth_bloc.dart (SendOTP handler)
  │  Calls: userRepository.sendOTP(phone)
  │    → POST /api/auth/send-otp  { phone }
  │  On success: yield OTPSent(phone: phone)
  │  On error: yield SendOTPFailed(message: ...)
  │
  ▼
phone_otp_verification_screen.dart
  │  User enters 6-digit OTP, presses "Verify"
  │  Dispatches: VerifyOTP(phone: phone, otp: otp)  [goes through BLoC]
  │
  ▼
auth_bloc.dart (VerifyOTP handler)
  │  Calls: userRepository.verifyOTP(phone, otp)
  │    → POST /api/auth/verify-otp  { phone, otp }
  │    → Returns "OTP_VERIFIED" or "Error:..."
  │  On success: yield PhoneVerified(phone: phone)
  │  yield OTPVerificationSuccess()
  │
  ▼
phone_signup_screen.dart BlocListener
  │  On OTPVerificationSuccess:
  │    → If email already known: Navigator.pushNamed('/address-entry')
  │    → If email needed: Navigator.pushNamed('/email-entry-after-phone')
  │
  ▼
email_entry_after_phone_screen.dart → email_verification_after_phone_screen.dart
  │  → address_entry_screen.dart → create_password_screen.dart
  │  → CompleteSignup event → signUp() → POST /api/auth/unified-signup
```

#### Path 1B: Firebase Phone Auth (Alternative)

**Files involved:**
- `firebase_phone_auth.dart` — Singleton wrapping `FirebaseAuth.instance`
- `phone_login_screen.dart` — "Verify via Firebase" button
- `phone_signup_screen.dart` — "Verify via Firebase" button
- `phone_otp_verification_screen.dart` — Firebase OTP handling

**Step-by-step trace:**

```
phone_login_screen.dart / phone_signup_screen.dart
  │  User presses "Verify via Firebase"
  │  Calls: _firebasePhoneAuth.initiatePhoneVerification(phone)
  │    → _auth.verifyPhoneNumber(phoneNumber: phone, ...)
  │    → Firebase sends SMS, calls onCodeSent with verificationId
  │  Navigator.pushNamed('/phone-otp-verification', arguments: {
  │    isFirebaseAuth: true, verificationId: verificationId, ...
  │  })
  │
  ▼
phone_otp_verification_screen.dart
  │  User enters SMS code, presses "Verify"
  │  Dispatches: VerifyFirebaseOtp(smsCode: code, verificationId: ...)
  │
  ▼
auth_bloc.dart (VerifyFirebaseOtp handler)
  │  Calls: FirebasePhoneAuth.instance.verifyPhoneOtp(smsCode, verificationId)
  │    → PhoneAuthProvider.credential(verificationId:, smsCode:)
  │    → _auth.signInWithCredential(credential)
  │  On success: yield FirebasePhoneOtpVerified()
  │
  ▼
  │  LOGIN path: Navigator.pop(context) twice → back to login page  [⚠️ FLAG-007]
  │  SIGNUP path: → Navigator.pushNamed('/address-entry')
```

### Working End-to-End Assessment

| Sub-flow | Status | Evidence |
|----------|--------|----------|
| Backend OTP → Login | ✅ **Working** | `sendOTP()` → `loginViaPhoneOtp()` → saves JWT → dashboard. No BLoC involvement but functional. |
| Backend OTP → Signup | ✅ **Working** | `SendOTP` → BLoC → `VerifyOTP` → BLoC → `OTPVerificationSuccess` → address entry → password → `CompleteSignup`. Full BLoC flow. |
| Firebase OTP → Login | ⚠️ **Incomplete UX** | Verified but returns to login page. User must re-enter credentials. |
| Firebase OTP → Signup | ✅ **Working** | Verified → address entry → unified signup. |

---

## FLOW 2: Google Sign-In — PARTIAL

### Existence: ✅ **YES** — Two paths (Login and Signup)

#### Path 2A: Google Sign-In for Login

**Files involved:**
- `google_sign_in.dart` — `GoogleSignInHelper` singleton (uses `serverClientId`)
- `user_repository.dart` — `googleSignIn()`, `_loginWithGoogle()`, `linkGoogleAccount()`
- `auth_bloc.dart` — `GoogleSignIn` event handler
- `login_page.dart` — Google login button
- `link_google_account_screen.dart` — Handle `link_required` case

**Step-by-step trace:**

```
login_page.dart
  │  User presses Google button on Sign In tab
  │  Dispatches: GoogleSignIn()
  │
  ▼
auth_bloc.dart (GoogleSignIn handler)
  │  Calls: userRepository.googleSignIn()
  │
  ▼
user_repository.dart:804 (googleSignIn())
  │  Calls: GoogleSignInHelper.instance.signIn()
  │
  ▼
google_sign_in.dart:signIn()
  │  Calls: _googleSignIn.authenticate()
  │    → Shows Google account picker
  │    → Returns GoogleSignInAccount?  (actually non-nullable in 7.x)  [⚠️ FLAG-001]
  │  if (account != null) {  // always true
  │    return userRepository._loginWithGoogle(account)
  │  }
  │  return {'type': null, ...}  // dead branch
  │
  ▼
user_repository.dart:867 (_loginWithGoogle())
  │  final idToken = await currentUser.authenticationToken();  // serverAuthCode with serverClientId
  │  POST /api/auth/google  { googleId, email, displayName, photoUrl, idToken }
  │  Returns Map with 'type': 'login_success' | 'link_required' | 'signup_required'
  │  ⚠️ photoUrl: currentUser.photoUrl (Uri?) → stored as Uri, not String  [⚠️ FLAG-002]
  │
  ▼
auth_bloc.dart (handles 3 return types)
  │
  ├── 'login_success': saves JWT → yield AuthenticationSuccess() → dashboard
  │
  ├── 'link_required': yield GoogleLinkRequired(googleSignInData)
  │     → link_google_account_screen.dart
  │       │  User enters phone → OTP verification
  │       │  Calls: userRepository.linkGoogleAccount(phone, otp, googleData)
  │       │    POST /api/auth/link-google-account
  │       │  On success: saves JWT → dashboard
  │
  └── 'signup_required': yield SignUpStarted()
       → User navigated to signup flow (email/phone selection)
```

#### Path 2B: Google Sign-In for Sign Up

**Files involved:**
- `login_page.dart` — Google card on Sign Up tab
- `google_phone_entry_screen.dart` — Name + phone entry
- `phone_otp_verification_screen.dart` — OTP verification (Google+Signup path)
- `auth_bloc.dart` — `GoogleSignUpEnterPhone` event

**Step-by-step trace:**

```
login_page.dart (Sign Up tab)
  │  User presses Google card
  │  Calls: _handleGoogleSignUp()
  │    → GoogleSignInHelper.instance.signIn() (direct call, not through BLoC)
  │    → Gets GoogleSignInAccount
  │    → Navigator.pushNamed('/google-signup', arguments: GoogleSignInAccount)
  │
  ▼
google_phone_entry_screen.dart
  │  Email pre-filled (read-only), user enters first name, last name, phone
  │  Dispatches: GoogleSignUpEnterPhone(
  │    googleSignInAccount: ...,
  │    firstName: ..., lastName: ..., phone: ...
  │  )
  │
  ▼
auth_bloc.dart (GoogleSignUpEnterPhone handler)
  │  Stores signup data in _signupData map
  │  If phone is sufficient, dispatches EnterAddress internally
  │  OR yields GoogleSignupEmailVerified → navigates to /phone-otp-verification
  │
  ▼
phone_otp_verification_screen.dart (isGoogleSignup: true)
  │  OTP verified → navigates to /address-entry
  │  → /create-password → dispatches CompleteSignup
  │
  ▼
auth_bloc.dart (CompleteSignup handler)
  │  Calls: userRepository.signUpWithGoogle(data)  [⚠️ uses googleSignInData fields]
  │    POST /api/auth/unified-signup  { ...google specific fields... }
  │  Resets signup state (BUG FIX 5)
  │  Clears password (BUG FIX 17)
  │  Saves JWT → yield AuthenticationSuccess() → dashboard
```

### Working End-to-End Assessment

| Sub-flow | Status | Evidence |
|----------|--------|----------|
| Google Login (existing user) | ✅ **Working** | `googleSignIn()` → `_loginWithGoogle()` → `login_success` → JWT saved → dashboard |
| Google Login (link required) | ✅ **Working** | `link_required` → `link_google_account_screen.dart` → phone+OTP → `linkGoogleAccount()` → dashboard |
| Google Login (new user) | ✅ **Working** | `signup_required` → user sent to signup flow |
| Google Sign Up | ✅ **Working** | Direct GoogleSignIn → `google_phone_entry_screen.dart` → OTP → address → password → `signUpWithGoogle()` → dashboard |
| Known bugs | ⚠️ **Flagged** | FLAG-001 (null check), FLAG-002 (photoUrl type), FLAG-004 (BLoC bypass not applicable here) |

---

## FLOW 3: Email/Password — YES

### Existence: ✅ **YES**

#### Login via Email/Password

**Entry Point:** `login_page.dart` → Sign In tab → Email + Password fields

**Step-by-step trace:**

```
login_page.dart
  │  User enters email and password, presses "Sign In"
  │  Dispatches: LogIn(email: email, password: password)
  │
  ▼
auth_bloc.dart (LogIn handler)
  │  Calls: userRepository.login(email, password)
  │
  ▼
user_repository.dart:300 (login())
  │  POST /api/auth/signin  { email, password }
  │  On success: saves JWT via secureStorageService.saveToken(jwt)
  │  Returns user data
  │
  ▼
auth_bloc.dart
  │  On success: yield AuthenticationSuccess() → dashboard
  │  On error: yield LogInFailed(message: ...) → login page shows toast
```

#### Signup via Email-First (Unified Flow)

```
login_page.dart (Sign Up tab)
  │  User presses Email card
  │  Dispatches: ChooseSignupMethod('email')
  │
  ▼
auth_bloc.dart → yields SignupMethodSelected('email')
  │  login_page.dart BlocListener navigates to /email-signup
  │
  ▼
email_verification_screen.dart
  │  User enters email, presses "Send Code"
  │  Dispatches: EnterEmail(email: email)
  │    → auth_bloc → userRepository.sendEmailVerification(email)
  │      → POST /api/auth/send-email-verification
  │  User enters 6-digit code, presses "Verify"
  │  Dispatches: VerifyEmail(email: email, code: code)
  │    → auth_bloc → userRepository.verifyEmailCode(email, code)
  │      → POST /api/auth/verify-email-code
  │    → On success: yields EmailVerified(email: email)
  │
  ▼
phone_entry_after_email_screen.dart
  │  User enters phone → navigates to /address-entry
  │
  ▼
address_entry_screen.dart → create_password_screen.dart
  │  → dispatches CompleteSignup
  │
  ▼
auth_bloc.dart: CompleteSignup → userRepository.signUp(data)
  │  POST /api/auth/unified-signup  { email, phone, password, address, ... }
  │  saves JWT → yield AuthenticationSuccess() → dashboard
```

#### Password Reset

**Entry Point:** `login_page.dart` → "Forgot Password?" → `forgot_password_screen.dart`

Two methods available:

**Method A: Phone OTP Reset**
```
forgot_password_screen.dart
  │  User selects "Reset via Mobile"
  │  Calls: userRepository.sendOTP(phone)
  │  Navigator.pushNamed('/reset-password-mobile-otp')
  │
  ▼
reset_password_mobile_screen.dart (STEP 1: OTP)
  │  User enters OTP
  │  Calls: userRepository.verifyOTP(phone, otp)
  │
  ▼
reset_password_mobile_screen.dart (STEP 2: New Password)
  │  User enters new password (FlutterPwValidator: min 8 chars, upper+lower+2 digits+1 special)
  │  Calls: userRepository.resetPasswordViaMobile(phone, otp, newPassword)
  │    POST /api/auth/reset-password-mobile
  │  On success: Navigator.pop to login page
```

**Method B: Email OTP Reset**
```
forgot_password_screen.dart
  │  User selects "Reset via Email"
  │  Calls: userRepository.sendEmailVerification(email)
  │  Navigator.pushNamed('/reset-password-email-code')
  │
  ▼
reset_password_email_screen.dart
  │  User enters verification code + new password
  │  Calls: userRepository.resetPasswordViaEmail(email, code, newPassword)
  │    POST /api/auth/reset-password-email
  │  On success: Navigator.pop to login page
```

### Working End-to-End Assessment

| Sub-flow | Status | Evidence |
|----------|--------|----------|
| Email/Password Login | ✅ **Working** | `login()` → `POST /api/auth/signin` → JWT → dashboard. Full BLoC flow. |
| Email-First Signup | ✅ **Working** | Unified flow: email verification → phone → address → password → `signUp()` → dashboard. Full BLoC flow. |
| Password Reset (Email) | ✅ **Working** | `sendEmailVerification()` → `resetPasswordViaEmail()`. Two backend endpoints wired. |
| Password Reset (Phone) | ✅ **Working** | `sendOTP()` → `verifyOTP()` → `resetPasswordViaMobile()`. Three backend endpoints wired. |

---

## FLOW 4: Auto-login with Token — YES (with caveat)

### Existence: ✅ **YES**

**File:** `auth_bloc.dart` — `AutoLogIn` event handler

### Step-by-step trace

```
App startup
  │  AuthenticationBloc initialized
  │  Dispatches: AutoLogIn()
  │
  ▼
auth_bloc.dart (AutoLogIn handler)
  │  Checks internet connectivity
  │  If no internet: yield AutoLoginFailed("No internet connection") → public mode
  │  If has internet:
  │    Calls: userRepository.autoLogin()
  │
  ▼
user_repository.dart:244 (autoLogin())
  │  Reads JWT from SecureStorage (secureStorageService.getToken())
  │  If no token: return null
  │  If token exists:
  │    Decodes JWT payload locally (base64 decode — no signature verification)
  │    Checks 'exp' claim:
  │      → If expired (> 30 days from issue): returns null
  │      → If valid: saves decoded user info to SharedPreferences
  │    Calls: getUserDetailsFromServer()
  │      → GET /api/test/user  (with JWT in Authorization header)
  │      → On success: updates user info
  │      → On failure: still proceeds with locally decoded data
  │    Returns user data
  │
  ▼
auth_bloc.dart
  │  autoLogin() returned data:
  │    → yield AuthenticationSuccess(user: ...) → full dashboard
  │  autoLogin() returned null:
  │    → yield AutoLoginFailed("Session expired") → public dashboard with toast
  │
  ▼
Dashboard
  │  Full authenticated experience if success
  │  Public mode with catalog preview if failed
```

### BR-006 Compliance

The functional spec defines: **"No credential storage or silent re-authentication."**

The code confirms compliance:
- JWT is stored in SecureStorage, not plain SharedPreferences.
- On expiry, the token is simply discarded — no refresh token is used.
- `autoLogin()` validates locally (exp check only) — no network call to validate the token.
- If the token is invalid/expired on the server but valid locally, the app will show authenticated state until `getUserDetailsFromServer()` fails.

### `getToken()` double-call concern [⚠️ FLAG-005]

```dart
Future<String?> getToken() async {
  await autoLogin();          // first call
  var token = await secureStorageService.getToken();
  if (token == null) {
    await autoLogin();        // second call if token still null
    token = await secureStorageService.getToken();
  }
  return token;
}
```

The double `autoLogin()` call (lines 782 and 789) is inefficient. If `autoLogin()` fails to produce a token the first time, it's unlikely to succeed on the second attempt since there's no network refresh logic between calls.

### Working End-to-End Assessment

| Sub-flow | Status | Evidence |
|----------|--------|----------|
| Valid JWT → Auto-login | ✅ **Working** | Local decode → `getUserDetailsFromServer()` → `AuthenticationSuccess` → dashboard |
| Expired JWT → Fallback | ✅ **Working** | `exp` check fails → `AutoLoginFailed` → public mode |
| No JWT → Public mode | ✅ **Working** | `autoLogin()` returns null → `AutoLoginFailed` → public mode |
| No internet → Fallback | ✅ **Working** | Internet check in BLoC → `AutoLoginFailed("No internet connection")` |
| Token refresh | ✅ **N/A by design** | BR-006: no silent re-authentication. Token valid for 30 days, user must re-login. |
| `getToken()` efficiency | ⚠️ **FLAG-005** | Double `autoLogin()` call is redundant. |

---

## Summary: Working End-to-End

| Flow | Status | Flags | Notes |
|------|--------|-------|-------|
| **FLOW 1: Phone OTP** | ✅ **PARTIAL** | FLAG-003, FLAG-004, FLAG-007, FLAG-008 | Backend OTP path works. Firebase path has UX gap for login. |
| **FLOW 2: Google Sign-In** | ✅ **PARTIAL** | FLAG-001, FLAG-002 | All 3 login return types handled. Signup works through unified flow. Two low-severity bugs. |
| **FLOW 3: Email/Password** | ✅ **YES** | None | Login, signup (email-first), and password reset all wired through BLoC. |
| **FLOW 4: Auto-login** | ✅ **YES** | FLAG-005 | Local JWT decode works. Double `autoLogin()` inefficiency. BR-006 compliant. |

### Legend

| Status | Meaning |
|--------|---------|
| ✅ **YES** | Flow is fully implemented and appears functional end-to-end through the code |
| ✅ **PARTIAL** | Flow exists and is partially functional, but has known bugs or incomplete paths |
| ❌ **NO** | Flow does not exist in code (not applicable here) |

---

## Appendix: Key Singletons and Dependencies

| Service | File | Type | Purpose |
|---------|------|------|---------|
| `UserRepository` | `lush/lib/UserRepository/user_repository.dart` (1519 lines) | `ChangeNotifier` | All backend auth API calls, JWT management |
| `AuthenticationBloc` | `lush/lib/bloc/AuthBloc/auth_bloc.dart` (508 lines) | `Bloc` | Auth state machine |
| `GoogleSignInHelper` | `lush/lib/views/models/google_sign_in.dart` (96 lines) | Singleton | Google Sign-In wrapper |
| `FirebasePhoneAuth` | `lush/lib/views/models/firebase_phone_auth.dart` (167 lines) | Singleton | Firebase Phone Auth wrapper |
| `SecureStorageService` | `lush/lib/UserRepository/user_repository.dart` (inline) | Instance | JWT token persistence |

### API Endpoints Used

| Endpoint | Method | File Reference | Flows |
|----------|--------|----------------|-------|
| `/api/auth/signin` | POST | `user_repository.dart:300` | Email/Password Login |
| `/api/auth/send-otp` | POST | `user_repository.dart:547` | Phone OTP, Password Reset |
| `/api/auth/verify-otp` | POST | `user_repository.dart:582` | Phone OTP Verification |
| `/api/auth/unified-signup` | POST | `user_repository.dart:330,449` | All Signup paths |
| `/api/auth/google` | POST | `user_repository.dart:867` | Google Sign-In Login |
| `/api/auth/login-otp` | POST | `user_repository.dart:929` | Phone OTP Login |
| `/api/auth/link-google-account` | POST | `user_repository.dart:976` | Google Link Account |
| `/api/auth/send-email-verification` | POST | `user_repository.dart:619` | Email-First Signup, Password Reset |
| `/api/auth/verify-email-code` | POST | `user_repository.dart:640` | Email-First Signup |
| `/api/auth/reset-password-mobile` | POST | `user_repository.dart:664` | Password Reset (Phone) |
| `/api/auth/reset-password-email` | POST | `user_repository.dart:693` | Password Reset (Email) |
| `/api/test/user` | GET | `user_repository.dart:1164` | Auto-Login User Details |
| `/api/auth/account` | DELETE | `user_repository.dart:1127` | Account Deletion |
| Firebase Auth (client-side) | SDK | `firebase_phone_auth.dart` | Firebase Phone Verification |

---

*Generated by code audit — all claims traceable to specific lines in `lush/lib/` and `lush/lib/UserRepository/`. No backend Java code was consulted.*
