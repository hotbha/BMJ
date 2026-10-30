# BMJ V1 Launch Scope & API Contract Freeze

> **Status:** Frozen for V1 launch (Google sign-in + OTP).
> **Owner:** Engineering.
> **Companion documents:** [API.md](API.md) ·
> [PRODUCT_ALIGNMENT_REPORT.md](../PRODUCT_ALIGNMENT_REPORT.md) ·
> [architecture/ADR-003-chargebee-integration-strategy.md](architecture/ADR-003-chargebee-integration-strategy.md) ·
> [chargebee_final_state.md](chargebee_final_state.md)

---

## 1. Purpose

This document is the **contract of record** for the V1 launch. It freezes:

1. Which customer-facing flows ship in V1.
2. Which backend routes those flows are allowed to call.
3. The rule that **no customer-facing V1 flow may depend on `/api/test/*`**.

If a flow or route is not listed here as in-scope, it is out of scope for V1.

---

## 2. In-scope V1 flows

| # | Flow | Entry point | Production API surface |
| :--- | :--- | :--- | :--- |
| 1 | Google sign-in / sign-up | `LoginPage` → `GoogleSignupScreen` | `/api/auth/google`, `/api/auth/unified-signup` |
| 2 | OTP sign-in / sign-up | `PhoneSignupScreen`, `PhoneOtpVerificationScreen`, `phone_login_screen.dart` | `/api/auth/send-otp`, `/api/auth/verify-otp`, `/api/auth/login-otp`, `/api/auth/unified-signup` |
| 3 | Catalog browse (Products screen) | `ProductCatalogScreen`, `menu.dart`, `menu_tab.dart` | `GET /api/v1/catalog/charge-items` |
| 4 | Cart | `CartScreen`, `CartBloc` → `CartRepository` | `/api/v1/cart/**` |
| 5 | One-time checkout | `CartScreen` → Chargebee Hosted Page | `POST /api/v2/checkout/with-items` |
| 6 | Order history | `OrderHistoryPage`, `OrderHistoryScreen` | `GET /api/orders/by-customer` ✅, `GET /api/orders/{id}` |
| 7 | Subscription list / pause / resume / cancel | `SubscriptionManagementScreen`, `SubscriptionBloc` | `GET /api/subscriptions/my`, `PUT /api/subscriptions/{id}/pause`, `PUT /api/subscriptions/{id}/resume`, `PUT /api/subscriptions/{id}/cancel` |
| 8 | Plan catalogue | `PlanSelectionScreen`, `subscription_plans_screen.dart` | `GET /api/subscriptions/pricing/plans` |
| 9 | Profile read | `getUserDetailsFromServer()` | `GET /api/v1/user/profile` |
| 10 | Address book | `AddressScreen`, `address_repository` | `GET /api/v1/user/profile` (read), `/api/v1/address/**` |

> ✅ **Flow 6 caveat — resolved 2026-10-16 (`D-6` approved and implemented).** The route used to
> return an empty list because of a pre-existing id-mapping defect. `OrderController` now resolves the
> **Chargebee** customer id (`resolveChargebeeCustomerId`) before querying, so the flow returns the
> customer's real orders. See *“Order-history id mapping — fixed”* in §5 and
> `PRODUCT_ALIGNMENT_REPORT.md` §J.5.

---

## 3. Out of scope for V1

These were explicitly retired or deferred, and **must not be reintroduced** without a
new ADR:

| Capability | Status | Why |
| :--- | :--- | :--- |
| Chargebee Portal (Self-Serve Page) | **Retired — HTTP 410 Gone** | Replaced by native `SubscriptionManagementScreen` |
| Chargebee Pricing Pages (plan discovery / comparison / plan change) | **Retired — HTTP 410 Gone** | Replaced by native plan + billing screens |
| Day-wise schedule modification (`PUT /api/subscriptions/{id}/modify`) | **Removed** | Never implemented server side; the client call was deleted so no 404 remains |
| Email + password sign-up as the primary path | Deferred — **de-advertised 2026-10-16** | V1 launch is Google + OTP; `/api/auth/unified-signup` is retained only as the signup completion step for those two flows. **`D-5` implemented:** the “Sign up with Email” card was removed from the LoginPage Sign Up tab, so the path is no longer offered; its screens remain in the tree but are unreachable |
| Bottle tracking UI | Backend ready, no V1 screen | See `PRODUCT_ALIGNMENT_REPORT.md` §C-7 |
| Notification centre | Backend ready, no V1 screen | See `PRODUCT_ALIGNMENT_REPORT.md` §C-6 |

