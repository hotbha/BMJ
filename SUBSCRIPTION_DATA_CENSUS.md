# Subscription Data Census

**Date:** 2026-10-31
**Database:** `bmj-smoke-mysql` (container, `DB_NAME` from `.env`)
**Method:** read-only SQL. Regenerate with `python _captures/qa/sub_census.py`.

> **Correction to `SUBSCRIPTION_IDENTITY_AUDIT.md`.** That document stated "0 of 81 `customer_entity` rows are keyed by a local user id". That was **wrong** — the query used a non-existent `id` column and silently returned nothing. The key column is `customer_id`, and **43 of 81 customer records are numeric-keyed**. The defect is therefore not "a missing bridge" but **duplicate customer identities**: the same person exists twice, under two keys. Everything below reflects the corrected measurement.

---

## 1. Subscription rows

| Metric | Value |
|---|---|
| Total subscription rows | **16** |
| — ACTIVE | **14** |
| — CANCELLED | **2** |
| Distinct `customer_id` keys | **8** (`500, 502, 503, 504, 505, 506, 507, 601` — all numeric) |
| Rows keyed by a Chargebee-generated id | **0** |

## 2. Row classification by id space

| Classification | Rows | Notes |
|---|---:|---|
| On a **dual-space numeric key** (the id is both a `users.id` and a `customer_entity.customer_id`) | **12** | `500`×1, `502`×1, `503`×1, `504`×9 |
| On a **numeric customer with no owning user** | **4** | `505`, `506`, `507`, `601` — all ACTIVE, no user row exists |
| On a **local user id with no customer record** | 0 | — |
| On a **Chargebee id** | 0 | the write path's convention is unused in this data |
| True orphans (no user, no customer) | 0 | — |

**Rows unreachable through `/api/subscriptions/my`: 13 of 16** (all except the single row for user 500).

## 3. Customer records — the duplicate identity space

| Metric | Value |
|---|---|
| `customer_entity` rows | **81** |
| — numeric-keyed (`^[0-9]+$`) | **43** |
| — Chargebee-keyed | **38** |

The same person appears twice, e.g.:

| `customer_id` | phone | email | first name |
|---|---|---|---|
| `502` | 6666666666 | 1010101010@gail.com | bharat |
| `169oAaVYQ0fXY5psP` | 9999999933 | e2e.signup.20261018@example.com | E2E |
| `504` | 8989898989 | 8989898989@gail.com | bharat |
| `16CS3UVZQtF20nFJ` | 9876543210 | qa.sub.probe@bookmyjuice.test | QA |

The numeric rows carry junk/placeholder contacts; the Chargebee-keyed rows carry the contacts the real signup flow created. Subscription rows point at the **numeric** twin; `users.chargebee_customer_id` points at the **Chargebee** twin.

## 4. Affected users

Resolver simulated exactly as `SubscriptionController.getCustomerIdFromSecurityContext()` does it, then `/my` does `findByCustomer(customer_entity[key])`.

| user | phone | `chargebee_customer_id` | rows owned | ACTIVE owned | resolver key | rows reachable | UI |
|---|---|---|---:|---:|---|---:|---|
| 502 | 9999999933 | `169oAaVYQ0fXY5psP` | 1 | **1** | `169oAaVYQ0fXY5psP` | **0** | **"No subscription yet"** |
| 503 | 9876500002 | `AzZZThVZQdBOqb3g` | 1 | 0 | `AzZZThVZQdBOqb3g` | **0** | **"No subscription yet"** |
| 504 | 9876543210 | `16CS3UVZQtF20nFJ` | **9** | **8** | `16CS3UVZQtF20nFJ` | **0** | **"No subscription yet"** |
| 500 | 9999999911 | `500` *(local repair)* | 1 | 1 | `500` | 1 | correct ✅ |

Plus **4 ACTIVE rows** (`505, 506, 507, 601`) that belong to **no user at all** — billing state with no owner.

## 5. Reachability summary

| | rows | ACTIVE |
|---|---:|---:|
| Reachable through the API | 1 | 1 |
| Unreachable — owner exists but key mismatch | 11 | 9 |
| Unreachable — no owner at all | 4 | 4 |
| **Total** | **16** | **14** |

**1 of 14 ACTIVE subscriptions (7 %) is visible to its owner.**

## 6. Answer to "how many users see 'No subscription yet' despite having subscriptions?"

**3 users** — 502, 503, 504.

- 2 of them (502, 504) currently hold **ACTIVE** subscriptions: **9 active rows hidden from their owners**.
- As a share of the population that owns any subscription: **3 of 4 = 75 %**.
- As a share of all users in the database: **3 of 6 = 50 %**.

The only correctly-rendering subscriber (500) renders correctly **because of the local data repair**, not because the model works.

## 7. Caveats

- This is the local smoke database, populated largely by QA/E2E flows, so absolute counts are small. The *structure* — two identity spaces, 43 of 81 customers numeric-keyed — is the part that generalises.
- Row counts were taken at a single point in time; the `chargebee_customer_id` of user 500 is a local repair made during an earlier debugging session.
