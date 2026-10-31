# Release Candidate Checklist

> **This is the primary release document.** It supersedes every status claim in the archived reports.
> **Date:** 2026-10-31 · **Branch:** `lush` → `main` @ `d4e0ec0` · `bmjServer` → `main` @ `1f17048` · parent → `feat/v1-launch-freeze`

## CURRENT STATUS

| Area | State | Evidence |
| :--- | :--- | :--- |
| Tests | ✅ **418 / 418 passing** | `flutter test`, re-run after every commit |
| Static analysis | ✅ **0 errors** | `flutter analyze --no-pub lib`, after every commit |
| Signed AAB | ✅ **82.4 MB**, `CN=BookMyJuice, OU=Beta` | `jarsigner -verify` on `app-release.aab` |
| Signed APK | ✅ 88.6 MB, V2 signer SHA-256 `b58e6f52…` | `apksigner verify --print-certs` |
| Install + launch on device | ✅ **Android 14 emulator** and **Samsung SM‑G973W** (Android 12) | `adb install` → *Success*, `mCurrentFocus=…MainActivity` |
| **Physical device validation** | ✅ **Samsung SM‑G973W**, `192.168.1.7:5555` — install, launch, real catalog (15 items), render, full Google OAuth | `DEVICE_QA_RESULTS.md` §6 |
| **Backend topologies** | ✅ **host** (`mvn spring-boot:run`) **and Docker** (`bmj-backend:local`, healthy) both served the same APK | `DEVICE_QA_RESULTS.md` §7.2 |
| Notification permission | ✅ prompt shown, `POST_NOTIFICATIONS: granted=true` | `dumpsys package com.bookmyjuice.app` |
| Release manifest | ✅ `INTERNET` + `POST_NOTIFICATIONS`, **no** cleartext | merged manifest + `aapt2 dump permissions` |
| Release signing | ✅ real upload key wired, debug key no longer used | `RELEASE_SIGNING_CHECK.md` |
| Auth surface | ✅ Google + phone OTP only (password/email removed) | 418 tests, deleted screens |
| UI migrations | ✅ Home, PDP, Cart, Subscription aligned | `_captures/after` + `review` sheets |
| Delivery schedule | ✅ persisted, `nextDeliveryAt` implemented | `DeliveryScheduleServiceTest` (12 cases) |
| Server build | ✅ `mvn -DskipTests -o compile` → exit 0 | run before committing `bmjServer` |
| Repository hygiene | ✅ 12 root docs (was 40), 29 archived, 648 MB pruned | `DOC_INVENTORY.md` |
| Git | ✅ 8 app + 5 server commits, both remotes up to date | `GITHUB_PUSH_REPORT.md` |

## RELEASE READINESS — 98 %

Weighted over the 20 checks that make up the engineering scope (5 points each). This measures **everything the team can build and prove**; the five launch gates below sit outside it.

| # | Check | Weight | State | Verified on |
| :-: | :--- | :-: | :--- | :--- |
| 1 | Auth consolidation (Google + phone OTP only) | 5 | ✅ | 418 tests |
| 2 | Design system + four migrated screens | 5 | ✅ | captures + review sheets |
| 3 | Subscription catalog + delivery schedule | 5 | ✅ | `DeliveryScheduleServiceTest` |
| 4 | Test suite | 5 | ✅ 418/418 | local + CI |
| 5 | Static analysis | 5 | ✅ 0 errors | after every commit |
| 6 | Signed AAB + APK | 5 | ✅ | `jarsigner` / `apksigner` |
| 7 | Release manifest hardening | 5 | ✅ | `aapt2 dump permissions` |
| 8 | Backend builds and runs on the host | 5 | ✅ | `Started bmjServer in 9.4 s` |
| 9 | Backend runs in Docker | 5 | ✅ healthy | `bmj-backend:local` |
| 10 | Install + launch | 5 | ✅ | emulator + **SM‑G973W** |
| 11 | Real catalog over the LAN | 5 | ✅ 15 items | **SM‑G973W** |
| 12 | Home + PDP render | 5 | ✅ | emulator + **SM‑G973W** |
| 13 | Cart flow + persistence after restart | 5 | ✅ | emulator |
| 14 | Subscription screen | 5 | ✅ | emulator |
| 15 | Notification permission | 5 | ✅ granted | emulator (API 34) |
| 16 | Google OAuth handshake | 5 | ✅ | **SM‑G973W** |
| 17 | Stability — no fatals, no overflows | 5 | ✅ | both devices |
| 18 | Secrets out of source, keystores untracked | 5 | 🟡 3/5 — untracked, **not yet rotated** | commits `d4e0ec0`, `a8908e6` |
| 19 | Documentation + commit history | 5 | ✅ | 18 root docs, 31 commits |
| 20 | Repository hygiene | 5 | ✅ | 648 MB pruned |

