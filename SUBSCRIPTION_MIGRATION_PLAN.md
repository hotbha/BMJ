# Subscription Identity — Migration Plan

**Status:** design only. **Nothing implemented, nothing executed.** Awaiting approval.
**Inputs:** `SUBSCRIPTION_IDENTITY_AUDIT.md`, `SUBSCRIPTION_DATA_CENSUS.md`.
**Scope:** server + data. No client, UI, material or token change.

---

## 1. Root cause

A person is represented by **two different keys**, and the read path and the write path disagree about which one is authoritative.

| Layer | Uses | Example |
|---|---|---|
| `users.chargebee_customer_id` | Chargebee-generated id | `16CS3UVZQtF20nFJ` |
| `customer_entity.customer_id` | **either** a local user id **or** a Chargebee id — 43 numeric of 81 | `504` **and** `16CS3UVZQtF20nFJ` |
| `subscription_entity.customer_id` | FK → `customer_entity.customer_id`; in this data always the **numeric** twin | `504` |
| `SubscriptionController.getCustomerIdFromSecurityContext()` | returns the **Chargebee** id when `users.chargebee_customer_id` is set | `16CS3UVZQtF20nFJ` |
| `SubscriptionMapper.toEntity()` (the only writer) | uses the **Chargebee** id | `16CS3UVZQtF20nFJ` |

`/api/subscriptions/my` therefore resolves *customer `16CS3UVZQtF20nFJ`*, whose subscription list is empty, while the nine subscriptions sit on *customer `504`* — the same human, a different record.

Three distinct defects fall out:

- **D1 — duplicate identity.** One person, two `customer_entity` rows, no link between them. 43 of 81 customers are in the numeric space.
- **D2 — silent empty result.** `/my` answers `200 {"status":"success","subscriptions":[]}` for a user who has subscriptions. The client cannot tell "no plan" from "identity mismatch", so it renders the empty state truthfully-looking and wrongly.
- **D3 — write/read convention drift.** The writer keys by Chargebee id, the existing rows are keyed numerically. Whichever way one side moves, the other must move with it.
- Contributing: rows for `505/506/507/601` have **no owning user** — the resolver can never reach them, and nothing reports them.

## 2. Design decision

**Align storage to the Chargebee id** (Option A) rather than teaching the read path to use numeric keys (Option B).

Why A: `SubscriptionMapper` already writes Chargebee ids, Chargebee is the system of record for subscriptions, and Option B would leave two live conventions that break as soon as real webhook data arrives. Option B is retained only as a *transitional read-path safety net* (§3, Phase 5) for the cohort that cannot be migrated yet.

Three cohorts, handled differently:

| Cohort | Members here | Treatment |
|---|---|---|
| **A — migratable** | 502, 503, 504 | rows re-keyed from numeric id → their `chargebee_customer_id` (target `customer_entity` row verified to exist) |
| **B — unmigratable** | 500 (no Chargebee-keyed customer row) | cannot be re-keyed without a Chargebee lookup; covered by the Phase 5 resolver fallback, then backfilled later |
| **C — ownerless** | 505, 506, 507, 601 | never reachable; quarantined and reported, not silently deleted |

---

## 3. Migration SQL

### Phase 0 — backup (mandatory, before anything)

```sql
CREATE TABLE subscription_entity_bak_20261031 AS SELECT * FROM subscription_entity;
CREATE TABLE customer_entity_bak_20261031    AS SELECT * FROM customer_entity;
CREATE TABLE users_bak_20261031              AS SELECT id, username, chargebee_customer_id FROM users;
```

### Phase 1 — preflight (read-only; every query must satisfy its expectation)

```sql
-- 1a. how many rows will move
SELECT COUNT(*) AS will_move
FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
JOIN customer_entity c ON c.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> '';
-- expect 11 (500:1 + 502:1 + 503:1 + 504:9, less the cohort-B row for 500)

-- 1b. blockers: rows whose owner has no Chargebee id (cannot move)
SELECT u.id, u.username, COUNT(s.id) AS stuck_rows
FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.chargebee_customer_id IS NULL OR u.chargebee_customer_id = ''
GROUP BY u.id, u.username;
-- expect 500 -> 1   (cohort B)

-- 1c. FK safety: every target customer row must already exist
SELECT u.id, u.chargebee_customer_id,
       (SELECT COUNT(*) FROM customer_entity c WHERE c.customer_id = u.chargebee_customer_id) AS target_exists
FROM users u
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> '';
-- every target_exists must be >= 1

-- 1d. ownerless rows
SELECT s.customer_id, COUNT(*) AS rows_no_owner
FROM subscription_entity s
LEFT JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.id IS NULL
GROUP BY s.customer_id;
-- expect 505, 506, 507, 601
```

**Do not run Phase 3 if 1c returns any `target_exists = 0`.**

