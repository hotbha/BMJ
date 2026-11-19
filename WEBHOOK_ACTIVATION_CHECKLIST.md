# Webhook Activation Checklist

**Purpose:** the ordered, evidence-backed procedure to switch Chargebee webhooks back on against the
new VPS deployment. **Nothing in this checklist has been executed** — the Chargebee endpoints are
still disabled exactly as found.

**Preconditions already met (verified 2026-11-19):**

| Item | Status | Evidence |
|---|---|---|
| Backend reachable over public HTTPS | ✅ | `https://api.bookmyjuice.co.in/api/health` → 200 `{"status":"UP"}` |
| All five webhook routes exist and are protected | ✅ | 401 without credentials, 401 with a wrong password, 500 with the correct one (request reaches the controller) |
| Backend survives reboot | ✅ | `bmj-stack.service` enabled; stack runs under Docker Compose |
| TLS at nginx, Tomcat loopback-only | ✅ | `127.0.0.1:8080->8080` |

---

## 1. Current Chargebee configuration (live audit)

| Endpoint | Current URL | Disabled | Events | Action |
|---|---|:--:|---:|---|
| `subscription` | `http://api.bookmyjuice.co.in:8080/api/webhooks/subscriptions` | **YES** | 10 | **fix URL, then enable** |
| `Customer` | `http://api.bookmyjuice.co.in:8080/api/webhooks/customers` | **YES** | 4 | **fix URL, then enable** |
| `item` | `https://364fa3ab7f7d.ngrok-free.app/api/webhooks/items` | no | 6 | **replace ngrok URL** |
| `itemPrices` | `http://api.bookmyjuice.co.in:8080/api/webhooks/item-prices` | no | 3 | **fix URL** + drop duplicate `item_price_*` |
| `orderWebhook` | `http://api.bookmyjuice.co.in:8080/api/webhooks/orders` | no | 9 | **fix URL** |

Two facts make "just enable it" unsafe:

1. **Port 8080 is no longer published on the host** — the API is loopback-only behind nginx. Every
   `http://…:8080` URL above is now unreachable and must become `https://api.bookmyjuice.co.in/api/…`.
2. **Three subscribed subscription events have no handler**: `subscription_activated`,
   `subscription_started`, `subscription_deleted`.

---

## 2. Code prerequisites (blocking — do these first)

| # | Prerequisite | Why | Where |
|---|---|---|---|
| **P1** | Add processor cases for `subscription_activated`, `subscription_started`, `subscription_deleted` | subscribed by the endpoint but absent from the `switch` in `processSubscriptionEvent`; they would be rejected on enable | `WebhookEventProcessor` |
| **P2** | Answer **400** (not 500) for a body without a usable `id` | verified today: `{"id":"probe-not-a-real-event"}` returns 500, and Chargebee keeps retrying anything that errors | 13 webhook controllers |
| **P3** | Fail fast when `WEBHOOK_USERNAME` / `WEBHOOK_PASSWORD` are blank | `@Value("${WEBHOOK_USERNAME:}")` defaults to empty, so Spring builds a blank-password user and the endpoint **fails open** | `WebSecurityConfig` |
| **P4** | Decide on `payment_*` / `invoice_*` | no endpoint subscribes them, so `/api/webhooks/payments` and `/invoices` are dead routes and dunning UX cannot work | dashboard decision |

Until P1–P3 are merged, enabling the subscription endpoint will fail three event types and produce a
500-then-retry loop on malformed bodies.

---

## 3. URL migration

| Endpoint | Set URL to |
|---|---|
| `subscription` | `https://api.bookmyjuice.co.in/api/webhooks/subscriptions` |
| `Customer` | `https://api.bookmyjuice.co.in/api/webhooks/customers` |
| `item` | `https://api.bookmyjuice.co.in/api/webhooks/items` |
| `itemPrices` | `https://api.bookmyjuice.co.in/api/webhooks/item-prices` |
| `orderWebhook` | `https://api.bookmyjuice.co.in/api/webhooks/orders` |

Rules:

- **HTTPS only.** Three endpoints currently send customer PII over cleartext HTTP.
- **Never point a production endpoint at ngrok.** The tunnel id rotates and item sync dies silently.
- Keep Basic Auth **identical to `.env`** (`WEBHOOK_USERNAME` / `WEBHOOK_PASSWORD`), or every call
  returns 401 and Chargebee retries until it gives up.

---

## 4. Activation order

Enable one endpoint at a time and verify after each. Do **not** flip all five at once.

### Step 1 — `itemPrices` (lowest risk, no identity involvement)

