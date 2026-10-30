# Authentication Simplification Plan

**Project:** BookMyJuice (BMJ) — Flutter app `lush/`, Spring server `bmjServer/`
**Date:** 2026-10-17
**Status:** Draft for sign-off — **one server approval (§3) gates step A3**
**Approved product decision:** the only supported authentication methods are **Google Sign-In** and **Phone OTP**. No password creation, no password login, no email signup, no email verification, no forgot/reset password, no email OTP. *No exceptions.*
**Supersedes:** `BMJ_UX_REHAUL_PLAN.md` §1 **D3** (which kept password sign-in for existing credential holders) and every auth row of that plan's P1/P2 tables. §8 below carries the re-baseline.
**Does not touch:** backend architecture, Chargebee architecture, pricing logic, business rules, or the ten V1 flows in `docs/BMJ_V1_SCOPE.md` §2 — with the single, explicitly-requested exception described in §3.

---

## 0. Verdict in six lines

1. **22 auth screen files exist. 20 auth routes are live. 15 of the 22 files are dead weight or duplicates** and can be deleted (§4).
2. The app already has clean seams: `/auth/login-otp` returns a `signup_required` discriminator (`user_repository.dart:900-902`), and OTP send/verify are real endpoints.
3. **But there is no way to create a new account without email + password.** `/auth/unified-signup` and `/auth/signup` both mark `email` and `password` `@NotBlank` server-side, and `/auth/login-otp` explicitly does **not** create users (`AuthController.java:473-480`).
4. Therefore "remove password *and* email, no exceptions" requires **two additive server endpoints** (§3, Option A). That is not an architecture change and it changes no existing contract — but it is backend work, so it needs your one-line approval.
5. The UI work splits cleanly: **A0–A2 (2.25 d) can start today**, A3 (1.0 d) is gated on §3, A4 (1.25 d) is the deletion sweep.
6. With the approved model, Stitch alignment on shipped screens lands at **85.8 % across 19 designs** (was 86.1 % across 22) — §8 has the arithmetic.

---

## 1. The approved authentication model

### 1.1 Four journeys, and only four

```
NEW USER · Google
  /login → [Continue with Google] → Google account chooser (SDK)
        → /auth/google … link_required
        → /google-signup (name · phone · address; Google email read-only, verified)
        → /auth/google-signup → JWT
        → /dashboard            (Chargebee customer created server-side)

NEW USER · Phone
  /login → [Continue with Phone] → /phone-entry (10-digit + fixed +91)
        → /auth/send-otp → /phone-otp-verification (6 boxes)
        → /auth/verify-otp → /auth/login-otp … user_not_found + signupToken
        → /address-entry (name + 9 address fields)
        → /auth/phone-signup → JWT
        → /dashboard            (Chargebee customer created server-side)

EXISTING USER · Google
  /login → [Continue with Google] → /auth/google → JWT → /dashboard

EXISTING USER · Phone
  /login → [Continue with Phone] → /phone-entry → OTP → /auth/login-otp → JWT → /dashboard
```

**"Chargebee Mapping" is not a screen.** Today it is the `Customer.create()` call plus the `user_addresses` insert inside the signup handler (`AuthController.java:721-769`). It happens server-side, immediately after address submit, and it stays there. No UI is added for it, and no Chargebee configuration changes.

### 1.2 What is guaranteed after this work

| Guarantee | Check |
| :--- | :--- |
| No screen collects a password | `Select-String -Pattern "obscureText"` over `lib/` returns only non-auth uses |
| No screen collects an email for identity | Only `GoogleSignupScreen` *displays* the Google-verified address, read-only |
| No route named `*password*`, `*email*`, `*otp-login*` remains | `main.dart` route table (§5) |
| `/otp` survives but renders the **real** OTP screen, not the stub | `main.dart:280` after repoint |
| Existing users keep a way in | Google (same email) or phone OTP (same number) — **pre-flight count in §9, gate A4-G1** |
| Deep links do not 404 | 13 redirect stubs (§5.2) |

### 1.3 Explicitly out of scope (refused even though it would be easier)

