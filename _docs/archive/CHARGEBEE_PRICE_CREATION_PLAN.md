# Chargebee Price Creation Plan — `B14` / `PR-18`

> **Site:** `bookmyjuice-test` (TEST environment) · **Currency:** INR, stored in **paise**
> **Prepared:** 2026-10-16 · **Basis:** read-only census — see [`CATALOG_PRICE_MATRIX.md`](CATALOG_PRICE_MATRIX.md)
> **Scope:** create the **45 missing one-time item prices** on the 15 `bmj-item-*` `charge` items, so `GET /api/v1/catalog/charge-items` stops returning `"prices":[]`.
> **Status:** 📋 **PLAN ONLY — NOTHING HAS BEEN CREATED.** This document is a request for approval. **No write to Chargebee is authorised by the existence of this file.**

> ⚠️ **SUPERSEDED (2026-10-16) by [`CHARGEBEE_EXECUTION_PLAN.md`](CHARGEBEE_EXECUTION_PLAN.md).** Keep for history only — do not execute this file. Two of its gates are no longer valid:
> - `G2` (sign-off on 9 disputed price points) → **closed**: the values are resolved in `CHARGEBEE_FINAL_PRICE_MATRIX.md` (`P-2`: Delight 500ml = **₹220**, not ₹229).
> - `G3` (`PR-17` must ship before the prices can be read) → **withdrawn**: `CATALOG_PRICE_LOADING_VERDICT.md` proves the per-item path at `ItemService.java:1109-1113` already serves `ItemPrice` data, so **no code change is required**. `PR-17` remains performance debt only.

---

## 0. Authorisation gate (read this first)

| Gate | Requirement | State |
| :--- | :--- | :--- |
| `G1` | Explicit human go-ahead to write to Chargebee | ⛔ **not given** |
| `G2` | Product sign-off on the 9 disputed price points (§3) | ⛔ **not given** |
| `G3` | `PR-17` (`ItemService.java:937` `limit(200)` → paginated) shipped — otherwise the new prices may still not be read | ⛔ **not shipped** |
| `G4` | Price-creation mechanism agreed (§5) | ⛔ **open** |
| `G5` | Rollback path agreed (§8) | ⛔ **open** |

**Do not execute §4 until `G1`–`G5` are all ✅.** The MCP agent that can perform this write is the **destructive** `onboarding_agent`; every measurement in this plan used the read-only `data_lookup_agent`.

---

## 1. What exists and what does not

| | Count | Evidence |
| :--- | :--- | :--- |
| `bmj-item-*` items (`charge`) | **15** | `list_items` — all `active`, correct families, checkout + portal enabled |
| Item prices attached to them | **0** | `list_item_prices` — 314 rows walked, 0 with an `bmj-item-` `item_id` |
| **Item prices required** | **45** | 15 products × 3 sizes (200 / 300 / 500 ml) |
| Charge-type prices on the site today | **5** | all legacy, all belonging to *other* items (§6) |

**Nothing needs to be repaired, re-pointed or migrated.** The target rows have never existed. This is a pure **create** operation.

**Why the previous attempt failed silently (important):** an import of these very 45 prices was attempted historically — the 15 items landed, the 45 prices did not — and the false premise *"charge types use flat pricing via `item.price`"* (`docs/chargebee_final_state.md:80`) was written down to explain it. **The premise is false** (§1.1 of the matrix). The concrete discrepancy between the failed payload and every charge price that *does* exist on this site is the **`period` / `period_unit` fields** (§4.2) — that is the prime suspect for a silent no-op, and §4.3 therefore tests it with a canary.

---

## 2. What must be created — the target state

| Family | Items | Prices per item | Prices | Resulting `item_type` |
| :--- | :-: | :-: | :-: | :--- |
| `delight` | 5 | 3 | 15 | `charge` |
| `signature` | 5 | 3 | 15 | `charge` |
| `premium` | 5 | 3 | 15 | `charge` |
| **Total** | **15** | | **45** | |

**Site totals after creation (expected):** item prices `314 → 359`; `charge`-type prices `5 → 50`; items with zero prices `15 → 0`; storefront items served with a price `1 → 16`.

**Profile of each row to create** (field-by-field rationale in §4.1):