---

## 4. Endpoint mapping (old → new)

Every customer-facing dependency on the non-production `/api/test/*` namespace was
replaced by a production route. Behaviour is preserved: the production handlers
delegate to the **same service methods** and return the **same payloads**.

| # | Flutter call site (before) | Endpoint (before) | Endpoint (after) | Server handler | Behaviour change |
| :--- | :--- | :--- | :--- | :--- | :--- |
| A | `user_repository.dart::getChargeItems()` | `GET /api/test/charge-items` | `GET /api/v1/catalog/charge-items` | `CatalogController#getChargeItemsWithCategoriesAndSizes` (NEW) | None — same `ItemService` query, same JSON array. Also mapped at `/api/catalog/charge-items`. |
| B | `user_repository.dart::getUserDetailsFromServer()` | `GET /api/test/user` | `GET /api/v1/user/profile` | `UserProfileController#getProfile` (NEW) | None — same `User` payload, same role rule. Also mapped at `/api/user/profile`. |
| C | `user_repository.dart::getCartCheckoutUrl()` (from `cart_screen.dart`) | `POST /api/test/cartCheckout` | `POST /api/v2/checkout/with-items` | `CheckoutV2Controller#createCheckoutWithItems` (existing) | **Bug fix, intended:** the legacy route passed the local user id where Chargebee expects a customer id. The production path resolves `chargebeeCustomerId`, so checkout no longer fails with `Chargebee customer ID not found`. Request body is now `{"items":[{"price_id","quantity"}]}`; response is read from `data.url`. |
| D | `user_repository.dart::fetchOrders()` (from `order_history_page.dart`) | `GET /api/test/ordersByCustomerId` | `GET /api/orders/by-customer` | `OrderController#getOrdersByCustomerId` (NEW alias) | None — **proven identical lookup.** The retired route passed `JwtUtils.getUserIdFromSecurityContext()` and the new route passes `OrderController#getCustomerIdFromSecurityContext()`; both return `userDetails.getId().toString()`, and both call `orderService.fetchOrdersByCustomerId(customerId)` → `orderRepository.findByCustomerId(customerId)`. Same raw array. |
| E | `SubscriptionBloc` → `SubscriptionService.cancelSubscription()` | `PUT /api/subscriptions/{id}/cancel` → **404** | `PUT /api/subscriptions/{id}/cancel` | `SubscriptionController#cancelSubscriptionViaPut` (NEW alias → existing `DELETE /{id}` logic) | **404 removed.** Same Chargebee cancel, same 9 PM IST cutoff, same `202 Accepted`. |
| F | `SubscriptionBloc` → `SubscriptionService.modifySchedule()` | `PUT /api/subscriptions/{id}/modify` → **404** | *(client call deleted)* | — | **404 removed by deleting the caller.** Schedule modification is out of V1 scope and has no server implementation; the orphaned `modify_schedule_screen.dart` and the bloc event/state were removed with it. |
| G | `services/subscription_service_v2.dart::getPricingPageUrl()` | `GET /api/subscriptions/pricing-page` → **404** | *(file deleted)* | — | **404 removed by deleting the file.** It was an unreferenced duplicate of `subscription_service.dart` (0 imports repo-wide). |
| H | `user_repository.dart::getPricingPageUrl()` / `getPricingPageUrls()` | `GET /api/test/generate_pricing_page_session_url` → **410 Gone** | *(client methods deleted)* | — | **410 dependency removed.** Pricing Pages are retired by architecture decision; the client chain (`getSubscriptionPageUrl`, `getPricingPageUrl`, `getPricingPageUrls`, `pricingPageUrlsMap`, `isUrlvalid`) had **zero callers**. |
| I | `user_repository.dart::fetchSelfServePageUrlFromServer()` (from `welcome_header.dart`) | `GET /api/test/portal` → **410 Gone** | *(client method deleted)* | — | **410 dependency removed.** The Chargebee Portal is retired; `WelcomeHeader` now opens the native `SubscriptionManagementScreen` (`/manage-subscriptions`). |

