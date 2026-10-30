# PRODUCTION_READINESS_REPORT.md

**Prepared:** 16 October 2026
**Question:** what stands between the frozen tree and *paying customers on a production URL* — not code quality, not architecture, only deployment readiness.
**Method:** read-only inspection of the frozen tree + the deploy pipeline, one local release-artifact build, one live local smoke (§3). **Nothing in `lush/`, `bmjServer/src/` or the 14 screens was modified to produce this report.**
**Companions:** `BMJ_LAUNCH_CHECKLIST.md` (gates), `B5_SMOKE_TEST_PLAN.md` (how to run the smoke), `DEPLOYMENT_RUNBOOK.md` (how to ship).

---

## 1. Verdict

| Question | Answer |
| :--- | :--- |
| Does the shippable backend artifact build? | ✅ **Yes** — `mvnw -o -q -DskipTests package` → `com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar`, **61.1 MB**. That is the exact command `deploy-vps.yml` runs. |
| Is there anywhere to deploy it *to*? | 🔴 **No.** Every prod/staging hostname in the docs is DNS `NXDOMAIN`, so **B5 cannot be executed as written** → `PR-4`. |
| Would a CI build contain the whole app? | 🔴 **No.** Two *untracked* controllers serve the catalog — the first flow the app opens → `PR-1`, highest severity here. |
| Could a release APK built today reach the backend? | 🔴 **No.** With no `--dart-define=API_BASE_URL` it targets the phone's own loopback → `PR-3`. |
| Is the release APK publishable? | 🔴 **No** — signed with the **debug** keystore → `PR-2`. |
| Is HTTPS configured? | 🔴 **No** — Let's Encrypt is commented out; nginx listens on `:80` only → `PR-5`. |
| Does the catalog deliver **prices**? | 🔴 **No** — every item ships `"prices":[]`; the batch fetch is rejected and swallowed, **and no price records exist on any catalog item** → `PR-17` + `PR-18`, `PR-16`. |
| Does the app degrade safely when Chargebee is down? | 🔴 **No** — it returns `200 []`, i.e. a silently empty storefront → `PR-16`. |

**Summary:** the code builds and the artifact runs — but **the pipeline, the signing, the environment and the catalog payload are not launch-ready.** Five of those rows are configuration or process and three are one-line fixes; the catalog rows (`PR-16`/`PR-17`/`PR-18`) were found **only** by actually running the smoke and inspecting the response *body* rather than its status code, and then going upstream to count the data: `PR-17`'s one-line fix, on its own, still ships an unpriced catalog, because the test site holds **no price records at all** for the 15 items the storefront serves.

### Severity legend

🔴 blocks a paid launch · 🟠 blocks a *production-grade* launch (needs a sign-off or a follow-up) · 🟡 hygiene.

---

## 2. Findings

### PR-1 🔴 — The catalog is served by **untracked** source files; any pipeline build ships without it *(new blocker = `B8`)*

| Probe | Result |
| :--- | :--- |
| `git -C bmjServer ls-files src/main/java/com/bookmyjuice/controllers/` | 34 tracked files; **`CatalogController.java` and `UserProfileController.java` are absent** |
| `git -C bmjServer status --porcelain` | `?? src/main/java/com/bookmyjuice/controllers/CatalogController.java`<br>`?? src/main/java/com/bookmyjuice/controllers/UserProfileController.java` |

**Why it is fatal — and why it fails silently**

- `CatalogController.java:38` declares `@RequestMapping({ "/api/catalog", "/api/v1/catalog" })`; `:54` declares `@GetMapping("/charge-items")`.
- The app calls exactly that route: `lush/lib/UserRepository/user_repository.dart:160` → `Uri.parse('$server/api/v1/catalog/charge-items')`; `lush/lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart:198` documents it as *"Fetch from backend: GET /api/v1/catalog/charge-items (production)"*.
- `WebSecurityConfig.java:92` permits `/api/catalog/**` + `/api/v1/catalog/**`, so the route is expected to be publicly reachable.
- `.github/workflows/deploy-vps.yml` and `backend-ci.yml` both build from `actions/checkout@v4`. **A fresh clone does not contain the class.**
- The build still **succeeds**, because every remaining reference is javadoc only: `TestController.java:40` `{@link CatalogController}`, `:42` `{@link UserProfileController}`. `javac` ignores `{@link}` in comments.
- Net effect of deploying today: **HTTP 404 on the app's first screen.** Flows 1–3 of `docs/BMJ_V1_SCOPE.md` (catalog → cart) die, and it presents as "empty catalog", not as a build error.

**Fix — one minute, inside B1:**

```powershell
git -C bmjServer add src/main/java/com/bookmyjuice/controllers/CatalogController.java `
                       src/main/java/com/bookmyjuice/controllers/UserProfileController.java
