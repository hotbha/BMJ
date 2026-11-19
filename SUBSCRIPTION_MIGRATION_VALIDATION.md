# Subscription Migration — Validation Review

**Date:** 2026-10-31
**Reviewed:** `SUBSCRIPTION_DATA_CENSUS.md`, `SUBSCRIPTION_MIGRATION_PLAN.md`
**Method:** read-only dry run (`python _captures/qa/sub_migration_dryrun.py`). **No migration SQL was executed. Nothing was written to the database.**
**Verdict:** root cause **CONFIRMED** · migration **SAFE with 3 amendments** · rollback **EXACT** · production impact **NOT YET KNOWABLE from this database**.

---

## 1. Root cause — confirmed

| Element | Evidence | Status |
|---|---|---|
| Two identity spaces exist | `users.chargebee_customer_id` (`16CS3UVZQtF20nFJ`) vs `subscription_entity.customer_id` (`504`) | confirmed |
| The FK target is `customer_entity.customer_id` (the PK) | `key_column_usage` → `subscription_entity.customer_id = customer_entity.customer_id` | confirmed |
| `/my` resolves by the Chargebee id | `getCustomerIdFromSecurityContext()` → `customerRepository.findById(customerId)` → `findByCustomer(subscription)` | confirmed (code read) |
| The rows sit on the numeric twin | dry run [1]: all 16 rows keyed `500/502/503/504/505/506/507/601` | confirmed |
| The result is a silent empty list | `200 {"status":"success","subscriptions":[]}` from `/my` | confirmed (API probe, users 502 & 504) |

**The duplicate-identity claim is now proven, not inferred.** Each migrating user has two `customer_entity` rows, and the one their subscriptions point at is **not the one that describes them**:

| user | login phone | numeric twin phone | Chargebee id | Chargebee twin phone |
|---|---|---|---|---|
| 502 | `9999999933` | `6666666666` ← junk | `169oAaVYQ0fXY5psP` | **`9999999933`** ✅ |
| 503 | `9876500002` | `3322332233` ← junk | `AzZZThVZQdBOqb3g` | **`9876500002`** ✅ |
| 504 | `9876543210` | `8989898989` ← junk | `16CS3UVZQtF20nFJ` | **`9876543210`** ✅ |

The Chargebee twin matches the login phone exactly in all three cases; the numeric twin does not. So re-keying moves rows onto **the record of the same person** — the single most important safety property, and it holds.

---

## 2. Exact SQL impact

Only one statement mutates business data. Its cardinality is known in advance:

```sql
UPDATE subscription_entity s
JOIN users u             ON s.customer_id = CAST(u.id AS CHAR)
JOIN customer_entity tgt ON tgt.customer_id = u.chargebee_customer_id
SET s.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> '';
```

| Measure | Value |
|---|---|
| Rows examined by the join | 16 |
| **Rows updated** | **11** |
| Rows matching but unchanged (idempotent no-op) | 1 (user 500, key already `500`) |
| Rows not matched — cohort B (owner cannot migrate) | **0** |
| Rows not matched — cohort C (no owner) | **4** |
| Columns modified | **1** (`subscription_entity.customer_id`) — no other column, no PK, no schema |
| ACTIVE rows that become visible to their owner | **9** |
| FK violations projected | **0** (gate [4] passes) |

The other phases touch nothing in business data: Phase 0 creates 3 snapshot tables, Phase 1 is `SELECT` only, Phase 2 updates 0 rows here (no Chargebee twin exists for user 500), Phase 4 copies 4 rows into a quarantine table, Phase 5 is code, Phase 6 reverts one debugging value.

---

## 3. Affected rows — every row, before → after

Dry run [1], verbatim. `tgt` = how many rows exist in `customer_entity` for the proposed key (must be ≥ 1).

