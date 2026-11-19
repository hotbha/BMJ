# End-to-End Validation Report

**Date:** 2026-11-19 · **Backend:** `865fb16` on `api.bookmyjuice.co.in` · **Device:** SM_G973W (Android 12)
**Scope:** real physical device via ADB, real backend, real Chargebee account. Nothing simulated.
**Companion reports:** `DEVICE_TEST_REPORT.md`, `WEBHOOK_VALIDATION_REPORT.md`,
`SYNC_VALIDATION_REPORT.md`, `QA_ACCOUNTS.md`

---

## Verdict

# **FAILED — 6 of 22 success criteria verified**

The device, deployment and catalogue path work. Everything that depends on **identity** (OTP → session
→ subscriptions → webhooks → self-heal) is blocked by configuration gaps outside the code: no SMS
provider, no mail credentials, and a **wrong webhook password stored in Chargebee**.

No criterion was marked PASS without evidence, and no blocked criterion was worked around by reading a
server-side OTP — that would have produced a false pass on "SMS received".

---

## Success criteria

| # | Criterion | Result | Evidence |
|---:|---|---|---|
| 1 | Device connected | **PASS** | `adb devices` → `192.168.1.7:5555 device product:beyond1qltecs model:SM_G973W` |
| 2 | App launches | **PASS** | `mCurrentFocus=…com.bookmyjuice.app/.MainActivity`; Impeller Vulkan+GLES init |
| 3 | Home screen loads | **PASS** | `e2e_01_launch.png` — 1080×2280, 47 colour buckets, non-flat luminance |
| 4 | Catalog loads | **PASS** | nginx `GET /api/v1/catalog/charge-items 200 8022 "Dart/3.12"`; Spring `Filtered to 20 CHARGE items out of 176` |
| 5 | Products visible | **PASS** | same call; 20 charge items returned and rendered |
| 6 | OTP works | **PARTIAL** | `POST /api/auth/send-otp` → 200, OTP generated — but response says "Dev mode" and delivery failed (see 7) |
| 7 | SMS received | **FAIL** | Fast2SMS now reached and rejects the account: `status_code 428 "Quick API Access is disabled"` |
| 8 | Google login works | **BLOCKED (policy)** | device holds only Bharat's personal Google account |
| 9 | Session persistence works | **NOT TESTED** | requires a session; 6–8 produced none |
| 10 | Chargebee customer exists (QA) | **FAIL** | no QA BMJ account; existing fixtures are unreachable |
| 11 | Chargebee subscription exists (QA) | **NOT CREATED** | would create real billing; needs approval |
| 12 | Subscription visible in app | **NOT TESTED** | needs a linked user |
| 13 | Customer webhook works | **FAIL** | no customer delivery attempted; endpoint enabled, no event occurred |
| 14 | Subscription webhook works | **FAIL (improved)** | auth now **passes** — Chargebee gets 400 instead of 401 — but the payload carried no `id`, so no event was claimed |
| 15 | `webhook_events` populated | **FAIL** | still **0 rows** (400 is rejected before the controller claims the event) |
| 16 | `processing_status = COMPLETED` | **FAIL** | no rows exist |
| 17 | Identity self-heal works | **NOT EXERCISED** | production has **0 users** |
| 18 | Email works | **PARTIAL** | `send-email-verification` → 200 and a code is generated, but the mail service logs `[DEV] …: 467802` — no SMTP send confirmed |
| 19 | No critical backend errors | **PASS** | no crash/ANR; no 5xx from the app |
| 20 | No dead-letter growth | **PASS (vacuous)** | 0 dead letters because 0 events were accepted |
| 21 | QA account documented | **PASS** | `QA_ACCOUNTS.md` records inventory, intent, blockers |
| 22 | QA account reusable | **BLOCKED** | account could not be created (6–7) |

Tally: **6 PASS** (1–5, 19) · **1 vacuous PASS** (20) · **7 FAIL** (7, 10, 13, 14, 15, 16, 18) ·
**8 BLOCKED / NOT TESTED** (6, 8, 9, 11, 12, 17, 22).

---

## Root causes — all configuration, none in the delivered code

### RC-1 — Chargebee's stored webhook password is wrong *(highest impact)*

| Evidence | Result |
|---|---|
| Chargebee deliveries in nginx log | 5 requests from `3.215.11.205`, UA `ChargeBee`, **all 401** |
| Server credentials against its own endpoint | **400** — accepted (the 400 is the payload guard) |
| Wrong password against the same endpoint | **401** |
| Container vs `.env` password hash | identical (`23912d90…`) — server is self-consistent |

The endpoint, the auth filter and the stored credential all work; Chargebee sends a different secret.
**Fix in Chargebee (Basic Auth password), not in the deployment.**

