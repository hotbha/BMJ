# BookMyJuice — V1 Launch Checklist

**Prepared:** 16 October 2026
**Subject:** V1 launch readiness after the launch freeze (`D-1` Option 1) plus the approved decisions **D-2 / D-5 / D-6**.
**Evidence base:** `PRODUCT_ALIGNMENT_REPORT.md` §J, `docs/BMJ_V1_SCOPE.md` §2–§6, `docs/API.md` *V1 Launch Freeze — Contract Changes (2026-10-16)*, and the commands in the appendix below.
**Scope:** questions only — this document adds no scope and changes no code.

### Classification legend

| Label | Meaning |
| :--- | :--- |
| **BLOCKER** | Must be done, or must have a signed-off workaround, **before** real paying customers are onboarded. |
| **POST-LAUNCH** | Safe to ship without. Fix in the first iteration after launch; none of these leaks data, blocks a V1 flow or stops a payment. |
| **IGNORE** | Accepted as-is. Recorded so it is not re-raised. No action planned. |

---

## 1. Critical Launch Blockers

All seven are **BLOCKER**. Each has a named fix and an owner; none is architectural.

| # | Blocker | Class | Evidence | Fix (smallest safe change) | Owner | Est. |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B1** | **The freeze is not committed anywhere.** All three repos hold it as uncommitted working-tree state: root on `feat/v1-launch-freeze` (`HEAD be41c89`), `lush` on `main` (`e1d11e6`), `bmjServer` on `main` (`fa34ca9`). Two deliverables are still **untracked** (`PRODUCT_ALIGNMENT_REPORT.md`, `docs/BMJ_V1_SCOPE.md`). Nothing that has been verified is deployable. | BLOCKER | `git status --porcelain` in all three repos; §5 rows 11–16 | Commit the freeze in `bmjServer` and `lush`, then root; push; **tag the commit in each repo** (`v1.0.0-launch`); build the release artefact from that tag. Resolve **B7** and the `logs/**` churn (§2 I5) before staging. | Repo owner | 1–2 h |
| **B2** | **`GET /api/test/orders` returns every customer's order PII to an unauthenticated caller.** `/api/test/**` is `permitAll` and `OrdersController#getAllOrders` carries no `@PreAuthorize`, so it returns `orderRepository.findAll()` mapped to `OrderResponse` — including the `shippingAddress` and `billingAddress` maps, amounts, dates and customer ids for **all** customers. | BLOCKER | `WebSecurityConfig.java:93`; `OrdersController.java:40-43`; `OrderResponseMapper.java:13-62` | One line: add `@PreAuthorize("hasRole('ADMIN')")` to `OrdersController#getAllOrders` (the deprecated twin of the ADMIN-only `GET /api/orders/admin/all-orders`), or delete the deprecated route. **Deliberately not done in the freeze** — this was the retained G-8 item. *The sibling `GET /api/test/ordersByCustomerId` is also unauthenticated but reads its id from the security context, so an anonymous call resolves to `null` and returns `[]` — no leak there.* | Backend | 15 min |
| **B3** | **Order history (in-scope flow 6) is not verified against real data.** The `D-6` code is in place and compiles, but nothing has shown `GET /api/orders/by-customer` returning a non-empty array. Accounts with no Chargebee customer correctly return `[]`, which looks identical to the old defect — so an untested launch cannot distinguish "fixed" from "still broken". | BLOCKER (verification gate, not code) | `docs/BMJ_V1_SCOPE.md` §5 row 13; `OrderController.java:69-88` | Run the flow once against a user who has a `chargebeeCustomerId` **and** at least one synced order; confirm a populated array, then confirm the `[]` case for an account without a Chargebee customer. | Backend + QA | 30 min |
| **B4** | **The `D-2` backfill has never been exercised.** It is best-effort by design, so a silent failure would leave the checkout dead-end it was written to remove. It also **creates a Chargebee customer**, so exercising it is a deliberate action on a real Chargebee account. | BLOCKER (verification) | `AuthController.java:431-455`; §5 row 12 | Sign in by OTP with a legacy account whose `chargebeeCustomerId` is null (or null it on a staging row); confirm the id is persisted and that checkout no longer fails with `Chargebee customer ID not found`. | Backend | 30 min |
| **B5** | **No live end-to-end evidence.** All 16 verification rows are compile, static-analysis or unit-test results. Nothing in the freeze record exercises a real OTP delivery or a real payment (`POST /api/v2/checkout/with-items` → Chargebee Hosted Page → WebView). The device E2E templates are gated by `--dart-define=E2E=true` and are non-functional scaffolding. | BLOCKER | §5 rows 1–16; `integration_test/cart_test.dart:22`; `integration_test/physical_device_template_test.dart:23` | One manual staging smoke on a real device: signup (Google **and** OTP) → catalog → cart → pay → order appears in order history → subscription visible in `/manage-subscriptions`. | QA + Backend | 2–3 h |
| **B6** | **A paying subscriber cannot pause or cancel from the app** (`G-2`, P0). The API routes work (the freeze fixed the `PUT /{id}/cancel` 404), but no screen entry point was ever wired, so `SubscriptionManagementScreen`'s pause/resume/cancel actions are unreachable. This is a product/legal decision, not a code defect. ✅ **RE-VERIFIED 2026-10-16: this premise is stale.** The screen *is* wired and *is* reachable (Profile → Manage Subscriptions, or the home card's *Pause* button), calling `PUT /{id}/pause|resume|cancel` — all three exist server-side with matching payload keys. Option **(a) is already satisfied**; the residual item is one step in the **B5** device smoke. See `B6_DECISION_REPORT.md`. | BLOCKER (product decision) | `PRODUCT_ALIGNMENT_REPORT.md` §J.3 G-2 = "Still open — the freeze was plumbing only; no UI was wired up" | Either (a) wire the existing screens to the fixed endpoints, or (b) accept and publish a support process ("contact us to pause/cancel") for launch, and fix in the next iteration. (b) is a valid sign-off if Product agrees. | Product + Flutter | (a) 4–6 h, (b) 30 min |
| **B7** | **Unrelated uncommitted UI work is sitting inside the freeze tree** (`W0`). `lush/lib/views/screens/home_tab.dart` and `menu_tab.dart` hold **210 insertions / 80 deletions** that have nothing to do with this change. Whatever is done with them decides what actually ships. | BLOCKER (release integrity) | §J.5 W0; `git -C lush diff --stat` | Decide explicitly: commit them as a **separate, reviewed** change, or `git stash` them so the freeze commit contains only freeze scope. Do not let them ride inside the freeze commit unlabelled. | Repo owner | 15 min |