| Field | Value | Why |
| :--- | :--- | :--- |
| `item_id` | existing `bmj-item-*` id | must equal the storefront item id or the backend's `pricesByItemId` lookup misses (`ItemService.java:940,962`) |
| `item_family_id` | `delight` / `signature` / `premium` | must match the family the category filter resolves |
| `pricing_model` | `flat_fee` | one-time amount per bottle |
| `price` | paise (§3) | backend converts with `movePointLeft(2)` |
| `currency_code` | `INR` | site currency |
| `name` / `description` | **must contain the literal `200ml` / `300ml` / `500ml`** | `extractSizeFromItemPrice` (`:1165-1177`) is a `contains()` test on name **then** description; without the token the price is silently discarded |
| `period`, `period_unit` | **`null` / `null`** | ⚠️ **differs from the historical payload** — see §4.2 |
| `trial_period`, `trial_period_unit` | `null` / `null` (fallback `0` / `day`) | mirrors existing charge prices |

---

## 3. Price decision — ⛔ **BLOCKED, Product input required**

The 45 rows to create need **values**, and the prepared payload's values are **not confirmed by any approved source**. Three sources disagree:

| Source | delight 200 / 300 / 500ml | signature 200 / 300 / 500ml | premium 200 / 300 / 500ml |
| :--- | :--- | :--- | :--- |
| `chargebee_items_payload.json` (prepared payload) | **129 / 159 / 220** | **141.90 / 174.90 / 242** | **156.09 / 192.39 / 266.20** |
| `docs/PRICING_STRUCTURE.md` (per-bottle table) | 129 / 159 / **229** | **199 / 249 / 349** | **299 / 349 / 449** |
| Live subscription, implied ₹/bottle (matrix §6) | 76.83 / 101.50 / 173.17 | 82.00 / 107.67 / 177.33 | 92.33 / 111.67 / 187.50 |

**What the payload actually encodes:**

- `signature` = `delight × 1.1`, exactly (`12900→14190`, `15900→17490`, `22000→24200`).
- `premium` = `delight × 1.21`, exactly (`12900→15609`, `15900→19239`, `22000→26620`).
- So the payload is a **10 %-step ladder over the delight base**, *not* the absolute per-bottle prices in `PRICING_STRUCTURE.md`.
- The payload's `delight` 500ml is `22000` (₹220) where **both** `PRICING_STRUCTURE.md` **and** `scripts/chargebee/import_catalog.py` say `22900` (₹229) — likely a typo.

**Net: 8 of the 9 distinct price points differ between the payload and the documented price list.** Sending the payload therefore commits the business to values nobody has formally approved.

### Decisions required before `G2` can be signed

| # | Decision | Options |
| :-: | :--- | :--- |
| `P-1` | Which price list wins? | (a) the payload as-is · (b) `PRICING_STRUCTURE.md` per-bottle · (c) a new Product-supplied list |
| `P-2` | Is the delight 500ml base ₹220 or ₹229? | one number |
| `P-3` | Are signature/premium a **1.1× / 1.21× ladder** over delight, or the absolute ₹199–₹449 figures? | ladder · absolute · other |
| `P-4` | Do one-time prices include GST, or is tax added by Chargebee? | confirm — affects the number stored |
| `P-5` | Should one-time (per-bottle) prices sit **below** the implied subscription ₹/bottle, or above? | sanity check on the above — subscriptions are currently 40–55 % cheaper per bottle than the notional one-time price |

> **Recommendation:** answer `P-1`–`P-5`, then have Product supply the final 45 values in paise as a single table. Do not derive them from a ratio again — that is how the current ambiguity was created.

---

## 4. The exact creation payload

### 4.1 Shape (one row per product × size = 45 rows)

```json
{
  "id":                "bmj-item-mix-punch-200ml",
  "name":              "Mix Punch 200ml",
  "description":       "Mix Punch - 200ml",
  "pricing_model":     "flat_fee",
  "item_id":           "bmj-item-mix-punch",
  "item_family_id":    "delight",
  "price":             12900,
  "currency_code":     "INR",
  "period":            null,
  "period_unit":       null,
  "trial_period":      null,
  "trial_period_unit": null,
  "tiers":             []
}
```

- `name` / `description` **must** keep the `200ml` / `300ml` / `500ml` token (backend `contains()` test — matrix §2 step 6).
- `price` is **paise**; the backend divides by 100.
- `pricing_model: flat_fee` is used by 298 of 300 existing plan prices, so it is proven on this site.