### Production API additions

| Method | Route | Class | Notes |
| :--- | :--- | :--- | :--- |
| GET | `/api/v1/catalog/charge-items` (alias `/api/catalog/charge-items`) | `CatalogController` (new) | Delegates to `ItemService#getChargeItemsWithCategoriesAndSizes()`. `permitAll` in `WebSecurityConfig`, mirroring the legacy route's effective access. |
| GET | `/api/v1/user/profile` (alias `/api/user/profile`) | `UserProfileController` (new) | Authenticated. Returns the `User` entity. |
| GET | `/api/orders/by-customer` | `OrderController` (extended) | Authenticated. Delegates to `OrderService#fetchOrdersByCustomerId()`. |
| PUT | `/api/subscriptions/{subscriptionId}/cancel` | `SubscriptionController` (extended) | Authenticated alias for `DELETE /api/subscriptions/{subscriptionId}`. |

---

## 5. Non-production namespace policy (`/api/test/*`)

- `/api/test/**` is **development / diagnostics only**. It is `permitAll` in
  `WebSecurityConfig` and must never carry customer-facing traffic.
- The controllers in that namespace (`TestController`, `CheckoutController`,
  `PricingPageController`, `SelfServePageController`, `MetadataTestController`) are
  marked `@Deprecated` and documented as **NON-PRODUCTION**. `OrdersController` was
  **deleted on 2026-10-16** (blocker `B2` — see §7).
- `OrdersController` was the one route in this namespace that leaked PII:
  `GET /api/test/orders` returned `OrderService#fetchOrders()` for **all** customers,
  unauthenticated. It was deleted rather than authorized because it had zero callers in
  any repository and both its routes have production replacements.