---

### 1a. Closures and new blockers from the **live smoke** — 16 October 2026

Executed against the real release artifact (`bmjServer-0.0.2-SNAPSHOT.jar`, 61.1 MB) on an isolated MySQL, with Chargebee **read-only**. Evidence: `PRODUCTION_READINESS_REPORT.md` §3. Re-runnable: `powershell -File ops\smoke_test.ps1 -BaseUrl http://127.0.0.1:<port>`.

**Status changes to existing rows**

| # | Change |
| :--- | :--- |
| **B2** | ✅ **CLOSED — verified live.** `GET /api/test/orders` and `GET /api/test/ordersByCustomerId` both return **404** to an anonymous caller. Closed more thoroughly than this checklist assumed: the routes are **gone**, not merely guarded. |
| **B3** | 🟠 **Half-verified.** The `[]` case is now proven live (`GET /api/orders/by-customer` → `200 []` for an account with a null Chargebee customer). The **populated** case still needs an account with a real Chargebee customer → stays open, but with less work left. |
| **B5** | 🟠 **PARTIAL.** The application half passes locally (report §3.2: artifact boots, catalog serves, auth boundary holds). The *deployed* half **cannot start** — no host exists (`PR-4`). |
| **B6** | 🟠 **Verdict carries a caveat** — see **B13**. Cannot be closed unconditionally. |

**New blockers — every one live-verified, none architectural**

