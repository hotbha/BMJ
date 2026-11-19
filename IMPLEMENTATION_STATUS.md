# Implementation Status

**Last updated:** 2026-11-19
**Repos:** `bookmyjuice/bmjServer` (backend), `lush` (Flutter app), `hotbha/BMJ` (docs + this file)
**Branches:** backend `main` @ `865fb16` · docs `feat/v1-launch-freeze`

---

## 1. Snapshot

| Area | State | Evidence |
|---|---|---|
| Backend API | **Live** on `api.bookmyjuice.co.in` over HTTPS | `/api/health` -> 200 `{"status":"UP"}` |
| Backend build | Deployed from `865fb16` | JAR sha256 `BD559EF8...8049DC`, verified on the host |
| Database | MySQL 8 in Docker, named volume, no host port | `bmj-sql` healthy |
| Process supervision | systemd unit enabled | `systemctl is-enabled bmj-stack` -> `enabled` |
| Identity identity-linking | Self-heals on login **and** from webhooks | `IdentityLinker` + `WebhookIdentityHook` |
| Subscription read contract | Never answers a false empty | 409 `identity_unlinked` / `identity_broken` / `subscription_unavailable` |
| Webhook retry | Worker drains FAILED, dead-letters after 3 | `WebhookRetryService` |
| Webhook payload validation | Malformed -> **400** | `WebhookPayloadValidationFilter` |
| Webhook credentials | Startup fails if blank | `WebSecurityConfig.validateWebhookCredentials` |
| Event coverage | 29 of 29 subscribed types handled | `WebhookEventCoverage` + test |
| **Chargebee webhooks (live)** | **DISABLED - nothing delivered** | `CHARGEBEE_LIVE_AUDIT.md` §3 |
| Chargebee production credentials | **Missing** - VPS runs the test site | `.env` `CHARGEBEE_SITE=bookmyjuice-test` |
| Flutter app | 418 tests passing, material work uncommitted | `flutter test` |

---

## 2. Commit inventory (backend `main`)

| Commit | Type | What it does | Rollback |
|---|---|---|---|
| `865fb16` | fix(security) | Startup aborts when `WEBHOOK_USERNAME`/`WEBHOOK_PASSWORD` are blank (previously failed open) | revert; but reopens a blank-password endpoint - also ensure env vars are set |
| `fd07e48` | fix(webhooks) | Filter answers 400 for malformed/envelope-less bodies, replays body downstream | revert; malformed bodies return 500 again |
| `00e2a19` | feat(sync) | Handlers for `subscription_activated` / `_started` / `_deleted`; `WebhookEventCoverage` map | revert; those three types fail on delivery if the endpoint is enabled |
| `051ee6b` | feat(sync) | `IdentityLinker.linkUser` + self-heal on 7 auth entry points | revert; links stop self-healing, existing links unaffected |
| `7975aeb` | feat(sync) | Read-only drift detection (D1/D2/D3/D4), disabled by default | revert; no data impact |
| `3bf040e` | feat(sync) | Retry worker + dead-letter + `@EnableScheduling` | revert; failed events stay FAILED |
| `042333b` | feat(sync) | Identity linking from customer/subscription webhooks | revert; webhooks stop linking |
| `53d1718` | feat(sync) | Identity Linker as the single writer of the link | revert; auth sets links inline again |
| `7d761de` | feat(sync) | Resolver hardening, explicit identity outcomes, `409` contract | revert only with a client change - the app depends on the 409 today |

**Every backend commit above compiles and its tests pass.** None writes business data at startup.

---

## 3. Test evidence

| Suite | Cases | Result |
|---|---:|---|
| `IdentityLinkerTest` | 18 | pass |
| `CustomerIdentityResolverTest` | 9 | pass |
| `WebhookEventCoverageTest` | 6 | pass |
| `WebhookRetryServiceTest` | 6 | pass |
| `WebhookPayloadValidationFilterTest` | 5 | pass |
| `WebhookCredentialsValidationTest` | 5 | pass |
| `SubscriptionIdentityEndpointTest` | 5 | pass |
| `WebhookIdentityHookTest` | 4 | pass |
| `DriftDetectionServiceTest` | 3 | pass |
| **Total (sync/webhook suites)** | **61** | **0 failures** |

`mvn -o -q -DskipTests package` -> exit 0. Flutter side untouched: `flutter test` 418/418.

---

## 4. Deployment state

| Item | Value |
|---|---|
| Host | `api.bookmyjuice.co.in` (160.250.205.241), Ubuntu 24.04 |
| Reachable over HTTPS | **yes** — `/api/health` -> 200 `{"status":"UP"}` |
| Reachable over SSH | **yes** — the earlier timeouts were a host-key issue, not a network block |
| Build running on the host | **`865fb16`** — container `/app/app.jar` sha256 `bd559ef8…8049dc` |
| Previous build kept for rollback | `app.jar.prev` = `ac69f648…bbb11` (`7975aeb`) |
| Remote image | `bmj-backend:vps` = `sha256:c484fca5…` |
| Migration run | **no** |
| Subscription data touched | **no** — `customer_entity` 81 / `subscription_entity` 16 unchanged |

**Incident fixed during verification:** the server `.env` carried a stale `CHARGEBEE_API_KEY` that
Chargebee answered with `401 Invalid api key`, so the catalogue came back as `200 []`. The key line was
replaced (timestamped `.env.bak-*` kept) and `bmj-api` restarted; the catalogue now returns 200 with
15 items. Full evidence in `DEPLOYMENT_VERIFICATION_REPORT.md` §5.

Known code defect surfaced by that incident: `CatalogController` converts a Chargebee failure into
`200 []`, so "no products" and "broken credentials" look identical to the client. Should be a 5xx.


---

## 5. Rollback — deployment level

| Scope | Command | Data impact |
|---|---|---|
| Revert just the API binary | `cp app.jar.prev app.jar && docker compose ... up -d --build bmj-api` | none |
| Revert the nginx proxy | restore `/etc/nginx/sites-available/default.bak-<stamp>`, `nginx -t`, reload | none |
| Stop the stack, keep data | `sudo systemctl stop bmj-stack` | none |
| Destroy everything | `docker compose ... down -v` | **deletes `bmj-mysql-data`** — back up first |

Keep `app.jar.prev` on the host; it is what makes a one-command rollback possible without a
round-trip to the workstation.

---

## 6. What is still open

| Priority | Item | Owner |
|---|---|---|
| **Blocker** | SSH access to the VPS (port 22 times out) — blocks shipping `865fb16` | ops |
| **Blocker** | Chargebee `subscription` + `Customer` endpoints disabled | dashboard |
| **Blocker** | Chargebee endpoint URLs are `http://...:8080` (loopback-only now) | dashboard |
| High | Chargebee production credentials (`CHARGEBEE_SITE=bookmyjuice-test` today) | product |
| High | Rotate the Chargebee API key (printed once during the audit) and the 12-char webhook password | ops |
| Medium | `MAIL_PASSWORD` placeholder — email disabled | ops |
| Medium | `payment_*` / `invoice_*` are not subscribed by any endpoint | dashboard decision |
| Medium | Identity repair of the 11 twin-keyed rows (`SUBSCRIPTION_MIGRATION_PLAN.md`) — **not executed** | needs approval |
| Low | No alerting on `/api/health`, `DEAD_LETTER` growth or webhook 401s | ops |