```

This is the same defect class `B1` already records for the two untracked *markdown* deliverables — it simply had not been checked for *source*.

### PR-2 🔴 — The release APK is signed with the **debug** keystore

`lush/android/app/build.gradle.kts:36-42`:

```kotlin
buildTypes {
    release {
        // TODO: Add your own signing config for the release build.
        // Signing with the debug keys for now, so `flutter run --release` works.
        signingConfig = signingConfigs.getByName("debug")
    }
}
```

No `android/key.properties` and no `*.jks` anywhere under `lush/android`.

**Impact:** Play rejects debug-cert builds; the debug key is neither secret nor yours, so switching to a real key later breaks the update path for everyone who installed the debug-signed build. For V1 this is tolerable **only** as a direct/sideloaded APK to named first customers — which must be recorded as an explicit Product decision.

**Fix:** upload keystore + gitignored `key.properties` + `signingConfigs.release` (`DEPLOYMENT_RUNBOOK.md` §6), or sign off sideload-only.

### PR-3 🔴 — A release APK with no `--dart-define` points at the *device's own* loopback

`lush/lib/config/api_config.dart`:

```dart
static const String baseUrl = String.fromEnvironment('API_BASE_URL');
```

`String.fromEnvironment` with no `defaultValue` compiles to the **empty string** when the define is absent — there is no fallback and no error. A second, independent instance of the same class:

| File | Line | Value |
| :--- | :--- | :--- |
| `lib/config/api_config.dart` | — | `String.fromEnvironment('API_BASE_URL')` → `''` |
| `lib/services/firebase_notification_service.dart` | 152-155 | hard-coded `10.0.2.2:8080` (Android **emulator** alias) |

**Impact:** `flutter build apk --release` with no define produces an APK that talks to `localhost:8080` *on the phone itself*. Every request fails, and it presents as "app cannot load" — not as a config error. `10.0.2.2` is only valid inside an Android emulator; on a physical handset it is a dead address.

**Fix (build-time only, no code change):** always pass
`--dart-define=API_BASE_URL=https://<host>` (see `DEPLOYMENT_RUNBOOK.md` §5). Add a CI guard that fails the APK job when the define is empty.

### PR-4 🔴 — There is no deployed environment, so **`B5` cannot run as written**

| Host (from `docs/`) | DNS |
| :--- | :--- |
| `api.bookmyjuice.com` | `NXDOMAIN` |
| `bookmyjuice.co.in` | `NXDOMAIN` |
| `staging.*` | `NXDOMAIN` |

The docs also disagree with each other on the domain (`.com` in `docs/API.md` and `docs/DEPLOYMENT.md` vs `.co.in` in `docs/QUALITY_MANAGEMENT.md`), so there is not even a single agreed target.

`deploy-vps.yml` needs `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` repository secrets; `docs/HUMAN_INTERVENTION_REQUIRED.md` already lists the VPS as **H12, pending**. Until a host exists there is nothing to smoke, nothing to point the APK at, and nothing to tag a launch against.

**Two ways forward — a Product/Infra decision, not a code decision:**

1. **Provision the VPS** (`ops/provision-vps.sh`, ~30 min), set the three secrets, run `deploy-vps.yml`, then execute `B5_SMOKE_TEST_PLAN.md` §"Deployed" against the real host. Gives HTTPS, a stable URL and a repeatable pipeline.
2. **LAN smoke** against a laptop on the same Wi-Fi (`http://<lan-ip>:8080`), relying on `usesCleartextTraffic="true"`. Validates the *flows*, proves nothing about TLS/DNS/systemd/nginx — i.e. it closes `B5`'s app findings but not the environment ones.

Both paths are written out in `B5_SMOKE_TEST_PLAN.md` §"Executing without a VPS".

### PR-5 🔴 — No HTTPS anywhere in the deploy path

- `ops/provision-vps.sh` **Phase 8**: the Let's Encrypt / `certbot` block is commented out.
- The nginx site in the same script has a single `listen 80;` server block — no `443`, no `ssl_certificate`, no redirect.
- The APK sets `usesCleartextTraffic="true"` (`lush/android/app/src/main/AndroidManifest.xml`) — required for plain-HTTP during bring-up, but it must be flipped off at the HTTPS cutover.

**Impact:** `http://` only. Play Store policy aside, every bearer token, phone number and password crosses the network in clear text. This is the single largest customer-facing risk in this report and it is a ~15-minute fix on a host that exists.

### PR-6 🟠 — CORS is a wildcard `*`

`WebSecurityConfig.java:146-161`: `configuration.setAllowedOriginPatterns(List.of("*"))` with `setAllowCredentials(true)`, applied `/**`.

Mitigating fact worth recording: the API authenticates with `Authorization: Bearer` from secure storage — **not** cookies — so a hostile origin cannot silently ride a session. Bearer tokens must be stolen to be replayed, which blunts the classic CSRF-style attack.

Still: a browser-based client can call the API from *any* site the user visits, so any future cookie/session mode becomes immediately exploitable, and it removes a cheap layer of defence. **Fix:** allow-list the app's real origins at cutover. Not a launch blocker; a cutover task.

### PR-7 🟠 — The artifact version can never match the release tag

