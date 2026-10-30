# Launch Hardening Sprint

> **Date:** 2026-10-30 · **Scope:** device validation, Chargebee rollout, commit plan,
> metadata gaps, orphan-schedule cleanup.
> **Rules observed:** no UI redesign, no new components, no new screens, no architecture
> or business-logic changes. Every claim below is measured in this environment.

## 0. Verdict at a glance

| # | Area | State | Owner action |
| :-: | :--- | :--- | :--- |
| 1 | Device validation | 🟡 **One tier runnable** — Android 14 (API 34) emulator is attached; no physical device, no iOS | Buy/attach device tiers T1–T5 |
| 2 | Chargebee rollout | 🔴 **Blocked externally** — price-variant API not enabled on the site | Chargebee support ticket |
| 3 | Commit plan | 🟢 **Ready** — 7-commit sequence defined below | Review + land |
| 4 | Metadata gaps | 🔴 **4 release blockers**, 2 fixed today, 2 need human decisions | Rotate key, set prod URL |
| 5 | Orphan schedules | 🟡 **Proposal only** — every abandoned checkout leaves a row; no cleanup exists | Approve job + owner |

**Fixed in this sprint** (verified: `flutter analyze` 0 errors, `flutter test` 418/418):

1. `INTERNET` permission added to the **release** manifest (it existed only in debug/profile — a release build had no network at all).
2. `POST_NOTIFICATIONS` declared (Android 13+ cannot show FCM notifications without it).
3. `usesCleartextTraffic="true"` removed from the release manifest; kept only in debug/profile for local HTTP QA.
4. Hardcoded Chargebee test key removed from `lib/config/api_config.dart` (it was dead code — nothing read `ChargebeeConfig.apiKey`).

---

## 1. Real device validation matrix

### 1.1 What this environment can actually run (measured)

| Device | ID | Status |
| :--- | :--- | :--- |
| Android 14, API 34 | `emulator-5554` | ✅ available |
| Windows desktop | `windows` | ✅ available |
| Chrome 156 / Edge 155 | `chrome`, `edge` | ⚠️ app cannot run on web (`dart:io` data layer, Firebase bootstrap) |

Toolchain: **Flutter 3.43.0-0.3.pre, channel beta**. A beta SDK in a launch build is a risk worth recording — pin a stable release for the ship build.

Build facts: `applicationId com.bookmyjuice.app`, `version 1.0.0+1`, `minSdk 24`, **`targetSdk 36`** (both read from the merged release manifest this sprint). iOS: `Runner.xcodeproj` + `Info.plist` exist but there is **no `Podfile`**, so iOS cannot build until pods are set up (and no macOS host exists here).

**Verified this sprint:** the merged *release* manifest at `build/app/intermediates/merged_manifests/release/processReleaseManifest/AndroidManifest.xml` now declares `INTERNET` and `POST_NOTIFICATIONS`, and declares **no** `usesCleartextTraffic` (platform default: blocked for targetSdk ≥ 28).

Artifact check — a release build was produced and inspected:

```
flutter build apk --release --dart-define=API_BASE_URL=https://…
→ Built build\app\outputs\flutter-apk\app-release.apk (88.6MB, 754.5s)

aapt2 dump permissions app-release.apk
package: com.bookmyjuice.app
uses-permission: android.permission.INTERNET            ← was missing before
uses-permission: android.permission.POST_NOTIFICATIONS  ← was missing before
uses-permission: android.permission.ACCESS_NETWORK_STATE
uses-permission: android.permission.WAKE_LOCK
uses-permission: com.google.android.gms.permission.AD_ID
…
```

Two follow-ups from that artifact: ship an **AAB** (88.6 MB is a fat all-ABI APK), and declare `AD_ID` usage in the Play data-safety form.

### 1.2 The matrix

| Tier | Device / OS | Size & scale | Must prove | Runnable here |
| :--- | :--- | :--- | :--- | :--- |
| **T0** Smoke | API 34 emulator | 390 × 844 @ 1.0 | install, Google sign-in, phone OTP, catalog, PDP → size sheet → cart, checkout handoff, subscription + day schedule, push | ✅ now |
| **T1** Small phone | 360 × 640, API 26 | 360 × 640 @ 1.0 / 1.3 | no overflow on shell, PDP, cart, subscription (layout baseline is 390) | ❌ no device |
| **T2** Baseline | 390 × 844, API 30 | @ 1.0 | the reference canvas: every screen matches the captures | ❌ no device |
| **T3** Large | 430 × 932, API 34 | @ 1.0 / 2.0 | large type does not clip the header, nav, CTAs | ❌ no device |
| **T4** Newest OS | API 35/36 (Android 15/16) | — | POST_NOTIFICATIONS prompt, edge-to-edge / gesture nav, target-sdk behaviour | ❌ no device |
| **T5** Tablet / foldable | 600 × 960 | @ 1.0 | no crash, content centred, nav reachable (not a design target) | ❌ no device |
| **T6** iOS | 17/18 | — | — | ❌ blocked: no Podfile, no macOS |