| # | Blocker | Evidence | Fix (smallest safe change) | Est. |
| :--- | :--- | :--- | :--- | :--- |
| **B8** | **The catalog is served by untracked source.** `CatalogController.java` and `UserProfileController.java` are absent from git; a CI build ships without them → **404 on the app's first screen**, presenting as an empty catalog. (`PR-1`) | `git ls-files` vs `git status --porcelain` | `git add` both files | 1 min |
| **B9** | **Nothing ever activates the `prod` profile.** systemd, `.env` and `deploy-vps.yml` all lack `SPRING_PROFILES_ACTIVE`, so production boots on dev defaults: **`ddl-auto=update` mutates the live schema on every deploy** and DB traffic runs `useSSL=false`. (`PR-12`) | systemd unit in `ops/provision-vps.sh`; `deploy-vps.yml`; report `PR-12` | `Environment=SPRING_PROFILES_ACTIVE=prod` | 5 min |
| **B10** | **Every catalog item ships `"prices":[]`.** `ItemService.java:937` asks for `ItemPrice.list().limit(200)`; Chargebee caps `limit` at 100, so the call **always** throws and is swallowed as a `WARN`. A storefront with no prices. (`PR-17`) | live payload: 15 items, `prices` populated **0/15**; log `WARN … limit : It should not be more than 100` | `.limit(100)` **+ paginate** like `:910-923` | 5 min + verify |
| **B11** | **The catalog silently returns `200 []` when Chargebee is unreachable** and the local cache is empty — an empty store with a green `/api/health`. On a fresh production DB the cache *is* empty. (`PR-16`) | observed **twice**; log `Error fetching items from Chargebee … Falling back to local database cache` | return `503` / `degraded: true` instead of an empty list | 30 min |
| **B12** | **`GET /api/user/profile` returns the BCrypt password hash to the client.** The raw `User` entity is serialised. (`PR-14`) | live body contains `"password":"$2b$12$…"`; `UserProfileController.java:60-61` | return a DTO / `@JsonIgnore` the secrets | 15 min |
| **B13** | **`GET /api/subscriptions/my` returns `401 "User not authenticated"` to a fully authenticated user** when `chargebee_customer_id` is null. The controller (not Spring Security) throws it. This is what `B6`'s verdict depends on. (`PR-15`) | same JWT accepted by `/api/user/profile` (200) and `/api/orders/by-customer` (200), rejected here (401); `SubscriptionController.java:71-73` | treat "no Chargebee customer" as *no subscriptions yet* → `200`; extend the `D-2` backfill to `/api/auth/signin` | 15 min |
| **B14** | 🔴 **There are no prices to deliver. The 15 catalog items have zero ItemPrice records — and this is *not* the `limit` bug.** A read-only census of the whole test site found **314 ItemPrices: `plan=300, charge=5, addon=9`**, attached to `bmj-premium-*` / `bmj-signature-*` / `bmj-delight-*` / `bmj-generic-*` and legacy ids — **not one on a `bmj-item-*` item.** So `.limit(100)` alone still ships an unpriced storefront. Root cause is a *recorded false premise*: `docs/chargebee_final_state.md:80` asserts *"Charge types use flat pricing via `item.price` field, not separate `item_prices`"*, and line 91 accepts the shortfall as `One-time item prices: 0 / 45 ⚠️`. **The live site contains 5 ItemPrices whose `item_type` is `charge`** — the premise is false; charge items do use `item_prices`. (`PR-18`) | read-only MCP `list_item_prices`, all 4 pages (100+100+100+14); cross-checked against the live catalog's 15 `itemId`s → **0 matched**; `docs/chargebee_final_state.md:79-80,91` | **Two parts:** (a) fix the code path (`PR-17`); (b) **create ItemPrices on the 15 `bmj-item-*` charge items — a Chargebee write, needs explicit go-ahead** (`D4`/`D6`) | 5 min code + ~1 h data |

**Why these were not in the original checklist:** the original was produced by reading code and grepping git, which finds missing files (`B8`) but cannot find a wrong `limit` argument (`B10`), a profile that is never set on a host that does not exist (`B9`), or a `401` returned by application code that looks like an auth failure (`B13`). `B10`, `B11` and `B13` were found **only** by running the artifact and reading the response *bodies* — asserting on status codes alone passes all three.



Real defects that are **not** launch-stopping. None leaks data, blocks a V1 flow or stops a payment.

