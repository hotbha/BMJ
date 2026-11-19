# Configuration Sync Report

**Date:** 2026-11-19 · **Direction:** `X:\BMJ\.env` → `/home/bmj/bmj/.env`
**Method:** merge (not blind overwrite), backup first, restart `bmj-api` only.
**No application code changed, no JAR rebuilt, no redeploy** — the running JAR hash is identical
before and after (`bd559ef8…8049dc`).

---

## 1. Old VPS fingerprint

`env_fingerprint.sh` (sha256 of each value, first 12 chars — values never printed), CR-normalised:

```
DB_NAME 1d95d5a5d001 · DB_USERNAME 9377bec70bc5 · DB_PASSWORD bc34b57e306f
DB_ROOT_PASSWORD 62ee6240245f · CHARGEBEE_SITE 9a53dad6bf8e
WEBHOOK_USERNAME e0f5af2155ac · WEBHOOK_PASSWORD 23912d90fc89
ADMIN_USER 91d0a772443a · ADMIN_PASSWORD 4d1996e34cb6 · JWT_SECRET 8c684dfaee13
MAIL_PASSWORD 3e813173f7e6 · CHARGEBEE_API_KEY a939bbcd287c
```

**12 keys, CRLF endings, mode 600.** Critically: **no `FAST2SMS_API_KEY` at all** — SMS could never work.

## 2. Why this was a merge, not a copy

A blind copy would have broken the running deployment:

| Key | Local value | Effect of overwriting | Decision |
|---|---|---|---|
| `DB_PASSWORD` | 8 chars | MySQL was **initialised** with the VPS 32-char password; the app would fail to connect | **kept VPS value** |
| `DB_ROOT_PASSWORD` | *absent locally* | would have been deleted | **kept VPS value** |
| `ADMIN_PASSWORD` | **empty** | would blank the Spring Security admin account | **kept VPS value** |

Everything else comes from local, because local is the declared source of truth. Every preserved value
was re-checked as non-empty before writing (`env_merge.sh` aborts otherwise).

## 3. New VPS fingerprint

```
lines 59 · CRLF 0 · mode 600 · backup .env.bak-20261119-162203
keys: ADMIN_PASSWORD ADMIN_USER API_BASE_URL CHARGEBEE_API_KEY CHARGEBEE_DASHBOARD_PASS
      CHARGEBEE_DASHBOARD_USER CHARGEBEE_SITE DB_HOSTNAME DB_NAME DB_PASSWORD DB_PORT
      DB_ROOT_PASSWORD DB_USERNAME FAST2SMS_API_KEY FAST2SMS_BASE_URL FAST2SMS_SENDER_ID
      FLUTTER_API_URL GOOGLE_CLIENT_ID GOOGLE_WEB_CLIENT_ID JWT_EXPIRATION_MS JWT_SECRET
      LOGGING_LEVEL MAIL_FROM MAIL_HOST MAIL_PASSWORD MAIL_PORT MAIL_USERNAME
      SPRING_PROFILES_ACTIVE WEBHOOK_PASSWORD WEBHOOK_USERNAME
```

Line endings normalised to LF — the old CRLF file had been silently corrupting value-hash comparisons.

## 4. Variables corrected

| Variable | Before | After |
|---|---|---|
| `FAST2SMS_API_KEY` | **absent** | present, 80 chars |
| `FAST2SMS_SENDER_ID`, `FAST2SMS_BASE_URL` | absent | present |
| `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_FROM` | absent | present |
| `MAIL_PASSWORD` | placeholder | real, 12 chars |
| `GOOGLE_CLIENT_ID`, `GOOGLE_WEB_CLIENT_ID` | absent | present, 71 chars |
| `JWT_SECRET` | VPS-generated | local value (old sessions invalidated; there were none) |
| `ADMIN_USER` | `bmjadmin` | local value |
| `DB_PASSWORD`, `DB_ROOT_PASSWORD`, `ADMIN_PASSWORD` | present | **preserved deliberately** (§2) |

**Second, equally important fix:** `docker-compose.prod.yml` never forwarded `FAST2SMS_*`, `MAIL_*` or
`GOOGLE_*` into the container — with only `.env` corrected the app would still have seen nothing. Those
were added to the service `environment:` block.

