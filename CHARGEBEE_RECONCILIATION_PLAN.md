# Chargebee Reconciliation Plan

**Status:** design only. No code, no scheduling enabled, no database write.
**Companions:** `CHARGEBEE_SYNC_ARCHITECTURE.md`, `CHARGEBEE_SYNC_GAP_ANALYSIS.md`.

**Premise:** webhooks are a latency optimisation. This plan is the correctness mechanism. If every
webhook were lost for a week, the system must still converge.

---

## 1. Principles

1. **Pull, never replay assumptions** — every repair reads current truth from Chargebee.
2. **Idempotent** — running a pass twice changes nothing the second time.
3. **Resumable** — an interrupted pass continues from a stored cursor.
4. **Bounded** — per-run caps on rows and API calls; no unbounded sweep in production.
5. **Observable** — every pass emits counts, durations and findings, even when it finds nothing.
6. **Non-destructive** — orphaned or ambiguous data is flagged and quarantined, never deleted.
7. **Read-only where possible** — a pass may run in `DRY_RUN` and report what it *would* change.

---

## 2. Cadence

| Job | Cadence | Scope | Budget |
|---|---|---|---|
| **Hourly repair** | 5 min (retry) + 60 min (hot checks) | retry drain; users touched in the last 24 h; subscriptions changed in the last 24 h | ≤ 500 API calls |
| **Nightly repair** | 02:00 local, once | full identity pass, subscription diff since cursor, duplicate detection, orphan sweep | ≤ 20 000 API calls, chunked |
| **Manual repair** | on demand | one user / subscription / event / customer | unbounded, operator-driven |

The hourly job asks "is anything wrong right now". The nightly job converges everything. Neither may
mutate BMJ-owned fields (delivery preferences, cart, roles).

---

## 3. Detectors

Every detector has a read-only probe, a severity, and a repair that always reads Chargebee.

### D1 — missing `chargebee_customer_id`

```sql
SELECT u.id, u.username
FROM users u
WHERE (u.chargebee_customer_id IS NULL OR u.chargebee_customer_id = '')
  AND EXISTS (SELECT 1 FROM customer_entity c WHERE c.phone = u.username);
```

- **Severity:** critical (gap C1).
- **Repair:** Chargebee `customer.list(phone)` → exactly one → set the link; zero → leave; two or more
  → **conflict**, never guess.
- **Frequency:** hourly for touched users, nightly for all.

### D2 — duplicate customers (one person, two records)

```sql
SELECT phone, COUNT(*) AS n, GROUP_CONCAT(customer_id) AS ids
FROM customer_entity
WHERE phone IS NOT NULL AND phone <> ''
GROUP BY phone HAVING n > 1;
```

- **Severity:** high. Baseline: 43 numeric-keyed vs 38 Chargebee-keyed.
- **Repair:** choose the canonical id — the one referenced in `users.chargebee_customer_id`, else the
  one with active subscriptions, else the newest in Chargebee. Re-point child rows, retain the retired
  row as audit. **Never delete in an automated pass.**

### D3 — orphaned subscriptions (no reachable owner)

```sql
SELECT s.customer_id, COUNT(*) AS rows_, SUM(s.status='ACTIVE') AS active
FROM subscription_entity s
LEFT JOIN users u ON u.chargebee_customer_id = s.customer_id
WHERE u.id IS NULL
GROUP BY s.customer_id;
```

- **Severity:** high. Baseline: 4 ACTIVE rows (`505`, `506`, `507`, `601`) have no user.
- **Repair:** query Chargebee per subscription id.
  - exists → reconstruct the customer, attempt a link by phone/email; if no BMJ user exists, keep the
    row and flag `no_local_user`.
  - 404 → mark `ORPHANED(chargebee_gone)`, retain, exclude from read paths.
- **Never delete** — this may be revenue requiring refunds.

### D4 — mismatched customer ids (the migration class)

```sql
SELECT u.id, u.username, u.chargebee_customer_id, s.id AS sub_id, s.customer_id AS stored_key
FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> s.customer_id;
```

- **Severity:** critical. Baseline: 11 rows, 9 ACTIVE.
- **Repair:** re-key to `u.chargebee_customer_id` **only after** the same-person gate passes
  (`customer_entity[u.chargebee_customer_id].phone = u.username`), exactly as in
  `SUBSCRIPTION_MIGRATION_PLAN.md` Phase 1e.

### D5 — missing local records (Chargebee knows, BMJ does not)

- **Probe:** list Chargebee subscriptions with `updated_at > cursor`; check each id against
  `subscription_entity`.
- **Severity:** high — a paying customer is invisible.
- **Repair:** fetch and upsert the projection, ensure the customer row, then the identity link. This
  detector is what makes lost webhooks harmless.

### D6 — stale local state (both exist, they disagree)

| Field | Comparison | Repair |
|---|---|---|
| `status` | local vs Chargebee | take Chargebee |
| `billing_period`, `billing_period_unit` | local vs Chargebee | take Chargebee |
| `cancelled_at` | local null vs Chargebee set, or inverse | take Chargebee |
| `resource_version` | local < Chargebee | take Chargebee |
| customer `email` / `phone` | local vs Chargebee | take Chargebee |

- **Severity:** high — a cancelled plan still shown active becomes a billing dispute.
- **Repair:** overwrite mirror fields from Chargebee, then recompute derived BMJ fields
  (`nextDeliveryAt`). Never the reverse.

### D7 — failed or stuck webhook events

