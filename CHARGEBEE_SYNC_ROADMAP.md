# Chargebee Sync Roadmap

**Status:** design only. No code, no commits, no migration.
**Companions:** `CHARGEBEE_SYNC_ARCHITECTURE.md`, `CHARGEBEE_SYNC_GAP_ANALYSIS.md`,
`CHARGEBEE_RECONCILIATION_PLAN.md`, `CHARGEBEE_WEBHOOK_MATRIX.md`.

**Sequencing principle:** stop the harm, then make it self-healing, then make it provable.

```
Phase 1  honest read path        ── stops users seeing a false empty screen
Phase 2  identity repair         ── fixes today's drift, and prevents recurrence
Phase 3  webhook hardening       ── makes new events trustworthy
Phase 4  reconciliation          ── makes the system converge without webhooks
Phase 5  observability           ── makes failures visible in minutes
Phase 6  operational tooling     ── makes repair repeatable by a human
```

Each phase is independently shippable, independently revertible, and leaves the system strictly
better on its own.

---

## Phase 1 — Immediate protections

**Goal:** no user is ever told "no subscription" when Chargebee says otherwise.

| Deliverable | Detail | Evidence it addresses |
|---|---|---|
| `resolve(user)` contract | explicit `IdentityUnlinked` / `IdentityBroken` outcomes instead of a null key | gap C2, F7 |
| `/api/subscriptions/my` | return `409` with a reason when the identity is unlinked; never `200 + []` for an unlinked user | gap C2 |
| Null-key guard | repository-level assertion: a null/blank customer id can never reach `findByCustomer` | gap C2 |
| Login self-heal (read-only) | on successful auth, if the link is null, attempt to derive it from `customer_entity` by verified phone — log only, no writes yet | gap H3 |
| Client copy | a distinct "we couldn't load your plan" state, not the empty state | gap C2 |

**Exit criteria:** a user with an unlinked identity receives an explicit error; a user with a linked
identity and rows receives them; no path returns an empty list for a known-unlinked user.
**Effort:** small (one controller method, one guard, one client state).
**Risk:** low — no data is written. **Rollback:** revert the commit.
**This is the only phase that reduces customer-visible harm on its own.**

---

## Phase 2 — Identity repair

**Goal:** today's drift is fixed, and new drift cannot be created.

| Deliverable | Detail |
|---|---|
| Identity Linker (extracted) | one component owns `users.chargebee_customer_id`; auth and webhooks both call it |
| Linking policy | phone → email, exactly-one-match rule, conflict detection (§3 of the architecture) |
| Login self-heal (write-enabled) | a null link is repaired on login, inside the auth transaction |
| `customer_created` / `subscription_created` hooks | the Linker runs on the webhook path too |
| One-off re-key | `SUBSCRIPTION_MIGRATION_PLAN.md` Phases 0–4, with the same-person gate (1e) and FK gate (1c) |
| Duplicate-customer report | read-only list of one-person-two-records, published before any merge |

**Exit criteria:** `sub_census.py` reports `AFFECTED = 0`; every user with rows is linked; the
same-person gate passes for 100 % of re-keyed rows; `sync_findings` shows zero conflicts introduced.
**Effort:** medium (one new service, three call-site changes, one gated data migration).
**Risk:** medium — this is the only phase that writes business data. Mitigations: Phase 0 snapshot,
dry-run first, per-cohort approval, row caps.
**Rollback:** per `SUBSCRIPTION_MIGRATION_PLAN.md` §4 (exact, because only `customer_id` moves).

---

## Phase 3 — Webhook hardening

**Goal:** new events are authenticated, ordered, retried and dead-lettered.

| Deliverable | Detail | Gap |
|---|---|---|
| Signature verification | validate `chargebee-signature` on all 13 endpoints | H1 |
| Malformed-body handling | 400 with a reason, no event row created | H1 |
| Staleness guard | reject/complete `skipped_stale` on older `resource_version` / `event_date` | H2 |
| Retry worker | drain `FAILED` while `retry_count < 3`, every 5 minutes | C4 |
| Crash recovery | `PROCESSING` older than 15 min is treated as `FAILED` | M1 |
| Dead-letter | status `DEAD_LETTER`; excluded from cleanup; alert on entry | M1 |
| Event metrics | received / completed / failed / retried / stale per event type | M3 |

**Exit criteria:** a deliberately failing handler recovers within 15 minutes without human action;
an out-of-order event cannot overwrite a newer projection; a replay of any completed event changes
nothing; no event is silent for longer than 5 minutes.
**Effort:** medium. **Risk:** low–medium — the retry worker can amplify a persistent bug; cap it at
3 attempts and alert rather than loop.
**Rollback:** disable with `SYNC_ENABLED=false`; the webhook path itself keeps working.

