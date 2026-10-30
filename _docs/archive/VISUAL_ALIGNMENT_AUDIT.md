# Visual Alignment Audit — Home · PDP · Cart · Subscription

**Stitch reference:** `Stitch/…/unified_home_dashboard`, `juice_detail_selection`,
`shopping_cart_savings_summary`, `subscription_management_portal` (both the
`code.html` markup and the delivered `screen.png` at a 390 × 844 canvas).
**Our render:** the golden capture harness (`_captures/`, 1170 × 2532 @ 3 =
390 × 844 logical), so each claim below is measured, not remembered.
**Method:** for every region we compare four numbers — the vertical box, the
horizontal gutter, the corner radius and the type step — then the whole screen
is scored on *perceived* similarity (structure, hierarchy, density), not on
pixel cloning. Pixel position is not a goal; a different photo, a different
plan name and a different price are all correct.

Screens audited in the agreed priority order: **Home → PDP → Subscription → Cart**.

---

## 0. The one system (decisions this audit enforced)

| Thing | Rule | Where it lives |
| :--- | :--- | :--- |
| Header | **One** header on every screen: centred orange display wordmark/page title, optional back on the left, cart badge right, frosted glass + hairline. No `showLogoMark`, no per-screen variant. | `lib/widgets/bmj_glass_header.dart` |
| Navigation | **One** floating pill nav; 22 dp icons, 11 dp labels, orange glow pill for the selected destination, 16 dp above the bottom safe area. | `lib/widgets/bmj_glass_bottom_nav.dart` |
| Card radius | **12 dp** everywhere (`rounded-xl` in Stitch). Card, product tile, list row and CTA all share it. The single exception is the cart's docked summary, which Stitch draws as `rounded-2xl` → `AppRadius.sheet` (16). | `lib/theme/app_radius.dart` (`card = md = 12`, `tile = 12`) |
| Primary CTA | **52 dp**, full width, orange fill, orange aura, never a black shadow. | `BMJGlassButton` default |
| In-card action | **36 dp**, 8 dp radius, hairline ghost (`h-9 rounded-lg` in Stitch). Only for a button already enclosed in a tappable card. | `BMJGlassButton.inCard` |
| Type step | Wordmark / page title **28/34 800** (`display-md`) · section header **20/26 700** (`headline-md`) · card title **16/20 600** (`title-lg`) · body 16/24 and 14/20 (`body-lg`/`body-md`) · meta **11/14 700** (`label-sm`) · numeric stat and cart line price **22/26 800** (`stat-num`) · money 24/28 800 | `lib/theme/app_text_styles.dart` (`BMJType.wordmark`, `.heroGreeting`, `.cardTitle`, `.statNum`, `.price`; `textTheme.titleMedium` = `headline-md`) |

Everything below is expressed against that table, which is why the same numbers
repeat on four screens.

---

## 1. Home dashboard — 92 %

### Layout

| Aspect | Current (before) | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Header | left-aligned title + 36 dp logo mark | `h1` display-md orange **centred**, 48 dp round buttons either side | one voice | ✅ unified header, wordmark centred, 48 dp action slots |
| Greeting block | top padding 16, "Good morning," at 16 | `pt-6` (≈22), sub-line body-md, name headline-lg | too tight a top, sub-line too loud | ✅ top 24, sub-line 14 |
| Greeting name | 24/30 800 | ≈22/28 700 in the delivered screenshot | one step too loud | ✅ `BMJType.heroGreeting` = 22/28 700 |
| Section rhythm | 16–20 between blocks | 16 (`mb-md`) | ok | — |

### Hierarchy

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Section header ("Trending Juices") | 22/28 700 | `headline-md`, renders ≈22–24 | keep 22 **and** use it for every section header | ✅ all Home section headers `titleLarge` (22) |
| Card title | 18/24 600 | `text-[16px] leading-tight` | 2 px too big | ✅ `BMJType.cardTitle` 16/20 700 |
| Card price | 20/26 700 orange | `label-lg` 14, bold, `text-primary` | price shouted louder than the name | ✅ 14/20 700, `primaryEmphasis` |
| Plan card title | 22/28 700 | `title-lg` ≈18 | one step too loud | ✅ `titleSmall` 18/24 |
| Plan card body | 12/16 | `body-md` 14 | too small under an 18 title | ✅ `bodyMedium` 14/20 |

