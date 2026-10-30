# Chargebee Beta Status

> **Date:** 2026-10-30 · **Site:** `bookmyjuice-test` (TEST) · **Strategy:** Option A only — no redesign, no Option B.

## 1. Gate state (measured today)

```
python _captures/chargebee_price_rollout.py preflight
→ price variants: NOT AVAILABLE on this site
  Chargebee said: data.list_price_variants failed: list price variants. Invalid input
  provided. Chargebee API responded with: This API operation is not enabled for this
  site. Please contact support@chargebee.com to get this enabled
→ Nothing was written. The rollout stays paused.
```

**Status: 🔴 still blocked externally.** Nothing in the repository can change this; only Chargebee can enable the feature on the site.

## 2. Readiness snapshot (measured, read-only census)

| Metric | Value | Notes |
| :--- | ---: | :--- |
| `plan` prices | **300** | day 91 · month 149 · week 56 · year 4 — subscriptions are fully chargeable |
| `charge` prices | **7** | storefront rows: only 2 of the 45 planned |
| `addon` prices | 9 | — |
| Zero/negative prices | **0** | clean |
| Non-INR prices | **0** | clean |
| Storefront priced products | **2 / 15** | `bmj-item-mix-punch-200ml` ₹129.00, `bmj-item-bloody-red-200ml` ₹156.09 |

So the **subscription** half of beta is commercially ready; the **one-time purchase** half is not, and the PDP/cart show the honest em-dash fallback for the 13 unpriced products.

## 3. The four readiness commands (all green/known when unblocked)

| Step | Command | Today |
| :--- | :--- | :--- |
| preflight | `python _captures/chargebee_price_rollout.py preflight` | 🔴 variants unavailable |
| canary | re-read `bmj-item-mix-punch-200ml` → ₹129.00 | ✅ row exists (canary effectively already run) |
| census | `python _captures/chargebee_catalog_check.py` | ✅ runs, numbers in §2 |
| verify | after rollout: `charge` prices **7 → 52**, products with zero prices **15 → 0** | ⏳ pending |

## 4. The instant Price Variants become available

Run **in this order**, stopping if any step disagrees:

1. `python _captures/chargebee_price_rollout.py preflight` → must print variants **AVAILABLE**.
2. Re-read the canary and confirm ₹129.00 — if the canary is gone, recreate it first (one row only).
3. Create the remaining **44** rows with `_captures/chargebee_price_rollout.py` (gated script; Option A shape).
4. `python _captures/chargebee_catalog_check.py` → expect `charge` 7 → 52, non-INR 0, zero-price products 15 → 0.
5. Storefront probe: every product returns **3** sizes with prices.
6. Only then, rebuild the app (no code change needed — prices come from the API).

**Authorisation is still required before step 3.** Every measurement above used the read-only data-lookup agent; the write path (M-1 in `CHARGEBEE_GO_LIVE_RECOMMENDATION.md`) needs explicit human sign-off, and rollback = deleting exactly the 45 new price ids.

## 5. What beta can ship with today

- ✅ Weekly / monthly / daily subscription checkout (300 plan prices).
- ✅ Cart totals, taxes and delivery computed by Chargebee at checkout.
- 🟡 One-time purchase limited to 2 of 15 products; the rest render the em-dash fallback.
- ⚠️ App and server both default to the **TEST** site. A beta build pointed at production must set `CHARGEBEE_SITE=bookmyjuice` **and** a production API key; the app itself never touches the Chargebee API (verified: `ChargebeeConfig` is unused in `lib/`).