### 4.2 ⚠️ Two corrections to the historical payload (likely why it silently no-op'd)

The payload in `chargebee_items_payload.json` sets `"period": 1, "period_unit": "day"` on every one of the 45 charge prices. **Every charge price that actually exists on this site has `period: null`, `period_unit: null`:**

| Existing charge price | `item_type` | `pricing_model` | `period` / `period_unit` |
| :--- | :--- | :--- | :--- |
| `abc200-INR` | charge | `per_unit` | `null` / `null` |
| `carrot300-INR` | charge | `per_unit` | `null` / `null` |
| `pineapple300-INR` | charge | `per_unit` | `null` / `null` |
| `ABC-INR` | charge | `flat_fee` | `null` / `null` |
| `cbdemo_one-time-setup-fee` | charge | `flat_fee` | `null` / `null` |

| # | Correction | Rationale |
| :-: | :--- | :--- |
| `C-1` | `period` / `period_unit` → **`null`** for all 45 rows | a one-time charge has no billing period; `period: 1 day` describes a **recurring** product and is inconsistent with every charge price on the site. The MCP `ItemPrice` schema explicitly allows `null` for both. |
| `C-2` | `trial_period` / `trial_period_unit` → **`null`** (fallback `0` / `"day"` if the importer rejects null) | existing charge prices expose no trial fields at all |

**This is a hypothesis, not a certainty** — which is exactly why §4.3 creates **one** row first.

### 4.3 Execution shape — canary first, never a 45-row blind write

1. **Canary:** create **one** price — `bmj-item-mix-punch-200ml`, the representative row in §12 — using the corrected shape above.
2. **Verify by read** (§7 steps 1–2): the row exists, `item_type == "charge"`, `period == null`, `price == 12900`, `item_id == bmj-item-mix-punch`.
3. **Verify through the app** (§7 step 3): if `PR-17` is fixed, the storefront shows `Mix Punch` with a `200ml` price. If it still shows `prices:[]`, the fault is `PR-17`, **not** the payload — re-read §0 `G3`.
4. Only then create the remaining **44** rows in one batch.

**Stop-the-line rule:** if the canary does not appear in `list_item_prices`, do **not** batch the other 44. Treat it as a payload-shape rejection and escalate with the raw error body. A silent `200` with no row created is the failure mode this plan exists to prevent.

---

## 5. Creation mechanism — options and recommendation

⚠️ **The mechanism matters, because the same operation has already failed silently once.** The historical import created 15 items and **0** prices from a payload that contained all 45.

| Option | How | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **A. MCP `import_product_catalog`** (`onboarding_agent`) | `tools/call` with `{items:[], itemFamilies:[], itemPrices:[45], currencies:[{currency_code:"INR"}]}` (all four are required top-level) | already used successfully for items and for 102 plan prices | **this is the call that silently produced 0 prices**; its description says conflicts must be handled "manually in Chargebee", implying error reporting is not dependable | ⚠️ **only with canary proof** (§4.3) |
| **B. Chargebee Dashboard** | Product Catalog → the item → add the 3 sizes | zero tooling risk; human-visible; no credentials in a script | 45 manual entries; transcription risk on price values | ✅ **acceptable — prefer for the canary** |
| **C. Chargebee REST API** `POST /api/v2/item_prices` | one small script looping over 45 rows | deterministic; **returns a real error body on rejection** (no silent `200`); re-runnable; loggable | needs the site API key handled as a secret (never committed) | ✅ **recommended primary** |
| **D. App-side (Chargebee Java SDK in `bmjServer`)** | one-off admin endpoint/CLI using `ItemPrice.create()` | uses the SDK already on the classpath | puts a **write path into the production app for a one-time data fix** | ❌ **rejected** |

> **Recommended:** canary via **B**, remaining 44 via **C** — or a single **C** run if the canary lands cleanly. Do **not** use **A** unless the canary has already proved the corrected shape works.
>
> The operation must be **resumable**: `id` is site-unique, so a re-run after partial success fails loudly on already-created ids rather than duplicating them. See §8.

---

## 6. Deliberately **NOT** in this plan

