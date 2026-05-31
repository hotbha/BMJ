# BookMyJuice — Unified Authentication Requirements
# Version: 2.0 — Hardened Specification
# Last Updated: June 2026
# Status: AUTHORITATIVE — All auth implementations MUST conform to this document

---

## 1. Executive Summary

Every authentication path in BMJ (Google Sign-In, Phone OTP, Email+Password) MUST:

1. Successfully authenticate the user identity via its respective provider
2. Exchange the provider credential for a **BMJ-issued JWT** from the backend API
3. Store the JWT securely on-device (Flutter Secure Storage)
4. Navigate the user to the **Dashboard** screen
5. Maintain the JWT for all subsequent authenticated API calls

No auth path is considered working unless ALL 5 steps complete successfully.

---

## 2. Architecture: Unified Auth Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CLIENT (Flutter App)                            │
│                                                                     │
│  ┌─────────────┐   ┌───────────────┐   ┌──────────────────────┐    │
│  │ Google      │   │ Phone OTP     │   │ Email + Password      │    │
│  │ Sign-In     │   │               │   │                       │    │
│  └──────┬──────┘   └───────┬───────┘   └──────────┬───────────┘    │
│         │                  │                       │                │
│         ▼                  ▼                       ▼                │
│  Google ID Token     Firebase Phone          Email + Password       │
│  (from Google SDK)   ID Token                (plain credentials)    │
│         │                  │                       │                │
│         └──────────────────┴───────────────────────┘                │
│                            │                                        │
│                            ▼                                        │
│                   POST /api/auth/{provider}                         │
│                   (to BMJ Backend on 192.168.1.x:8080)              │
│                            │                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Node/Spring/Go)                         │
│                                                                     │
│  1. Verify the provider token/credential with Firebase Admin SDK    │
│  2. Upsert user record in database (create if new, update if exist) │
│  3. Generate BMJ JWT (HS256/RS256, 7-day expiry)                    │
│  4. Return { token: "<jwt>", user: { id, email, name, phone } }     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIENT (Flutter App) — POST AUTH                 │
│                                                                     │
│  1. Receive JWT from backend                                        │
│  2. Store JWT in FlutterSecureStorage (key: "bmj_jwt")              │
│  3. Store user profile in memory/local state                        │
│  4. AuthBloc emits: AuthAuthenticated(user)                         │
│  5. Router navigates to: /dashboard                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Known Critical Bug — MUST FIX FIRST

### BUG-001 [CRITICAL]: Google Sign-In fails with SocketException

**Confirmed from logcat (June 2026):**
```
✅ Signed in: pbharat.hotwani@gmail.com       ← Google OAuth works
✅ Display Name: Bharat Hotwani
❌ Google login failed: ClientException with SocketException:
   No route to host (OS Error: No route to host, errno = 113),
   address = 192.168.1.6, port = 60090,
   uri=http://192.168.1.6:8080/api/auth/google
```

**Root Cause:** The backend server at `192.168.1.6:8080` is either:
- Not running (most likely — server process is down)
- Running but on a different IP (machine IP changed after restart)
- Blocked by Windows/Linux firewall on port 8080
- Port 8080 is occupied by another process

**Secondary Bug:** The `AuthenticationBloc` catches the SocketException and emits `SignUpStarted(Instance of 'User')` instead of `AuthError`. This causes the app to navigate to signup instead of showing an error. This is a bug in error handling.

**Fix Sequence:**
1. Start the backend: `cd backend && npm start` (or `./gradlew bootRun` etc.)
2. Verify it's reachable from the phone: `adb shell curl http://192.168.1.6:8080/api/health`
3. If IP changed, update `.env` in Flutter app with new `BASE_URL`
4. Fix the BLoC to emit `AuthError` on SocketException (see Section 6.4)

---

## 4. Auth Path Specifications

### 4.1 Google Sign-In

**Trigger:** User taps "Continue with Google" button on Login screen

**Step-by-step:**

| Step | Actor | Action | Expected Result |
|------|-------|--------|-----------------|
| 1 | Flutter | Call `GoogleSignIn().signIn()` | Google account picker shown |
| 2 | User | Select Google account | Picker closes |
| 3 | Flutter | Get `googleUser.authentication` | Returns `idToken` + `accessToken` |
| 4 | Flutter | Check `idToken != null` | If null → emit `AuthError('Google token empty')` |
| 5 | Flutter | POST `idToken` to `/api/auth/google` | Backend receives request |
| 6 | Backend | Verify token via Firebase Admin SDK | Token validated |
| 7 | Backend | Upsert user in DB | User record created/updated |
| 8 | Backend | Return `{ token: JWT, user: {...} }` | 200 OK response |
| 9 | Flutter | Store JWT in FlutterSecureStorage | Key: `bmj_jwt` |
| 10 | Flutter | Emit `AuthAuthenticated(user)` | BLoC state changed |
| 11 | Flutter | Navigate to `/dashboard` | Dashboard shown |

