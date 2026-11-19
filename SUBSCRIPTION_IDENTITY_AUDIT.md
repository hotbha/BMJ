# Subscription Identity Audit

**Date:** 2026-10-31
**Scope:** read-only investigation. No code was changed, no data was changed by this audit.
**Question:** can a real user hold an ACTIVE subscription and still see the empty state?

**Answer: yes — demonstrated twice, on unmodified accounts, via the live API.**

> **CORRECTION (superseded by `SUBSCRIPTION_DATA_CENSUS.md`).** Two queries in §1–§3 used a non-existent
> `customer_entity.id` column. The key column is `customer_id`, and **43 of the 81 customer rows are
> numeric-keyed**, i.e. the same person exists twice. The defect described below is therefore *duplicate
> identity*, not a *missing bridge*; the observed symptom and the production impact are unchanged.
> Read the census document for the corrected numbers.


---

## 1. Observed schema

Two different identifiers exist for the same person, and they are stored in different places.

| Table | Column | Holds | Example |
|---|---|---|---|
| `users` | `id` | BMJ's own user id (BIGINT) | `500` |
| `users` | `chargebee_customer_id` | Chargebee's customer id (VARCHAR, nullable) | `169oAaVYQ0fXY5psP`, or `NULL` |
| `subscription_entity` | `customer_id` | FK → `customer_entity.id` | `500` (local) or `169oAaVYQ0fXY5psP` (Chargebee) |
| `customer_entity` | `id` | Chargebee customer id (81 rows; **no row is keyed by a local user id**) | `16CS3UVZQtF20nFJ` |

Measured state of the environment:

```
subscription_entity by customer_id:  504→9 rows  ·  500→1  ·  502→1  ·  503→1  ·  505/506/507/601→1 each
users:                               6 rows, 2 of them with chargebee_customer_id NULL
customer_entity:                     81 rows, none with id in ('500','502','503','504','505','506','507','601')
```

So the stored subscription rows are keyed by **local user id**, while `customer_entity` is keyed by **Chargebee id**.

---

## 2. Current lookup behaviour

`SubscriptionController.getCustomerIdFromSecurityContext()` (line 344) resolves the key in this order:

1. `user.getChargebeeCustomerId()` — if set, **return it**.
2. Otherwise `customerRepository.findById(localId.toString())` — return that row's id.
3. Otherwise `logger.error("No Chargebee customer ID found for local user: {}")` and **return `null`**.

The result is then passed to `subscriptionService.findByCustomerId(key)`.

Consequences of that chain:

| Situation | Key passed to the query | Matches stored rows? | UI |
|---|---|---|---|
| `chargebee_customer_id` set **and** rows keyed by Chargebee id (what `SubscriptionMapper` writes) | Chargebee id | ✅ | correct |
| `chargebee_customer_id` set, rows keyed by local id | Chargebee id | ❌ | **empty state** |
| `chargebee_customer_id` NULL, `customer_entity` has a row keyed by local id | local id | ✅ | correct |
| `chargebee_customer_id` NULL, no such `customer_entity` row (**the real state here**) | `null` | ❌ | **empty state** |

The write path, for the record, is `SubscriptionMapper.toEntity`: it deliberately ignores the commented-out
`entity.setCustomerId(chargebeeSubscription.customerId())` and instead does
`entity.setCustomer(CustomerMapper.fromId(customerId))`, i.e. it keys rows by the **Chargebee** customer id.

---

## 3. Mismatch analysis — reproduced, not inferred

Live API calls (dev OTP, read-only GETs). Nothing was repaired for these two accounts.

| Account | `users.chargebee_customer_id` | Rows in `subscription_entity` | `/api/subscriptions/my` returned |
|---|---|---|---|
| `9876543210` (user 504) | `16CS3UVZQtF20nFJ` | **9 rows, 8 ACTIVE** | **`count=0`** |
| `9999999933` (user 502) | `169oAaVYQ0fXY5psP` | **1 row, 1 ACTIVE** | **`count=0`** |
| `9999999911` (user 500) | **`500`** ← set by me earlier | 1 row, ACTIVE | `count=1` ✅ |

Reproduce with: `python _captures/qa/sub_identity_probe.py 9876543210`

Two distinct defects fall out of this:

- **D1 — identity not linked ⇒ silent empty list.** When `chargebee_customer_id` is NULL the resolver's fallback depends on a `customer_entity` row whose id equals the *local* id. No such row exists in this database (0 of 81). The resolver therefore returns `null`, `findByCustomerId(null)` returns an empty list, and the client shows "No subscription yet" — for a user who has one. This is a genuine code-level defect: it is the only bridge between the two id spaces, and it does not bridge them.
- **D2 — rows keyed by the wrong id space ⇒ unreachable rows.** Subscription rows stored under a local user id can never be found by a lookup that keys on the Chargebee id. Nine rows for user 504 are simply unreachable through the API.

