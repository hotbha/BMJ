# B6_DECISION_REPORT.md — Subscriber pause/cancel, and the 14 dead screens

**Prepared:** 16 October 2026
**Question:** `BMJ_LAUNCH_CHECKLIST.md` blocker **B6** — *"A paying subscriber cannot pause or cancel from
the app (`G-2`, P0). The API routes work …, but no screen entry point was ever wired, so
`SubscriptionManagementScreen`'s pause/resume/cancel actions are unreachable."*
**Outcome:** ✅ **B6 is closed under option (a) — the wiring already exists in the frozen tree and is
reachable.** No code change is required. Full evidence chain in §2.
**Stitch reference used:** `Stitch/…/subscription_management_portal/code.html` (the canonical V1 portal).
**Scope discipline:** the **14 unreferenced screens were not touched** — not archived, not deleted, not edited.
They are classified in §5 so the decision can be taken separately.

---

## 1. What B6 was actually asking

B6 offers two acceptable answers: **(a)** wire the existing screens to the fixed endpoints, or **(b)** publish
a support process ("contact us to pause/cancel") and fix it next iteration. The checklist rates (a) at 4–6 h
and (b) at 30 min, and requires Product sign-off for (b).

This report shows that **(a) was already delivered by the launch freeze** and that B6's evidence line is stale
by exactly one freeze — the plumbing fix *did* make the built-in UI work, because the UI was never missing.

## 2. Verdict: B6 = CLOSED (option (a) already implemented)

An unbroken chain, every link verified in the frozen tree this pass:

| # | Link | Evidence (file:line) |
| :--- | :--- | :--- |
| 1 | **The post-login shell is `Dashboard`** | `main.dart:418-474` — `AuthWrapper` returns `Dashboard()` on the authenticated branch |
| 2 | **`Dashboard` builds all four tabs** — `IndexedStack` constructs every child, not just the visible one | `dashboard.dart:97-112` — `children: [HomeTab(…), MenuTab(), OrdersTab(…), ProfileTab(…)]` |
| 3 | **Two live entry points push the route** | `home_tab.dart:564-573` — "Pause" *and* "Modify" buttons → `pushNamed(context, '/manage-subscriptions')`; `profile_tab.dart:165-172` — "Manage Subscriptions" row → same route |
| 4 | **The route resolves** | `main.dart:293-294` — `'/manage-subscriptions': (_) => const SubscriptionManagementScreen()` |
| 5 | **The screen has the actions** | `subscription_management_screen.dart:415-419` Pause (`status == 'ACTIVE'`), `:433-439` Resume (`status == 'PAUSED'`), `:421-426` **and** `:441-446` Cancel; each guarded by the **9 PM IST cutoff** (`:53-74`, `:396-407`) and a confirmation dialog |
| 6 | **The client calls the real contract** | `subscription_service.dart:124-128` `PUT /api/subscriptions/{id}/pause`; `:146-149` `PUT …/resume`; `:170-174` `PUT …/cancel`; `:54-57` `GET /api/subscriptions/my` |
| 7 | **The server implements all four** | `SubscriptionController` — `:66-67` `GET /my` + `@PreAuthorize(hasRole('USER'\|'MODERATOR'\|'ADMIN'))`; `:157` `PUT /{id}/pause`; `:188` `PUT /{id}/resume`; `:258-262` `PUT /{id}/cancel` → delegates to the same logic as `DELETE /{id}` (`:220`) |
| 8 | **The `PUT /cancel` route is the freeze's own fix** | `docs/BMJ_V1_SCOPE.md` §5 row E — *"404 removed. Same Chargebee cancel, same 9 PM IST cutoff, same 202 Accepted."* |
| 9 | **No payload mismatch** | `SubscriptionController:285-302` `mapSubscriptionToResponse` emits `id`, `planId`, `status`, `nextBillingAt` — the exact four keys the screen reads (`:320-322`, `:393-395`) |
| 10 | **V1 scope names this as a shipped flow** | `docs/BMJ_V1_SCOPE.md` §2 **flow 7**: *"Subscription list / pause / resume / cancel — Entry point: `SubscriptionManagementScreen`, `SubscriptionBloc` — `GET /api/subscriptions/my`, `PUT /{id}/pause`, `PUT /{id}/resume`, `PUT /{id}/cancel`"* |