1. Set URL to `https://api.bookmyjuice.co.in/api/webhooks/item-prices`.
2. In Chargebee → *Integrations → Webhooks*, **Resend** a recent `item_price_updated` event.
3. Verify on the server:

```bash
docker logs --tail 50 bmj-api | grep -i "item price"
docker exec bmj-sql mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db \
  -e "select event_id, event_type, processing_status, retry_count from webhook_events order by processed_at desc limit 5;"
```

Expect `processing_status = COMPLETED` and no `FAILED` / `DEAD_LETTER` row.

### Step 2 — `item`

1. Replace the ngrok URL with `https://api.bookmyjuice.co.in/api/webhooks/items`.
2. **Remove `item_price_*` from this endpoint** (leave them only on `itemPrices`) — today the same
   event is delivered twice to two different URLs.
3. Resend an `item_updated` event; repeat the verification.

### Step 3 — `orderWebhook`

1. Set URL to `https://api.bookmyjuice.co.in/api/webhooks/orders`.
2. Resend an `order_created` event; verify an `order_entity` row appears and the event completes.

### Step 4 — `Customer` (identity-producing, medium risk)

1. Set URL to `https://api.bookmyjuice.co.in/api/webhooks/customers`.
2. Enable the endpoint.
3. Resend a `customer_created` or `customer_changed` event for a customer whose phone matches a BMJ user.
4. Verify the identity link — the whole point of Phase 2:

```bash
docker exec bmj-sql mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -e \
  "select id, username, chargebee_customer_id from users where chargebee_customer_id is not null;"
docker logs --tail 100 bmj-api | grep -i "Identity link"
```

Expect `Identity link created: user <id> -> customer '<cb_id>' (matched by phone)`. A logged
`AMBIGUOUS` or `CONFLICT` is the designed refusal, not a bug.

### Step 5 — `subscription` (highest impact — enable last)

1. Requires **P1** merged, or three event types will fail.
2. Set URL to `https://api.bookmyjuice.co.in/api/webhooks/subscriptions`.
3. Enable the endpoint.
4. Resend a `subscription_created` event.
5. Verify the projection:

```bash
docker exec bmj-sql mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -e \
  "select id, customer_id, status from subscription_entity order by updated_at desc limit 5;"
```

6. Verify the client contract — the end-to-end proof:

```bash
curl -s -H "Authorization: Bearer <token>" https://api.bookmyjuice.co.in/api/subscriptions/my
```

Expect `200` with the subscription — **not** `409 identity_unlinked`, and **not** `200 {"subscriptions":[]}`.

---

## 5. Rollback

A misbehaving endpoint is disabled, not redeployed:

1. Chargebee → *Integrations → Webhooks* → the endpoint → **Disable**.
2. Confirm no further deliveries:
   `docker exec bmj-sql mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -e "select max(processed_at) from webhook_events;"`
3. If a bad event left the projection wrong, correct it from Chargebee (the reconnaissance/repair
   path in `CHARGEBEE_RECONCILIATION_PLAN.md`), never by editing the row by hand.

Disabling an endpoint has **no effect on the running backend** — the API is independent of inbound
webhooks; it only loses freshness.

---

## 6. Post-activation verification (all five enabled)

| Check | Command | Expected |
|---|---|---|
| All events completing | `select processing_status, count(*) from webhook_events group by processing_status;` | mostly `COMPLETED`; `FAILED` transient only |
| No dead letters | `select * from webhook_events where processing_status='DEAD_LETTER';` | empty |
| Identity coverage rising | `select count(*) from users where chargebee_customer_id is not null;` | increases as customers are mirrored |
| Projection fresh | `select max(updated_at) from subscription_entity;` | recent after any Chargebee change |
| Client sees plans | `GET /api/subscriptions/my` for a linked user | `200` with data |
| Drift detection clean | enable `sync.detection.enabled=true`, then `docker logs bmj-api \| grep -i drift` | all four counts `0` |

---

## 7. Security checklist for the activation window

- [ ] `WEBHOOK_PASSWORD` rotated to 32+ random characters (currently 12).
- [ ] `WEBHOOK_USERNAME`/`WEBHOOK_PASSWORD` in Chargebee match `.env` **exactly**.
- [ ] `CHARGEBEE_API_KEY` rotated (it was printed once during this deployment) and `.env` updated.
- [ ] P3 merged (fail-fast on blank credentials) so a missing env var cannot open the endpoint.
- [ ] Consider an IP allowlist for Chargebee's published ranges at the proxy layer.
- [ ] Alert on `401` from `/api/webhooks/**` and on any `DEAD_LETTER` row.
- [ ] `payment_*` / `invoice_*` decision recorded (subscribe them, or delete the dead controllers).