---

## Phase 4 — Scheduled reconciliation

**Goal:** the system converges even if no webhook ever arrives.

| Deliverable | Detail |
|---|---|
| Hourly job | retry drain + hot checks (D1 for touched users, D5 for 24 h window, D7) |
| Nightly job | full ordered pass: identity → duplicates → subscription diff → mismatch → orphans → staleness → schedule sweep → cursor → report |
| Detectors D1–D7 | as specified in `CHARGEBEE_RECONCILIATION_PLAN.md` §3 |
| State | `sync_cursor` + `sync_findings` (additive tables only) |
| Dry-run mode | default on for the first week of any new detector |
| Budget guards | row caps, API caps, single-leader lock |

**Exit criteria:** with webhooks disabled for 24 hours in staging, the nightly run restores full
agreement; a second consecutive run produces zero findings (proving idempotency); `AFFECTED = 0`
holds for seven consecutive nights.
**Effort:** large (the biggest phase). **Risk:** medium — writes business data, so it ships detector by
detector, dry-run first.
**Rollback:** per-detector kill switches; `SYNC_DRY_RUN=true` reverts behaviour without a deploy.

---

## Phase 5 — Observability

**Goal:** a sync failure is visible in minutes, not discovered by a customer.

| Deliverable | Detail |
|---|---|
| Metrics | link coverage %, rows on twin keys, orphan ACTIVE subs, failed/stale events, drift repaired per run, run duration |
| Alerts | any non-zero on the four "must be zero" metrics; missed nightly heartbeat; drift > 10× baseline |
| Dashboards | one sync-health board: coverage, drift trend, top findings |
| Run reports | persisted per run in `sync_findings`, queryable by detector and subject |
| Retention | ≥ 30 days for findings (today: 4 h for events) |
| SLOs | identity coverage 100 %; projection freshness ≤ 24 h; webhook processing ≤ 5 min p95 |

**Exit criteria:** a deliberately unlinked user raises an alert within one hourly cycle; a missed
nightly run alerts by 04:00; the four zero-metrics are on a dashboard and green for 7 days.
**Effort:** medium. **Risk:** low (read-only). **Rollback:** noise — tune thresholds, keep emitting.

---

## Phase 6 — Operational tooling

**Goal:** a support engineer can diagnose and repair one customer's identity in minutes, safely.

| Deliverable | Detail |
|---|---|
| `audit(userId)` | prints link, twins, owned rows, reachability — the tool I hand-wrote to find this defect |
| `relink(userId)` | D1 for one user with a full match trace; refuses on conflict |
| `rekey(subscriptionId)` | D4 for one row behind the same-person gate |
| `replay(eventId)` | re-drive a webhook idempotently |
| `sweep(dryRun)` | abandoned delivery schedules (orphan remediation) |
| Runbooks | one page per operation: what it does, what it writes, how to undo, who may run it |
| Access | admin-only, audited, no bulk flag |

**Exit criteria:** a support engineer can resolve "customer says they have a plan but the app shows
nothing" without engineering, and every action is in the audit log.
**Effort:** medium. **Risk:** low if the tools are per-subject and refuse ambiguity.
**Rollback:** tools are additive; disable endpoints if misused.

---

## Dependencies and ordering

```
P1 honest read path ──────────────┐ (no dependency; ship now)
                                  │
P2 identity repair ───────────────┤ needs P1's resolve() contract for verification
        │                         │
        ├──> P4 reconciliation ───┤ needs P2's Linker; detectors D1/D4 depend on it
        │                         │
P3 webhook hardening ─────────────┘ independent of P2, but P4 catches what P3 misses
        │
        └──> P5 observability ──── needs P3's event metrics + P4's run reports
                     │
                     └──> P6 tooling ── needs everything above to be safe
```

- **P1 and P3 can start in parallel.** P2 depends on P1 only for its verification story.
- **P4 must not precede P2**, because re-keying without a valid link would move rows to the wrong
  person.
- **P5 before P6**, so the tools are observable from day one.

## What each phase does for the observed defect

| Phase | Effect on the measured 3 affected users |
|---|---|
| P1 | they get an honest error instead of a false "No subscription yet" — harm reduced, not fixed |
| P2 | they get their subscriptions back (9 ACTIVE rows become visible) |
| P3 | prevents new users joining that set |
| P4 | repairs anyone who slips through anyway |
| P5 | tells us immediately if the number ever rises again |
| P6 | lets support fix an individual case without a deploy |

## Explicitly out of scope

- No change to pricing, plans or billing rules.
- No move away from Chargebee, and no local billing computation.
- No client redesign; the only client change is the honest error state in P1.
- No new tables beyond the two additive sync tables in P4.
- No deletion of any customer, subscription or schedule.