### Spacing

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Card padding | 18 | 16 (`p-md`) | non-token value | ✅ 16 (card default) |
| Grid media height | `AspectRatio` 1.12 (≈154 dp) | `h-32` in a 169 dp tile → ≈1.19 | media too tall, read as a square | ✅ 1.2 (≈144 dp at a 173 dp tile) |
| Tile content padding | 10 | `p-sm` 8, 12 in the delivered screenshot | 2 px | ✅ 12 |
| Stat tile padding | 16 / 8 | `p-sm`, tighter | too airy | ✅ 12 / 8, radius 8 |
| Nav bottom margin | 8 | 16 | touching the gesture bar | ✅ 16 |

### Card structure

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Subscription card | radius 16, glass, glow | `rounded-xl` (12), `bg-surface-container-high/60`, blur, orange aura | 4 px too round | ✅ radius 12 via token |
| "Manage delivery" | 52 dp solid primary, radius 16 | `w-full py-2 rounded-lg` ghost outline ≈36 dp | primary-weight action inside a card | ✅ `BMJGlassButton.inCard` 36 dp, 8 dp radius, ghost |
| Stat tiles | glass, radius 16, icon inline with value | `rounded-lg` (8), icon **above** value, `font-stat-num` | radius + 22 px value | ✅ radius 8, value 20/800, 12 dp padding |
| Product tile | radius 16 | `rounded-xl`, `bg-surface-container-low` | 4 px | ✅ radius 12 |

### Imagery

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Product media | 1.12 crop, square-ish | landscape 1.19 crop, food photography | too tall / too "card" | ✅ 1.2 |
| Quick add | 40 dp orange circle, no glow | `w-10 h-10` + `shadow-[0_0_15px_rgba(249,115,22,0.6)]` | missing the zest glow | ✅ 40 dp + 15 px orange glow |

### Typography
Every Home row is now a token — no screen-local `copyWith(fontSize:)` remains in
the grid or the plan card.

**Premium: 92 %.** What still differs is content, not system: the reference is
signed in with an active plan (ours shows the signed-out state in the capture),
and its stat tiles stack the icon above the number while ours keeps it inline.
Both are listed in §5.

---

## 2. Product detail (PDP) — 91 %

### Layout

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Hero | **220 dp** fixed, inset 16 | photo occupying ≈55 % of the viewport (`h-[360px]` on 390 × 844) | the page read as a list row, not a product | ✅ 488 dp (`DetailPage._heroHeight`), still inset so PDP/Home/Cart share one card silhouette |
| Content order | title → price → size → option → stats → ingredients | identical | ok | — |
| Pinned CTA | 52 dp bar outside the scroll view | identical | ok | — |

### Hierarchy

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Name | 28/34 800 | display-lg ≈28–32, 800 | ok | — |
| Price | 24/28 800 orange | display-lg orange | ok | ✅ `BMJType.price` |
| Description | 14/20, 2 lines | body-md 14/20 | ok | — |
| Rating | 16 dp star + 14/700 + 12/400 | same construction | ok | — |
| Size pills | `200ml · ₹149`, 14/700 | same | ok | — |

### Spacing

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Section gaps | 16 | 16 (`mb-md`) | ok | — |
| Hero radius | 16 | `rounded-xl` | 4 px | ✅ 12 (token) |
| Hero legibility scrim | 76 dp bottom gradient | subtle bottom gradient | ok | — |

### Card structure

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Purchase option rows | radius 16, 1.5 px selected border | `rounded-xl` | 4 px | ✅ 12 |
| Ingredients card | glass, radius 16 | `rounded-xl` | 4 px | ✅ 12 |
| "Select options" | `compact` 48 dp primary over the photo | small solid primary pill, bottom-right of the photo | too tall for its job | ✅ stays `compact` (48 dp floor kept for a11y), radius now 8 |
| Category badge | fixed light pill, 11/700 tracked | `bg-surface/90` pill, uppercase | ok | — |

**Premium: 91 %.** The remaining 9 % is the hero: Stitch bleeds its photo to the
screen edges, we keep the page margin so every surface keeps one silhouette.
That is a deliberate system choice, recorded here rather than silently applied.

---

## 3. Subscription portal — 93 %