## 5. Restart result

```
Container bmj-sql Healthy → bmj-api Started
api responding after 25s
restarts=0 status=running
/app/app.jar sha256 = bd559ef8…8049dc   (unchanged — no rebuild, no redeploy)
Started bmjServer in 21.006 seconds
Webhook Basic Auth configured for user 'support@bookmyjuice.co.in'
HikariPool-1 - Start completed            (the preserved DB_PASSWORD works)
```

Runtime verification (`printenv`, presence + length only): `FAST2SMS_API_KEY` **len=80**,
`MAIL_PASSWORD` len=12, `WEBHOOK_USERNAME` len=25, `WEBHOOK_PASSWORD` len=14, `CHARGEBEE_API_KEY`
len=37, `MAIL_HOST` len=12, `MAIL_USERNAME` len=25, `JWT_SECRET` len=62, `ADMIN_PASSWORD` len=32
(not blanked), `DB_PASSWORD` len=32 (preserved), `GOOGLE_CLIENT_ID` len=71.

Health: `{"timestamp":"2026-11-19T21:57:13Z","status":"UP"}`.

## 6. Post-sync validation results

### OTP — API **PASS**, delivery **FAIL**

```
POST /api/auth/send-otp → http=200  0.899s
{"message":"Success: OTP sent! Check console for OTP (Dev mode)"}
[DEV] OTP for 9999999911: 212548 (SMS not sent - check Fast2SMS config)
```

The endpoint works and generates an OTP, but the response itself says "Dev mode".

### SMS delivery — **FAIL, provider-side**

```
ERROR c.bookmyjuice.util.SmsService - Fast2SMS API returned HTTP 401 for phone 9999999911:
{"return":false,"status_code":428,"message":"Quick API Access is disabled."}
```

**The key now reaches Fast2SMS** — a different failure from before (no key at all). The provider rejects
the account with *"Quick API Access is disabled"*, which is a Fast2SMS account setting (API access /
plan / KYC), not a BMJ defect. Nothing to fix in the code; the account must enable API access.

### Email — **PARTIAL**

```
POST /api/auth/send-email-verification → http=200  2.07s
{"message":"Success: Verification code sent to qa-nonexistent@bookmyjuice.co.in"}
[DEV] Email verification code for qa-nonexistent@bookmyjuice.co.in: 467802
```

The flow works end to end, but the mail service also falls back to console logging — **no SMTP send is
confirmed** even though the credentials are now present.

### Webhook — **improved from 401 to 400**

```
3.215.11.205 … [19/Nov/2026:14:57:07] "POST /api/webhooks/subscriptions" 401 … "ChargeBee"
3.215.11.205 … [19/Nov/2026:15:57:12] "POST /api/webhooks/subscriptions" 400 55 … "ChargeBee"
```

**Authentication now passes.** 400 is the payload guard rejecting a body with no usable `id` — a large
step from the 401 storm. `webhook_events` is still empty because a 400 is rejected before the controller
claims the event; the payload that arrived had no `id` (consistent with a Chargebee endpoint-validation
ping rather than a real event).

## 7. Summary

| Item | Result |
|---|---|
| Backup taken | ✅ `.env.bak-20261119-162203` |
| Local values applied | ✅ 18 new keys + 5 changed values |
| Deployment-critical secrets preserved | ✅ DB_PASSWORD, DB_ROOT_PASSWORD, ADMIN_PASSWORD |
| Compose now forwards SMS/mail/Google vars | ✅ |
| Container restarted, no rebuild | ✅ same JAR hash |
| Health after restart | ✅ UP |
| OTP API | ✅ 200 |
| SMS delivery | ❌ Fast2SMS: "Quick API Access is disabled" |
| Email delivery | ⚠️ 200 + dev fallback, no SMTP send |
| Webhook auth | ⚠️ 401 → **400** (auth fixed; payload lacked `id`) |

## 8. What is still needed

1. **Fast2SMS account**: enable API access / complete KYC so `status_code 428` clears.
2. **Mail**: the service still logs instead of sending — confirm whether an environment flag gates the
   real send, then either enable it or accept console mode as the current behaviour.
3. **Webhook**: send one real event (not a validation ping) and confirm a `webhook_events` row with
   `COMPLETED`.