### 1.3 Cross-cutting checks, run at every tier

Font scale **1.0 / 1.3 / 2.0** (no automated text-scale coverage exists — measured below), dark **and** light theme, cold start vs warm start, airplane mode, 3G-throttled network, background/foreground during checkout, process death during the Chargebee hosted page, notification permission denied, deep link into PDP/cart.

### 1.4 What automated coverage exists — and where it stops

| Layer | Count | Limitation |
| :--- | :--- | :--- |
| Widget/unit tests | **418 passing** | PDP and subscription tests use 780×3200 / 800×4000 viewports (tall canvases, not device sizes); **zero `textScaler` or `setSurfaceSize` usage** anywhere |
| Integration tests | 9 files (`app_smoke_test`, `full_e2e_test`, `fullstack_auth_and_pricing_test`, `subscription_flow_test`, `cart_test`, `subscription_card_test`, `simple_e2e_test`, `e2e_suite_test`, `physical_device_template_test`) | need a running API on `:8080` |
| Patrol | 1 bundle (`patrol_test/test_bundle.dart`) | needs a device |
| Golden captures | 8 (dark + light × 4 screens) | renders the widget tree, not OS chrome/IME/notifications |

So tiers T1–T5 are **manual** work: text scaling and small-screen overflow are not covered by any automated test today.

### 1.5 Commands to run the tiers that are possible here

```powershell
cd X:\BMJ\lush
flutter test                                                             # 418
flutter build apk --release --dart-define=API_BASE_URL=https://<prod-api> # proves the manifest fix ships
flutter test integration_test/app_smoke_test.dart -d emulator-5554       # needs the API on :8080
# font scale on the attached emulator:
adb -s emulator-5554 shell settings put system font_scale 1.30
adb -s emulator-5554 shell am force-stop com.bookmyjuice.app
adb -s emulator-5554 shell monkey -p com.bookmyjuice.app -c android.intent.category.LAUNCHER 1
```

### 1.6 Exit criteria for this workstream

T0 green with a release build; T1 and T3 green at font scale 1.3 (overflow-free); T4 notification prompt observed; T6 either scoped out explicitly or pods added and a macOS runner booked.

---

## 2. Chargebee rollout readiness

### 2.1 Live census (measured today, read-only, TEST site)

| Item type | Count | Range |
| :--- | ---: | :--- |
| `plan` prices | **300** | ₹16 – ₹10,776 — day 91, month 149, week 56, year 4 |
| `charge` (one-time) prices | **7** | ₹89 – ₹500 |
| `addon` prices | 9 | ₹21 – ₹500 |

Integrity: **0** zero-or-negative prices, **0** non-INR prices.

Storefront delta: only **2 of the 45** one-time rows exist — `bmj-item-mix-punch-200ml` (₹129.00) and `bmj-item-bloody-red-200ml` (₹156.09). The other 13 products return an empty `prices[]`, which the UI renders as the em-dash fallback.

### 2.2 The gate is still red (measured)

```
python _captures/chargebee_price_rollout.py preflight
→ price variants: NOT AVAILABLE on this site
  Chargebee: "This API operation is not enabled for this site.
              Please contact support@chargebee.com to get this enabled"
→ Nothing was written. The rollout stays paused.
```

### 2.3 Gate-by-gate state (the five mandatory conditions)

| Gate | Requirement | State today |
| :--- | :--- | :--- |
| `M-1` | Explicit human authorisation to **write** | ❌ not granted; this sprint used read-only access only |
| `M-2` | Canary row created and read back | 🟢 **effectively done** — `bmj-item-mix-punch-200ml` exists at ₹129.00; re-verify readback before batching |
| `M-3` | Corrected payload shape | 🟡 prepared for the flat shape; the **variant** shape needs the mapping re-cut for size variants |
| `M-4` | Post-creation census verification | 🟢 tool ready (`chargebee_catalog_check.py`) with expected deltas below |
| `M-5` | Rollback named before writing | 🟡 mechanism clear (delete the 45 new price ids), **owner unnamed** |