| Not creating / not touching | Why |
| :--- | :--- |
| **Subscription prices** | 102 already live (matrix §6). The `plan` side needs no work for `B14`. |
| **Re-pointing subscription prices at charge items** | a `plan` price is recurring; that is the data-model error in the abandoned `scripts/chargebee/chargebee_setup_catalog.py:119` |
| `bmj-premium-bloody-red-200ml/300ml/500ml` (+ their 6 subscription prices) | a **separate** gap on the subscription side (the original `42/45` shortfall). Needs its own decision — do not bundle into `B14`. |
| The 5 legacy charge prices / `abc200`, `carrot300`, `pineapple300`, `ABC`, `cbdemo_*` | `PR-19` (matrix §4) — needs an owner decision (archive vs filter fix). **Deleting anything is out of scope.** |
| Any change to the 15 items themselves | they are already correct (matrix §3) |

---

## 7. Verification — how we will know it worked

Run in this order. Steps 1–2 are read-only and need no deployment; step 3 needs a running backend; step 4 is the launch gate.

| # | Step | Command / tool | Expected result |
| :-: | :--- | :--- | :--- |
| 1 | Census re-run | `list_item_prices` (all pages, read-only) | **359** total prices; `item_type=charge` **50** (5 legacy + 45 new); `bmj-item-*` **45** |
| 2 | Spot-check rows | `retrieve_item_price` on `bmj-item-mix-punch-200ml`, `bmj-item-abc-juice-300ml`, `bmj-item-detox-smoothie-500ml` | `item_type "charge"`, `period null`, correct `item_family_id`, `price` = approved paise |
| 3 | Endpoint check | `GET /api/v1/catalog/charge-items` | **16** items with a non-empty `prices` array (15 BMJ + legacy `abc200`); each BMJ item shows 3 sizes with ₹ values; **0** BMJ items with `"prices":[]` |
| 4 | Launch gate | `ops/smoke_test.ps1` probe **`2b`** | 🟢 green — the probe asserts on the **payload**, not the status code |

**Guardrail on step 3:** if step 1 passes but step 3 still shows empty `prices` for BMJ items, the cause is **`PR-17`** (`limit(200)` over 359 rows), **not** the data — re-read §0 `G3`. Do **not** re-create or re-import in that case.

**Evidence to capture** (same convention as `ops/smoke_run_2026-10-16.log`): census output before/after, the creation log with one line per row, the endpoint payload, and the smoke log.

---

## 8. Rollback

| Level | Action |
| :--- | :--- |
| Before starting | none needed — nothing of ours exists yet |
| After canary, canary is wrong | delete/archive **one** item price in the Dashboard — no customer-facing impact |
| After batch, values wrong | item prices are **editable in place** (change `price`) — prefer editing over delete/re-create, since a re-create burns the site-unique id |
| After batch, should not have run at all | delete the 45 `bmj-item-<product>-<size>ml` rows in the Dashboard; the id space is namespaced to `bmj-item-`, so the blast radius is exactly these 45. **No delete tool exists on either MCP agent** — this is a Dashboard/API operation. |

**Blast-radius statement:** every row this plan creates is named `bmj-item-<product>-<size>ml`. **Nothing else on the site is written.**

---

## 9. Order of operations (the whole change window)

| Seq | Action | Owner | Gate |
| :-: | :--- | :--- | :--- |
| 1 | Answer `P-1`–`P-5` (§3) → final 45 values in paise | Product | `G2` |
| 2 | Fix `PR-17`: `ItemService.java:937` `.limit(200)` → paginated like `:910-923` | Eng | `G3` |
| 3 | Explicit write authorisation on the record | Launch owner | `G1` |
| 4 | Create **canary** `bmj-item-mix-punch-200ml` (§4.3) | Eng | `G4` |
| 5 | Verify canary (§7 steps 1–2) | Eng | — |
| 6 | Create the remaining **44** rows (§12) | Eng | — |
| 7 | Verify (§7 steps 1–3) | Eng | — |
| 8 | Re-run `ops/smoke_test.ps1` → probe `2b` green (§7 step 4) | Eng | `B5` |
| 9 | Correct `docs/chargebee_final_state.md:79-80` (`item.price` premise) and the `0/45` row | Eng | — |
| 10 | Close `B14` / `PR-18` in the report + checklist | Eng | `B14` |

