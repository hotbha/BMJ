# Post-Deployment Sync Report

**Date:** 2026-11-19 · **Server time at validation:** 14:11 UTC
**Host:** `api.bookmyjuice.co.in` · **Build:** `865fb16` (`bd559ef8…8049dc`)
**Method:** read-only. No data modified, no migration executed, no Chargebee setting changed.

---

## Headline

**The synchronisation path is not carrying traffic yet.** Chargebee shows every endpoint enabled with
correct HTTPS URLs, but **zero webhook events have been received**, and the container is still
configured with the **old webhook password** (proven by hash), so any delivery that arrives will be
rejected `401`.

The mirror that exists today came from the **startup sync**, not from webhooks:

| Table | Rows | Source |
|---|---:|---|
| `customer_entity` | 81 | Chargebee startup sync |
| `subscription_entity` | 16 | Chargebee startup sync |
| `webhook_events` | **0** | nothing received |
| `users` | **0** | nobody has signed up on this database yet |

---

## 1. `webhook_events` by status

| Status | Count |
|---|---:|
| COMPLETED | **0** |
| FAILED | **0** |
| PROCESSING | **0** |
| DEAD_LETTER | **0** |
| **total** | **0** |

`MIN(processed_at)` = NULL, `MAX(processed_at)` = NULL — the table has never held a row.

## 2. Customer webhook validation

| Check | Result |
|---|---|
| Events received (`customer_created`, `customer_changed`, `_deleted`, `_entitlements_updated`) | **0** |
| Latest receipt | none |
| Endpoint state in Chargebee | `Customer` = **enabled**, `https://api.bookmyjuice.co.in/api/webhooks/customers` |
| Endpoint behaviour from the internet | verified earlier: 401 unauthenticated, 400 for a malformed authenticated body |

**No live customer event has been received.** The endpoint is correctly configured and protected; it
has simply not been exercised.

## 3. Subscription webhook validation

| Event type | Received |
|---|---:|
| `subscription_created` | **0** |
| `subscription_changed` | **0** |
| `subscription_activated` | **0** |
| `subscription_started` | **0** |
| `subscription_deleted` | **0** |

Chargebee's own delivery record for the most recent `subscription_renewed` (`ev_169pAfVbMGr878tR5`)
shows the subscription endpoint (`whv2_6ob9UUhT0EQo3TYf`) in state **`re_scheduled`** — an attempt that
failed and was queued for retry. Across the 30 most recent events:

| webhook_status | Count |
|---|---:|
| `not_applicable` | 143 |
| `re_scheduled` | 7 |
| `succeeded` | **0** |
| `failed` (final) | **0** |

## 4. Identity coverage

| Measure | Value |
|---|---:|
| Users total | **0** |
| Linked | **0** |
| Unlinked | **0** |
| Ambiguous (several users sharing one customer id) | **0** |
| Conflicts (duplicate customer rows per phone) | **7 phones** |

There is nothing to measure: the production database has no BMJ users. The 7 duplicated phones are
duplicate *customer* rows pulled from Chargebee (`9876543210` appears **11** times), not user
conflicts — with zero users, no two users can collide.

## 5. Drift detection (all detectors, read-only SQL)

| Detector | Meaning | Findings |
|---|---|---:|
| **D1** | users with subscriptions but no link | **0** |
| **D2** | duplicate customer identities per phone | **7** |
| **D3** | subscription rows no user can reach | **16** (all of them) |
| **D4** | subscription rows on a legacy numeric (twin) key | **0** |
| D4 active rows | — | **0** |

**D3 = 16** is the only substantive number and its cause is benign: those subscriptions belong to
Chargebee customers for whom **no BMJ user exists yet**. They become reachable as soon as that customer
signs up, because `IdentityLinker.linkUser` links them on first login. This is "not yet onboarded",
not "corrupted keys".

**D4 = 0** is the important result: the defect that motivated the migration plan (11 rows on numeric
twin keys) **does not exist in this database**.

## 6. Retry worker

