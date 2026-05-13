# AUTH Module — Detailed Test Cases

> **Document Version:** 1.1
> **Last Updated:** 2026-05-12 (Added Firebase Phone Auth test cases TC-AUTH-019 to TC-AUTH-027 and FCM test cases TC-AUTH-028 to TC-AUTH-029)

---

## TC-AUTH-001: Successful user signup with valid email

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-001 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock UserRepo, PasswordEncoder, RoleRepo |
| **Steps** | POST /api/auth/signup with valid email, password, name |
| **Expected** | 500 (Chargebee not mocked) — signup flow starts correctly |
| **Auto** | ✅ Automated |
| **Coverage** | AuthController.java:signup |

## TC-AUTH-002: Signup with duplicate email fails

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-002 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock userRepo.existsByEmail=true |
| **Steps** | POST /api/auth/signup with existing email |
| **Expected** | 400 BAD_REQUEST |
| **Auto** | ✅ Automated |
| **Coverage** | AuthController.java:signup |

## TC-AUTH-003: Successful login

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-003 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock AuthManager, JwtUtils |
| **Steps** | POST /api/auth/signin with valid credentials |
| **Expected** | 200 + JWT token |
| **Auto** | ✅ Automated |
| **Coverage** | AuthController.java:signin |

## TC-AUTH-004: Login with invalid credentials

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-004 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock AuthManager throws BadCredentials |
| **Steps** | POST /api/auth/signin with wrong password |
| **Expected** | BadCredentialsException thrown |
| **Auto** | ✅ Automated |
| **Coverage** | AuthController.java:signin |

## TC-AUTH-005: Login with non-existent user

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-005 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock AuthManager throws BadCredentials |
| **Steps** | POST /api/auth/signin with unknown email |
| **Expected** | BadCredentialsException thrown |
| **Auto** | ✅ Automated |
| **Coverage** | AuthController.java:signin |

## TC-AUTH-006: JWT generation with valid user

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-006 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock Authentication |
| **Steps** | JwtUtils.generateJwtToken |
| **Expected** | Token with 3 dot-separated segments |
| **Auto** | ✅ Automated |
| **Coverage** | JwtUtils.java |

## TC-AUTH-007: JWT validation with valid token

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-007 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock Authentication |
| **Steps** | generate then validateJwtToken |
| **Expected** | true |
| **Auto** | ✅ Automated |
| **Coverage** | JwtUtils.java |

## TC-AUTH-008: JWT validation with empty token

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-008 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | — |
| **Steps** | validateJwtToken("") |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | JwtUtils.java |

## TC-AUTH-009: JWT validation with null token

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-009 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | — |
| **Steps** | validateJwtToken(null) |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | JwtUtils.java |

## TC-AUTH-010: JWT parsing extracts username

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-010 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock Authentication |
| **Steps** | generate then getUserNameFromJwtToken |
| **Expected** | "testuser" |
| **Auto** | ✅ Automated |
| **Coverage** | JwtUtils.java |

## TC-AUTH-011: Email verification code generation (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-011 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | EmailVerificationService instance |
| **Steps** | generateVerificationCode("test@example.com") |
| **Expected** | Returns 6-digit string, stored in codeStore |
| **Auto** | ✅ Automated |
| **Coverage** | EmailVerificationService.java |

## TC-AUTH-012: Email verification code — valid code passes (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-012 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Generate verification code first |
| **Steps** | verifyCode(email, generatedCode) |
| **Expected** | true, code marked as used |
| **Auto** | ✅ Automated |
| **Coverage** | EmailVerificationService.java |

## TC-AUTH-013: Email verification code — wrong code fails (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-013 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Generate verification code first |
| **Steps** | verifyCode(email, "wrongcode") |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | EmailVerificationService.java |

## TC-AUTH-014: Email verification code — reusing used code fails (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-014 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Generate code, verify once |
| **Steps** | verifyCode(email, sameCode) again |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | EmailVerificationService.java |

## TC-AUTH-015: OTP generation (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-015 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | OTPUtil instance |
| **Steps** | generateOTP("9876543210") |
| **Expected** | Returns 6-digit string |
| **Auto** | ✅ Automated |
| **Coverage** | OTPUtil.java |

## TC-AUTH-016: OTP verification — valid OTP passes (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-016 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Generate OTP first |
| **Steps** | verifyOTP(phone, generatedOTP) |
| **Expected** | true, OTP marked as used |
| **Auto** | ✅ Automated |
| **Coverage** | OTPUtil.java |

## TC-AUTH-017: OTP verification — wrong OTP fails (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-017 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Generate OTP first |
| **Steps** | verifyOTP(phone, "wrongotp") |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | OTPUtil.java |

## TC-AUTH-018: OTP verification — unknown phone fails (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-018 |
| **Module** | AUTH |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | — |
| **Steps** | verifyOTP("unknown@phone", "123456") |
| **Expected** | false |
| **Auto** | ✅ Automated |
| **Coverage** | OTPUtil.java |

---

## Firebase Phone Auth Test Cases

### TC-AUTH-019: Firebase Phone Auth — Initiate phone verification

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-019 |
| **Module** | AUTH (Firebase) |
| **Type** | Integration |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Firebase project configured, device with SIM card, `FirebasePhoneAuth.instance` initialized |
| **Steps** | Call `initiatePhoneVerification(phone: "+919876543210", onCodeSent, onError, onTimeout)` |
| **Expected** | SMS sent to phone; `onCodeSent` callback invoked with a non-null `verificationId` |
| **Auto** | ❌ Manual |
| **Coverage** | `FirebasePhoneAuth.initiatePhoneVerification()` |