**API Contract:**
```
POST /api/auth/google
Content-Type: application/json

{ "idToken": "<google-id-token>" }

→ 200 OK
{ 
  "token": "<bmj-jwt>",
  "user": { "id": "uuid", "email": "user@gmail.com", "name": "Bharat Hotwani" },
  "isNewUser": false
}

→ 401 Unauthorized (invalid token)
{ "error": "INVALID_GOOGLE_TOKEN", "message": "Google ID token verification failed" }

→ 503 Service Unavailable (Firebase Admin down)
{ "error": "AUTH_SERVICE_UNAVAILABLE" }
```

**Flutter Error Handling:**
```dart
// In AuthBloc — GoogleSignIn event handler
try {
  final googleUser = await GoogleSignIn().signIn();
  if (googleUser == null) {
    // User cancelled — stay on screen, emit nothing
    return;
  }
  
  final googleAuth = await googleUser.authentication;
  if (googleAuth.idToken == null) {
    emit(AuthError('Google authentication failed: no ID token'));
    return;
  }

  // POST to backend
  final response = await authRepository.googleSignIn(idToken: googleAuth.idToken!);
  
  // Store JWT
  await secureStorage.write(key: 'bmj_jwt', value: response.token);
  
  emit(AuthAuthenticated(response.user));
  
} on SocketException catch (e) {
  // BACKEND IS DOWN — show clear error, do NOT navigate
  emit(AuthError(
    'Cannot connect to server. Please check your internet connection.\n'
    'Technical: ${e.address}:${e.port} unreachable'
  ));
} on ClientException catch (e) {
  emit(AuthError('Network error: ${e.message}'));
} on UnauthorizedException catch (_) {
  emit(AuthError('Google Sign-In rejected by server. Please try again.'));
} catch (e) {
  emit(AuthError('Google Sign-In failed: $e'));
}
```

---

### 4.2 Phone OTP

**Trigger:** User taps "Continue with Phone" button on Login screen

**Step-by-step:**

| Step | Actor | Action | Expected Result |
|------|-------|--------|-----------------|
| 1 | Flutter | Show phone number input screen | Phone input displayed |
| 2 | User | Enter phone number (e.g. +91 9876543210) | Validated: must be E.164 format |
| 3 | Flutter | Call Firebase `verifyPhoneNumber()` | SMS sent by Firebase |
| 4 | User | Receive SMS OTP (6 digits) | OTP received on phone |
| 5 | Flutter | Show OTP input screen | OTP entry UI shown |
| 6 | User | Enter OTP | App captures 6-digit code |
| 7 | Flutter | Call `PhoneAuthProvider.credential(verificationId, smsCode)` | Credential created |
| 8 | Firebase | Return `firebaseIdToken` | Token from Firebase Auth |
| 9 | Flutter | POST `firebaseIdToken` to `/api/auth/phone` | Backend call |
| 10 | Backend | Verify token, upsert user, return JWT | JWT issued |
| 11 | Flutter | Store JWT, emit `AuthAuthenticated`, navigate to dashboard | Done |

**API Contract:**
```
POST /api/auth/phone
Content-Type: application/json

{ "firebaseIdToken": "<firebase-phone-auth-id-token>" }

→ 200 OK
{ 
  "token": "<bmj-jwt>",
  "user": { "id": "uuid", "phone": "+919876543210" },
  "isNewUser": true
}

→ 401 { "error": "INVALID_PHONE_TOKEN" }
→ 429 { "error": "OTP_RATE_LIMITED", "retryAfter": 60 }
```

**OTP Validation Rules:**
- Phone number: must match `^\+[1-9]\d{9,14}$` (E.164)
- India numbers: must start with `+91` followed by 10 digits starting with 6-9
- OTP: exactly 6 digits, numeric only
- OTP expires in 120 seconds (Firebase default)
- Max 3 OTP attempts before lockout (5 minutes)
- Resend OTP available after 30 seconds cooldown

---

### 4.3 Email + Password

**Trigger:** User enters email/password and taps "Sign In" button

**Step-by-step:**