`bmjServer/pom.xml` declares `0.0.2-SNAPSHOT`, and `deploy-vps.yml` renames the JAR to `bmjServer-<sha>.jar`. `BMJ_LAUNCH_CHECKLIST.md` tags `v1.0.0-launch`. Nothing links the built bytes to the tag, so "what is running in production?" cannot be answered from the artifact alone.

**Fix:** set `<version>1.0.0</version>` in the launch commit, and record the artifact SHA-256 in the runbook. This is one line, done in the same commit as the tag.

### PR-8 🟠 — `/api/test/**` remains `permitAll` in every profile

`WebSecurityConfig.java` permits `/api/test/**` unconditionally, and there is no profile guard around it. `TestController` is the class whose javadoc still `{@link}`s the untracked catalog controller (`PR-1`), so it is live code, not a stub.

Verified live during this smoke (§3, probe 3): `/api/test/orders` and `/api/test/ordersByCustomerId` now return **404** — so the specific data-leaking handlers recorded in `B2` really are gone, and `B2` is genuinely closed. But the **namespace stays open**: any future method added to `TestController` is automatically anonymous, with no test to catch it.

**Fix:** in the launch commit, either delete `TestController` or gate it with `@Profile("!prod")`. Two lines; removes a whole class of future leak.

### PR-9 🟠 — The active production profile is not the one written for production

See `PR-12` — this is the deeper version of the same problem. Summarised here because it is a property *default*, not a pass/fail: the base `application.properties` supplies dev-shaped defaults (`spring.jpa.hibernate.ddl-auto=update`, a `PASS@123` password fallback, `show-details=always`). Any missing env var therefore **silently** falls back to a dev-shaped value instead of failing fast. Both the fix for `PR-9` and `PR-12` is the same one-liner.

### PR-10 🟡 — Deployment does not use the `app.jar` committed in the repo

`bmjServer/app.jar` is tracked in git, but `deploy-vps.yml` builds from source and publishes `bmjServer-<sha>.jar` to `$APP_DIR/current.jar`. The committed JAR is therefore dead weight — and actively harmful: it invites a future operator to "just deploy the jar that's in the repo", which ships an unbounded-age artifact. It also churns the repo on every build. `git status` already shows it staged as deleted (`D app.jar`) as part of the pending freeze.

**Fix:** keep it deleted, and add it to `.gitignore` in the same commit.

### PR-11 🟠 — The credentials in `.env` are live and un-rotated

The working `.env` holds the Chargebee **test-site** API key, the JWT secret, DB credentials and the `9999999901` test account's password. Two consequences:

- Once a VPS exists, the same values are written to `/home/bmj/bmj/.env` on that host. Anything that has ever passed through a chat log, a CI log or a screenshot of this repo is effectively public — so **these must be rotated before real customers use the system**, in the Chargebee dashboard and in the DB, not just edited on disk.
- `JWT_SECRET` rotation invalidates every issued token. That is fine *now* (no real users) and painful *later* — which is another reason to do it before launch rather than after.

**Fix:** rotate Chargebee key + JWT secret + `9999999901` password, update all three repos' `.env` templates (`ops/provision-vps.sh` heredoc and the local `.env`), and confirm no secret is committed. Sequence it as the last step before the tag so the tag points at the rotated config.

### PR-12 🔴 — **Nothing ever activates the `prod` profile.** `application-prod.properties` is dead code in production

Found by reading the systemd unit during this session; the highest-value finding here, because it silently disables the one file written to make production safe.

Three artifacts, none of which sets the profile:

| Artifact | Relevant content |
| :--- | :--- |
| systemd unit (`ops/provision-vps.sh`) | `ExecStart=/usr/bin/java -jar ${APP_DIR}/current.jar` — **no** `--spring.profiles.active` |
| `EnvironmentFile=${APP_DIR}/.env` heredoc | `DB_*`, `ADMIN_*`, `CHARGEBEE_*`, `JWT_*`, `WEBHOOK_*`, `MAIL_*`, `REDIS_*`, `SENTRY_*` — **no `SPRING_PROFILES_ACTIVE`** |
| `.github/workflows/deploy-vps.yml` | only `sudo systemctl restart "$SYSTEMD_SERVICE"` — passes **no** profile flag |

The service therefore starts with the **default** profile: base `application.properties` only. What that costs:

| Setting | `application-prod.properties` (intended) | Base file (actually runs) |
| :--- | :--- | :--- |
| `hibernate.ddl-auto` | `validate` — refuse to boot on schema drift | `update` — **Hibernate mutates the production schema on every deploy** |
| `spring.datasource.url` | `useSSL=true` | `useSSL=false` — **DB traffic unencrypted** |
| `logging.level.*security*` | `WARN` | `DEBUG` — auth internals written to disk |
| Hikari pool | sized for production | defaults |
| Error detail | sanitised | verbose |

**Impact:** the deploy target silently disagrees with the file documenting its intended behaviour. Because `ddl-auto=update`, an entity change can alter or drop production columns with no migration review — the exact failure `validate` exists to prevent.