- The full inventory and the production replacement for each route is published in
  [API.md → Non-Production Endpoints](API.md#non-production-endpoints-apitest).
- **Regression guard:** `lush/integration_test/fullstack_auth_and_pricing_test.dart`
  asserts that the retired routes keep returning `410 Gone`.

### Verification performed

Rows 1–7 were executed on 2026-10-15; rows 8–11 on 2026-10-16, after the repo-hygiene pass
described in [PRODUCT_ALIGNMENT_REPORT.md](../PRODUCT_ALIGNMENT_REPORT.md) §J.7; rows 12–16 on
2026-10-16, after implementing the approved decisions **D-2 / D-5 / D-6**. All observations are
recorded verbatim.

| # | Check | Command | Observed result |
| :--- | :--- | :--- | :--- |
| 1 | No `lush/lib` → `/api/test/*` **call site** remains | `Get-ChildItem -Recurse -Filter *.dart lib \| Select-String 'api/test'` | 2 hits, **both comment-only** (`welcome_header.dart:20` explanatory note, `product_catalog_bloc.dart:198` route comment — corrected to `/api/v1/catalog/charge-items`) |
| 2 | Production routes are what the client actually calls | `Select-String 'api/v1/catalog\|api/v1/user/profile\|api/orders/by-customer\|api/v2/checkout/with-items\|subscriptions/.*cancel'` on `lush/lib` | `/api/v1/catalog/charge-items` (`user_repository.dart:160`), `/api/v1/user/profile` (`:1013`, `:1021`), `/api/orders/by-customer` (`:34`), `/api/v2/checkout/with-items` (`:70`), `/api/subscriptions/{id}/cancel` (`subscription_service.dart:171`) |
| 3 | Server compiles with the freeze in place | `bmjServer\mvnw.cmd -o -DskipTests compile` | **BUILD SUCCESS** — `Compiling 172 source files`; `CatalogController.class` and `UserProfileController.class` emitted to `target/classes` |
| 4 | Flutter static analysis | `lush\dart analyze lib test integration_test` | **0 errors**, 38 warnings, 367 info (all pre-existing lint noise; no new diagnostics) |
| 5 | Flutter test suite | `lush\flutter test` | **351 passed, 12 failed** |
| 6 | Focused V1-freeze unit suites | `lush\flutter test test\unit\services\subscription_service_test.dart test\subscription_bloc_test.dart` | **59/59 pass** (`All tests passed!`) |
| 7 | Are those 12 failures caused by the freeze? | clean-HEAD worktree (`git worktree add … HEAD --detach`) + same two test files | **Same 12 failures at HEAD `e1d11e6` (`+18 -12`)** → **0 regressions attributable to the freeze** |
| 8 | Server still compiles **after** the line-ending normalization of `CheckoutController` / `OrderController` / `OrdersController` (§J.7 item 2) | `bmjServer\mvnw.cmd -o -DskipTests compile` | **BUILD SUCCESS** — `Compiling 172 source files` |
| 9 | Flutter static analysis after the same normalization | `lush\dart analyze lib test integration_test` | **0 errors** (405 issues — all `info`-level lints, the same baseline as row 4) |
| 10 | Freeze diff carries no line-ending-only churn | `git -C bmjServer diff --numstat` / `git -C lush diff --numstat` | Churn removed from 4 files (`CheckoutController` 84/67 → **17/0**, `OrderController` 199/168 → **31/0**, `OrdersController` 48/29 → **19/0**, `fullstack_auth_and_pricing_test.dart` 42/68 → **31/57**) plus `lush/.gitignore` 49/44 → **5/0**; one residual, `user_repository.dart` (§J.7) |
| 11 | The freeze sits exactly on the baseline commit used in row 7 — no drift, nothing committed yet | `git -C lush rev-parse --abbrev-ref HEAD` → `main`; `git -C lush --no-pager log --oneline -1` → `e1d11e6`; same two commands in `bmjServer` → `main` / `fa34ca9` | **Same commit** — in all three repos the freeze is **uncommitted working-tree state**, so row 7 compares against the literal parent state. Root repo is on `feat/v1-launch-freeze`; the nested repos have **no release branch** (**D-3**) |
| 12 | **D-2** — `login-otp` Chargebee backfill added | `bmjServer\mvnw.cmd -o -DskipTests compile` | **BUILD SUCCESS** — `Compiling 172 source files`. Best-effort block in `AuthController#loginViaOtp` (mirrors the Google Step 7 repair; a Chargebee failure is logged and sign-in still succeeds) |
| 13 | **D-6** — order-history id mapping fixed | `bmjServer\mvnw.cmd -o -DskipTests compile` + source review | **BUILD SUCCESS**. `OrderController#resolveChargebeeCustomerId` implements the `SubscriptionController:310-330` pattern; `GET /api/orders/by-customer`, `GET /api/orders` and `GET /api/orders/local/history` all resolve through it. **Not verified against a populated account** — needs a user with a Chargebee customer *and* a synced order (`BMJ_LAUNCH_CHECKLIST.md` §1) |
| 14 | **D-5** — email signup no longer advertised | `lush\flutter test test\widget\screens\login_page_test.dart` | **21/21 pass**, including the rewritten *“Sign Up tab shows the two V1 method cards”* which asserts `Sign up with Email` is `findsNothing` |
| 15 | Flutter static analysis after D-2/D-5/D-6 | `lush\dart analyze lib test integration_test` | **0 errors** — 405 issues, the **identical count** to rows 4 and 9 (no new diagnostics; all `info`/lint-level) |
| 16 | Flutter test suite after D-2/D-5/D-6 | `lush\flutter test` | **351 passed, 12 failed** — the same 12 failures listed below, confirmed by diffing the `[E]` failure lines against row 5 → **0 regressions** |

#### The 12 pre-existing failures (not caused by this change)

| Suite | Count | Root cause |
| :--- | :--- | :--- |
| `test/subscription_screens_test.dart` | 11 | `ProviderNotFoundException: Could not find the correct Provider<ThemeCubit>` — the test helper `buildTestApp()` only installs `BlocProvider<SubscriptionBloc>`, while `SubscriptionPlanScreen` / `SubscriptionScheduleScreen` / `SubscriptionSummaryScreen` read `ThemeCubit` from context. Test-harness gap in an **unmodified** file. |
| `test/unit/bloc/product_catalog_bloc_test.dart` | 1 | `FilterByCategory emits [Empty] when filter matches no items` expects `ProductCatalogEmpty`, bloc emits `ProductCatalogFiltered`. Test drift introduced when the filtered-state behaviour landed (HEAD `b4932b2` “catalog chips persist after filter”). |

Both suites and both production widgets are untouched by this freeze (see §6), and both
fail identically from a pristine checkout of HEAD, so they are recorded here as
pre-existing debt rather than V1 regressions.

---

### Order-history id mapping — fixed 2026-10-16 (`D-6`)

> **Status: ✅ FIXED.** This section originally documented a defect that the freeze preserved 1:1 from
> the retired route. Decision **`D-6`** was subsequently approved and implemented, so in-scope
> **flow 6 (Order history)** now returns real data. The mechanism is retained below as the evidence
> base for the fix.

`OrderEntity.customerId` holds the **Chargebee** customer id — it is written only by
`OrderMapper.toEntity(Order)` / `OrderMapper.toEntity(Order, OrderEntity)`, which copy
`order.customerId()` (e.g. `cbdemo_xxxxx`) from the Chargebee order. `OrderRepository` declares a
plain derived query: `List<OrderEntity> findByCustomerId(String customerId)` → `WHERE customer_id = ?`.

Both the retired route and the new one pass the **local numeric user id**:

| | Value passed to `fetchOrdersByCustomerId(String)` |
| :--- | :--- |
| `GET /api/test/ordersByCustomerId` (retired) | `JwtUtils.getUserIdFromSecurityContext()` → `userDetails.getId().toString()` |
| `GET /api/orders/by-customer` (new) | `OrderController#getCustomerIdFromSecurityContext()` → `userDetails.getId().toString()` |

So `findByCustomerId("42")` never matches `cbdemo_xxxxx` → **`GET /api/orders/by-customer` returns `[]`**,
and it did so before the freeze too. The lookup is *identical*, so this is **not a regression** — it is
a latent defect the migration neither caused nor cured.

The canonical, correct pattern already exists in the same codebase —
`SubscriptionController#getCustomerIdFromSecurityContext()` (`SubscriptionController.java:310-330`)
resolves the local id via `userRepository.findById(localId)` and returns
`user.getChargebeeCustomerId()`. Its Javadoc states the rule outright:

> *"This ensures we send the Chargebee Customer ID (e.g. `cbdemo_xxxxx`) to Chargebee APIs, not the
> local database auto-increment ID."*

**Applied fix (2026-10-16, decision `D-6`):** `OrderController#getCustomerIdFromSecurityContext()` was
replaced by `resolveChargebeeCustomerId(Long localUserId)`, which implements the `SubscriptionController`
pattern above — `userRepository.findById(localId)` → `getChargebeeCustomerId()`, with the legacy
`CustomerRepository` fallback — and all three order read routes now pass that id to the service layer.
When no Chargebee id is resolvable the endpoints return an **empty** collection with `200` (the shape
users saw before the fix) rather than a misleading `401`.

> **Verification gap:** the populated response can only be proven with a live user who has a Chargebee
> customer *and* at least one synced order. That live check is an open item — see
> `BMJ_LAUNCH_CHECKLIST.md` §2.

---

## 6. Files changed for the V1 freeze

**Server (`bmjServer/`)**

| File | Change |
| :--- | :--- |
| `src/main/java/com/bookmyjuice/controllers/CatalogController.java` | **NEW** — `GET /api/v1/catalog/charge-items` (+ `/api/catalog/...`). |
| `src/main/java/com/bookmyjuice/controllers/UserProfileController.java` | **NEW** — `GET /api/v1/user/profile` (+ `/api/user/...`). |
| `src/main/java/com/bookmyjuice/controllers/OrderController.java` | Added `GET /api/orders/by-customer`. **`D-6` fix (2026-10-16):** the local-id → Chargebee-id resolution (`resolveChargebeeCustomerId`) now backs all three order read routes, so order history returns real data instead of `[]`. |
| `src/main/java/com/bookmyjuice/controllers/AuthController.java` | **`D-2` fix (2026-10-16):** `POST /api/auth/login-otp` backfills `chargebeeCustomerId` (best-effort `Customer.create()`) for an existing user who has none, mirroring the Google sign-in repair block. Removes the permanent checkout dead-end. |
| `src/main/java/com/bookmyjuice/controllers/SubscriptionController.java` | Added `PUT /api/subscriptions/{subscriptionId}/cancel` alias. |
| `src/main/java/com/bookmyjuice/security/WebSecurityConfig.java` | `permitAll` for `/api/catalog/**`, `/api/v1/catalog/**`. |
| `src/main/java/com/bookmyjuice/controllers/TestController.java` | Marked `@Deprecated` + NON-PRODUCTION Javadoc; documents the two production replacements. |
| `src/main/java/com/bookmyjuice/controllers/OrdersController.java` | **DELETED 2026-10-16 (`B2`).** Was marked `@Deprecated` + NON-PRODUCTION Javadoc; removed outright because `GET /api/test/orders` served every customer's order PII (incl. shipping/billing addresses) to anonymous callers. Replacements: `GET /api/orders/admin/all-orders` (ADMIN) and `GET /api/orders/by-customer`. |
| `src/main/java/com/bookmyjuice/controllers/CheckoutController.java` | Marked `@Deprecated` + NON-PRODUCTION Javadoc (notes the local-id-vs-Chargebee-customer-id defect). |
| `src/main/java/com/bookmyjuice/controllers/MetadataTestController.java` | Marked `@Deprecated` + NON-PRODUCTION Javadoc. |
| `src/main/java/com/bookmyjuice/controllers/PricingPageController.java` | Already `@Deprecated(forRemoval = true)`; returns `410 Gone`. |
| `src/main/java/com/bookmyjuice/controllers/SelfServePageController.java` | Already `@Deprecated(forRemoval = true)`; returns `410 Gone`. |

**Flutter (`lush/`)**

| File | Change |
| :--- | :--- |
| `lib/UserRepository/user_repository.dart` | Repointed 4 endpoints to production; removed the dead pricing-page / portal chain (7 methods, 251 lines). |
| `lib/views/screens/cart_screen.dart` | Checkout payload key `itemPriceId` → `price_id`. |
| `lib/views/widgets/welcome_header.dart` | Opens native `/manage-subscriptions` instead of the retired Chargebee Portal webview. |
| `lib/services/subscription_service.dart` | Removed `modifySchedule` (no server route). |
| `lib/bloc/SubscriptionBloc/subscription_bloc.dart` | Removed `ModifySubscriptionSchedule` event, `SubscriptionModified` state and its handler. |
| `lib/views/screens/subscription/modify_schedule_screen.dart` | **DELETED** (orphaned). |
| `lib/services/subscription_service_v2.dart` | **DELETED** (unreferenced duplicate containing the 404 `pricing-page` contract). |
| `lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart` | Stale `/api/test/charge-items` route comment corrected to `/api/v1/catalog/charge-items` (comment only, no behaviour change). |
| `test/unit/services/subscription_service_test.dart` | Dropped the `modifySchedule` group. |
| `test/subscription_bloc_test.dart` | Dropped the `ModifySubscriptionSchedule` group. |
| `lib/views/screens/login_page.dart` | **`D-5` (2026-10-16):** removed the “Sign up with Email” method card; the Sign Up tab now offers **Phone (OTP)** and **Google** only. |
| `test/widget/screens/login_page_test.dart` | Sign-Up-tab expectations updated to the two V1 method cards; asserts `Sign up with Email` is absent. |
| `integration_test/full_e2e_test.dart` | T1.12/T1.13 now assert the V1 method set and that email signup is not advertised. |
| `integration_test/cart_test.dart`, `integration_test/physical_device_template_test.dart` | The two email-first signup templates are marked `skip: true` (they logged in through the removed surface) and need re-authoring against the V1 entry. |
| `integration_test/fullstack_auth_and_pricing_test.dart` | Asserts production profile/checkout contracts + `410 Gone` for retired routes. |
| `integration_test/cart_test.dart` | Uses `POST /api/v2/checkout/with-items`. |

**Docs**

| File | Change |
| :--- | :--- |
| `docs/BMJ_V1_SCOPE.md` | **NEW** — this document. |
| `docs/API.md` | Added `### Catalog`, `GET /api/orders/by-customer` (with the `D-6` caveat), a subscription cancel contract note, and `### Non-Production Endpoints (/api/test/*)`. |

---

## 7. Rules for future changes

1. Adding a customer-facing flow requires a new row in §2 of this document.
2. A customer-facing flow may only call routes listed in §2 or §4.
3. Never point new code at `/api/test/*`. If you need data that only exists there,
   add a production route in the appropriate namespace and record it in §4.
4. Retiring a route means **deleting the client caller**, not just returning an
   error — see rows F, G, H and I for the pattern.



