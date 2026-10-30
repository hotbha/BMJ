# STITCH_IMPLEMENTATION_STATUS.md — Flutter fidelity vs the Stitch bundle

**Prepared:** 17 October 2026
**Question answered:** *how much of what Stitch designed is actually built in `lush/`?*
**Inputs:** `Stitch/**` — 31 design folders, 31 `code.html`, 31 `screen.png`, 3 `DESIGN.md` (30 unique screens after de-duplication); `lush/lib/views/screens/**` (60 Dart files); `lush/lib/theme/**`.
**Status:** ⚠️ **Analysis only.** No Flutter file, Stitch file or asset was created, edited or deleted in this pass. Nothing was run on a device.

---

## 0. What was measured, and what was not

| Step | Method | Output |
| :--- | :--- | :--- |
| 1 | Stripped `<script>`/`<style>` from every `code.html` and extracted headings, body strings, button labels, placeholders, colour hex, radius classes, `backdrop-blur`/`grid-cols-2` counts | Structural fingerprint per design |
| 2 | Parsed each counterpart Dart file for `Text('…')` literals, `AppColors.*` tokens, `Color(0x…)`, `BorderRadius.circular`, `BackdropFilter`, `BlocBuilder`, `context.read`, `GridView`/`ListView`, `pushNamed` | Structural fingerprint per screen |
| 3 | Traced routes in `main.dart` and every `pushNamed` in `lib/` | Reachability per screen |
| 4 | Grepped the whole of `lib/` for the two Stitch palettes (`#FFB690`, `#F97316`, `#4AE176`, `#FFBC49`) | **NONE found** |
| 5 | Counted style-system usage across `lib/` | `Roboto` 64 refs · `GoogleFonts` 4 files · `AppTextStyles` 12 files · `AppColors.glass*` 11 files · `BackdropFilter` 4 files |

> **Explicit limitation.** No Flutter build was launched and no screenshot was captured, so **Visual** is judged from design tokens and style code, **not** from a rendered pixel diff. The 30 `screen.png` files remain the ground truth for a future pixel review. All percentages are rubric judgements (±10), not image-similarity output.

---

## 1. Rubric

| Axis | What earns points |
| :--- | :--- |
| **Visual** | Palette family (dark glass vs light), primary hue, type family/weights, shape language (8/16/24 px radii), elevation (blur + hairline borders), imagery treatment |
| **Layout** | Which sections exist and in what order, grid model (2-column vs list), header/nav pattern, density and spacing scale |
| **Interaction** | Controls present **and** wired — state changes, BLoC events, API calls, navigation, validation, timers |

**Implementation % = 0.35 · Layout + 0.35 · Visual + 0.30 · Interaction**

Anchors: **90–100** faithful port · **75–89** same design, minor drift · **50–74** same flow, different skin or composition · **25–49** same purpose, substantially different UI · **0–24** stub or absent.

Weights are a choice, not a measurement. Re-weighting to Layout 50 / Visual 25 / Interaction 25 moves the headline from **49.6 %** to **52.1 %** — the conclusion is insensitive to the weighting.

---

## 2. Headline

| Metric | Value |
| :--- | ---: |
| **Overall Stitch implementation — 30 unique designs** | **50 %** (sum 1 491 / 30 = 49.7) |
| Overall — one design per unique flow (20 flows, duplicates removed) | **49 %** |
| Average **Visual** match | **29 %** |
| Average **Layout** match | **57 %** |
| Average **Interaction** match | **65 %** |
| Screens scoring ≥ 75 % (faithful port) | **0 of 30** |
| Screens scoring 50–74 % | 19 |
| Screens scoring 25–49 % | 10 |
| Screens scoring < 25 % | 1 (`juice_detail_selection`) |

**Reading of the result.** Stitch's *information architecture* is largely present — every unique flow has a working screen, and interaction wiring is the strongest axis. What is **not** present is the Stitch *visual language* (zero palette adoption, Roboto instead of Poppins/Plus Jakarta Sans, light Material surfaces on 2 of 3 screens) and a handful of compositions (product detail, cart money summary, per-day scheduler, home testimonials). No screen is a faithful reproduction of its design.

---

## 3. Screen-by-screen status (all 30 unique designs)

`Impl` is the weighted composite; `Vis` / `Lay` / `Int` are the three axes.