**Conclusion:** B6 option **(a)** is satisfied. A subscriber reaches *Profile → Manage Subscriptions* (or the
home card's *Pause* button) and can pause, resume and cancel against working endpoints. **No new screen, no
re-wiring and no support-process fallback is needed for V1.**

> 📌 **The stale line that kept B6 open.** `PRODUCT_ALIGNMENT_REPORT.md` §J.3 records `G-2` as
> *"Still open — the freeze was plumbing only; no UI was wired up."* That was true **before** the freeze's
> plumbing landed: `G-2` was raised against `Cancel/Pause/ResumeSubscriptionScreen` (the standalone screens,
> §5 rows 2–4), which are indeed unreachable. But `G-2` was never re-checked against
> **`SubscriptionManagementScreen`**, which was *already reachable* and calls the same endpoints directly.
> B6 inherited the stale status. Both status lines are corrected in this pass (§6).

---

## 3. Stitch's portal vs. the shipped screen — the one real gap

`Stitch/…/subscription_management_portal/code.html` was read in full as the canonical reference. Its anatomy:

- Page title **"Manage Subscriptions"** + subtitle (L155-158)
- **9 PM IST Cutoff** warning panel — *"Changes made after 9 PM will apply to the day after tomorrow's delivery."* (L159-166)
- Status card: live dot + **"Active"** + `Plan ID: #BMJ-7892`, plan name, description, and a 2-column grid — **Next Delivery** "Tomorrow, 7 AM" / **Billing** "₹4,500 / week" (L167-190)
- **Actions (L191-205): `Modify Plan` (full-width, primary, orange glow) · `Pause` · `Cancel`**

| Stitch element | Shipped `SubscriptionManagementScreen` | Verdict |
| :--- | :--- | :--- |
| 9 PM IST cutoff notice | `_isBefore9PMIST()` (`:53-62`) + blocking dialog (`:67-74`) + inline "Actions available after 9 AM tomorrow" (`:396-407`) | ✅ parity (behaviour + dialog rather than a static banner) |
| Status badge / plan id / billing date | status badge (`:320`), `ID: …` (`:392`), `Next Billing: …` (`:393-395`) | ✅ parity (mockup says "Next Delivery", app says "Next Billing") |
| Pause | `:413-419` → `PUT …/pause` | ✅ |
| Cancel | `:421-426` / `:441-446` (red) → `PUT …/cancel` | ✅ |
| **Resume** — absent from the static mockup | `:433-439`, rendered when `status == 'PAUSED'` → `PUT …/resume` | ✅ **app is ahead of the mockup** |
| **Modify Plan** — the mockup's only primary CTA | **absent** | ❌ **the single divergence** |

**Why *Modify Plan* stays out of V1 (→ V2), on the evidence:**

1. **No production endpoint exists.** `SubscriptionController` exposes only `GET /pricing/plans` for plans; there is no `modify`/plan-change mapping.
2. **It is already-scoped-out.** `BMJ_V1_SCOPE.md` §3 retires plan change with the Pricing Pages (`410 Gone`) and records that schedule modification *"is out of V1 scope and has no server implementation"* (`C-5` — the client caller was deleted).
3. **It is a write against a live subscription.** A Chargebee plan change plus a new production contract is outside a launch freeze's risk envelope.

**V2 remediation (no new screen required):** add one authenticated endpoint (e.g. `PUT /api/subscriptions/{id}/plan`) delegating to Chargebee's change-plan API, then add the button to the **existing** live screen next to Pause/Cancel.

## 4. Verified vs. still unverified (honest limits of this report)

| Item | Status |
| :--- | :--- |
| Reachability, route, actions, client calls, server routes, payload keys | ✅ **Verified statically** (§2, 10 links) |
| `nextBillingAt` unit | ✅ **Resolved** — `SubscriptionEntity.nextBillingAt` is `int` (epoch **seconds**, Chargebee-native), so the screen's `(… as int) * 1000` (`:395`) is correct |
| **Live end-to-end with a real paying subscriber** | ❌ **NOT verified — and not verifiable here.** Exercising it means real Chargebee calls on a real subscription, which the project guardrail reserves for explicit approval. This is precisely the **B5** device smoke item *"subscription visible in `/manage-subscriptions`"*. **Fold B6's closure into B5.** |
| Non-`ACTIVE`/`PAUSED` statuses | ⚠️ The screen renders actions **only** for `ACTIVE` (Pause/Cancel) or `PAUSED` (Resume/Cancel). Any other state — `in_trial`, `non_renewing`, `cancelled`, `future` — shows **no buttons**. Confirm during B5 that the test subscription normalises to `active`/`paused` (the screen uppercases the value at `:320`). |
| The BLoC path | ⚠️ `SubscriptionBloc` *also* implements pause/resume/cancel (`subscription_bloc.dart:654`, `:679`, `:699`) but **no live screen consumes it** — the reachable screen calls `SubscriptionService` directly. A second, parallel implementation; not required for V1, and not a blocker. |

---

## 5. The 14 unreferenced screens — classification (no action taken)

All 14 were re-verified this pass: **0 external references** each (case-insensitive, across `lib`,
`test` and `integration_test`). They are **untouched** — not archived, not deleted, not edited.

Legend: **KEEP_AND_RECONNECT** = keep, wire it up later · **REDESIGN** = keep the intent, rebuild ·
**ARCHIVE** = keep in history for reference, remove from the live tree · **DELETE** = remove outright
(history retains it).

| # | File (size) | What it is (evidence) | Live equivalent | Class | V1? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `views/screens/subscription/active_subscription_screen.dart` (12.8 KB) | `ActiveSubscriptionScreen`, `SubscriptionBloc`-driven; pushes `/subscription-family` (`:357` — itself unreachable) | `SubscriptionManagementScreen` (`/manage-subscriptions`, live) | **ARCHIVE** | N |
| 2 | `views/screens/subscription/cancel_subscription_screen.dart` (8.3 KB) | `CancelSubscriptionScreen` + `SubscriptionBloc` + the live `SubscriptionService` | `SubscriptionManagementScreen` → Cancel (`:421-426`) | **ARCHIVE** | N |
| 3 | `views/screens/subscription/pause_subscription_screen.dart` (5.0 KB) | `PauseSubscriptionScreen` + `SubscriptionBloc` | `SubscriptionManagementScreen` → Pause (`:413-419`) | **ARCHIVE** | N |
| 4 | `views/screens/subscription/resume_subscription_screen.dart` (4.5 KB) | `ResumeSubscriptionScreen` + `SubscriptionBloc` | `SubscriptionManagementScreen` → Resume (`:433-439`) | **ARCHIVE** | N |
| 5 | `views/screens/subscription/subscription_plans_screen.dart` (11.2 KB) | `SubscriptionPlansScreen` + `SubscriptionBloc`; pushes `/subscription-summary` (`:56`, unreachable) | `PlanSelectionScreen` (`/plan-selection`, live from `DetailPage`) | **ARCHIVE** | N |
| 6 | `views/screens/notification_centre_screen.dart` (9.2 KB) | `NotificationCentreScreen`, the **Stitch-canonical** notification centre (`Stitch/…/notifications`) + `NotificationBloc` | **none** — `/notifications` ships `notifications.dart` (no bloc, no design match) | **KEEP_AND_RECONNECT** | N (V2) |
| 7 | `views/screens/profile/address_screen.dart` (7.4 KB) | `AddressScreen` → `UserRepository` + `serviceability_checker`; contains a `TODO` for an unwired `UserBloc` | `AddressSelectionScreen` / `AddressEntryScreen` (both live) | **ARCHIVE** | N |
| 8 | `views/screens/orders/order_catalog_screen.dart` (8.8 KB) | `OrderCatalogScreen` → `ItemService`; declares `_JuiceItemCard` (`:154`) | `ProductCatalogScreen` (`/catalog`, live) | **ARCHIVE** | N |
| 9 | `views/screens/orders/order_checkout_screen.dart` (13.2 KB) | `OrderCheckoutScreen` → `CartBloc` + `UserRepository`; pushes `/dashboard` (`:71`) | `CartScreen` → `CheckoutScreen` (live hosted-page WebView) | **ARCHIVE** | N |
| 10 | `views/screens/orders/order_item_screen.dart` (9.5 KB) | `OrderItemScreen` → `CartBloc` + `ItemService` | `DetailPage` + `CartScreen` | **ARCHIVE** | N |
| 11 | `views/widgets/my_bottles_widget.dart` (12.0 KB) | `MyBottlesScreen` → `UserBloc` (`user_bloc`/`user_events`/`user_state`) | **none** — bottle tracking has a complete API and **no** live UI | **KEEP_AND_RECONNECT** | N (V2) |
| 12 | `widgets/subscription_card.dart` (4.0 KB) | `SubscriptionCard` — **name collides** with the `SubscriptionCard` in `widgets/dashboard_components.dart`; the two mutually import each other (`PRODUCT_ALIGNMENT_REPORT` §D.3) | the live `SubscriptionCard` in `dashboard_components.dart` | **DELETE** | N |
| 13 | `views/widgets/subscription_plan_card.dart` (6.6 KB) | `SubscriptionPlanCard`; pushes `/plan-selection` (`:18`) | `PlanSelectionScreen`'s own inline plan cards | **ARCHIVE** | N |
| 14 | `views/widgets/shimmer_subscription_card.dart` (3.5 KB) | `ShimmerSubscriptionCard` | `ShimmerProductCard` / `ShimmerCartItem` (both live) | **ARCHIVE** | N |

### 5.1 Tally and what it means

| Class | Count | Screens |
| :--- | ---: | :--- |
| **ARCHIVE** | **10** | 1-5, 7-10, 13, 14 |
| **KEEP_AND_RECONNECT** | **2** | 6 (`notification_centre_screen`, Stitch-canonical), 11 (`my_bottles_widget`, V2 backend ready) |
| **DELETE** | **1** | 12 (`subscription_card.dart` — duplicate class name, mutual import) |
| **REDESIGN** | **0** | — nothing here needs a rebuild; the four subscription screens are *superseded*, not broken |
| **Required for V1** | **0** | ⭐ **B6 needs none of the 14.** |

**The structural reason:** screens 1-5 are the **`SubscriptionBloc`-driven twin** of the live flow. There are
two complete implementations of subscriber self-service — the reachable one (`SubscriptionManagementScreen` →
`SubscriptionService` → REST) and the unreachable one (`Active`/`Pause`/`Cancel`/`Resume` screens →
`SubscriptionBloc` → the same service). Wiring the second one up would not close B6; it would create a
**second pause/cancel path with its own UX, its own tests and its own failure modes** — a regression risk,
not a fix.

> ⚠️ **Correction for two scope-document references.** `BMJ_V1_SCOPE.md` §2 names dead files as entry points
> for two flows: flow 8 lists `subscription_plans_screen.dart` (row 5 above) and flow 10 lists `AddressScreen`
> (row 7). Both flows are nonetheless **reachable** via `PlanSelectionScreen` and
> `AddressSelectionScreen`/`AddressEntryScreen`. The freeze document was **not** rewritten (a doc edit for an
> already-true flow is out of scope for this pass); this note records the discrepancy.

---

## 6. Decisions, actions, and the two status lines corrected

| # | Decision / action | Owner | Est. |
| :--- | :--- | :--- | :--- |
| 1 | **Record B6 as CLOSED under option (a)** — no support-process fallback is needed, no UI work is needed | Product | 0 |
| 2 | **Fold B6's proof into the B5 device smoke** — one step of the existing ticket: after paying, open Profile → Manage Subscriptions and pause, resume, then cancel a test subscription | QA | +15 min on B5 |
| 3 | **Watch the status normalisation** during that smoke (§4) — actions only render for `ACTIVE`/`PAUSED` | QA | — |
| 4 | **Schedule *Modify Plan*** as a V2 feature: one endpoint + one button on the existing screen (§3) | Product + Backend | V2 backlog |
| 5 | **Take the §5 decisions separately** (10 × ARCHIVE, 1 × DELETE, 2 × KEEP_AND_RECONNECT). Nothing is executable until approved — **no screen was moved or deleted in this pass** | Product + Flutter | post-launch |
| 6 | **Do not reconnect screens 1-5.** Reconnecting would fork the pause/cancel flow (§5.1) | Flutter | — |

### 6.1 Stale status lines corrected in this pass

| Document | Was | Now |
| :--- | :--- | :--- |
| `PRODUCT_ALIGNMENT_REPORT.md` §J.3, row **G-2** | *"Still open — the freeze was plumbing only; no UI was wired up"* | Re-verified 2026-10-16: the wiring exists **and** is reachable — see this report |
| `BMJ_LAUNCH_CHECKLIST.md` §1, row **B6** | *"…no screen entry point was ever wired, so `SubscriptionManagementScreen`'s pause/resume/cancel actions are unreachable"* | Re-verified 2026-10-16: option **(a) satisfied** in the frozen tree; the residual item is the B5 smoke step |

---

*Nothing in this report is executable. It closes **B6** on evidence, and it deliberately leaves all 14 screens
where they are: 0 of them are required for V1, and 5 of them would introduce a second implementation of a flow
that already ships.*

