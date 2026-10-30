# Auth Simplification â€” Implementation Plan (W-0 â†’ A6)

**Status:** APPROVED â€” execution starting 2026-10-17
**Supersedes (for execution detail):** `AUTH_SIMPLIFICATION_PLAN.md` Â§9â€“Â§10
**Parent plans:** `AUTH_SIMPLIFICATION_PLAN.md`, `BMJ_UX_REHAUL_PLAN.md` (amended: 4 tabs)
**Trees:** client `x:\BMJ\lush` Â· server `x:\BMJ\bmjServer`
**Constraint:** no visual redesign in this wave. No passwords. No email auth. Two methods only: **Google Sign-In** and **Phone OTP**.

---

## 1. Decisions this plan executes

| ID | Decision | Effect on this plan |
| :--- | :--- | :--- |
| A-1 | **APPROVED** â€” build the two additive endpoints | `POST /auth/phone-signup`, `POST /auth/google-signup`; `signupToken` added to the `login-otp` not-found body |
| A-2 | **KEEP** `LinkGoogleAccountScreen` | remains the collision resolver (Google identity meets an existing phone account) |
| A-3 | **APPROVED (temporary)** â€” system mailbox | `{phone}@phone.bookmyjuice.in`, DB-only, never in UI, **never sent to Chargebee** |
| A-4 | KEEP server `signin` / `unified-signup` | dead client callers only; no server deletion in this wave |
| A-5 | **MANDATORY** impact query before deleting email/password | gate `A4-G1` below |
| D2 | **4 tabs**: Home Â· Subscription Â· Orders Â· Profile | `Orders` is the existing `OrdersTab`; `Catalog` is reached from Home; see Â§7 |
| â€” | No fake accounts, no password UI, no email signup flow | acceptance gate `A0-G2` (guardrail test) |

> **D2 note.** The approval names the four tabs `Home / Subscription / Orders / Profile`. This replaces the earlier "Home Â· Catalog Â· Subscription Â· Profile + re-home Orders" proposal. Therefore index 1 becomes `Orders` (the existing `OrdersTab`), `MenuTab` stays reachable from Home, and index 2 becomes the real `SubscriptionTab`. No screen is deleted to achieve this.

---

## 2. Why deletion alone cannot work (restated for implementers)

1. `POST /auth/login-otp` returns `{status: user_not_found}` â€” it does **not** create an account (`AuthController.java:473-480`).
2. `POST /auth/google` returns `{status: link_required}` when no account exists (`:222-231`).
3. Both signup handlers require `email` **and** `password` (`UnifiedSignupRequest`; `AuthController.java:665`, `:691`).
4. The OTP is marked **used** by `login-otp` and then cleared (`AuthController.java:475`, `OTPUtil.java:108-112`), so a later signup POST cannot re-verify it.

The only honest bridge from "phone verified" to "account exists" without a password is a short-lived **`signupToken`** minted at verification time and redeemed once by a signup endpoint.


---

## 3. Contract A-1 (server)

All paths are relative to `/api` and exist under both `/api/auth` and `/api/v1/auth` (class-level mapping). All are `permitAll` via `WebSecurityConfig.java:89`.

### 3.1 `signupToken`

| Property | Value |
| :--- | :--- |
| Format | JWT, HS256, signed with the existing `bezkoder.app.jwtSecret` |
| Subject | the verified 10-digit phone |
| Claim `purpose` | `"phone-signup"` |
| TTL | 15 minutes |
| Minted by | `POST /auth/login-otp` when the user does **not** exist |
| Redeemed by | `POST /auth/phone-signup`, `POST /auth/google-signup` |
| Replay | allowed until TTL; signup is guarded by the uniqueness checks below |
| Invalid/expired | `400 {"message":"Error: Phone verification expired. Please verify your number again."}` |

Added to `JwtUtils`: `generatePhoneVerificationToken(String phone)` and `getPhoneFromVerificationToken(String token)`. The `purpose` claim is checked on read so a normal access token can never be used as a signup token, and vice versa.

### 3.2 `POST /auth/phone-signup`

```jsonc
{
  "signupToken": "<jwt>",
  "firstName": "Asha",
  "lastName": "Rao",
  "email": "asha@example.com",      // optional; blank => system mailbox
  "address": "12 MG Road",
  "extendedAddr": "Near Metro",
  "extendedAddr2": "",
  "city": "Bengaluru",
  "state": "Karnataka",
  "zip": "560001",
  "country": "IN"
}
```

