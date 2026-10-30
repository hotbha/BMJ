# B5_SMOKE_TEST_PLAN.md

**Companions:** `PRODUCTION_READINESS_REPORT.md` (findings + §3 evidence), `BMJ_LAUNCH_CHECKLIST.md` (`B5` gate), `DEPLOYMENT_RUNBOOK.md` (shipping).
**Automation:** `ops/smoke_test.ps1` implements §2 and §3.2 as a single runnable command.

---

## 0. What this gate is for

`B5` exists to answer one question with evidence rather than opinion: **does the exact artifact we intend to ship actually work against the exact environment our customers will use?**

Two things are deliberately *not* in scope: code quality, and any change to the frozen architecture. A smoke test that requires a code change to pass is a **finding**, and is written up in the report — never patched here.

**Chargebee rule for this whole plan:** every probe is read-only. Creating a customer, pausing, resuming or cancelling a subscription requires explicit go-ahead first — those steps are quarantined in §4 and are **not** part of the automated script.

---

## 1. Preconditions

| # | Condition | Why | Check |
| :--: | :--- | :--- | :--- |
| 1 | Release artifact built | The thing under test | `Get-ChildItem bmjServer\target\*.jar` |
| 2 | `CatalogController.java` **tracked** | `PR-1` — a clean checkout otherwise 404s on flow 1 | `git -C bmjServer ls-files --error-unmatch src/main/java/com/bookmyjuice/controllers/CatalogController.java` |
| 3 | Test account exists with a known password | Probes 7-10 | §2.2 seed step, or a real signup |
| 4 | A reachable base URL | Probes need a target | §2.1 (local) or `PR-4` resolved (deployed) |
| 5 | `chargebee.sync.enable-startup-sync=false` **unless** you intend a sync | Keeps the smoke from touching Chargebee data on boot | `--chargebee.sync.enable-startup-sync=false` |
| 6 | **The catalog's items carry ItemPrices in Chargebee** | `PR-18`: probe 2b cannot pass without them. Today **0 of the 15 `bmj-item-*` items have a price**, so a failure there is a *data* gap, not a code regression | re-run the read-only census in report §3.5 **before** blaming the code |

> Preconditions 2 and 6 are the two that silently ruin this gate — one hides a route, the other hides an empty price list. Verify both; do not assume either.
>
> **Probe 2b is expected to FAIL until `PR-18` is closed.** Record that failure as `PR-18`; do **not** weaken the probe to make the run green — that is the hollow pass this plan exists to prevent.

---

## 2. Variant A — local smoke (no host required)

This is the variant that was **actually executed on 16 October 2026**; the results are recorded in the report §3.2. It proves the artifact runs and the flows work. It cannot prove anything about TLS, DNS, nginx, systemd or a real customer.

### 2.1 Bring up an isolated backend

```powershell
# 1. Throwaway MySQL 8.0 on 3307 - never reuse a database you care about.
docker run -d --name bmj-smoke-mysql `
  -e MYSQL_ROOT_PASSWORD=rootpw -e MYSQL_DATABASE=bmj_db `
  -e MYSQL_USER=bmj -e MYSQL_PASSWORD='PASS@123' `
  -p 3307:3306 mysql:8.0

# 2. Build the release artifact exactly as CI does.
cd x:\BMJ\bmjServer
.\mvnw.cmd -o -q -DskipTests package

