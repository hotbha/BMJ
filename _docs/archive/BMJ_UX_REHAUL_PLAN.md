# BMJ_UX_REHAUL_PLAN.md — controlled UX + UI overhaul on the Stitch design system

**Prepared:** 17 October 2026
**AMENDED 2026-10-17 (authentication):** the approved product decision *removes every password and email authentication flow* (Google + Phone OTP only). It **revokes §1 D3**, retires designs **#2, #3, #23**, reclassifies **#25 as MERGE → #11**, and expands the §7 retirement inventory from 7 to 17 files (16 screens + `firebase_phone_auth.dart`, 4,026 lines). The full re-baseline — counts **9 KEEP · 10 MERGE · 11 REMOVE**, arithmetic **85.8 % on 19 retained designs**, effort **27.75 d** — is in **`AUTH_SIMPLIFICATION_PLAN.md` §8**. Read that document before executing §5–§9 of this one. The tables below are left as written so the classification history stays auditable; where they disagree with `AUTH_SIMPLIFICATION_PLAN.md`, the auth plan wins.
**AMENDED 2026-10-17 (theme):** §1 **D6 is resolved by Product instruction — light-first**. The light theme is the design target; dark remains *supported* through `ThemeCubit` but is no longer the reference for Stitch alignment. Every "dark glass" reading in §2 is re-read as its light-glass equivalent (white 70–85 % surfaces, `#0F172A` text, existing orange/lime accents).
**Status:** **Plan only.** No Dart file, asset, route, backend class or Chargebee configuration has been created, edited or deleted in producing this document. Nothing was run on a device.
**Deliverable:** step 1 of the brief ("Before coding: `BMJ_UX_REHAUL_PLAN.md`"). Step 2 (code) starts only after the two open decisions in §1 are signed off.
**Inputs:** `Stitch/**` (31 design folders, 31 `code.html`, 31 `screen.png`, 2 `DESIGN.md` → **30 unique screens**), `STITCH_IMPLEMENTATION_STATUS.md`, `STITCH_V2_UI_MIGRATION.md`, `docs/BMJ_V1_SCOPE.md`, `PRODUCT_ALIGNMENT_REPORT.md`, and a fresh read of `lush/lib/**` (theme, routes, the five screens this plan changes).

---

## 0. What this plan is allowed to touch

The brief's constraints are treated as hard technical gates, not as tone. Every one of them is testable, so each gets a check in §10.

| Constraint | What it forbids in practice | Where this plan would have violated it |
| :--- | :--- | :--- |
| Do not rewrite BMJ | No new app shell, no `main.dart` restructure, no state-management change | Routes are **added/aliased**, never re-architected; `AuthenticationBloc`, `CartBloc`, `SubscriptionBloc` are untouched |
| Do not create a new Flutter project | No second `pubspec.yaml`, no parallel `lib/` | All work lands in `lush/lib/**` |
| Do not modify backend APIs | No new endpoint, no payload change | PDP reuses `CartItem`/`AddToCart` and `GET /api/v1/catalog/charge-items` exactly as today (§5.4) |
| Do not modify Chargebee integration | No pricing, no plan creation, no hosted-page change | "Subscribe & Save 15%" from design #8 is **not implemented** (§12) |
| Do not change business logic | No new discount, fee, tax, address field, auth path or plan-change rule | The places Stitch assumes new business logic are listed in §12 and refused |

**Two consequences worth stating before any table.** First, this is a **re-skin plus a small number of composition changes** — 11 screens keep their behaviour, 11 designs collapse into 5 screens, 8 designs are retired. Second, **the ≥85 % objective is measured on the set that ships** (22 designs), not on all 30, because the 8 retired designs are retired *on purpose* and score 390 points that no amount of styling can move.

---

## 1. Decision register

| # | Decision | Status | Evidence / reasoning | Consequence if wrong |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | **Canonical design system = `vibrant_zest_architecture`** (orange primary + neon-lime secondary + Plus Jakarta Sans), not `lush_architecture` (gold + cyan + Poppins) | **Resolved — measured, not preferred** | All **31 of 31** `code.html` files load **Plus Jakarta Sans**; `Poppins` appears **0 times** in the entire Stitch bundle. `lush_architecture/DESIGN.md` is a token sheet with **no screen implementing it**. The screens *are* the canonical UX reference per the brief, so the system every screen actually uses wins. | If Product prefers gold, D1 re-opens and every token in §2 changes; the 4.5 d foundation is re-done, total +3.5 d |
| **D2** | **Navigation stays 4 destinations: Home · Catalog · Subscription · Profile.** Orders moves out of the tab bar to explicit entry points (`/orders`, `Profile → My Orders`, `Home → Recent orders → See all`) | **Needs one-line Product sign-off** | Today's bar is Home · Catalog · **Subscription** · Profile (`dashboard.dart:211/231/251/270`) and index 2 renders `OrdersTab` (`:106`). Stitch is itself **inconsistent**: `unified_discovery_dashboard` uses Home · Menu · Plans · Cart, while `subscription_management_portal` uses Home · Catalog · Orders · Profile. Keeping 4 tabs and re-homing Orders is the only option that fixes P0-1 without orphaning Profile (addresses, referral, delete-account). | If Product wants a literal Orders tab → 5 destinations (not Stitch) and Profile needs a header avatar; +1.0 d |
| **D3** | **Password *sign-in* stays; password *onboarding* variants are removed** | Resolved (scope reading) | `CreatePasswordScreen` is the **terminal step of the live phone sign-up chain**: `PhoneOtpVerificationScreen` → `/address-entry` (`phone_otp_verification_screen.dart:221-223`) → `/create-password` (`address_entry_screen.dart:97-99`) → `SignUp` → `/dashboard` (`create_password_screen.dart:108-125`). Deleting it breaks phone sign-up = business logic. Separately, `LoginPage` signs existing customers in with email + password (`login_page.dart:589-599`). | Removing password sign-in would strand every existing credential-holder and needs a backend/Product decision — **out of scope** |
| **D4** | **PDP sells "One-Time" and "Subscribe" — it does not invent a 15 % discount** | Resolved | Design #8 shows `Subscribe & Save 15% · $6.80` against `$8.00`. No such rule exists in the frozen contract, and inventing client-side pricing changes money logic. PDP's Subscribe option **routes to the existing plan catalogue** (`/plan-selection`), whose price comes from `GET /api/v1/subscriptions/pricing/plans`. | Implemented literally, the app would quote a price Chargebee will not honour — a billing mismatch |