Server behaviour:
1. Redeem `signupToken` â†’ `phone`. Reject on invalid/expired.
2. Reject if `existsByUsername(phone)` or `findByPhone(phone)` â†’ `400 "Error: Phone number is already registered!"`.
3. Email: if blank â†’ `phone + "@phone.bookmyjuice.in"`; if present â†’ lower-case/trim and reject when `existsByEmail`.
4. Create `User(username=phone, email, encoder.encode(UUID.randomUUID().toString()))`, assign `ROLE_USER`, set names/address/phone, save.
5. Chargebee: **only when the email is not a system mailbox.** System-mailbox accounts are created without a Chargebee customer and logged at INFO.
6. Create the default `UserAddressEntity` (reuse the block currently inside `unifiedSignup`, extracted to a private helper).
7. Return `JwtResponse` (auto-login) â€” no follow-up password call.

### 3.3 `POST /auth/google-signup`

```jsonc
{
  "idToken": "<google id token>",
  "signupToken": "<jwt>",
  "address": "...", "extendedAddr": "...", "extendedAddr2": "...",
  "city": "...", "state": "...", "zip": "...", "country": "IN"
}
```

Server behaviour:
1. Re-verify the Google ID token server-side (tokeninfo, `email_verified == true`) â€” never trust a client-supplied `googleId`/`email`.
2. Redeem `signupToken` â†’ `phone`; reject when the phone is already registered.
3. Reject when the Google email is already registered â†’ `400 "Error: Email is already registered! Sign in with Google instead."`
4. Create the user with a random unrecoverable password, `googleId`, `googlePhotoUrl`, Google names, phone, address; Chargebee customer with the **real** Google email; default address row.
5. Return `JwtResponse`.

### 3.4 Error envelope

Existing convention: `{"message": "Error: ..."}` with `400`. No new error shape.

### 3.5 Rate limiting

Add `/api/auth/phone-signup` and `/api/auth/google-signup` to `RateLimitingFilter`'s protected path list (same bucket as `send-otp`).

### 3.6 System mailbox guard (A-3 enforcement)


---

## 4. Client flow after this wave

```
LoginPage ("/login")
â”œâ”€â”€ Continue with Google â”€â”€â–¶ GoogleSignIn â”€â”€â”¬â”€ login_success â”€â”€â–¶ Dashboard
â”‚                                           â””â”€ link_required â”€â”€â–¶ LinkGoogleAccountScreen
â”‚                                                                 â”œâ”€ existing phone + OTP â”€â”€â–¶ link & Dashboard
â”‚                                                                 â””â”€ "Create a new account" â”€â”€â–¶ GoogleSignupScreen
â”‚                                                                                                â””â”€ phone â”€â”€â–¶ OTP â”€â”€â–¶ Address â”€â”€â–¶ /auth/google-signup â”€â”€â–¶ Dashboard
â””â”€â”€ Continue with Phone â”€â”€â–¶ PhoneEntryScreen ("/phone-entry")
                              â””â”€ SendOTP â”€â”€â–¶ PhoneOtpVerificationScreen
                                               â”œâ”€ existing user â”€â”€â–¶ Dashboard
                                               â””â”€ user_not_found â”€â”€â–¶ AddressEntryScreen (signupToken)
                                                                       â””â”€ /auth/phone-signup â”€â”€â–¶ Dashboard
```

`/phone-entry` replaces both `/phone-login` and `/phone-signup`. `/otp` (the unverified stub) redirects to `/phone-entry`.

---

## 5. Screen disposition (final)