| # | Bug | Class | Evidence | Action |
| :--- | :--- | :--- | :--- | :--- |
| **I1** | **12 pre-existing test failures** — 11 × `ProviderNotFoundException<ThemeCubit>` in `test/subscription_screens_test.dart`, 1 × `ProductCatalogEmpty` vs `ProductCatalogFiltered` drift in `test/unit/bloc/product_catalog_bloc_test.dart`. Both suites fail identically at clean `e1d11e6`, so they are debt, not regressions — but they mask regression signal on the subscription screens (flow 7). | POST-LAUNCH | `docs/BMJ_V1_SCOPE.md` §5 "The 12 pre-existing failures" | Add `BlocProvider<ThemeCubit>` to that test's helper; re-point the catalog assertion at `ProductCatalogFiltered`. ~1 h. |
| **I2** | **`GET /api/orders` page-scans the Chargebee account on every call.** `OrderApiService#getCustomerOrders` calls `Order.list().request()` (all orders) and then filters in memory by `customerId`. It works, but it is O(all orders) per request — latency and Chargebee rate-limit exposure as volume grows, for data that is already in `order_entity`. | POST-LAUNCH | `OrderApiService.java:35-56`; reached from the app via `OrderBloc` → `OrdersTab` / `OrderHistoryScreen` | Serve from the local `order_entity` cache (the `by-customer` path already does), or filter server-side in the Chargebee query. |
| **I3** | **Two parallel order-history implementations with different response shapes.** `OrderHistoryPage` uses `UserRepository.fetchOrders()` → `GET /api/orders/by-customer` (raw JSON array, now correct after `D-6`). `OrderHistoryScreen` / `OrdersTab` use `OrderBloc` → `GET /api/orders` (`{status, data}` envelope). Same user-visible feature, two code paths — easy to fix one and miss the other. | POST-LAUNCH | `user_repository.dart:27-54`; `bloc/OrderBloc/order_bloc.dart:32-71`; `services/order_service.dart:29-50` | Consolidate on one path (recommend the local-cache-backed `by-customer`) before the second order-UI iteration. |
| **I4** | **A test credential was committed to the repo.** `temp_signin.json` (tracked since 2026-05-20) contained a username/password pair for a UAT phone account. **The file was deleted on 2026-10-16** (`SAFE_DELETE_LIST.md` §A2), but **deletion does not purge it from git history** — it remains reachable via `git log --all -- temp_signin.json`. | POST-LAUNCH (with a pre-launch check) | `git log --all --oneline -- temp_signin.json` | Confirm the UAT account does **not** exist in production (or rotate its password), then purge history (`git filter-repo` / BFG) in a dedicated maintenance window. The password itself is deliberately **not reproduced in this document** (it was redacted 2026-10-16 alongside the file deletion). | 10 min to verify; 1–2 h if history is purged |
| **I5** | **`bmjServer/logs/**` is tracked and churns on every run** — 30 files, currently showing 19 deleted + 26 untracked + 3 modified. This is `W0` (`D-3`-adjacent): unless handled, the churn rides into the freeze commit, and application logs can carry customer identifiers. | POST-LAUNCH | §J.7 (options A/B) | **Recommended: option A** — `git rm -r --cached logs`, add `/logs/` to `bmjServer/.gitignore`, keep the files on disk. Option B (keep as UAT evidence) is acceptable if a review confirms no PII. Do this **before** B1. |
| **I6** | **The email-first signup surface still exists behind the removed entry point.** After `D-5` the screens are unreachable, but they remain registered routes (`/email-signup`, `/create-password`, `/signup`, `/signup-method-selection`) and `EmailSignupScreen` still renders a "Sign up with Email" title. `SignupMethodSelectionScreen` has no push site at all. | POST-LAUNCH | `lush/lib/main.dart:299-315`; `email_signup_screen.dart:17,76`; `signup_method_selection_screen.dart:16` | Delete the orphan screens + routes in the first post-launch iteration, or gate them behind a dev flag. Leaving them costs nothing at launch. |
| **I7** | **Google sign-in config is present but unverified against the release key.** `lush/android/app/google-services.json` now carries two Android OAuth clients plus the web client (`24122477606-…64c`) — the earlier "empty `oauth_client`" blocker documented in `HUMAN_INTERVENTION_REQUIRED.md` is resolved. Whether the release keystore's SHA-1 is registered in Firebase/Google Cloud is still unverified. | POST-LAUNCH | `lush/android/app/google-services.json`; `docs/HUMAN_INTERVENTION_REQUIRED.md` (H19 note) | Fold into the B5 device smoke: sign in with Google on a **release-signed** build. |

---

## 3. Nice-To-Have Items

Polish and hygiene. Nothing here should delay launch.

