# Release Candidate Checklist

> **This is the primary release document.** It supersedes every status claim in the archived reports.
> **Date:** 2026-10-30 · **Branch:** `lush` → `main` @ `28357c1` · `bmjServer` → `main` @ `1f17048` · parent → `feat/v1-launch-freeze`

## CURRENT STATUS

| Area | State | Evidence |
| :--- | :--- | :--- |
| Tests | ✅ **418 / 418 passing** | `flutter test`, re-run after every commit |
| Static analysis | ✅ **0 errors** | `flutter analyze --no-pub lib`, after every commit |
| Signed AAB | ✅ **82.4 MB**, `CN=BookMyJuice, OU=Beta` | `jarsigner -verify` on `app-release.aab` |
| Signed APK | ✅ 88.6 MB, V2 signer SHA-256 `b58e6f52…` | `apksigner verify --print-certs` |
| Install + launch on device | ✅ Android 14 (API 34) | `adb install` → *Success*, `mCurrentFocus=…MainActivity` |
| Notification permission | ✅ prompt shown, `POST_NOTIFICATIONS: granted=true` | `dumpsys package com.bookmyjuice.app` |
| Release manifest | ✅ `INTERNET` + `POST_NOTIFICATIONS`, **no** cleartext | merged manifest + `aapt2 dump permissions` |
| Release signing | ✅ real upload key wired, debug key no longer used | `RELEASE_SIGNING_CHECK.md` |
| Auth surface | ✅ Google + phone OTP only (password/email removed) | 418 tests, deleted screens |
| UI migrations | ✅ Home, PDP, Cart, Subscription aligned | `_captures/after` + `review` sheets |
| Delivery schedule | ✅ persisted, `nextDeliveryAt` implemented | `DeliveryScheduleServiceTest` (12 cases) |
| Server build | ✅ `mvn -DskipTests -o compile` → exit 0 | run before committing `bmjServer` |
| Repository hygiene | ✅ 12 root docs (was 40), 29 archived, 648 MB pruned | `DOC_INVENTORY.md` |
| Git | ✅ 8 app + 5 server commits, both remotes up to date | `GITHUB_PUSH_REPORT.md` |

## BLOCKERS — five, and only five

| # | Blocker | Owner | Unblocks when | Evidence |
| :-: | :--- | :--- | :--- | :--- |
| **B1** | **Chargebee Price Variants not enabled** on `bookmyjuice-test` | Chargebee support | API returns variants; `preflight` prints AVAILABLE | `preflight` → `"This API operation is not enabled for this site"` |
| **B2** | **Production `API_BASE_URL` undecided** — app defaults to `http://localhost:8080` | Product/ops | a beta HTTPS host is chosen and injected at build time | `PRODUCTION_ENDPOINT_AUDIT.md` §5 |
| **B3** | **Production Chargebee credentials missing** — app/server default to the TEST site and no prod key exists in the repo | Ops | `CHARGEBEE_SITE=bookmyjuice` + prod API key in the environment | `application.properties:5` |
| **B4** | **Real-device validation incomplete** — 1 of 10 scenarios verified | QA | a network-enabled device or emulator + running backend | `DEVICE_QA_RESULTS.md` §1 |
| **B5** | **One-time purchase rollout not executed** — 2 of 45 prices exist | Chargebee/ops | B1 resolved → run the 45-row rollout | census: `charge` prices = 7 |

Subscription checkout is **commercially ready** (300 plan prices) and does not depend on B1.

## HIGH RISK — must be closed before public release

| # | Risk | Detail | Mitigation |
| :-: | :--- | :--- | :--- |
| H1 | **Two signing keystores were committed to git** — now untracked | `lush/keystore_name.jks` (alias `your_alias`) and `lush/clientkeystore` (alias `client`), both PKCS12, both opened with password `android`. Removed from tracking in commit `d4e0ec0` and matched by `.gitignore`; they remain in git history and on disk | **rotate both keys** (they are public forever) and delete the local copies; the new upload key lives outside the repo |
| H2 | **Chargebee MCP keys committed** | `.clinerules/cline-guardrails.md:10,15,17`, `.vscode/mcp.json:20,27`, `docs/CHARGEBEE_MCP.md:15,16` — all **tracked** | rotate both keys in Chargebee, replace with placeholders, decide on history rewrite |
| H3 | **Upload key has no backup** | `X:/BMJ/_secrets/bmj-upload.jks` + `android/key.properties` exist only on this machine | copy both into a password manager today; losing them blocks all future updates |
| H4 | **CI has no release build** | `.github/workflows/ci-cd.yml:222` builds a *debug* APK against `localhost` | add a release job that injects `API_BASE_URL` and asserts the manifest |
| H5 | **Release build can point at localhost** | a build without `--dart-define` silently uses `http://localhost:8080` | add a CI grep guard, then make the default fail fast |