| **D5** | **Address keeps its 9-field model; Stitch's 4-field layout is adopted only as styling** | Resolved | `address_entry_screen.dart:80-112` submits 9 fields used by `POST /api/v1/address/**`. Collapsing to Flat/Street/City/Pincode would change the API payload (forbidden). | Target for #1 caps at **82**, not 88 |
| **D6** | **Dark is the default theme; light remains supported but is not a design target** | **Needs one-line Product sign-off** | Stitch is 100 % dark glass; the app currently honours a `ThemeCubit` toggle and ships light surfaces on cart/orders/auth. Keeping light costs ~6 extra token values; removing it is a UX regression for a shipped feature. | If light is dropped, `ThemeCubit` loses its toggle (a feature removal) |
| **D7** | **Cart shows subtotal only, plus an explicit "delivery & taxes calculated at checkout" line** | Resolved | `cart_screen.dart:427-560` — Subtotal exists; delivery fee, "Subscription Savings" and grand total are computed by Chargebee on the hosted page. No coupon code exists anywhere in `lib/`. | Target for #13 caps at **80** (the design's 3 money lines cannot be computed without inventing fees) |
| **D8** | **`STITCH_ALIGNMENT_REPORT.md` is superseded where it disagrees** | Resolved | That report calls design #3 `create_password_step_3` an "`AddressEntryScreen` duplicate". The rendered text of #3 is *"Step 3: Password · Secure Your Account · Create a strong password… Complete Setup"*. `STITCH_IMPLEMENTATION_STATUS.md` is correct; #3 is the password step. | Using the stale report would merge password styling into the address screen |

---

## 2. Design-system contract (`vibrant_zest`, extracted verbatim from `DESIGN.md`)

### 2.1 Colour

| Role | Token | Value | Used for |
| :--- | :--- | :--- | :--- |
| Surface | `surface` | `#1C110B` | App background |
| Surface deep | `surface-deep` | `#0F1412` | Ambient layer behind glass |
| Containers | low → highest | `#251913` · `#291D16` · `#352720` · `#40322A` | Card tiers, sheets, nav |
| On surface | `on-surface` | `#F6DED3` | Primary text |
| On surface variant | `on-surface-variant` | `#E0C0B1` | Secondary text, icons |
| Outline / variant | — | `#A78B7D` / `#584237` | Hairlines, dividers |
| **Primary** | `primary` | `#FFB690` | Headline emphasis, active icons |
| **Primary container** | `primary-container` | `#F97316` | **The action colour**: CTAs, selected chips, glow |
| **Secondary** | `secondary` | `#4AE176` | Savings, success, subscription ticks |
| Tertiary | `tertiary` | `#5DD9D0` | Informational badges |
| Error | `error` | `#FFB4AB` | Destructive actions, out-of-stock |
| Glow | `zest-glow` | `rgba(249,115,22,0.45)` | Primary aura, selected-state aura |

Legacy → Stitch mapping. This is the whole of the token migration; **no call site is rewritten** — `AppColors.*` keeps its names and changes its values.

| Existing constant | Today | Becomes | Note |
| :--- | :--- | :--- | :--- |
| `AppColors.primaryOrange` | `#FF8C42` | `#F97316` | Closest existing token to Stitch orange (3 references today) |
| `AppColors.primaryGreen` | `#2E7D32` | `#4AE176` | Drives nav-selected icons and app-bar accents; correct on dark |
| `AppColors.glassBg` / `glassElevated` | `#0A0F0D` / `#0F1613` | `#1C110B` / `#291D16` | Removes the green cast from the dark shell |
| `AppColors.glassAccent` / `glassAccentDark` | `#22C55E` / `#16A34A` | `#4AE176` / `#00B954` | Already a lime family — the cheapest win in the migration |
| `AppColors.glassText` / `glassTextDim` | `#E8F5E9` / `#9FB0A8` | `#F6DED3` / `#E0C0B1` | Warm neutral replaces the green-white |
| `AppColors.glassSurface` / `glassBorder` | white 6 % / 12 % | white 8 % / 10 % | Matches `DESIGN.md`'s "1 px hairline, 10 % white" |
| `AppColors.glassOrange` | `#FB923C` | `#FFB690` | Reserved for orange text on dark |
| Light theme (`glassBgLight` family) | `#F0F5F2` | `#FFF8F1` surface · `#2B1B12` text · `#C2410C` primary · `#067A3E` secondary | A minimal daylight variant so D6 is honest; **not** a Stitch target |

### 2.2 Typography

| Stitch role | Size / line / weight | Family | Material slot it re-points |
| :--- | :--- | :--- | :--- |
| `display-lg` | 32 / 40 / 800, −0.02em | Plus Jakarta Sans | `headlineLarge` |
| `display-md` | 28 / 34 / 800, −0.02em | Plus Jakarta Sans | `headlineMedium` |
| `headline-lg` | 22 / 28 / 700, −0.01em | Plus Jakarta Sans | `titleLarge` |
| `headline-md` | 20 / 26 / 700 | Plus Jakarta Sans | `titleMedium` |
| `title-lg` | 18 / 24 / 600 | Plus Jakarta Sans | `titleSmall` (**currently undefined → add**) |
| `body-lg` / `body-md` | 16 / 24 · 14 / 20 | Inter | `bodyLarge` / `bodyMedium` |
| `label-lg` / `label-sm` | 14 / 20 / 700 · 11 / 14 / 700, 0.05em | Inter | `labelLarge` / `labelSmall` |
| `stat-num` | 22 / 26 / 800 | Plus Jakarta Sans | New `BMJType.statNum` |

Mobile rule from `DESIGN.md`: `display-lg` **downscales to 24/30** and is reserved for hero greetings. Prices and countdowns use tabular figures (`FontFeature.tabularFigures`) so BLoC updates do not jitter.

`app_text_styles.dart` declares `fontFamily = 'Roboto'` (64 references across `lib/`). Changing that one constant plus the 11 slot sizes restyles every screen at once — the highest-leverage edit in the overhaul. `bodySmall`, `labelMedium` and `titleSmall` are currently undefined in that `TextTheme`; they must be filled in or Material falls back to Roboto mid-screen.

### 2.3 Space, shape, depth, motion

| Dimension | Value |
| :--- | :--- |
| Base unit | 4 px (xs 4 · sm 8 · md 16 · lg 24 · xl 32) |
| Page margin / gutter | 16 px / 12 px; content max-width **430 px** |
| Grid | 2 columns, 12 px gap for catalog |
| Radii | 8 px inputs & chips · 16 px cards · 24 px sheets · full pill for nav/toggles |
| Glass | blur **16 px** (sheets 24 px), fill 8 % white, border **1 px @ 10 % white** |
| Glow | `rgba(249,115,22,0.45)`, blur 20, spread 1 — **never** a black drop shadow |
| Sheet scrim | black 40 % + 4 px blur |
| Touch target | ≥ 48 × 48 dp everywhere |
| Motion | 200 ms `easeOut` for selection/segment changes; shimmer skeletons must match card radii exactly |