# 3. Load credentials into THIS shell's environment.
#    java -jar does NOT honour spring.dotenv.location, so the variables must be
#    exported explicitly - ${DB_USERNAME} would otherwise reach MySQL as a literal.
Get-Content ..\.env | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
    [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

# 4. Run it on a free port (8080 may already be held by another local service).
java -jar target\com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar `
  --server.port=8085 `
  --spring.profiles.active=dev `
  --spring.datasource.url="jdbc:mysql://127.0.0.1:3307/bmj_db?allowPublicKeyRetrieval=true&useSSL=false" `
  --chargebee.sync.enable-startup-sync=false
```

Wait for `GET /api/health` to return `200 UP` before probing:

```powershell
1..40 | ForEach-Object {
  try { (Invoke-WebRequest http://127.0.0.1:8085/api/health -UseBasicParsing -TimeoutSec 5).Content; break }
  catch { Start-Sleep -Seconds 3 }
}
```

> **Signup contract since 18 Oct 2026 (mandatory email):** `POST /api/auth/phone-signup`
> requires a real `email` **and** an `emailVerificationToken` minted by
> `/api/auth/verify-email-code`; the address block is optional. Seeded accounts must
> therefore carry a real email, and a phone-first signup probe is a four-call chain:
> `send-otp` -> `login-otp` -> `send-email-verification` + `verify-email-code` ->
> `phone-signup`. Read both codes from `bmjServer/logs/local-run.log`
> (`[DEV] OTP` / `[DEV] Email verification code`). Full contract: `docs/API.md`,
> rationale: `AUTH_SIMPLIFICATION_IMPLEMENTATION_PLAN.md` §16.


### 2.2 Seed the test account (fresh DB only)

`db/migration/V6__seed_test_accounts.sql` is **not applied automatically** — there is no Flyway/Liquibase in `pom.xml` (`PR-13`). On a fresh database, Hibernate creates the tables and a startup seeder creates the roles, but there are **no users**, and `signin` correctly returns `400`. Seed one, using the same hash `V6` specifies for `Test@1234`:

```powershell
cd x:\BMJ\bmjServer
$sql = @'
INSERT IGNORE INTO users (id,username,email,password,first_name,last_name,phone,token_version,deleted,chargebee_customer_id)
VALUES (1,'9999999901','ta01@bookmyjuice.co.in','$2b$12$mpZ8lsANcb/B4X5gQsxoM.vUsJoIx5gnx9EKQa5vDb/5OzHzweM22','Test','User One','9999999901',1,0,NULL);
INSERT IGNORE INTO user_roles (user_id,role_id) SELECT 1,id FROM roles WHERE name='ROLE_USER';
'@
$sql | Set-Content -Path target\smoke_seed.sql -Encoding ascii
cmd /c "docker exec -i bmj-smoke-mysql mysql -ubmj -pPASS@123 bmj_db < target\smoke_seed.sql"
```

`chargebee_customer_id` is deliberately `NULL`: that is what lets probe 10 verify `D-6`'s null-handling and probe 9 expose `PR-15`.

### 2.3 Run the battery

```powershell
powershell -File x:\BMJ\ops\smoke_test.ps1 -BaseUrl http://127.0.0.1:8085
```

Expected on a tree with `PR-1`, `PR-14`, `PR-16`, `PR-17` fixed and a fresh DB: **10 passed, 0 failed, 1 warning** (probe 9's `PR-15` caveat — 11 probes total). On the tree as it stands today, probes **2b** (`prices:[]`, `PR-17`), **8** (hash leak, `PR-14`) and intermittently **2** (`200 []`, `PR-16`) fail **by design** — those failures *are* the open findings, and the script exiting non-zero is the correct outcome.

Re-run with `-Seeded` once the account genuinely has a `chargebee_customer_id`, which turns probe 9 into a hard failure instead of a warning.

### 2.4 Known-good baseline (16 Oct 2026)

| Probe | Observed |
| :--- | :--- |
| 1 health | `200 {"status":"UP"}` |
| 2 catalog | `200`, 7 657 bytes of real test-site items |
| 3-4 test routes | `404` — `B2` closed |
| 5-6 anon protected | `401` both |
| 7 signin | `200` + JWT, `roles=ROLE_USER` |
| 8 profile | `200` — **leaked `"password":"$2b$12$…"`** → `PR-14` |
| 9 subscriptions (auth) | **`401 {"error":"User not authenticated"}`** → `PR-15` |
| 10 orders (auth) | `200 []` — `D-6` verified |

Any deviation from this baseline at probe 2 or 7 means the local environment is wrong, not that the baseline is stale.

---

## 3. Variant B — deployed smoke (requires `PR-4` resolved)

The same battery, plus the checks that only a real host can answer. **None of these has ever been executed**, because no host exists.

### 3.1 Pre-deploy assertions

These catch the whole class of "it deployed but the profile is wrong" — the failure mode that costs the most and shows up the least.

```powershell
$h = 'api.<your-host>'      # decide the domain FIRST - the docs disagree (.com vs .co.in)

# PR-5: HTTPS must work, and plain HTTP must redirect
(Invoke-WebRequest "https://$h/api/health" -UseBasicParsing).StatusCode        # expect 200
try { Invoke-WebRequest "http://$h/api/health" -UseBasicParsing -MaximumRedirection 0 }
catch { $_.Exception.Response.StatusCode.value__ }                            # expect 301/308
```

On the VPS itself (`ssh $VPS_USER@$VPS_HOST`):

```bash
# PR-12: the prod profile MUST be active - the single most likely silent failure
sudo systemctl show bmj-backend -p Environment | tr ' ' '\n' | grep -i profile
journalctl -u bmj-backend --since '-10 min' | grep -i profile
# expect: SPRING_PROFILES_ACTIVE=prod  and  "The following 1 profile is active: prod"

# PR-12: ddl-auto must be validate, not update
journalctl -u bmj-backend --since '-10 min' | grep -iE "ddl-auto|Hibernate|schema"

# PR-13: if Flyway was wired, history must be non-empty
mysql -u"$DB_USERNAME" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT version,description,success FROM flyway_schema_history;"

# PR-5: real certificate, no stray plaintext listener
sudo nginx -T | grep -E "listen (80|443)|ssl_certificate"
echo | openssl s_client -connect "$h:443" -servername "$h" 2>/dev/null | openssl x509 -noout -issuer -dates
```

### 3.2 The battery

```powershell
powershell -File ops\smoke_test.ps1 -BaseUrl "https://$h" -Seeded
```

`-Seeded` makes probe 9 a **hard** failure rather than a known caveat: on a real account with a `chargebee_customer_id`, `/api/subscriptions/my` must return `200`.

### 3.3 Deploy-path checks (verify by hand, record the output)

| # | Check | Command / evidence | Expect |
| :--: | :--- | :--- | :--- |
| D1 | Deployed artifact is the one CI built | `sha256sum /home/bmj/bmj/current.jar` vs the workflow artifact | identical |
| D2 | Survives a restart | `sudo systemctl restart bmj-backend`, then re-run §3.2 | same result |
| D3 | Starts on boot | `systemctl is-enabled bmj-backend` | `enabled` |
| D4 | Catalog reachable **through nginx**, with prices | §3.2 probes 2 and 2b | 200 **with prices** |
| D5 | Pool survives a small burst | 10 parallel `GET /api/health` | all 200, no pool-exhaustion log |
| D6 | Logs hold no secrets | `journalctl -u bmj-backend \| grep -iE "password\|secret\|api_key"` | no hits |
| D7 | Shipped APK has cleartext off | inspect the built APK manifest | `false` (after the HTTPS cutover) |

---

## 4. Steps that touch **live Chargebee** — require explicit go-ahead

**Do not run these without a recorded go-ahead.** They are the only steps in this plan that mutate Chargebee state.

| Step | What it does | Preconditions |
| :--- | :--- | :--- |
| `B4` — customer backfill | signs up via `unified-signup` / `login-otp` / `google` (`D-2`) so a Chargebee customer + subscription are created | a **test site**, never live; record the created customer/subscription ids for cleanup |
| `B6` — in-app pause/cancel | pauses then resumes a test subscription through the app UI, per `B6_DECISION_REPORT.md` | `B4` done; `PR-15` understood (below); recorded go-ahead |
| Cleanup | cancels/deletes anything created above | same session, so nothing is left behind |

**`B6` caveat (from live evidence):** `B6`'s verdict — "the subscriber can pause/cancel from inside the app" — depends on `GET /api/subscriptions/my`, which returns **401** for any account whose `chargebee_customer_id` is null (`PR-15`). So `B6` can only be honestly closed:

- after `B4` has given the test account a customer id, **and**
- with `PR-15` either fixed or explicitly accepted.

Otherwise, pause/cancel is verified to work *only* for accounts that already have a Chargebee customer — which is not what the verdict claims.

---

## 5. Evidence to capture (fill this in during the run)

| Item | Where it goes |
| :--- | :--- |
| Full `smoke_test.ps1` output, both variants | paste into `PRODUCTION_READINESS_REPORT.md` §3 or attach a run log |
| `journalctl` excerpt showing the active profile | proves `PR-12` |
| `sha256` of the deployed `current.jar` and of the local build | proves what was smoked is what shipped |
| `openssl` certificate output | proves `PR-5` |
| Chargebee customer/subscription ids created in §4, plus cleanup confirmation | audit trail for `B4`/`B6` |
| The APK file, its hash, and the `--dart-define` used | proves `PR-3` |

---

## 6. Pass / fail criteria and sign-off

**Green** requires probes 1, 2, 2b, 3, 4, 5, 6, 7, 8, 9 and 10 to pass, §3.1 and §3.3 to pass, and **no probe to be skipped**.

**But probe 2b cannot pass yet.** It asserts the catalog carries prices, and `PR-18` shows no price records exist for any of the 15 items — so as the data stands today, `B5` is **unachievable** rather than failing. Close `PR-18` first (a Chargebee write — `D4`/`D6`), then re-run. Recording a green `B5` with probe 2b skipped, or with its assertion softened, would be precisely the hollow pass this plan exists to prevent.

| Result | Meaning |
| :--- | :--- |
| Any probe **FAIL** | `B5` is not green. Record the finding; do not proceed to the tag. |
| Probe 2b FAIL, **and** the §3.5 census still shows 0 prices on `bmj-item-*` | `PR-18` is open — a **data** gap, not a code regression. Does not block the code fix. |
| Probe 2b FAIL, **but** the census shows prices now exist | `PR-17`'s code fix is missing or wrong — this is the real regression signal. |
| Probe 9 **WARN** on the deployed run | acceptable only if `PR-15` is accepted in writing (`D3`); otherwise treat as FAIL |
| Any probe **skipped** | `B5` is not green — a skipped probe is an unverified claim |
| Probes pass but §3.1/§3.3 not run | `B5` is **partially** green: flows verified, environment unverified. Must be stated exactly that way in the checklist. |

Sign-off: `B5` is closed by a named person recording the date, the artifact hash, the base URL and the table above. **"It worked when I tried it" is not evidence** — paste the output.

---

## 7. Teardown (after a local run)

```powershell
# stop the smoke backend
$p = Get-Content x:\BMJ\bmjServer\smoke_backend.pid -ErrorAction SilentlyContinue
if ($p) { Stop-Process -Id $p -Force }

# remove the throwaway database
docker rm -f bmj-smoke-mysql
```

The seeded account (`9999999901`) lives **only** inside that container, so removing it removes the seed. **Never seed that account into production.**

**Leftover check:** `docker ps -a | Select-String bmj-smoke` returns nothing, and port 3307 is free.