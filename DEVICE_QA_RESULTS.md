# Device QA Results — Beta Matrix (T1–T10)

> **Date:** 2026-10-30 · **Device:** `emulator-5554`, Android 14 (API 34), 1080 × 2400
> **Build under test:** release-signed APK from `flutter build apk --release`
> (`CN=BookMyJuice, OU=Beta`, SHA-256 `b58e6f52…`), version `1.0.0+1`
> **Policy:** only failures are expanded; every PASS carries its evidence.

## 1. Environment limits measured before testing

| Check | Result |
| :--- | :--- |
| Emulator attached and online | ✅ `adb devices` → `emulator-5554 device` |
| Emulator network egress | 🔴 **none** — `ping 8.8.8.8` → *1 transmitted, 0 received, 100% packet loss*; `ping bookmyjuice.co.in` → same |
| Backend reachable from the device | 🔴 `bmjServer` is not running locally, and no deployed API host was provided (`API_BASE_URL` was the placeholder `https://api.bookmyjuice.example`) |
| Google account on the emulator | 🔴 none signed in |
| SMS delivery for OTP | 🔴 not available on this emulator |

Because of the first row, **every scenario that needs an HTTP call cannot be verified here**, no matter how the app is configured. Those rows are marked FAIL with `blocked:` and the precise blocker, not passed by omission.

## 2. Matrix

| # | Scenario | Result | Evidence / blocker |
| :-: | :--- | :--- | :--- |
| **T1** | Phone OTP **Sign Up** | **FAIL** — `blocked: no network egress` | requires `POST /api/auth/...` to reach the backend and an SMS; emulator cannot resolve or route any host (measured §1) |
| **T2** | Phone OTP **Sign In** | **FAIL** — `blocked: no network egress` | same as T1 |
| **T3** | Google **New User** | **FAIL** — `blocked: no Google account + no egress` | Google sign-in needs Play Services with a signed-in account and a token exchange with the backend |
| **T4** | Google **Existing User** | **FAIL** — `blocked: no Google account + no egress` | same as T3 |
| **T5** | Google **Collision Flow** | **FAIL** — `blocked: no Google account + no egress` | needs a successful Google token first, then the `GoogleLinkRequired` round trip |
| **T6** | Address Capture | **FAIL** — `blocked: no authenticated session` | unreachable without T1–T4 |
| **T7** | One-Time Purchase | **FAIL** — `blocked: no egress + no Chargebee prices` | cart/checkout needs the API; only 2 of 45 one-time prices exist in Chargebee |
| **T8** | Subscription Purchase | **FAIL** — `blocked: no egress + no backend` | needs `SubscriptionCheckoutService` to mint the Chargebee hosted-page session |
| **T9** | Checkout **Return** Flow | **FAIL** — `blocked: T7/T8 never started` | deep-link/hosted-page return cannot be reached without a session |
| **T10** | **Notifications Permission** | **PASS** | on first launch the Android 14 dialog rendered — “Allow BookMyJuice to send you notifications?” — and after **Allow**: `dumpsys package com.bookmyjuice.app` → `POST_NOTIFICATIONS: granted=true` (and `INTERNET: granted=true`) |

### Also verified (not part of the ten, but part of beta readiness)

| Check | Result | Evidence |
| :--- | :--- | :--- |
| Release APK installs on a clean device | **PASS** | old debug-signed package uninstalled → `adb install -r` → *Success* |
| App launches to its own UI | **PASS** | `mCurrentFocus=com.bookmyjuice.app/.MainActivity`; screenshot `_captures/qa/T0_after_allow.png` shows the cream/orange app surface (mean RGB 238,217,202 with brand-orange pixels present) |
| Doesn’t crash without a backend | **PASS** | process alive 12 s after launch, no `FATAL EXCEPTION` in logcat |

## 3. Evidence inventory

| File | Contents |
| :--- | :--- |
| `_captures/qa/T0_launch.png` | first launch, notification permission dialog |
| `_captures/qa/T0_after_allow.png` | app surface after granting |
| `_captures/qa/ui_launch.xml` | UI Automator dump of the permission dialog (native, readable in release) |
| `_captures/qa/ui_login.xml` | the post-dialog dump (empty: Flutter release builds expose no semantics tree to UI Automator — a tooling limit, not an app bug) |
| `_captures/aab3.out.log` / `.err.log` | bundle build |
| `_captures/apk_signed.out.log` | APK build |

Note on automation: driving Flutter release builds by UI Automator is not viable (no semantics). The reliable route is the repo’s own `integration_test/` suite on a device, which needs a reachable API.

## 4. What unblocks T1–T9 (one order of operations)