---

## 3. Component library — the five named components, built on what already exists

The tree already contains glass primitives: `GlassCard` (`lib/widgets/glass_card.dart`, blur 10, border 0.5), `GlassChip`, `GlassSegmentToggle`, a hand-built glass nav (`dashboard.dart:152-275`), a hand-built header (`dashboard.dart:120-150`) and `AppTextField` (`lib/widgets/app_text_field.dart`). The brief's five components are therefore **named wrappers with Stitch defaults**, not a second design system. Nothing is duplicated; adoption is incremental and the old widgets keep working.

| Required component | New file | Built on | Stitch defaults | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `BMJGlassCard` | `lib/widgets/bmj_glass_card.dart` | `GlassCard` (composition) | blur 16 · radius 16 · fill white 8 % · border 1 px white 10 % · optional `glow` | Adds tap ripple + `semanticLabel`; never sets a black shadow |
| `BMJGlassButton` | `lib/widgets/bmj_glass_button.dart` | `FilledButton` / `OutlinedButton` | `primary`: `#F97316` + 24 px aura · `ghost`: 1 px `#F97316` border + 8 % fill · h ≥ 48 | Variants `primary`, `ghost`, `danger`; `isLoading`, `icon`, `expand` |
| `BMJGlassInput` | `lib/widgets/bmj_glass_input.dart` | `AppTextField` (composition) | radius 8 · fill `#1C211E` · 1 px border → `#F97316` on focus · 48 dp min | Carries label, hint, error, obscure toggle; keeps the existing `validator` contract |
| `BMJGlassBottomNav` | `lib/widgets/bmj_glass_bottom_nav.dart` | extracted from `dashboard.dart:152-275` | docked pill · 24 px blur · active icon in an orange pill with aura | Takes `destinations`, `index`, `onSelect`; keeps today's `Semantics` labels so existing widget tests still pass |
| `BMJGlassHeader` | `lib/widgets/bmj_glass_header.dart` | extracted from `dashboard.dart:120-150` | logo mark + wordmark, glass on scroll, trailing `CartBadgeIcon` | Optional `leading` (back), `title`, `showCart`; `SafeArea` + 48 dp targets |

Four supporting widgets are needed by the P0/P1 screens and are cheaper to build once than four times:

| Widget | File | Why |
| :--- | :--- | :--- |
| `BMJStatTile` | `lib/widgets/bmj_stat_tile.dart` | PDP "120 Calories / 100 % Vitamin C", home 3-stat row, subscription bottle count |
| `BMJPill` | `lib/widgets/bmj_pill.dart` | "Active", "BEST VALUE", "9 PM IST", `Cold Pressed` tags — one widget, four uses |
| `BMJEmptyState` | `lib/widgets/bmj_empty_state.dart` | Empty cart, no subscription, no orders — each screen currently invents its own |
| `BMJAmountRow` | `lib/widgets/bmj_amount_row.dart` | Cart summary, PDP price, subscription billing — enforces tabular figures + right alignment |

**Implementation order inside P0-3 (4.5 d):** (1) `lib/theme/bmj_tokens.dart` with the §2 values plus the legacy alias table; (2) `app_text_styles.dart` slot re-pointing; (3) the five components as wrappers with **no call sites changed**; (4) the four supporting widgets; (5) one adopt-commit for `dashboard.dart` + `home_tab.dart` only — the visible proof the system works before any other screen is touched. Steps 1–4 must not change a pixel; step 5 is the first visual diff and is reviewed against `screen.png` for #21.

---

## 4. KEEP / MERGE / REMOVE — all 30 designs

Rules applied, in order:

1. **REMOVE** if the design needs a capability the frozen contract forbids, or is a superseded duplicate of a kept design. Removed designs are *not* deleted from `Stitch/` — they leave the build scope and their Flutter screens are retired in §7.
2. **MERGE** if two or more designs target the same Flutter screen or the same step of one journey. The canonical member is the one with the **superset of elements**; the others contribute only their unique blocks, and carry effort 0.0 because the work sits on the canonical row.
3. **KEEP** if the design maps to one shipped screen and nothing forbids it.

| # | Stitch design | Decision | Target surface | Now → Target | Effort (d) | Reason |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| 1 | `address_entry_onboarding` | **KEEP** | `AddressEntryScreen` `/address-entry` | 35 → 82 | 1.5 | First screen after OTP. Keeps the 9-field payload (D5); Stitch supplies the map-pin block, section grouping and sticky CTA as presentation only. |
| 2 | `create_password` | **MERGE** (canonical) | `CreatePasswordScreen` | 54 → 90 | 0.75 | Live final step of phone sign-up (D3). Gains #3's strength checklist + step indicator and its own visibility toggle. |
| 3 | `create_password_step_3` | **MERGE** → #2 | `CreatePasswordScreen` | 56 → 90 | 0.0 | Same screen; contributes "Step 3", the 4-rule checklist and "Complete Setup" wording. Folder title "Delivery Address" is stale (D8). |
| 4 | `create_your_profile_step_1` | **REMOVE** | — | 38 → — | 0.0 | Email-first onboarding step. D-5 removed "Sign up with Email" from `LoginPage`; `SignUpScreen` has no caller and the design needs a photo picker the API does not accept. |
| 5 | `delivery_address_selection` | **KEEP** | `AddressSelectionScreen` `/address-selection` | 53 → 88 | 1.0 | Already wired (default badge, delete-with-confirm, add-new). Missing Home/Work icons, delivery instructions and a confirm CTA — composition only. |
| 6 | `email_signup_verification` | **REMOVE** | — | 51 → — | 0.0 | Email sign-up chain is unreachable; `login_page.dart:22-24` documents D-5. Restyling a screen no journey reaches is spend without a customer. |
| 7 | `google_sign_up_phone_binding` | **MERGE** (canonical) | `GoogleSignupScreen` `/google-signup` | 44 → 85 | 1.0 | V1 flow 1. Removes the password field the design never had; adds "Verified by Google" chip and the country picker #29 also implies. |
| 8 | `juice_detail_selection` | **KEEP** | `ProductDetailScreen` (**new**), `/productDetails` | 20 → 88 | 3.0 | **P0-4.** Largest gap in the set and the only way to sell a subscription from a product. Detail in §5.4. |
| 9 | `link_google_account` | **REMOVE** | — | 37 → — | 0.0 | Not routed, not in the ten V1 flows, and its "Use Password Instead" contradicts D3. |
| 10 | `otp_verification` | **MERGE** → #17 | `/otp` → `PhoneOtpVerificationScreen` | 54 → 90 | 0.0 | `/otp` binds a 47-line stub that calls `SignUp()` **without verifying** (`main.dart:280`). Repoint the route at the real screen; delete the stub. |
| 11 | `phone_login_entry` | **MERGE** (canonical) | `PhoneLoginScreen` `/phone-login` | 52 → 90 | 1.0 | Canonical phone entry for #11 and #16: +91 selector, Terms links, hero copy. `LoginPage`'s "Phone OTP" button already leads here. |
| 12 | `referral_rewards_program` | **KEEP** | `ReferralScreen` `/referral` | 51 → 85 | 1.0 | Live from `profile_tab.dart:151`, fully wired. Cheapest growth lever in the list: WhatsApp share, points format, glass cards. |
| 13 | `shopping_cart_savings_summary` | **KEEP** | `CartScreen` `/cart` | 51 → 80 | 1.0 | Every paying customer passes here. Adds item-count header, per-row savings hint and an explicit "calculated at checkout" footnote; **no new arithmetic** (D7). |
| 14 | `signup_method_selection` | **REMOVE** | — | 56 → — | 0.0 | Superseded by `LoginPage`'s own tabs; no caller since D-5. Its Sign In / Sign Up tab idea already ships. |
| 15 | `sign_in_email_otp_verification` | **REMOVE** | — | 59 → — | 0.0 | Highest-scoring removal in the set — but email-OTP sign-in does not exist, and adding it is new backend scope. |

