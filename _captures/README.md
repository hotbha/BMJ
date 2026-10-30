# Before / After screen captures (vibrant_zest migration)

True before/after renders for the four priority screens:

| # | Screen | Before (HEAD) | After (working tree) | Side-by-side |
|---|--------|---------------|----------------------|--------------|
| 1 | Home dashboard | `before/01_home.png` | `after/01_home.png` | `compare/01_home_before_after.png` |
| 2 | Product detail (PDP) | `before/02_pdp.png` | `after/02_pdp.png` | `compare/02_pdp_before_after.png` |
| 3 | Cart summary | `before/03_cart.png` | `after/03_cart.png` | `compare/03_cart_before_after.png` |
| 4 | Subscription dashboard | `before/04_subscription.png` | `after/04_subscription.png` | `compare/04_subscription_before_after.png` |

`after/02_pdp.png` was regenerated after the PDP pass (hero "Select options",
dedicated "Select a size" block, "Key ingredients", pinned bottom CTA) so the
comparison shows the migrated flow, not the earlier mid-migration state.

## 2026-10-29 refresh (visual alignment pass)

All eight goldens were regenerated against
[`VISUAL_ALIGNMENT_AUDIT.md`](../VISUAL_ALIGNMENT_AUDIT.md). The final pass
re-derived every number from the Stitch `code.html` Tailwind config rather than
from the PNGs, so the renders now show:

* one centred header (28/34 800 wordmark, 48 dp brand glyph on the tab shell,
  `FittedBox` scale-down for long page titles);
* 12 dp card radius, 8 dp in-card surfaces, 36 dp in-card actions, 52 dp page
  CTAs;
* a full-bleed `4/5` PDP hero with glass pills on top and a glass title card
  pulled up 32 dp over the photograph;