---

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Import silently no-ops again (as it did before) | **Medium** | High — looks done, storefront still empty | canary → verify by **read** (§4.3); never trust a bare `200` |
| Wrong price values committed | **Medium** | High — customer-facing pricing error | `G2` sign-off on the exact 45 values *before* the write |
| `PR-17` not fixed → prices exist but are never read | **High** if `G3` skipped | High — false "fix", then a red probe | `G3` is a hard gate; §7 guardrail |
| `period: 1 day` rejected/ignored | Medium | Medium | correction `C-1` (§4.2) + canary test |
| Duplicate / inconsistent price ids | Low | Medium | ids are site-unique; a re-run fails loudly on the gap instead of duplicating |
| Legacy `abc200` ₹99 continues to sell | High (already live) | Medium | tracked as `PR-19` (matrix §4) |

---

## 11. Authorisation block — to be completed before execution

```
B14 / PR-18 — Chargebee item-price creation AUTHORISATION

[ ] G1  Write to Chargebee authorised by : ____________________  date: __________
[ ] G2  Price values approved by Product : ____________________
        P-1 __  P-2 __  P-3 __  P-4 __  P-5 __
[ ] G3  PR-17 (ItemService.java:937) fixed and merged : commit ____________
[ ] G4  Mechanism chosen :  ( ) A MCP import   ( ) B Dashboard   ( ) C REST API
[ ] G5  Rollback owner named : ______________________________________________

Countersigned : ______________________________
Site : bookmyjuice-test  (TEST — not production)
```

**Until this block is signed, this plan remains a document and no Chargebee write may occur.**

---

## 12. Appendix — the 45 rows (reference values, pending `P-1`–`P-5`)

Every row uses: `pricing_model: "flat_fee"`, `currency_code: "INR"`, `period: null`, `period_unit: null`, `trial_period: null`, `trial_period_unit: null`, `tiers: []`, and `name: "<Product> <size>"`, `description: "<Product> - <size>"` — so the size token the backend requires is always present.

**Values below are the *prepared* payload values — they are NOT approved (see §3).**

### 12.1 `delight` — 15 rows

| Price ID | `item_id` | `price` (paise) | ₹ |
| :--- | :--- | --: | --: |
| `bmj-item-mix-punch-200ml` | `bmj-item-mix-punch` | 12900 | ₹129.00 |
| `bmj-item-mix-punch-300ml` | `bmj-item-mix-punch` | 15900 | ₹159.00 |
| `bmj-item-mix-punch-500ml` | `bmj-item-mix-punch` | 22000 | ₹220.00 |
| `bmj-item-carrot-juice-200ml` | `bmj-item-carrot-juice` | 12900 | ₹129.00 |
| `bmj-item-carrot-juice-300ml` | `bmj-item-carrot-juice` | 15900 | ₹159.00 |
| `bmj-item-carrot-juice-500ml` | `bmj-item-carrot-juice` | 22000 | ₹220.00 |
| `bmj-item-colon-cleanser-200ml` | `bmj-item-colon-cleanser` | 12900 | ₹129.00 |
| `bmj-item-colon-cleanser-300ml` | `bmj-item-colon-cleanser` | 15900 | ₹159.00 |
| `bmj-item-colon-cleanser-500ml` | `bmj-item-colon-cleanser` | 22000 | ₹220.00 |
| `bmj-item-beat-the-heat-200ml` | `bmj-item-beat-the-heat` | 12900 | ₹129.00 |
| `bmj-item-beat-the-heat-300ml` | `bmj-item-beat-the-heat` | 15900 | ₹159.00 |
| `bmj-item-beat-the-heat-500ml` | `bmj-item-beat-the-heat` | 22000 | ₹220.00 |
| `bmj-item-winter-special-200ml` | `bmj-item-winter-special` | 12900 | ₹129.00 |
| `bmj-item-winter-special-300ml` | `bmj-item-winter-special` | 15900 | ₹159.00 |
| `bmj-item-winter-special-500ml` | `bmj-item-winter-special` | 22000 | ₹220.00 |

### 12.2 `signature` — 15 rows