**Also do not run Phase 3 if this returns any row** (same-person gate, added per `SUBSCRIPTION_MIGRATION_VALIDATION.md` §6 A2):

```sql
-- 1e. every migrating user's Chargebee twin must describe the SAME person
SELECT u.id, u.username, u.chargebee_customer_id, c.phone AS twin_phone, c.email AS twin_email
FROM users u
JOIN customer_entity c ON c.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> ''
  AND c.phone <> u.username
  AND NOT (c.email = u.username);
-- expect 0 rows; any row is a stop-the-migration condition
```

### Phase 2 — backfill the identity column (cohort B preparation)

> **AMENDED (see `SUBSCRIPTION_MIGRATION_VALIDATION.md` §6 A1).** The original join
> `ON c.phone = u.username` is non-deterministic when two customers share a phone — duplicate
> contacts already exist here. It is replaced with a uniqueness-guarded version. This phase
> updates **0 rows** in this environment and may be skipped entirely.

```sql
-- only where EXACTLY ONE Chargebee-keyed customer row matches the login phone
UPDATE users u
JOIN (SELECT phone, MAX(customer_id) AS customer_id, COUNT(*) AS n
      FROM customer_entity
      WHERE customer_id NOT REGEXP '^[0-9]+$'
      GROUP BY phone
      HAVING n = 1) c
  ON c.phone = u.username
SET u.chargebee_customer_id = c.customer_id
WHERE u.chargebee_customer_id IS NULL OR u.chargebee_customer_id = '';
-- in this environment: 0 rows (no Chargebee twin exists for user 500) — safe no-op
```

If 500 still has no twin afterwards it stays in cohort B and is served by Phase 5.

### Phase 3 — re-key subscription rows (single transaction)

```sql
START TRANSACTION;

UPDATE subscription_entity s
JOIN users u             ON s.customer_id = CAST(u.id AS CHAR)
JOIN customer_entity tgt ON tgt.customer_id = u.chargebee_customer_id
SET s.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL
  AND u.chargebee_customer_id <> '';

COMMIT;
```

Idempotent: after a row moves, `JOIN users ON s.customer_id = CAST(u.id AS CHAR)` no longer matches it, so a re-run is a no-op.

### Phase 4 — quarantine ownerless rows (no deletion)

```sql
CREATE TABLE subscription_orphan_20261031 AS
SELECT s.* FROM subscription_entity s
LEFT JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.id IS NULL;

SELECT COUNT(*) FROM subscription_orphan_20261031;
```

They are counted and reported; deletion needs a separate, explicit decision.

### Phase 5 — resolver hardening (code; separate commit, shippable alone)

1. `/my` must not answer `200 + []` when the resolved customer row has no subscriptions **and** a numeric twin exists for this user — try the numeric key before declaring empty.
2. When the resolver returns `null`, answer `409 "customer identity not linked"` rather than `401 "User not authenticated"` — the user *is* authenticated; the linkage is what is missing.
3. Emit a counter/log each time the fallback is taken, so the remaining cohort stays measurable.

### Phase 6 — revert the local repair

After A/B are handled, set user 500's `chargebee_customer_id` back to its true Chargebee value (or keep the numeric key only if Phase 5 is what serves it). The `'500'` value in the database today is a debugging artifact and must not be mistaken for production truth.

> **ORDERING CONSTRAINT (added per `SUBSCRIPTION_MIGRATION_VALIDATION.md` §6 A3).** User 500 is
> cohort B — no Chargebee twin exists, so its rows cannot be re-keyed. It renders correctly *only*
> because of the local repair. **Phase 5 must be deployed and verified before Phase 6 runs**,
> otherwise user 500 goes dark again.

---

## 4. Rollback plan

| Phase | Rollback | Data loss risk |
|---|---|---|
| 0 | drop the three `*_bak_20261031` tables | none |
| 2 (identity backfill) | `UPDATE users u JOIN users_bak_20261031 b ON b.id=u.id SET u.chargebee_customer_id=b.chargebee_customer_id;` | none — original values preserved |
| 3 (re-key) | `UPDATE subscription_entity s JOIN subscription_entity_bak_20261031 b ON b.id=s.id SET s.customer_id=b.customer_id;` | none — `id` is the primary key and is untouched |
| 4 (quarantine) | drop `subscription_orphan_20261031` | none — it is a copy, source rows untouched |
| 5 (code) | revert the commit; behaviour returns to today's | none |

Phase 3 is exactly reversible because the migration changes **only** `customer_id`; every other column and the primary key stay identical, so a row-for-row restore is always possible from the backup table.

---

## 5. Validation plan

### 5.1 Database assertions (all must pass)

