# Chargebee Webhook Matrix

**Status:** design only. No code, no configuration change.
**Current transport:** 13 endpoints under `/api/webhooks/*`; each receives `{ "id": "<event_id>" }`,
then re-fetches the event from Chargebee (`Event.retrieve(id)`) — so payload content is trustworthy,
but there is no `chargebee-signature` verification and a body without `id` raises a 500.
**Current idempotency:** `webhook_events` table, `event_id` PK, status `PROCESSING → COMPLETED/FAILED`,
`retry_count`, `last_error`, `@Version`.

Legend — **Today** describes the code as it stands; **Required** is the target behaviour.

---

## Summary

| Event | Endpoint | Local action | Idempotency | Retry | Failure handling |
|---|---|---|---|---|---|
| `customer_created` | `/api/webhooks/customers` | insert `customer_entity`; **+ link user** | event-id claim | none today | mark FAILED, no drain |
| `customer_changed` | same | update `customer_entity`; **+ re-assert link** | event-id claim | none today | mark FAILED, no drain |
| `subscription_created` | `/api/webhooks/subscriptions` | upsert subscription + items | event-id claim | none today | mark FAILED, no drain |
| `subscription_changed` | same | update plan/dates | event-id claim | none today | mark FAILED |
| `subscription_cancelled` | same | status `CANCELLED`, stop deliveries | event-id claim | none today | mark FAILED |
| `subscription_paused` | same | status `PAUSED`, suspend schedule | event-id claim | none today | mark FAILED |
| `subscription_resumed` | same | status restored, recompute `nextDeliveryAt` | event-id claim | none today | mark FAILED |
| `payment_succeeded` | `/api/webhooks/payments` | insert/update `payment_entity` | event-id claim | none today | mark FAILED |
| `payment_failed` | same | record failure; **no subscription action today** | event-id claim | none today | mark FAILED |

**Shared gaps across all nine:** no signature check · no retry drain · no staleness guard · no
dead-letter · no metric · no identity link on any customer-touching path.

---

## 1. `customer_created`

- **Source:** Chargebee, on customer creation (signup, hosted-page signup, API create).
- **Today:** `WebhookEventProcessor.processCustomerEvent` → `CustomerService.saveCustomer` →
  insert `customer_entity`; returns `false` (200 "already exists") if the id is present.
- **Required local action:** upsert the customer **and run the Identity Linker** — if exactly one BMJ
  user has this verified phone (else email), set `users.chargebee_customer_id`. Two matches →
  record conflict, do not link.
- **Idempotency:** claim `event_id`; upsert by primary key (`customer_entity.customer_id`), not
  insert-or-skip — a replay after a partial write must converge.
- **Retry:** on exception, `markEventFailed` and return 5xx so Chargebee retries; BMJ retry worker
  re-runs while `retry_count < 3`.
- **Failure handling:** never leave a created customer without attempting the link; a customer with
  no BMJ user is legal (pre-signup) and must not be flagged as an error.

## 2. `customer_changed`

- **Source:** Chargebee, on any customer field change (email, phone, address, billing prefs).
- **Today:** `CustomerService.updateCustomer` → refresh `customer_entity` fields, incl.
  `resource_version`.
- **Required:** also re-assert the link when `users.chargebee_customer_id` is null, and re-evaluate it
  when the phone/email changed (a typo fix can move a customer between match sets).
- **Idempotency:** full-row overwrite from the event; safe to replay any number of times.
- **Retry:** same as above; this is the **only** path that refreshes an existing customer, so a lost
  event means permanently stale contact data until reconciliation (gap H7).
- **Failure handling:** on failure, keep the old row rather than a partially-updated one — the whole
  handler runs in one transaction.

## 3. `subscription_created`

- **Source:** Chargebee, after a successful hosted-page payment or API create.
- **Today:** processor first calls `customerService.saveCustomer(event)` (idempotent), then
  `SubscriptionService.saveSubscriptions` → `subscription_entity` + items via `SubscriptionMapper`
  (industry-correct: rows keyed by the **Chargebee customer id**).
- **Required:** additionally (a) link the user, (b) reconcile the reserved `delivery_schedule` row
  against the now-real subscription id.
- **Idempotency:** `subscription_entity.id` is the Chargebee subscription id — upsert by PK; replay
  converges.
- **Retry:** 5xx → Chargebee retries; BMJ drain re-runs; reconciliation D5 catches it if both fail.
- **Failure handling:** if the customer row cannot be written, fail the whole event — a subscription
  must never exist without its customer.

## 4. `subscription_changed`

- **Source:** Chargebee, on plan change, quantity change, billing-period change, coupon change.
- **Today:** `SubscriptionService.updateSubscription` — overwrites fields from the event.
- **Required:** apply only when the incoming `resource_version` (or `event_date`) is **not older**
  than the stored one; recompute `nextDeliveryAt` afterwards.
