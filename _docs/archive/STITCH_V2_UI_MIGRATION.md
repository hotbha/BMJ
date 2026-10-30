# Stitch V2 — UI Migration & Prioritisation

**Status:** analysis only. **No code, route, token, test or asset was changed to produce this document.**
**Prepared:** 17 October 2026 · **Owner:** Engineering (UI track)
**Percentages from:** [`STITCH_IMPLEMENTATION_STATUS.md`](STITCH_IMPLEMENTATION_STATUS.md) — 30 unique designs, weighted composite (Layout 0.35 / Visual 0.35 / Interaction 0.30).
**Scope contract:** [`docs/BMJ_V1_SCOPE.md`](docs/BMJ_V1_SCOPE.md) (flow freeze) · [`BMJ_LAUNCH_CHECKLIST.md`](BMJ_LAUNCH_CHECKLIST.md) (blocker legend) · [`DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).

---

## 0. What this document decides

1. One priority — **P0 / P1 / P2** — for each of the 30 designs.
2. **Current %**, **target %** and **effort in dev-days** for each.
3. The order in which the work can actually be done (§9), and what it costs.
4. What V2 deliberately does **not** do (§7) — because the frozen V1 contract already forbids it.

It does not re-score screens (that is the baseline document's job) and it does not propose code.

---

## 1. How priority was assigned

Three tests, applied in order. A screen's *score* never raises its priority; only a user can.

| Test | Question | Consequence |
| :--- | :--- | :--- |
| **A. Flow** | Is the screen inside one of the ten frozen V1 flows (`BMJ_V1_SCOPE.md` §2)? | No → ceiling of P1 |
| **B. Reachability** | Does anything in `lib/` navigate to it? | No → ceiling of **P2** (see R1) |
| **C. Severity** | In a live screen, does a day-one customer hit a wrong answer, a dead control, or a missing money field? | Yes → **P0**; visible divergence → **P1** |

**R1 — no live caller means no priority above P2.** An unreachable screen cannot block a launch, cannot confuse a customer and cannot lose a rupee. It can only be *retired* or *revived with an entry point*, and both of those are decisions, not styling. This single rule reclassifies 10 designs that a score-only reading would have put in P0/P1.

| Priority | Meaning here | Project legend equivalent |
| :--- | :--- | :--- |
| **P0** | Fix before onboarding paying customers, or accept a workaround in writing. | `BLOCKER` |
| **P1** | Ship without it; do it in the first post-launch iteration. | `POST-LAUNCH` |
| **P2** | Cosmetic, or invisible (dead / withdrawn / duplicate). No launch or retention impact. | `IGNORE` |

> **P0 is deliberately short — three items, 5.75 days.** `BMJ_LAUNCH_CHECKLIST.md` lists 14 launch blockers (B1–B14) and **not one is a UI item**; they are process, backend and data defects. The UI does not gate launch. Two of the three P0 items are navigation defects rather than styling, and the third is the styling foundation itself.

---

## 2. New evidence: reachability (and why it changes the answer)

Method: parsed all **47 route registrations** in `lush/lib/main.dart`, every `'/route'` literal in `lush/lib/**`, and the class→file map; then walked the graph from `LoginPage` and `Dashboard`. There is **no route-constant indirection** in the tree (`Routes.*` appears 0 times), so a literal scan is complete for *static* navigation.

Result: **26 of 47 registered routes have a live caller; 21 do not.** Of the 30 designs, **17 still have a live target screen** and 13 do not.

| Dead route | Screen | Why it matters |
| :--- | :--- | :--- |
| `/plan-selection` | `PlanSelectionScreen` | **Only** pushed by `detail.dart:262` (the dead PDP) and by `SubscriptionPlanCard` (`subscription_plan_card.dart:18`), a widget instantiated **nowhere**. Design **#20 has no entry point** — V1 flow 8 (plan catalogue) is unreachable. |
| `/subscription-schedule` | `SubscriptionScheduleScreen` | Pushed only by `subscription_plan_screen.dart:21`; `SubscriptionPlanScreen` itself has no caller. Designs **#18/#26** are unreachable too. |
| `/productDetails` | `DetailPage` | Self-reference only. Design **#8** is not merely a stub, it is unreachable. |
| `/otp` | `OTPLoginPage` (stub) | No caller at all. Design **#10** cannot fire its `SignUp()` bug on a real user — the defect is latent, not live. |
| `/notifications` | `NotificationsScreen` | Only `app_drawer.dart:163`; `AppDrawer` is instantiated **nowhere**. Design **#27** never renders its hard-coded fixture. |
| `/signup-method-selection` | `SignupMethodSelectionScreen` | No caller — `LoginPage`'s own tabs replaced it when D-5 removed “Sign up with Email”. Design **#14** is superseded. |
| `/email-signup`, `/email-verification`, `/phone-entry-after-email` | email sign-up chain | Unreachable, consistent with D-5. Designs **#6/#15** withdrawn. |
| `/google-phone-entry` | `GooglePhoneEntryScreen` | No caller; Google sign-up collects the phone inline instead. Design **#7** lives on `GoogleSignupScreen`. |
| 11 more (`/orders`, `/myaccount`, `/subscription-plan`, `/subscription-summary`, `/subscription-family`, `/mobileNumberPage`, `/forgotPasswordPage`, `/day-wise-schedule`, `/delete-account`, `/delivery-slot-selection`, `/otpSignUpScreen`) | various | No live caller. Retirement candidates, not design targets (§6). |

**22 files / 6,908 lines** sit behind no live caller (of 37,611 lines in `lib/`). About **1,943 of those lines are subscription/plan code worth reviving** (`plan_selection_screen.dart` 736, `subscription_schedule_screen.dart` 490, `subscription_plan_screen.dart` 475, `subscription_plans_screen.dart` 242) — the code behind P0-2 and #18 exists and is orphaned, it is not missing.

> **Caveat (honest limitation):** this is static analysis. Deep links, `initialRoute`, and navigation built from runtime strings are not modelled. A 15-minute device check closes it (§13). Every claim that depends on reachability carries its `file:line` so it can be disproved in one step.

---

## 3. Headline

| Metric | Now | After V2 as scoped |
| :--- | ---: | ---: |
| Overall, all 30 designs | **50%** (1,491 / 30 = 49.7) | **73%** (2,188 / 30 = 72.9) |
| Designs with a live target screen (17) | **52%** (880 / 17 = 51.8) | **85%** (1,451 / 17 = 85.4) |
| Designs at or above the 75% bar | **0 of 30** | **19 of 30** |
| Committed effort | — | **25.0 dev-days** |
| Split | — | P0 **5.75** · P1 **18.5** · P2 **0.75** |

The 73% ceiling is not a compromise in the work; it is the eight **withdrawn** designs (#4, #6, #9, #14, #15, #22, #28, #30) sitting at their current scores. Re-opening them costs ≈8.5 days and lifts the mean to **82%** — but V1 does not offer email sign-up, so that money buys a screen nobody can reach. §7 lists every such cap with its source.

---

## 4. P0 — launch blockers (3 items, 5.75 d)

| # | Item | Evidence | Now | Target | Effort (d) |
| :--- | :--- | :--- | ---: | ---: | ---: |
| **P0-1** | **The “Subscription” tab opens Orders.** The third destination is labelled `Subscription` (`dashboard.dart:251`) but renders `OrdersTab` (`dashboard.dart:106`), and the app has **no** Orders destination anywhere in the 4-tab bar. A paying subscriber taps the one tab named after their subscription and gets a list of past orders; the real screen is only reachable from `home_tab.dart:567/573` and `profile_tab.dart:171`. This item fixes the label and the destination; the screen's 58 → 82 lift is #19 in P1. | `dashboard.dart:106`, `dashboard.dart:251` | — | — | **0.25** |
| **P0-2** | **The plan catalogue cannot be reached.** `PlanSelectionScreen` (design #20) is live code with a working Chargebee hand-off, but its two callers are a dead widget (`subscription_plan_card.dart:18`, never instantiated) and a dead screen (`detail.dart:262`). V1 flow 8 has no entry point, so the subscription business has no storefront. Fix = one CTA into `/plan-selection` from the home subscription block **and** from the catalog, plus the two compositional gaps that make the screen saleable (period toggle, BEST VALUE badge). | `main.dart:321`, `subscription_plan_card.dart:18`, `detail.dart:262`, `home_tab.dart:567` | 51 | 88 | **2.0** |
| **P0-3** | **Design tokens are not adopted — the `vibrant_zest` palette is 0% present.** `#FFB690`, `#F97316`, `#4AE176`, `#FFBC49` appear **0 times** in `lib/`; the shipped primary is `#FF8C42`; `Roboto` is referenced 64 times against Plus Jakarta Sans. This is P0 only as a **sequencing dependency**: every P1 item below is a repaint, and repainting onto the wrong palette means painting twice. | `theme/app_colors.dart`, `theme/app_text_styles.dart`; palette grep = 0 hits | — | — | **3.5** |

**Total P0: 0.25 + 2.0 + 3.5 = 5.75 d.**

Why nothing else is P0:

- **#8 PDP (20%)** — the purchase path does **not** need it: tapping a product opens the size sheet and adds to cart (`product_catalog_screen.dart:377-414`), so one-time juice can be bought today. A missing PDP is a revenue-quality problem, not a blocker; and it is unreachable anyway. **P1.**
- **#10 OTP stub** — the screen that calls `SignUp()` without verifying is behind a route nothing pushes (`main.dart:280`). Latent, not live. **P2.**
- **#27 Notifications fixture** — reachable only from an `AppDrawer` that is never instantiated. **P2.**
- **#13 cart (subtotal only)** — totals are owned by the Chargebee hosted page by design (`BMJ_LAUNCH_CHECKLIST.md`; no coupon code exists anywhere in `lib/`), so the customer still pays a correct amount. Becomes P0 the day coupons ship (§12, D3).
- **#19 missing “Modify Plan”** — the design's primary CTA, but `BMJ_V1_SCOPE.md` §3 removed plan change. Implementing it would violate the freeze. **Contract-capped, not a defect.**

---

## 5. P1 — post-launch UX (19 designs, 18.5 d)

Live screens, in-scope flows, work that changes what a customer can do or understand. Ordered by leverage, not by score.

| # | Design → shipped screen | Now | Target | Effort (d) | Why this class |
| :--- | :--- | ---: | ---: | ---: | :--- |
| 8 | `juice_detail_selection` → `DetailPage` (**unreachable**) | 20 | 90 | 3.0 | The largest single gap and the only way to sell a subscription from a product: no size chips, no One-Time vs Subscribe, no nutrition/ingredients/rating, Buy Now toasts “Feature coming soon!”. Rebuild **and** wire it from the catalog; its `/plan-selection` call is also what P0-2 replaces. |
| 21 | `unified_discovery_dashboard` → `HomeTab` | 61 | 90 | 1.5 | Best match in the set, and the only screen every session sees. Missing testimonial rail, category chips, search entry and the 2-column grid. Highest reach-per-day in the whole list. |
| 13 | `shopping_cart_savings_summary` → `CartScreen` | 51 | 85 | 1.5 | Summary is **Subtotal only** — no delivery line, no savings line, no total. Every paying customer passes here; a cart that won't state a total is the most visible money defect short of a wrong charge. Stays P1 only because Chargebee shows the truth at checkout. |
| 1 | `address_entry_onboarding` → `AddressEntryScreen` | 35 | 85 | 1.5 | First screen after OTP; collects **9 fields against the design's 4** and has no map-pin block. Field-model decision comes before styling. Highest onboarding drop-off risk of any P1 row. |
| 19 | `subscription_management_portal` → `SubscriptionManagementScreen` | 58 | 82 | 1.0 | The only subscription surface reachable at launch. Pause/Cancel/Resume and the 9 PM cutoff banner work; missing status pill and plan-card art. Target is **82, not 95** — “Modify Plan” is contractually removed. |
| 18 | `simplified_weekly_scheduler` → `SubscriptionScheduleScreen` (**unreachable**) | 56 | 85 | 1.5 | Already one of only 3 screens using `BackdropFilter`, so the family is close. Missing master-day lock, per-day chips, 6/6 counter, price footer. Needs the same entry point as P0-2 before anyone can see it. |
| 12 | `referral_rewards_program` → `ReferralScreen` | 51 | 85 | 1.0 | Live from `profile_tab.dart:151` and fully wired to the API (code, clipboard, `share_plus`). Missing WhatsApp share and points format — the cheapest growth lever in the list. |
| 17 | `sign_in_phone_otp_verification` → `PhoneOtpVerificationScreen` | 57 | 90 | 1.0 | The real OTP screen for V1 flow 2. Structure already matches; remaining work is the glass skin, `(00:45)` timer format and “Verify Continue” wording. Effort is shared with #24 (same file). |
| 7 | `google_sign_up_phone_binding` → `GoogleSignupScreen` | 44 | 85 | 1.0 | V1 flow 1. Phone binding is real; the design's “Welcome, Alex!” + country picker + single CTA are missing, and the Flutter flow adds a password step the design never had — a flow defect, not a skin defect. |
| 25 | `verify_phone_step_2` → `PhoneSignupScreen` | 46 | 80 | 1.0 | Sends the OTP then hands off; the design's step tabs (Name+Email / Phone / Password) and country list have no counterpart, so the signup feels like three apps. |
| 29 | `sign_in_with_google` → `GoogleSignupScreen` | 46 | 80 | 1.0 | Target is capped at **80** because Google's own account chooser is OS/SDK-rendered and cannot be restyled. What is ours: “Almost there!”, the Verified-by-Google chip, and the hardcoded `country: 'IN'` in the sign-in payload. |
| 16 | `sign_in_phone_entry` → `LoginPage` | 43 | 75 | 1.0 | The shipped `LoginPage` is a full email+password+Google+forgot-password composition; the design is a phone-only entry. Target 75 because D-5 leaves the Sign Up tab with two methods by decision — the gap is composition, not missing features. |
| 11 | `phone_login_entry` → `PhoneLoginScreen` | 52 | 88 | 0.75 | Title, number and “Send OTP via SMS” are real. No country selector at all (`expand_more` in the design, zero picker code) and no Terms/Privacy links — a compliance-adjacent omission for a paid product. |
| 5 | `delivery_address_selection` → `AddressSelectionScreen` | 53 | 88 | 0.75 | Everything functional is wired (default badge, add, delete-with-confirm, set-default). Missing Home/Work labels, delivery instructions, “Current Location” and an explicit Confirm CTA at the foot. Pure composition. |
| 23 | `verify_email_otp_step_1.1` → `EmailVerificationAfterPhoneScreen` | 59 | 88 | 0.5 | A near-copy of `EmailVerificationScreen`: six boxes, resend and API verify all match. Remaining: skin and timer format. Live via `phone_otp_verification_screen.dart:186`. |
| 2 | `create_password` → `CreatePasswordScreen` | 54 | 85 | 0.5 | Live in the phone-signup chain (`address_entry_screen.dart:99`). Both fields are `obscureText: true` with **no visibility toggle** — an accessibility defect, not a style preference. No strength meter. |
| 24 | `verify_phone_otp_step_2.1` → `PhoneOtpVerificationScreen` | 56 | 90 | 0.0 | Same screen as #17; only the “Step 2 of 3” indicator is unique to this design. Counted once. |
| 3 | `create_password_step_3` → `CreatePasswordScreen` | 56 | 85 | 0.0 | Same screen as #2 (the `<title>` reading “Delivery Address” is stale). Only the Step 3 indicator is unique. Counted once. |
| 26 | `weekly_subscription_scheduler` → `SubscriptionScheduleScreen` | 50 | 72 | 0.0 | Same screen as #18, and effort is counted once there. Its ceiling is lower (72 vs 85) because Quick Fill, Repeat Last and per-day “Pick Flavor” contradict the deliberate one-juice-across-all-days rule (§12, D4). |

**Total P1: 18.5 d.** Rows at 0.0 are second designs on a screen already counted (#24 → #17, #3 → #2, #26 → #18). Across the whole P1 set that is **19 designs → 15 screens**.

---

## 6. P2 — cosmetic and invisible (10 designs, 0.75 d)

Two different things share P2, and both are correctly last: work a customer would never notice improving, and work on screens a customer cannot reach. “Effort now” is what V2 should spend; “if revived” is what it would cost if the product later re-opens the surface — **not included in any total in this document**.

| # | Design → shipped screen | Now | Target | Effort now (d) | If revived (d) | Why P2 |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| 10 | `otp_verification` → `/otp` → `OTPLoginPage` stub | 54 | 90 | 0.25 | 0.5 | Unreachable (`main.dart:280`, no caller), yet it is a **latent `SignUp()` without verification**. Delete the stub and the route, or repoint `/otp` at `PhoneOtpVerificationScreen`. Fifteen minutes removes the trap. |
| 27 | `notifications` → `NotificationsScreen` (fixture) + `NotificationCentreScreen` (BLoC) | 48 | 88 | 0.5 | 1.0 | Two half-built implementations, neither reachable (`AppDrawer` is never instantiated). Decision: route the BLoC screen and delete the fixture — or delete both. No V1 flow needs it. |
| 22 | `unified_home_dashboard` → `HomeTab` | 58 | 90 | 0.0 | 0.5 | The **competing duplicate** of #21 for the same file. Pick #21 as canonical and retire this design; the only unique element worth porting is the 3-stat row (juices / bottles returned / streak). |
| 14 | `signup_method_selection` → `SignupMethodSelectionScreen` | 56 | 88 | 0.0 | 0.5 | Superseded: D-5 moved the method choice onto `LoginPage`'s own tabs, and nothing navigates to this screen any more. |
| 30 | `sign_up_gateway` → `SignUpScreen` + method picker | 49 | 85 | 0.0 | 1.0 | Email sign-up is de-advertised; both counterpart screens are unreachable. Its Sign In / Sign Up tab idea already exists on `LoginPage`. |
| 4 | `create_your_profile_step_1` → `SignUpScreen` | 38 | 80 | 0.0 | 1.5 | Withdrawn with D-5. If email sign-up returns, this becomes the step-1 screen and needs the photo picker and step indicator. |
| 6 | `email_signup_verification` → `EmailSignupScreen` → `EmailVerificationScreen` | 51 | 85 | 0.0 | 1.5 | Chain has no live caller. Two screens cover one design — a consolidation task whenever it is revived, not a styling task. |
| 15 | `sign_in_email_otp_verification` → `EmailVerificationScreen` | 59 | 88 | 0.0 | 0.5 | Highest-scoring withdrawal in the set: nearly free to finish **if** email OTP sign-in existed. It does not. |
| 28 | `sign_in_email_entry` → `LoginPage` | 42 | 75 | 0.0 | 2.0 | The design is email → OTP/magic link. V1 has no email-OTP sign-in entry point, so this is new scope, not migration. |
| 9 | `link_google_account` → `LinkGoogleAccountScreen` | 37 | 75 | 0.0 | 1.0 | Not routed and not in the ten V1 flows. Flutter also renders a different interaction (OTP + resend) than the design's one-tap “Link Accounts”. |

**Total P2: 0.75 d.** Retiring the withdrawn and duplicate designs costs 0. Re-opening all ten rows costs ≈10 d; the eight withdrawn/duplicate ones alone cost ≈8.5 d and lift the mean from **73% to 82%** — a decision for Product, not for this plan.

---

## 7. Where the target is capped by the frozen contract

A target below 90 is never laziness here. Each of these would require re-opening a decision that already has an ADR or a freeze entry.

| Cap | Designs | Source of the cap | Consequence |
| :--- | :--- | :--- | :--- |
| No plan change / no “Modify Plan” | #19 | `BMJ_V1_SCOPE.md` §3 — Chargebee Pricing Pages retired (`410 Gone`), `PUT /modify` removed | Target 82, not 95 |
| One juice across all delivery days | #26 | Product rule in `subscription_schedule_screen.dart`; modify route removed | #26 caps at 72 while #18 reaches 85 on the same screen |
| Email + password sign-up de-advertised | #4, #6, #15, #28, #30 | `BMJ_V1_SCOPE.md` §3, decision **D-5** | Withdrawn; 0 effort |
| Google's account chooser is SDK-rendered | #29 | Platform, not ours | Target 80 |
| Tax and total owned by Chargebee | #13 | `BMJ_V1_SCOPE.md` §2 flow 5; checkout hand-off | Target 85 until coupons are a product decision (§12, D3) |
| No notification or search surface in V1 | #27, #21 | Not among the ten flows; no search endpoint in `docs/API.md` | Composition only, no fake affordance |

---

## 8. How the effort numbers were built

- **Unit:** 1.0 d = one focused day (≈6 productive hours) for a Flutter developer who already knows this tree. Not calendar days, not including review latency.
- **Drivers:** (a) number of missing composition blocks from the baseline's “Remaining work” column, (b) whether state/BLoC/API wiring already exists, (c) verification cost (analyze + widget test + a device pass over the flow).
- **Bands:** `0.25–0.5` copy/label/single-widget · `0.75–1.5` composition on a wired screen · `2.0–3.0` new screen or new flow segment.
- **Assumes P0-3 has landed.** Every P1 number is a *repaint onto adopted tokens*. Done out of order, add 30–40% for the second pass.
- **Excludes:** QA regression (add 25–30% → ≈31–33 d total), design review, backend/API work, Chargebee configuration, copywriting and legal copy, and pixel-diff tooling.
- **Confidence:** ±25% on the 0.25–0.5 d rows, **±50% on the 2–3 d rows**. #8 and P0-2 are the two rows where the estimate can double if the sizing/plan model changes.

---

## 9. Sequencing (dependency-ordered)

| Wave | Scope | Designs | Days | Cumulative | Why this position |
| :--- | :--- | :--- | ---: | ---: | :--- |
| **W0 — P0** | Nav label → subscription, plan-catalogue entry, token adoption | P0-1/2/3 (#20) | 5.75 | 5.75 | Tokens block every repaint; the plan entry is the only revenue gate; the nav fix is 2 hours and removes a permanent embarrassment. |
| **W1 — Purchase funnel** | PDP rebuild + wire, cart summary, address selection | #8, #13, #5 | 5.25 | 11.0 | Highest revenue exposure. #8 and P0-2 touch the same `/plan-selection` seam, so doing them close together avoids double work. |
| **W2 — Onboarding** | Address entry (field model), password visibility, Google sign-up, phone login, `LoginPage` composition, OTP verify, email-verify-after-phone, phone sign-up, Google sign-in | #1, #2/#3, #7, #11, #16, #17/#24, #23, #25, #29 | 8.25 | 19.25 | The whole sign-up funnel becomes consistent once tokens are in — 11 designs across 8 screens — but it is the least revenue-urgent of the live work. |
| **W3 — Subscription & retention** | Scheduler, management portal, referral | #18/#26, #19, #12 | 3.5 | 22.75 | Needs the W0 entry point before #18 is even visible. Referral is the cheap growth win. |
| **W4 — Home & cleanup** | Home composition, retire/repair dead surfaces | #21/#22, #10, #27 | 2.25 | 25.0 | Home already scores best (61); retiring the two dead surfaces last keeps focus on customer-facing value. The 6,908-line orphan cleanup is a separate decision (D5). |

**25.0 d ≈ 5 weeks solo, ≈2.5–3 weeks with two developers** running W1 and W2 in parallel after W0. Including QA (25–30%), it is **≈6.5 weeks for one developer or ≈3.5 weeks for two** — which is why P0 must be able to ship on its own in week 1.

---

## 10. Coverage gap: in-scope flows with no Stitch design

Four of the ten frozen V1 flows have **no design among the 30**, so they cannot be migrated — only token-restyled, and no honest target % can be quoted for them:

| V1 flow | Screen | Design status |
| :--- | :--- | :--- |
| 3 · Catalog browse | `ProductCatalogScreen`, `MenuTab` | **No design** — the 30 folders contain no product list |
| 5 · One-time checkout | `CheckoutScreen` → Chargebee hosted page | Not designable (third-party page) |
| 6 · Order history | `OrderHistoryScreen`, `OrderDetailScreen` | **No design** |
| 9 · Profile read | `UserProfileScreen`, `ProfileTab`, `OrdersTab` | **No design** |
| — | `InvoiceViewScreen`, forgot/reset password | **No design** |

Consequence: after V2, these remain the visual weak link *by construction*. If the V2 bar is “every surface matches a design”, **four designs must be commissioned** (catalog list, order history, profile/account, orders) before the migration can be called complete — and this plan should not absorb that cost silently.

---

## 11. Risks

| # | Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| R1 | **The token foundation is built against the wrong design system.** `lush_architecture` (gold, Poppins) and `vibrant_zest` (orange, Plus Jakarta Sans) both ship in the bundle. 3.5 d of W0 and every later repaint depend on the answer. | High | High | §12 D1 before W0 starts. One ADR, one paragraph. |
| R2 | **A dead screen is actually reachable** through a deep link or runtime-built route, so a P2 is really a P0. | Medium | Medium | §13 device check, 15 minutes, before publishing the plan. |
| R3 | **The PDP rebuild breaks the working purchase path.** Today a product tap → size sheet → `AddToCart` works (`product_catalog_screen.dart:377-414`). | Medium | High | Add the PDP as a *second* entry; never remove the size sheet in the same release. Widget-test both add-to-cart paths. |
| R4 | **Deleting orphaned screens breaks tests or imports.** 22 files / 6,908 lines; 1,943 of them are subscription code that must be kept. | Medium | Medium | Grep imports first; one file per commit; exclude the four revivable subscription files. |
| R5 | **The target %s are read as measured.** They are estimates from the same composite rubric, with no pixel diff. | High | Medium | Already stated in §3 and §8; repeat it in any stakeholder deck. |
| R6 | **Coupons ship in the launch offer**, making #13 a P0 with a backend dependency. | Low | High | §12 D3; if yes, re-class #13 and add the backend estimate. |
| R7 | **P1 work starts before P0-3**, forcing a second repaint. | Medium | Medium | Treat W0 as a gate, not a suggestion: +30–40% otherwise. |
| R8 | **“V2 complete” is claimed while four in-scope flows still have no design** (§10). | High | Medium | Define done as “the 17 live-target designs”, not “the app”. |

---

## 12. Decisions that block this plan

| ID | Decision | Blocks | Cost of not deciding |
| :--- | :--- | :--- | :--- |
| **D1** | Which design system is canonical: `lush_architecture` (gold / Poppins) or `vibrant_zest` (orange / Plus Jakarta Sans)? | P0-3, and therefore **all** of W1–W4 | The single largest risk in the plan (R1) |
| **D2** | Where does subscription purchase start — home card, catalog, profile, or all three? | P0-2 | V1 flow 8 stays unreachable; no subscription revenue |
| **D3** | Do coupons / delivery fees ship in V1? Who owns the total in the cart? | #13 target (85 vs 90), P0 re-classification | A cart that shows a subtotal only |
| **D4** | Is “one juice across all delivery days” permanent? | #26 target (72 vs 85) | 1.5 d spent on a scheduler the product then changes |
| **D5** | Retire or revive the 22 orphaned screens (6.9 k lines)? | W4 cleanup, P2 rows | Dead code keeps being read, tested and mis-scored |
| **D6** | Notifications: route the BLoC-backed `NotificationCentreScreen`, or delete both? | #27 | Two half-features keep drifting apart |

---

## 13. How to verify this document

```powershell
# 1. Reachability (rebuilds §2 and rule R1) — no code changes, read-only
python C:\Users\Public\bmj_nav_graph.py      # live classes + routes with no live caller
python C:\Users\Public\bmj_route_refs.py     # every route literal and who references it
python C:\Users\Public\bmj_dead_loc.py       # orphaned lines / lib total

# 2. Table integrity + totals for this file
python C:\Users\Public\md_v2_check.py
```

**Device check (closes R2, ~15 minutes):** launch the app, confirm that the third tab is labelled “Subscription” and opens order history; tap a product and confirm the size sheet adds to cart; try to reach a plan screen from home, catalog and profile; confirm nothing opens `DetailPage` or the notifications fixture.

---

## 14. Verdict

1. **The UI does not gate launch.** All 14 blockers are backend, data or process; the only P0 a customer can point at is a tab labelled “Subscription” that opens Orders — a 2-hour fix.
2. **The real launch-shaped defect is a missing entrance, not a missing screen.** `PlanSelectionScreen` is 736 lines of working code that nothing can navigate to, so the subscription business has no storefront while its own storefront is sitting in the tree.
3. **V2 is a 25-day, five-wave programme** (≈6 weeks with QA): 5.75 d of P0, 18.5 d of P1 across 15 screens, 0.75 d of cleanup. It takes the live surface from **52% to 85%** and the full 30-design set from **50% to 73%**.
4. **The 73% is a contract ceiling, not an effort ceiling.** The remaining gap is eight withdrawn designs (#4, #6, #9, #14, #15, #22, #28, #30) that V1 deliberately does not offer; re-opening them costs ≈8.5 d and buys screens no customer can reach.
5. **Two things must be decided before any code is written:** the canonical design system (D1) and where subscription purchase begins (D2). Everything else in this plan is already unblocked.

*Analysis only — no application code, route table, token file, test or asset was modified.*