| # | Stitch file | Flutter screen (route) | Impl | Vis | Lay | Int | Remaining work |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| 1 | `address_entry_onboarding/code.html` | `AddressEntryScreen` (`/address-entry`) | **35** | 15 | 45 | 45 | Dark-glass shell absent. Field model diverges: Flutter collects 9 fields (First, Last, Flat, Society, Sector, City, State, ZIP, Country) against the design's 4 (Flat/Building, Street/Area, City, Pincode). No map-pin block ("Tap to adjust on map"). Decide the field model before restyling. |
| 2 | `create_password/code.html` | `CreatePasswordScreen` (`/create-password`) | **54** | 20 | 65 | 80 | Structure already matches (title, new + confirm, rule block, submit). Both fields are `obscureText: true` with **no visibility toggle** (the design has one). No strength meter ("Weak"). Light theme vs dark glass. |
| 3 | `create_password_step_3/code.html` | `CreatePasswordScreen` (`/create-password`) | **56** | 20 | 70 | 80 | Content is the **password step** (Step 3: Password, 4-item checklist, Complete Setup) — the `<title>` reading "Delivery Address" is stale. Checklist is implemented; missing a "Step 3" progress indicator and the glass skin. |
| 4 | `create_your_profile_step_1/code.html` | `SignUpScreen` (not routed) + `UserProfileScreen` (`/user-profile`) | **38** | 20 | 40 | 55 | SignUpScreen has name/email/password only. Missing: profile-photo picker (`add_a_photo`), "Step 1 of 3" indicator, "Send OTP to Email" framing, Terms line. `UserProfileScreen` is a profile *view* and is not this design. |
| 5 | `delivery_address_selection/code.html` | `AddressSelectionScreen` (`/address-selection`) | **53** | 25 | 65 | 70 | Card list, DEFAULT badge, add-new, delete-with-confirm and set-default all wired. Missing: Home/Work icon labels, per-address delivery instructions, "Current Location" action, explicit Confirm CTA at the foot. |
| 6 | `email_signup_verification/code.html` | `EmailSignupScreen` (`/email-signup`) → `EmailVerificationScreen` (`/email-verification`) | **51** | 22 | 60 | 75 | Two screens cover one design. Code entry, 60 s resend countdown, validation and API verify are real. Missing: single-screen continuity, the password field on the verify step, dark styling. |
| 7 | `google_sign_up_phone_binding/code.html` | `GoogleSignupScreen` (`/google-signup`) + `GooglePhoneEntryScreen` (`/google-phone-entry`) | **44** | 20 | 50 | 65 | Phone binding exists (name + phone + Send OTP, real API). Flutter adds a password step the design does not have; design has a country picker (+1), a "Welcome, Alex!" greeting and a single Complete Signup CTA. |
| 8 | `juice_detail_selection/code.html` | `DetailPage` (`/productDetails`) — **orphaned** | **20** | 25 | 20 | 15 | Largest gap. `detail.dart` is a legacy demo: hardcoded "Subscribe @Rs. 129 → 89/juice", Buy Now only toasts "Feature coming soon!", no size chips, no One-Time vs Subscribe choice, no nutrition, ingredients or rating. `/productDetails` is registered but **nothing in `lib/` pushes it** (recursive grep); the live catalog adds to cart from the grid + size sheet instead. Stitch's PDP has no working implementation. |

---