- **Idempotency:** PK upsert; safe to replay.
- **Retry:** as above.
- **Failure handling:** a stale-event rejection is **not** a failure — record `skipped_stale` and
  complete the event, or the retry loop will fight itself.

## 5. `subscription_cancelled`

- **Source:** Chargebee, on immediate or end-of-term cancellation.
- **Today:** `updateSubscription` sets status `CANCELLED`, `cancelled_at`; deliveries are not
  explicitly stopped.
- **Required:** set status verbatim, **stop delivery scheduling** for that subscription, and keep the
  history readable (a cancelled plan must still render in the app, not vanish).
- **Idempotency:** PK upsert; replay converges. Cancellation is terminal — a replay must never
  resurrect an active state.
- **Retry:** as above.
- **Failure handling:** if the schedule cannot be stopped, the subscription must still be marked
  cancelled **first** (billing truth wins); the schedule stop is retried separately and reported.

## 6. `subscription_paused`

- **Source:** Chargebee, when a pause is applied (immediate or scheduled).
- **Today:** `updateSubscription` sets status `PAUSED`.
- **Required:** also suspend the delivery schedule and record `paused_at`; a scheduled pause with a
  future date must not take effect early.
- **Idempotency:** PK upsert with `resource_version` guard.
- **Retry:** as above.
- **Failure handling:** distinguish "paused now" from "paused at period end" — the latter must leave
  deliveries running until the effective date.

## 7. `subscription_resumed`

- **Source:** Chargebee, on resume/reactivation (`subscription_reactivated` is handled separately in
  the processor).
- **Today:** `reactivateSubscription` restores the active state.
- **Required:** recompute `nextDeliveryAt` from the **new** billing period, then re-enable delivery
  scheduling. Do not reuse the pre-pause date.
- **Idempotency:** PK upsert; a replay after the next renewal must not roll dates backwards
  (guarded by `resource_version`).
- **Retry:** as above.
- **Failure handling:** if `nextDeliveryAt` cannot be computed, leave deliveries disabled and flag —
  a wrong date is worse than no date.

## 8. `payment_succeeded`

- **Source:** Chargebee, on successful charge.
- **Today:** `processPaymentEvent` → insert/update `payment_entity`; no subscription state change.
- **Required:** persist the payment, and confirm the subscription is (or becomes) `ACTIVE` — a
  successful payment after a dunning period is the moment a plan comes back to life.
- **Idempotency:** `payment_entity` keyed by Chargebee transaction id — PK upsert; replay converges.
- **Retry:** as above.
- **Failure handling:** a payment that cannot be stored must be surfaced loudly (it is revenue
  evidence); the subscription projection must not depend on it succeeding.

## 9. `payment_failed`

- **Source:** Chargebee, on a declined or failed charge (the dunning cycle).
- **Today:** records the failed payment; **the subscription is left untouched**.
- **Required:** record the payment **and** reflect the subscription's `payment_failed`/dunning state
  from Chargebee (rather than inferring), so the app can show "payment needs attention" instead of
  silently showing an active plan that is about to lapse.
- **Idempotency:** keyed by transaction id; replay converges. Multiple failures are distinct events.
- **Retry:** as above.
- **Failure handling:** never mark a subscription cancelled locally on a payment failure — only
  Chargebee decides that, and it will send `subscription_cancelled` when it does.

---

## Cross-cutting requirements (apply to every event)

| Requirement | Today | Required |
|---|---|---|
| Authenticity | re-fetch by id; **no HMAC** | verify `chargebee-signature`; reject unknown ids with 4xx |
| Malformed body | `e.get("id")` → NPE → 500 | 400 with a reason, no event row created |
| Idempotency | `webhook_events` PK + `@Version` | keep; add ack-after-commit |
| Retry | query exists, no worker | 5-min drain, `retry_count < 3`, then dead-letter |
| Staleness | not checked | `resource_version` / `event_date` guard on every subscription event |
| Identity | never linked | Identity Linker on customer events and after `subscription_created` |
| Observability | none | per-event metric: received / completed / failed / retried / stale |
| Audit | `last_error` only, 4 h retention | `sync_findings` row per event outcome; retain ≥ 30 days |
| Ordering | none | per-subscription serialisation by `event_date` |
| Replay | no endpoint | `replay(eventId)` manual operation (see reconciliation plan §7) |

---

## Which events the client depends on

| Client behaviour | Depends on | If the event is lost |
|---|---|---|
| Home shows the active plan | `subscription_created`, `subscription_changed` | card missing until reconciliation |
| Subscription screen shows pause/cancel state | `subscription_paused`, `subscription_resumed`, `subscription_cancelled` | wrong state shown indefinitely |
| "Payment needs attention" | `payment_failed` | user is not warned before lapsing |
| Plan restored after dunning | `payment_succeeded` | plan appears dead after payment |

That table is the argument for reconciliation: every one of those rows currently has **no** repair
path if the webhook is missed.