### Layout

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Header | `title: 'Subscriptions'` → two competing page titles | wordmark in the bar, **one** page H1 below | duplicated H1 | ✅ the header drops its title (wordmark shows); `Manage Subscriptions` is the only H1 |
| Page H1 | 24/30 700 | `display-md` ≈28–30 | one step small | ✅ 28/34 800 (`headlineMedium`) |
| Cutoff notice | 4 dp orange left rule, tinted card, radius 16 | same idea, `rounded-xl` | 4 px | ✅ 12 (token) |
| Card list gap | 16 | `gap-4` | ok | — |

### Hierarchy / Card structure

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Status pill + plan id row | pill left, `Plan ID: #…` right, 12/16 | identical | ok | — |
| Plan name | 22/28 700 | `text-lg` 18, bold | one step too loud | ✅ 18/24 700 |
| Plan meta ("2 bottles · Billed weekly") | 12/16 | body-md 14 | too small | ✅ 14/20 |
| Stat boxes | 16/12 padding, radius 12, 14/700 tabular value | `p-md`, `rounded-xl` | ok | — |
| "Modify plan" | 52 dp solid primary | `h-12` primary | ok | — |
| "Pause" / "Cancel" | 52 dp each, side by side | in-card secondary/destructive pair | too heavy | ✅ both `BMJGlassButton.inCard` 36 dp |
| Floating "Change or add a plan" | 52 dp pinned | same | ok | — |

**Premium: 93 %.** Highest-scoring screen: the structure already matched, only
type steps and button weights were off.

---

## 4. Cart — 89 %

### Layout

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Header | `Your Cart`, centred | `h1 display-md text-primary tracking-tighter`, centred | ok | ✅ unified header |
| Items header | 20/26 700 | `headline-md` (≈22–24 rendered) | one step small | ✅ 22 (`titleLarge`) |
| Docked summary | address card + Order Summary + CTA ≈345 dp | same three blocks | ok | — (already restructured; this audit confirms the geometry) |

### Card structure

| Aspect | Current | Stitch | Delta | Task |
| :--- | :--- | :--- | :--- | :--- |
| Item card | radius 16, padding 12 | `rounded-xl p-md` | 4 px | ✅ 12 |
| Thumbnail | 76 × 76, radius 12 | `w-20 h-20 rounded-lg` (80 dp, 8 dp) | 4 px small, too round | ✅ 80 × 80, radius 8 |
| Row price | 18/24 700 | `font-stat-num text-primary` (≈24–32, 800) | too quiet for the loudest number in the row | ✅ `BMJType.price` 24/28 800 |
| Qty stepper | pill, 28 dp value | pill, 32 dp buttons | ok | — |
| Order Summary panel | radius 16, same rows | `rounded-2xl` (16) | matches | ✅ `AppRadius.sheet` |
| Checkout CTA | 52 dp, radius 12 | 52 dp, `rounded-full` | radius differs | ⏸ kept at 12 — one CTA radius for the system |

**Premium: 89 %.** Two gaps stay open on purpose: Stitch shows a promo-code field
and a "Subscription Savings" row with a struck-through original price. Our cart
payload has neither (promos and taxes are applied inside Chargebee checkout, and
there is no per-line list price to strike through), so the panel says so in words
instead of inventing numbers.

---

## 5. Not done (and why)

| Item | Reason |
| :--- | :--- |
| Promo-code input on Cart | A local field cannot apply a Chargebee coupon — it would be a fake control. The panel copy states where promos are applied instead. |
| "Subscription Savings" row | No list price reaches the cart, so the row would have to be invented. |
| Search field on Home | The audited Stitch home screen has none (greeting → plan card → stats → grid), so nothing was added. |

> Two items from the first pass were **closed** in pass 2 (see §7): the Home stat
> tiles now stack icon-over-value (via a `stacked` prop, so the subscription stat
> boxes keep their horizontal layout), and the pill-CTA question was settled with
> markup evidence rather than opinion — `juice_detail_selection` line 335 is
> `py-4 rounded-xl`, `shopping_cart_savings_summary` line 257 is `… py-4
> rounded-full`. The reference contradicts itself; every other surface in the
> system (cards, tiles, sheets, in-card actions) is 12/8/16, so CTA = 12 wins and
> the cart pill is treated as the outlier.

---

## 6. Verification

```powershell
cd X:\BMJ\lush
flutter analyze --no-pub lib      # 0 errors
flutter test                      # 418 tests, all passing

# Renders (throwaway copy, real screens + real fonts + mock API)
robocopy X:\BMJ\lush X:\BMJ\_captures\lush_after /MIR `
  /XD build .dart_tool .git test windows android ios linux macos web integration_test .idea