1. Bring up the backend: MySQL + `bmjServer` with `DB_HOSTNAME`, `CHARGEBEE_SITE=bookmyjuice-test`, `CHARGEBEE_API_KEY`, `WEBHOOK_USERNAME/PASSWORD`, mail credentials.
2. Give the emulator working egress (host DNS/proxy), and sign a Google account into Play Services for T3–T5.
3. Rebuild with a reachable API and install:
   ```powershell
   flutter build apk --release --dart-define=API_BASE_URL=http://10.0.2.2:8080
   adb install -r build\app\outputs\flutter-apk\app-release.apk
   ```
   (debug manifest keeps cleartext enabled, so plain HTTP to `10.0.2.2` works for QA only.)
4. Run the flows, or drive them from the suite:
   ```powershell
   flutter test integration_test/app_smoke_test.dart -d emulator-5554 `
     --dart-define=E2E=true --dart-define=API_BASE_URL=http://10.0.2.2:8080
   ```
5. For OTP without SMS, use the backend’s test/stub path (or seed a user) rather than weakening auth.

## 5. 2026-10-31 emulator session — stub-backed functional run

The emulator was rebooted (`Pixel_6_API_34`) and its networking had changed: **host loopback is reachable** (`ping 10.0.2.2` → 0% loss) while external internet remains blocked (`8.8.8.8` → 100% loss). That allowed a real functional run against the project's stub API instead of an offline launch.

**Setup:** `python _captures/stub_server.py --port 8099` on the host (binds `127.0.0.1`, reachable from the emulator as `10.0.2.2`) → `flutter build apk --debug --dart-define=API_BASE_URL=http://10.0.2.2:8099` → `adb install -r app-debug.apk`.

| Check | Result | Evidence |
| :--- | :--- | :--- |
| Install + cold launch | **PASS** | `Starting: Intent …MainActivity`, focus on `MainActivity` |
| Notification permission | **PASS** | dialog shown, granted → `POST_NOTIFICATIONS: granted=true` |
| Catalog fetch + JSON parse | **PASS** | logcat: `Fetching charge items from: http://10.0.2.2:8099/api/v1/catalog/charge-items` → `Successfully fetched 6 items`; `ProductCatalogLoaded` with 6 items × 3 prices, sizes `[200ml, 300ml, 500ml]`, categories `[Delight, Premium, Signature]` |
| Home render | **PASS** | screenshot `emu_01_home.png`: header, greeting, plan card + CTA, 3-tile stat strip, section header, 2-column grid, bottom nav |
| PDP navigation + hero | **PASS** | tap on a tile → `emu_02_pdp.png`: full-bleed hero, overlapping title card, pinned CTA |
| Size sheet | **PASS** | `emu_03_after_add.png`: sheet with options and confirm CTA |
| Add to cart | **PASS** | logcat: `AddToCart(CartItem(Carrot Premium, quantity: 1, price: 199.00))` → `CartLoaded([...])` |
| Cart persistence across restart | **PASS** | after force-relaunch: `LoadCart()` → `CartLoaded([CartItem(Carrot Premium, quantity: 1, price: 199.00)])` |
| Cart screen render | **PASS** | `emu_06_cart.png`: item row with thumbnail, address selector, order-summary panel, pinned checkout CTA |
| Subscription tab | **PASS** | `emu_07_subscription.png`: empty state with CTA, third nav item highlighted (no plan on the stub) |
| Stability | **PASS** | no `FATAL EXCEPTION`, no `E/flutter`, no `FlutterError`, no `RenderFlex overflow` in the whole session; process alive throughout |

**Still unverified after this session:**

| Scenario | Why |
| :--- | :--- |
| T1/T2 phone OTP sign-up/sign-in | the stub has no auth endpoints; external network is blocked, so no OTP can be sent |
| T3–T5 Google new/existing/collision | no Google account on the emulator, no external egress |
| T6 address capture | requires an authenticated session |
| T7 checkout completion | add-to-cart and cart are verified; the Chargebee hosted page needs a backend session + egress |
| T8/T9 subscription purchase and return | same |

The debug build was used because release builds block cleartext HTTP; the release binary's install/launch/permission behaviour is already recorded in §2.

**Artifacts:** `_captures/qa/emu_01_home.png` … `emu_07_subscription.png` (7 screenshots) and `perm_dialog.xml`.

## 6. Conclusion (updated after the 2026-10-31 run)

The picture is materially better than §2's first pass, and still incomplete:

- **Verified on a device:** install, cold launch, notification permission, catalog fetch + parse, Home render, PDP navigation, size sheet, add-to-cart, cart persistence across a restart, cart render, subscription empty state, and session-wide stability (no fatal errors, no overflows).
- **Still blocked:** the six scenarios that need real authentication and external egress — phone OTP (T1/T2), Google new/existing/collision (T3–T5), address capture (T6), and checkout completion (T7–T9).

So: **5 device-side behaviours pass outright** (T10 plus the install/render/cart path), and the rest remain environment gates rather than product findings. Everything that could be exercised without a backend has now been exercised.

