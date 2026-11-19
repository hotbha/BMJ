# Chargebee Synchronisation Architecture

**Status:** design only. No code, no migration, no database write.
**Basis:** read from the running codebase (`bmjServer` @ `1f17048`) plus the measured data in
`SUBSCRIPTION_DATA_CENSUS.md` and `SUBSCRIPTION_MIGRATION_VALIDATION.md`.
**Goal:** BMJ stays consistent with Chargebee continuously, not by a one-off repair.

---

## 1. Source of truth decision

Chargebee owns **billing truth**. BMJ owns **experience state**. Neither may write the other's fields.

| Entity / fact | Source of truth | BMJ may write? | Notes |
|---|---|---|---|
| Customer existence (id, email, phone, billing address) | **Chargebee** | no — mirror only | `customer_entity` is a cache |
| Subscription (plan, status, dates, quantity, mrr) | **Chargebee** | no — mirror only | `subscription_entity` is a cache |
| Invoice, payment, credit note, order | **Chargebee** | no — mirror only | already mirrored via webhooks |
| Item / item_price (catalogue) | **Chargebee** | no — mirror only | `item_entity`, `item_price_entity` |
| `users.id`, credentials, roles | **BMJ** | yes | Chargebee has no concept of it |
| The **identity link** `users.chargebee_customer_id` | **BMJ** (derived from Chargebee identity) | yes — by one component only | see §2; today it is written only at auth time |
| Delivery schedule / preferred slot | **BMJ** | yes | local-only; Chargebee receives the reserved subscription id |
| Cart, browsing state | **BMJ** | yes | never leaves the device except as an order |
| Notification preferences | **BMJ** | yes | — |

**Rule of precedence:** if BMJ and Chargebee disagree about a billing fact, Chargebee wins and BMJ is
overwritten. No reconciliation path may ever "fix" Chargebee from BMJ.

**Rule of derivation:** a local fact (e.g. `nextDeliveryAt`) may be *computed* from Chargebee truth,
but must be recomputed whenever the underlying Chargebee fact changes — never independently edited.

---

## 2. Identity model

Three identifiers exist; the architecture's job is to keep exactly one mapping between them.

```
users.id                     (BIGINT, BMJ)          e.g. 504
users.chargebee_customer_id  (VARCHAR, BMJ)         e.g. 16CS3UVZQtF20nFJ
customer_entity.customer_id  (VARCHAR, PK)          the Chargebee id — must equal the middle value
```

**Invariant I-1 (core):** for every user that has ever transacted,
`users.chargebee_customer_id` is non-null, points to an existing `customer_entity` row, and that row
describes the same person (phone or email matches).

**Invariant I-2 (storage convention):** every child row referencing a customer
(`subscription_entity`, `order_entity`, `invoice_entity`, `payment_entity`, `charge_entity`,
`delivery_schedule`, `bottle_transactions`) stores the **Chargebee customer id** — never an id
derived from `users.id`.

**Invariant I-3 (one writer):** only the *Identity Linker* writes
`users.chargebee_customer_id`. Today that role is played implicitly by `AuthController` (9 call
sites: L153, L351, L371, L442, L452, L548, L558, L1086, L1175) and **no webhook path performs it** —
which is the root of the defect.

**Legacy tolerance.** Numeric-keyed `customer_entity` rows (43 of 81, measured) are historical
artifacts: readable during transition, never created again, retired by the Phase 2 repair.

**Resolution contract** — every read path must implement this and nothing looser:

```
resolve(user) ->
    key = users.chargebee_customer_id
    if key is null                  -> IdentityUnlinked   (explicit error, never "no data")
    if customer_entity[key] missing -> IdentityBroken
    else key
```

The distinction between **"no subscription"** and **"identity not linked"** is a first-class part of
the model. Conflating the two is what produced the silent empty screen.

---

## 3. Customer lifecycle

| Trigger | Where it happens today | What must be true afterwards |
|---|---|---|
| New user via OTP | `AuthController` creates the Chargebee customer, then `user.setChargebeeCustomerId(...)` | link set, `customer_entity` row present, both in one transaction |
| New user via Google | separate path in `AuthController` (L351/L371) | identical post-condition |
| Email/password (legacy) | `AuthController` L442–459 | identical |
| Existing user logging in | link should **self-heal** when null | today: does not |
| `customer_created` webhook | `CustomerService.saveCustomer` → `customer_entity` only | must also attempt the link when a BMJ user with the same verified phone exists |
| `customer_changed` webhook | `CustomerService.updateCustomer` → `customer_entity` | re-assert the link if it was missing |