*(Reassurance, correcting the earlier hypothesis: `${DB_USERNAME}` **is** resolved in production — `EnvironmentFile=` does supply it. The unit is correct there; only the profile is missing.)*

**Fix — one line, in the launch commit:**

```ini
Environment=SPRING_PROFILES_ACTIVE=prod
```

Add it to the unit in `ops/provision-vps.sh`, then confirm with `journalctl -u bmj-backend | Select-String "The following.*profile"`. Do this **before the first real customer**, and re-verify `ddl-auto=validate` passes — the first `validate` boot is where any drift surfaces.

### PR-13 🟠 — The six `db/migration/*.sql` files are applied by nothing

There is **no `flyway` and no `liquibase` dependency in `pom.xml`** (verified by grep) and no migration runner in any startup path. The files are inert scripts.

Proof from this smoke's throwaway database: Hibernate `ddl-auto=update` created **31 tables** — all entity-mapped ones — but **`V4`'s consent tables and `V5`'s `refresh_tokens` table are absent**, because no entity maps them; their scripts never ran. `webhook_events` *does* exist, because it has an entity and needs no script.

Consequences:

- Anything a migration was meant to change (indexes, constraints, seed rows) exists **only** if Hibernate happens to infer it. `V6__seed_test_accounts.sql` — the `9999999901` account used by `ops/test_signin.ps1` and by `B5` — was **never applied**: the fresh smoke DB had zero users until one was inserted by hand. On a fresh production DB, roles appear (a startup seeder creates them; `roles.id=1` already existed) but the seeded *accounts* do not.
- `V5`'s table is missing while the docs list `POST /api/auth/refresh` as available (checklist `H20`) — that path has no storage on a fresh database. Wire it or remove it before customers reach it.

**Fix:** pick one, and write the choice down — (a) wire Flyway (`flyway-core` + `flyway-mysql`, `spring.flyway.enabled=true`, `baseline-on-migrate`) so the scripts become the schema of record, or (b) delete the orphaned scripts and let Hibernate own the schema. **(a) is required before `ddl-auto=validate` (`PR-12`) can hold reliably.**

### PR-14 🟠 — `GET /api/user/profile` returns the BCrypt password hash to the client

Captured live during this smoke (§3, probe 8):

```json
{"id":1,"username":"9999999901","email":"ta01@bookmyjuice.co.in",
 "password":"$2b$12$mpZ8lsANcb/B4X5gQsxoM.vUsJoIx5gnx9EKQa5vDb/5OzHzweM22", ...}
```

Source — `UserProfileController.java:60-61`:

```java
return userRepository.findById(userId)
        .<ResponseEntity<?>>map(ResponseEntity::ok)   // ← serialises the raw User entity
```

The JPA **entity is returned directly**, so every field Jackson can see is published — password hash, `google_id`, `token_version`.

**Impact:** a user receives their own credential hash, exposing it to on-device storage, logging proxies, crash reporters and the network. Anyone who obtains a response body (a leaked HAR, a proxy log) gets the exact material for offline cracking. No client needs the hash — login happens server-side.

**Fix:** return a DTO/`Map` of public fields (`id`, `username`, `email`, `firstName`, `lastName`, `phone`, `roles`), or mark the secrets `@JsonIgnore`. This file is **also untracked (`PR-1`)** — fix and `git add` belong in the same commit.

### PR-15 🟠 — `GET /api/subscriptions/my` returns **401 to a fully authenticated user** when `chargebee_customer_id` is null

Reproduced live (§3, probes 7-9). A user signed in successfully (`POST /api/auth/signin` → **200** + JWT, `roles=ROLE_USER`), and that same token was accepted by `/api/orders/by-customer` (**200 `[]`**) and `/api/user/profile` (**200**) — yet `/api/subscriptions/my` answered:

```
401  {"error":"User not authenticated"}
```

The 401 is **not** from Spring Security. The controller throws it — `SubscriptionController.java:71-73`:

```java
String customerId = getCustomerIdFromSecurityContext();
if (customerId == null) {
    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
            .body(Map.of("error", "User not authenticated"));   // misleading: the user IS authenticated
}
```

The account has a valid session but `chargebee_customer_id = NULL` — exactly the state `D-2`/`G-2` fixed for the *checkout* path, where the same null ends in "Chargebee customer ID not found".

**Why this matters to `B6`:** `B6`'s verdict was *"option (a) — the subscriber can pause/cancel from inside the app"*, resting on `SubscriptionManagementScreen` loading `GET /api/subscriptions/my`. That call **fails with 401 for any account without a Chargebee customer id**, so `B6` needs this caveat attached rather than being closed unconditionally:

- For accounts created via `unified-signup` / `login-otp` / `google` (the V1 onboarding paths), `D-2` backfills the customer id → the screen works.
- For a **legacy/password** account — and `/api/auth/signin` performs **no** backfill, unlike the other three paths — the screen shows an error instead of the subscription, and the home-tab pause affordance has nothing to act on.

