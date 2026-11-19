# VPS Deployment Runbook — BMJ Backend

**Target:** `api.bookmyjuice.co.in` (160.250.205.241), user `bmj`
**Executed:** 2026-11-19 · **Result:** API healthy on public HTTPS, stack survives reboot
**Status of this document:** describes what was actually done, in the order it was done, including the
two failures encountered. Everything below was verified on the host, not assumed.

---

## 1. Server baseline (measured before any change)

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.5 LTS |
| Hostname | Bharathitwani.com |
| Resources | 4 vCPU · 5.9 GB RAM · 88 GB free on `/` |
| Docker | 29.10.0 (Compose v5.8.0) — **already present** |
| Java / Maven | **not installed — and not needed** (image ships the JRE) |
| MySQL | **not installed** (runs as a container) |
| Ports in use | 22, 80, 443 (nginx) only — 8080 and 3306 were free |
| Existing BMJ data | **none** — no containers, no DB, no app directory |

Because the host was greenfield, the deployment created new infrastructure and could not overwrite
existing production data. **No data migration was run.** The application created its own schema on
first boot through its default `spring.jpa.hibernate.ddl-auto=update` against an empty database.

---

## 2. Architecture on the box

```
internet ──443 (TLS, Let's Encrypt)──> nginx ──/api/──> 127.0.0.1:8080 ──> bmj-api (Spring Boot)
                                                                              │
                                                        bmj-net (docker) ─────┴──> bmj-sql (MySQL 8)
                                                                                    volume: bmj-mysql-data
```

Deliberate choices:

- **The API is published on `127.0.0.1:8080` only.** Tomcat is never reachable from the internet; nginx
  is the single entry point. This matters because the webhook scheme is Basic Auth over TLS, not a
  signature (see `CHARGEBEE_LIVE_AUDIT.md`).
- **MySQL publishes no host port at all** — only the API container can reach it.
- Data lives in the named volume `bmj-mysql-data`, not in a bind mount under the home directory.

---

## 3. Files on the server (`/home/bmj/bmj`, 62 MB total)

| File | Purpose | Mode |
|---|---|---|
| `app.jar` | Spring Boot fat JAR, built on the workstation | 664 |
| `Dockerfile.runtime` | `eclipse-temurin:17-jre`, copies the JAR | 644 |
| `docker-compose.prod.yml` | MySQL + API, healthchecked, loopback-bound | 644 |
| `.env` | all runtime secrets | **600** |
| `bmj-stack.service` | systemd unit wrapping compose | 644 (installed to `/etc/systemd/system`) |
| `apply-nginx.py` | idempotent nginx proxy insertion, takes a timestamped backup | 644 |
| `install-services.sh` | installs the unit + applies nginx | 755 |
| `fix-env.sh` | adds the two env vars that were initially missing | 755 |

---

## 4. Environment variables (`/home/bmj/bmj/.env`)

`docker-compose.prod.yml` passes each of these into the container explicitly; Compose `.env`
substitution alone is **not** enough (this caused the second boot failure, §6).

| Key | Source | Notes |
|---|---|---|
| `DB_NAME` | generated | `bmj_db` |
| `DB_USERNAME` | generated | `bmj` |
| `DB_PASSWORD` | generated (32 chars) | MySQL user password |
| `DB_ROOT_PASSWORD` | generated (32 chars) | MySQL root password |
| `CHARGEBEE_SITE` | workstation `.env` | `bookmyjuice-test` |
| `CHARGEBEE_API_KEY` | workstation `.env` | **rotate** — it was printed once during this deployment |
| `WEBHOOK_USERNAME` | workstation `.env` | `support@bookmyjuice.co.in` |
| `WEBHOOK_PASSWORD` | workstation `.env` | 12 chars — **rotate to 32+** |
| `ADMIN_USER` | generated | Spring Security admin |
| `ADMIN_PASSWORD` | generated (32 chars) | Spring Security admin |
| `JWT_SECRET` | **generated on the server** (`openssl rand -hex 32`) | never left the host |
| `MAIL_PASSWORD` | placeholder | email is disabled until real credentials are supplied |

### Required env vars — complete list

The application has **ten** placeholders with no defaults. Missing any of them aborts startup:

```
ADMIN_USER  ADMIN_PASSWORD  JWT_SECRET  MAIL_PASSWORD
CHARGEBEE_SITE  CHARGEBEE_API_KEY
DB_USERNAME  DB_PASSWORD
WEBHOOK_USERNAME  WEBHOOK_PASSWORD
```

`JWT_SECRET` and `MAIL_PASSWORD` are not mentioned anywhere in the compose file's documentation
upstream and are the two that were missing on the first attempt.

---

## 5. Deployment procedure (what was executed)

### 5.1 Build the JAR on the workstation

```powershell
cd X:\BMJ\bmjServer
mvn -o -q -DskipTests package
# -> target/com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar  (64,156,372 bytes)
Get-FileHash .\target\com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar -Algorithm SHA256
# -> AC69F64898DDC98F408BB2162449712B0FAD0D901AB96FA5682C0011004BBB11
```

