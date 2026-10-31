# Changelog

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