**Fix (small, safest ordering):** treat "no Chargebee customer" as *"no subscriptions yet"* rather than an authentication failure — return `200` with the empty payload lines 82-85 already build, and keep the 401 for a genuinely missing principal. One `if`-branch; no schema, no API-shape, no screen change. Then extend the `D-2` backfill to `/api/auth/signin` so the paths agree.

*(A live-verified flaw in a frozen file. Reported, not patched — per the no-refactor constraint. Candidate for the launch commit or a fast-follow, at your call.)*

### PR-16 🔴 — The catalog **silently returns `200 []`** when Chargebee is unreachable

Observed **twice**, intermittently, during this smoke — with the same URL that returned 7,657 bytes of real items three times in a row minutes earlier. The log explains it exactly:

```
INFO  c.bookmyjuice.services.ItemService - Fetching items from Chargebee with category and size filtering
ERROR c.bookmyjuice.services.ItemService - Error fetching items from Chargebee: bookmyjuice-test.chargebee.com
INFO  c.bookmyjuice.services.ItemService - Falling back to local database cache
```

There is a deliberate degradation chain — **live Chargebee → local DB cache → empty list** — and when both live and cache are empty the API answers `200 []` (`ItemService.java:668` logs the error; the caller returns an empty payload). **No error status, no warning to the client.** The app renders an empty store, identical to the symptom of `PR-1`'s missing route and identical to "we genuinely sell nothing".

**Why this is a launch risk, not a curiosity:**

- On a **fresh production database the local cache is empty by definition** — so the very first customers depend on a live Chargebee call succeeding, with a silent-empty failure mode if it does not. One Chargebee hiccup, rate limit or network blip = an empty storefront with a green health check.
- It is **indistinguishable from success** to both the app and the on-call engineer: `/api/health` stays `UP`, the smoke's status-code probes pass, and no alert fires.
- The smoke in §3 only caught it because probe 2 was re-run and the payload inspected. This is the single strongest argument in this report for asserting on **payload content**, not status codes.

**Fix:** have the fallback distinguish "empty cache" from "cache populated but nothing matched" — return `503`/`502` (or a `degraded: true` flag) when the upstream fetch fails *and* the cache yields nothing, so the app can show "please try again" instead of "no products". At minimum, log and emit a metric on this path so it is alertable.

### PR-17 🔴 — **Every item's `prices` array is empty** — the ItemPrice batch fetch is rejected by Chargebee and the failure is swallowed

Captured live (§3). A successful `200` catalog response, 15 items, every field checked for population:

| Field | Populated | Field | Populated |
| :--- | :--- | :--- | :--- |
| `itemId` … `category` (8 fields) | **15/15** ✅ | **`prices`** | **0/15** ❌ |
| `imagePath` | 0/15 ❌ | `calories`, `servingSize`, `benefits` | 0/15 ❌ |
| `allergies`, `tags`, `nutritionalInfo` | 0/15 ❌ | `customization`, `meals`, `startColor` … | 0/15 ❌ |

```json
{"itemId":"bmj-item-detox-smoothie","name":"Detox Smoothie","category":"premium", … ,"prices":[]}
```

**Exact cause — `ItemService.java:937`:**

```java
// Pre-fetch ALL ItemPrices in a single batch to avoid N+1 API calls
try {
    com.chargebee.ListResult allPricesResult = ItemPrice.list().limit(200).request();   // ← 200
    ...
} catch (Exception e) {
    logger.warn("Failed to batch-fetch ItemPrices: {}", e.getMessage());                 // ← swallowed
}
```

Chargebee's list endpoint caps `limit` at 100, and the sibling call one line earlier gets this right (`Item.list().limit(100)`, `:913`). So the price pre-fetch **always throws**, is downgraded to a WARN at `:943`, `pricesByItemId` stays empty, and the response carries `prices: []` for every item. The log confirms it on every request:

```
WARN c.bookmyjuice.services.ItemService - Failed to batch-fetch ItemPrices: limit : It should not be more than 100
```

**Impact:** the catalog page ships **without prices**. If the app renders price from this array, customers see items with no price and checkout has nothing to charge from — a store that cannot be bought from, while every status code is `200` and `/api/health` is `UP`. `PR-16` and `PR-17` fail *identically* to the naked eye: an empty-looking storefront.

**Fix — and it must be verified, not assumed:** change `:937` to `.limit(100)` **and add the pagination loop** that `:910-923` uses for items (a single `limit(100)` page silently drops prices for items beyond the first 100 — this site already has **176 items**, so the truncation is real). Then re-run `ops/smoke_test.ps1` and confirm probe **2b** passes.

> **Honesty note — since resolved (§3.5, `PR-18`):** the WARN proves the call *fails*; it does not prove the site *has* ItemPrices to return. **That was settled read-only: the site holds 314 ItemPrices and not one of them belongs to a catalog item.** So the fix below is *necessary but not sufficient* — the second half is a data task in Chargebee.

**Why the earlier status-only probes missed this:** probe 2 asserted `200` + the presence of `itemId`, both of which pass. The smoke script now asserts `"prices":[` **and the absence of `"prices":[]`** (probe 2b) precisely so this class of hollow-200 cannot pass again.