| Step | Actor | Action | Expected Result |
|------|-------|--------|-----------------|
| 1 | Flutter | Validate email format (client-side) | Must match RFC 5322 email regex |
| 2 | Flutter | Validate password (client-side) | Min 8 chars, 1 uppercase, 1 number |
| 3 | Flutter | POST to `/api/auth/login` with email+password | Backend call |
| 4 | Backend | Verify credentials against Firebase or DB | Validated |
| 5 | Backend | Generate and return BMJ JWT | JWT issued |
| 6 | Flutter | Store JWT, emit `AuthAuthenticated`, navigate to dashboard | Done |

**API Contract:**
```
POST /api/auth/login
Content-Type: application/json

{ "email": "user@example.com", "password": "SecurePass@1" }

→ 200 OK
{ "token": "<bmj-jwt>", "user": { "id": "uuid", "email": "..." } }

→ 401 { "error": "INVALID_CREDENTIALS", "message": "Email or password is incorrect" }
→ 404 { "error": "USER_NOT_FOUND" }
→ 429 { "error": "RATE_LIMITED", "retryAfter": 300 }
```

**Client-Side Validation:**
- Empty email → show inline error "Email is required"
- Invalid email format → "Please enter a valid email address"
- Empty password → "Password is required"
- Password < 8 chars → "Password must be at least 8 characters"
- All validation shown inline below respective field, NOT as toast

---

### 4.4 Email Sign-Up (New User Registration)

**Trigger:** User taps "Sign Up" tab → "Sign Up with Email"

**Fields Required:**
- Full name (min 2 chars, max 50)
- Email (unique, RFC 5322 valid)
- Password (min 8 chars, 1 uppercase, 1 digit, 1 special char)
- Confirm password (must match)

**API Contract:**
```
POST /api/auth/register
Content-Type: application/json

{ 
  "name": "Bharat Hotwani",
  "email": "user@example.com",
  "password": "SecurePass@1" 
}

→ 201 Created
{ "token": "<bmj-jwt>", "user": { "id": "uuid", "email": "...", "name": "..." } }

→ 409 { "error": "EMAIL_ALREADY_EXISTS", "message": "An account with this email already exists. Try Sign In." }
→ 422 { "error": "VALIDATION_FAILED", "fields": { "email": "invalid", "password": "too_short" } }
```

---

## 5. JWT Specification

### 5.1 Token Structure
```json
{
  "header": { "alg": "HS256", "typ": "JWT" },
  "payload": {
    "sub": "<user-uuid>",
    "email": "user@example.com",
    "name": "Bharat Hotwani",
    "phone": "+919876543210",
    "authProvider": "google|phone|email",
    "iat": 1780000000,
    "exp": 1780604800
  }
}
```

### 5.2 Token Lifecycle
- **Expiry:** 7 days from issue
- **Storage:** `FlutterSecureStorage`, key: `bmj_jwt`
- **Refresh:** Backend must expose `POST /api/auth/refresh` accepting valid (not expired) JWT → returns new JWT with fresh 7-day expiry
- **Revocation:** `POST /api/auth/logout` — invalidates token server-side (add to blocklist)
- **Auto-login:** On app start, read JWT from secure storage → `GET /api/auth/me` to validate → if valid, emit `AuthAuthenticated`; if expired, emit `AutoLoginFailed`

### 5.3 JWT Usage
All authenticated API calls must include:
```
Authorization: Bearer <bmj-jwt>
```
Backend returns `401 Unauthorized` for missing/invalid/expired JWT.
Flutter Dio interceptor must:
1. Auto-attach JWT to all requests
2. On 401 response → attempt token refresh once
3. If refresh fails → emit `SessionExpired` → navigate to login

---

## 6. Auth State Machine

```
                    ┌─────────────────┐
                    │   AppStart      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  CheckJWT in    │
                    │  SecureStorage  │
                    └────────┬────────┘
                    ┌────────┴────────┐
                    │                 │
              JWT found           No JWT /
              & valid             expired
                    │                 │
                    ▼                 ▼
           ┌──────────────┐  ┌───────────────┐
           │ AutoLogin    │  │ AutoLoginFailed│
           │ Authenticated│  │ → Dashboard   │
           │ → Dashboard  │  │   (guest mode)│
           └──────────────┘  └───────────────┘
                                    │
                            User taps Sign In
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  LoginScreen     │
                          │ (3 auth options) │
                          └─────────┬────────┘
              ┌────────────────┬────┴──────────────────┐
              │                │                       │
              ▼                ▼                       ▼
      ┌─────────────┐  ┌──────────────┐   ┌──────────────────┐
      │ Google      │  │ Phone OTP    │   │ Email+Password   │
      │ Sign-In     │  │              │   │                  │
      └──────┬──────┘  └──────┬───────┘   └────────┬─────────┘
             │                │                    │
             └────────────────┴────────────────────┘
                              │
                        Backend Call
                    POST /api/auth/{provider}
                              │
              ┌───────────────┴────────────────┐
              │                                │
           Success                           Failure
              │                                │
              ▼                                ▼
      ┌─────────────────┐            ┌──────────────────┐
      │ Store JWT       │            │ AuthError state  │
      │ AuthAuthenticated│           │ Show error on    │
      │ → Dashboard     │            │ login screen     │
      └─────────────────┘            │ (NOT navigate)   │
                                     └──────────────────┘
```

