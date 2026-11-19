# Changelog

## [2026-11-19] Backend deployed to the VPS + identity self-heal and webhook hardening

**Deployment** - the BMJ backend now runs on `api.bookmyjuice.co.in` (Ubuntu 24.04), nginx + TLS in
front, MySQL 8 and the API as Docker Compose services under a systemd unit. Details and the two
failures encountered are in `VPS_DEPLOYMENT_RUNBOOK.md`.

- Verified `https://api.bookmyjuice.co.in/api/health` -> `200 {"status":"UP"}` and
  `/api/catalog/charge-items` -> `200` with 15 items.
- Tomcat is bound to `127.0.0.1:8080` only; MySQL publishes no host port. nginx is the single entry.
- `bmj-stack.service` enabled, so the stack returns after a reboot.
- Required env vars turned out to be ten (not eight): `JWT_SECRET` and `MAIL_PASSWORD` have no
  defaults and are the ones that crash-loop the container when missing.

**Identity self-heal on login** (`feat(sync)`, `051ee6b`) - `IdentityLinker.linkUser()` derives the
link in the user -> customer direction, is idempotent, repairs dangling links and prefers the
Chargebee-shaped customer id over a legacy numeric twin. Wired into `signin`, `googleSignIn`,
`linkGoogleAccount`, `loginViaOtp`, `jwtFor` (phone + Google signup) and both registration returns.
It never throws, so a linking failure cannot lock a user out.

**Subscription event coverage** (`feat(sync)`, `00e2a19`) - handlers for `subscription_activated`,
`subscription_started` and `subscription_deleted`, which the live Chargebee subscription endpoint
subscribes but the processor rejected. `WebhookEventCoverage` is now the single map of event type ->
handling component, and a test asserts all **29** subscribed types are covered.

**Malformed webhook payloads** (`fix(webhooks)`, `fd07e48`) - a body without `id` used to raise a
`NullPointerException` that the controllers' catch-all turned into a **500**, which Chargebee retried
forever. A filter now answers **400** with `{"error":"malformed_webhook_payload"}` and replays the
buffered body so controllers are unaffected. It runs after Spring Security, so unauthenticated
callers still get 401 first.

**Webhook credentials** (`fix(security)`, `865fb16`) - `WEBHOOK_USERNAME`/`WEBHOOK_PASSWORD`
defaulted to empty, so Spring built an in-memory user with a blank password and `/api/webhooks/**`
accepted any `Basic` header: the endpoint **failed open**. Startup now aborts with a message naming
the missing variable; `webhook.auth.optional=true` is the documented local-only escape hatch.

**Tests** - 61 new/updated cases across 9 suites, all passing. `bmjServer` pushed to
`origin/main` (`865fb16`).

**Chargebee status** - unchanged and still disabled: `subscription` and `Customer` endpoints are
switched off, every URL is `http://...:8080` (now loopback-only) and one endpoint points at an ngrok
tunnel. `WEBHOOK_ACTIVATION_CHECKLIST.md` carries the ordered procedure and the code prerequisites.



- **Drawer (one system, newly wired):** `lib/widgets/app_drawer.dart` rebuilt and attached to the tab shell (`dashboard.dart`) via the shared header's leading slot. Exactly four destinations — **Profile** (`/user-profile`), **Subscription plans** (`/plan-selection`), **Menu** (`/catalog`), and **Logout** (authenticated, confirmed) or **Sign in** (guest) in the same slot. The previous drawer existed but was unused, required a signed-in `User`, and carried seven unrelated entries.
- **Subscription plans:** `plan_selection_screen.dart` now opens with a **current plan** card (status, plan name, deliveries left, next delivery) when the customer is subscribed, followed by the existing plan chooser. Existing screen reused — no new page.
- **Menu:** the drawer item opens the existing catalog screen (category filters + per-item size sheet). No new page.
- **Guest access:** `login_page.dart` gains **Continue without signing in**, which replaces the auth route with the dashboard so the app is browsable without an account.
- **Hosted checkout chrome:** `_ChargebeeCheckoutWebView` now matches the order-checkout contract — explicit back button, back walks the hosted page's own history first, leave-confirmation for an unfinished payment, and a loading progress bar. Payment remains fully in-app (no external browser hand-off).
- **Docs:** `docs/functional-specs/FUNCTIONAL_SPEC.md` §12.5 (navigation, drawer, session entry) and §12.6 (hosted checkout presentation); `docs/ARCHITECTURE_OVERVIEW.md` § Client Navigation & Session.
- **Verification:** `flutter analyze` 0 errors, `flutter test` 418/418. Drawer, Menu, plans page and the guest entry were exercised on the Android emulator against the live backend.

