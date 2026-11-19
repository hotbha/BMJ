# Chargebee Live Audit

**Date:** 2026-10-31
**Site audited:** `bookmyjuice-test` (from `CHARGEBEE_SITE` in `.env`)
**Credentials:** `CHARGEBEE_API_KEY` from `.env` (never printed, never logged)
**Method:** read-only `GET` against `https://bookmyjuice-test.chargebee.com/api/v2`.
Nothing was created, updated or deleted in Chargebee.
**Reproduce:** `python _captures/qa/chargebee_live_audit.py`, `chargebee_webhook_dump.py`,
`chargebee_event_delivery.py`, `identity_coverage.py`

---

## 1. Headline

**The webhook endpoints that matter are switched off.** The `subscription` and `Customer`
endpoints both point at production and are both **disabled**; of the 30 most recent events,
**zero** had a successful delivery. The local mirror has therefore never been fed by
subscription or customer webhooks — every subscription row in BMJ came from seed data or a
manual call.

That one fact explains every drift measurement in `SUBSCRIPTION_DATA_CENSUS.md`.

---

## 2. Account facts

| Measure | Live value | Local (`bmj-smoke-mysql`) | Agreement |
|---|---:|---:|---|
| Customers | **81** | 81 `customer_entity` rows | counts match |
| Subscriptions | **16** (14 active, 2 cancelled) | 16 rows (14 ACTIVE, 2 CANCELLED) | **count and status split match exactly** |
| Items | **176** (151 plans) | — | catalogue is large |
| Events sampled | 30 (recent renewals / invoices / payments) | — | — |

The subscription **count** matching exactly matters: the mirror is not missing or duplicating
rows. The defect is the **key** those rows are filed under (§7).

---

## 3. Webhook endpoints (live configuration)

`GET /api/v2/webhook_endpoints` → 5 endpoints:

| Name | URL | Primary | Disabled | Events |
|---|---|---|:--:|---:|
| `subscription` | `http://api.bookmyjuice.co.in:8080/api/webhooks/subscriptions` | **yes** | **YES** | **10** |
| `Customer` | `http://api.bookmyjuice.co.in:8080/api/webhooks/customers` | no | **YES** | **4** |
| `item` | `https://364fa3ab7f7d.ngrok-free.app/api/webhooks/items` | no | no | 6 |
| `itemPrices` | `http://api.bookmyjuice.co.in:8080/api/webhooks/item-prices` | no | no | 3 |
| `orderWebhook` | `http://api.bookmyjuice.co.in:8080/api/webhooks/orders` | no | no | 9 |

- **2 of 5 are disabled — and they are the two that carry billing identity.**
- 3 of 5 use **plain HTTP**: event payloads, including customer PII, travel unencrypted.
- 1 active endpoint targets an **ngrok tunnel** — an ephemeral dev URL that will disappear,
  so item sync is already unreliable.
- The only endpoint flagged `primary_url` is a disabled one, so there is no effective
  subscription delivery path even as a failover.

---

## 4. Subscribed events

**Union: 29 event types.**

| Endpoint | Events |
|---|---|
| `subscription` (disabled) | `subscription_created`, `_cancelled`, `_paused`, `_resumed`, `_activated`, `_started`, `_changed`, `_reactivated`, `_renewed`, `_deleted` |
| `Customer` (disabled) | `customer_created`, `_changed`, `_deleted`, `_entitlements_updated` |
| `item` | `item_created`, `_updated`, `_deleted`, `item_price_created`, `_updated`, `_deleted` |
| `itemPrices` | `item_price_created`, `_updated`, `_deleted` |
| `orderWebhook` | `order_created`, `_updated`, `_cancelled`, `_delivered`, `_returned`, `_ready_to_process`, `_ready_to_ship`, `_deleted`, `_resent` |

**Gaps against the running server:**

| Finding | Detail |
|---|---|
| **No `invoice_*` event subscribed anywhere** | `/api/webhooks/invoices` exists in code but can never receive an event |
| **No `payment_*` event subscribed anywhere** | `/api/webhooks/payments` is a dead route; `payment_failed` never reaches BMJ, so the "payment needs attention" behaviour in the webhook matrix is unreachable today |
| 3 subscribed types have **no processor case** | `subscription_activated`, `subscription_started`, `subscription_deleted` are subscribed but the switch handles only created/changed/paused/cancelled/updated/reactivated/renewed — enabling the endpoint as-is would fail those three |
| Duplicate subscription | `item_price_*` is subscribed by **two** endpoints, so the same event can be delivered twice to different URLs; our idempotency table absorbs it, but it is avoidable noise |