### RC-2 — No SMS provider
`FAST2SMS_API_KEY` is unset, so `OTPUtil` falls back to console logging and sends nothing. Blocks 6, 7
and therefore 9, 10, 12, 17, 22.

### RC-3 — Mail password is still the placeholder
`MAIL_PASSWORD=not-configured-email-disabled`. Blocks 18.

### RC-4 — No QA Google identity on the device
Only Bharat's personal account is present, which the QA policy forbids. Blocks 8.

### RC-5 — Device storage 100 % full (814 MB free)
Caused the first install to fail; solved with a 34.8 MB `--split-per-abi` release build. Not a product
defect, but it will recur.

---

## What is genuinely proven

1. **The app runs on the real device against the production VPS over HTTPS.** The catalogue request is
   in nginx from the phone's IP with a Dart user agent, answered 200 (8 022 bytes), and the backend
   logged the 176 → 20 item filter.
2. **The deployment is sound.** Health 200, catalogue 200, webhook endpoints correctly refuse
   unauthenticated (401) and malformed (400) traffic, and the server's own webhook credential
   authenticates.
3. **Chargebee reaches the VPS.** The 401s prove connectivity, not silence.
4. **The pull sync works.** 81 customers and 16 subscriptions mirrored, matching Chargebee's counts.
5. **No crashes, no ANR, no unhandled exceptions** in the app or the backend during this run.

## What cannot be claimed

- That webhooks are processed.
- That identity linking or self-heal works **in production** — no users exist to test with.
- That OTP, Google login, sessions, subscriptions-in-app or email work.

Claiming otherwise would require inventing evidence.

---

## Fix list, in dependency order

| # | Action | Unblocks |
|---:|---|---|
| 1 | Set Chargebee's webhook Basic Auth **password** to the `/home/bmj/bmj/.env` value, then resend an event | 13–16, makes 17 observable |
| 2 | Provision `FAST2SMS_API_KEY`, restart `bmj-api` | 6, 7, then 9–12, 22 |
| 3 | Create `BMJ-QA-PRIMARY` on a phone number that appears **once** in Chargebee | 9, 10, 12, 17 |
| 4 | Configure `MAIL_PASSWORD` | 18 |
| 5 | Add a QA Google account to the device | 8 |
| 6 | Approve or refuse creating a QA subscription in the live Chargebee site | 11 |
| 7 | Free ≥3 GB on the test device, or standardise on split-per-abi builds | smoother runs |

## Retest plan once 1–3 are done

1. Resend a subscription event → expect a `webhook_events` row with `COMPLETED`.
2. Register `BMJ-QA-PRIMARY` via OTP → expect a `users` row, a `chargebee_customer_id`, and
   `Identity link created: user … -> customer …` in the log.
3. Re-run drift: D1/D4 remain 0, **D3 should fall** as the new user links to its subscriptions.
4. Log out, log back in, restart the app → the subscription must stay reachable.

Until steps 1 and 2 are complete, criteria 6–17 remain unverifiable and the mission stays **FAILED**.

---

## Post-configuration-sync addendum (2026-11-19, after `CONFIGURATION_SYNC_REPORT.md`)

The local `.env` was merged onto the VPS (backup `.env.bak-20261119-162203`) and `bmj-api` restarted —
**same JAR `bd559ef8`, no rebuild, no redeploy**. Three of the four earlier root causes were addressed:

| Root cause | Was | Now |
|---|---|---|
| RC-2 no SMS provider | `FAST2SMS_API_KEY` absent | key present (80 chars) and **reaching Fast2SMS**; provider rejects the *account* with `428 "Quick API Access is disabled"` |
| RC-3 mail placeholder | `not-configured-email-disabled` | real credential present; flow returns 200 but still logs instead of sending |
| RC-1 webhook password | 5 × **401** | **400** — authentication now passes; payload arrived without `id` |
| RC-4 no QA Google account | unchanged | still blocked by policy |

**Net effect on the mission: still FAILED, but the two blockers that were *ours* are now cleared.** What
remains is one provider-account setting (Fast2SMS API access), one mail-mode question, and one real
webhook event to prove end-to-end processing.

Revised tally: **6 PASS** · **2 PARTIAL** (6 OTP API, 18 email flow) · **1 FAIL-but-improved** (14
webhook auth fixed) · **7 FAIL** · **6 BLOCKED / NOT TESTED**.

Next verification, once Fast2SMS API access is enabled and a real event is sent:

1. `send-otp` → SMS arrives on the device → login completes → `users` row appears.
2. A real `subscription_created` delivery → `webhook_events` row with `COMPLETED`.
3. Re-run drift: D3 should fall as the new user links to its subscriptions.


