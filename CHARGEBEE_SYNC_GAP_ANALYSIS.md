# Chargebee Sync — Gap Analysis

**Status:** analysis only. No code, no migration, no write.
**Compared:** implementation at `bmjServer` @ `1f17048` versus `CHARGEBEE_SYNC_ARCHITECTURE.md`.
**Evidence:** file:line citations are from the current source; data figures from `SUBSCRIPTION_DATA_CENSUS.md`.

**Headline:** the mirroring engine is in better shape than the clinical picture suggested — 13 webhook
controllers, a `webhook_events` idempotency table with `@Version`, retry counters and a cleanup
scheduler all exist. What is missing is the **identity link**, the **retry drain**, the
**reconciliation loop**, and an **honest read contract**. Those four account for every observed
symptom.

---

## CRITICAL

| # | Gap | Evidence | Consequence |
|---|---|---|---|
| C1 | **No webhook path ever writes `users.chargebee_customer_id`.** The link is set only inside `AuthController` (9 sites). `CustomerService` and `SubscriptionService` never touch `users`. | writes at `AuthController` L153, L371, L452, L558, L1086, L1175; zero writes outside it. `User.java:74` documents the intended 1:1 but nothing enforces it | a user created or linked outside the exact auth sequence stays unlinked **forever**, even though Chargebee and the local mirror are perfectly correct |
| C2 | **A false empty answer.** `/my` returns `200 {"status":"success","subscriptions":[]}` when the resolved customer has no rows — including when the key resolved to the *other* identity twin. | `SubscriptionController` L71–110: `customer.isPresent() ? findByCustomer(...) : List.of()` | client cannot distinguish "no plan" from "identity mismatch"; **measured: 3 users, 9 ACTIVE rows hidden** |
| C3 | **No reconciliation process exists.** No `@Scheduled` and no `@EnableScheduling` anywhere in `src/main` — the only scheduling is an in-process cleanup executor. | repo-wide grep returns nothing for `@Scheduled|@EnableScheduling` | any missed webhook is permanent drift; correctness depends entirely on webhook delivery |
| C4 | **Retry capability is dead code.** A retry method and the exact query for it exist, but nothing invokes either. | `IdempotencyService.retryEvent(...)` L189 and `findByProcessingStatus("FAILED")` L227 — no callers; the only scheduler (`L50`) calls `cleanupExpiredEvents` | a handler failure is never retried by BMJ; recovery depends on Chargebee re-delivering |
| C5 | **Legacy identity drift is unreachable and unmeasured.** Business rows keyed by a numeric customer id cannot be found by a lookup keyed on the Chargebee id, and nothing reports them. | measured: 13 of 16 rows unreachable; 4 ACTIVE rows belong to no user at all | paying customers see an empty subscription screen; nobody is alerted |

---

## HIGH

| # | Gap | Evidence | Consequence |
|---|---|---|---|
| H1 | **No webhook authenticity check.** Controllers ignore `chargebee-signature`; they trust `body.id` and re-fetch the event from Chargebee. | `CustomerWebhookController` L34: `Event.retrieve(e.get("id").toString())` | content cannot be forged (good), but anyone can force arbitrary event re-processing; a body without `id` throws → 500 instead of 400 |
| H2 | **No staleness / ordering guard.** `resource_version` is stored but never compared before overwrite. | only `CustomerService.java:120` assigns it; no comparison anywhere | an older, late-arriving event overwrites a newer projection; a cancel can be undone by a stale "created" |
| H3 | **No self-heal on login.** Existing auth paths create a Chargebee customer only when the link is null, and never re-derive the link from an existing Chargebee customer. | `AuthController` L351, L442, L548 guard on `getChargebeeCustomerId() == null` | the natural repair point (every login) is skipped exactly when it is needed |
| H4 | **Local write-side inherits the identity defect.** `delivery_schedule` and `bottle_transactions` are keyed by whatever the resolver returns. | `DeliveryScheduleService.reserve(customerId, …)` from `SubscriptionController` L163 | the identity bug propagates into scheduling and bottle tracking, not just subscriptions |
| H5 | **Orphaned schedule rows are unavoidable.** The schedule is reserved **before** the hosted page opens; there is no delete path and no sweeper. | `SubscriptionController` L163 comment "Written before checkout" | every abandoned checkout leaks a row permanently (see `ORPHAN_SCHEDULE_REMEDIATION.md`) |
| H6 | **Duplicate Chargebee customers can be created by concurrent auth.** Three separate paths check-then-create without a unique constraint on phone/email. | `AuthController` L351/442/548 pattern | two customers for one person — the exact condition that produced the 43/38 split |
| H7 | **Customer updates are one-way only.** `saveCustomer` returns `false` when the customer already exists, so the *only* path that refreshes a customer is `customer_changed`. | `CustomerService.saveCustomer` early-return | if that one event is lost, customer data is stale forever with no repair path |