---

### PR-18 🔴 — The catalog's 15 items have **no price records at all** — so `PR-17`'s fix, alone, still ships an unpriced store

`PR-17` proves the batch fetch *fails*. It does **not** prove prices *exist*. That gap was closed read-only — no artifact change, nothing written to Chargebee — by paging the MCP `list_item_prices` tool to exhaustion and intersecting the result with the live catalog's 15 item ids.

**Census — all 4 pages (100 + 100 + 100 + 14) = 314 ItemPrices:**

| Slice | Result |
| :--- | :--- |
| by `item_type` | **`plan=300`, `charge=5`, `addon=9`** |
| attached to a `bmj-item-*` item (the catalog's own family) | **0** |
| catalog items (15) covered by ≥1 price | **0 / 15** |

The prices that do exist hang off `bmj-premium-*` / `bmj-signature-*` / `bmj-delight-*` / `bmj-generic-*` — all `item_type: plan` — plus legacy and demo ids (`abc200`, `carrot300`, `daily_delight200`, `cbdemo_*`, `meteredTest`, …). The 15 ids the catalog actually serves (`bmj-item-detox-smoothie`, `bmj-item-coconut-milk`, …) appear **nowhere** in the price set, on any page.

**Root cause: a recorded false premise that this very site disproves.** `docs/chargebee_final_state.md:79-80`:

> ## One-Time Juice Items (15)
> Created 2026-05-28 via MCP. Type: `charge`. IDs: `bmj-item-*` pattern.
> **Charge types use flat pricing via `item.price` field, not separate `item_prices`.**

and line 91 books the consequence as an accepted gap — `| One-time item prices | 0 | 45 | ⚠️ Charge type doesn't use item_prices |`.

**That premise is false.** 5 of the site's 314 ItemPrices carry `item_type: "charge"` — charge-type items demonstrably *do* use `item_prices`, which is exactly why `ItemService.java:937` reads `ItemPrice.list()` in the first place. So ~45 one-time prices were never created because of a wrong belief, logged as a ⚠️, and a catalog was then built that depends on the data the sibling note declares unnecessary. The bug and the gap compose:

| | After `.limit(100)` only | After `.limit(100)` **and** creating the prices |
| :--- | :--- | :--- |
| `"prices"` on the 15 catalog items | **still `[]`** | populated |

**Consequence for the gate:** `G12`/`B10` cannot be closed by code alone — probe 2b *cannot* pass until the data exists. The second half is a **Product + Chargebee-data task, not an engineering one**: each bottle's price has to come from the business, in the same `flat_fee`/INR shape the 5 existing charge prices already use.

**Fix:** (a) the `PR-17` code change; (b) create one `ItemPrice` per `bmj-item-*` item — a **Chargebee write, requiring explicit go-ahead** (`D4`/`D6`).

**How this was found, and the lesson:** not by the smoke script, but by a follow-up census prompted by `PR-17`'s own honesty note. The WARN proved a call *failed*; only a count could prove the data was *absent*. **A failed read is not evidence that the data is missing — absence of a result is not absence of data. Go and count it.**

---

## 3. Live smoke evidence (local, reproducible)

`B5` asks for a deployed smoke. **The deployed half is blocked by `PR-4`** (no host exists). The *local* half was executed in full against the real release artifact, on an isolated database, with startup Chargebee sync disabled — so no Chargebee data was touched and no production system was contacted.

### 3.1 Method

| Element | Value |
| :--- | :--- |
| Artifact under test | `com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar` — the same `mvnw -o -q -DskipTests package` output `deploy-vps.yml` ships |
| Database | MySQL 8.0 in Docker, container `bmj-smoke-mysql`, port **3307**, database `bmj_db` — **isolated**; the host's own MySQL on 3306 was not used |
| Backend | `java -jar` on port **8085** (8080 is held by an unrelated local service), profile `dev`, `--chargebee.sync.enable-startup-sync=false` |
| Credentials | exported into the process environment from `.env` (**not** via `spring.dotenv.location`, which `java -jar` does not honour) |
| Chargebee | **read-only.** No customer, subscription, order, invoice or plan was created, paused, resumed or cancelled. `POST /api/auth/signin` is confirmed to make no Chargebee call. |

### 3.2 Probe results

| # | Probe | Expected | **Observed** | Verdict |
| :--: | :--- | :--- | :--- | :--- |
| 1 | `GET /api/health` (anonymous) | 200 `UP` | **200** `{"status":"UP","timestamp":"2026-10-16T13:02:08…"}` | ✅ |
| 2 | `GET /api/v1/catalog/charge-items` (anonymous) | 200 + items | **200**, 7 657 bytes, real items — but **intermittently `200 []`** on identical calls | ⚠️ **`PR-16`** |
| 2b | …**same route, payload inspected** | items **carrying prices** | **200**, 15 items, **`"prices":[]` on all 15**; 17 of 25 fields null — and §3.5 shows **no prices exist to carry** | 🔴 **`PR-17` + `PR-18`** |
| 3 | `GET /api/test/orders` (anonymous) | 404 — gone | **404** `{"error":"Not Found","message":"No handler found for this route"}` | ✅ **`B2` closed** |
| 4 | `GET /api/test/ordersByCustomerId` (anonymous) | 404 — gone | **404** (same body) | ✅ `B2` closed *more* thoroughly than the checklist assumed |
| 5 | `GET /api/subscriptions/my` (anonymous) | 401 | **401** | ✅ (route exists, auth enforced) |
| 6 | `GET /api/orders/by-customer` (anonymous) | 401 | **401** | ✅ (route exists, auth enforced) |
| 7 | `POST /api/auth/signin` — legacy account | 200 + JWT | **200** + JWT, `id=1`, `roles=ROLE_USER` | ✅ no Chargebee customer created |
| 8 | `GET /api/user/profile` (Bearer) | 200 | **200** — **and it contains `"password":"$2b$12$…"`** | 🔴 **`PR-14`** |
| 9 | `GET /api/subscriptions/my` (Bearer, `chargebee_customer_id=NULL`) | 200 `[]` | **401** `{"error":"User not authenticated"}` | 🟠 **`PR-15`** |
| 10 | `GET /api/orders/by-customer` (Bearer, same account) | 200 `[]` | **200 `[]`** | ✅ `D-6` null-handling verified live |

### 3.3 What the probes prove

1. **The release artifact builds *and runs*.** It boots, serves the health endpoint, opens a pool to MySQL and answers real traffic. The `61.1 MB` JAR is not merely buildable, it is executable end to end.
2. **Flow 1 (catalog) works against live Chargebee data** — probe 2 returned the real test-site catalog. This is simultaneously the **proof that `PR-1` is fatal**: the 200 came from `CatalogController`, a file **not in git**. A CI build — from a clean checkout — would 404 here.
3. **`B2` is closed** (probes 3-4): both anonymous test-order routes are gone, and they are gone for the stricter reason, not merely hidden behind auth.
4. **`D-6` is verified live** (probe 10): an account with no Chargebee customer now gets `200 []` from the orders endpoint instead of an error.
5. **`PR-15` is a genuine defect, not a testing artefact** — the same JWT that satisfies probes 8 and 10 is rejected by probe 9, and the source shows the controller itself returns 401.

### 3.4 What could not be tested — and why it matters

| Untestable here | Blocked by |
| :--- | :--- |
| Anything on a real hostname, over TLS, through nginx, under systemd | `PR-4` — no host exists |
| A release APK talking to a real backend | `PR-3` (no `API_BASE_URL` default) + `PR-4` |
| The `D-2` backfill on `unified-signup` / `login-otp` / `google` | Requires a Chargebee **write** — needs your explicit go-ahead. `docs`/checklist record it as `B4`, still unexercised. |
| Pause / resume / cancel inside the app (`B6` step) | Requires Chargebee **writes** against a real subscription — needs your go-ahead, and `PR-15` must be understood first |
| `ddl-auto=validate` boot, prod logging, pool sizing | `PR-12` — the `prod` profile is never activated, so none of it ran |
| Flyway/migration behaviour on a clean production DB | `PR-13` — no migration runner exists |

### 3.5 The price census — the read-only check the probes cannot make (`PR-18`)

Probe 2b proves the *response* carries no prices. It cannot tell whether prices exist **upstream**, and that distinction decides whether `G12` is an engineering task or a data task. So the upstream was counted directly — read-only, paged to exhaustion, nothing written:

| Measurement | Result |
| :--- | :--- |
| ItemPrices in the test site | **314** (4 pages: 100 + 100 + 100 + 14) |
| by `item_type` | `plan=300`, `charge=5`, `addon=9` |
| attached to a `bmj-item-*` item | **0** |
| catalog items (15) covered by any price | **0** |

Cross-checked against the live `GET /api/v1/catalog/charge-items` response, whose 15 `itemId`s (`bmj-item-detox-smoothie`, `bmj-item-coconut-milk`, …) do not intersect the price set at all. Written up as `PR-18`; the gate consequence is recorded in `G12`.

**Bottom line for `B5`:** the *application* half passes — the artifact runs, the catalog serves, the auth boundary holds, `B2` is closed and `D-6` is verified. The *environment* half cannot be attempted until `PR-4` is decided, and two defects (`PR-14`, `PR-15`) were found only because the smoke was actually run.

---

## 4. The launch gate

Every row must be green before `v1.0.0-launch` is tagged. "Effort" assumes a host already exists.

| # | Gate | Status | Blocked by | Effort |
| :--: | :--- | :--- | :--- | :--- |
| G1 | Freeze committed — working tree clean in all three repos | 🔴 Not done | `B1` + `PR-1` (untracked source) | 10 min |
| G2 | Catalog controller tracked so CI ships it | 🔴 **Not done** | `PR-1` / `B8` | 1 min |
| G3 | Release artifact builds | ✅ **Done** — 61.1 MB JAR | — | — |
| G4 | Local application smoke green | ✅ **Done** — §3 | — | — |
| G5 | Deployed smoke green (`B5`) | 🔴 **Cannot start** | `PR-4` | 2-3 h |
| G6 | `prod` profile actually active | 🔴 Not done | `PR-12` | 5 min |
| G7 | HTTPS live, cleartext off | 🔴 Not done | `PR-5` | 30 min |
| G8 | Release APK signed with a real key (or signed off) | 🔴 Not done | `PR-2` | 1 h / decision |
| G9 | APK built with `--dart-define=API_BASE_URL` | 🔴 Not done | `PR-3` | 1 min |
| G10 | Credentials rotated | 🔴 Not done | `PR-11` | 1 h |
| G11 | Pause/cancel usable in-app (`B6`) | 🟠 **Caveat** | `PR-15` + Chargebee write go-ahead | decision |
| G12 | Catalog delivers **prices** | 🔴 **Not done** — `"prices":[]` on every item, **and no price records exist to deliver** (`PR-18`) | `PR-17` (code) + `PR-18` (**Chargebee write**) | 5 min code + 1 h data |
| G13 | Storefront degrades safely, not silently empty | 🔴 **Not done** | `PR-16` | 30 min |

**Eleven of thirteen gates are still open. Five need code or config changes; `G12` additionally needs price data that does not exist yet.** The rest are a host (`PR-4`), a keystore decision (`PR-2`), and a rotation (`PR-11`).

## 5. Recommended sequence

Ordered so that each step is verifiable before the next depends on it, and so the tag lands on the exact bytes that were smoked.

1. **Fix the two untracked files (`PR-1`/`B8`) and add `CatalogController.java` + `UserProfileController.java` to git.** Nothing else can be trusted until a clean checkout builds the whole app. *(1 min)*
2. **Decide `PR-4`** — provision a VPS, or accept a LAN smoke. Everything from step 4 onward depends on this.
3. **One-line production config commit:** `Environment=SPRING_PROFILES_ACTIVE=prod` (`PR-12`), `TestController` gated or deleted (`PR-8`), pom → `1.0.0` (`PR-7`), `app.jar` deleted + gitignored (`PR-10`). *(15 min)*
4. **Provision + deploy**, then run `B5_SMOKE_TEST_PLAN.md` §"Deployed" — including, for the first time, a boot under the `prod` profile, which is where `ddl-auto=validate` (`PR-12`) and the missing migration runner (`PR-13`) will show themselves.
5. **HTTPS cutover (`PR-5`)**, then flip `usesCleartextTraffic="false"` and rebuild the APK *with* the define (`PR-3`).
6. **Certify the signing decision (`PR-2`)**, then build the customer-facing APK.
7. **Rotate credentials (`PR-11`)**, then run the closing Chargebee smoke (`B4`, `B6`) with your go-ahead.
8. **Commit the freeze, close the checklist, tag `v1.0.0-launch`** — only after G1-G10 are green.

## 6. Decisions needed from you

| # | Decision | Options | Consequence |
| :--: | :--- | :--- | :--- |
| D1 | `PR-4` — where does V1 actually run? | (a) provision the VPS now; (b) LAN smoke only | (a) closes G5/G7 and gives a real URL; (b) leaves the environment gates open and untestable |
| D2 | `PR-2` — Play-grade signing? | (a) real keystore; (b) sideload-only sign-off | (b) must be recorded as a Product decision, and switching keys later breaks updates for installed users |
| D3 | `PR-15` — fix in the launch commit? | (a) fix the controller branch; (b) fast-follow | (a) is a 3-line change in a frozen file; (b) leaves the subscription screen erroring for legacy accounts |
| D4 | Chargebee **writes** | go / no-go | Gates `B4` (backfill) and `B6` (pause/cancel) — the only two smoke steps that touch live Chargebee data |
| D5 | `PR-13` — Flyway or Hibernate-owns-schema? | (a) wire Flyway; (b) delete orphan scripts | (a) is required before `ddl-auto=validate` can be relied on |
| D6 | `PR-17` + `PR-18` — the catalog has **no price data at all**. The `.limit(200)` bug is proven (§3), and the site's 314 ItemPrices contain **nothing** for the 15 `bmj-item-*` items (all 4 pages checked, 0/15 matched) — so the one-line fix alone ships an unpriced store | (a) fix `limit` **and** create ItemPrices on the 15 `bmj-item-*` items; (b) fix the code only; (c) leave both | **(b) is now known to be insufficient** — it was option (a) that would have "settled whether prices exist", and they do not. (a) needs a **Chargebee write** (`D4`), and the price list must come from Product, not from the developer |
| D7 | `PR-16` — how should an empty catalog present? | (a) `503` + retry affordance; (b) keep `200 []` | (b) means launch day can show an empty store with a green health check |

All seven are Product/Infra calls; none is an architecture change. **Every code-touching item above is one line to a few lines, except `PR-2` and `PR-13`.**