- No email OTP / magic link (design #15, #28 — no backend support).
- No "set a password later" upsell (that is password creation).
- No client-side minting of credentials (§3 Option B is documented and **not recommended**).
- No change to `/auth/signin` **on the server**. It stays for API compatibility; it simply becomes unreachable from the app.

## 2. Ground truth — what the code does today

| # | Finding | Evidence |
| :--- | :--- | :--- |
| F1 | 22 auth screen files, 6,576 lines; 20 live auth routes | `main.dart:275-316`; §4 inventory |
| F2 | Every auth screen **class** is instantiated in exactly one place — its `main.dart` route line — except the two state-rendered screens (`SignUpScreen`, `LinkGoogleAccountScreen`). The only other coupling is string route pushes, listed per row in §4 | `auth_map.py` §D: all rows are `main.dart:<n>` or "NO EXTERNAL REFERENCE"; `main.dart:431-444` for the two state-rendered screens |
| F3 | Phone OTP already distinguishes existing from new users | `loginViaPhoneOtp` returns `{'type':'signup_required'}` (`user_repository.dart:900-902`); server returns `status: user_not_found` (`AuthController.java:473-480`) |
| F4 | **New account creation requires email + password** | `UnifiedSignupRequest.java:12-23` (`@NotBlank @Email email`, `@NotBlank @Size(min=8) password`); `EmailSignupRequest.java:12-19`; handler at `AuthController.java:688-691` |
| F5 | OTP verify does **not** create an account | `AuthController.java:415-486` — returns `user_not_found`, never `new User(...)` |
| F6 | Google sign-in does **not** create an account either | `AuthController.java:222-230` returns `link_required`; the only two `new User(` sites are lines 688 and 801 (both signup handlers) |
| F7 | `users.email` and `users.password` are `@NotBlank`; email is unique | `User.java:22-43` — a phone-only row cannot be inserted without *some* valid, unique email and *some* password hash |
| F8 | The OTP is **cleared** before the client can use it for signup | `AuthController.java:475` `otpUtil.clearOTP(...)` on the `user_not_found` branch. A post-address signup call therefore cannot re-verify the same OTP |
| F9 | Address is the terminal step, then a password screen, then signup | `address_entry_screen.dart:97-113` → `/create-password`; `create_password_screen.dart` → `CompleteSignup` → `userRepository.signUp()` (`auth_bloc.dart:386-450`) |
| F10 | **Two OTP implementations exist.** The Firebase one posts a literal string as the OTP and is dead | `phone_otp_verification_screen.dart:212` sends `otp: 'firebase_verified'` to `/auth/login-otp`, which calls `otpUtil.verifyOTP` → always fails. `isFirebaseAuth` flags at `:40/:54/:114/:166/:252`; `firebase_phone_auth.dart` (166 lines) |
| F11 | **Google is split-brained.** Sign-In tab: correct backend call, but a *new* user lands on the legacy email+password `SignUpScreen`. Sign-Up tab: skips `/auth/google` entirely | `login_page.dart:649-657` fires `GoogleSignIn`; `auth_bloc.dart:495` emits `SignUpStarted`; `main.dart:431-433` renders `SignUpScreen`. Separately `login_page.dart:626-634` pushes `/google-signup` for returning users too, who then hit *"Email is already registered"* |
| F12 | `/otp` is a stub that signs up without verifying anything | `main.dart:280` → `otp_login_page.dart:48` `add(SignUp())` |
| F13 | `/mobileNumberPage` pushes `/otpSignUpScreen`, a route that is commented out | `enter_mobile_number.dart:33`; `main.dart:281` |
| F14 | `LinkGoogleAccountScreen` **is** reachable | `auth_bloc.dart:470-475` emits `GoogleLinkRequired`; `main.dart:436-444` renders the screen. (The UX plan's "not routed" note was true but its "no caller" implication was wrong.) |
| F15 | Only two test files reference any auth screen | `test/widgets/signup_screen_test.dart` (SignUpScreen ×2), `test/widget/screens/login_page_test.dart` (LoginPage ×8) |
| F16 | The frozen scope already says V1 is Google + OTP and email signup is de-advertised — but the screens were only *hidden*, never removed | `docs/BMJ_V1_SCOPE.md:28-29,57` |

---

## 3. Blocker A-1 — new-account creation without email + password

This is the only part of the decision that cannot be satisfied in the Flutter client alone. It needs a decision before A3 starts.

### 3.1 Why it is a blocker (not an inconvenience)

To create an account the server must insert a `users` row. That row requires a non-blank, unique, `@Email`-valid `email` and a `@NotBlank` `password` (`User.java:36-43`). Both signup endpoints demand them from the client (`F4`). Neither OTP verify nor Google sign-in creates users (`F5`, `F6`). So:

> **"Phone → OTP → Address → Dashboard" for a first-time user has no server endpoint to land on.** It cannot be built by deleting screens.

### 3.2 The three options

| | Option A — **additive endpoints** *(recommended)* | Option B — **hidden credentials in the client** | Option C — **defer phone signup** |
| :--- | :--- | :--- | :--- |
| Server change | 2 new endpoints + 1 extra response field. Existing contracts untouched. | **None** | None |
| How a phone user is created | `POST /auth/phone-signup` verifies a short-lived `signupToken`, mints an unrecoverable BCrypt secret, inserts the row, returns a JWT | Client derives a random password and `{phone}@phone.bookmyjuice.in`, posts the **existing** `/auth/unified-signup` | Not created |
| Email in the DB | System mailbox (§3.3), or `NULL` in the clean variant | System mailbox, invented by the client | n/a |
| Chargebee | `Customer.create()` **without** `.email(...)` — phone + name + billing address only | Server passes the fake email to Chargebee (`AuthController.java:724`) → **invoices/receipts undeliverable** | n/a |
| Satisfies "no password in UI" | Yes | Yes | Yes |
| Satisfies "no password anywhere" | **Yes in the user sense** — the secret is random, unrecoverable, never shown and never accepted from a client; the column still stores a hash (see §3.4) | **No** — a password is still created and sent | n/a |
| New users can use phone | Yes | Yes | **No** — Google only, which contradicts the brief |
| Effort | **1.5 d server + 1.0 d client** | 0.5 d client | 0.25 d copy/guard |
| Risk | Needs your approval to touch `bmjServer` | Silent billing-data corruption | Ships an incomplete flow |
| Verdict | **Approve this** | Documented for completeness; **not recommended, and not implementable without an explicit instruction** | Fallback if the backend freeze is absolute |

### 3.3 Option A — exact server surface (additive, no contract broken)

1. **`POST /api/auth/login-otp`** — on the `user_not_found` branch (line 476), add `"signupToken": "<JWT 10 min, claim purpose=phone_signup, claim phone>"` to the existing body. Existing clients ignore unknown fields; nothing else changes. This is required because `otpUtil.clearOTP` at line 475 invalidates the OTP before the address form is filled (`F8`).
2. **`POST /api/auth/phone-signup`** — body `{signupToken, firstName, lastName, address, extendedAddr, extendedAddr2, city, state, zip, country}`. It:
   - verifies the token signature, expiry, purpose and phone;
   - is **idempotent** — if a user already exists for that phone, return `409 {status:"login_required"}` so the app sends the user back to `/phone-entry`;
   - inserts `username = phone`, `phone = phone`, `password = encoder.encode(random 32 bytes)` (never returned, never logged), `email = {phone}@phone.bookmyjuice.in`;
   - `Customer.create().phone(...).firstName(...).lastName(...).billingAddress*` — **no `.email(...)`**;
   - reuses the existing `user_addresses` default-address block (`AuthController.java:750-769`);
   - returns the **same `JwtResponse` shape as `/login-otp`**, so the client never calls `/auth/signin` again.
3. **`POST /api/auth/google-signup`** — body = today's `UnifiedSignupRequest` **minus `password`**, plus the Google ID token. Server verifies the token, uses the *real* Google email, mints the same unrecoverable secret, creates the Chargebee customer **with** the real email, returns `JwtResponse`.

> Why two new endpoints instead of relaxing `password` in `UnifiedSignupRequest`: making a `@NotBlank` field optional *is* a contract change to a live endpoint. Adding endpoints is not.

### 3.4 The one honest caveat

Even under Option A, a phone-first account stores a **system mailbox** (`{phone}@phone.bookmyjuice.in`) because the entity forbids a blank email (`F7`). Consequences and their mitigations:

- It is **never** shown: `ProfileTab` / `UserProfileScreen` mask any address ending in `@phone.bookmyjuice.in` → render "Add email later" (display rule only, no backend change).
- It is **never** sent to Chargebee (step 2 above), so no invoice is mailed into a void.
- It is **not deliverable** by design — the subdomain has no MX. If you prefer a proper data model, the clean variant is *nullable `users.email`* (schema migration + `@Email`/`@NotBlank` relaxation + profile DTO change, ≈2.5 d server, higher regression risk). **Recommendation: system mailbox now, nullable email in a later ADR.**
- **The password column has the same shape of compromise.** `users.password` is `@NotBlank`, so `phone-signup` writes a random 32-byte BCrypt secret. It is *not* a user password: never chosen, never shown, never accepted from a client, unrecoverable by design. But if "no password creation" is read literally at the schema level, only the nullable-column variant satisfies it. This is the honest boundary of what a UI-only change can promise.

---

## 4. Screen inventory and classification

**KEEP 5 · MERGE 2 → 1 new screen · DELETE 15.** Every auth screen appears exactly once. "Caller" lists the only places the screen is instantiated.

### 4.1 Entry point

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `login_page.dart` (831) | `/login` | `main.dart:316`; `delete_account_screen:44`; `orders_tab:61`; `profile_tab:97`; `sign_up_screen:344`; `signup_method_selection:151`; `reset_password_email:119`; `reset_password_mobile:120` | **KEEP** (rewrite) | Two CTAs only: Continue with Google, Continue with Phone, plus Terms. Delete the email form (`:296-338`, `:589-600`), Forgot Password (`:312-331`) and the tab scaffold. Target ~330 lines. Four callers survive (main, delete-account, orders, profile) and need no change. |

### 4.2 Phone cluster

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `phone_otp_verification_screen.dart` (441) | `/phone-otp-verification` (registered twice, `main.dart:306-307`) | `phone_signup:67,131`; `phone_login:56,91`; `phone_entry_after_email:57`; `google_phone_entry:68` | **KEEP** (canonical OTP) | Backend OTP only. On `signup_required` → `/address-entry`; on `login_success` → `/dashboard`. Remove `_isFirebaseAuth` (`:40,54,114-118,166,252`) and the four duplicate branches at `:184,232,270,318`. |
| `phone_signup_screen.dart` (279) | `/phone-signup` | `login_page:474`; `signup_method_selection:96` | **MERGE → `PhoneEntryScreen`** | Enter 10-digit number → `SendOTP` → `/phone-otp-verification`. |
| `phone_login_screen.dart` (250) | `/phone-login` | `login_page:391` | **MERGE → `PhoneEntryScreen`** | Same screen; the `isFirebaseAuth: true` argument (`:97`) disappears with the Firebase branch. |
| `enter_mobile_number.dart` (128) | `/mobileNumberPage` | none — route only; pushes `/otpSignUpScreen`, never registered (`main.dart:281`) | **DELETE** | `/phone-entry`. |
| `otp_login_page.dart` (53) | `/otp` | none; fires `SignUp()` with no OTP (`F12`) | **DELETE** | Route repointed to `PhoneOtpVerificationScreen` (UX plan #10). |
| `google_phone_entry_screen.dart` (249) | `/google-phone-entry` | none — route only | **DELETE** | `/google-signup` already collects the phone (`google_signup_screen.dart:139`). |
| `views/models/firebase_phone_auth.dart` (166) | — | `phone_login:24,97`; `phone_signup:27,73`; `auth_bloc:545-566,585-599` | **DELETE** (duplicate OTP) | Backend `/auth/send-otp` + `/auth/verify-otp` only. |

### 4.3 Google cluster

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `google_signup_screen.dart` (588) | `/google-signup` | `login_page:630`; `signup_method_selection:133`; `main.dart:312` | **KEEP** (de-password) | Google email shown read-only; collects name + phone + 9 address fields; `CompleteGoogleSignup` → `/auth/google-signup` → JWT. Remove `_passwordController` / `_confirmPasswordController` (`:151-152`) and the 58 password references. |
| `link_google_account_screen.dart` (309) | not routed — rendered by state | `main.dart:436-444` on `GoogleLinkRequired` (`auth_bloc:470-475`) | **KEEP** (function only) | Keep the OTP-based link (prevents duplicate accounts for people with two emails). Remove **"Use Password Instead"**. Stitch design #9 stays REMOVE; the screen is token-restyled only. |

### 4.4 Signup completion

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `address_entry_screen.dart` (419) | `/address-entry` | `phone_otp:221,296,307`; `email_verification_after_phone:115` | **KEEP** (terminal step) | Submit → `phoneSignup()` (A-1) or `CompleteGoogleSignup()`; on JWT → `/dashboard`. Delete the `/create-password` push (`:97-113`); keep all 9 fields (UX plan D5 still holds). |
| `create_password_screen.dart` (291) | `/create-password` | `address_entry:97` | **DELETE** | Account is created at address submit; no password step exists. |

### 4.5 Email chain — all deleted

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `signup_method_selection_screen.dart` (272) | `/signup-method-selection` | none — route only (`main.dart:299-300`) | **DELETE** | `/login`, which already offers exactly the two approved methods. |
| `email_signup_screen.dart` (179) | `/email-signup` | `signup_method_selection_screen.dart:82` | **DELETE** | `/login` → Google or `/phone-entry`. |
| `email_verification_screen.dart` (252) | `/email-verification` | `email_signup_screen.dart:48` | **DELETE** | No email verification exists; nothing replaces it because nothing needs it. |
| `phone_entry_after_email_screen.dart` (179) | `/phone-entry-after-email` | `email_verification_screen.dart:130` | **DELETE** | `/phone-entry`. |
| `email_entry_after_phone_screen.dart` (173) | `/email-entry-after-phone` | `phone_otp_verification_screen.dart:184,232,270,318` | **DELETE** | After OTP, a new user goes **straight** to `/address-entry`. |
| `email_verification_after_phone_screen.dart` (241) | `/email-verification-after-phone` | `email_entry_after_phone_screen.dart:56` | **DELETE** | Same — no email step in the chain. |
| `sign_up_screen.dart` (452) | not routed | rendered by `main.dart:431-433` on `SignUpStarted` (`auth_bloc:495,505,615`) | **DELETE** | New Google user → `/google-signup`; new phone user → `/phone-entry`. Fix the BLoC emission so it cannot land here (§7.3). |

### 4.6 Password reset — all deleted

| File (lines) | Route | Caller today | Class | Replacement flow |
| :--- | :--- | :--- | :--- | :--- |
| `forgot_password_screen.dart` (319) | `/forgot-password` | `login_page.dart:320` | **DELETE** | Copy on `/login`: *"No password to reset — sign in with Google or a phone OTP."* |
| `reset_password_mobile_screen.dart` (311) | `/reset-password-mobile-otp` | `forgot_password_screen.dart:47` | **DELETE** | — |
| `reset_password_email_screen.dart` (308) | `/reset-password-email-code` | `forgot_password_screen.dart:73` | **DELETE** | — |
| `forgot_password_page.dart` (52) | `/forgotPasswordPage` | none (body commented out) | **DELETE** | — |

### 4.7 Totals

| Category | Screens | Files | Lines |
| :--- | ---: | ---: | ---: |
| KEEP (rewritten) | 5 | 5 | 2,588 |
| MERGE → `phone_entry_screen.dart` | 2 | 2 retired, 1 created (~300) | 529 retired / ~300 added |
| DELETE | 15 | 15 | 3,459 |
| DELETE (duplicate OTP model, not a screen) | — | 1 | 166 |
| **Net** | **22** | **16 removed, 1 added** | **≈ −4,550** |

KEEP set: `login_page`, `phone_otp_verification_screen`, `google_signup_screen`, `link_google_account_screen`, `address_entry_screen`.
Rewrite cost inside KEEP: login 831→~330, google 588→~450, address 419→~430, link 309→~280, OTP 441→~400. All five are already in the UX plan's P1/P2 scope, so this redirects that effort rather than adding styling work.

---

## 5. Route disposition (`main.dart:275-316`)

### 5.1 Kept or repointed (real screens)

| Route | Binds to | Change |
| :--- | :--- | :--- |
| `/login` | `LoginPage` | kept; rewritten to two CTAs |
| `/phone-entry` | **`PhoneEntryScreen`** | **new** — merges `/phone-login` + `/phone-signup` |
| `/phone-otp-verification` | `PhoneOtpVerificationScreen` | kept; duplicate registration at `:306-307` collapsed to one |
| `/google-signup` | `GoogleSignupScreen` | kept; password fields removed |
| `/address-entry` | `AddressEntryScreen` | kept; becomes the terminal step |
| `/phone-login` | `PhoneEntryScreen` | repointed (old deep links keep working) |
| `/phone-signup` | `PhoneEntryScreen` | repointed |
| `/otp` | `PhoneOtpVerificationScreen` | repointed — closes the `SignUp()`-without-verification trap (`F12`) |

### 5.2 Retired routes — 13 redirect stubs to `/login`

`/mobileNumberPage` · `/google-phone-entry` · `/create-password` · `/email-signup` · `/email-verification` · `/phone-entry-after-email` · `/email-entry-after-phone` · `/email-verification-after-phone` · `/signup-method-selection` · `/forgot-password` · `/forgotPasswordPage` · `/reset-password-mobile-otp` · `/reset-password-email-code`

Stub shape (no screen import):

```dart
'/forgot-password': (_) => const LoginPage(),   // retired 2026-10-17 — AUTH_SIMPLIFICATION_PLAN.md
```

**Why stubs at all:** links live in cached PWAs, sent emails and old builds. `RouteExistenceFilter.java` already guards server routes; the client needs the same courtesy so a stale link lands on the two-method hub instead of a white screen.

---

## 6. Replacement flows, step by step

### 6.1 New user · Phone (the only changed journey)

| Step | Screen | Call | Success | Failure |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `/login` | tap **Continue with Phone** | `/phone-entry` | — |
| 2 | `/phone-entry` | local 10-digit validation (`^[6-9]\d{9}$`, same as server) | `SendOTP(phone)` | inline error, no network call |
| 3 | `/phone-entry` | `POST /auth/send-otp` | push `/phone-otp-verification` | 429 → "Try again in 5 minutes" |
| 4 | `/phone-otp-verification` | 6 boxes filled | `POST /auth/verify-otp` | wrong code → shake + clear |
| 5 | `/phone-otp-verification` | `POST /auth/login-otp` | **token** → `/dashboard` | `user_not_found` → step 6 |
| 6 | `/address-entry` | name + 9 fields (D5) | `POST /auth/phone-signup` (A-1) | 409 → back to `/phone-entry` |
| 7 | `/address-entry` | JWT stored, `getUserDetailsFromServer()` | `/dashboard` | — |

### 6.2 New user · Google

`/login` → **Continue with Google** → SDK chooser → `GoogleSignIn` event → `POST /auth/google`:

- **user found** → JWT → `/dashboard`.
- **`link_required`** → `/google-signup` prefilled (email read-only, name, phone, address) → `POST /auth/google-signup` → JWT → `/dashboard`.
- **email belongs to an account with a different Google ID** → `GoogleLinkRequired` → `LinkGoogleAccountScreen` (phone OTP proves ownership) → link → `/dashboard`.

### 6.3 Existing user · Phone

Steps 1–5 of §6.1; `login_success` ends at `/dashboard`. **No address prompt** — `loginViaPhoneOtp` already loads the profile (`user_repository.dart:911`).

### 6.4 Cross-method collision (unchanged behaviour, now explicit)

| Situation | Behaviour |
| :--- | :--- |
| Google email matches an existing phone-only account | `link_required` → `LinkGoogleAccountScreen` → OTP → linked. Still no password. |
| Phone matches an account created by Google | `/auth/login-otp` finds by `username` then by `phone` (`AuthController.java:425-429`) → signs in. |
| Phone already registered when signing up | `409 login_required` → `/phone-entry`, user signs in instead of creating a duplicate. |

---

## 7. Non-screen cleanup (this is where a "delete the screens" job usually breaks)

### 7.1 `UserRepository/user_repository.dart` — remove 8 methods, add 2

| Method | Lines (approx.) | Fate |
| :--- | :--- | :--- |
| `signIn` / `login(email, password)` → `/auth/signin` | 254-287 | **DELETE** (no caller survives) |
| `signUp()` → `/auth/unified-signup` | 411-510 | **DELETE** — replaced by `phoneSignup()` / `googleSignup()` |
| `signUpWithGoogle()` → `/auth/unified-signup` | 288-400 | **DELETE** — replaced by `googleSignup()` |
| `sendEmailVerification`, `verifyEmailCode` | 580-620 | **DELETE** |
| `resetPasswordMobile`, `resetPasswordEmail` | 630-680 | **DELETE** |
| `checkEmailExists` | 105-132 | **DELETE** after a `Select-String` confirms no other caller |
| `sendOTP`, `verifyOTP` | 515-570 | **KEEP** |
| `loginViaPhoneOtp` | 876-922 | **KEEP** — the discriminator is already correct |
| `loginWithGoogle`, `linkGoogleAccount` | 806-870, 924-960 | **KEEP** |
| **NEW** `phoneSignup({signupToken, ...address})` → `/auth/phone-signup` | — | returns `{type:'login_success'\|'login_required'\|'error'}` |
| **NEW** `googleSignup({idToken, ...profile})` → `/auth/google-signup` | — | returns the same shape |

### 7.2 BLoC surface (`bloc/AuthBloc/`)

| Item | Fate |
| :--- | :--- |
| `LogIn(username, password, remember)` | **DELETE** (the only password-carrying event) |
| `EnterEmail`, `VerifyEmail`, `ChooseSignupMethod`, `EnterPhone`, `MobileSignUp`, `SignUp`, `FacebookSignUp` | **DELETE** (no remaining caller) |
| `CompleteSignup(password, confirmPassword, referralCode)` | **REPLACE** with `CompletePhoneSignup(address fields, referralCode)` — no password arguments |
| `GoogleSignUpEnterPhone(... password, confirmPassword ...)` | **REPLACE** with `CompleteGoogleSignup(... no password ...)` and keep `referralCode` |
| `FirebasePhoneSignIn`, `FirebasePhoneOtpSent`, `VerifyFirebaseOtp`, `FirebasePhoneAuthError`, `FirebasePhoneAuthInProgress` | **DELETE** — duplicate OTP (`F10`) |
| `SendOTP`, `VerifyOTP`, `ResendOTP`, `PhoneOtpLogin`, `AutoLogIn`, `LogOut`, `GoogleSignIn`, `EnterAddress` | **KEEP** |
| `SignUpStarted` | **REPLACE** with `GoogleSignupRequired(googleUser)`; `main.dart` renders `GoogleSignupScreen` instead of `SignUpScreen` (`F11`) |
| `GoogleLinkRequired` | **KEEP** |
| `AuthenticationSuccess`, `SignUpFailed`, `SignUpSuccessful`, `AuthenticationInProgress`, `AutoLoginFailed`, `InternetIssue` | **KEEP** |

> **Constraint note:** the UX plan said "do not touch BLoCs". That constraint was written for *styling* work. Auth simplification cannot be done without touching `auth_bloc.dart`, `auth_events.dart`, `auth_state.dart` and `user_repository.dart` — those are exactly the files that encode "password signup". No *other* BLoC (`CartBloc`, `SubscriptionBloc`, `ProductCatalogBloc`, `OrderBloc`, `UserBloc`, `ReferralBloc`, `NotificationBloc`) is touched.

### 7.3 `main.dart` auth gate (`:405-475`)

| Today | After |
| :--- | :--- |
| `SignUpStarted` → `SignUpScreen` (`:431-433`) | `GoogleSignupRequired` → `GoogleSignupScreen` |
| `GoogleLinkRequired` → `LinkGoogleAccountScreen` (`:436-444`) | unchanged |
| 20 auth routes | 8 real (7 retained/repointed + 1 new) + 13 stubs (§5) |

### 7.4 Tests

| File | Action |
| :--- | :--- |
| `test/widgets/signup_screen_test.dart` | **DELETE** with the screen (`F15`) |
| `test/widget/screens/login_page_test.dart` | **REWRITE** — 21 tests today; keep the "no email signup card" assertion and add "no password field", "two methods only" |
| **NEW** `test/widget/screens/auth_no_password_test.dart` | Asserts no `TextField`/`TextFormField` with `obscureText: true` on `/login`, `/phone-entry`, `/google-signup`, `/address-entry`; asserts no route in `main.dart` matches `password\|reset\|email-signup` |
| `integration_test/fullstack_auth_and_pricing_test.dart` | **UPDATE** the auth section to Google + phone OTP only |
| `integration_test/full_e2e_test.dart` | T1.12/T1.13 already assert "email signup not advertised" — extend to "email signup **absent**" |

### 7.5 Docs to amend in the same commit

- `docs/BMJ_V1_SCOPE.md` §3 row 4: "screens remain in the tree" → "screens removed 2026-10-17; `/auth/signin` and `/auth/unified-signup` retained server-side only".
- `BMJ_UX_REHAUL_PLAN.md`: dated **amendment block added at the top** (D3 revoked, #2/#3/#23 retired, #25 reclassified, #9 caller corrected, 7→16 retirement files). The tables themselves keep their original classification for audit; the rewrite lands with the A4 commit.
- `docs/API.md`: document `/auth/phone-signup` and `/auth/google-signup` (only after §3 approval).

---

## 8. Impact on `BMJ_UX_REHAUL_PLAN.md`

### 8.1 Decisions and rows that change

| UX-plan item | Before | After | Why |
| :--- | :--- | :--- | :--- |
| **D3** — "password sign-in stays" | Resolved | **REVOKED** | Product decision 2026-10-17: no password login, no exceptions |
| #2 `create_password` | MERGE canonical, 0.75 d | **REMOVE** | Screen deleted (`create_password_screen.dart`) |
| #3 `create_password_step_3` | MERGE → #2 | **REMOVE** | Same screen |
| #23 `verify_email_otp_step_1.1` | KEEP, 0.75 d | **REMOVE** | No email step in the chain |
| #25 `verify_phone_step_2` | KEEP, 1.0 d, target 85 | **MERGE → #11**, 0.0 d, target 90 | Phone sign-up and phone login become one screen; the design's "three steps in one screen" (Name+Email / Phone / Password) no longer exists |
| #9 `link_google_account` | REMOVE, "not routed, no caller" | REMOVE, **caller corrected** | It *is* reachable: `auth_bloc:470-475` → `main.dart:436-444`. Design stays out; screen stays, token-restyled |
| §7 P2 inventory | 7 files / 1,578 lines | **16 files / 3,625 lines** | §4.5–4.6 + `firebase_phone_auth.dart` |
| §9 wave W2 | 7.0 d, 8 screens | **5.5 d, 4 screens + A3** | Password, email-verify and phone-sign-up-entry restyles disappear |

**New classification counts: 9 KEEP · 10 MERGE (into 4 canonical screens) · 11 REMOVE.**
Canonical merge targets: #7 Google · #11 PhoneEntry · #17 OTP · #18 Scheduler.

### 8.2 Target-score arithmetic (recomputed, 19 retained designs)

| Retained | 1 | 5 | 7 | 8 | 10 | 11 | 12 | 13 | 16 | 17 | 18 | 19 | 20 | 21 | 24 | 25 | 26 | 27 | 29 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Now | 35 | 53 | 44 | 20 | 54 | 52 | 51 | 51 | 43 | 57 | 56 | 58 | 51 | 61 | 56 | 46 | 50 | 48 | 46 |
| Target | 82 | 88 | 85 | 88 | 90 | 90 | 85 | 80 | 90 | 90 | 85 | 82 | 88 | 90 | 90 | 90 | 72 | 85 | 80 |

- **Retained 19:** baseline **932 / 19 = 49.1 %** → after **1,630 / 19 = 85.8 %**.
- **All 30:** baseline **1,491 / 30 = 49.7 %** → after **2,189 / 30 = 73.0 %** (the 11 retired designs keep their current scores: **559**).
- **At or above 75 %:** **18 of 19** retained (**18 of 30** overall). The only one below is #26 at 72, capped by the one-juice rule.

> The headline is unchanged in substance: **≥85 % is met on the screens that ship (85.8 %)**, not across designs no customer can reach (73.0 %). Deleting the password and email screens removed three 90-target designs from the retained set and lowered the average by 0.3 points.

### 8.3 Effort, recomputed with every row counted once

The UX plan's 25.75 d total **excludes its own 0.75 d retirement budget**: the W4 row describes "delete 7 retired files behind redirects", but its 2.75 d is exactly home (2.0) + notifications (0.75). Counted once, the original is **26.5 d**. Corrected and re-baselined:

| Stream | Before | After | Δ |
| :--- | ---: | ---: | ---: |
| P0 (tab fix 0.5 · plan catalogue 2.0 · foundation 4.5 · PDP 3.0) | 10.0 | 10.0 | 0 |
| P1 design restyles (13 rows → 10 rows) | 15.0 | **12.5** | −2.5 |
| P2 (retirement 0.75 → 1.25 for 16 files; notifications 0.75) | 1.5 | **2.0** | +0.5 |
| Auth A0–A3 (new) | — | **3.25** | +3.25 |
| **Client subtotal** | **26.5** | **27.75** | **+1.25** |
| Server A-1 (optional, §3) | — | 1.5 | +1.5 |
| **Total** | **26.5** | **27.75 / 29.25** | **+1.25 / +2.75** |

Auth detail: A0 guardrails 0.5 · A1 phone+OTP consolidation 1.0 · A2 LoginPage rebuild 0.75 · A3 signup completion 1.0 · A4 deletions 1.25 (inside P2).

---

## 9. Sequencing

Auth goes first because it is a *structural* change, not a repaint — but A2 uses the `BMJGlass*` components, so it follows W0.

| Wave | Scope | Days | Cumulative | Gate before starting |
| :--- | :--- | ---: | ---: | :--- |
| **W-0 — Auth structure** | A0 guardrails + A1 merge phone entry, retire Firebase OTP, repoint `/otp` | 1.5 | 1.5 | none — **starts now** |
| **W0 — Foundation** | Tokens, 5 components, 4 supporting widgets, tab fix (P0-1), plan catalogue (P0-2) | 7.0 | 8.5 | W-0 merged (route table stable) |
| **WA — Login rebuild** | A2: two CTAs with `BMJGlassButton`, Terms, no-password copy | 0.75 | 9.25 | W0 tokens merged |
| **W1 — Purchase funnel** | PDP (P0-4), cart, address selection | 5.0 | 14.25 | W0 |
| **W2 — Onboarding** | Address entry #1, Google #7, phone entry #11, OTP #17, **A3** | 5.5 | 19.75 | **A-1 approved** for A3 |
| **W3 — Subscription & retention** | Scheduler #18, portal #19, referral #12 | 4.0 | 23.75 | W0 entry points |
| **W4 — Home, notifications, deletion** | Home #21, notifications #27, **A4** sweep | 4.0 | **27.75** | A3 shipped; A4-G1 passed |

### 9.1 Pre-flight gates

| Gate | When | Command / check | Pass condition |
| :--- | :--- | :--- | :--- |
| **A4-G1** — no stranded customers | before A4 deletes anything | `SELECT COUNT(*) FROM users WHERE google_id IS NULL AND (phone IS NULL OR phone = '') AND deleted = false;` | **0**, or a named outreach list. These are the only people who lose every way in. |
| **A4-G2** — no live caller | before each delete | `Select-String -Path (Get-ChildItem lib,test -Recurse -Filter *.dart).FullName -Pattern "\bClassName\b"` | only the `main.dart` route line + redirect stub |
| **A4-G3** — deep links | after stubs, before delete | `flutter run`, open each of the 13 retired routes | lands on `/login`; no white screen |
| **A1-G1** — single OTP | end of W-0 | `Select-String -Path (Get-ChildItem lib -Recurse -Filter *.dart).FullName -Pattern "isFirebaseAuth\|FirebasePhoneAuth"` | 0 hits |
| **A3-G1** — new phone signup | end of W2 | cleared install → phone → OTP → address → dashboard | JWT stored, `chargebeeCustomerId` non-null, `user_addresses` row created |
| **A2-G1** — no password field | end of WA | `flutter test test/widget/screens/auth_no_password_test.dart` | green |

### 9.2 Contingency

- **A-1 rejected (backend frozen)** → execute **Option C**: A1/A2/A4 still ship, but `/address-entry` is unreachable for phone users; the phone CTA gets *"New here? Create your account with Google — phone sign-up is coming."* W2 drops A3 and #1 (−2.5 d), total **25.25**. The brief's "Phone → OTP → Address" criterion is then **not met** and must be re-signed.
- **A-1 approved** → the full flow ships; server work runs in parallel with W0 (different repo, no merge conflict).

---

## 10. Acceptance criteria

### 10.1 Machine checks (run from `x:\BMJ\lush`)

```powershell
# 1. No password UI anywhere in lib/
Select-String -Path (Get-ChildItem lib -Recurse -Filter *.dart).FullName `
  -Pattern "obscureText|confirmPassword|Forgot Password|Use Password Instead"
# PASS: 0 hits (comments excluded by review)

# 2. No retired route in the route table
Select-String -Path lib\main.dart `
  -Pattern "'/forgot|'/reset-password|'/email-|'/create-password|'/signup-method|'/mobileNumberPage|'/google-phone-entry|'/phone-entry-after-email"
# PASS: 0 hits

# 3. Only backend OTP remains
Select-String -Path (Get-ChildItem lib -Recurse -Filter *.dart).FullName `
  -Pattern "isFirebaseAuth|FirebasePhoneAuth|firebase_verified"
# PASS: 0 hits

# 4. Build hygiene
flutter analyze                      # PASS: 0 errors
flutter test                         # PASS: all green, incl. auth_no_password_test.dart
```

### 10.2 Journey checks (physical device, cleared install)

| # | Journey | Pass |
| :---: | :--- | :--- |
| 1 | Phone → OTP → Address → Dashboard | account created, JWT present, address saved, subscription purchasable |
| 2 | Phone → OTP → Dashboard (existing) | no address prompt; profile loads |
| 3 | Google → account chooser → Dashboard (existing) | no profile-completion screen |
| 4 | Google → new account → complete profile → Dashboard | creates account, no password field visible |
| 5 | Google email collides with phone account | link screen appears; OTP links; no password fallback offered |
| 6 | Open `/forgot-password` from a stale link | lands on `/login`; no crash |
| 7 | Profile shows a system mailbox | masked as "Add email later", never `@phone.bookmyjuice.in` |

### 10.3 Non-regression (untouched surfaces)

`flutter test` on cart, subscription, order, catalog and referral suites must be green. `POST /api/v2/checkout/with-items` and the subscription endpoints are not modified. Server suite `bmjServer\mvnw.cmd -o test` green **before** and **after** A-1.

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Existing email+password-only customers cannot sign in | **Medium** | **High** | A4-G1 count before deletion; if >0, run a "switch to Google or phone" campaign and keep the API endpoint alive |
| A-1 not approved → phone signup impossible | Medium | High | Option C messaging + explicit re-sign of the success criterion (§9.2) |
| Placeholder email leaks to Chargebee | Low | **High** (billing) | Never pass `.email()` in `phone-signup`; integration test asserts the Chargebee payload carries phone only |
| System mailbox shown in Profile / invoices | Medium | Medium | Mask in app; never pass to Chargebee |
| OTP cleared before signup | **Certain** if unhandled | High | `signupToken` in the `user_not_found` body (§3.3) |
| Deleting a screen that a test or deep link still uses | Medium | Medium | A4-G2 / A4-G3; stubs first, deletion in a separate commit |
| Auth BLoC edits collide with UX work | Medium | Low | Auth branch first; merge before W0's dashboard adoption |
| Google returning user forced into signup completion | **Certain** today (`F11`) | High | Render `GoogleSignupScreen` only on `link_required`; device check §10.2 #3 |
| Two OTP implementations diverge further | High if left | Medium | A1 deletes the Firebase path outright |

---

## 12. Sign-off required

| # | Decision | Recommendation | If declined |
| :--- | :--- | :--- | :--- |
| **A-1** | Approve two **additive** server endpoints (`/auth/phone-signup`, `/auth/google-signup`) + `signupToken` in the `login-otp` not-found body | **Approve** — 1.5 d, no existing contract changes, the only way to meet the brief | Phone signup cannot ship (§9.2) |
| **A-2** | Keep `LinkGoogleAccountScreen` as a conflict-resolution step (no Stitch design, token-restyled) | **Keep** — deleting it creates duplicate accounts for users with two emails | Google+phone collision has no resolution path |
| **A-3** | System mailbox `{phone}@phone.bookmyjuice.in` for phone-first accounts | **Accept** now; nullable `users.email` in a later ADR | Requires a schema migration before A3 |
| **A-4** | `/auth/signin` and `/auth/unified-signup` stay on the server (unreachable from the app) | **Keep** — removing them is an unrelated backend change | Extra server diff, no customer benefit |
| **A-5** | Confirm no customer relies **only** on email+password (A4-G1) | **Run the count before W4** | Do not delete; keep the password form until migration is done |

**On approval I start W-0** (A0 + A1) in the Flutter tree — guardrail test, `PhoneEntryScreen`, route repoints, Firebase-OTP removal — as one commit that touches no styling and no business logic. A2 waits for W0's tokens; A3 waits for A-1.

---

*End of plan. Evidence for every line reference was read from the working tree on 2026-10-17; scripts used: `C:\Users\Public\auth_map.py`, `auth_flow.py`, `auth_routes.py`, `auth_handlers.py`, `grep_otp.py`, `auth_feasibility.py`.*