| 9 | `link_google_account/code.html` | `LinkGoogleAccountScreen` (not routed) | **37** | 25 | 45 | 40 | Design is one-tap "Link Accounts" plus "Use Password Instead". Flutter renders an OTP field, resend timer and Cancel — a different interaction model. Not reachable from any surface. |
| 10 | `otp_verification/code.html` | `/otp` → `OTPLoginPage` (**stub**); real UI in `PhoneOtpVerificationScreen` (`/phone-otp-verification`) | **54** | 30 | 65 | 70 | The route binds a 54-line stub: pin field + "Submit" that pops to root and fires `SignUp()` — no verification, no resend. The working screen is 6-digit with a 60 s resend, BLoC and Firebase. Design is 4-digit. Fix: point `/otp` at the real screen or delete the route. |
| 11 | `phone_login_entry/code.html` | `PhoneLoginScreen` (`/phone-login`) | **52** | 28 | 60 | 70 | Title + number + "Send OTP via SMS" is real. Missing: +91 country selector (`expand_more` in the design — zero country-picker code in the file), Terms/Privacy links, the design's hero copy. |
| 12 | `referral_rewards_program/code.html` | `ReferralScreen` (`/referral`) | **51** | 25 | 60 | 70 | Code, copy-to-clipboard, `share_plus` share, 4-step explainer and "Total Earned ₹" are wired to the API. Missing: direct WhatsApp share, the design's 3-step copy, points-balance format ("1,500 pts"), glass card treatment. |
| 13 | `shopping_cart_savings_summary/code.html` | `CartScreen` (`/cart`) | **51** | 30 | 60 | 65 | Item rows, quantity, remove, clear-cart, address + slot selection and checkout hand-off are real. The summary is **Subtotal only**: no promo field (no coupon code exists anywhere in `lib/`), no delivery line, no subscription-savings line, no total — tax and total are deliberately owned by Chargebee. |
| 14 | `signup_method_selection/code.html` | `SignupMethodSelectionScreen` (`/signup-method-selection`) | **56** | 30 | 65 | 75 | Three method buttons with BLoC events and the real Google SDK. Labels read "Sign up with …" vs the design's "Continue with …"; no "or" divider, no Terms/Privacy footer, logo asset instead of the mark. |
| 15 | `sign_in_email_otp_verification/code.html` | `EmailVerificationScreen` (`/email-verification`) | **59** | 25 | 75 | 80 | Structurally the closest match in the set: icon, title, masked email, six boxes, resend with countdown, verify CTA, API verify. Remaining: dark-glass skin, the design's `(00:45)` timer format, "Verify Sign In" wording. |
| 16 | `sign_in_phone_entry/code.html` | `LoginPage` (`/login`) | **43** | 30 | 40 | 60 | LoginPage is a full email/password + Google + forgot-password composition; the design is a phone-only entry. The closer screen is `PhoneLoginScreen` (see #11) but it is not the route this design belongs to. |
| 17 | `sign_in_phone_otp_verification/code.html` | `PhoneOtpVerificationScreen` (`/phone-otp-verification`) | **57** | 28 | 70 | 75 | Section order matches (icon, title, masked number, six boxes, resend, verify). Missing: dark-glass skin, `(00:45)` timer format, "Verify Continue" wording. |
| 18 | `simplified_weekly_scheduler/code.html` | `SubscriptionScheduleScreen` (`/subscription-schedule`) | **56** | 45 | 60 | 65 | One of only 3 screens using `BackdropFilter`, so the visual family is close. "Same juice everyday" covers the design's "Same for all days"; Sunday is a holiday. Missing: master-day lock ("Synced to Monday"), per-day chips ("500ml • Energy"), 6/6 day counter and price footer. |
| 19 | `subscription_management_portal/code.html` | `SubscriptionManagementScreen` (`/manage-subscriptions`) | **58** | 30 | 70 | 75 | Plan card, ID, next billing, the 9 PM cutoff banner ("Actions available after 9 AM tomorrow") and Pause/Cancel/Resume are all wired. Missing: **Modify Plan** — the design's primary CTA — because no production plan-change endpoint exists; also the "Active" status pill and the price/plan-card art. |
| 20 | `subscription_plan_comparison/code.html` | `PlanSelectionScreen` (`/plan-selection`) | **51** | 30 | 55 | 70 | Plan cards, size selector and Chargebee checkout work. Missing: the Weekly/Monthly segmented toggle (period is per card), per-tier feature lists, and the BEST VALUE badge — the POPULAR ribbon exists only in `subscription_plans_screen.dart`, which is unreachable. |
| 21 | `unified_discovery_dashboard/code.html` | `HomeTab` (`/dashboard`, tab 0) | **61** | 55 | 60 | 70 | Best match in the set. Dark glass, hero, active-subscription card with bottle count and next delivery, trending rail, recent orders, 4-tab glass nav. Missing: testimonial carousel ("Real Stories"), category chips, search affordance, and a 2-column grid (trending is a 5-item horizontal list). |
| 22 | `unified_home_dashboard/code.html` | `HomeTab` (`/dashboard`, tab 0) | **58** | 55 | 55 | 65 | Same implementation as #21 — this is the competing duplicate design. Missing the design's 3-stat row (juices consumed / bottles returned / day streak) and per-card quick-add. |
| 23 | `verify_email_otp_step_1.1/code.html` | `EmailVerificationAfterPhoneScreen` (`/email-verification-after-phone`) | **59** | 25 | 75 | 80 | A near-copy of `EmailVerificationScreen`; six boxes, resend and API verify match the design. Remaining: skin and timer format. Two Flutter screens for one design is duplication, not extra coverage. |
| 24 | `verify_phone_otp_step_2.1/code.html` | `PhoneOtpVerificationScreen` (`/phone-otp-verification`) | **56** | 28 | 68 | 75 | Same target as #17. Missing the design's "Step 2 of 3" indicator; the rest of the composition is equivalent. |
| 25 | `verify_phone_step_2/code.html` | `PhoneSignupScreen` (`/phone-signup`) → `PhoneOtpVerificationScreen` | **46** | 22 | 55 | 65 | Sends the OTP then hands off to the verification screen. The design's step tabs (Name+Email / Phone / Password), country list (+91/+1/+44) and inline 4-digit entry have no counterpart. |
| 26 | `weekly_subscription_scheduler/code.html` | `SubscriptionScheduleScreen` (`/subscription-schedule`) | **50** | 45 | 50 | 55 | Same target as #18. Quick Fill, Repeat Last and per-day "Pick Flavor" have no counterpart — the app intentionally enforces one juice across all delivery days, so this is a product decision to record, not a bug. |
| 27 | `notifications/code.html` | `/notifications` → `NotificationsScreen` (static); `NotificationCentreScreen` (**unreachable**) | **48** | 25 | 70 | 50 | Split brain: the routed screen renders a hard-coded fixture list with local mark-all-read; the BLoC-backed, API-reading `NotificationCentreScreen` is never routed (only the dead `app_drawer` pushes `/notifications`). Design's per-type icons, timestamps and unread emphasis are not rendered. |
| 28 | `sign_in_email_entry/code.html` | `LoginPage` (`/login`) | **42** | 28 | 45 | 55 | Design is email → OTP/magic link. LoginPage is email + password; `EmailEntryAfterPhoneScreen` does send an OTP but belongs to the phone-first flow. There is no email-OTP sign-in entry point. |
| 29 | `sign_in_with_google/code.html` | `GoogleSignupScreen` (`/google-signup`) | **46** | 25 | 50 | 65 | Google's own account chooser is OS/SDK-rendered and cannot be restyled (and is not). The "Almost there!" half maps to the profile-completion form. Missing: optional mobile field on the same screen, "Verified by Google" chip, and PIN-code country handling (`country: 'IN'` is hardcoded). |
| 30 | `sign_up_gateway/code.html` | `SignUpScreen` (not routed) + `SignupMethodSelectionScreen` (`/signup-method-selection`) | **49** | 28 | 55 | 65 | No single counterpart: password form + method picker cover the design in two screens. Missing the Sign In / Sign Up mode tabs, the Terms line and the brand hero ("Vitalize Your Day"). |

---

## 4. Where the missing 50 points are

### 4.1 Axis summary

| Axis | Mean | Reading |
| :--- | ---: | :--- |
| **Visual** | **29 %** | The largest deficit by far, and it is systemic rather than per-screen. `lib/` contains **zero** occurrences of `#FFB690`, `#F97316`, `#4AE176` or `#FFBC49`; the shipped primary is `#FF8C42`, typography is `Roboto` (64 refs), and only 4 files in `lib/` use `BackdropFilter` (3 screens plus `glass_card.dart`) while 11 files reference the glass token set. Two of every three screens render as light Material surfaces; Stitch is 100 % dark glass. |
| **Layout** | **57 %** | Section order is usually right; what is missing is *composition* — a product detail page, a full money summary, a per-day scheduler, plan tiers with features, testimonials on home. |
| **Interaction** | **65 %** | The strongest axis. BLoC events, API calls, resend timers, validation, delete/confirm dialogs and Chargebee checkout hand-offs are real on 19 of 30 screens. Failures are concentrated in the orphaned PDP, the `/otp` stub and the two notification implementations. |

### 4.2 The five structural gaps

| # | Gap | Designs affected | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | **Stitch's visual language was never adopted** | all 30 | 0 Stitch hex tokens in `lib/`; `Roboto` vs Poppins/Plus Jakarta Sans + Inter; light surfaces on the auth, cart, orders, profile and address screens |
| 2 | **No product detail page** | #8 | `/productDetails` registered in `main.dart:330`, pushed from **nowhere**; `detail.dart` shows "Feature coming soon!" and hardcodes 129 → 89 |
| 3 | **Cart money summary is one line** | #13 | `cart_screen.dart` renders Subtotal only; no promo, delivery, savings or total line. The only `promo` matches in `lib/` are `NotificationType.promotion` in `notifications.dart` — there is no coupon code anywhere |
| 4 | **Bottom-nav model does not match the designs** | #19, #21, #22, #27 | `dashboard.dart` label "Subscription" renders `OrdersTab` (`dashboard.dart:106`); there is no Orders destination at all. Stitch's nav is Home / Subscription / Orders / Profile |
| 5 | **Duplicate designs share one implementation** | #3, #15/#23, #10/#17/#24, #18/#26, #21/#22, #14/#30 | Each duplicate pair scores the same implementation twice, which is why the per-design average is 50 % while the per-flow average is 49 % |

> Gap 4 is a genuine defect, not just a design difference: tapping **Subscription** shows order history (`IndexedStack` child 2 is `OrdersTab`, `dashboard.dart:106`). Nothing in the shipped tab bar opens subscription management, which is reachable only from profile/home entry points.

---

## 5. Highest-leverage remaining work

Ranked by overall percentage gained per unit of risk. `Δ overall = Δ impl ÷ 30`.

| Rank | Work item | Screens | Δ impl each | Δ overall | Risk / cost |
| ---: | :--- | :--- | ---: | ---: | :--- |
| 1 | **Adopt one Stitch token set** (palette, type scale, radii, blur, hairline borders) in `AppTheme` + `AppColors` + `AppTextStyles` | ~26 light screens | +16 | **+13.7** (50 → 64) | Medium churn, low logic risk: tokens are centralised, but it repaints every screen and must be verified against the existing test battery. Pick **one** architecture — `lush_architecture` (gold) or `vibrant_zest` (orange) — not both. |
| 2 | **Build the product detail page** to #8 (size chips, One-Time vs Subscribe, nutrition, ingredients, rating, add-to-cart) and push it from the catalog grid | #8 | +60 | **+2.0** | Medium — new screen, but API and size/price data already exist (`ProductCatalogBloc`, `size_selection_modal`) |
| 3 | **Complete the cart summary** (promo field, delivery, subscription savings, total) | #13 | +21 | +0.7 | Low code, **high product risk** — tax and total are deliberately delegated to Chargebee; adding local totals duplicates pricing logic |
| 4 | **Consolidate notifications** — route `/notifications` to the BLoC screen, delete the fixture | #27 | +22 | +0.7 | Low |
| 5 | **Fix the `/otp` route** — bind the real OTP screen, delete the stub | #10 | +18 | +0.6 | Low |
| 6 | **Nav model** — add an Orders destination, point Subscription at subscription management | #19, #21, #22 | +5 | +0.3 | Low code, medium UX impact |
| 7 | **Per-day scheduler + Quick Fill** | #18, #26 | +16 | +1.1 | Medium — contradicts the current one-juice-for-all-days rule; needs a product decision first |

Rows 1–6 total **+18.0**, i.e. **50 % → 68 %**. Passing **75 %** additionally requires per-screen composition work that no token change touches: home testimonials and category chips, plan-tier feature lists, address-entry map block, Google/Auth gateway unification.

---

## 6. Relationship to `STITCH_ALIGNMENT_REPORT.md`

Both documents are correct; they measure different things.

| | `STITCH_ALIGNMENT_REPORT.md` (16 Oct) | This document (17 Oct) |
| :--- | :--- | :--- |
| Unit of measure | **Presence** — does a Flutter counterpart exist and is it wired (A/B/C/D/E) | **Fidelity** — how closely the counterpart reproduces the design (0–100) |
| Headline | 21 of 31 designs **A**, 0 **C**, 1 **E** | Mean **50 %**, 0 of 30 designs ≥ 75 % |
| "Already implemented" means | screen exists, routes exist, BLoC/API wiring is real | nothing — fidelity is scored separately |
| Practical consequence | no V1 *flow* is missing | most screens would visibly change if Stitch were honoured |

Examples where the two verdicts diverge, and both are true:

| Design | Earlier status | Fidelity here | Why both hold |
| :--- | :--- | ---: | :--- |
| #8 `juice_detail_selection` | **A** | 20 % | `DetailPage` exists and is registered — but it is a demo with "coming soon" and is pushed from nowhere |
| #13 `shopping_cart_savings_summary` | **A** | 51 % | Cart works end-to-end; the savings/summary half of the design does not exist |
| #19 `subscription_management_portal` | **B** | 58 % | Pause/Cancel/Resume are wired; Modify Plan and the visual treatment are not |
| #21 `unified_discovery_dashboard` | **A** | 61 % | Home shell exists; testimonials, categories and 2-column grid do not |

**Two factual corrections to the earlier report**, found while profiling the HTML:

1. **#3 `create_password_step_3`** is described there as "a duplicate of #1/#5" holding *Delivery Address*. Its markup is a **password step**: "Step 3: Password", Enter Password, Confirm Password, Password Strength, four-rule checklist, Complete Setup. The folder name is right; the `<title>` ("BookMyJuice - Delivery Address") is stale. It duplicates **#2**, not the address screens.
2. **#27 `notifications`** is described as a "dead notification centre". It is two screens: `NotificationsScreen` is **routed but static** (hard-coded fixture); `NotificationCentreScreen` is **BLoC-backed but unrouted**. The capability is half-built twice, not absent.

---

## 7. Duplicate designs (why the average is per-design, not per-flow)

| Design(s) | Relationship | Evidence |
| :--- | :--- | :--- |
| #3 → #2 | Same password step, stale title in #3 | identical field set and checklist |
| #6, #15, #23 | Three email-verification designs | same six-box + resend structure; #15 and #23 are near-identical |
| #10, #17, #24 | Three phone-OTP designs | same structure; #24 adds "Step 2 of 3" |
| #18, #26 | Two schedulers | #26 adds Quick Fill / Repeat Last / per-day flavours |
| #21, #22 | Two home dashboards | same hero + subscription card; #22 adds a 3-stat row |
| #11, #16 | Two phone-entry designs | #16 is the sign-in framing, #11 the login framing |
| #14, #30 | Two auth gateways | #30 adds Sign In/Sign Up tabs |
| `sign_in_email_otp_verification` | **Byte-identical across both export batches** (12 444 B) | same file length and content |

31 folders therefore contain **30 unique designs** and roughly **20 unique flows**. The 20-flow mean is **49 %** — statistically indistinguishable from the 30-design mean of **50 %**, so duplicate inflation is *not* what produces the headline number.

---

## 8. Limitations and how to close them

| # | Limitation | Effect | How to close |
| :--- | :--- | :--- | :--- |
| 1 | No rendered Flutter screenshots were taken (no device/emulator run in this pass) | **Visual** is scored from tokens and style code, not pixels | Run the app, capture the 30 routes, place beside `screen.png`, then diff |
| 2 | Axis scores are rubric judgements | ±10 per axis, so ±5 on `Impl` | Two reviewers score independently; keep the rubric anchors fixed |
| 3 | Only `code.html` was parsed; `screen.png` was not opened | Hero/gradient/imagery judgements rely on markup classes | Pixel review pass against the 30 PNGs |
| 4 | Design-system choice is unresolved (two architectures ship in the bundle) | Any "adopt tokens" work is blocked on picking one | Governance decision: `lush_architecture` (gold, Poppins) vs `vibrant_zest` (orange, Plus Jakarta Sans) |
| 5 | Weighting (35/35/30) is a choice | Headline moves 49.6 → 52.1 under 50/25/25 | Disclosed; conclusion unchanged |

---

## 9. Verdict

| Question | Answer |
| :--- | :--- |
| **Overall Stitch implementation** | **50 %** across 30 unique designs (49 % across 20 unique flows) |
| Is every Stitch flow implemented? | **Yes** — 20 of 20 flows have a working screen |
| Is any Stitch screen faithfully reproduced? | **No** — 0 of 30 reach 75 %, best is `unified_discovery_dashboard` at 61 % |
| Best match | Home dashboard (#21) — dark glass, subscription card, trending rail |
| Worst match | Product detail (#8) at 20 % — demo screen, orphaned route, no purchase options |
| Biggest single cause | Visual language never adopted: 0 Stitch colour tokens, `Roboto`, light surfaces (Visual 29 %) |
| Second cause | Four missing compositions: PDP, cart money summary, per-day scheduler, plan tiers |
| Real defect found | Tab labelled **Subscription** renders order history (`dashboard.dart:106`) |
| What a port would buy | ~+14 % overall from tokens alone, ~+18 % with the four compositions — without touching working flows |
| What a port would cost | A full repaint of 26 screens, one product decision (scheduler), one pricing decision (cart totals) |

*Analysis only: this document creates no Flutter screen, edits no Dart, and deletes nothing. The numbers are reproducible from `code.html` structure, Dart source and the greps listed in §0.*