## [2026-10-31] Physical Device Validation

- **Device**: Samsung **SM‑G973W** (Galaxy S20 5G), Android 12 (API 31), 1440×3040, adb over Wi‑Fi at `192.168.1.7:5555`
- **Backend**
  - **Host topology** — `mvn spring-boot:run` on `192.168.1.10:8081` → `Started bmjServer in 9.361 seconds`, health `{"status":"UP"}` — **PASS**
  - **Docker topology** — `bmj-backend:local` built from the repo Dockerfile (503 MB), container `Up (healthy)`, `0.0.0.0:8081->8080` — **PASS**
  - The **same unchanged APK** worked against both topologies
- **Results**: **15 products fetched** from MySQL via the real API; **15 catalog items rendered** (`Successfully fetched 15 items` → `Converted to 15 catalog items`)
- **Google Sign‑In**: **PASS** — native account picker → consent ("Allow Google to sign you in to BookMyjuice") → `✅ Signed in: pbharat.hotwani@gmail.com` → backend recorded `googleEmail=pbharat.hotwani@gmail.com` → `GoogleLinkRequired` (the designed link path for an unlinked identity)
- **Cart persistence**: **PASS** — an added item survived a full app restart (`LoadCart()` → `CartLoaded([CartItem(Carrot Premium, quantity: 1, price: 199.00)])`)
- **Crashes**: **NONE**
- **Render overflows**: **NONE**
- **Environment fixes required**: port 8080 was held by the IDE `AgentService` → backend moved to 8081; Tomcat bound IPv6‑only so the device timed out → restarted with `-Djava.net.preferIPv4Stack=true` + `SERVER_ADDRESS=0.0.0.0` (listener confirmed `0.0.0.0:8081`)
- **Open items surfaced by this run**: debug‑build FCM reports `FIS_AUTH_ERROR` (the release SHA‑1 must be registered in Firebase); most catalog items still return `"prices": 0`, so the UI renders the em dash — that is the Chargebee Price Variants blocker, visible on real hardware
- **Not verifiable yet**: OTP verification (no SMS path), address capture, checkout completion, subscription purchase completion, Google existing‑user and collision paths

## [2026-06-09] Password Strength Upgrade: 1 → 2 Numbers (FLAG-010)
- **Scope**: BRD §4.6, USE_CASES.md, FUNCTIONAL_SPEC.md, app_text_field.dart, sign_up_screen.dart,
  google_signup_screen.dart, create_password_screen.dart, TC_AUTH.md
- **Change**: Password requirement changed from "at least 1 number" → "at least 2 numbers"
- **Regex**: Updated from `(?=.*\d)` to `(?=(?:.*\d){2})` in Flutter validators
- **Documents**: BRD regex updated to `(?=(?:.*\d){2})`, USE_CASES.md "2 numbers" confirmed, FUNCTIONAL_SPEC §3.4 line 215 confirmed
- **Backend**: No regex validation exists on backend (uses @Size(min=8, max=40) only). Backend already accepts any 8+ char password, so this is purely a frontend validation change.
- **Test Cases**: TC-AUTH-037 (special char check) and TC-AUTH-054 (buffer overflow) unaffected.
  TC-AUTH-038 updated description to explicitly mention "2 numbers" requirement.
  TC-AUTH-051 (login) unaffected — server validates credentials, not password format.
  TC-AUTH-052 (forgot password) unaffected — queries by email, not password.
- **UI labels**: All Flutter password requirement lists updated: "1 number" → "2 numbers"