- **Probe:** `processing_status IN ('FAILED','PROCESSING')` with `processed_at` older than 15 min.
- **Severity:** medium — D5 may already have repaired the data, so this is a leading indicator.
- **Repair:** re-drive while `retry_count < 3`; beyond that, dead-letter and alert.

---

## 4. Repair actions — allowed writes

| Detector | May write | Must not |
|---|---|---|
| D1 | `users.chargebee_customer_id` | create users, edit credentials |
| D2 | child `customer_id` re-key; audit row | delete customers or subscriptions |
| D3 | status flag `ORPHANED`; audit row | deletion |
| D4 | `subscription_entity.customer_id` | touch `status` in the same pass |
| D5 | insert missing `customer_entity` / `subscription_entity` | invent ids |
| D6 | the mirror columns above | `delivery_schedule`, cart, `nextDeliveryAt` inputs |
| D7 | `webhook_events` status / retry_count | business tables directly |

Every repair writes a `sync_findings` row whether or not it succeeded, so runs stay auditable and
idempotent.

---

## 5. Hourly job

```
every 5 min : drainRetries()
                FAILED and retry_count < 3  -> re-run handler
                FAILED and retry_count >= 3 -> dead-letter + alert
                PROCESSING older than 15 min -> treat as FAILED (crash recovery)

every 60 min: hotCheck()
                D7  stuck events
                D1  users modified in last 24 h with null link
                D5  subscriptions updated at Chargebee in last 24 h vs local
                budget guard: stop before 500 API calls, resume next hour
```

Rationale: the expensive full sweep is unnecessary hourly; drift that matters is fresh drift.

---

## 6. Nightly job

```
02:00  start(run_id)
  1  identity pass      D1  every user with null/blank link          -> link or conflict
  2  duplicate pass     D2  group by phone, email                    -> choose canonical, re-key children
  3  subscription diff  D5  Chargebee list updated_at > cursor        -> upsert missing / drifted
  4  mismatch pass      D4  local rows on a numeric twin key          -> re-key behind same-person gate
  5  orphan pass        D3  local rows with no reachable owner        -> reconstruct / flag
  6  staleness pass     D6  field-level compare for touched rows      -> take Chargebee
  7  schedule sweep     abandoned delivery_schedule rows > 48 h       -> flag, do not delete
  8  cursor advance     store Chargebee high-water mark
  9  report             emit counts, durations, findings, failures
```

Ordering matters: identity (1, 2) before mismatch (4), because re-keying depends on a valid link.

**Cursor state** (only new storage this plan needs — two small tables, no changes to existing ones):

```
sync_cursor   ( job text PK, cursor_value text, high_water_mark text, updated_at timestamp )
sync_findings ( id PK, run_id text, detector text, severity text, subject text,
                action text, outcome text, detail text, created_at timestamp )
```

Both are additive and can be created without touching existing tables.

---

## 7. Manual repair

Operator-invoked, per subject, always dry-run first.

| Operation | Input | Effect | Safety |
|---|---|---|---|
| `relink(userId)` | BMJ user | D1 for one user, with full match trace | refuses on conflict; prints candidates |
| `requery(customerId)` | Chargebee customer | D5 + D6 for that customer's subscriptions | writes only mirror fields |
| `rekey(subscriptionId)` | local sub id | D4 for one row | refuses unless same-person gate passes |
| `replay(eventId)` | `webhook_events.event_id` | re-runs the handler idempotently | requires `--force` if already COMPLETED |
| `audit(userId)` | BMJ user | prints every identity fact: link, twins, rows, reachability | read-only |
| `sweep(dryRun)` | — | D3/Q for abandoned schedules | `dryRun` default **true** |

Every manual operation requires the operator to state the subject explicitly; there is no "repair all"
flag on the manual path — that is what the scheduled jobs are for.

---

## 8. Safety controls

| Control | Value | Why |
|---|---|---|
| Global dry-run switch | `SYNC_DRY_RUN=true` default on first deploy | prove the detector output before any write |
| Per-run row cap | 500 (hourly), 5 000 per phase (nightly) | bound blast radius |
| Per-run API cap | 500 / 20 000 | protect Chargebee rate limits |
| Concurrency | single leader per job (DB advisory lock) | prevent double-repair |
| Delete policy | **never** | all removals are operator actions |
| Ambiguity policy | stop and report | two matches is a data problem, not a coin flip |
| Kill switch | `SYNC_ENABLED=false` | disable all jobs without a deploy |

---

## 9. Run report and metrics

Every pass emits, and stores in `sync_findings`:

```
run_id, job, started_at, finished_at, duration_ms
counts: checked, matched, drifted, repaired, skipped, conflicts, failures
per detector: D1..D7 with sample subject ids
api_calls, rate_limit_hits
```

Metrics that must alert (see Phase 5 of the roadmap):

| Metric | Alert threshold |
|---|---|
| users with null link and subscriptions present | > 0 |
| rows on a numeric twin key | > 0 |
| orphan ACTIVE subscriptions | > 0 |
| FAILED events older than 15 min | > 0 |
| nightly run not completed by 04:00 | missing heartbeat |
| drift repaired per run | sudden >10× baseline |

---

## 10. Rollout of this plan

The reconciler is useless without the read-path fix, and dangerous without dry-run. Order:

1. **Read-path honesty first** (Phase 5 of the roadmap) — stops false empties immediately.
2. **Detectors in read-only mode** for one week — publish the findings, tune thresholds, confirm the
   numbers match `SUBSCRIPTION_DATA_CENSUS.md`.
3. **Repairs enabled one detector at a time** — D1, then D5, then D4, then D2, then D3/D6.
4. **Delete nothing** until six months of stable findings.