| # | Item | Class | Notes |
| :--- | :--- | :--- | :--- |
| **N1** | Delete the two stale root temp files (`temp_search.txt` 2026-05-13, `temp_signin.json` 2026-05-20 — the latter also covered by **I4**). | IGNORE | Both are tracked; removing them is a 1-minute cleanup whenever root is next touched. |
| **N2** | 405 analyzer issues (all `info`/lint-level, no errors) — the standing baseline across rows 4, 9 and 15. | POST-LAUNCH | Ratchet a few at a time; the count is unchanged by the freeze, so nothing regressed. |
| **N3** | Dead code flagged by the analyzer: `menu_tab.dart:_cachedOneTimeCategories` (unused field), `active_subscription_screen.dart:_formatDate` (unreferenced element), `day_wise_schedule_screen.dart:329 juiceName` (unused local). | POST-LAUNCH | All in files untouched by the freeze. |
| **N4** | Decide what to do with the untracked root `Stitch/` folder (31 design exports) — vendor it, or move it to the design repo. | POST-LAUNCH | Untracked, so it neither ships nor breaks the build; it just makes `git status` noisy. |
| **N5** | Confirm production observability is wired: `sentry_flutter` is a dependency — verify the DSN is set for the release build so launch-day crashes are visible. | POST-LAUNCH | App-side config check. |
| **N6** | Review the existing rate limits (`RateLimitingFilter` covers `/api/auth/send-otp`, `/api/auth/signin`, …) against expected launch traffic, so OTP abuse cannot burn the SMS budget on day one. | POST-LAUNCH | Limits already exist; this is a tuning decision, not a gap. |

---

## 4. Technical Debt Deferred

Architectural and process debt. Explicitly **not** fixed by the freeze; none changes what a customer can do on day one.

| # | Debt | Class | Why it can wait |
| :--- | :--- | :--- | :--- |
| **T1** | **`D-3` — branch strategy for the two nested repos.** `lush/` and `bmjServer/` are independent git repos (not submodules), both still on `main`, while the root repo sits on `feat/v1-launch-freeze`. There is no release branch or tag anywhere, so "which code is live" is currently unanswerable. | POST-LAUNCH | Tagging the freeze commit in all three repos (part of **B1**) removes the immediate risk; a durable branch/tag policy is a process decision, not a launch gate. |
| **T2** | **`G-6` — unversioned controllers.** `/api/v1/catalog` and `/api/v1/user` were added by the freeze, but `/api/orders`, `/api/subscriptions`, `/api/invoices`, `/api/bottles` and `/api/referral` remain unversioned. | POST-LAUNCH | Additive change; existing clients keep working. Version them when the next contract change lands. |
| **T3** | **`G-7` / `G-8` — the `/api/test/**` namespace is still shipped.** ~30 endpoints remain across `TestController`, `OrdersController`, `CheckoutController` and `MetadataTestController`; the namespace stays `permitAll` and is now documented rather than restricted. The one live exposure is **B2**. | POST-LAUNCH | Retire the namespace or profile-gate it (`@Profile("!prod")`) in the next iteration. `MetadataTestController` is already ADMIN-guarded. |
| **T4** | **`G-12` — `ProductsBloc` vs `ProductCatalogBloc` duplication.** The freeze deleted `subscription_service_v2.dart`, but the two catalogue blocs remain. | POST-LAUNCH | Duplication, not divergence; both currently hit the production catalogue route. |
| **T5** | **`G-13` — the 0-byte `OneTimeCheckoutController.java`.** | IGNORE | Empty file; it compiles to nothing and is referenced by no route. Recorded so it is not re-raised. |
| **T6** | **`D-4` — breadth of the `410 Gone` guarantee.** Only `lush/integration_test/fullstack_auth_and_pricing_test.dart` asserts that the retired Chargebee Portal / Pricing-Page routes stay gone. | POST-LAUNCH | The routes are already `410`; this is missing coverage on a retired surface. |
| **T7** | **`docs/API.md` drift (C-1, C-2).** The document still describes one Chargebee webhook endpoint while 13 exist, and one checkout contract while four mechanisms coexist. The freeze added a *V1 Launch Freeze — Contract Changes* section, which mitigates but does not fix the drift. | POST-LAUNCH | Documentation-only; corrected in the post-launch doc pass. |
| **T8** | **`user_repository.dart` residual line-ending churn** — 25/261 of a 279-line refactor. The committed blob is mixed-EOL (1480 CRLF + 18 LF), so no `.gitattributes` or normalization script can reproduce it byte-for-byte. | IGNORE | Review-noise only; the file's content is correct and it builds, analyzes and tests clean. Accepted as-is. |
| **T9** | **Test-count documentation is stale.** `docs/test-baselines/TEST_BASELINE.md`, `docs/test-registry/COVERAGE_REPORT.md` and `docs/QUALITY_MANAGEMENT.md` quote counts from before the freeze (e.g. `subscription_service_test.dart` "23 tests") even though the freeze dropped the `modifySchedule` group. | POST-LAUNCH | Pure documentation refresh; the executable truth is `flutter test` (351/12). |