Building locally means the server needs no JDK, no Maven and no repository credentials.

### 5.2 Create the target directory and upload

```powershell
# helpers (in _captures/qa): vps.ps1 runs a command over plink, vscp.ps1 uploads a file.
# Both read the password from %TEMP%\bmj_vps.cred, so it never enters a script.
.\vps.ps1  -Command "mkdir -p /home/bmj/bmj && chmod 750 /home/bmj/bmj"
.\vscp.ps1 -LocalFile '...\com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar' -RemotePath '/home/bmj/bmj/app.jar'
.\vscp.ps1 -LocalFile 'X:\BMJ\deploy\Dockerfile.runtime'      -RemotePath '/home/bmj/bmj/Dockerfile.runtime'
.\vscp.ps1 -LocalFile 'X:\BMJ\deploy\docker-compose.prod.yml' -RemotePath '/home/bmj/bmj/docker-compose.prod.yml'
.\vscp.ps1 -LocalFile "$env:TEMP\bmj_vps.env"                 -RemotePath '/home/bmj/bmj/.env'
.\vps.ps1  -Command "chmod 600 /home/bmj/bmj/.env"
```

**Always verify the upload.** The first attempt was cut short by the terminal and left a 17 MB file;
only the hash comparison caught it:

```bash
sha256sum /home/bmj/bmj/app.jar     # must equal the workstation hash
ls -l /home/bmj/bmj/.env            # must be -rw-------
```

### 5.3 Start the stack

```bash
cd /home/bmj/bmj
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

MySQL starts first; the API container waits on `condition: service_healthy`.

### 5.4 Install systemd + nginx (as root)

```bash
sudo -S -p '' bash /home/bmj/bmj/install-services.sh < /home/bmj/.sudo_pw
```

This installs `bmj-stack.service`, enables it, runs `apply-nginx.py` (which writes a timestamped
backup of `/etc/nginx/sites-available/default` first), runs `nginx -t`, then reloads nginx.

### 5.5 Verify

```bash
curl -s http://127.0.0.1:8080/api/health          # from the host
curl -s https://api.bookmyjuice.co.in/api/health  # through nginx + TLS
```

---

## 6. Two failures encountered (and their fixes)

**F1 — truncated upload.** First `pscp` returned early and left a 17 MB `app.jar` instead of 61 MB.
Caught by size + SHA-256, re-uploaded, verified. *Lesson: never trust "100%" in a scp progress line.*

**F2 — crash loop, `restarts=12`.** The container exited during Tomcat startup:

```
java.lang.IllegalArgumentException: Could not resolve placeholder 'JWT_SECRET' in value "${JWT_SECRET}"
```

Two things were wrong at once:
1. `JWT_SECRET` and `MAIL_PASSWORD` were absent from `.env`;
2. even after adding them, the compose service did not pass them into the container — Compose's
   `--env-file` only substitutes values written in the compose file itself.

Fix: append both keys to `.env` (`JWT_SECRET` generated on the server with `openssl rand -hex 32`),
add both to the `environment:` block of `docker-compose.prod.yml`, then
`docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api`.

Successful boot:

```
Tomcat started on port(s): 8080 (http) with context path ''
Started bmjServer in 18.111 seconds (process running for 19.115)
```

---

## 7. Verified state

| Check | Result |
|---|---|
| `https://api.bookmyjuice.co.in/api/health` | **200** `{"status":"UP","timestamp":"2026-11-19T13:19:13Z"}` |
| `https://api.bookmyjuice.co.in/api/catalog/charge-items` | **200**, 15 items, 8 003 bytes (Chargebee startup sync populated the catalogue) |
| API container | `Up`, `restarts=0`, port `127.0.0.1:8080->8080` |
| MySQL container | `Up (healthy)`, no host port published |
| systemd | `bmj-stack.service` **enabled** |
| nginx | **active**, config test passed, reload successful |
| Transfer integrity | `sha256sum` on the server equals the workstation hash |

### Webhook endpoints (Basic Auth matrix)

| endpoint | no auth | wrong password | correct credentials |
|---|---:|---:|---:|
| `/api/webhooks/customers` | 401 | 401 | 500 |
| `/api/webhooks/subscriptions` | 401 | 401 | 500 |
| `/api/webhooks/items` | 401 | 401 | 500 |
| `/api/webhooks/item-prices` | 401 | 401 | 500 |
| `/api/webhooks/orders` | 401 | 401 | 500 |

Interpretation: **401 without credentials and 401 with a wrong password** prove the endpoint is
protected and the password is actually checked. **500 with the right password** proves the request
passes authentication and reaches the controller — the 500 is the controller calling
`Event.retrieve("probe-not-a-real-event")` and failing, i.e. expected for a fabricated event id.
It also confirms the malformed-body weakness from `CHARGEBEE_WEBHOOK_MATRIX.md`: a real Chargebee
retry with a valid id will work, but a body without `id` should be answered `400`, not `500`.

