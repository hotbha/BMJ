# QA Accounts

**Purpose:** one documented place for reusable BMJ test accounts, so future runs reuse them instead of
creating duplicates.
**Rule followed:** Bharat's personal phone, email and Google account were **not** used.

---

## 1. Existing accounts found (inventory, 2026-11-19)

### BMJ users (production VPS database)

**None.** `SELECT id, username, email, chargebee_customer_id FROM users` returned **0 rows**. The
production database has never had a BMJ account created on it.

### Chargebee-side QA fixtures (customers mirrored locally)

These are reusable *billing* fixtures, not BMJ logins — they have no BMJ user yet:

| customer_id | phone | email | first name |
|---|---|---|---|
| `169m1FVKSGoO233mc` | 9876543210 | e2e-full-flow@bookmyjuice.co.in | QA |
| `16CS3UVZQtF20nFJ` | 9876543210 | qa.sub.probe@bookmyjuice.test | QA |
| `169oAaVYQ0fXY5psP` | 9999999933 | e2e.signup.20261018@example.com | E2E |
| `16BRqVVKXmYW2tGe` | 9876543212 | e2e-existing@bookmyjuice.co.in | Existing |
| `16BdPNVKRXxJA2uIq` | 9900000005 | e2e-race-871106@bookmyjuice.co.in | Race |
| `169m1FVKRXvYo2typ` | 9900000002 | e2e+test-812191@bookmyjuice.co.in | Plus |

**Problem with reusing them:** both QA fixtures share the phone `9876543210` with **eleven** customer
rows in total. The `IdentityLinker` correctly refuses ambiguous matches, so an account created on that
phone could never auto-link to either fixture — the E2E identity test would fail by design, not by bug.
A clean QA account needs a phone number that maps to exactly one customer.

---

## 2. Intended primary account — **NOT created (blocked)**

| Field | Value |
|---|---|
| Account name | `BMJ-QA-PRIMARY` |
| Intended phone | `9999999911` (synthetic, unused in production, not a real subscriber) |
| Intended email | `bmj-qa-primary@bookmyjuice.co.in` (to be created) |
| Google account | **none available** — see §4 |
| BMJ user id | — |
| Chargebee customer id | — |
| Subscription id | — |
| Created date | — |
| Purpose | OTP login, identity linking, subscription visibility, webhook validation |
| Status | **BLOCKED — see §3** |

## 3. Why it could not be created

Creating the account requires completing an OTP round-trip on the device, which requires an SMS:

| Requirement | State | Evidence |
|---|---|---|
| SMS provider configured | **NO** | `docker exec bmj-api printenv FAST2SMS_API_KEY` → key absent |
| OTP delivery path | console fallback only | `OTPUtil.generateOTP` logs `[SMS] OTP sent … via Fast2SMS` only when a key exists; otherwise it falls back to console |
| Device able to receive the SMS | not applicable | no SMS is sent at all |

The only way to finish registration without an SMS would be to read the console OTP from the server
log — which validates the *API* but **not** "SMS received on the actual device", so it would have
produced a misleading PASS. It was therefore not done.

## 4. Google account

The device's only signed-in Google identity is **Bharat's personal account**, which the QA policy
forbids. No QA Google account exists on the device and none can be created from here (Google requires
interactive setup, phone verification and consent). Google sign-in is therefore **not testable under
policy** on this device.

---

## 5. Required to unblock (in order)

1. **Provision Fast2SMS** — set `FAST2SMS_API_KEY` in `/home/bmj/bmj/.env` and restart `bmj-api`.
   Then run the OTP flow with `9999999911` and record the issued user id here.
2. **Create a QA Google account** and add it to the test device. Then the Google path becomes testable.
3. **Do not create the account until §1's phone collision is understood** — if the new account lands on
   `9876543210`, linking cannot succeed; use a dedicated number that appears exactly once in Chargebee.

## 6. Reuse policy for future runs

- Reuse `BMJ-QA-PRIMARY` for every subsequent run. Do not create `BMJ-QA-2`, `-3`, … per session.
- If a test corrupts the account state, document the corruption in this file rather than creating a
  replacement account.
- Record every new account here **before** using it, with the full id set (user, customer, subscription).