**Linking policy** — one rule, used by auth *and* by webhook:

1. Match on **verified phone** (`users.username`) first; fall back to verified email.
2. Exactly one match → set the link.
3. Zero matches → do nothing (a Chargebee customer can legitimately exist before the BMJ user).
4. **Two or more BMJ users match** → never guess. Emit an `identity_conflict` finding, leave both
   unlinked, alert.
5. Two or more Chargebee customers match one BMJ user → prefer the one with an active subscription,
   else the most recent; record the duplicate in the reconciliation report.

Duplicate customers (the 43-vs-38 split) are a data condition, not a design feature: the target state
is one `customer_entity` row per person, with retired twins kept only as audit records.

---

## 4. Subscription lifecycle

BMJ is a **projection** of Chargebee's subscription state.

| Transition | Chargebee event | BMJ projection |
|---|---|---|
| Purchase intent | — | `DeliveryScheduleService.reserve()` writes a schedule keyed by the reserved subscription id **before** the hosted page opens |
| Created | `subscription_created` | upsert `subscription_entity` (+ items), ensure customer row, link if possible |
| Renewed | `subscription_renewed` | update period dates, recompute `nextDeliveryAt` |
| Changed | `subscription_changed` | update plan / quantity / dates |
| Paused | `subscription_paused` | status `PAUSED`; suspend delivery scheduling |
| Resumed | `subscription_reactivated` | restore status; recompute `nextDeliveryAt` |
| Cancelled | `subscription_cancelled` | status `CANCELLED`; stop deliveries; retain history |
| Abandoned | no event arrives | schedule row remains reserved → **orphan**, swept by reconciliation |

**Status authority.** `subscription_entity.status` is copied verbatim from Chargebee (`ACTIVE`,
`CANCELLED`, `PAUSED`, `IN_TRIAL`, `NON_RENEWING`, …). BMJ never invents a status and never
transitions one locally except optimistically, with the webhook authoritative on arrival.

**Local augmentation.** `delivery_schedule`, `nextDeliveryAt` and slot preferences are BMJ-owned
columns attached to a Chargebee subscription id. They survive status changes and are re-derived — not
re-entered — when the billing period changes.

**Ordering rule.** Events for one subscription apply in Chargebee's `event_date` order; a late older
event must not overwrite a newer projection (guard on `resource_version`).

---

## 5. Failure scenarios

| # | Scenario | Today | Required |
|---|---|---|---|
| F1 | Webhook never delivered | silently lost, no re-fetch | nightly reconcile finds the drift by comparing Chargebee ↔ BMJ |
| F2 | Out-of-order delivery | older event overwrites newer | reject stale `resource_version` / `event_date` |
| F3 | Duplicate delivery | handled — `webhook_events` PK claims the event | keep; extend to ack-after-commit |
| F4 | Handler throws | `markEventFailed` + retry counter, **but nothing retries** | worker drains FAILED while `retryCount < 3`, then dead-letters |
| F5 | Partial write | one transaction per event, cascades inside `@Transactional` | keep; require idempotent per-entity upserts so replay is safe |
| F6 | Identity ambiguous (two users, one customer) | silently unlinked → empty screen | record conflict, refuse to guess, surface to ops |
| F7 | `users.chargebee_customer_id` NULL | `findByCustomer(null)` → `200 []` | explicit `IdentityUnlinked`, never an empty list |
| F8 | Legacy numeric keys | unreachable rows (13 of 16 measured) | re-key via repair; reads tolerate both during transition |
| F9 | Chargebee unavailable during reconcile | n/a — no reconciler exists | backoff, partial progress, resumable cursor |
| F10 | Chargebee customer deleted | `customer_deleted` handled | retain local rows for audit; mark link broken |
| F11 | Webhook spoofing | content cannot be forged (event is re-fetched by id) but **no `chargebee-signature` check**, and a body without `id` yields a 500 | verify signature, reject unknown ids with 4xx |