| Screen | Route(s) | Action |
| :--- | :--- | :--- |
| `login_page.dart` | `/login` | **EDIT** â€” remove email + password fields, forgot-password link and password submit; keep Google + Phone CTAs and both tabs |
| `phone_entry_screen.dart` | `/phone-entry` | **NEW** â€” merges `/phone-login` + `/phone-signup`; backend OTP only |
| `phone_otp_verification_screen.dart` | `/phone-otp-verification` | **EDIT** â€” one verification path (`login-otp`), Firebase branch removed, routes to address with `signupToken` |
| `address_entry_screen.dart` | `/address-entry` | **EDIT** â€” terminal step; posts to `/auth/phone-signup` or `/auth/google-signup`; optional email field for phone accounts |
| `google_signup_screen.dart` | `/google-signup` | **EDIT** â€” phone collection only (no password, no address); hands off to OTP |
| `link_google_account_screen.dart` | (state-driven) | **KEEP + small edit** â€” add "Create a new account" escape to `/google-signup` |
| `sign_up_screen.dart` | (state-driven) | **DELETE** â€” email/password signup |
| `signup_method_selection_screen.dart` | `/signup-method-selection` | **DELETE** |
| `email_signup_screen.dart` | `/email-signup` | **DELETE** |
| `email_verification_screen.dart` | `/email-verification` | **DELETE** |
| `phone_entry_after_email_screen.dart` | `/phone-entry-after-email` | **DELETE** |
| `email_entry_after_phone_screen.dart` | `/email-entry-after-phone` | **DELETE** |
| `email_verification_after_phone_screen.dart` | `/email-verification-after-phone` | **DELETE** |
| `create_password_screen.dart` | `/create-password` | **DELETE** |
| `forgot_password_page.dart` | `/forgotPasswordPage` | **DELETE** |
| `forgot_password_screen.dart` | `/forgot-password` | **DELETE** |
| `reset_password_mobile_screen.dart` | `/reset-password-mobile-otp` | **DELETE** |
| `reset_password_email_screen.dart` | `/reset-password-email-code` | **DELETE** |
| `phone_login_screen.dart` | `/phone-login` | **DELETE** (replaced by `/phone-entry`) |
| `phone_signup_screen.dart` | `/phone-signup` | **DELETE** (replaced by `/phone-entry`) |
| `google_phone_entry_screen.dart` | `/google-phone-entry` | **DELETE** (dead) |
| `otp_login_page.dart` | `/otp` | **DELETE** (stub that called `SignUp()` unverified) |
| `views/models/firebase_phone_auth.dart` | n/a | **DELETE** + Firebase BLoC events/states/handlers |

**17 files / 4,026 lines deleted** (16 screens = 3,860 lines, `firebase_phone_auth.dart` = 166 lines). Retired routes remain as one-line redirect stubs to `/login` (deep links and stale builds must not 404), except the three replaced by `/phone-entry` (`/phone-login`, `/phone-signup`, `/otp`).


---

## 6. Server change list

| File | Change |
| :--- | :--- |
| `security/jwt/JwtUtils.java` | `+ generatePhoneVerificationToken`, `+ getPhoneFromVerificationToken`, `+ PURPOSE`/TTL constants |
| `payload/request/PhoneSignupRequest.java` | **NEW** DTO (`signupToken`, `firstName`, address block; `email` optional) |
| `payload/request/GoogleSignupRequest.java` | **NEW** DTO (`idToken`, `signupToken`, address block) |
| `controllers/AuthController.java` | `signupToken` in `login-otp` not-found body; `+ /phone-signup`; `+ /google-signup`; extract `saveDefaultAddress(...)`; `isSystemMailbox(...)` guard on **all** Chargebee create sites |
| `security/RateLimitingFilter.java` | `+ /api/auth/phone-signup`, `+ /api/auth/google-signup` |
| `test/.../controllers/AuthSignupFlowTest.java` | **NEW** â€” token mint/redeem, expiry, wrong-purpose rejection, duplicate phone/email, system-mailbox Chargebee skip, random password is unusable |

---

## 7. Client change list