### 2.4 What is chargeable today, without the rollout

| Flow | Works now? | Why |
| :--- | :--- | :--- |
| Weekly / monthly / daily subscriptions | ✅ yes | 300 plan prices are complete and period-correct |
| One-time purchase | 🟡 2 of 15 products | only two `charge` prices exist |
| Cart totals | ✅ yes | Chargebee computes tax/delivery; the app shows the subtotal it holds |
| PDP price display | 🟡 em dash where unpriced | honest fallback by design |

### 2.5 Unblock sequence (each step has a proof command)

1. **Chargebee support** enables Price Variants on `bookmyjuice-test` (dashboard: Settings → Configure Chargebee → Product Catalog → Price Variants). External SLA — the only true blocker.
2. `python _captures/chargebee_price_rollout.py preflight` → must print variants **AVAILABLE**.
3. Re-read the canary (`bmj-item-mix-punch-200ml`) and confirm ₹129.00.
4. Run the gated batch for the remaining 44 rows.
5. `python _captures/chargebee_catalog_check.py` → expect `charge` prices **7 → 52**, items with zero prices **15 → 0**, 0 rows outside the 15 target ids.
6. Storefront probe: every product returns **3** sizes with prices.

### 2.6 Server configuration (verified in `application.properties`)

`chargebee.site=bookmyjuice-test` (TEST), API key from `CHARGEBEE_API_KEY`, startup sync on (batch 50, pool 3, 30-minute timeout), webhook basic auth via `WEBHOOK_USERNAME`/`WEBHOOK_PASSWORD`, MySQL datasource. **No production site value exists in the repo yet** — going live also needs `chargebee.site=bookmyjuice`, a prod key and a separate webhook secret.

---

## 3. Commit plan

### 3.1 Inventory (measured)

`git status`: **88 modified, 22 deleted, 30 untracked**. Four entries are junk and must not be committed: `build_clean.err`, `build_fix.err`, `build_profile.err`, `build_run.err` (`.gitignore` covers `*.log` and `/build/` only).

### 3.2 Sequence — seven commits, in this order

| # | Commit | Contents | Why here | Verify |
| :-: | :--- | :--- | :--- | :--- |
| **C1** | `chore(security): release manifest + remove committed secrets` | `main/debug/profile AndroidManifest.xml`, `api_config.dart` key removal, `.gitignore` (+`*.err`, `*.jks`), `git rm --cached keystore_name.jks` | Nothing else matters until the app can build and reach a network in release | `flutter build apk --release`; analyze 0 |
| **C2** | `feat(design-system): vibrant_zest tokens, widgets, typography` | 16 new `lib/widgets/bmj_*`, `lib/theme/*`, `lib/utils/price_utils.dart`, `test/theme/no_raw_white_test.dart`, `test/widget/bmj_design_system_test.dart` | Foundation for every later UI file | 418 |
| **C3** | `feat(auth): Google + phone OTP only` | 20 deleted screens/services (`forgot_password*`, `email_*`, `phone_login_screen`, `sign_up_screen`, `subscription_service_v2`, `modify_schedule_screen`), `auth_bloc`, `auth_state`, `main.dart` routes, `login_page_test`, `auth_no_password_test`, `phone_entry_screen_test` | Needs C2's widgets | 418 + `mvn test` |
| **C4** | `feat(subscription): day-wise delivery schedule` | `DeliveryScheduleEntity/Repository/Service`, `SubscriptionCheckoutService`, `SubscriptionApiService`, `SubscriptionController`, `DeliveryScheduleServiceTest` (12 cases), client `subscription_service`, `subscription_summary_screen`, `size_selection_sheet`, `subscription_tab` | Touches `main.dart` only trivially | `mvn test`; 418 |
| **C5** | `feat(catalog): filtered-empty state + price formatting` | `product_catalog_bloc` (+`ProductCatalogFiltered`), its test, `item_card_view`, `menu_tab` | Small and isolated | 418 |
| **C6** | `style: dart format (mechanical only)` | the formatter pass over `lib/` | Kept **separate** so reviewers can skip it (`git show <sha> --ignore-all-space --stat` → 0) | analyze 0 |
| **C7** | `docs: visual audit, review, hardening sprint` | `VISUAL_ALIGNMENT_AUDIT.md`, `VISUAL_REVIEW.md`, `LAUNCH_HARDENING_SPRINT.md`, `_captures/*` | Last, no runtime impact | — |

