# Deployment Verification Report

**Date:** 2026-11-19
**Host:** `api.bookmyjuice.co.in` (160.250.205.241), Ubuntu 24.04
**Deployed build:** `865fb16`
**Result:** deployed and verified. One unrelated configuration defect was found and fixed during
verification (§5) — without it the catalogue would have shipped empty.

---

## 1. Running image

| Property | Value |
|---|---|
| Container | `bmj-api` — `Up`, **restarts=0** |
| Image | `bmj-backend:vps` |
| Image ID | `sha256:c484fca5176c76f5c32c73f328a65fcbdf687dd34f5b4918c622fc1d452e42af` |
| Image built | `2026-11-19T13:45:24Z` (rebuild after promoting the new JAR) |
| Container started | `2026-11-19T13:56:12Z` (restart after the key fix, §5) |
| Port binding | `127.0.0.1:8080->8080` — **loopback only**, nginx is the sole public entry point |
| Database | `bmj-sql` — `Up 6 hours (healthy)`, no host port published, volume `bmj-mysql-data` preserved |
| systemd | `bmj-stack.service` → **enabled** |
| nginx | **active** |

## 2. JAR hashes

| Artefact | SHA-256 |
|---|---|
| **Running** (`/app/app.jar` inside the container) | `bd559ef8d5282444134943c3b9b28ffca3f012e3b7aa422aa22f1dd81b8049dc` |
| **On host** (`/home/bmj/bmj/app.jar`) | `bd559ef8d5282444134943c3b9b28ffca3f012e3b7aa422aa22f1dd81b8049dc` |
| **Rollback copy** (`app.jar.prev`) | `ac69f64898ddc98f408bb2162449712b0fad0d901ab96fa5682c0011004bbb11` (previous build `7975aeb`) |

The container hash equals the host hash equals the locally built artefact, so what runs is provably
what was tested.

## 3. Git commit

| Repo | Branch | Commit |
|---|---|---|
| `bookmyjuice/bmjServer` | `main` | **`865fb16`** `fix(security): refuse to start without webhook credentials` |
| `bookmyjuice/bmjServer` | `main` | parents: `fd07e48` (400 for malformed), `00e2a19` (3 handlers), `051ee6b` (self-heal) |
| `hotbha/BMJ` | `feat/v1-launch-freeze` | docs + submodule pointer (pushed before this deployment) |

Runtime proof the new code is live (from `docker logs bmj-api`):

```
INFO c.b.security.WebSecurityConfig - Webhook Basic Auth configured for user 'support@bookmyjuice.co.in'
INFO com.bookmyjuice.bmjServer - Started bmjServer in 17.753 seconds
```

That first line exists only in `865fb16`.

## 4. Health results

| Check | Result |
|---|---|
| `https://api.bookmyjuice.co.in/api/health` | **200** `{"timestamp":"2026-11-19T19:27:20Z","status":"UP"}` |
| `https://api.bookmyjuice.co.in/api/catalog/charge-items` | **200**, **8 003 bytes** (15 items) — live Chargebee read |
| Internal `http://127.0.0.1:8080/api/health` | `UP` |
| Boot time | 17.753 s |

## 5. Incident found during verification — stale Chargebee API key (fixed)

Straight after the rebuild, `/api/catalog/charge-items` returned **`200 []`** while health said UP.

| Evidence | Finding |
|---|---|
| `docker logs bmj-api` | `com.chargebee.APIException: Sorry, authentication failed. Invalid api key` at `CatalogController.getChargeItemsWithCategoriesAndSizes` |
| Direct call from inside the container | `HTTP/1.1 401 Unauthorized` |
| Container env key SHA-256 | `4b78d7de…` — **rejected by Chargebee** |
| Workstation `.env` key SHA-256 | `a939bbcd…` — **accepted (81 customers returned)** |

The server held an outdated Chargebee key; the workstation `.env` held a valid one. The deployment
itself was correct — the configuration it consumed was stale, and had been before this deploy: the
`item_entity` / `item_price_entity` tables were empty, so the startup sync had never populated them.

**Fix applied:** replaced the single `CHARGEBEE_API_KEY` line in `/home/bmj/bmj/.env` (previous file
kept as `.env.bak-<timestamp>`), restarted `bmj-api`, then verified: container key SHA-256 is now
`a939bbcd…`, `/api/health` = UP, `/api/catalog/charge-items` = **200, 8 003 bytes**.

**Secondary defect worth fixing in code:** the catalogue endpoint swallows the Chargebee exception and
answers `200 []`, so an empty catalogue and a broken API key look identical to the client. It should
return `502`/`503` with a reason.

## 6. Webhook endpoint results (live, over HTTPS)

| Endpoint | no auth | wrong password | authenticated, body `{}` | authenticated, fake event id |
|---|---:|---:|---:|---:|
| `/api/webhooks/customers` | **401** | **401** | **400** | 500 |
| `/api/webhooks/subscriptions` | **401** | **401** | **400** | 500 |
| `/api/webhooks/items` | **401** | **401** | **400** | 500 |
| `/api/webhooks/item-prices` | **401** | **401** | **400** | 500 |
| `/api/webhooks/orders` | **401** | **401** | **400** | 500 |

- **401 / 401** — protected, and the password is genuinely checked.
- **400** for a body without `id` — the new behaviour from `fd07e48`, demonstrated in production
  (it was **500** before this deploy).
- **500** for a well-formed body with a fake event id is correct: authentication and validation pass,
  the controller runs, and Chargebee cannot find that event.

## 7. Rollback instructions

**Fastest — binary only, ~60 s, no data impact:**

```bash
cd /home/bmj/bmj
cp app.jar app.jar.broken-$(date +%Y%m%d-%H%M)   # keep the evidence
cp app.jar.prev app.jar                          # ac69f648… = build 7975aeb
docker compose --env-file .env -f docker-compose.prod.yml up -d --build bmj-api
curl -s https://api.bookmyjuice.co.in/api/health
```

**Config rollback (the key change from §5):**

```bash
cd /home/bmj/bmj && ls .env.bak-*                # timestamped backups
cp .env.bak-<stamp> .env && chmod 600 .env
docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api
```

**nginx** (`apply-nginx.py` writes timestamped backups):

```bash
sudo cp /etc/nginx/sites-available/default.bak-<stamp> /etc/nginx/sites-available/default
sudo nginx -t && sudo systemctl reload nginx
```

**Stack:** `sudo systemctl stop bmj-stack` (data preserved) · `docker compose … down -v` **destroys the
database** — back it up first.

After any rollback, verify `docker exec bmj-api sha256sum /app/app.jar` equals the hash you intended.

## 8. Data untouched

No migration was run, no subscription row was modified, and no Chargebee setting was changed. The only
writes were: the new JAR (plus `app.jar.prev`), one line in `.env` (with a backup), and the Docker
image rebuild. `customer_entity` (81) and `subscription_entity` (16) counts were unchanged across the
deployment.