---

## 5. Authentication model

**Configured protection: HTTP Basic Auth.**

- `.env` defines `WEBHOOK_USERNAME` and `WEBHOOK_PASSWORD`. There is **no**
  `WEBHOOK_SECRET` or signing-key variable anywhere in the file.
- The server implements it correctly: `WebSecurityConfig` declares a dedicated
  `@Order(1)` chain with `securityMatcher("/api/webhooks/**")`, `anyRequest().authenticated()`
  and `httpBasic(...)`, backed by an `InMemoryUserDetailsManager` user with role `WEBHOOK`
  built from those two properties.
- `GET /webhook_endpoints` exposes **no** authentication field: the resource has only
  `id, name, url, primary_url, api_version, disabled, enabled_events, send_card_resource`.

**Weakness in our implementation (not Chargebee's):** both properties default to empty
(`@Value("${WEBHOOK_USERNAME:}")`, `@Value("${WEBHOOK_PASSWORD:}")`). If either is missing in a
deployed environment, Spring still builds the in-memory user with a **blank password**, and the
endpoint accepts `Basic <anything>:`. It fails open.

---

## 6. Retry behaviour

**Measured, not assumed.** Each event record carries a `webhooks[]` array with per-endpoint
delivery status. Across the 30 most recent events:

| Delivery status | Count |
|---|---:|
| `not_applicable` (endpoint does not subscribe this event) | 90 |
| `disabled` (endpoint is switched off) | 60 |
| `succeeded` | **0** |
| `failed` | **0** |
| `retry_scheduled` / `retrying` | **0** |

Observed sample:

```
subscription_renewal_reminder -> not_applicable, disabled, disabled, not_applicable, not_applicable
subscription_renewed          -> disabled, not_applicable, not_applicable, disabled, not_applicable
invoice_generated             -> disabled, not_applicable, not_applicable, disabled, not_applicable
payment_succeeded             -> not_applicable, ..., disabled, disabled
```

Conclusions:

- Nothing is **retried**, because nothing is **attempted** for subscriptions or customers — that
  is a configuration state, not a delivery failure.
- Chargebee's own retry schedule is not exposed through the API and could not be measured from
  this account. Recorded as *unmeasured* rather than restated as fact.
- BMJ-side retry now exists (`WebhookRetryService`, commit `3bf040e`) but has nothing to drain
  while the endpoints are off.

---

## 7. Customer / subscription counts and identity-link coverage

**Customers:** 81 live, 81 mirrored. Only **14 of 81** match a BMJ user by phone; the rest are
demo, QA and catalogue fixtures.

**Subscriptions:** 16 live, 16 local, identical status split.

**Identity-link coverage** (measured against the live customer list):

| Measure | Value |
|---|---:|
| BMJ users | 6 |
| Users with a non-empty `chargebee_customer_id` | **4 (67 %)** |
| Users without one | **2** — ids 1 and 501; neither owns a subscription |
| Users owning subscription rows | 4 |
| …whose link resolves to a customer that exists in Chargebee | 4 |
| …whose subscriptions `/api/subscriptions/my` can actually return | **1** |

The last two rows are the distinction that matters: **identity coverage 4/6, projection
reachability 1/4.** Users 502, 503, 504 have valid links, but their rows are still filed under
numeric twin keys — the 11-row mismatch measured in the census, and the reason Phase 1 now
answers `409 subscription_unavailable` instead of a false empty list.

---

## 8. Is webhook signature verification available for this site?

**Verified answer: not available to us today — do not implement HMAC.**

| Check | Result |
|---|---|
| Does `GET /webhook_endpoints` expose a signing secret / signature config? | **No.** The record's fields are `api_version, disabled, enabled_events, id, name, object, primary_url, send_card_resource, url` — no auth material of any kind |
| Are there dedicated signature endpoints? | `GET /webhook_endpoints/signature` → **404** "Webhook endpoint not found"; `GET /webhook_endpoints/secret` → **404** |
| Does the account hold a webhook secret in configuration? | **No** — `.env` has `WEBHOOK_USERNAME` / `WEBHOOK_PASSWORD` only; no `*SECRET*` key exists |
| Is the endpoint authenticated at all? | Yes, by them: the server chain requires Basic Auth, and the `.env` credentials pair with it |

Because Chargebee exposes no signing secret for these endpoints, an HMAC implementation could
not be provisioned, tested or rotated — it would be dead code guarding nothing. **Per the
instruction, HMAC is not implemented.** Hardening is designed around Basic Auth instead (§9).

Residual risk to accept knowingly: Basic Auth authenticates the *caller* but does not stop a
replay of a captured request, because the payload carries no signature. Mitigation is transport
security (HTTPS) plus idempotency (already present via `webhook_events`).

---

## 9. Hardening designed around Basic Auth

Ordered by risk reduction per unit of effort. None of this is implemented yet.

| # | Control | Why | Where |
|---|---|---|---|
| **1** | **Fail fast on missing credentials.** Abort startup if `WEBHOOK_USERNAME` or `WEBHOOK_PASSWORD` is blank. | Today blank values silently create a blank-password user → the endpoint accepts anything | `WebSecurityConfig` |
| **2** | **Re-enable the two disabled endpoints** (`subscription`, `Customer`) | They are the reason no billing event has ever been delivered | Chargebee dashboard (**needs your action; I made no changes**) |
| **3** | **HTTPS only for every endpoint URL** | 3 of 5 are plain HTTP, sending customer PII in clear text | Chargebee dashboard |
| **4** | **Retire the ngrok endpoint**; point items at the same stable host as the others | The tunnel is ephemeral; item sync breaks whenever it rotates | Chargebee dashboard |
| **5** | **Rotate `WEBHOOK_PASSWORD`** to a generated 32-byte value, stored only in the secret store | Current value is short and lives in a file | secrets |
| **6** | **Subscribe `payment_*` and `invoice_*`** (or delete the dead controllers) | `/api/webhooks/payments` and `/invoices` can never receive anything today | Chargebee dashboard |
| **7** | **Add processor cases for `subscription_activated`, `_started`, `_deleted`** | Subscribed but unhandled → they would fail on enable | `WebhookEventProcessor` |
| **8** | **Remove the duplicate `item_price_*` subscription** from one of the two endpoints | Same event delivered twice | Chargebee dashboard |
| **9** | **Restrict the webhook filter chain to POST** | Only POST is meaningful; narrower surface | `WebSecurityConfig` |
| **10** | **Edge controls**: IP allowlist for Chargebee's ranges, and rate limiting on `/api/webhooks/**` | Defence in depth on a shared-secret scheme | reverse proxy |
| **11** | **Alert on any `401` from the webhook path, and on `DEAD_LETTER` growth** | The integration can go silent without anyone noticing — which is precisely what happened | monitoring |

Deferred by decision: HMAC signature validation (no secret is available to provision it — §8).
If Chargebee enables signing for this site later, the change is additive: verify the header
before the controller body and keep Basic Auth as a second factor.

---

## 10. What this changes about the roadmap

| Previous assumption | Correction from live data |
|---|---|
| "Webhooks may be missed occasionally" | **No subscription or customer webhook has ever been delivered.** The mirror is seed-only |
| "Retry hardening will repair failed deliveries" | Retry has nothing to retry until endpoint #2 above is done |
| "Signature verification is Phase 3 work" | Not provisionable for this site — Phase 3 closes on retry/dead-letter only |
| "Payment failures reach the app" | No `payment_*` event is subscribed anywhere → the dunning UX cannot work yet |
| "Identity coverage is the main gap" | Identity is 4/6 linked; **delivery** is 0 % — the more fundamental gap |

---

## 11. Immediate actions

**Yours (Chargebee dashboard, I did not modify anything):**
1. Re-enable `subscription` and `Customer` endpoints.
2. Switch their URLs to HTTPS.
3. Replace the ngrok item URL with the stable host.
4. Subscribe `payment_*` / `invoice_*`, or approve deleting those controllers.
5. Rotate the webhook password.

**Mine, on approval:**
6. Fail-fast credential validation in `WebSecurityConfig` (§9.1) — small, testable commit.
7. Processor cases for the three unhandled subscription types (§9.7).
8. Then verify the first real delivery end-to-end and re-run the census; with delivery working,
   the identity repair of `SUBSCRIPTION_MIGRATION_PLAN.md` can finally be validated against live
   traffic instead of seed data.

---

## 12. Audit integrity

- Only `GET` requests were issued. No endpoint was created, disabled, enabled or modified.
- The API key was never printed: scripts load it from `.env` into memory and log only the site name.
- Raw evidence: `_captures/qa/chargebee_live_audit.json`, `chargebee_event_delivery.json`,
  `identity_coverage.json`.
- Scope note: the site is a **test** site (`bookmyjuice-test`), so all counts above describe test
  data. The *configuration findings* (disabled endpoints, HTTP URLs, ngrok, no signing secret) are
  configuration facts that should be re-verified on the production site before go-live.