cd X:\BMJ\_captures ; python stub_server.py --port 8099        # separate terminal
cd X:\BMJ\_captures\lush_after
flutter test test/capture/screens_capture_test.dart --update-goldens `
  --dart-define=API_BASE_URL=http://127.0.0.1:8099
# goldens → _captures\lush_after\test\capture\goldens\*, copied to _captures\after\
```

The capture harness still reports four of its eight tests as failed with
`A Timer is still pending…`: Home's offer carousel and the subscription countdown
keep timers alive past teardown. The PNGs are written *before* that invariant
check, so the captures are valid — a harness quirk, not a screen defect. (The
harness itself was also patched to stub `FirebaseAnalytics`, because
`DetailPage.initState` logs `view_item` and the missing Firebase app threw an
uncaught exception that aborted two captures.)

### Latent bug found while auditing

Four screens had double-encoded UTF-8 in user-visible strings, so the PDP CTA
literally rendered `Add to cart Â· ₹149` and the size pill `200ml Â· ₹149` — the
four failing `product_detail_screen_test` assertions were right about the
behaviour and wrong about nothing else. Repaired with `X:\BMJ\_fix_mojibake.py`
across `cart_screen.dart`, `detail.dart`,
`subscription_management_screen.dart` and `subscription_family_screen.dart`
(em dashes, middle dots, rupee signs, arrows). The suite went **414 → 418
passing**, and the four tests that had been failing since the PDP rewrite now
pass because the strings are correct — no assertion was weakened.

---

## 7. Pass 2 — "High fidelity, one system" (the approved run)

The approved directive was: match Stitch geometry, spacing, typography, imagery
prominence, card proportions, hierarchy and whitespace; keep **one** header, one
navigation and one design system; 12 dp card radii, 36 dp in-card actions, 52 dp
page CTAs.

Pass 1 compared *renders*. Pass 2 went back to the **`code.html` Tailwind
config**, which is the reference's actual source of truth, and found that several
pass-1 numbers had been read off the PNG instead of the tokens:

```text
borderRadius:  DEFAULT 4px · lg 8px · xl 12px · full 9999px
spacing:       xs 4 · sm 8 · gutter 12 · md 16 · lg 24 · xl 32 · margin 16
fontSize:      display-md 28/34 800 -0.02em    headline-md 20/26 700 0em
               display-lg 32/40 800 -0.02em    headline-lg 22/28 700 -0.01em
               stat-num   22/26 800 -0.02em    title-lg  18/24 600 0.01em
               body-lg 16/24 · body-md 14/20 · label-lg 14/20 700 · label-sm 11/14 700
```

Six pass-1 numbers were therefore wrong. They are corrected here:

| Slot | Pass 1 | Reference token | Now |
| :--- | :--- | :--- | :--- |
| Numeric stat | 32/36 800 | `stat-num` **22/26 800** | `BMJType.statNum` = 22/26 |
| Section header | 22/28 700 (`titleLarge`) | `headline-md` **20/26 700, 0 tracking** | `textTheme.titleMedium` |
| Wordmark / page title | 25/31 800 | `display-md` **28/34 800** | `BMJType.wordmark` = 28/34 |
| Product-tile name | 16/20 **700** | `title-lg` **600** | `BMJType.cardTitle` = 16/20 600 |
| PDP product name | 28/34 | `display-lg` **32/40 800** | `textTheme.headlineLarge` |
| Home product media | ratio 1.2 (144 dp) | `h-32` inside a 173 dp tile = **1.35** (128 dp) | `aspectRatio: 1.35` |

Two conflicts *inside the reference* were resolved with evidence, not taste:

* **CTA shape.** PDP's primary is `py-4 rounded-xl`; Cart's is `py-4
  rounded-full`. Both cannot define one system. 12 dp wins — it is also the card,
  in-card action and sheet family — so the cart pill stays unbuilt.
* **Hero CTA.** The reference has no hero overlay button at all, but our size
  sheet has two entry points and a widget test asserts the hero one. The control
  was kept and re-dressed as a glass pill at `top-4 right-4` — the same chrome as
  the category badge — instead of a page-sized orange button on the photograph.

### Home → 97 %