### 3.3 Rules

- **Do not squash C2–C5.** Each is independently revertible, which is what makes a launch-week rollback possible.
- C6 stays out of the functional commits so no reviewer reads 5,500 lines of rewrapping.
- Every commit must pass `flutter analyze` (0 errors) and `flutter test` (418) on its own.
- C1 is the only commit that must also be smoke-tested on a device: it is the one that decides whether a release build has network.

---

## 4. Metadata gap analysis

Two different gaps get called "metadata"; both block launch in different ways.

### 4.1 Product metadata — what the UI asks for and the catalog cannot answer

| Field the UI wants | Would drive | Present in data? | Consequence today |
| :--- | :--- | :--- | :--- |
| Attribute tags (`organic`, `cold-pressed`, `vegan`) | PDP's second badge | ❌ only one `category` per item | one badge instead of the reference's two |
| Hero image set (multiple angles) | PDP carousel that peeks from both edges | ❌ one `imagePath` per item | single static photo |
| Per-size imagery | cart thumbnails matching the chosen size | ❌ | one image regardless of size |
| Savings / discount policy | cart savings row figure, PDP "save 15%" | ❌ Chargebee computes at checkout | row exists with an em dash |
| Promo eligibility | promo field | ❌ | no field (a dead control would be worse) |
| Line-item recurrence flag | cart's "Weekly" badge | ❌ `CartItem` has item/quantity/size/customizations/selectedPrice only | no badge |
| Tax / delivery amounts | cart totals | ❌ Chargebee-owned | "At checkout" |
| Short plan reference | subscription card header on one line | 🟡 id is full-length | wraps to two lines |

Available and *used*: `kacl` (nutrition panel), `servingSize`, `ingredients` (list), `rating`, `itemPrices[].{name,price}`, `startColor`/`endColor`, `category`.

**What this means:** the remaining visual-parity items are not UI work — they are catalog-schema work. Populating `metadata` (already a `Map` on `Item`) with attribute flags plus a per-size image field would close four of the eight rows above without touching a widget.

### 4.2 Release metadata — what ships with the binary

| Item | State before this sprint | State now | Action |
| :--- | :--- | :--- | :--- |
| `INTERNET` in release manifest | ❌ absent (debug/profile only) | ✅ **fixed** | re-build APK and confirm |
| `POST_NOTIFICATIONS` (Android 13+) | ❌ absent | ✅ **fixed** | verify prompt on API 34/35 |
| Cleartext HTTP in release | ❌ `usesCleartextTraffic="true"` | ✅ **removed** (debug/profile keep it for local QA) | — |
| Chargebee test key in source | ❌ hardcoded default | ✅ **removed** (was dead code) | rotate the key — it is in git history |
| `keystore_name.jks` | 🔴 **tracked in git** (2,752 bytes) | unchanged | `git rm --cached`, add to `.gitignore`, generate a new upload key, rotate |
| Release signing | 🔴 `build.gradle.kts:40` uses `signingConfig = signingConfigs.getByName("debug")` — the tracked keystore is not wired in at all | unchanged | create `key.properties` + a real `signingConfigs.release`, keep it out of git, then sign with a Play upload key |
| API base URL | 🔴 defaults to `http://localhost:8080` / `http://127.0.0.1:8080` | unchanged | CI must pass `--dart-define=API_BASE_URL=https://…`; assert it in the release build |
| iOS build | 🔴 no `ios/Podfile` | unchanged | scope out, or add pods + a macOS runner |
| Version | `1.0.0+1` | unchanged | decide versionCode strategy before the first upload |
| Flutter channel | `3.43.0-0.3.pre` (beta) | unchanged | pin a stable SDK for the ship build |
| Store listing (title, screenshots, privacy, data-safety form) | ❌ not in repo | unchanged | owner outside this repo |

---

## 5. Orphan schedule cleanup proposal

### 5.1 How rows are created (measured in code)

`SubscriptionCheckoutService` calls `DeliveryScheduleService.reserve(customerId, schedule)`, which

1. mints an id — `"bmj" + UUID(32 hex)`,
2. **writes the row immediately** (`delivery_schedule`, PK `subscription_id`),
3. hands that id to Chargebee as `subscription[id]` and returns it to the client.

