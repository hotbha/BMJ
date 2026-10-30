# STITCH_ALIGNMENT_REPORT.md — BMJ V1 ↔ Stitch canonical UX

**Prepared:** 16 October 2026
**Subject:** Map every `Stitch/` design onto the existing Flutter codebase, so the V1 UX reference is
canonical **without** a new project, **without** rewriting Flutter, and **without** porting Stitch blindly.
**Inputs:** `Stitch/**` (31 `code.html` + 31 `screen.png` + 3 `DESIGN.md`), `lush/lib/**`,
`docs/BMJ_V1_SCOPE.md`, `PRODUCT_ALIGNMENT_REPORT.md`.
**Status:** ⚠️ **analysis only.** No Flutter screen was created, edited, archived or deleted in this pass.

---

## 0. Method & evidence

| # | Question | Command (from `x:\BMJ`) | Result |
| :--- | :--- | :--- | :--- |
| 1 | Is `Stitch/` actually in the repository? | `git ls-files Stitch` | **0 files** — untracked, `git status` shows `?? Stitch/` |
| 2 | Would the mockups even be committed? | `git check-ignore -v Stitch/**/screen.png` | ⛔ **`.gitignore:10:*.png`** — all 31 mockups were ignored |
| 3 | How many designs? | `Get-ChildItem -Recurse -Directory Stitch` | 31 design folders + 3 `DESIGN.md` |
| 4 | Which Flutter screen does each map to? | `PRODUCT_ALIGNMENT_REPORT.md` §B.1 | 31-row mapping, spot-re-verified below |
| 5 | Does the design-matching screen exist? | `Get-ChildItem -Recurse lib -Filter <name>.dart` | 14 screens exist with **0 external references** |

**Two export batches** (both must stay — they are not duplicates overall):

- `Stitch/stitch_bookmyjuice_flutter_bloc_ui/` — **26** designs + `vibrant_zest_architecture/DESIGN.md`
- `Stitch/stitch_bookmyjuice_flutter_bloc_ui (1)/` — **5** designs (`notifications`, `sign_in_email_entry`,
  `sign_in_email_otp_verification`, `sign_in_with_google`, `sign_up_gateway`) + a **byte-identical copy** of
  `vibrant_zest_architecture/DESIGN.md` + `lush_architecture/DESIGN.md`

> ⛔ **Freeze blocker found in step 2.** `git add Stitch/` would have committed the 31 HTML files and 3
> `DESIGN.md` files but **silently dropped all 31 `screen.png` mockups** (root `.gitignore:10` is a blanket
> `*.png`). The reference would have shipped incomplete and nobody would have noticed. **Fixed in this pass** —
> see §7.

## 1. Status legend (as specified)

| Code | Meaning |
| :--- | :--- |
| **A** | Already implemented |
| **B** | Partially implemented |
| **C** | Missing and required for V1 |
| **D** | Missing and defer to V2 |
| **E** | Replace existing Flutter screen |

## 2. Stitch screen → Flutter screen (all 31 designs)