| File | Change |
| :--- | :--- |
| `lib/views/screens/phone_entry_screen.dart` | **NEW** â€” phone field, 10-digit validation, `SendOTP`, listener â†’ `/phone-otp-verification` |
| `lib/bloc/AuthBloc/auth_state.dart` | `+ PhoneSignupRequired(phone, signupToken)`; remove Firebase states |
| `lib/bloc/AuthBloc/auth_events.dart` | remove Firebase events; `+ PhoneSignupRequested`, `+ GoogleSignupRequested` |
| `lib/bloc/AuthBloc/auth_bloc.dart` | `PhoneOtpLogin` emits `PhoneSignupRequired` on not-found; `+` handlers for the two signup events; remove Firebase handlers/import; `GoogleSignIn.signup_required` â†’ `GoogleLinkRequired` |
| `lib/UserRepository/user_repository.dart` | `loginViaPhoneOtp` returns `signupToken`; `+ completePhoneSignup`, `+ completeGoogleSignup` (save JWT, then `getUserDetailsFromServer`) |
| `lib/views/screens/phone_otp_verification_screen.dart` | Firebase removal; single `PhoneOtpLogin` dispatch; route on `PhoneSignupRequired` |
| `lib/views/screens/address_entry_screen.dart` | terminal submit; google vs phone payload; optional email |
| `lib/views/screens/google_signup_screen.dart` | phone-only rewrite (no password/address) |
| `lib/views/screens/link_google_account_screen.dart` | `+ "Create a new account"` â†’ `/google-signup` |
| `lib/views/screens/login_page.dart` | password UI removal (A2-lite); layout unchanged |
| `lib/main.dart` | routes: add `/phone-entry`; delete 15 route entries; redirect stubs; imports pruned; `AuthWrapper` no longer constructs `SignUpScreen` |
| `lib/views/all_screens.dart` | drop `otp_login_page` + `sign_up_screen` exports |
| `lib/views/screens/subscription_tab.dart` | **NEW** â€” tab wrapper (P0-1/D2) |
| `lib/views/screens/subscription_management_screen.dart` | `+ final bool embedded` (default `false`) â€” body without `Scaffold`/`AppBar` |
| `lib/views/screens/dashboard.dart` | tabs: Home Â· **Orders** Â· **Subscription** Â· Profile |
| `lib/views/screens/home_tab.dart` | `+ "Browse plans"` â†’ `/plan-selection`; `+ "See all"` on recent orders â†’ `/orders` |
| `lib/views/screens/plan_selection_screen.dart` | (P0-2) Weekly/Monthly toggle + data-driven BEST VALUE badge |
| `test/widget/screens/auth_no_password_test.dart` | **NEW** guardrail |
| `test/widget/screens/phone_entry_screen_test.dart` | **NEW** |
| `test/widget/screens/login_page_test.dart` | updated for the two-CTA surface |
| `test/widgets/signup_screen_test.dart`, `signup_validation_test.dart` | **DELETE** |
| `test/unit/bloc/auth_bloc_test.dart` | prune cases that no longer compile |


---

## 8. Commit sequence and gates

| # | Commit | Contents | Gate |
| :--- | :--- | :--- | :--- |
| **W-0a** | `test(auth): no-password guardrail + phone entry` | guardrail test, `PhoneEntryScreen`, `/phone-entry` route | `flutter analyze` clean; new widget test green |
| **W-0b** | `refactor(auth): one phone OTP path` | OTP screen edit, state/event/repository plumbing, `/otp` repoint | `flutter test` green |
| **W-0c** | `feat(auth): delete email/password screens` | 15 screens + firebase wrapper + Firebase BLoC; route stubs; `login_page` strip; google signup rewrite; address terminal step | `A0-G2` green; `flutter analyze` clean |
| **A1** | `feat(server): phone/google signup + signupToken` | server files Â§6 | `mvnw verify -Dtest=AuthSignupFlowTest,AuthControllerTest` |
| **A3** | `feat(auth): redeem signupToken in the app` | repository + BLoC wiring end-to-end | manual: cleared install â†’ phone â†’ OTP â†’ address â†’ dashboard |
| **P0-1** | `fix(nav): Subscription tab opens subscriptions` | `SubscriptionTab`, `embedded`, dashboard tabs | widget test: index 2 has no `OrdersTab`; Orders reachable |
| **P0-2** | `feat(catalog): plan catalogue entry points` | 3 live entries + toggle/badge | widget test per entry |

Gates that must be **redâ†’green** before W-0c merges:

- **A0-G1** `flutter analyze` â€” zero new issues.
- **A0-G2** `auth_no_password_test.dart` â€” no `obscureText`, no `password`/`confirmPassword` identifiers, no `'Password'` label in auth screens, and the 16 files are absent.
- **A0-G3** `flutter test` â€” full suite.

---

## 9. A-5 gate (blocking, run before W-0c merges)

```sql
SELECT COUNT(*) FROM users
WHERE google_id IS NULL
  AND (phone IS NULL OR phone = '')
  AND deleted = false;
```

- `0` â†’ proceed.
- `> 0` â†’ stop; produce a migration plan (each row is an account reachable only by password today). Report the count with the commit.

Also record: `SELECT COUNT(*) FROM users WHERE deleted = false AND google_id IS NULL;` (phone-only population) and `SELECT COUNT(*) FROM users WHERE deleted = false AND (phone IS NULL OR phone='');` (email-only population).