| sub id | current key | status | user | login phone | proposed key | cohort | tgt |
|---|---|---|---|---|---|---|---|
| `16CRlVUlCHf5e3ra` | `500` | ACTIVE | 500 | 9999999911 | `500` | **no-op** | 1 |
| `Azq8hoUjJP8eh4Ju` | `502` | ACTIVE | 502 | 9999999933 | `169oAaVYQ0fXY5psP` | re-key | 1 |
| `Azq8hoUjJXAvH4kz` | `503` | CANCELLED | 503 | 9876500002 | `AzZZThVZQdBOqb3g` | re-key | 1 |
| `169zaaUjfmivz6Zc` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `169zfLUjkpLMhXsK` | `504` | CANCELLED | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `16BkznUjkpj7HaAd` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `16Bl9NUjdfsI11vpk` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `AzyfWOUjkpBJ0WQj` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `AzyyIFUoJiiuI138q` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `Azz2z6UjbTpOgiGF` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `Azz3qJUpKZ0Ir2QTC` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `AzZeDeUnjFNUr8RT` | `504` | ACTIVE | 504 | 9876543210 | `16CS3UVZQtF20nFJ` | re-key | 1 |
| `169zToUkPQwosGpr` | `505` | ACTIVE | — | — | — | **C: no owner** | 0 |
| `6oaWdUmxwHarix` | `506` | ACTIVE | — | — | — | **C: no owner** | 0 |
| `AzydsWUvHxQ8SDykz` | `507` | ACTIVE | — | — | — | **C: no owner** | 0 |
| `16CRexUiMXmQzFHL` | `601` | ACTIVE | — | — | — | **C: no owner** | 0 |

## 4. Before → after, per customer

| current key | rows | active | after key | end state |
|---|---:|---:|---|---|
| `500` | 1 | 1 | `500` (unchanged) | stays reachable **only** while the local repair exists → depends on Phase 5 |
| `502` | 1 | 1 | `169oAaVYQ0fXY5psP` | `/my` returns 1 ✅ |
| `503` | 1 | 0 | `AzZZThVZQdBOqb3g` | `/my` returns 1 (CANCELLED) ✅ |
| `504` | 9 | 8 | `16CS3UVZQtF20nFJ` | `/my` returns 9 ✅ |
| `505` | 1 | 1 | — | quarantined, no owner |
| `506` | 1 | 1 | — | quarantined, no owner |
| `507` | 1 | 1 | — | quarantined, no owner |
| `601` | 1 | 1 | — | quarantined, no owner |

## 5. Post-state projection

| | before | after |
|---|---:|---:|
| ACTIVE rows visible to their owner | 1 | **10** |
| ACTIVE rows hidden by a key mismatch | 9 | **0** |
| ACTIVE rows with no owner | 4 | **4** (quarantined, unchanged by design) |
| Affected users (own subs, API returns 0) | 3 | **0** |

---

## 6. Migration safety — three amendments required before approval

Validating the plan against the dry run surfaced three real defects *in the plan*. All are plan corrections; none is implemented.

### A1 — Phase 2's phone join is non-deterministic (remove or harden)

```sql
-- as written in the plan
UPDATE users u
JOIN customer_entity c ON c.phone = u.username AND c.customer_id NOT REGEXP '^[0-9]+$'
SET u.chargebee_customer_id = c.customer_id
```

If two Chargebee customers share a phone, the join fans out and MySQL applies **whichever row it reads last** — there is no `LIMIT` and no uniqueness guard. Duplicate contacts already exist in this data (`1010101010@gail.com` sits on both `500` and `502`). A production run could bind a user to a stranger's customer id, after which Phase 3 would migrate their subscriptions to that stranger.

**Amendment:** drop Phase 2 (it is a no-op here) and let Phase 5 serve cohort B, or require a unique match:

```sql
UPDATE users u
JOIN (SELECT phone, MAX(customer_id) AS customer_id, COUNT(*) AS n
      FROM customer_entity WHERE customer_id NOT REGEXP '^[0-9]+$'
      GROUP BY phone HAVING n = 1) c
  ON c.phone = u.username
SET u.chargebee_customer_id = c.customer_id
WHERE u.chargebee_customer_id IS NULL OR u.chargebee_customer_id = '';
```

### A2 — Phase 3 has no same-person gate

Phase 3 trusts `users.chargebee_customer_id` blindly. If that column were wrong, subscription rows would move to another person's account — a data-leak-shaped failure, not merely a display bug.

**Amendment:** add a preflight that every migrating user's Chargebee twin matches their login identity, and abort the run if any user fails:

```sql
SELECT u.id, u.username, u.chargebee_customer_id, c.phone AS twin_phone, c.email AS twin_email
FROM users u
JOIN customer_entity c ON c.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id <> ''
  AND c.phone <> u.username
  AND NOT (c.email = u.username);
-- expect 0 rows; any row stops the migration
```