| # | Stitch screen | Existing Flutter equivalent | Status | V1? | Recommended action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `address_entry_onboarding` | `AddressEntryScreen` (`/address-entry`) | **A** | Y | Keep. No port. |
| 2 | `create_password` | `CreatePasswordScreen` (`/create-password`) | **A** | Y | Keep. No port. |
| 3 | `create_password_step_3` (title "*Delivery Address*") | `AddressEntryScreen` | **A** | Y | Keep. Design is a **duplicate of #1/#5 with a misleading folder name** — fix the Stitch name, not the code. |
| 4 | `create_your_profile_step_1` | `SignUpScreen` (implemented, **not routeable**) | **B** | N | Keep as-is. V1 signup is Google + OTP (`D-5`); route decisions are post-launch (`I6`). |
| 5 | `delivery_address_selection` | `AddressSelectionScreen` (`/address-selection`) | **A** | Y | Keep. No port. |
| 6 | `email_signup_verification` | `EmailSignupScreen` (`/email-signup`) | **B** | N | Keep as-is. Email signup is de-advertised for V1 (`D-5`); screen stays in the tree. |
| 7 | `google_sign_up_phone_binding` | `GoogleSignupScreen` + `GooglePhoneEntryScreen` | **A** | Y | Keep — one design legitimately spans two screens. No port. |
| 8 | `juice_detail_selection` | `DetailPage` (`/productDetails`) | **A** | Y | Keep. No port. |
| 9 | `link_google_account` | `LinkGoogleAccountScreen` (implemented, **not routeable**) | **B** | N | Keep as-is. Post-launch (`I6`). |
| 10 | `otp_verification` | `OTPLoginPage` (`/otp`) | **A** | Y | Keep. No port. |
| 11 | `phone_login_entry` | `PhoneLoginScreen` (`/phone-login`) | **A** | Y | Keep. Overlaps #16 — deduplicate the **design**, not the code. |
| 12 | `referral_rewards_program` | `ReferralScreen` (`/referral`) | **A** | Y | Keep. No port. |
| 13 | `shopping_cart_savings_summary` | `CartScreen` (`/cart`) | **A** | Y | Keep. No port. |
| 14 | `signup_method_selection` | `SignupMethodSelectionScreen` (`/signup-method-selection`) | **B** | Y | Keep. The design offers more signup paths than V1 advertises (`D-5`: Phone-OTP + Google only) — the design is ahead of the released scope, the code is correct. |
| 15 | `sign_in_email_otp_verification` | `EmailVerificationScreen` (`/email-verification`) | **A** | N | Keep. Duplicate of #29 (cross-batch). |
| 16 | `sign_in_phone_entry` | `LoginPage` (`/login`) | **A** | Y | Keep. Overlaps #11 — a design-governance issue, not a code one. |
| 17 | `sign_in_phone_otp_verification` | `PhoneOtpVerificationScreen` (`/phone-otp-verification`) | **A** | Y | Keep. Duplicate of #24/#25. |
| 18 | `simplified_weekly_scheduler` | `SubscriptionScheduleScreen` (`/subscription-schedule`) | **A** | N | Keep the screen. **Not V1** — `BMJ_V1_SCOPE.md` §3 removed schedule modification. ⚠️ 0 live entry points (§5). |
| 19 | `subscription_management_portal` | `SubscriptionManagementScreen` (`/manage-subscriptions`) | **B** ⭐ | Y | **This is B6.** Pause / Resume / Cancel **are** implemented, wired and reachable; the Stitch **primary** CTA — **Modify Plan** — is not (no production plan-change endpoint; §3 scope). Keep + no code change. See `B6_DECISION_REPORT.md`. |
| 20 | `subscription_plan_comparison` | `PlanSelectionScreen` (`/plan-selection`) + `SubscriptionPlanScreen` (`/subscription-plan`) | **A** | Y | Keep. One design → two screens; the **reachable** one is `PlanSelectionScreen` (§5). |
| 21 | `unified_discovery_dashboard` | `Dashboard` / `HomeTab` | **A** | Y | Keep — this is the shipped home shell. |
| 22 | `unified_home_dashboard` | `Dashboard` / `HomeTab` (same `<title>` as #21) | **E** | N | **Deferred.** Two competing Stitch homes, one shipped implementation. Pick a winner in V2 (`G-15`); replacing the live home shell is a redesign, outside a launch freeze. |
| 23 | `verify_email_otp_step_1.1` | `EmailVerificationScreen`, `EmailVerificationAfterPhoneScreen` | **B** | N | Keep. Third design for one flow — design-governance issue. |
| 24 | `verify_phone_otp_step_2.1` | `PhoneOtpVerificationScreen` | **A** | Y | Keep. Duplicate of #17. |
| 25 | `verify_phone_step_2` | `PhoneOtpVerificationScreen` | **A** | Y | Keep. Duplicate of #17. |
| 26 | `weekly_subscription_scheduler` | `SubscriptionScheduleScreen` | **A** | N | Keep. Duplicate of #18. |
| 27 | `notifications` | `NotificationCentreScreen` — **exists, 0 references**; `/notifications` ships a *different* file (`notifications.dart`) | **B** | N | **KEEP_AND_RECONNECT post-launch.** This is the Stitch-canonical notification centre and it is dead. Not a V1 flow → no V1 work. (`G-18`) |
| 28 | `sign_in_email_entry` | `LoginPage` (`/login`) | **A** | Y | Keep. No port. |
| 29 | `sign_in_email_otp_verification` | `EmailVerificationScreen` | **A** | N | Keep. Exact duplicate of #15. |
| 30 | `sign_in_with_google` | `GoogleSignupScreen` (`/google-signup`) | **A** | Y | Keep. No port. |
| 31 | `sign_up_gateway` | `AuthWrapper` + `SignupMethodSelectionScreen` | **B** | Y | Keep. Ambiguous 1→2 mapping; the shipped pair covers the design. |

### 2.1 Totals

| Status | Count | Meaning for V1 |
| :--- | ---: | :--- |
| **A — already implemented** | **21** | Nothing to do. **This is the headline result.** |
| **B — partially implemented** | **9** | 6 are design-vs-scope drift (`D-5`, route gaps), not missing UI. 2 real gaps: the Stitch portal's *Modify Plan* (#19) and the dead notification centre (#27). |
| **C — missing and required for V1** | **0** | ⭐ **Stitch contains no screen that V1 requires and Flutter lacks.** |
| **D — missing, defer to V2** | **0 screens** | 3 *capabilities* defer instead — see §4. |
| **E — replace existing screen** | **1** | #22 (competing home design) — deferred, not executed. |

> ⭐ **The single most important conclusion of this report:** Stitch is a **style and layout reference**,
> not a functional gap list. Every one of the 31 designs already has a shipped Flutter counterpart, and the
> flows that *are* missing from Stitch (order history, order detail, invoices, delivery slots, profile,
> delete-account) are the ones Flutter already implements. **Therefore a blind port would replace working
> code with mockups and add nothing to V1.**

---

## 3. The three `DESIGN.md` token sets (and which one is real)

| Design tokens | Primary | Fonts | Implemented in `lush`? |
| :--- | :--- | :--- | :--- |
| `Stitch/.../vibrant_zest_architecture/DESIGN.md` | `#FFB690` / brand Orange 500 `#F97316` | Plus Jakarta Sans + Inter | ❌ No |
| `Stitch/.../vibrant_zest_architecture/DESIGN.md` **(batch-2 copy)** | identical, byte-for-byte (8,046 B) | — | ❌ No |
| `Stitch/.../lush_architecture/DESIGN.md` | `#FFBC49` "Golden Nectar" | Poppins + Inter | ❌ No |
| *(shipped app — for contrast)* | `#FF8C42` (`lib/theme/app_colors.dart`, matches `docs/DESIGN_SYSTEM.md`) | Google Sans | ✅ **This is what ships** |

**Verdict:** three palettes, **zero** of the Stitch ones implemented; the `vibrant_zest` copy is byte-identical.
**Do not** repaint the app during a freeze — a palette swap touches every screen and cannot be verified by the
existing test battery. Keep `docs/DESIGN_SYSTEM.md` as the V1 token source of record, then adopt one Stitch
architecture as a **V2** visual refresh (`G-17`), deleting the duplicated copy at that time.

## 4. Capabilities with no Stitch design, and what defers to V2

**Inverse finding.** Five V1 flows have **no** Stitch design at all — and all five are already implemented:

| V1 flow (`BMJ_V1_SCOPE.md` §2) | Stitch design | Shipped implementation |
| :--- | :--- | :--- |
| 6 — Order history | ❌ none | `OrderHistoryPage` `/orders`, `OrderHistoryScreen` `/order-history` |
| — Order detail | ❌ none | `OrderDetailScreen` `/order-detail` |
| — Invoices | ❌ none | `InvoiceViewScreen` `/invoices` |
| — Delivery slot selection | ❌ none | `DeliverySlotSelectionScreen` `/delivery-slot-selection` |
| 9 / 10 — Profile read, address book | ❌ none | `UserProfileScreen`, `AddressSelectionScreen`, `AddressEntryScreen` |

**Deferred to V2 (capability-level — no Stitch *screen* is missing):**

| # | Capability | Why it is V2 | Evidence |
| :--- | :--- | :--- | :--- |
| D-1 | **Modify Plan** — the Stitch portal's primary CTA (#19) | No production plan-change endpoint exists. `BMJ_V1_SCOPE.md` §3 retires plan change with the Pricing Pages; the only `modify` route was never implemented server-side and its client caller was deleted (`C-5`). | `SubscriptionController` has no `modify` mapping; `SubscriptionManagementScreen` renders only Pause/Resume/Cancel |
| D-2 | **Subscription purchase wizard** — `family → plan → schedule → summary` | Unreachable V1 dead-end; the reachable purchase path is `DetailPage → /plan-selection` (`detail.dart:262`) | §5 |
| D-3 | **Bottle tracking UI** | Explicitly out of V1: *"Backend ready, no V1 screen"* | `BMJ_V1_SCOPE.md` §3; `my_bottles_widget.dart` (0 refs) |

---

## 5. Reachability audit — the "reconnect subscription flows" question

Every push into the subscription/plan surface, verified this pass:

| Route | Pushed by | Live? |
| :--- | :--- | :--- |
| `/manage-subscriptions` | `profile_tab.dart:171` (**live tab**), `home_tab.dart:567,573` (**live tab**), `menu.dart:242` (dead), `app_drawer.dart:133,138` (dead), `welcome_header.dart:22` (dead widget) | ✅ **YES — 2 live entry points** |
| `/plan-selection` | `detail.dart:262` (**live `DetailPage`**), `subscription_plan_card.dart:18` (dead) | ✅ **YES** |
| `/subscription-family` | `app_drawer.dart:143` (dead), `active_subscription_screen.dart:357` (dead screen) | ❌ **NO live entry point** |
| `/subscription-plan` | *(nothing pushes it anywhere)* | ❌ **NO** |
| `/subscription-schedule` | `subscription_plan_screen.dart:21` (itself unreachable) | ❌ **NO** (inherited) |
| `/subscription-summary` | `subscription_plans_screen.dart:56` (dead screen) | ❌ **NO live entry point** |
| pause / cancel / resume / active-subscription screens | no route, no push, 0 refs | ❌ **NO** |

**Answer to "reconnect subscription management flows":** the two flows V1 actually ships — §2 flow 7
(list / pause / resume / cancel) and flow 8 (plan catalogue) — are **already connected end-to-end**. What
remains disconnected is the *purchase wizard* chain and the four standalone pause/cancel/resume screens, and
V1 needs neither. **No reconnection code is required for V1.** Full verdict: `B6_DECISION_REPORT.md`.

## 6. Verdict

| Question | Answer |
| :--- | :--- |
| Does aligning V1 with Stitch require a new project? | **No.** 21 of 31 designs are already implemented. |
| Does it require rewriting Flutter? | **No.** 0 screens are missing-and-required; the 1 replacement candidate is deferred. |
| Should Stitch be ported? | **No — not blindly.** 12+ designs duplicate each other (2× home, 3× phone-OTP, 3× email verification, 2× schedule, 3× address entry), and 5 V1 flows have no design at all. |
| Is Stitch still the canonical UX reference? | **Yes — as style canon, not scope canon.** The subscription-management portal is the design that answered B6 (#19). |
| Any V1 code change needed from this report? | **None.** |

---

## 7. Actions required (all outside Flutter)

| # | Action | Why | Command / status |
| :--- | :--- | :--- | :--- |
| 1 | ✅ **Done this pass** — `!Stitch/**/*.png` added to root `.gitignore` (final rule, line 344) | Without it all 31 mockups stay ignored and the canonical reference ships incomplete | `git check-ignore -v Stitch/**/screen.png` → prints the **negation**, i.e. *not* ignored; `git add -n Stitch` → **65 files** (was 34) |
| 2 | **Stage `Stitch/` into the freeze commit** (repo owner, task **B1**) | `git ls-files Stitch` is still **0** — the folder exists only in the working tree | `git add Stitch` → 65 files (31 html + 31 png + 3 md) |
| 3 | Fix misleading Stitch folder names (`create_password_step_3` actually holds *Delivery Address*) — **design repo only**, never rename Flutter files to match | Stops the next reader from "porting" a duplicate | — |
| 4 | Decide the fate of the duplicated `vibrant_zest_architecture/DESIGN.md` and the competing `unified_home_dashboard` (#22) | 3 palettes, 2 homes — governance (`G-15` / `G-17`) | — |

---

*Analysis only: this report creates no screen, edits no Flutter code and deletes nothing. The single
repository change it drove is the `.gitignore` negation in **row 1 of §7** — without it, "Stitch is the
canonical UX reference" would be false in the committed tree.*