---

## 10. Test plan

| Layer | Test | Asserts |
| :--- | :--- | :--- |
| Widget | `auth_no_password_test.dart` | guardrail A0-G2 (static file scan â€” no widget pumping) |
| Widget | `phone_entry_screen_test.dart` | empty/short/invalid phone errors; valid phone dispatches `SendOTP`; no Firebase affordance |
| Widget | `login_page_test.dart` | exactly two auth CTAs; no password field; phone CTA pushes `/phone-entry` |
| Widget | `subscription_tab_test.dart` | `SubscriptionTab` renders; `OrdersTab` absent from index 2 |
| BLoC | `auth_bloc_test.dart` | `PhoneOtpLogin` â†’ `PhoneSignupRequired` carries `signupToken`; `PhoneSignupRequested` success â†’ `AuthenticationSuccess` |
| Server | `AuthSignupFlowTest` | Â§6 rows; plus "a random-password account cannot sign in with `password`/`12345678`" |
| Manual | device pass | cleared install: phone â†’ OTP â†’ address â†’ dashboard; kill app â†’ autologin; Google new user â†’ create account â†’ dashboard; Google existing phone â†’ link â†’ dashboard |

---

## 11. Risks and rollback

| Risk | Mitigation |
| :--- | :--- |
| `signupToken` replay creates duplicate accounts | uniqueness checks on phone/email + DB constraint; 15-min TTL |
| System mailbox reaches Chargebee (A-3 violation) | single `isSystemMailbox` guard on every create site + server test |
| Phone-only account cannot check out (no Chargebee customer, no invoice email) | documented limitation: Chargebee is created on first sign-in **after** a real email is captured; checkout surfaces the existing "Chargebee customer ID not found" error. Follow-up: email capture before checkout |
| Deleting screens breaks stale imports | `flutter analyze` gate + mechanical reference sweep (Â§12) |
| Login page loses password but a deep link still posts `LogIn` | server `signin` remains (A-4); only client UI removed |
| Rollback | one revert per commit; server endpoints are additive, so reverting client commits alone leaves the server harmless |

---

## 12. Mechanical verification

```powershell
cd X:\BMJ\lush
flutter analyze
flutter test
Get-ChildItem lib,test,integration_test -Recurse -Filter *.dart |
  Select-String -Pattern 'SignUpScreen|EmailSignupScreen|CreatePasswordScreen|OTPLoginPage|PhoneLoginScreen|PhoneSignupScreen|FirebasePhoneAuth'
```

Expected: only the guardrail test's own allow-list mentions the deleted names.

---

## 13. Execution checklist

- [x] W-0a guardrail + `PhoneEntryScreen` + route
- [x] W-0b single OTP path + `PhoneSignupRequired`
- [x] A-5 query reported (`A4-G1`) â€” **reported 2026-10-18 against bmj_db on 3307: 0 password-only / phone-only 1 / email-only 0 / total 1 - gate passes, see section 15**
- [x] W-0c deletions + route stubs + login strip + google signup rewrite
- [x] A1 server endpoints + tests
- [x] A3 client redemption end-to-end (code complete; device pass PASS 2026-10-18, see section 15)
- [x] P0-1 Subscription tab
- [x] P0-2 plan catalogue entry points (3 live entries; PDP entry deferred to P0-4)
- [x] Device pass (partial: phone flow PASS on 192.168.1.5 over Wi-Fi ADB; Google flows not exercised - see section 15)

---

## 14. Execution log (2026-10-17)

**Client (`x:\BMJ\lush`)**