> **Reminder from §1:** the remaining `/api/test/**` routes (other than `GET /api/test/orders`, **B2**)
> were kept in place and documented on purpose (`G-7`/`G-8` partial); `bmjServer/logs/**` churn and
> `D-3` are process noise rather than onboarding risk.

---

## 5. Recommended Launch Date Readiness

### Can BookMyJuice onboard real paying users tomorrow?

**No — not with today's tree. But it is roughly one working day away, and no part of the gap is architectural.**

The freeze itself is in good shape: the server compiles, the app analyzes clean, and every
customer-facing flow points at a production route. What is missing is not code quality — it is that
**the verified work is not committed, one unauthenticated endpoint returns every customer's order PII,
and nothing has been exercised end-to-end.**

### Why not tomorrow

| Reason | Blockers | Character |
| :--- | :--- | :--- |
| Nothing verified is deployable — the freeze is uncommitted in all three repos and two deliverables are untracked | **B1** (+ **B7**, §2 I5) | Process, hours |
| `GET /api/test/orders` serves all customers' order PII (incl. shipping/billing addresses) to anonymous callers | **B2** | Security, one line |
| `D-6` and `D-2` are implemented but unproven against real data | **B3**, **B4** | Verification, minutes |
| No live E2E evidence at all: no real OTP delivery, no real payment | **B5** | Verification, hours |
| A paying subscriber cannot pause/cancel in-app (needs the UI, or a published support process) | **B6** | Product decision |

### What is already proven (the floor)

| Proven | Evidence |
| :--- | :--- |
| Server compiles with the whole freeze + D-2/D-5/D-6 in place | `mvnw.cmd -o -DskipTests compile` → **BUILD SUCCESS**, 172 sources |
| Client static analysis is clean | `dart analyze lib test integration_test` → **0 errors**, 405 baseline lints |
| No test regressions from any change | `flutter test` → **351 passed / 12 failed**, failure set identical to clean `e1d11e6` |
| No customer-facing flow calls `/api/test/*` any more | 2 comment-only hits remain in `lush/lib` |
| Every in-scope flow points at a production route | `docs/BMJ_V1_SCOPE.md` §4 mapping rows A–I |
| Order-history id mapping is fixed (`D-6`) | `OrderController#resolveChargebeeCustomerId` |
| Signup/sign-in always reaches a Chargebee customer (`D-2`) | `unified-signup` + Google repair + new `login-otp` backfill |
| Email + password signup is no longer advertised (`D-5`) | Sign Up tab = Phone (OTP) + Google; `login_page_test.dart` 21/21 |
| Google sign-in OAuth config is present | `lush/android/app/google-services.json` (2 Android clients + web client) |

### Green light — do not open the doors until every row is ✓