* Home product media at 1.35 (the reference's `h-32` in a 173 dp tile) with 8 dp
  of caption padding, and a scrollable 112 dp stat strip whose tiles stack
  glyph over `stat-num` 22/26 800;
* `headline-md` 20/26 700 section headers on Home, Cart and the PDP.

* `after/01_home.png` … `after/04_subscription.png` — dark theme (unchanged names).
* `after/01_home_light.png` … `after/04_subscription_light.png` — the **light**
  renders, which are the ones to compare against the Stitch deliverables (the
  product is light-first; the light goldens exercise the palette the reference
  was drawn in).

Two harness facts worth knowing before re-running it:

1. `DetailPage.initState` logs a `view_item` analytics event. With no Firebase
   app in the test VM that throws an uncaught `FirebaseException` *after* the
   exception drain, which used to fail the PDP captures. `setUpAll` now installs
   a `mocktail` `FirebaseAnalytics` stub via
   `AnalyticsService.setAnalyticsForTesting`.
2. Home's offer carousel and the subscription countdown keep timers alive past
   teardown, so four tests end with `A Timer is still pending…`. The golden PNG
   is written before that invariant, so the images are valid; treat the failure
   as expected.

## How "before" is produced without touching the working tree

`git worktree add X:\BMJ\_captures\lush_before HEAD --detach` (HEAD `e1d11e6`)
gives a pristine legacy tree. Nothing is stashed and the migration working tree
(`X:\BMJ\lush`) is never modified.

For "after", the working tree is copied to `X:\BMJ\_captures\lush_after`
(robocopy, excluding `build`, `.dart_tool`, `.git`, `test`, platform folders) so
the capture harness lives only in throwaway copies.

The only files added to those copies are:

* `lib/capture_main.dart` – skips `_initializeApp()` (see *Why not a browser*).
* `test/capture/screens_capture_test.dart` – the capture harness.

## Identical capture conditions

| Dimension | Value (same for both trees) |
|-----------|------------------------------|
| Canvas | 1170x2532 px @ DPR 3 = **390x844 logical**, ScreenUtil designSize 375x812 as in `main.dart` |
| Theme mode | **dark** (`ThemeState.darkTheme`), light theme registered but unused |
| Providers | Byte-for-byte the `MultiBlocProvider` tree from `main.dart` (Auth, Cart, ProductCatalog, User, Subscription, Products, ThemeCubit, Order, Referral, Notification) + `ToastificationWrapper` + `ScreenUtilInit` |
| Mock data | One local stub API (`stub_server.py`, port 8099, `--dart-define=API_BASE_URL`) serving `/api/v1/catalog/charge-items`, `/api/test/charge-items`, `/api/subscriptions/my`, `/api/v1/cart*`; cart seeded through `CartRepository.saveCartItems`; PDP item built from the same catalog payload |
| Fonts | `assets/fonts/PlusJakartaSans-Variable.ttf` → `Plus Jakarta Sans` (+ alias), `assets/fonts/Inter-Variable.ttf` → `Inter`, SDK Roboto → `Roboto`/`Poppins`, SDK `materialicons-regular.otf` → `MaterialIcons`, all loaded via `FontLoader` |
| Networking | `HttpOverrides.global = null` + local stub, so the app's real service/BLoC code paths run |

Re-run either side:

```powershell
cd X:\BMJ\_captures\stub_server.py % cd X:\BMJ\_captures ; python stub_server.py --port 8099
cd X:\BMJ\_captures\lush_after   # or lush_before
flutter test test/capture/screens_capture_test.dart --update-goldens `
  --dart-define=API_BASE_URL=http://127.0.0.1:8099
# goldens land in test/capture/goldens/
powershell -NoProfile -File X:\BMJ\_captures\compose_compare.ps1
```

## Why not a browser screenshot

Both trees hang before `runApp()` on Flutter web: `_initializeApp()` awaits
Firebase/Sentry/FCM initialisation and FCM's service-worker registration never
resolves, and the data layer (`HttpClient`, `IOClient` in
`user_repository.dart` / `products_repository.dart`) is `dart:io`-only. The
golden harness renders the same widget tree with the same engine (Skia) and
bypasses only that pre-`runApp` bootstrap.

## Product detail migration (this pass)

Approved flow: **product tile → PDP → existing size sheet → cart → checkout**.

`lib/views/screens/detail.dart` (migrated further toward `juice_detail_selection`):

* Hero: product photography with a legibility scrim, category pill and a
  Stitch-style **"Select options"** CTA that opens the *existing* shared
  `showSizeSelectionSheet` (`lib/views/widgets/size_selection_sheet.dart`) — the
  same sheet the Menu grid and Home quick-add use. The decorative bottle glyph
  is now only a fallback when the item has no image.
* New **"Select a size"** block (Stitch "Select Size"): one pill per real
  `ItemPrice` (`size · ₹price`, cheapest preselected, unpriced options disabled)
  plus a "Choose quantity" entry point into the sheet.
* Title block carries the description and the real `rating` (Stitch prints both
  under the price); a rating of `0` is treated as unknown and hidden.
* **"Purchase option"** block (Stitch "Purchase Option"): a `One-time purchase`
  radio row quoting the selected catalog price, and a `Weekly subscription` row
  that routes to the existing `/plan-selection` flow. The weekly row shows
  `View plans` instead of a price — subscription pricing belongs to the plan
  screen, so nothing is invented.
* `Key ingredients` renders as the reference's bulleted list (was chips).
* **One pinned CTA** (Stitch sticky bar): `Add to cart · ₹X` for one-time,
  `View weekly plans` when the subscription row is selected. The size sheet
  stays reachable from the hero "Select options" and from "Choose quantity", so
  the second footer button (and the vertical space it took) is gone. The CTA
  price always mirrors the selected `ItemPrice` — no invented prices.
* Hero category chip is a fixed light badge with dark ink (`DELIGHT`), because a
  theme-aware pill cannot guarantee contrast over unknown product photography.

`lib/widgets/bmj_glass_button.dart`: the label `Row` now wraps the `Text` in
`Flexible` — long labels ellipsised instead of overflowing (found while adding
the PDP test at 390 dp).

`test/widget/screens/product_detail_screen_test.dart` (7 tests): catalog
name/price/size pills, pill→CTA price sync, both sheet entry points opening the
shared sheet, the legacy `Product` path hiding catalog-only affordances, the
description/rating/purchase-option block, and the CTA swap.

Verification: `flutter test` **415 passing**, `flutter analyze` **0 errors**
(468 informational lints project-wide — one fewer than before this pass, none in
the touched files), `test/theme/no_raw_white_test.dart` still covers `detail.dart`.

## Home, cart & subscription migration (this pass)

The three remaining priority screens were aligned to their Stitch references.
Every BLoC dispatch, route and Chargebee/checkout/auth call is unchanged.

### Home → `unified_home_dashboard`

* Greeting (`Good morning,` + `Welcome back, <name>` / `Welcome to BookMyJuice`)
  replaces the green hero gradient, matching the reference's first viewport.
* Liquid-glass subscription card: `Active Subscription` pill, plan name,
  descriptive line, next-delivery row and a full-width outlined
  **Manage delivery** action (`/manage-subscriptions`); the signed-out state is
  the same shell with **Browse plans** (`/plan-selection`).
* Three centred stat tiles (`100% Natural`, `30m Delivery`, `0 Preservatives`).
* **Trending Juices** is now a 2-column grid of Stitch product tiles
  (artwork, floating orange `+` → shared size sheet, name, ingredients, price).
* The promo rail, quick picks and recent orders keep their existing data and
  routes and move below the Stitch block; the page is padded for the floating
  bottom nav.

### Cart → `shopping_cart_savings_summary`

* Header `Your Cart`, `Items (n)` section header with the existing clear-cart
  dialog moved into it.
* Item cards gain a remove `X` (same `RemoveFromCart` event) and the Stitch
  `- n +` pill stepper; price stays the real local line total.
* **Order Summary** card groups Subtotal / Taxes & delivery / Total. Only the
  subtotal is a number — tax, delivery and total remain **At checkout** because
  Chargebee is the single source of truth (no invented amounts). A promo note
  replaces the reference's promo field: the app has no coupon API and coupons
  are entered on the hosted page.
* Delivery address card and `Proceed to checkout` keep the exact payload and
  409 `CART_TYPE_CONFLICT` handling.

### Subscription → `subscription_management_portal`

* Page intro (`Manage Subscriptions` + supporting line) and the **9 PM IST
  Cutoff** notice (same rule the actions enforce).
* Plan card: status pill + `Plan ID: #…`, plan name, `N bottles · Billed weekly`
  meta, `NEXT DELIVERY` / `NEXT BILLING` boxes, full-width **Modify plan**
  primary action, then `Pause/Resume` + `Cancel` in a second row.
* Bottom `Change or add a plan` bar retained; the list is padded so it no longer
  hides the last card.

### Asset fix

`assets/carrot.png` shipped as **24-bit RGB with a baked-in checkerboard**
(the "transparent" background was painted pixels), so it rendered as a
placeholder pattern in every catalog surface. It is now a 32-bit RGBA PNG with
the connected light-grey background removed (alpha 0) and every produce/splash
pixel preserved. No path, catalog JSON or code reference changed.

### Verification

* `flutter test` — **403 passing**, 0 failures.
* `flutter analyze` — **0 errors** (the pre-existing warnings/infos are
  unchanged; the three migrated files add none).
* Goldens in `after/` and side-by-sides in `compare/` were regenerated with the
  same harness, stub payloads, fonts, theme mode and viewport as the "before"
  set.

## Known artifacts (all pre-existing, present only in the "before" images)

* **Legacy top bar is clipped** – `Dashboard._buildTopBar` is wrapped in
  `PreferredSize(Size.fromHeight(60.h))` while its content needs
  `top: 48.h` + a 28.sp row, so the wordmark and cart pill are cut off.
* **Legacy PDP white sheet** – the `Colors.white` panel renders white text on
  white (`detail.dart` legacy body); this is exactly what the PDP migration
  replaces.
* **Block glyphs on a few legacy labels** – legacy styles that rely on the
  theme's default font (no explicit family) fall back to the test VM's Ahem
  font; on device they would use Roboto.
* Test-teardown failures ("A Timer is still pending") are expected: the goldens
  are written before teardown, and the harness is not part of the test suite.

## Launch-readiness pass (this pass)

### Light-first verification

`ThemeCubit` defaults to `ThemeMode.system` and the app ships both token sets, so
the four priority screens are now captured **in the light set as well**:
`after/01_home_light.png`, `02_pdp_light.png`, `03_cart_light.png`,
`04_subscription_light.png`. The harness takes a `themeMode` argument; the
before/after pairs stay dark (they compare UI, not theme). No contrast or
overflow defect surfaced; the only real finding was the PDP hero category chip
(white label over bright fruit), fixed with a fixed light badge + dark ink.

### Pricing audit

`python audit_pricing.py` scans the four migrated screens, the shared BMJ
components, the size sheet and `price_utils.dart` for hardcoded rupee literals,
`?? 0` price fallbacks and `.99` placeholders. Result: **0 fabricated prices** —
all hits are documentation comments describing the removed `₹0` / `₹9.99`
fallbacks. Money still goes through `formatRupees` / `cheapestPricedOption`, so
an unknown price renders the em dash.

### Subscription "Next delivery"

`lib/utils/subscription_view_utils.dart` now owns the two data decisions the
screen used to inline, with unit tests (`test/unit/utils/`):

* `quantityOf` falls back to `items[0].quantity` — the shape the API actually
  returns (the entity mapper exposes `items`, not a top-level `quantity`), so a
  real device shows `N bottles` instead of dropping the line.
* `nextDeliveryDateLabel` renders **only** a published `nextDeliveryAt`.
  Deriving it from `nextBillingAt` was implemented, reviewed and **rejected**:
  a weekly *billing* cycle does not prove the delivery cadence (a weekly plan can
  deliver daily), so it would promise a delivery on a day that may not be
  scheduled.

The gap behind the em dash is now **closed** on the backend:

| Piece | Where | What it does |
| :--- | :--- | :--- |
| `delivery_schedule` table + `DeliveryScheduleService` | `bmjServer` | Persists the day-wise schedule the customer submitted at checkout, keyed by the subscription id the checkout reserves. |
| Reserved subscription id | `subscribe`, `subscribe/direct`, `POST /api/subscriptions/create` | Passed to Chargebee as `subscription[id]`, so the `subscription_created` webhook joins the stored schedule to the subscription deterministically (Chargebee's `checkout_new` accepts custom ids but **not** `meta_data`). |
| `nextDeliveryAt` / `deliverySchedule` | `GET /api/subscriptions/my`, `GET /api/subscriptions/{id}` | Next scheduled delivery day (epoch seconds, midnight IST) computed from the stored schedule + start date; `null` when no schedule exists, or the subscription is paused/cancelled. |
| Client | `subscription_service.createSubscription(planId, daySchedule:)` | Sends the schedule picked on the subscription summary flow. |

`nextDeliveryDateLabel` still renders **only** a published `nextDeliveryAt`, so a
subscription bought before this change (or one created without a schedule) keeps
showing the em dash — which is the truthful value. Unit coverage:
`bmjServer/src/test/java/com/bookmyjuice/services/DeliveryScheduleServiceTest.java`
(12 cases: normalisation, JSON round trip, weekday selection, Sunday skip, future
start, paused/cancelled suppression).

### Chargebee track (read-only)

`python chargebee_catalog_check.py` (data-lookup MCP, paginated census):

| Item type | Count | INR range |
| :--- | ---: | :--- |
| `charge` (one-time / cart / PDP) | **5** | ₹89 – ₹500 |
| `addon` | 9 | ₹21 – ₹500 |
| `plan` (subscriptions) | 300 | ₹16 – ₹10,776 |

* 0 zero/negative prices, 0 non-INR prices.
* The 5 `charge` prices are legacy/demo ids (`ABC-INR` ₹89, `abc200-INR` ₹99,
  `carrot300-INR` ₹89, `pineapple300-INR` ₹99, `cbdemo_one-time-setup-fee` ₹500).
* Subscriptions are complete: 56 weekly + 149 monthly + 91 daily + 4 yearly plan
  prices covering every juice and size (e.g. `bmj-delight-carrot-juice-200ml-weekly`
  = ₹461).

**Blocker (now decision-approved, awaiting Chargebee):** the 15 storefront products
still have almost no `charge` prices per size (2 of 45: `bmj-item-mix-punch-200ml`,
`bmj-item-bloody-red-200ml`), so a live `GET /api/v1/catalog/charge-items` returns
an incomplete `prices[]` for them and the PDP/cart render the em dash for the
missing sizes. Chargebee stores only one INR price point per `charge` item, so the
45 rows need **Price Variants** (`bmj-200ml` / `bmj-300ml` / `bmj-500ml`). Option A
is approved and fully prepared — payload, gated rollout script and mapping docs —
but the site does not have variant pricing enabled yet:

* [`CHARGEBEE_ONE_TIME_PRICE_MODELLING_DECISION.md`](CHARGEBEE_ONE_TIME_PRICE_MODELLING_DECISION.md) — options + evidence
* [`CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md`](CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md) — enablement request
* [`CHARGEBEE_PRICE_VARIANTS_MAPPING.md`](CHARGEBEE_PRICE_VARIANTS_MAPPING.md) — the 45-row mapping + runbook

`python _captures/chargebee_price_rollout.py preflight` is the gate and currently
prints `price variants: NOT AVAILABLE on this site`. The harness stub's
₹149/₹199/₹292 are mock layout data, not catalog truth.

### Not executed in this environment

* Checkout / subscription-checkout handoff: needs a running `bmjServer` (it is
  down: `localhost:8080` times out) plus a Chargebee hosted-page session.
* Device matrix (Google new/existing/collision, phone signup/signin, address,
  one-time purchase, subscription purchase): no Android/iOS device or emulator
  is attached — `flutter devices` lists only `windows`, `chrome`, `edge`, and the
  app cannot run on web (`dart:io` data layer + Firebase bootstrap).