| Change | Detail |
| :--- | :--- |
| `phone_entry_screen.dart` | new, `/phone-entry`; BLoC `SendOTP`; `_awaitingOtp` guard prevents a resend from stacking a second route |
| `phone_otp_verification_screen.dart` | rewritten: single `PhoneOtpLogin` dispatch; `PhoneSignupRequired` â†’ `/address-entry` with `signupToken`; all Firebase branches removed |
| `address_entry_screen.dart` | terminal step; dispatches `PhoneSignupRequested` / `GoogleSignupRequested`; optional email (read-only for Google); success â†’ `/dashboard` |
| `google_signup_screen.dart` | rewritten to phone collection only (no password, no address); carries Google identity to OTP |
| `link_google_account_screen.dart` | single OTP check (the old `verify-otp` + `link` double check always failed because OTPs are single-use); `Create a new account instead` â†’ `/google-signup` |
| `login_page.dart` | email/password fields, forgot-password link and submit removed; two CTAs on the Sign In tab; sign-up phone card â†’ `/phone-entry` |
| `main.dart` | `/phone-entry` added; `/phone-login`, `/phone-signup`, `/otp` land on it; 12 retired routes â†’ `_retiredAuthRoute`; `AuthWrapper` no longer mounts `SignUpScreen` |
| `auth_state.dart` / `auth_events.dart` / `auth_bloc.dart` | `PhoneSignupRequired(phone, signupToken)`; `PhoneSignupRequested` / `GoogleSignupRequested`; Firebase events, states, handlers and import removed; Google not-found â†’ `GoogleLinkRequired` |
| `user_repository.dart` | `loginViaPhoneOtp` returns `signupToken`; new `completePhoneSignup` / `completeGoogleSignup` (+ shared `_handleSignupResponse` that saves the JWT and loads the profile) |
| `dashboard.dart` / `subscription_tab.dart` / `subscription_management_screen.dart` | tabs Home Â· Orders Â· Subscription Â· Profile; `embedded` mode; `Change or add a plan` â†’ `/plan-selection` |
| `home_tab.dart` | empty subscription state â†’ `Browse plans` (`/plan-selection`); recent orders `View All` â†’ `/orders` |

**Server (`x:\BMJ\bmjServer`)**

| Change | Detail |
| :--- | :--- |
| `JwtUtils` | `generatePhoneVerificationToken` / `getPhoneFromVerificationToken`; `purpose=phone-signup`, 15-min TTL; access tokens rejected |
| `PhoneSignupRequest` / `GoogleSignupRequest` | new validated DTOs (no password, no client-supplied phone/email for Google) |
| `AuthController` | `/phone-signup`, `/google-signup`; `signupToken` in the `login-otp` not-found body; `isSystemMailbox` guard on all three Chargebee backfill sites; shared `createChargebeeCustomer`, `saveDefaultAddress`, `jwtFor` |
| `RateLimitingFilter` | both new endpoints rate-limited |

**Gates run**

| Gate | Result |
| :--- | :--- |
| `flutter analyze` (full tree) | **0 errors** (pre-existing infos/warnings unchanged) |
| `dart analyze` on every touched file | clean |
| `auth_no_password_test.dart` (A0-G2) | 4/4 pass |
| `phone_entry_screen_test.dart` | 4/4 pass |
| `login_page_test.dart` | 7/7 pass |
| `auth_bloc_test.dart` | 24/24 pass (incl. 3 new `PhoneOtpLogin` cases) |
| `test/widget_test.dart` | pass |
| `mvnw test -Dtest=AuthControllerTest,JwtUtilsTest` | **75 pass, 0 fail** (incl. 5 new signup-endpoint tests, 3 new token tests) |
| Reference sweep for deleted classes | clean |

**Known state / deviations**

1. `test/subscription_screens_test.dart` has 11 **pre-existing** failures in plan/schedule/summary screens (untouched files), and `integration_test/google_signup_test.dart` was a structure-only stub for the removed password UI, so it was deleted.
2. The A-5 user-impact query has **not** been executed â€” no DB credentials in this environment. It remains a hard gate before deployment.
3. Chargebee customer creation is deliberately skipped for system-mailbox accounts (A-3). Phone-only customers therefore cannot check out until a real email is captured; the existing "Chargebee customer ID not found" path surfaces it. Follow-up work: capture an email before the first checkout.
4. The working tree already contained unrelated uncommitted changes before this wave; nothing was committed, so those changes are untouched and the auth diff is reviewable with `git diff -- <paths>`.
5. A Google signup attempt on a phone number that already belongs to an account currently signs that user in **without** linking the Google identity (the `/auth/login-otp` success path). Linking remains available through the `link_required` route on a later Google sign-in. Follow-up: when `isGoogleSignup` is true and login succeeds, offer "Link this Google account" (the `/link-google-account` endpoint already supports it).
6. `SubscriptionTab` shows a sign-in / browse-plans state for unauthenticated visitors so the tab never fires an unauthenticated subscriptions request at app start.

---

## 15. Device pass - 2026-10-18 (LAN, `bmj-smoke-mysql`)