| Gate | Evidence required | Owner |
| :--- | :--- | :--- |
| B1 | Freeze committed + pushed + tagged in all three repos; release artefact built from that tag | Repo owner |
| B7 + I5 | `home_tab.dart` / `menu_tab.dart` committed separately or stashed; `logs/**` untracked or reviewed | Repo owner |
| B2 | `GET /api/test/orders` no longer returns data to an anonymous caller (verified with a token-less request) | Backend |
| B3 | `GET /api/orders/by-customer` returns a **populated** array for a seeded user, and `[]` for one without a Chargebee customer | Backend + QA |
| B4 | `login-otp` persists a Chargebee id for a legacy null-id account, and checkout then succeeds | Backend |
| B5 | Staging smoke: Google signup **and** OTP signup → catalog → cart → paid → order in history → subscription in `/manage-subscriptions` | QA |
| B6 | Either the in-app pause/cancel entry point ships, or Product signs off the support-process fallback in writing — **and** `B13` is resolved either way | Product |
| B8 | A **clone of the repo** contains `CatalogController.java`; a build from that clone returns items from `/api/v1/catalog/charge-items` | Repo owner |
| B9 | `journalctl -u bmj-backend` shows `The following 1 profile is active: "prod"`; `ddl-auto` is `validate` | Backend |
| B10 | `/api/v1/catalog/charge-items` returns items **with a non-empty `prices` array** (smoke probe 2b passes) — **`B14` must be closed first**: no code change can populate an empty price set | Backend + Chargebee |
| B14 | A read-only census shows `bmj-item-*` charge items carrying **ItemPrices in Chargebee** (≥1 per catalog item); the catalog's 15 item ids and the price `item_id` set intersect | Chargebee |
| B11 | An unreachable Chargebee + empty cache does **not** present as `200 []` | Backend |
| B12 | `GET /api/user/profile` response contains **no** `password` field (smoke probe 8 passes) | Backend |
| B13 | `GET /api/subscriptions/my` returns `200` for a signed-in account with no Chargebee customer | Backend |

### Earliest realistic dates

| Scenario | Date | Conditions |
| :--- | :--- | :--- |
| **Full sign-off (recommended)** | **~2 working days** (≈ 18 Oct 2026) | All blockers closed — B1–B7 plus the smoke's `B8`–`B14` — including B6 option (a). Staging smoke repeated on the release build. |
| **Conditional launch** | **Tomorrow is achievable** | Requires, in roughly half a day: B1 + B7 + B2 (one line) + B3 + B4, then the B5 smoke — **and** Product signing off B6 as option (b), a published "contact support to pause/cancel" process. |
| **Not acceptable under any scenario** | — | Shipping with **B2** open. Exposing every customer's order *and* address data to unauthenticated callers is not a trade-off a paid launch can make. |

**Verdict:** *BookMyJuice cannot take paying customers tomorrow as the tree stands, but there is no
architectural work between here and launch. Close B1–B7 — about a day of process, verification and one
one-line security fix — and the product is ready to onboard real subscribers.*

**Revised 16 October 2026, after the live smoke.** The blocker count is **14, not 7**, and the day-long
estimate no longer holds: `B8`–`B13` were found only by *running* the artifact, `B14` by then *counting the upstream price data*, and three of them
(`B9`, `B10`, `B12`) are one-to-five-line fixes whose absence would have shipped a storefront with no
prices, a production database mutated without review, and a password hash in a response body. The
architecture is still frozen and none of the new items reopens it — but the honest statement is now:
**the artifact runs; the environment, the payload and three security/robustness edges are not yet
launch-ready, and the deployed half of `B5` cannot even be attempted until `PR-4` is decided.**

---

## Appendix — how this checklist was produced

Every claim above is traceable to one of these commands (run from `x:\BMJ` unless noted).

| # | Question | Command |
| :--- | :--- | :--- |
| 1 | Is the freeze committed? | `git status --porcelain`; then the same with `-C lush` and `-C bmjServer`; plus `git -C lush log --oneline -1` / `git -C bmjServer log --oneline -1` |
| 2 | Does the server compile? | `cd bmjServer; .\mvnw.cmd -o -DskipTests compile` |
| 3 | Is the client analyzable? | `cd lush; dart analyze lib test integration_test` |
| 4 | Do the tests pass, and did anything regress? | `cd lush; flutter test` (then diff the `[E]` failure lines against a clean `e1d11e6` worktree) |
| 5 | Are the `D-5`/`D-6` behaviours asserted? | `cd lush; flutter test test\widget\screens\login_page_test.dart` |
| 6 | Is any `/api/test/*` still called by the app? | `Get-ChildItem lush\lib -Recurse -Filter *.dart \| Select-String 'api/test'` |
| 7 | Is the `/api/test/orders` exposure real? | Read `WebSecurityConfig.java:88-97`, `OrdersController.java:40-48`, `OrderResponseMapper.java:13-62` |
| 8 | Is the `D-6` fix in place? | Read `OrderController.java` (`resolveChargebeeCustomerId`, `by-customer`) |

**Maintenance:** this checklist is a point-in-time gate for the 16 October 2026 tree. Re-run commands
1–5 before acting on it; after the freeze is committed, cite the tag (`v1.0.0-launch`) instead of
working-tree state.