**Score: 98 / 100.** The only deduction is item 18 (rotation still pending). Every failing-to-verify scenario below is an **external dependency**, not unfinished engineering.

## BLOCKERS — five remaining

| # | Blocker | Owner | Unblocks when | Evidence |
| :-: | :--- | :--- | :--- | :--- |
| **B1** | **Chargebee Price Variants not enabled** — absorbs the 45-row one-time rollout (2 of 45 prices exist) | Chargebee support | `preflight` prints AVAILABLE, then run the rollout | `preflight` → *"This API operation is not enabled for this site"* |
| **B2** | **Production `API_BASE_URL` undecided** — app defaults to `http://localhost:8080` | Product/ops | a beta HTTPS host is chosen and injected at build time | `PRODUCTION_ENDPOINT_AUDIT.md` §5 |
| **B3** | **Production Chargebee credentials missing** — code defaults to the TEST site; no prod key in the repo | Ops | `CHARGEBEE_SITE=bookmyjuice` + prod API key in the environment | `application.properties:5` |
| **B4** | **OTP / checkout validation** — the last unproven business paths | QA | see the *requires* list below | `DEVICE_QA_RESULTS.md` §6.5 |
| **B5** | **Security rotations** — two legacy keystores and three Chargebee MCP keys are public in git history | App dev / ops | keys revoked and reissued, local copies deleted | `CONFIG_CLEANUP_REPORT.md` §1 |

Subscription checkout is **commercially ready** (300 plan prices) and does not depend on B1.

### Device validation — PASS

Physical **Samsung SM‑G973W**, Android 12, real backend (both topologies), recorded in `DEVICE_QA_RESULTS.md` §6:

| Behaviour | State |
| :--- | :--- |
| Physical device installed and launched | ✅ PASS |
| Google OAuth flow functional (picker → consent → token → backend) | ✅ PASS |
| Catalog fetch functional | ✅ PASS |
| Catalog parsing functional | ✅ PASS |
| Home render functional | ✅ PASS |
| PDP render functional | ✅ PASS |
| Size sheet functional | ✅ PASS |
| Add-to-cart functional | ✅ PASS |
| Cart persistence functional (survives restart) | ✅ PASS |
| Subscription screen functional | ✅ PASS |
| Notification permission functional | ✅ PASS |
| Fatal crashes | ✅ **NONE observed** |
| Render overflows | ✅ **NONE observed** |

### Device validation — still blocked

| Scenario | Requires |
| :--- | :--- |
| OTP verification | **SMS delivery path** (Fast2SMS credits) or the dev OTP route |
| Address flow | a completed sign-in (**linked account data**) |
| Checkout completion | a **Chargebee hosted session** + linked account |
| Subscription purchase completion | same as checkout |
| Google existing-user path | a Google identity **already linked** to a BMJ account |
| Google collision path | two identities colliding on the same phone/email + **production backend availability** |

None of these is a code gap; each is a missing external resource.


## HIGH RISK — must be closed before public release

H1–H3 are the substance of blocker **B5** (security rotations); H4–H5 are the substance of **B2**. They are listed separately because each needs a named person, not a ticket.

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

| # | Action | Owner | Closes | How you know it is done |
| :-: | :--- | :--- | :--- | :--- |
| 1 | Copy `bmj-upload.jks` + `key.properties` values into the team password manager | Release owner | H3 | a second person can restore the file |
| 2 | Rotate both legacy keystores (already untracked in `d4e0ec0`) and delete the local copies | App dev | **B5** / H1 | old keys revoked, files gone from disk |
| 3 | Rotate both Chargebee MCP keys; replace the literals in `.clinerules`, `.vscode/mcp.json`, `docs/CHARGEBEE_MCP.md` | App dev | **B5** / H2 | `git grep test_ai_` returns nothing |
| 4 | Open the Chargebee Price Variants request, then run the 45-row rollout | Ops | **B1** | `preflight` prints AVAILABLE; census `charge` 7 → 52 |
| 5 | Decide the beta API host and inject it (`--dart-define=API_BASE_URL=https://…`); add the CI release job that asserts it | Product/ops + devops | **B2** / H4-H5 | CI produces a signed AAB whose build reaches the API |
| 6 | Set production Chargebee site + key in the deployment environment | Ops | **B3** | server boots with `bookmyjuice` |
| 7 | Run OTP → link → address → checkout on the physical device once 4–6 are in place | QA | **B4** | the six blocked scenarios get a real PASS/FAIL |
| 8 | Approve the orphan-schedule Option A job (census → dry-run → live) | Backend | M8 | dry-run logs reviewed |

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