| Metric | Value |
|---|---:|
| FAILED | 0 |
| Retry queue (`FAILED` with `retry_count < 3`) | 0 |
| DEAD_LETTER | 0 |
| Stuck `PROCESSING` (> 15 min) | 0 |
| COMPLETED | 0 |
| Retry activity in the log | none |

The worker is scheduled and running but has nothing to do. An empty queue is a healthy queue — it is
simply untested against real failures.

## 7. Remaining migration scope

| Measure | Value |
|---|---:|
| Users requiring re-keying | **0** |
| Rows requiring re-keying | **0** |
| Users requiring linking | **0** |
| Subscription rows in total | 16 |

## 8. Recommendation

### **C — Migration no longer required**

For this database the migration has nothing to act on: **0 users, 0 twin-keyed rows, 0 dangling
links**. Every number the plan was written to fix is zero. Running it here would be a no-op and should
not be executed.

**Conditional on two things you should decide deliberately:**

1. **This is scoped to the production database.** The workstation smoke database still holds the
   6-user / 11-row twin-key case (`SUBSCRIPTION_DATA_CENSUS.md`). That is test data — it needs
   discarding, not migrating.
2. **Sync is not yet carrying traffic**, so "self-heal" has not been demonstrated against live events.
   See §9.

---

## 9. Blocker found — the server still expects the OLD webhook password

This is why nothing has been delivered. Proven without exposing either secret:

| Evidence | Result |
|---|---|
| `docker exec bmj-api printenv WEBHOOK_PASSWORD` sha256 | `5be7b515…` |
| `sha256("rADHASOAMI@0")` — the previous password | `5be7b515…` — **identical** |
| `/home/bmj/bmj/.env` `WEBHOOK_PASSWORD` sha256 | `5be7b515…` — same as the container |
| Chargebee (per the rotation you reported) | rotated |

The container and `.env` both still hold the **pre-rotation** value, so Basic Auth will answer **401**
to every Chargebee delivery — before the controller is reached, which is exactly why `webhook_events`
stays empty (an event row is only created after authentication succeeds).

Supporting evidence that no Chargebee request has reached the host since the URLs were fixed: nginx's
access log contains only my own probe traffic (IP `223.190.85.230`, PowerShell user agent — 31×401,
10×400, 15×500) and **no request from a Chargebee origin**.

**To unblock** (one value; no code, no redeploy):

```bash
cd /home/bmj/bmj
cp -p .env .env.bak-$(date +%Y%m%d-%H%M%S)
# replace ONLY the WEBHOOK_PASSWORD line with the value now set in Chargebee
docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api
# then re-send one event from Chargebee and confirm it lands:
docker exec bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -e \
  "select event_type, processing_status, processed_at from webhook_events order by processed_at desc limit 5;"'
```

I did not make this change: the rotated value is a secret only you hold, and writing a guess into
production configuration is exactly what this validation exists to prevent.

## 10. What is demonstrably working

| Capability | Evidence |
|---|---|
| Chargebee → BMJ **pull** sync | 81 customers and 16 subscriptions mirrored by the startup sync |
| Live catalogue read | `/api/catalog/charge-items` → 200, 8 003 bytes, 15 items |
| Identity linking mechanism deployed | `IdentityLinker` + self-heal on 7 auth paths + webhook hook |
| Read contract honesty | 409 `identity_unlinked` / `identity_broken` / `subscription_unavailable` |
| Webhook endpoints reachable and authenticated | 401 unauthenticated, 400 malformed, 500 fake-id (reaches controller) |
| Retry / dead-letter machinery | scheduled, queue empty |
| Event coverage | 29/29 subscribed types handled (test-enforced) |

## 11. Verification steps performed (all read-only)

`SELECT`-only against `webhook_events`, `users`, `customer_entity`, `subscription_entity`; `GET`-only
against the Chargebee API; `docker logs`, `docker inspect`, `docker exec printenv` and the nginx access
log for evidence. No `INSERT` / `UPDATE` / `DELETE` / DDL, no migration, no Chargebee modification.