**Environment:** backend `java -jar com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar --server.port=8085 --spring.profiles.active=dev --spring.datasource.url=jdbc:mysql://127.0.0.1:3307/bmj_db?...` on host `192.168.1.10`; app built with `flutter build apk --debug --dart-define=API_BASE_URL=http://192.168.1.10:8085`, installed on device `192.168.1.5:5555` (package `com.bookmyjuice.app`) after `pm clear`. OTPs were read from `bmjServer/logs/local-run.log` (`[DEV] OTP for <phone>: <code>`; `FAST2SMS_API_KEY` blanked for the run).

| Step | Result |
| :--- | :--- |
| Public dashboard at launch (no token) | **PASS** - Home / Orders / Subscription / Profile tabs; Profile shows "Sign in to manage your account" |
| Login page content | **PASS** - exactly two CTAs (Google, Phone), no password field, helper text "No password needed - we text you a 6-digit code." |
| Phone entry -> OTP -> verify | **PASS** - one OTP delivered to the log, `login-otp` returns `user_not_found` + `signupToken` |
| Address step -> account creation | **PASS** - `POST /api/auth/phone-signup` 200; user **501** (`9999999922`) created with system mailbox `9999999922@phone.bookmyjuice.in` and `chargebee_customer_id` NULL (A-3 guard logged "Skipping Chargebee customer ... system mailbox"); default address row written |
| Kill app -> relaunch (autologin) | **PASS** - lands on the authenticated dashboard ("Good morning, Device") |
| Google flows (new user, existing-phone link) | **NOT EXERCISED** - needs a real Google ID token from a device signed into Play services |

The same chain was also confirmed headlessly (no device): `send-otp` -> 200, `login-otp` -> 200 + `signupToken`, `phone-signup` -> 200 + JWT (user 500).

### Findings raised by the pass

| ID | Severity | Detail |
| :--- | :--- | :--- |
| DP-1 | Medium | The signed-out **Home tab** calls `GET /api/subscriptions` and `GET /api/orders`; both answer 401 and the card renders "Failed to load subscription status" + Retry instead of the sign-in / browse-plans state (the §13 item 6 guard covers only `SubscriptionTab`) |
| DP-2 | Medium | Immediately after a successful phone signup the app goes to a **black screen with an empty semantics tree**; logcat shows `setState() called after dispose()` from `_SubscriptionManagementScreenState._loadSubscriptions` (`subscription_management_screen.dart:45,51`) plus `Unauthorized: Please login again`. Force-stop + relaunch recovers |
| DP-3 | Medium | For a phone-only account `SubscriptionController`/`OrderController` log "No Chargebee customer ID found for local user: 501" and reply `{error=User not authenticated}` (401), so the UI reports a session problem instead of the documented "Chargebee customer required" limitation (§11) |
| DP-4 | Low | `RenderFlex` bottom overflow of 6.0 px on the home promo banner (debug build) |

**Screenshots:** `ops/device_home.png`, `ops/device_after_signup.png`, `ops/device_state3.png`, `ops/device_subscription_error.png`.

---

## 16. Mandatory email at signup - supersedes A-3, resolves DP-3 (2026-10-18)

**Decision (owner):** every account must carry a **name, a phone and a verified
email**; the delivery address becomes **optional** at signup ("Skip for now",
add it later from Profile -> Addresses). The phone-first journey therefore gains
an email-OTP step and the system-mailbox fallback (A-3) is retired for new
accounts. Because the email is always real, a Chargebee customer can be
provisioned at signup, which is what dissolves **DP-3**.

### 16.1 Server (`x:\BMJ\bmjServer`)

| File | Change |
| :--- | :--- |
| `JwtUtils` | `generateEmailVerificationToken` / `getEmailFromVerificationToken`; `purpose=email-verify`, 15-minute TTL; access and phone tokens are rejected |
| `PhoneSignupRequest` | `email` + `emailVerificationToken` are `@NotBlank`; every address field lost `@NotBlank`/`@NotBlank`-style checks and is trimmed to `null` when blank |
| `GoogleSignupRequest` | address fields optional (Google already supplies a verified email) |
| `AuthController#phoneSignup` | redeems **both** tokens, rejects a phone/email proof mismatch, always stores a real (lower-cased) email, and skips `saveDefaultAddress` for a blank address |
| `AuthController#verifyEmailCode` | returns `{message, email, emailVerificationToken}`; the code stays single-use |
| `AuthController#sendEmailVerification` | normalises the address and answers **429** while the 30-second cooldown is active |
| `EmailVerificationService` | `ConcurrentHashMap` stores, 30-second resend cooldown, 5-guess cap, delivery failures logged instead of thrown (the `[DEV]` code line is unchanged, so local runs still work with a broken relay) |