---

## MEDIUM

| # | Gap | Evidence | Consequence |
|---|---|---|---|
| M1 | **No dead-letter store or replay endpoint.** FAILED rows are subject to the same 4-hour cleanup as COMPLETED ones. | `IdempotencyService.cleanupExpiredEvents` → `deleteOldCompletedEvents(cutoff)` | failures disappear from the record; audit trail is shorter than an incident investigation needs |
| M2 | **Idempotency has two sources of truth.** A per-instance in-memory `ConcurrentHashMap` sits in front of the DB claim. | `IdempotencyService` L37 | cache and DB can disagree across instances; a stale cache entry can skip or stall an event |
| M3 | **No alerting on sync health.** `getProcessingStats()` exists but nothing polls it; no metric is emitted. | `IdempotencyService.getProcessingStats` L~215 | the system can be failing silently for days — exactly what happened |
| M4 | **Shared mutable state in the processor.** `processingResults` is a plain `HashMap` field on a singleton service. | `WebhookEventProcessor` L56 | concurrent webhooks interleave and can report each other's results; not thread-safe |
| M5 | **No durable reconciliation cursor.** There is no `sync_cursor`/`last_synced_at` table. | schema inspection | a reconciler cannot resume after failure and cannot bound its work window |
| M6 | **Every webhook costs a Chargebee API call.** 13 controllers each do `Event.retrieve(id)`. | controller pattern | Chargebee rate limits become a BMJ availability dependency; latency on the webhook path |
| M7 | **Event timestamps are not stored.** `webhook_events` keeps `processed_at` only. | `WebhookEvent` columns | may not be detectable after the fact whether a projection was built from a stale event |
| M8 | **No promotion of the mirror to a tested contract.** No test asserts that a webhook creates a row the API can then read. | test inventory: no webhook→API integration test | the C1/C2 defect class has no regression net |

---

## LOW

| # | Gap | Evidence | Consequence |
|---|---|---|---|
| L1 | 13 near-duplicate webhook controllers | `controllers/webhooks/*` | copy-paste drift; a fix must be applied 13 times |
| L2 | No record of which events were *skipped* as duplicates | claim returns false → immediate ok | replay forensics are guesswork |
| L3 | Short retention on completed events | cleanup after `CLEANUP_HOURS` | cannot reconstruct history beyond the window |
| L4 | No documented replay runbook | — | operator cannot safely re-drive an event |
| L5 | `processingResults.clear()` at the start of each handler | `WebhookEventProcessor` L62, L104 | discards diagnostic context for the previous event |

---

## Scoring against the stated principles

| Principle | Current state | Blocking gaps |
|---|---|---|
| Chargebee is source of truth | **Partially true** — webhooks copy Chargebee → BMJ, but nothing ever re-reads | C3, H7 |
| Local DB is a cache + reporting layer | **Inverted in places** — the local identity column is treated as the authority | C1, H3 |
| No user sees "no subscription" when Chargebee says otherwise | **Violated** — measured 3 users | C2, C5 |
| Identity drift self-heals | **Not implemented** — drift is permanent | C1, C3, H3 |
| Idempotent | **Yes, and well built** (`webhook_events` PK + `@Version`) | M2, L2 |
| Retryable | **Designed but not wired** | C4, M1 |
| Observable | **No** — no metrics, no alerting, stats unread | M3, C5 |
| Auditable | **Partly** — status + retry_count + last_error, short retention | M1, M7, L3 |

---

## The four gaps that explain every symptom

1. **C1** — the link is a side effect of auth, so it is absent exactly when webhooks arrive.
2. **C2** — the read path converts a missing link into a plausible-looking empty list.
3. **C3/C4** — nothing repairs either condition afterwards, because there is no loop.
4. **C5** — the drift that already exists is invisible to both code and operators.

Everything else in this document is hardening. These four are the defect.