The `subscription_created` webhook then joins the schedule back by that exact id. There is **no delete path anywhere in the flow** (verified: `DeliveryScheduleRepository` is only ever read), and the server has **no `@Scheduled`/`@EnableScheduling`** infrastructure at all. So every checkout that is abandoned after the row is written leaves a permanent orphan.

### 5.2 Orphan classes

| Class | What it is | Volume | Harm |
| :--- | :--- | :--- | :--- |
| **A** | Reserved, checkout abandoned — no Chargebee subscription exists | one row per abandoned checkout (highest) | dead rows accumulate forever; no user-visible effect |
| **B** | Subscription cancelled/expired but schedule remains | one per churn | none today — `canPromiseDelivery(status)` already gates delivery promises |
| **C** | Retries: the same customer reserves N ids, only one converts | N-1 per re-attempt | dead rows; also confuses naive "latest row per customer" analysis |

### 5.3 Proposal — three phases, none of them code in this sprint

**Phase 1 — census first (read-only, safe today).** Size the problem before deleting anything:

```sql
-- rows older than 48 h (class A candidates, upper bound)
SELECT COUNT(*) FROM delivery_schedule
WHERE created_at < UNIX_TIMESTAMP(NOW()) - 172800;

-- age distribution
SELECT FLOOR((UNIX_TIMESTAMP(NOW()) - created_at)/86400) AS age_days, COUNT(*)
FROM delivery_schedule GROUP BY 1 ORDER BY 1 DESC;

-- class C: repeat attempts per customer
SELECT customer_id, COUNT(*) c FROM delivery_schedule
GROUP BY customer_id HAVING c > 1 ORDER BY c DESC LIMIT 20;
```

A SQL census cannot distinguish A from B — only Chargebee can. That is why phase 2 exists.

**Phase 2 — dry-run reconciliation job.** A `@Scheduled` task (daily, 03:30 IST) that takes rows older than 48 h, capped at 500/run, and for each:

| Chargebee answer | Action |
| :--- | :--- |
| subscription **404** (class A) | append row to `orphans-YYYY-MM-DD.jsonl`, then delete |
| subscription exists, `active` / `in_trial` / `future` | keep, log `kept-active` |
| subscription exists, `cancelled` / `expired` / `completed` (class B) | keep, log `kept-closed` (history is cheap; deleting removes audit trail) |
| API error / timeout | skip, log `deferred`, retry next run |

Guardrails: `bmj.schedule.cleanup.mode=dry-run` by default (logs what it *would* delete), a per-run cap, an export file written **before** any delete, and one named owner who reads the first week of logs.

**Phase 3 — stop creating them.** Cheapest first:
1. If setting `subscription[id]` on the Chargebee request throws, delete the freshly reserved row in the same `catch` (today it leaks).
2. Add `expires_at` (= `created_at + 48 h`) plus an index, so the job never needs a full scan.
3. Optional client signal (`POST /api/subscriptions/schedule/{id}/abandon`) on back-out — an API addition, so it needs its own decision.

### 5.4 Risks and acceptance criteria

| Risk | Mitigation |
| :--- | :--- |
| Deleting a row whose subscription *does* exist under a different id | ids are minted server-side and passed to Chargebee as `subscription[id]`; a mismatch cannot happen unless Chargebee rejected the id, which the 404 branch then covers |
| Job runs during checkout (row is < 48 h old) | 48-hour floor is far beyond any hosted-page session |
| Chargebee API rate limits | cap 500/run, sequential with backoff, one run per day |
| Loss of forensic data | JSONL export before delete + keep B rows |

**Done when:** census shows a stable row count week over week for rows older than 48 h, the dry run's "would delete" list contains only 404s, and a real run deletes exactly that list.

---

## 6. Launch exit criteria

- [ ] Release APK built with the new manifest; `INTERNET` + `POST_NOTIFICATIONS` present (`apkanalyzer manifest permissions`)
- [ ] CI passes `--dart-define=API_BASE_URL=https://<prod-api>` and the build asserts it
- [ ] `keystore_name.jks` untracked, replaced, and the Chargebee key rotated
- [ ] Chargebee Price Variants enabled, 45 rows created, census **7 → 52** and zero unpriced items
- [ ] Device matrix T0 green on a release build; T1/T3 green at font scale 1.3; T4 prompt observed; T6 decided
- [ ] Orphan census run; cleanup job approved with a named owner
- [ ] Commits C1–C7 landed in order