## MEDIUM RISK — acceptable for beta, fix before public scale

| # | Risk | Detail |
| :-: | :--- | :--- |
| M1 | CORS is `addAllowedOriginPattern("*")` | credentials off, so no cookie theft, but any site can call the API |
| M2 | `CHARGEBEE_SITE` defaults to `bookmyjuice-test` | a misconfigured prod deployment would charge the test site |
| M3 | `DB_HOSTNAME` defaults to `localhost` in the prod profile | a missing env var fails on boot rather than connecting to the wrong DB — still worth requiring |
| M4 | Artifact size | 88.6 MB universal APK / 82.4 MB AAB; ship the AAB and let Play split by ABI |
| M5 | Flutter SDK is beta (`3.43.0-0.3.pre`) | pin a stable channel for the ship build |
| M6 | iOS not buildable | no `ios/Podfile`, no macOS host — decide in/out of beta scope |
| M7 | `AD_ID` permission present (Firebase) | declare advertising-ID usage in the Play data-safety form |
| M8 | Orphan `delivery_schedule` rows accumulate | Option A cleanup job proposed, not implemented (`ORPHAN_SCHEDULE_REMEDIATION.md`) |
| M9 | Subscription plan reference wraps to two lines | cosmetic, no data change possible without a short-id policy |

## READY — do not re-open

- Authentication: Google sign-in (new/existing/collision) and phone OTP, password and email flows removed.
- Navigation, theming, typography, spacing and the four migrated screens (Home, PDP, Cart, Subscription).
- Subscription purchase path against Chargebee hosted checkout (validated in `_captures/subscription_checkout`).
- Day-wise delivery schedule persistence and `nextDeliveryAt` projection.
- Release signing, release manifest, signed APK/AAB, install + first-run on Android 14.
- Repository: single checklist, single commit strategy, single screenshot index, one archive folder, no duplicate reports, no junk.

## NEXT ACTIONS — in order

| # | Action | Owner | Blocks | How you know it is done |
| :-: | :--- | :--- | :--- | :--- |
| 1 | Copy `bmj-upload.jks` + `key.properties` values into the team password manager | Release owner | H3 | a second person can restore the file |
| 2 | ~~`git rm --cached keystore_name.jks clientkeystore`~~ **done in `d4e0ec0`** — remaining: rotate both legacy keys and delete the local copies | App dev | H1 | the old keys are revoked in the console and the files are gone from disk |
| 3 | Rotate both Chargebee MCP keys; replace the literals in the three tracked files | App dev | H2 | `git grep test_ai_` returns nothing |
| 4 | Decide the beta API host and inject it: `flutter build appbundle --release --dart-define=API_BASE_URL=https://…` | Product/ops | B2, H5 | `aapt2 dump` build + a device reaches the API |
| 5 | Open the Chargebee Price Variants request (`CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md`) | Ops | B1, B5 | `preflight` prints AVAILABLE |
| 6 | Add a CI release job that injects the URL and asserts the manifest | Devops | H4 | CI produces a signed AAB artifact |
| 7 | Bring up backend + network-enabled device; run `DEVICE_QA_RESULTS.md` §4 for T1–T9 | QA | B4 | 10/10 rows have a real PASS/FAIL |
| 8 | When variants unlock: run the 45-row rollout, then census 7 → 52 | Ops | B5 | `chargebee_catalog_check.py` shows 52 |
| 9 | Set production Chargebee site + key in the deployment environment | Ops | B3 | server boots with `bookmyjuice` |
| 10 | Approve the orphan-schedule Option A job (census → dry-run → live) | Backend | M8 | dry run logs reviewed |

**Definition of "beta-ready":** blockers B1–B5 closed, risks H1–H5 closed, 418 tests green, 0 analyze errors, and a signed AAB whose `API_BASE_URL` points at a reachable HTTPS host.

## Evidence map

| Need | Document |
| :--- | :--- |
| Why each file exists | `DOC_INVENTORY.md` |
| Commit history and grouping | `FINAL_COMMIT_STRATEGY.md`, `GITHUB_PUSH_REPORT.md`, `COMMIT_READINESS.md` |
| Signing detail | `RELEASE_SIGNING_CHECK.md` |
| Bundle artifact detail | `AAB_RELEASE_REPORT.md` |
| Endpoint inventory | `PRODUCTION_ENDPOINT_AUDIT.md`, `CONFIG_CLEANUP_REPORT.md` |
| Device matrix | `DEVICE_QA_RESULTS.md` |
| Chargebee gates + rollout | `CHARGEBEE_BETA_STATUS.md`, `CHARGEBEE_PRICE_VARIANTS_MAPPING.md` |
| Orphan schedules | `ORPHAN_SCHEDULE_REMEDIATION.md` |
| Images | `SCREENSHOT_INDEX.md` |
| Operations | `DEPLOYMENT_RUNBOOK.md` |
| History | `_docs/archive/` |