### TC-AUTH-020: Firebase Phone Auth — Verify valid SMS code

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-020 |
| **Module** | AUTH (Firebase) |
| **Type** | Integration |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | TC-AUTH-019 completed successfully; user received SMS code |
| **Steps** | Call `verifyPhoneOtp(smsCode)` with the 6-digit code from SMS |
| **Expected** | Returns `true`; `isVerified` property becomes `true` |
| **Auto** | ❌ Manual |
| **Coverage** | `FirebasePhoneAuth.verifyPhoneOtp()` |

### TC-AUTH-021: Firebase Phone Auth — Verify invalid SMS code

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-021 |
| **Module** | AUTH (Firebase) |
| **Type** | Integration |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | TC-AUTH-019 completed successfully |
| **Steps** | Call `verifyPhoneOtp("000000")` with an incorrect code |
| **Expected** | Returns `false`; error toast displayed to user |
| **Auto** | ❌ Manual |
| **Coverage** | `FirebasePhoneAuth.verifyPhoneOtp()` |

### TC-AUTH-022: Firebase Phone Auth — Verify before initiation fails

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-022 |
| **Module** | AUTH (Firebase) |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | `FirebasePhoneAuth` instance with no prior verification |
| **Steps** | Call `verifyPhoneOtp("123456")` without calling `initiatePhoneVerification` first |
| **Expected** | Returns `false`; debug logs show "No verification ID" |
| **Auto** | ✅ Automated |
| **Coverage** | `FirebasePhoneAuth.verifyPhoneOtp()` |

### TC-AUTH-023: Firebase Phone Auth — Reset state

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-023 |
| **Module** | AUTH (Firebase) |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | `FirebasePhoneAuth` instance after successful verification |
| **Steps** | Call `reset()` |
| **Expected** | `verificationId` cleared; `isVerified` = false; `isVerifying` = false; `verifiedPhone` = null |
| **Auto** | ✅ Automated |
| **Coverage** | `FirebasePhoneAuth.reset()` |

### TC-AUTH-024: Firebase Phone Auth — Sign out

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-024 |
| **Module** | AUTH (Firebase) |
| **Type** | Integration |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | User signed in via Firebase Phone Auth |
| **Steps** | Call `signOut()` |
| **Expected** | Internal state cleared; `currentFirebaseUser` returns null |
| **Auto** | ❌ Manual |
| **Coverage** | `FirebasePhoneAuth.signOut()` |

### TC-AUTH-025: Firebase Phone Auth — "Verify via Firebase" button renders on phone_login_screen

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-025 |
| **Module** | AUTH (UI) |
| **Type** | Widget |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Widget test with `PhoneLoginScreen` |
| **Steps** | Render `PhoneLoginScreen`; find button with text "Verify via Firebase" |
| **Expected** | OutlinedButton.icon exists with "Verify via Firebase" label and blue styling |
| **Auto** | ✅ Automated |
| **Coverage** | `phone_login_screen.dart` |

### TC-AUTH-026: Firebase Phone Auth — "Verify via Firebase" button renders on phone_signup_screen

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-026 |
| **Module** | AUTH (UI) |
| **Type** | Widget |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Widget test with `PhoneSignupScreen` |
| **Steps** | Render `PhoneSignupScreen`; find button with text "Verify via Firebase" |
| **Expected** | OutlinedButton.icon exists with "Verify via Firebase" label and blue styling |
| **Auto** | ✅ Automated |
| **Coverage** | `phone_signup_screen.dart` |

### TC-AUTH-027: Firebase Phone Auth — OTP screen receives isFirebaseAuth flag

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-027 |
| **Module** | AUTH (UI) |
| **Type** | Widget |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Widget test with `PhoneOtpVerificationScreen` with `isFirebaseAuth: true` in args |
| **Steps** | Navigate to screen with map: `{'phone': '9876543210', 'isFirebaseAuth': true, 'verificationId': 'abc123'}` |
| **Expected** | Screen renders without error; `_isFirebaseAuth` internal flag set to true; `_verificationId` set to 'abc123' |
| **Auto** | ✅ Automated |
| **Coverage** | `phone_otp_verification_screen.dart` |

---

## FCM Notification Test Cases

### TC-AUTH-028: FCM — Notification service initializes

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-028 |
| **Module** | NOTIFICATIONS |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | `FirebaseNotificationService.instance` initialized |
| **Steps** | Call `initialize()` |
| **Expected** | Returns without error; FCM token available via `token` property |
| **Auto** | ❌ Manual (requires real device) |
| **Coverage** | `FirebaseNotificationService.initialize()` |

### TC-AUTH-029: FCM — Foreground notification displayed as local notification

| Field | Value |
|-------|-------|
| **ID** | TC-AUTH-029 |
| **Module** | NOTIFICATIONS |
| **Type** | Integration |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | App running in foreground; notification permission granted |
| **Steps** | Send FCM push with `{ notification: { title: "Test", body: "Test body" } }` via Firebase Console |
| **Expected** | Local notification appears in system tray via `LocalNotificationService` |
| **Auto** | ❌ Manual (requires real device + Firebase Console) |
| **Coverage** | `FirebaseNotificationService._onMessageHandler()` |

---

## Total: 29 test cases (18 original + 11 new Firebase/FCM)
