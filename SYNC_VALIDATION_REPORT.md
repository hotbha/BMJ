# Sync Validation Report

**Date:** 2026-11-19 · **Method:** read-only SQL against the production database + log inspection
**Database:** `bmj_db` on `bmj-sql` (VPS) · **Backend:** `865fb16`

---

## 1. Table state

| Table | Rows | Interpretation |
|---|---:|---|
| `webhook_events` | **0** | no event has ever been accepted (see `WEBHOOK_VALIDATION_REPORT.md`) |
| `users` | **0** | no BMJ account exists on production |
| `customer_entity` | **81** | populated by the **startup pull sync** from Chargebee |
| `subscription_entity` | **16** (14 ACTIVE, 2 CANCELLED) | also from the startup pull sync |

The push path (webhooks) has contributed **nothing**; the pull path (startup sync) has contributed
everything. That is the single most important fact in this report.

## 2. Retry worker

| Metric | Value |
|---|---:|
| FAILED | 0 |
| Retry queue (`FAILED` with `retry_count < 3`) | 0 |
| DEAD_LETTER | 0 |
| Stuck `PROCESSING` (> 15 min) | 0 |
| COMPLETED | 0 |
| Retry activity in the log | none |

**Verdict: healthy but completely unexercised.** An empty queue is the correct state when no event has
been accepted; it proves nothing about the worker's behaviour under failure. No dead-letter growth
because no dead letters can exist.

## 3. Drift detectors (run read-only, as SQL)

| Detector | Meaning | Findings |
|---|---|---:|
| **D1** | users with subscriptions but no identity link | **0** |
| **D2** | duplicate customer identities per phone | **7 phones** |
| **D3** | subscription rows no user can reach | **16** (all of them) |
| **D4** | subscription rows on a legacy numeric (twin) key | **0** |

### Reading these numbers honestly

- **D1 = 0 and D4 = 0 are vacuous wins.** Both detectors join `users`; with zero users they cannot
  match anything. They will not become meaningful until an account exists.
- **D3 = 16 is real but benign.** All 16 subscriptions belong to Chargebee customers who have no BMJ
  user yet. They become reachable as soon as each customer registers, because
  `IdentityLinker.linkUser` links on login. This is "not yet onboarded", not corruption.
- **D2 = 7 is real and worth attention.** Duplicate customer rows per phone come straight from
  Chargebee, e.g. phone `9876543210` exists **11 times**:

```
| 9876543210  | 11 | 100,169m1FVKSGoO233mc,169qA9VZQs1agn0c,16BYIfVZQs08KmlF,…
| +1234567890 |  6 | 520,533,534,535,536,538
| 1234567890  |  5 | 517,530,539,541,542
| 00000001    |  2 | 514,518
| 1010101010  |  2 | 505,507
| 1111111111  |  2 | 508,516
| 9090909090  |  2 | 16BdPNVKNMfrs1SdM,519
```

**Operational consequence:** an account registering on `9876543210` will be **refused** a link by
design (`Outcome.AMBIGUOUS`), because the linker will not guess between eleven candidates. Any QA
account must therefore use a phone number that appears exactly once in Chargebee.

## 4. Identity coverage

| Measure | Value |
|---|---:|
| Users total | 0 |
| Linked | 0 |
| Unlinked | 0 |
| Ambiguous user↔customer matches | 0 (no users) |
| Conflicts (duplicate customer rows) | 7 phones |

Identity coverage cannot be measured without users. This is **not** a failure of the mechanism — the
`IdentityLinker`, the login self-heal and the webhook hook are deployed — it is the absence of any
subject to exercise them on.

## 5. Chargebee ↔ BMJ agreement

| Check | Result |
|---|---|
| Customer count | Chargebee **81**, local **81** — agree |
| Subscription count | Chargebee **16** (14 active, 2 cancelled), local **16** (14 ACTIVE, 2 CANCELLED) — agree |
| Agreement source | startup pull sync, not webhooks |
| Catalogue | live read at request time: 176 items, 20 charge items returned to the app |

## 6. What would make this report meaningful

1. **Fix the webhook credential** (`WEBHOOK_VALIDATION_REPORT.md` §6) → `webhook_events` becomes
   non-empty and the retry worker, dead-letter path and `COMPLETED` status become observable.
2. **Create the QA account** (`QA_ACCOUNTS.md` §5) → D1/D4 stop being vacuous, identity coverage and
   self-heal become testable, and D3 drops as the account links to its subscriptions.
3. **Decide on the D2 duplicates** — eleven customer rows on one phone is a Chargebee data condition
   that will keep producing `AMBIGUOUS` link outcomes for real users on that number.