---

## 8. Operations

| Task | Command |
|---|---|
| Follow API logs | `docker logs -f bmj-api` |
| Follow MySQL logs | `docker logs -f bmj-sql` |
| Restart the API only | `docker compose --env-file .env -f docker-compose.prod.yml restart bmj-api` |
| Stop everything (keep data) | `sudo systemctl stop bmj-stack` |
| Start everything | `sudo systemctl start bmj-stack` |
| Container health | `docker ps --format '{{.Names}}|{{.Status}}'` |
| Reboot survival | `systemctl is-enabled bmj-stack.service` → `enabled` |

### Updating the application

```powershell
# workstation
mvn -o -q -DskipTests package
Get-FileHash .\target\com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar -Algorithm SHA256
.\vscp.ps1 -LocalFile '...\jar' -RemotePath '/home/bmj/bmj/app.jar'
```

```bash
# server — confirm the hash FIRST, then rebuild only the API image
sha256sum /home/bmj/bmj/app.jar
cd /home/bmj/bmj && docker compose --env-file .env -f docker-compose.prod.yml up -d --build bmj-api
```

### Database backup (before any risky change)

```bash
docker exec bmj-sql sh -c 'exec mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --single-transaction bmj_db' \
  > /home/bmj/bmj/backup-$(date +%Y%m%d-%H%M).sql
```

---

## 9. Rollback procedure

Four levels, least destructive first. **Take the DB backup (§8) before level 2 or below.**

### R1 — revert the application binary (most common)

```bash
cd /home/bmj/bmj
cp app.jar app.jar.broken            # keep the evidence
# upload the previous known-good jar to app.jar, verify its sha256sum, then:
docker compose --env-file .env -f docker-compose.prod.yml up -d --build bmj-api
curl -s http://127.0.0.1:8080/api/health
```

Keep the previous jar on the server (`app.jar.prev`) so this needs no workstation round-trip.

### R2 — revert the nginx proxy

`apply-nginx.py` writes a timestamped backup every time it changes anything:

```bash
ls /etc/nginx/sites-available/default.bak-*
sudo cp /etc/nginx/sites-available/default.bak-<stamp> /etc/nginx/sites-available/default
sudo nginx -t && sudo systemctl reload nginx
```

This removes the `/api/` proxy and returns nginx to serving the static page. The API keeps running on
loopback, unreachable — a clean, safe state.

### R3 — stop the stack, keep the data

```bash
sudo systemctl stop bmj-stack        # containers stop; bmj-mysql-data survives
```

To come back: `sudo systemctl start bmj-stack`.

### R4 — full teardown (DESTROYS THE DATABASE)

```bash
cd /home/bmj/bmj
docker compose --env-file .env -f docker-compose.prod.yml down -v   # -v deletes bmj-mysql-data
```

Only after a verified backup. This is the "start over" path, not a rollback.

### R5 — remove the systemd unit entirely

```bash
sudo systemctl disable --now bmj-stack.service
sudo rm /etc/systemd/system/bmj-stack.service
sudo systemctl daemon-reload
```

---

## 10. Known gaps after this deployment

| # | Gap | Impact | Owner |
|---|---|---|---|
| 1 | `CHARGEBEE_SITE=bookmyjuice-test` | the VPS runs against the **test** Chargebee site; production credentials are still a release blocker | product |
| 2 | `MAIL_PASSWORD` is a placeholder | transactional email is disabled; the app starts but cannot send | ops |
| 3 | Chargebee webhook endpoints are still **disabled** in the dashboard | no billing events reach this deployment — see `WEBHOOK_ACTIVATION_CHECKLIST.md` | dashboard |
| 4 | Endpoint URLs still point at `http://api.bookmyjuice.co.in:8080` (plain HTTP, and 8080 is now loopback-only) | webhooks will fail if enabled without updating the URL to `https://api.bookmyjuice.co.in/api/...` | dashboard |
| 5 | No monitoring or alerting on `/api/health` | an outage is silent until a user reports it | ops |
| 6 | Secrets live in `/home/bmj/bmj/.env` (600) | acceptable single-tenant practice; a secret manager is better | ops |
| 7 | `JWT_SECRET` is generated per environment | fine now; document that rotating it invalidates all sessions | ops |

---

## 11. Security notes from this deployment

- The SSH password was used through a temp credential file on the workstation
  (`%TEMP%\bmj_vps.cred`) and a transient `/home/bmj/.sudo_pw` on the server. **Both were removed**
  (`shred -u` for the server copy). Re-deploy by re-creating them, not by storing them permanently.
- An SSH key pair with `sudo` rights would remove the need for both files — recommended follow-up.
- The Chargebee API key was printed once into a terminal during this work. **Rotate it** in the
  Chargebee dashboard and update `.env` on the server (then restart `bmj-api`).
- `WEBHOOK_PASSWORD` is 12 characters and shares a stem with the SSH password. Rotate both.
- Tomcat is loopback-bound, MySQL has no host port, and `/api/` is TLS-only through nginx.