**Critical Rule:** ANY auth failure (network, server error, invalid credentials) MUST:
1. Emit `AuthError(message)` state
2. Keep user on the Login screen
3. Display a human-readable error message inline or as snackbar
4. NEVER navigate to Dashboard, SignUp, or any other screen

---

## 7. Error Codes — Complete Reference

| Scenario | BLoC State | UI Behavior |
|----------|-----------|-------------|
| Backend unreachable (SocketException) | `AuthError('Server unreachable')` | Show snackbar with retry button |
| Google token null/empty | `AuthError('Google auth failed')` | Snackbar, stay on login |
| User cancelled Google picker | No state change | Stay on login, no error |
| Invalid credentials | `AuthError('Wrong email or password')` | Inline field error |
| User not found | `AuthError('No account found')` | Suggest signup |
| OTP expired | `AuthError('OTP expired, resend')` | Show resend button |
| OTP wrong | `AuthError('Incorrect OTP')` | Show attempts remaining |
| JWT expired | `SessionExpired` | Navigate to login with message |
| Rate limited | `AuthError('Too many attempts, wait Xs')` | Show countdown |
| Server 500 | `AuthError('Server error, try later')` | Retry button |

---

## 8. Backend Health Check Requirement

The backend MUST expose:
```
GET /api/health
→ 200 OK { "status": "ok", "timestamp": "2026-06-01T00:00:00Z" }
```

The Flutter app MUST check this endpoint on startup:
- If reachable → proceed normally
- If unreachable → show offline banner but still allow dashboard in guest mode
- Cline/tests MUST verify this endpoint is responding before running any auth tests

---

## 9. Environment Configuration

The backend URL is configured in the Flutter app's `.env` file:
```
BASE_URL=http://192.168.1.6:8080
```

**CRITICAL: When the dev machine IP changes (common with WiFi/DHCP), this value becomes stale.**

The correct IP must be discovered each time:
```bash
# On Windows
ipconfig | grep -A1 'Wireless LAN adapter Wi-Fi'

# On Mac/Linux
ifconfig | grep 'inet ' | grep -v 127.0.0.1
```

Then update `BASE_URL` in the Flutter `.env` and rebuild the app.

---

## 10. Test Coverage Matrix

Every auth path must be covered by Appium tests:

| Test ID | Scenario | Path | Expected Outcome |
|---------|----------|------|------------------|
| AUTH-001 | App launch → Dashboard (guest) | N/A | Dashboard shown |
| AUTH-002 | Google Sign-In happy path | Google | JWT stored, Dashboard shown |
| AUTH-003 | Google Sign-In → backend down | Google | Error shown, stays on login |
| AUTH-004 | Google Sign-In → user cancels picker | Google | Stays on login, no error |
| AUTH-005 | Phone OTP happy path | Phone | JWT stored, Dashboard shown |
| AUTH-006 | Phone OTP wrong code | Phone | Error shown, stays on OTP screen |
| AUTH-007 | Phone OTP expired | Phone | Resend option shown |
| AUTH-008 | Email+Password valid credentials | Email | JWT stored, Dashboard shown |
| AUTH-009 | Email+Password wrong password | Email | Error shown, stays on login |
| AUTH-010 | Email+Password nonexistent user | Email | Error shown, stays on login |
| AUTH-011 | Email+Password empty fields | Email | Validation shown, no API call |
| AUTH-012 | Email+Password invalid format | Email | Validation shown |
| AUTH-013 | Sign Up with new email | Email | JWT stored, Dashboard shown |
| AUTH-014 | Sign Up with existing email | Email | Error shown, suggest login |
| AUTH-015 | Logout → guest dashboard | Any | JWT deleted, guest state |
| AUTH-016 | Re-login after logout | Any | JWT stored, Dashboard shown |
| AUTH-017 | Auto-login with valid JWT | N/A | Dashboard shown directly |
| AUTH-018 | Auto-login with expired JWT | N/A | Login screen shown |
