# Device Test Report

**Date:** 2026-11-19 · **Device:** `192.168.1.7:5555` (ADB over Wi-Fi)
**Build tested:** Flutter release `arm64-v8a`, `--dart-define=API_BASE_URL=https://api.bookmyjuice.co.in`
**Evidence:** screenshots in `_captures/qa/`, `adb logcat`, nginx access log, Spring Boot log

---

## 1. Device baseline

| Property | Value |
|---|---|
| Model | **SM_G973W** (Galaxy S10 5G), codename `beyond1q` |
| Android | **12** |
| Screen | 1440 × 3040 physical, **override 1080 × 2280** |
| Battery at start | **29 %** |
| Storage | 109 GB total, **100 % used — 814 MB free** at start |
| ADB transport | `device`, transport_id 3, Wi-Fi |

The device is effectively full. This directly affected installation (§2) and is worth fixing before
future runs: a debug APK is 222 MB and needs roughly 2–3× that in free space to install.

## 2. Preparation and installation

| Step | Result |
|---|---|
| Clear previous app state | `adb uninstall com.bookmyjuice.app` → **Success** (also freed ~300 MB) |
| Install debug build (222.4 MB) | **FAILED** — `INSTALL_FAILED_INSUFFICIENT_STORAGE` |
| Build footprint-reduced artefact | `flutter build apk --release --split-per-abi` → `app-arm64-v8a-release.apk` **34.8 MB** |
| Install release build | **Success** |
| Free space after uninstall | 1.1 GB |

The previously installed build was `versionName=1.0.0`, last updated **2026-11-05** — i.e. it predates
this deployment and was not pointed at the VPS. It was replaced deliberately, and the replacement was
signed with the upload key (a debug-signed install could not be upgraded in place).

## 3. Phase 1 — application launch: **PASS**

| Check | Evidence |
|---|---|
| Process starts | `am start -n com.bookmyjuice.app/.MainActivity` → `Starting: Intent { cmp=com.bookmyjuice.app/.MainActivity }` |
| Window focused | `mCurrentFocus=Window{… com.bookmyjuice.app/com.bookmyjuice.app.MainActivity}` |
| Flutter engine up | logcat: `Using the Impeller rendering backend (Vulkan)` and `(OpenGLES)` |
| Services initialised | logcat: `Initializing GoogleSignIn…`, `GoogleSignIn initialized`, `FlutterFirebaseMessagingBackgroundService started!` |
| Fresh install state | logcat: `FlutterSecureStorage: No data found in EncryptedSharedPreferences.` (no stale session) |
| Screen is real UI, not blank | `e2e_01_launch.png` — 1080×2280, mean luminance **30.2**, std **45.0**, **47** coarse colour buckets, bright band at the bottom (62.2) consistent with a nav bar |

**No crash, no ANR, no blank screen.** No `FATAL EXCEPTION` in logcat.

## 4. Phase 2 — catalogue from the real device: **PASS**

The strongest evidence available, because it is logged independently on both sides:

| Side | Evidence |
|---|---|
| **Device → server** | nginx: `223.190.85.230 … "GET /api/v1/catalog/charge-items HTTP/1.1" 200 8022 "-" "Dart/3.12 (dart:io)"` at 15:42:00 UTC (two calls) |
| **Server processing** | Spring log 21:11:53 IST (= 15:41 UTC): `Securing GET /api/v1/catalog/charge-items` → `Secured` → `ItemService - Filtered to 20 CHARGE items out of 176 total items` |
| **Chargebee upstream** | the 176 items and the 20 charge items come from the live Chargebee catalogue read |

So: categories/products/pricing are served from the VPS over HTTPS to the physical device, and the
catalogue endpoint returns **200 with 8 022 bytes**.

Screenshot: `_captures/qa/e2e_01_launch.png`.

## 5. Phases 3–10 — status

| Phase | Status | Reason (evidence, not assumption) |
|---|---|---|
| 3 OTP login | **BLOCKED** | `FAST2SMS_API_KEY` is **absent** on the server, so no SMS is sent. The API can generate and log an OTP (console fallback), but "SMS received on the device" is impossible. Completing login by reading the console OTP would fake the criterion |
| 4 Google login | **BLOCKED (policy)** | The device's only Google identity is Bharat's personal account, which the QA policy forbids; no QA Google account exists on the device and cannot be created from here |
| 5 Profile / session / logout | **NOT REACHABLE** | requires a logged-in session, which phases 3–4 could not establish |
| 6 Chargebee subscription | **NOT ATTEMPTED** | no QA BMJ user exists, and creating a subscription would create real billing records in the live Chargebee account — needs explicit approval |
| 7 Webhook validation | **FAIL** | see `WEBHOOK_VALIDATION_REPORT.md`: Chargebee delivers, server answers **401** (5 attempts), `webhook_events` = 0 |
| 8 Identity self-heal | **NOT EXERCISED** | needs at least one BMJ user; production has **0** |
| 9 Email | **BLOCKED** | `MAIL_PASSWORD=not-configured-email-disabled` — SMTP cannot authenticate |
| 10 Order flow | **PARTIAL** | catalogue loads, so item browsing is reachable; add-to-cart/checkout needs an authenticated session and was not reached |

## 6. Log hygiene

| Check | Result |
|---|---|
| `FATAL EXCEPTION` / crash | **none** |
| ANR | **none** |
| `SocketException` / connection failure from the app | **none** — the catalogue call returned 200 |
| Backend 5xx caused by the app | **none** — the only 5xx in the log are my own webhook probes with fabricated event ids |

## 7. What a future run needs

1. Free at least 3 GB on the device (or keep using `--split-per-abi` release builds, 35 MB).
2. Provision `FAST2SMS_API_KEY` so the OTP arrives by SMS.
3. Add a QA Google account to the device for phase 4.
4. Fix the Chargebee webhook password (`WEBHOOK_VALIDATION_REPORT.md` §6) so phases 7 and 8 are
   testable at all.
5. Decide whether QA subscriptions may be created in the live Chargebee site (phase 6).