This run: **0 rows** (dry run [5]) — the gate passes here, and it is the check that makes the migration defensible in production.

### A3 — ordering hazard between Phase 5 and Phase 6

User 500 is cohort B: no Chargebee twin exists, so it cannot be re-keyed here. It renders correctly **only** because `users.chargebee_customer_id = '500'` (a debugging artifact). If Phase 6 (revert) runs before Phase 5 (resolver hardening) is live, **user 500 goes dark again**.

**Amendment:** **Phase 5 must deploy before Phase 6**, in a separate change window, with a re-check of `/my` for user 500.

### Minor documentation corrections

- Validation V1 (`JOIN users ON s.customer_id = CAST(u.id AS CHAR)` expecting 0) cannot detect leftovers in cohort C, because ownerless rows never join to a user. **V3** is the assertion covering C; the plan should say so.
- Phase 4's `CREATE TABLE … AS SELECT s.*` yields a snapshot without PK/FK — fine for audit, never for runtime.

---

## 7. Rollback safety — exact

| Property | Finding |
|---|---|
| What changes | `subscription_entity.customer_id` **only** |
| Primary key | `subscription_entity.id` — **present** (verified: 37 columns, `id` first), never modified |
| Backup | Phase 0 `subscription_entity_bak_20261031`, full copy with PK |
| Restore | `UPDATE subscription_entity s JOIN …_bak_20261031 b ON b.id = s.id SET s.customer_id = b.customer_id;` — deterministic, row-for-row |
| FK side effects | none — `customer_entity` is untouched, so a rollback cannot orphan anything |
| Quarantine | copy-only; dropping it reverts nothing else |
| Point of no return | **none** — every phase reverses from the Phase 0 snapshot |

**Verdict: safe and exact**, provided Phase 0 runs first and the snapshot is retained until acceptance.

Caveat: the backup is a table copy, not a transaction log. A subscription written by a webhook *after* the migration but *before* a rollback is preserved by key, but its `customer_id` would only be restored if that `id` existed in the snapshot. Close the rollback window before resuming traffic.

---

## 8. Production impact — honest limits

| Question | Answer |
|---|---|
| Can production numbers be stated now? | **No.** Every figure here is from `bmj-smoke-mysql`, a QA database with 6 users. |
| Is the structural defect production-real? | **Yes** — the code path is production code and answers `200 + []` on a mismatch. |
| Would production users see "No subscription yet"? | **Only where the two keys disagree.** If production writes through `SubscriptionMapper` (Chargebee id) and `users.chargebee_customer_id` is populated, the read matches and users are fine. The failure needs a mismatch — normal in this dataset (43 of 81 customers numeric), possibly rare in production. |
| What must be measured first | Phase 1 against a **production replica**: `will_move`, `blockers`, `target_exists`, `ownerless`. Approval is decided on those four numbers, not on this document. |
| Worst realistic case | Every user whose subscriptions predate the Chargebee id sees an empty subscription screen — silent, and indistinguishable from "never subscribed". |

So: **severity is confirmed, prevalence is not.** Prevalence is four queries away.

---

## 9. Go / no-go

| Gate | Status |
|---|---|
| Root cause proven | ✅ |
| Exact SQL impact known | ✅ 11 rows, 1 column |
| Every affected row enumerated with before/after | ✅ 16 of 16 |
| Same-person mapping proven | ✅ login phone = twin phone, 3 of 3 |
| FK safety gate passes with 0 violations | ✅ |
| Rollback exact and reasoned through | ✅ |
| Amendments A1–A3 folded into the plan | ⏳ **required before execution** |
| Phase 1 numbers from a production replica | ⏳ **required before production** |
| Application validation (Home / Subscription render) | ⏳ **blocked — no device connected** |

**Recommendation: approve Phase 5 only** — the resolver hardening. It is code, independently revertible, and immediately stops the silent empty answer. Hold Phases 0–4 until A1–A3 are folded in and Phase 1 has run against a production replica. Nothing should be executed against production on the strength of a smoke database.

---

## 10. Reproduction

```
python _captures/qa/sub_census.py                 # census numbers
python _captures/qa/sub_migration_dryrun.py       # the tables in this document
python _captures/qa/sub_identity_probe.py <phone> # live API behaviour per user
```

All three are read-only; none writes to the database.