**Was the repair of user 500 necessary?** Yes, but it is a **mask, not a fix.** It worked only because it changed the *lookup key* to equal the *seeded row key* (`500`). It makes one account display correctly and leaves the underlying disagreement in place. It should be reverted once the real fix lands, or kept only as a documented local-test shim.

**Origin of the local-id keyed rows:** the only Java path that constructs a `SubscriptionEntity` is `SubscriptionMapper`, which uses the Chargebee id — so these rows were not written by that path. No `INSERT INTO subscription_entity` exists in any tracked `.sql`/`.py`. The rows are therefore out-of-band seed data. Confidence on that specific point: **medium** (absence of a writer in tracked code, but the writer could be untracked or a manual edit).


---

## 4. Production impact

| # | Impact | Severity | Evidence |
|---|---|---|---|
| 1 | A user with an active subscription sees **"No subscription yet"** and the Browse-plans CTA | **High — user-visible, money-related** | proven on 2 accounts |
| 2 | The failure is **silent to the client**: HTTP 200, `{"status":"success","subscriptions":[]}`. The app cannot distinguish "no subscription" from "identity not linked" | **High** | API response shape |
| 3 | Every consumer of the same resolver inherits the fault (delivery schedule `reserve`, bottle ledger, modify/pause/cancel routes), because they all call `getCustomerIdFromSecurityContext()` | **High** | `SubscriptionController` line 344 callers |
| 4 | Rows written under a local id are unreachable — billing state exists but is invisible to support tooling that reads through the API | **Medium** | 9 unreachable rows |
| 5 | Only a server log line (`logger.error("No Chargebee customer ID found…")`) records the failure; no metric, no alert | **Medium** | resolver code |

Real users can therefore experience **Active subscription + empty-state UI**, and the most likely trigger is any signup/login path that does not persist `chargebee_customer_id` (the OTP path, and any historical Google/legacy row).

---

## 5. Recommended fix (not implemented — for approval)

Smallest-first; each step independently shippable.

1. **Close the silent-empty path (smallest, highest value).** When the resolver returns `null`, respond `409/428` with an explicit "customer identity not linked" reason instead of `200 + []`. The app can then say "we couldn't load your plan" rather than lying with an empty state. One method, ~10 lines, no migration.
2. **Make the identifier mandatory at the boundary.** Every auth path that creates or logs in a user must persist `chargebee_customer_id` (create the Chargebee customer if missing). Backfill existing `NULL`s from `customer_entity` by email/phone.
3. **One-time data migration.** For each `subscription_entity` row whose `customer_id` equals a local `users.id`, rewrite it to that user's `chargebee_customer_id`. Run in a transaction, with a dry-run count first.
4. **Replace the fallback with an explicit resolution** (local user → its `chargebee_customer_id`, else create/fetch the Chargebee customer) and delete the `customer_entity`-by-local-id guesswork.
5. **Regression tests** against a real DB: (a) linked user with rows ⇒ rows returned; (b) unlinked user ⇒ explicit error, never `[]`; (c) `NULL` id never reaches the repository.

Belt-and-braces: assert in the repository layer that the id passed to `findByCustomerId` is non-null, so a future caller cannot silently produce an empty result.

---

## 6. Confidence

| Claim | Confidence | Basis |
|---|---|---|
| Active subscription + empty state is reachable | **High** | reproduced on users 504 and 502 through the live API |
| Root cause is the id-space disagreement (Chargebee id vs local id) | **High** | code path + schema + measured rows agree |
| `chargebee_customer_id = NULL` always yields an empty list here | **High** | fallback requires a `customer_entity` row keyed by local id; 0 exist |
| Rows were written out-of-band (seed data), not by `SubscriptionMapper` | **Medium** | no writer for local-id keys in tracked code; writer could be untracked |
| The same fault reaches modify/pause/cancel and delivery reserve | **High** | they share the resolver, verified callers |
| User 500's repair is a mask | **High** | it changed only the lookup key, not the storage convention |

---

## 7. State of the environment

- User 500 (`9999999911`) still carries the earlier local repair (`chargebee_customer_id = '500'`), which is why that one account can render a plan. Users 502 and 504 remain unrepaired and would show empty states.
- No code, token, material or UI change was made in this audit. The only artifact added is the read-only probe `_captures/qa/sub_identity_probe.py`.