**Availability principle:** a webhook outage must degrade *freshness*, never *correctness*. The system
must converge with zero webhooks — that is what makes reconciliation mandatory rather than optional.

---

## 6. Recovery scenarios

| Failure | Recovery mechanism | Trigger | Time to converge |
|---|---|---|---|
| Lost webhook(s) | reconcile subscriptions changed since the last cursor | nightly + on demand | ≤ 24 h |
| Handler failure | retry drain (FAILED, `retryCount < 3`) | every 5 min | ≤ 15 min |
| Dead-lettered event | operator replay by event id | manual | operator-bound |
| Identity unlinked | identity repair pass (link by verified phone/email) | nightly + on login | ≤ 24 h |
| Legacy key drift | one-off re-key, then continuous detection | single window | once |
| Divergent projection | per-entity re-fetch from Chargebee and upsert | reconciliation | ≤ 24 h |
| Total loss of projection | full backfill from Chargebee customer list | manual runbook | hours |

**Recovery is always "pull from Chargebee", never "replay local assumptions."** Webhook replay is a
latency optimisation; reconciliation is the correctness mechanism.

---

## 7. Sync responsibilities

| Component | Owns | May write | Must never |
|---|---|---|---|
| `AuthController` (today) | authentication | `users.*`, including the link | mirror billing data |
| **Identity Linker** (new, extracted) | the mapping | `users.chargebee_customer_id` **only** | create/delete customers |
| `CustomerService` | customer mirror | `customer_entity` | touch `users` |
| `SubscriptionService` | subscription mirror | `subscription_entity`, items | touch `users` |
| `DeliveryScheduleService` | local scheduling | `delivery_schedule` | invent subscription status |
| `WebhookEventProcessor` | orchestration | `webhook_events` | write business fields directly |
| **Reconciler** (new) | convergence | any mirror table | overwrite BMJ-owned fields |
| **Reporter** (new) | observability | nothing | mutate |

Naming the Linker as its own responsibility is the single most valuable structural change: the defect
exists precisely because "link the user" is currently a side effect of three unrelated auth flows.

---

## 8. Event flow diagrams

**A — Purchase, happy path**

```
App          BMJ API                      Chargebee           Webhook            DB
 | create sub   |                            |                   |               |
 |------------->| reserve(schedule)          |                   |               |
 |              |--------------------------->| create hosted page|               |
 |<-- host url -|                            |                   |               |
 | pay on hosted page ---------------------->|                   |               |
 |              |                            |--subscription_created---------->|
 |              |<----------------------- id re-fetch ------------|               |
 |              | CustomerService.save   (mirror customer)                        |
 |              | IdentityLinker.link    (users.chargebee_customer_id)            |
 |              | SubscriptionService.save (projection + items)                   |
 |              | markEventCompleted                                             |
 |<-- redirect -|                                                                |
 | GET /my      | resolve(user) -> chargebee id -> rows                          |
```

**B — Nightly reconciliation**

```
cron 02:00
  |--> list Chargebee subscriptions changed since cursor
  |--> for each: diff with local projection
  |       match    -> advance cursor
  |       drifted  -> upsert from Chargebee, emit finding
  |       missing  -> create locally, emit finding
  |--> local rows whose Chargebee counterpart 404s
  |       -> mark ORPHANED(chargebee_gone), retain for audit
  |--> identity pass: users with null/broken link -> link or conflict
  |--> publish run report (counts, durations, findings)
```

**C — Webhook failure and retry**

```
receive -> claim(event_id) --duplicate--> ack 200
   | new
 handler -> success -> COMPLETED -> ack 200
   | fail
 markEventFailed(retryCount+1) -> ack 5xx (Chargebee also retries)
   |
 retry worker (5 min): FAILED and retryCount < 3 -> re-run
   | still failing
 dead-letter -> alert -> operator replay
   |
 nightly reconcile catches anything retries missed
```

---

## 9. What this architecture does not change

- No new billing logic; Chargebee remains the only place money is computed.
- No client contract change other than the honest `IdentityUnlinked` error replacing a false `[]`.
- No schema redesign required: `webhook_events` and the mirror tables already exist and are adequate;
  the missing pieces are the **Linker**, the **Reconciler**, and a **retry worker**.