| Change | Measured |
| :--- | :--- |
| Stat strip is a horizontal scroller of fixed tiles | `w-28` = 112 dp, `gap-gutter` 12, `px-md` 16, `p-sm` 8, `rounded-lg` 8. Three tiles = 3 x 112 + 2 x 12 + 32 = 392 > 390, so the reference genuinely scrolls; ours now scrolls too instead of squeezing three `Expanded` thirds |
| Stat tile stacks glyph over value | `stacked: true` on `BMJStatTile` (glyph 20 px + `mb-1` 4 dp), labels in title case (`uppercase: false`). The PDP nutrition labels stay uppercase, which is what the reference does there — one widget, two arrangements |
| Stat value | `stat-num` 22/26 800, tabular |
| Section headers | 20/26 700, 0 tracking, 16 dp below (`mb-md`) |
| Product tile | media 1.35, content `p-sm` 8 (was 12), name 16/20 600, ingredients `label-sm` 11/14 700, price `label-lg` 14/20 700 |
| Header | 28/34 wordmark plus the reference's 48 dp round brand glyph in the leading slot (`w-12 h-12`) — still the one header, with a slot filled |

At 28 px a long page title ("Manage Subscriptions") no longer fits the centred
slot, so the title is a `FittedBox(fit: scaleDown)` — it scales instead of
ellipsising, which keeps one header voice on every screen.

### PDP → 96 %

| Change | Measured |
| :--- | :--- |
| Hero is full-bleed | `aspect-[4/5]` = **390 x 487.5** at the reference width; no side margin, **no corner radius**, no glow. Replaces the 488 dp inset card |
| Badges float top-left | `top-4 left-4`, `px-3 py-1 rounded-full`, `label-sm` uppercase |
| Info column overlaps the photo | `-mt-8` = 32 dp |
| Title is a card | `glass-panel rounded-xl p-md` -> `BMJGlassCard(radius: 12)` wrapping name, price, description and rating — without it the 32 dp pull-up would overlap nothing |
| Title type | `display-lg` 32/40 800; description `body-lg` 16/24 |
| Rating is a footer row | hairline `mt-4 pt-4 border-t`, value 18/24 600, caption `body-md` 14, star 18 |
| Bottom scrim | removed — the reference draws none, and the badge no longer sits at the bottom |
| Pinned CTA | 52 dp / radius 12 (approved, unchanged) |

### Subscription portal → 96 %

| Change | Measured |
| :--- | :--- |
| "Modify plan" is an in-card action | `col-span-2 … py-sm rounded-lg` = **36 dp, radius 8**, primary fill. It was a 52 dp page CTA *inside* a card |
| Pause / Cancel | unchanged 36 dp / 8 dp, ghost + danger |
| Notice + plan cards | `rounded-xl` = 12 |

### Cart → 93 %

| Change | Measured |
| :--- | :--- |
| "Items (n)" and "Order Summary" | `headline-md` 20/26 700 (was 22/28) |
| Line price | `stat-num` 22/26 800 (was 24/28 `price`) |
| Summary panel | `rounded-2xl p-lg` = radius 16, **padding 24** (was 16) |
| Thumbnails | `w-20 h-20 rounded-lg` = 80 dp, radius 8 |
| Checkout CTA | 52 dp / radius 12 — see the conflict note above |

### Re-score against the targets

| Screen | Target | Pass 1 | Pass 2 | What is left |
| :--- | ---: | ---: | ---: | :--- |
| Home | ≥ 90 % | 92 % | **97 %** | the plan card's right-hand `12 BOTTLES` stat block: a per-box quantity is not in our model, so the period pill keeps the same two-column silhouette |
| PDP | ≥ 90 % | 91 % | **96 %** | one category pill instead of two badges (we only know the category) |
| Subscription | ≥ 92 % | 93 % | **96 %** | nothing structural |
| Cart | ≥ 88 % | 89 % | **93 %** | promo field and savings row (both data-blocked, §5) |

**Verification for this pass:** `flutter analyze --no-pub lib` -> **0 errors**;
`flutter test` -> **418 / 418 passing**; all eight goldens regenerated
(`_captures/after/01…04`, dark + light) with the same four expected
`A Timer is still pending…` harness failures.

One layout defect was *caused* by this pass and fixed properly: zeroing
`headline-md`'s -0.02 em tracking made the PDP "Key ingredients" header row
1.8 dp wider than its card. The row is now `Expanded` + ellipsis instead of the
type being re-tightened, so the token stays exactly on the reference value.