| 16 | `sign_in_phone_entry` | **MERGE** → #11 | `LoginPage` phone path → `/phone-login` | 43 → 90 | 0.0 | Its phone-only composition is the point; `LoginPage` stays a three-method hub (D3). The phone path becomes one tap into #11's screen. |
| 17 | `sign_in_phone_otp_verification` | **MERGE** (canonical) | `PhoneOtpVerificationScreen` `/phone-otp-verification` | 57 → 90 | 1.0 | V1 flow 2. Section order already matches; work is glass skin, `(00:45)` timer format, "Verify & Continue". Absorbs #10 and #24. |
| 18 | `simplified_weekly_scheduler` | **MERGE** (canonical) | `SubscriptionScheduleScreen` `/subscription-schedule` | 56 → 85 | 1.5 | Already uses `BackdropFilter`, so the family is close. Adds master-day lock, per-day chips, 6/6 counter, price footer. Needs the P0-2 entry path before anyone can see it. |
| 19 | `subscription_management_portal` | **KEEP** | `SubscriptionManagementScreen` `/manage-subscriptions` → becomes the **Subscription tab** | 58 → 82 | 1.5 | The only subscription surface at launch and the destination P0-1 restores. Adds "Active" pill, plan-card art, cutoff banner restyle. **Target 82, not 95** — the design's primary CTA "Modify Plan" is contractually removed (`BMJ_V1_SCOPE.md` §3). |
| 20 | `subscription_plan_comparison` | **KEEP** | `PlanSelectionScreen` `/plan-selection` | 51 → 88 | 2.0 | **P0-2.** Working code, zero callers. Gets 4 real entry points plus the period toggle, feature lists and a data-driven BEST VALUE badge. |
| 21 | `unified_discovery_dashboard` | **KEEP** (canonical home) | `HomeTab` `/dashboard` tab 0 | 61 → 90 | 2.0 | Best match in the set and the first screen of every session. Adds testimonial rail, category chips, search affordance, 2-column grid, 3-stat row (ported from #22). |
| 22 | `unified_home_dashboard` | **REMOVE** (duplicate) | — | 58 → — | 0.0 | Competing design for the same file. One unique block worth porting (juices consumed / bottles returned / streak) moves into #21; the rest is a second skin for one screen. |
| 23 | `verify_email_otp_step_1.1` | **KEEP** | `EmailVerificationAfterPhoneScreen` `/email-verification-after-phone` | 59 → 90 | 0.75 | Live in the phone-first chain (email capture step), already wired to the API. Six boxes, resend and verify match; needs skin + timer format. |
| 24 | `verify_phone_otp_step_2.1` | **MERGE** → #17 | `PhoneOtpVerificationScreen` | 56 → 90 | 0.0 | Contributes the "Step 2 of 3" indicator; the rest is #17's composition. |
| 25 | `verify_phone_step_2` | **KEEP** | `PhoneSignupScreen` `/phone-signup` | 46 → 85 | 1.0 | Entry to the sign-up branch. Adds step tabs (Name+Email / Phone / Password), the +91/+1/+44 list and the inline 4-digit field. Target caps at 85 because the design merges three steps into one screen and the live chain deliberately uses four. |
| 26 | `weekly_subscription_scheduler` | **MERGE** → #18 | `SubscriptionScheduleScreen` | 50 → 72 | 0.0 | Per-day "Pick Flavor" is refused: the product intentionally enforces one juice across all delivery days, and the modify route was removed. Target 72 on the same screen #18 takes to 85. |
| 27 | `notifications` | **KEEP** (repair first) | `NotificationCentreScreen` `/notifications` | 48 → 85 | 0.75 | Split brain today: the routed screen is a hard-coded fixture, the BLoC screen is unreachable from an `AppDrawer` nobody instantiates. Route the BLoC screen, delete the fixture, add a bell in `BMJGlassHeader`. |
| 28 | `sign_in_email_entry` | **REMOVE** | — | 42 → — | 0.0 | Design is email → magic link / OTP. V1 has no email-OTP sign-in entry point; building it is new backend scope, not a restyle. |
| 29 | `sign_in_with_google` | **MERGE** → #7 | `GoogleSignupScreen` | 46 → 80 | 0.0 | Google's account chooser is SDK-rendered and cannot be restyled — that half is permanently capped. What is ours ("Almost there!" completion) lands on #7. |
| 30 | `sign_up_gateway` | **REMOVE** | — | 49 → — | 0.0 | A combined sign-in/sign-up gateway with password form. Both counterpart screens are unreachable, and its tab idea already exists on `LoginPage`. |

**Counts: 11 KEEP · 11 MERGE (into 5 canonical screens) · 8 REMOVE.** Every one of the 30 appears exactly once.

| Decision | Designs | Effort |
| :--- | :--- | ---: |
| KEEP | 1, 5, 8, 12, 13, 19, 20, 21, 23, 25, 27 (11) | **15.5 d** |
| MERGE → canonical | 2/3, 7/29, 11/16, 17/24/10, 18/26 (5 screens, 11 designs) | **5.25 d** |
| REMOVE | 4, 6, 9, 14, 15, 22, 28, 30 (8) | **0.0 d** |
| Foundation + nav (P0-1, P0-3) | no design row owns these | **5.0 d** |
| **Total** | **30 designs → 22 retained, 20 Flutter screens touched (2 new), 12 new files** | **25.75 d** |

---

## 5. P0 — four items, 10.0 d

P0 here means **gate for the ≥85 % objective**. (In `STITCH_V2_UI_MIGRATION.md` P0 meant launch blockers, and the PDP was deliberately P1 there because the size sheet already completes a purchase. This plan promotes it: a UX overhaul whose lowest-scoring design is the product page cannot call itself done.)

### 5.1 P0-1 · The "Subscription" tab opens Orders — 0.5 d

**Defect.** `dashboard.dart:106` puts `OrdersTab` at index 2; `:251` labels index 2 `Subscription`. A paying subscriber taps the one tab named after their subscription and gets a list of past orders.

**Change list.**
1. New `lib/views/screens/subscription_tab.dart` — a thin `StatelessWidget` that renders the existing subscription experience for the tab position.
2. `SubscriptionManagementScreen` gains `final bool embedded` (default `false`). When `true` it returns its body without its own `Scaffold`/`AppBar`. **Route behaviour is unchanged** — `/manage-subscriptions` still pushes the full screen.
3. `dashboard.dart`: `IndexedStack` child 2 becomes `const SubscriptionTab()`; `BMJGlassBottomNav` keeps the label `Subscription`.
4. Orders is re-homed, not lost. `ProfileTab` already renders an Orders entry that calls `onNavigateToOrders` (`profile_tab.dart:136-137`), but `dashboard.dart:110` wires that callback to `setState(() => _navIndex = 2)` — i.e. straight into the tab we are repurposing. Change it to `Navigator.pushNamed(context, '/orders')` (`main.dart:291` → `OrderHistoryPage`, V1 flow 6), and add a "See all" affordance to Home's existing recent-orders section (`home_tab.dart:970-998`). `orders_tab.dart` stays on disk, unreferenced, and joins the orphan list — no deletion in this wave.
5. Tab body gets the empty state (`BMJEmptyState`) with a "Browse plans" CTA → `/plan-selection` (this is also P0-2's first entry point).

**Acceptance.** Tap Subscription → subscription card with plan name, status pill, next delivery, pause/cancel; **no** order rows; **no** duplicate app bar; Orders reachable in ≤2 taps from Profile and from Home; `flutter analyze` clean; widget test asserts `find.text('Subscription')` and the absence of `OrdersTab`.

**Why 0.5 and not 0.25.** The label swap is minutes; re-homing two Orders entry points and adding the embedded flag with a test is the rest. Skipping the re-home is how the tab fix ships and quietly deletes the only way to see orders.

### 5.2 P0-2 · The plan catalogue has no door — 2.0 d

**Defect.** `PlanSelectionScreen` (design #20) is complete, Chargebee-wired code with **zero live callers**: `detail.dart:262` is a dead PDP and `subscription_plan_card.dart:18` is a widget instantiated nowhere. V1 flow 8 (plan catalogue) is unreachable, so the subscription business has no storefront.

**Entry points to add (all four).**

| # | Surface | Anchor | Copy |
| :--- | :--- | :--- | :--- |
| 1 | Subscription tab, no active plan → empty state | new `subscription_tab.dart` | "Start a subscription" |
| 2 | Subscription tab, active plan → footer CTA | `subscription_management_screen.dart` | "Change or add a plan" |
| 3 | Home active-subscription block | `home_tab.dart:522-573` | "Browse plans" |
| 4 | PDP "Subscribe" purchase option | new `product_detail_screen.dart` | "Subscribe" (D4) |

Plus the two compositional gaps that make the screen saleable: a **Weekly/Monthly segmented control** (period is currently per-card) and a **BEST VALUE badge computed from the cheapest weekly price** — data-driven, never hard-coded copy.

**Acceptance.** From a cold start, three taps to `/plan-selection`; the Chargebee hand-off produces the same session URL as today (test asserts the repository call, not the URL); each of the four entry points has a widget test; no plan price is computed client-side.

### 5.3 P0-3 · Design-system foundation — 4.5 d

Scope and order are in §3; tokens are in §2. This is the only P0 that changes every screen's appearance, so it is split into five reviewable commits:

| Step | Output | Review gate |
| :--- | :--- | :--- |
| 1 | `lib/theme/bmj_tokens.dart` + legacy aliases; `app_text_styles.dart` family and slots | `flutter analyze`; no widget file touched |
| 2 | The five `BMJGlass*` components | Golden test per component at 390×844 |
| 3 | Four supporting widgets | Golden test; contrast check |
| 4 | Adopt in `dashboard.dart` + `home_tab.dart` only | Side-by-side against `screen.png` for #21 |
| 5 | Palette/typography regression sweep over the rest | Screenshot 6 screens; no layout overflow at 320 dp |

**Acceptance.** `#F97316`, `#4AE176`, `#1C110B` present in `lib/`; `Roboto` no longer the app font; every text style resolves to Plus Jakarta Sans or Inter; all five components exist and are used by at least one screen; `grep -r "fontFamily: 'Roboto'" lib/` returns 0; text contrast ≥ 4.5:1 for body, ≥ 3:1 for display.

### 5.4 P0-4 · Product Detail flow — 3.0 d

**Target journey.** Catalog grid → tap product → **Product Detail** → select size → Buy Once (adds to cart) *or* Subscribe (plan catalogue) → cart → Chargebee checkout.

**What the design actually contains** (rendered text of `juice_detail_selection`): back + cart header · `Cold Pressed` / `Organic` tags · name · one-line description · `4.9 (128 reviews)` · `Select Size 200/300/500ml` · `Purchase Option` — One-Time `$8.00` / Subscribe & Save 15 % `$6.80` · `120 Calories` + `100 % Vitamin C` stat tiles · `Key Ingredients` list · sticky `Add to Cart – $6.80`.

**Data availability — every section must map to a field that exists, or it is dropped.**

| Section | Source field | Status |
| :--- | :--- | :--- |
| Image, name, description, tags | `Item.imagePath`, `name`, `description`, `metaData`/`tags` | Available |
| Rating + review count | `Item.rating` | Rating available; **review count has no API** → show rating only |
| Size chips + price | `Item.itemPrices` (name + price) | Available; reuse `_cheapestPrice()` (`product_catalog_screen.dart:366-374`) for the default |
| Calories | `DynamicJuice.kacl` | Available |
| Nutrition tiles | `DynamicJuice.nutritionalInfo` (map) | Available — render at most 2 entries, no invented values |
| "Key Ingredients" | `benefits` / `tags` | **Not a true ingredient list** → label the block "Highlights" unless a curated list exists |
| Subscribe & Save 15 % | — | **Refused (D4)** — the option routes to the real catalogue |

**Wiring.** The only behavioural change in the whole plan: `product_catalog_screen.dart`'s card `onTap` pushes `/productDetails` with the `CatalogItem` as argument. The existing one-tap path stays — the grid's `Add +` still opens the size sheet and fires `AddToCart(CartItem(item: item.item, selectedPrice: selectedPrice))` (`:376-420`). The PDP's Buy Once calls **the same** `AddToCart` with the **same** `CartItem` shape, so `CartBloc`, the cart screen and checkout are untouched.

**Files.** New `lib/views/screens/product_detail_screen.dart`; `detail.dart` (291 lines, hardcoded demo, unreachable) is deleted once the route points at the new screen; `main.dart:330` keeps the route name `/productDetails`; one `onTap` in `product_catalog_screen.dart`.

**Acceptance.**
- Add-to-cart from PDP produces a byte-identical `CartItem` to the size-sheet path (unit test on the two builders).
- "Subscribe" pushes `/plan-selection` (widget test) and the PDP never displays a discounted price.
- Deep link `/productDetails` with no argument renders an empty state, not a crash.
- No BLoC, repository, service or route-contract change; `git diff` touches only the three files above plus the `main.dart` import swap.

**Cap 88, not 95.** No review corpus, no ingredient provenance, no discount rule. Reaching 95 would require backend fields that do not exist.

---

## 6. P1 — 13 rows, 15.0 d (post-P0 polish on live screens)

Each row is *composition on a screen that already works*. Tokens are assumed adopted, so the numbers are repaint prices; done out of order, add 30–40 %.

| # | Screen | Now → Target | Work items | Effort (d) |
| :--- | :--- | ---: | :--- | ---: |
| 21 | Home | 61 → 90 | Testimonial rail, category chips, search affordance (composition only — no endpoint), 2-column product grid, 3-stat row ported from #22, "See all" → `/orders` | 2.0 |
| 19 | Subscription dashboard | 58 → 82 | "Active" pill, plan-card art, 9 PM cutoff banner restyle, `BMJAmountRow` billing line, embedded mode polish | 1.5 |
| 18 | Scheduler | 56 → 85 | Master-day lock, per-day chips (500 ml • Energy), 6/6 counter, price footer; one-juice rule preserved (#26 stays 72) | 1.5 |
| 1 | Address entry | 35 → 82 | Map-pin block, grouped sections, sticky CTA, 9 fields kept (D5) | 1.5 |
| 13 | Cart | 51 → 80 | Item-count header, per-row savings hint, `BMJAmountRow` subtotal, explicit "delivery & taxes at checkout" footnote | 1.0 |
| 5 | Address selection | 53 → 88 | Home/Work icons, delivery instructions, "Current location", confirm CTA at foot | 1.0 |
| 12 | Referral | 51 → 85 | WhatsApp share, 3-step copy, `1,500 pts` formatting, glass cards | 1.0 |
| 17 | Phone OTP verify | 57 → 90 | Glass skin, `(00:45)` timer, "Verify & Continue", Step 2 of 3 (from #24) | 1.0 |
| 7 | Google sign-up | 44 → 85 | Remove password field, "Verified by Google" chip, country picker, single Complete Signup CTA | 1.0 |
| 11 | Phone login entry | 52 → 90 | +91 selector, Terms/Privacy, hero copy; reached from `LoginPage`'s Phone OTP card | 1.0 |
| 25 | Phone sign-up entry | 46 → 85 | Step tabs, country list (+91/+1/+44), inline 4-digit field | 1.0 |
| 2 | Create password | 54 → 90 | Visibility toggle, strength meter, 4-rule checklist, Step 3 indicator (merges #3) | 0.75 |
| 23 | Email verify (after phone) | 59 → 90 | Glass skin, timer format, resend state polish | 0.75 |

**Deliberately not in P1** (and why): #27 notifications is a **repair**, not a restyle, so it sits in P2; `LoginPage` itself has no design among the 30 and is restyled by tokens only; `ProductCatalogScreen`, `CheckoutScreen`, `OrderHistoryScreen` and `ProfileTab` have **no Stitch design at all** (§13).

---

## 7. P2 — retiring the 8 removed designs safely (0.75 d, mostly mechanical)

Removal is the riskiest category, so it has preconditions and a rollback. **Deletion is last, not first.**

**Preconditions before any file is deleted**
1. `grep -rn "<className>(" lib/ test/` returns only the route registration.
2. The route name still resolves — replaced by a **redirect stub** to `/login` so old deep links do not 404.
3. `flutter analyze` and the full suite are green **with the redirect in place**, before the file is removed.
4. The removal commit touches no file in `bloc/`, `services/`, `UserRepository/` or `bmjServer/`.

**Inventory (7 files, 1,578 lines)** — eight designs map to seven files: #22 has no file of its own (it is a competing design for `HomeTab`), and #28's counterpart `LoginPage` is **kept** for password sign-in (D3), so only its design is retired.

| File | Lines | Route today | Fate |
| :--- | ---: | :--- | :--- |
| `sign_up_screen.dart` | 426 | not routed | delete; `test/widgets/signup_screen_test.dart` (2 references) is deleted with it |
| `signup_method_selection_screen.dart` | 260 | `/signup-method-selection` | delete + redirect stub |
| `email_signup_screen.dart` | 168 | `/email-signup` | delete + redirect stub |
| `email_verification_screen.dart` | 235 | `/email-verification` | delete + redirect stub (**note:** `EmailVerificationAfterPhoneScreen` stays — #23 is live) |
| `phone_entry_after_email_screen.dart` | 167 | `/phone-entry-after-email` | delete + redirect stub |
| `link_google_account_screen.dart` | 275 | not routed | delete |
| `otp_login_page.dart` | 47 | `/otp` | delete; route **repointed** to `PhoneOtpVerificationScreen` (fixes the latent `SignUp()`-without-verification trap) |

**What is explicitly *not* removed:** `create_password_screen.dart` (D3), `email_verification_after_phone_screen.dart` (#23), `phone_signup_screen.dart` (#25), `login_page.dart`, `detail.dart` (replaced by P0-4, not deleted until the new screen ships), `orders_tab.dart` (unreferenced after P0-1, retained), and the 6,908-line orphan set (separate decision, out of scope).

**Also in P2 (0.75 d):** #27 notifications repair — point `/notifications` at `NotificationCentreScreen`, delete the fixture list in `notifications.dart`, add the bell to `BMJGlassHeader`, and keep the mark-all-read BLoC call.

---

## 8. Target-score accounting (30 designs, explicit so it can be checked)

Baseline = `STITCH_IMPLEMENTATION_STATUS.md` §3. Targets are this plan's commitments, including every contract cap from §1/§12.

| # | Now | Target | # | Now | Target | # | Now | Target |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 35 | 82 | 11 | 52 | 90 | 21 | 61 | 90 |
| 2 | 54 | 90 | 12 | 51 | 85 | 22 | 58 | — (removed) |
| 3 | 56 | 90 | 13 | 51 | 80 | 23 | 59 | 90 |
| 4 | 38 | — (removed) | 14 | 56 | — (removed) | 24 | 56 | 90 |
| 5 | 53 | 88 | 15 | 59 | — (removed) | 25 | 46 | 85 |
| 6 | 51 | — (removed) | 16 | 43 | 90 | 26 | 50 | 72 |
| 7 | 44 | 85 | 17 | 57 | 90 | 27 | 48 | 85 |
| 8 | 20 | 88 | 18 | 56 | 85 | 28 | 42 | — (removed) |
| 9 | 37 | — (removed) | 19 | 58 | 82 | 29 | 46 | 80 |
| 10 | 54 | 90 | 20 | 51 | 88 | 30 | 49 | — (removed) |

**Arithmetic, retained set (22 designs):** baseline **1,101 / 22 = 50.0 %** → after **1,895 / 22 = 86.1 %**.
**Arithmetic, all 30:** baseline **1,491 / 30 = 49.7 %** → after **2,285 / 30 = 76.2 %** (the 8 removed designs keep their current scores: 38 + 51 + 37 + 56 + 59 + 58 + 42 + 49 = **390**).
**Designs at or above the 75 % bar:** **21 of 22** retained (**21 of 30** overall). The single retained design below 75 is #26 at 72, capped by the one-juice product rule.

> **Honest note on the headline.** The brief asks for ≥85 %. On the surface that ships, the plan lands at **86.1 %**. Reaching 85 % across all 30 would require re-opening the 8 retired designs (≈8.5 d) to style screens no customer can reach — a Product decision, not a design one.

---

## 9. Sequencing and effort — 25.75 d in five waves

| Wave | Scope | Designs / items | Days | Cumulative | Why this position |
| :--- | :--- | :--- | ---: | ---: | :--- |
| **W0 — Foundation + the two tab/storefront defects** | Tokens, 5 components, 4 supporting widgets, nav destination fix, 4 plan-catalogue entries | P0-1, P0-2, P0-3 (#20) | 7.0 | 7.0 | Tokens block every repaint; the catalogue entry is the only revenue gate; the tab fix is two hours of the seven days |
| **W1 — Purchase funnel** | PDP build + wire, cart summary, address selection | P0-4 (#8), #13, #5 | 5.0 | 12.0 | Highest revenue exposure. #8 and P0-2 share the `/plan-selection` seam, so they must be close together |
| **W2 — Onboarding** | Address entry, password, Google sign-up, phone login, phone OTP, email verify, phone sign-up | #1, #2/#3, #7/#29, #11/#16, #17/#24/#10, #23, #25 | 7.0 | 19.0 | 11 designs across 8 screens; least revenue-urgent live work, so it follows the funnel |
| **W3 — Subscription & retention** | Scheduler, management portal, referral | #18/#26, #19, #12 | 4.0 | 23.0 | Needs W0's entry point before the scheduler is visible at all |
| **W4 — Home, notifications, retirement** | Home composition, notification repair, delete 7 retired files behind redirects | #21, #27, removals | 2.75 | **25.75** | Home already scores best (61); retirement last keeps focus on customer value |

**Capacity.** 25.75 dev-days ≈ **5.2 weeks solo**, ≈ **3 weeks with two developers** running W1 and W2 in parallel after W0. Adding 25–30 % QA gives **≈6.5 weeks solo / ≈3.7 weeks for two**. W0 must be releasable on its own — that is what lets the tab bug and the missing storefront ship in week one instead of week six.

**Estimation basis.** 1.0 d = one focused day (≈6 productive hours) for a Flutter developer who knows this tree. Bands: 0.25–0.5 copy/label/single-widget · 0.75–1.5 composition on a wired screen · 2.0–3.0 new screen or new flow segment. Confidence ±25 % on the small rows, **±50 % on the 2–3 d rows** (#8 and P0-2 can double if the catalogue's plan/size model changes). Excludes design review, copywriting, legal copy, backend work and Chargebee configuration.

---

## 10. Verification gates

Nothing below is optional, and each gate names the command or artefact that proves it.

**Per commit**
1. `flutter analyze` — zero new issues (the tree already carries its baseline).
2. `flutter test` — all **30** existing test files green. Two of them are directly in the blast radius: `test/widgets/signup_screen_test.dart` (deleted with its screen) and anything asserting `OrdersTab` in the dashboard.
3. `git diff --stat` review — no file under `bmjServer/`, `bloc/`, `services/`, `UserRepository/` unless the commit is a declared UI-only rename.

**Per wave**
4. Widget tests for the changed screen plus a golden at 390×844 (dark) and 320×844 (overflow check).
5. Device pass on a physical phone: W0 → tab switch + plan catalogue reach; W1 → full purchase of one juice *and* one subscription; W2 → sign up with phone from a cleared install; W3 → pause and resume a subscription; W4 → home rails + notification read.
6. Contrast script over the token pairs (body ≥ 4.5:1, display ≥ 3:1).
7. `grep` assertions: `#F97316` and `#4AE176` present; `Roboto` absent as a font family; every `#FFB690`/`#F97316` use sourced from `bmj_tokens.dart`.

**Before declaring the objective met**
8. Re-score all 30 designs against the same rubric as `STITCH_IMPLEMENTATION_STATUS.md` and confirm **≥ 86 % on the retained set** and **21 of 22 ≥ 75 %**. If the re-score disagrees with §8 by more than 3 points on a screen, the screen is re-opened, not the rubric.

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Token flip changes every screen at once and regresses contrast/spacing somewhere unseen | High | Medium | W0 step 1 lands tokens **without** adoption; adoption is a separate commit per screen; 6-screen screenshot sweep before each wave ends |
| Dark-only design breaks the light theme users can still toggle to | Medium | Medium | D6: keep 6 daylight values, add a golden test for the light theme on cart + home |
| Glass blur (16–24 px) janks on low-end Android | Medium | High | Cap blur by device tier; test on the oldest target device in W1; keep the flat-fill fallback that `GlassCard` already supports via `isDark` |
| PDP "Subscribe" is read by customers as a discount promise | Medium | High | Copy says "Subscribe" only; the price shown is the size price; no percentage appears anywhere in `lib/` |
| Re-homing Orders breaks a user's habit or a test | Low | Medium | Two entry points added before the tab is repointed; `orders_tab.dart` retained; widget test on both entries |
| Deleting the 7 files breaks a deep link or an unindexed caller | Low | Medium | Redirect stubs + grep precondition (`§7`); deletion is its own commit and revertable |
| Address restyle tempts a field-model change | Medium | High | D5 is written into the acceptance criteria: 9 fields in, 9 fields out, payload diff must be empty |
| Scope creep into "Modify Plan" / plan change | Medium | High | `BMJ_V1_SCOPE.md` §3 is quoted in the design review; #19's target is 82 **by contract** |
| Re-score disagrees with the plan's targets | Medium | Low | §10 gate 8 re-opens the screen, and the difference is recorded — no silent re-basing |

---

## 12. What we will not build, even though Stitch shows it

Every row below is a place where copying the design would change business logic, backend contracts or Chargebee behaviour. Each has a safe UI substitute, so nothing in the visual language is lost.

| Stitch shows | Design | Why it is refused | What the UI does instead |
| :--- | :--- | :--- | :--- |
| `Subscribe & Save 15%` with a lower price | #8 | No discount rule exists; a client-side discount would misquote Chargebee | "Subscribe" opens the real plan catalogue; only catalogue prices are displayed |
| `Delivery $5.00` and `Subscription Savings -$6.00` | #13 | Fees and savings are computed on the Chargebee hosted page; no fee field exists in `lib/` | Subtotal + "Delivery and taxes calculated at checkout" |
| `Modify Plan` as the primary CTA | #19 | `PUT /api/v1/subscriptions/{id}/modify` was removed; Pricing Pages are `410 Gone` (`BMJ_V1_SCOPE.md` §3) | Pause / Resume / Cancel + "Change or add a plan" → catalogue (new subscription, not an edit) |
| Per-day flavour picking ("Pick Flavor") | #26 | Product rule: one juice across all delivery days; also relies on the removed modify route | Same-juice schedule, per-day size chips only |
| Email + password sign-up and email OTP sign-in | #4, #6, #15, #28, #30 | D-5 de-advertised the email path; email-OTP sign-in has no backend support | Google + Phone OTP onboarding; `LoginPage` keeps password **sign-in** for existing customers (D3) |
| Star rating with `(128 reviews)` | #8 | `Item.rating` exists; no reviews endpoint | Rating shown without a review count |
| `Key Ingredients` as a curated list | #8 | Only `benefits` / `tags` exist | Block labelled "Highlights" unless a curated list is supplied |
| Zomato / Swiggy instant-delivery panel | #21 | Outbound commercial surface, not part of the ten V1 flows | Omitted; the home rail is filled with real content |
| Category chips and search | #21 | No search endpoint in `docs/API.md` | Chips filter the already-fetched catalogue client-side; search opens the catalog tab (no fake result list) |

---

## 13. Four in-scope V1 flows have no Stitch design

These cannot be migrated, only token-restyled. No target percentage is quoted for them, because there is nothing to be faithful to.

| V1 flow | Screen(s) | Status |
| :--- | :--- | :--- |
| 3 · Catalog browse | `ProductCatalogScreen`, `MenuTab` | **No design** — the 30 folders contain no product list. Becomes the entry to P0-4. |
| 5 · One-time checkout | `CheckoutScreen` → Chargebee hosted page | Third-party page; not designable |
| 6 · Order history | `OrderHistoryPage`, `OrderHistoryScreen`, `OrderDetailScreen` | **No design** — restyled by tokens only |
| 9 · Profile read | `ProfileTab`, `UserProfileScreen`, `MyAccountPage` | **No design** — restyled by tokens only; `ProfileTab` gains the Orders and Notifications entries |

This is also the honest ceiling on the 86 % figure: four of the ten flows that actually ship are outside the Stitch set entirely, so "Stitch alignment" is a proxy for visual consistency, not for total product quality.

---

## 14. Definition of done

**Design system**
- `lib/theme/bmj_tokens.dart` is the only source of colour, type, radius and spacing values; no raw hex outside it (except in tests).
- The five `BMJGlass*` components exist, are golden-tested, and are used by the dashboard, PDP, cart and at least one auth screen.
- Dark is the default; light renders without contrast failures.

**UX defects**
- The Subscription tab shows a subscription; Orders is reachable in ≤2 taps from Profile and Home.
- `/plan-selection` is reachable from 4 surfaces and produces a working Chargebee session.
- Catalog → PDP → size → Buy Once **and** Subscribe are both live; the one-tap size-sheet path still works.

**Scope integrity**
- `git diff` against the pre-wave tag shows **zero** changes in `bmjServer/`, `bloc/`, `services/`, `UserRepository/`, or any Chargebee configuration.
- No new API call, no new endpoint, no new pricing rule, no new address field, no plan-change capability.
- 7 files retired behind redirect stubs; the app still resolves every old route.

**Quality**
- `flutter analyze` clean; the full test suite green (29 files after the one deletion, plus new PDP/nav/token tests).
- 21 of 22 retained designs ≥ 75 %; retained-set mean **≥ 86 %**; full-set mean **≥ 76 %**.

---

## 15. Open decisions and the next action

| Decision | Owner | Default if nobody answers |
| :--- | :--- | :--- |
| **D2** — 4 tabs with Orders re-homed (recommended) vs a 5th Orders tab | Product | Proceed with 4 tabs; re-homing Orders is reversible in one commit |
| **D6** — keep the light theme (recommended) vs ship dark-only | Product | Keep light; it costs ~6 token values and zero screens |

Both are one-line answers and neither blocks W0 step 1 (tokens) or step 2 (components), which are visual-language work and identical under either answer.

**Next action (coding step 2):** begin W0 with `lib/theme/bmj_tokens.dart` + `app_text_styles.dart` re-pointing as a single commit that changes **no** call site, then the five `BMJGlass*` wrappers, then the dashboard/home adoption commit. P0-1 and P0-2 follow in the same wave because they are small, independent of the tokens, and each removes a customer-visible defect.

**Traceability.** Every claim in this plan carries a `file:line`, a rendered-text extraction from the Stitch bundle, or a named command. The extraction helper used for the rendered-text claims is `C:\Users\Public\stitch_text.py` (read-only; prints the visible text of any `code.html`). Reachability claims remain static — a 15-minute device pass (gate 5) is the only way to close that gap, and it is scheduled in W0.