| Price ID | `item_id` | `price` (paise) | ₹ |
| :--- | :--- | --: | --: |
| `bmj-item-abc-juice-200ml` | `bmj-item-abc-juice` | 14190 | ₹141.90 |
| `bmj-item-abc-juice-300ml` | `bmj-item-abc-juice` | 17490 | ₹174.90 |
| `bmj-item-abc-juice-500ml` | `bmj-item-abc-juice` | 24200 | ₹242.00 |
| `bmj-item-pineapple-200ml` | `bmj-item-pineapple` | 14190 | ₹141.90 |
| `bmj-item-pineapple-300ml` | `bmj-item-pineapple` | 17490 | ₹174.90 |
| `bmj-item-pineapple-500ml` | `bmj-item-pineapple` | 24200 | ₹242.00 |
| `bmj-item-amla-juice-200ml` | `bmj-item-amla-juice` | 14190 | ₹141.90 |
| `bmj-item-amla-juice-300ml` | `bmj-item-amla-juice` | 17490 | ₹174.90 |
| `bmj-item-amla-juice-500ml` | `bmj-item-amla-juice` | 24200 | ₹242.00 |
| `bmj-item-ashguard-juice-200ml` | `bmj-item-ashguard-juice` | 14190 | ₹141.90 |
| `bmj-item-ashguard-juice-300ml` | `bmj-item-ashguard-juice` | 17490 | ₹174.90 |
| `bmj-item-ashguard-juice-500ml` | `bmj-item-ashguard-juice` | 24200 | ₹242.00 |
| `bmj-item-citrus-juice-200ml` | `bmj-item-citrus-juice` | 14190 | ₹141.90 |
| `bmj-item-citrus-juice-300ml` | `bmj-item-citrus-juice` | 17490 | ₹174.90 |
| `bmj-item-citrus-juice-500ml` | `bmj-item-citrus-juice` | 24200 | ₹242.00 |

### 12.3 `premium` — 15 rows

| Price ID | `item_id` | `price` (paise) | ₹ |
| :--- | :--- | --: | --: |
| `bmj-item-bloody-red-200ml` | `bmj-item-bloody-red` | 15609 | ₹156.09 |
| `bmj-item-bloody-red-300ml` | `bmj-item-bloody-red` | 19239 | ₹192.39 |
| `bmj-item-bloody-red-500ml` | `bmj-item-bloody-red` | 26620 | ₹266.20 |
| `bmj-item-antioxidant-juice-200ml` | `bmj-item-antioxidant-juice` | 15609 | ₹156.09 |
| `bmj-item-antioxidant-juice-300ml` | `bmj-item-antioxidant-juice` | 19239 | ₹192.39 |
| `bmj-item-antioxidant-juice-500ml` | `bmj-item-antioxidant-juice` | 26620 | ₹266.20 |
| `bmj-item-wheatgrass-juice-200ml` | `bmj-item-wheatgrass-juice` | 15609 | ₹156.09 |
| `bmj-item-wheatgrass-juice-300ml` | `bmj-item-wheatgrass-juice` | 19239 | ₹192.39 |
| `bmj-item-wheatgrass-juice-500ml` | `bmj-item-wheatgrass-juice` | 26620 | ₹266.20 |
| `bmj-item-coconut-milk-200ml` | `bmj-item-coconut-milk` | 15609 | ₹156.09 |
| `bmj-item-coconut-milk-300ml` | `bmj-item-coconut-milk` | 19239 | ₹192.39 |
| `bmj-item-coconut-milk-500ml` | `bmj-item-coconut-milk` | 26620 | ₹266.20 |
| `bmj-item-detox-smoothie-200ml` | `bmj-item-detox-smoothie` | 15609 | ₹156.09 |
| `bmj-item-detox-smoothie-300ml` | `bmj-item-detox-smoothie` | 19239 | ₹192.39 |
| `bmj-item-detox-smoothie-500ml` | `bmj-item-detox-smoothie` | 26620 | ₹266.20 |

### 12.4 Count check

| Family | Rows | Sum keys (`item_id`) | Distinct `price` values |
| :--- | :-: | :-: | :--- |
| `delight` | 15 | 5 | 3 (12900 / 15900 / 22000) |
| `signature` | 15 | 5 | 3 (14190 / 17490 / 24200) |
| `premium` | 15 | 5 | 3 (15609 / 19239 / 26620) |
| **Total** | **45** | **15 items** | **9** |

45 rows = 15 products × 3 sizes = the exact count the census reports as missing (matrix §1, §5). Nothing extra is included and nothing on the site is modified.

---

**End of plan.** No Chargebee write has been performed. Execution requires the §11 authorisation block to be signed and `G1`–`G5` to be ✅.