Flow: `send-otp` -> `login-otp` (`signupToken`) -> `send-email-verification` ->
`verify-email-code` (`emailVerificationToken`) -> `phone-signup` (JWT).

### 16.2 Flutter (`x:\BMJ\lush`)

| File | Change |
| :--- | :--- |
| `signup_email_verification_screen.dart` (new, `/signup-email-verification`) | email -> code -> proof; 30-second resend countdown, "Change email", keys `signup_email_field`, `send_email_code_button`, `signup_email_code_field`, `verify_email_code_button`, `resend_email_code_button`, `change_email_button` |
| `phone_otp_verification_screen.dart` | `PhoneSignupRequired` now routes to the email step (Google keeps going straight to the address step) |
| `address_entry_screen.dart` | email is read-only ("verified"); name stays mandatory; address block is optional with **Skip for now** (`address_skip_now_button`) and `address_continue_button`; partial addresses only validate once line 1 is filled |
| `auth_events.dart` / `auth_bloc.dart` | `PhoneSignupRequested.emailVerificationToken`; `VerifyEmail` stores the proof and the phone-signup handler falls back to it |
| `user_repository.dart` | `completePhoneSignup(email, emailVerificationToken, …)` sends the proof and accepts blank address fields; `verifyEmailCode` returns `{status, email, emailVerificationToken}` / `{status, error}` |
| `main.dart` | new `/signup-email-verification` route (the retired `/email-verification` alias is untouched) |

### 16.3 Findings resolved in the same wave

| ID | Fix |
| :--- | :--- |
| DP-1 | `dashboard.dart` only dispatches `LoadActiveSubscriptions` when `UserRepository.userLoggedIn`; `home_tab.dart` only dispatches `LoadOrderHistory` when signed in and hides the subscription spinner/error cards for guests |
| DP-2 | `address_entry_screen.dart` navigates to `/dashboard` from `addPostFrameCallback` with `mounted` guards; `subscription_management_screen.dart#_loadSubscriptions` guards both `setState` calls with `mounted` |
| DP-3 | **Dissolved** - every phone-first account now has a real email, so `createChargebeeCustomer` runs during signup and `chargebee_customer_id` is populated (best-effort, as before) |
| DP-4 | Promo carousel height `130.h` -> `140.h` plus `maxLines`/`ellipsis` on the offer title and subtitle |

> **Behaviour note (Chargebee):** the existing best-effort `Customer.create()`
> call now runs for phone-first signups as well, because the email is real.
> Nothing else changed in the Chargebee integration; on the test site this means
> one test customer per successful signup.

### 16.4 Gates run

| Gate | Result |
| :--- | :--- |
| `mvn -o test -Dtest=EmailVerificationServiceTest,AuthControllerTest` | **81 pass, 0 fail** - 8 phone-signup cases (invalid phone token, missing email proof, mismatch, duplicate phone, duplicate email, happy path, skip-address, Google token guard) and 10 email-service cases (incl. cooldown and attempt cap) |
| `flutter analyze` on every touched file | **No issues found** |
| `flutter test` | 326 pass, 12 fail - **all pre-existing** (11 plan/schedule/summary cases in `test/subscription_screens_test.dart` already listed in §14, plus `product_catalog_bloc_test` `FilterByCategory`); no auth test regressed (`auth_bloc_test`, `phone_entry_screen_test`, `login_page_test`, `auth_no_password_test` pass) |
| Full `flutter analyze` | 0 errors (415 infos/warnings, unchanged baseline) |

### 16.5 Not done in this wave

1. **Device E2E** of the new step (phone OTP -> email OTP -> address Save/Skip ->
   dashboard -> relaunch autologin) is pending; the runbook is
   `docs/guides/DEVELOPMENT_TOOLS.md` §11 plus §11.6 for reading the email code.
2. **Google signup** remains `BLOCKED (manual)` - it needs a real Google ID
   token from a Play-signed-in device.
3. Existing accounts created with a system mailbox (`@phone.bookmyjuice.in`)
   keep working as before; only new signups require a real email.

**Runbook for repeating this pass:** `docs/guides/DEVELOPMENT_TOOLS.md` §11.
