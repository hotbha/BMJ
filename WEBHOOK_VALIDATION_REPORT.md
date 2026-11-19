# Webhook Validation Report

**Date:** 2026-11-19 · **Method:** read-only inspection of nginx access logs, application logs, the
`webhook_events` table, and an authenticated self-test against the live endpoint.
**Backend:** `865fb16` on `api.bookmyjuice.co.in`

---

## Verdict

| Check | Result |
|---|---|
| Chargebee endpoints enabled with HTTPS URLs | **PASS** (5/5, verified via API) |
| Chargebee is actually attempting delivery | **PASS** — real requests observed |
| Deliveries authenticated successfully | **FAIL** — every attempt answered **401** |
| `webhook_events` rows created | **FAIL** — 0 rows |
| `processing_status = COMPLETED` | **FAIL** — no rows to complete |
| Dead-letter growth | **PASS (vacuously)** — 0, because nothing was processed |
| Customer webhook processed | **FAIL** — no customer delivery attempted at all |
| Subscription webhook processed | **FAIL** — 5 attempts, all 401 |

**Root cause: the Basic Auth password stored in Chargebee does not match the one on the server.** The
server is correct; Chargebee is sending the wrong secret.

---

## 1. Chargebee is delivering — hard evidence

From `/var/log/nginx/access.log` (real Chargebee origin, real user agent):

```
3.215.11.205 - support@bookmyjuice.co.in [19/Nov/2026:12:27:31 +0000] "POST /api/webhooks/subscriptions HTTP/1.1" 401 129 "-" "ChargeBee"
3.215.11.205 - support@bookmyjuice.co.in [19/Nov/2026:14:19:00 +0000] "POST /api/webhooks/subscriptions HTTP/1.1" 401 129 "-" "ChargeBee"
3.215.11.205 - support@bookmyjuice.co.in [19/Nov/2026:14:21:02 +0000] "POST /api/webhooks/subscriptions HTTP/1.1" 401 129 "-" "ChargeBee"
3.215.11.205 - support@bookmyjuice.co.in [19/Nov/2026:14:27:04 +0000] "POST /api/webhooks/subscriptions HTTP/1.1" 401 129 "-" "ChargeBee"
3.215.11.205 - support@bookmyjuice.co.in [19/Nov/2026:14:57:07 +0000] "POST /api/webhooks/subscriptions HTTP/1.1" 401 129 "-" "ChargeBee"
```

Status tally for Chargebee-originated requests: **5 × 401, 0 × 2xx.**

The username carried in the request (`support@bookmyjuice.co.in`) **matches** the configured one, so
the mismatch is the password, not the identity.

## 2. The server side is correct — authenticated self-test

Run from inside the container, so the credentials never left the host and were never printed:

| Attempt | Result | Meaning |
|---|---|---|
| `curl -u "$WEBHOOK_USERNAME:$WEBHOOK_PASSWORD"` with body `{}` | **HTTP 400** | credentials **accepted**; 400 is the payload guard rejecting a body with no `id` |
| `curl -u "$WEBHOOK_USERNAME:wrong-password"` with body `{}` | **HTTP 401** | wrong password correctly rejected |

Both appear in nginx as `172.18.0.2 ... "curl/8.18.0"` at 15:30:55 (400) and 15:30:56 (401).

So the endpoint, the filter chain and the stored credential are all working. The only failing link is
the secret configured in Chargebee.

## 3. The stored password did change — but not to the matching value

| Measurement | Value |
|---|---|
| `WEBHOOK_PASSWORD` sha256 (trimmed), earlier today | `5be7b515…` (the pre-rotation value `rADHASOAMI@0`) |
| `WEBHOOK_PASSWORD` sha256 (trimmed), now | **`23912d90…`** |
| `.env` vs container | **identical** (`23912d90…` both) |

The password on the server *was* updated and is self-consistent. Chargebee's stored password is a
different value — most likely the rotation was applied in one place only, or with a different string.

## 4. `webhook_events` state

| Status | Count |
|---|---:|
| COMPLETED | 0 |
| FAILED | 0 |
| PROCESSING | 0 |
| DEAD_LETTER | 0 |
| **total** | **0** |

An event row is only written **after** Basic Auth succeeds (the controller claims the event id inside
the authenticated handler), which is exactly why a 401 storm leaves the table empty. The empty table is
a *symptom* of the 401s, not a separate fault.

## 5. Customer webhook

No delivery attempt from Chargebee to `/api/webhooks/customers` appears in the log at all. The endpoint
is enabled and correctly configured, but no recent `customer_created` / `customer_changed` event has
occurred on the account to trigger one. **Not testable until either an event occurs or the password is
fixed and an event is re-sent.**

## 6. Fix (one value, Chargebee side)

In Chargebee → *Settings → Integrations → Webhooks* → each endpoint → Basic Auth, set the password to
the value in `/home/bmj/bmj/.env` (`WEBHOOK_PASSWORD`). The username is already correct.

Verification after the fix:

```bash
# 1. re-send any event from Chargebee (Events → Resend)
# 2. expect HTTP 200/500 instead of 401 in the access log
sudo grep "ChargeBee" /var/log/nginx/access.log | tail -3
# 3. and a row to appear
docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -e \
  "select event_id, event_type, processing_status, processed_at from webhook_events order by processed_at desc limit 5;"'
```

Note: a `500` on a well-formed body is also progress — it means auth passed and the handler ran. The
`400` you should *not* see from Chargebee, since Chargebee always sends an `id`.