```sql
-- V1: no subscription row still references a numeric id that is a local user id
SELECT COUNT(*) FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR);          -- expect 0 for cohorts A+B

-- V2: every remaining row references an existing customer
SELECT COUNT(*) FROM subscription_entity s
LEFT JOIN customer_entity c ON c.customer_id = s.customer_id
WHERE c.customer_id IS NULL;                                  -- expect 0

-- V3: no ACTIVE subscription is unreachable by its owner
-- (run after Phase 4; ownerless rows are legitimately excluded)
SELECT COUNT(*) FROM subscription_entity s
LEFT JOIN users u ON u.chargebee_customer_id = s.customer_id
LEFT JOIN subscription_orphan_20261031 o ON o.id = s.id
WHERE s.status='ACTIVE' AND u.id IS NULL AND o.id IS NULL;    -- expect 0
```

### 5.2 API assertions (per cohort)

| Check | Command | Expected |
|---|---|---|
| 502 sees 1 | `python _captures/qa/sub_identity_probe.py 9999999933` | `count=1` |
| 503 sees 1 (CANCELLED) | `python _captures/qa/sub_identity_probe.py 9876500002` | `count=1` |
| 504 sees 9 (8 ACTIVE) | `python _captures/qa/sub_identity_probe.py 9876543210` | `count=9` |
| 500 still sees 1 | `python _captures/qa/sub_identity_probe.py 9999999911` | `count=1` |
| a user with none | `python _captures/qa/sub_identity_probe.py 9999999901` | `count=0` |

`python _captures/qa/sub_census.py` must then report **AFFECTED = 0**.

### 5.3 Application assertions (needs a device — currently unavailable)

- Home renders the Active Subscription card with plan name and delivery count.
- Subscription tab renders the plan card with Modify / Pause / Cancel.
- No `409` surfaces for a linked user.

### 5.4 Regression

`flutter test` (418) and `mvn -o compile`, plus the three DB-backed tests in §6.

---

## 6. Risk assessment

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | FK violation on re-key (`customer_entity` target missing) | Low | migration aborts | Phase 1c gate; single transaction, so a failure applies nothing |
| 2 | A row moves to the wrong person (bad `chargebee_customer_id`) | Low | cross-account data exposure | review 1a/1b output; `users_bak` restores exactly; spot-check the four affected accounts before commit |
| 3 | 43 numeric `customer_entity` twins left orphaned and referenced by other tables | Medium | confusing duplicates, stale order/invoice links | migration touches **only** subscription keys and deletes no customers; audit `order_entity`, `invoice_entity`, `payment_entity`, `charge_entity`, `delivery_schedule`, `bottle_transactions` for numeric keys before any cleanup |
| 4 | Ownerless rows (505–507, 601) belong to deleted accounts with live billing | Medium | revenue/state invisible | quarantine table + report; no deletion; decide against Chargebee as source |
| 5 | The Phase 5 fallback becomes permanent and hides the drift | Medium | two conventions survive forever | log a counter and review it; schedule Phases 2–3 rather than relying on the fallback |
| 6 | The local repair (`'500'`) is mistaken for real data in later reviews | High — already happened once | wrong conclusions | Phase 6 explicit revert; recorded in the census doc |
| 7 | Production split differs from this dataset | Medium | plan under-scoped | run Phase 1 against a production replica first; the plan is gated on those numbers, not on this data |

**Blast radius:** `subscription_entity` (16 rows here) and `users.chargebee_customer_id` (6 rows). No schema change, no column drop, no other table written.

---

## 7. Impact estimate (Task 3)

| Measure | Value |
|---|---|
| Users who see "No subscription yet" despite owning subscriptions | **3** (502, 503, 504) |
| — of which hold ACTIVE subscriptions | **2** (502, 504) |
| ACTIVE rows hidden from their owners | **9** |
| ACTIVE rows with no owner at all | **4** |
| ACTIVE rows currently visible | **1 of 14 (7 %)** |
| Affected share of users who own subscriptions | **75 %** (3 of 4) |
| Affected share of all users | **50 %** (3 of 6) |

Both shapes are present — an owner who sees nothing (D2) and rows with no owner at all — so the fix must handle both, not only the re-keying.

---

## 8. Execution order (after approval only)

1. Run Phase 0 + Phase 1 against a **production replica**; publish the numbers.
2. Approve cohort treatment (A re-key, B fallback-then-backfill, C quarantine).
3. Ship Phase 5 (code) — smallest, independently revertible, fixes D2 immediately.
4. Run Phases 0–4 on staging; execute §5.1 and §5.2.
5. Repeat on production in a maintenance window; §5.1 then §5.2.
6. Phase 6 revert of the local repair, then re-baseline the census.
7. Only then resume the Stitch review on a subscriber state that is genuinely correct.

---

## 9. Explicitly out of scope

- No client, UI, material-system or token change.
- No schema change (no new columns; a `users.id ↔ chargebee_customer_id` mapping column is a *possible* future refinement, not part of this plan).
- Deleting numeric `customer_entity` twins — deliberately deferred, because other tables may reference them.
- Fixing AutoLogin.



