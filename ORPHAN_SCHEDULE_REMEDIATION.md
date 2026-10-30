# Orphan Schedule Remediation

> **Date:** 2026-10-30 · **No code changed by this document.**
> Scope: `delivery_schedule` rows that exist without a live Chargebee subscription.

## 1. Why orphans exist (measured in the current code)

`SubscriptionCheckoutService` calls `DeliveryScheduleService.reserve(customerId, schedule)` **before** the Chargebee hosted page is created, because Chargebee's `checkout_new` accepts `subscription[id]` but **not** `subscription[meta_data]`. The reserved id is:

1. minted as `bmj<32 hex>`,
2. written to `delivery_schedule` immediately,
3. passed to Chargebee, and
4. used by the `subscription_created` webhook to join the schedule back to the subscription.

There is **no delete path** anywhere (the repository is only ever read), and **no scheduling infrastructure** in the server (`@Scheduled`/`@EnableScheduling` do not appear in the codebase). Consequence: every checkout abandoned after step 2 leaves a row forever.

| Class | Meaning | Volume |
| :--- | :--- | :--- |
| A | Reserved, no Chargebee subscription | one per abandoned checkout (largest) |
| B | Subscription cancelled/expired, schedule remains | one per churn |
| C | Same customer reserved several ids (retries) | N−1 per retry |

## 2. Option A — keep the reservation, add a reconciliation job

**Shape:** daily job, rows older than 48 h, capped at 500/run; for each row ask Chargebee for the subscription:

- **404** → export the row to JSONL, then delete (class A).
- **exists, active/trial/future** → keep.
- **exists, cancelled/expired/completed** → keep (cheap history, and `canPromiseDelivery(status)` already prevents delivery promises).
- **API error** → defer to the next run.

| Dimension | Assessment |
| :--- | :--- |
| Correctness of the webhook join | ✅ unchanged — still exact-id, never heuristic |
| Risk to conversion | ✅ zero: the happy path is untouched |
| Data loss window | 🟡 rows live ≤ 48 h (bounded, never used for anything but the join) |
| Client change | ✅ none |
| Server work | ~1 day: a `@Scheduled` class + `@EnableScheduling` + a Chargebee lookup + JSONL export + a mode flag |
| Operational cost | one alert on job failure; Chargebee call volume ≈ rows/run (capped) |
| Reversibility | ✅ high — job can be switched to `dry-run` or deleted |
| Failure mode | a wrong deletion is possible only if Chargebee returns 404 for an id that exists — impossible, ids are minted server-side and passed as `subscription[id]` |

## 3. Option B — reserve only after the hosted page succeeds

**Shape:** don't write anything up front; persist the schedule when the app returns from the hosted page (or when the webhook fires).

Two ways to do it, both worse than they look:

1. **Client posts the schedule after return.** The app holds the day-wise map in memory across the hosted page. If the OS kills the app, the browser is dismissed, or the return deep-link never fires, the Chargebee subscription exists **with no schedule** — the customer paid for a plan that cannot promise deliveries. Requires a new endpoint, client retry logic, and reconciliation of "subscription without schedule": the mirror image of today's orphans, but with a paying customer on the wrong side of it.
2. **Match after the fact** (customer + plan + timestamp). This is exactly the heuristic the current design was built to avoid; two subscriptions created minutes apart by the same customer are indistinguishable.

| Dimension | Assessment |
| :--- | :--- |
| Correctness of the webhook join | 🟠 becomes heuristic or depends on a client round-trip |
| Risk to conversion | 🔴 a killed app loses the schedule *after* payment |
| Data loss window | 🔴 unbounded (until the client retries) |
| Client change | required (new call, retry, offline handling) |
| Server work | ~2–3 days + a new endpoint + reconciliation for "paid but scheduleless" |
| Operational cost | higher: two new failure modes and a customer-visible defect class |
| Reversibility | 🟠 low once clients depend on it |

## 4. Comparison

| Criterion | Option A (cleanup job) | Option B (reserve later) |
| :--- | :--- | :--- |
| Eliminates orphans | ✅ after 48 h | ✅ in theory |
| Protects the paid path | ✅ absolutely | 🔴 can lose the schedule after payment |
| Join correctness | ✅ exact id | 🟠 heuristic / client-dependent |
| Client changes | none | required |
| Effort | ~1 day | ~2–3 days |
| Reversible | yes | no |
| Uses existing webhook contract | yes | partially |

## 5. Recommendation: **Option A**

Reasons, in order:

1. **Money correctness beats table cleanliness.** A is the only option that cannot produce a paying subscription without a schedule; B's failure mode does exactly that.
2. **It preserves the design's one good property** — the webhook joins by an id the server minted, with no guessing. B reintroduces the ambiguity that `DeliveryScheduleEntity`'s documentation explicitly rejects.
3. **Effort and reversibility.** One day, and one flag away from being disabled.
4. The rows A leaves behind for ≤48 h are inert: nothing reads them except the join.

### Recommended sequencing for A

| Phase | Work | Risk | Gate |
| :--- | :--- | :--- | :--- |
| 1 | **Census** (read-only SQL in `LAUNCH_HARDENING_SPRINT.md` §5.3) — size classes A, B, C | none | numbers reviewed |
| 2 | **Dry-run job** — logs "would delete", writes the JSONL export, deletes nothing | none | one week of logs, owner named |
| 3 | **Live job** — enabled by config flag, 500/run, 48 h floor | low | delete list matches the dry run |
| 4 | **Stop-at-source** — delete the reserved row when the Chargebee request itself throws; add `expires_at` + index so the job never full-scans | low | covered by a unit test |

Phase 4 is the only part that touches the checkout transaction, and it is a `catch`-block delete: the smallest possible change that stops new class-A rows at birth.

## 6. When Option B becomes right

Only if Chargebee adds metadata support to hosted checkout, so the schedule can travel with the request and be read back from the subscription. Until then B is a redesign with a worse failure mode, and the brief explicitly excludes architecture work.

