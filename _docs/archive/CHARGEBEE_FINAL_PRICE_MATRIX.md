# Chargebee Final Price Matrix — Approved One-Time Prices

> **Site:** `bookmyjuice-test` (TEST) · **Currency:** INR (stored in **paise**, ÷100 = ₹)
> **Produced:** 2026-10-16 · **Task:** `T1` + `T2`
> **Status:** 🔒 **VALIDATION ONLY — NOTHING WAS CREATED, CHANGED OR DELETED IN CHARGEBEE.**
> **Verdict:** ✅ **45 / 45 approved prices validated. 0 discrepancies against the approved table.**
> **Companion:** [`CATALOG_PRICE_MATRIX.md`](CATALOG_PRICE_MATRIX.md) (census) · [`CHARGEBEE_PRICE_CREATION_PLAN.md`](CHARGEBEE_PRICE_CREATION_PLAN.md) (execution plan) · [`CHARGEBEE_IMPORT_ROOT_CAUSE.md`](CHARGEBEE_IMPORT_ROOT_CAUSE.md) · [`CATALOG_PRICE_LOADING_VERDICT.md`](CATALOG_PRICE_LOADING_VERDICT.md) · [`CATALOG_LEGACY_ITEM_REPORT.md`](CATALOG_LEGACY_ITEM_REPORT.md) · [`CHARGEBEE_GO_LIVE_RECOMMENDATION.md`](CHARGEBEE_GO_LIVE_RECOMMENDATION.md)

---

## 0. TL;DR

| Question | Answer |
| :--- | :--- |
| How many prices must exist? | **45** = 15 products × 3 sizes |
| How many exist today? | **0** (`list_item_prices` → **0** of 314 rows carry a `bmj-item-*` `item_id`) |
| Do the 45 approved prices match the business table? | ✅ **Yes — 45/45, 0 mismatches** (§3) |
| Do they match the prepared payload? | ✅ **Yes — 45/45, 0 mismatches** (§3) |
| Do the target `item_id`s exist in Chargebee? | ✅ **Yes — 15/15**, all `active`, `type: charge`, families `delight`/`signature`/`premium` |
| Is any planned price id already taken? | ❌ **No** — no collision with an existing price id **or** item id (§2 `A4`) |
| Does the Chargebee price id exist yet? | ❌ **No — the "price id" column is a PROVISIONAL TARGET, not a live object** (§1.1) |
| Discrepancies found? | **0 price discrepancies**; **4 documentation discrepancies** (`D-1`…`D-4`, §6) |
| May anything be created? | ⛔ **No.** Read-only. Gates `G1`–`G5` (creation plan §0) remain **unsigned** |

---

## 1. What this document is — and is not

This is the **join of three independent sources**, re-measured on 2026-10-16:

| # | Source | Role | Authority |
| :-: | :--- | :--- | :--- |
| 1 | `docs/business-requirements/pricing-table.xlsx` (sheet `Pricing`) | the **approved** per-bottle one-time price | 🟢 **business source of truth** — used to validate Chargebee configuration |
| 2 | Live Chargebee TEST site (`data_lookup_agent`, read-only) | the **objects that exist** (15 items · 314 prices · 0 matching) | 🟢 **runtime source of truth** |
| 3 | `chargebee_items_payload.json` (45 rows) | the **prepared** payload awaiting approval | 🟡 subject to validation — validated here |

### 1.1 The "Chargebee price id" column is a target, not a fact

The 45 prices **do not exist**, so there is **no live Chargebee price id to report**. §4 records the **provisional target id** proposed by the payload, so that the creation step and the app-side lookup agree (`ItemService.java:940,962` → `pricesByItemId`, keyed on `item_id`). Read the column as *"the id that will exist after the approved creation step runs"*.

Two hard requirements the target ids satisfy:

1. **`item_id` must equal the live storefront item id** exactly (`bmj-item-<slug>`), or the price is invisible to the backend.
2. **The price `name`/`description` must contain the literal size token** (`200ml`/`300ml`/`500ml`), or the backend silently discards the row (`ItemService.java:1165-1177`). Verified **45/45**.

---

## 2. Validation method (reproducible, read-only)

| ID | Assertion | Result |
| :-- | :--- | :--- |
| `A1` | Excel price (₹) == payload price (paise ÷ 100), all 45 rows | ✅ **0 mismatches** |
| `A2` | payload `item_id` ∈ live census (15 `bmj-item-*`) | ✅ **45/45 present** |
| `A3` | each payload `name`+`description` contains its size token | ✅ **45/45 true, 0 offenders** |
| `A4` | no target price id already exists (as a price **or** as an item id) | ✅ **0 collisions** |
| `A5` | no live `bmj-item-*` item is missing from the payload | ✅ **0 missing** |
| `A6` | payload contains exactly 15 items and 45 prices | ✅ |
| `A7` | payload family ∈ {`delight`,`signature`,`premium`} **and** equals the live `item_family_id` | ✅ **45/45** |

Reproduce via the read-only census (`CATALOG_PRICE_MATRIX.md` §8) plus the join assertions in §7 below.

---

## 3. `T2` — verification of the 45 planned prices

### 3.1 The approved table (exactly as supplied to this validation)

| Family | 200ml | 300ml | 500ml |
| :--- | --: | --: | --: |
| Delight | ₹129 | ₹159 | ₹220 |
| Signature | ₹141.90 | ₹174.90 | ₹242.00 |
| Premium | ₹156.09 | ₹192.39 | ₹266.20 |

### 3.2 Result — 0 discrepancies

| Comparison | Outcome |
| :--- | :--- |
| Approved table vs **`pricing-table.xlsx`** (sheet `Pricing`, col *Regular price per bottle*) | ✅ **exact, 9/9 points** |
| Approved table vs **`chargebee_items_payload.json`** | ✅ **exact, 45/45 rows, 0 mismatches** |
| The 9 distinct payload values (paise) | ✅ `12900, 14190, 15609, 15900, 17490, 19239, 22000, 24200, 26620` |

> **`T2` result: PASS.** No discrepancy exists between the approved table, the business workbook and the prepared payload. **Nothing was auto-corrected — nothing required correction.**

### 3.3 Workbook data-quality notes (recorded, no action)

- The sheet spells the family **`Permium`** (typo) and stores floats, so it emits `242.00000000000003` and `266.20000000000005`. The approved values are **242.00** and **266.20**; the payload's integer paise (`24200`, `26620`) are the correct representation.
- Sheet `Families` note: *"All products in one-family and one-size have same pricing"* — the design rule this matrix satisfies (5 products share one price per family+size).
- The ratio is exact and **derived, not a rule**: `signature = delight × 1.1`, `premium = delight × 1.21` (129 → 141.90 → 156.09; 159 → 174.90 → 192.39; 220 → 242.00 → 266.20). Recorded here so nobody later mistakes the pattern for a business rule and re-derives prices from it.

---

## 4. The final price matrix — 45 rows

`approved ₹` = business source of truth (`pricing-table.xlsx` sheet `Pricing`). `paise` = the exact integer to send to Chargebee. `target price id` = **does not exist yet** (§1.1). `live?` = present on the site today.

### 4.1 `delight` — 15 rows

| # | `item_id` | product name | family | size | approved ₹ | paise | target price id | live? |
| :-: | :--- | :--- | :--- | :-: | --: | --: | :--- | :-: |
| 1 | `bmj-item-beat-the-heat` | Beat the Heat | `delight` | 200ml | ₹129.00 | 12900 | `bmj-item-beat-the-heat-200ml` | ❌ no |
| 2 | `bmj-item-beat-the-heat` | Beat the Heat | `delight` | 300ml | ₹159.00 | 15900 | `bmj-item-beat-the-heat-300ml` | ❌ no |
| 3 | `bmj-item-beat-the-heat` | Beat the Heat | `delight` | 500ml | ₹220.00 | 22000 | `bmj-item-beat-the-heat-500ml` | ❌ no |
| 4 | `bmj-item-carrot-juice` | Carrot Juice | `delight` | 200ml | ₹129.00 | 12900 | `bmj-item-carrot-juice-200ml` | ❌ no |
| 5 | `bmj-item-carrot-juice` | Carrot Juice | `delight` | 300ml | ₹159.00 | 15900 | `bmj-item-carrot-juice-300ml` | ❌ no |
| 6 | `bmj-item-carrot-juice` | Carrot Juice | `delight` | 500ml | ₹220.00 | 22000 | `bmj-item-carrot-juice-500ml` | ❌ no |
| 7 | `bmj-item-colon-cleanser` | Colon Cleanser | `delight` | 200ml | ₹129.00 | 12900 | `bmj-item-colon-cleanser-200ml` | ❌ no |
| 8 | `bmj-item-colon-cleanser` | Colon Cleanser | `delight` | 300ml | ₹159.00 | 15900 | `bmj-item-colon-cleanser-300ml` | ❌ no |
| 9 | `bmj-item-colon-cleanser` | Colon Cleanser | `delight` | 500ml | ₹220.00 | 22000 | `bmj-item-colon-cleanser-500ml` | ❌ no |
| 10 | `bmj-item-mix-punch` | Mix Punch | `delight` | 200ml | ₹129.00 | 12900 | `bmj-item-mix-punch-200ml` | ❌ no |
| 11 | `bmj-item-mix-punch` | Mix Punch | `delight` | 300ml | ₹159.00 | 15900 | `bmj-item-mix-punch-300ml` | ❌ no |
| 12 | `bmj-item-mix-punch` | Mix Punch | `delight` | 500ml | ₹220.00 | 22000 | `bmj-item-mix-punch-500ml` | ❌ no |
| 13 | `bmj-item-winter-special` | Winter Special | `delight` | 200ml | ₹129.00 | 12900 | `bmj-item-winter-special-200ml` | ❌ no |
| 14 | `bmj-item-winter-special` | Winter Special | `delight` | 300ml | ₹159.00 | 15900 | `bmj-item-winter-special-300ml` | ❌ no |
| 15 | `bmj-item-winter-special` | Winter Special | `delight` | 500ml | ₹220.00 | 22000 | `bmj-item-winter-special-500ml` | ❌ no |

### 4.2 `signature` — 15 rows

| # | `item_id` | product name | family | size | approved ₹ | paise | target price id | live? |
| :-: | :--- | :--- | :--- | :-: | --: | --: | :--- | :-: |
| 1 | `bmj-item-abc-juice` | ABC Juice | `signature` | 200ml | ₹141.90 | 14190 | `bmj-item-abc-juice-200ml` | ❌ no |
| 2 | `bmj-item-abc-juice` | ABC Juice | `signature` | 300ml | ₹174.90 | 17490 | `bmj-item-abc-juice-300ml` | ❌ no |
| 3 | `bmj-item-abc-juice` | ABC Juice | `signature` | 500ml | ₹242.00 | 24200 | `bmj-item-abc-juice-500ml` | ❌ no |
| 4 | `bmj-item-amla-juice` | Amla Juice | `signature` | 200ml | ₹141.90 | 14190 | `bmj-item-amla-juice-200ml` | ❌ no |
| 5 | `bmj-item-amla-juice` | Amla Juice | `signature` | 300ml | ₹174.90 | 17490 | `bmj-item-amla-juice-300ml` | ❌ no |
| 6 | `bmj-item-amla-juice` | Amla Juice | `signature` | 500ml | ₹242.00 | 24200 | `bmj-item-amla-juice-500ml` | ❌ no |
| 7 | `bmj-item-ashguard-juice` | Ashguard Juice | `signature` | 200ml | ₹141.90 | 14190 | `bmj-item-ashguard-juice-200ml` | ❌ no |
| 8 | `bmj-item-ashguard-juice` | Ashguard Juice | `signature` | 300ml | ₹174.90 | 17490 | `bmj-item-ashguard-juice-300ml` | ❌ no |
| 9 | `bmj-item-ashguard-juice` | Ashguard Juice | `signature` | 500ml | ₹242.00 | 24200 | `bmj-item-ashguard-juice-500ml` | ❌ no |
| 10 | `bmj-item-citrus-juice` | Citrus Juice | `signature` | 200ml | ₹141.90 | 14190 | `bmj-item-citrus-juice-200ml` | ❌ no |
| 11 | `bmj-item-citrus-juice` | Citrus Juice | `signature` | 300ml | ₹174.90 | 17490 | `bmj-item-citrus-juice-300ml` | ❌ no |
| 12 | `bmj-item-citrus-juice` | Citrus Juice | `signature` | 500ml | ₹242.00 | 24200 | `bmj-item-citrus-juice-500ml` | ❌ no |
| 13 | `bmj-item-pineapple` | Pineapple | `signature` | 200ml | ₹141.90 | 14190 | `bmj-item-pineapple-200ml` | ❌ no |
| 14 | `bmj-item-pineapple` | Pineapple | `signature` | 300ml | ₹174.90 | 17490 | `bmj-item-pineapple-300ml` | ❌ no |
| 15 | `bmj-item-pineapple` | Pineapple | `signature` | 500ml | ₹242.00 | 24200 | `bmj-item-pineapple-500ml` | ❌ no |

### 4.3 `premium` — 15 rows

| # | `item_id` | product name | family | size | approved ₹ | paise | target price id | live? |
| :-: | :--- | :--- | :--- | :-: | --: | --: | :--- | :-: |
| 1 | `bmj-item-antioxidant-juice` | Antioxidant Juice | `premium` | 200ml | ₹156.09 | 15609 | `bmj-item-antioxidant-juice-200ml` | ❌ no |
| 2 | `bmj-item-antioxidant-juice` | Antioxidant Juice | `premium` | 300ml | ₹192.39 | 19239 | `bmj-item-antioxidant-juice-300ml` | ❌ no |
| 3 | `bmj-item-antioxidant-juice` | Antioxidant Juice | `premium` | 500ml | ₹266.20 | 26620 | `bmj-item-antioxidant-juice-500ml` | ❌ no |
| 4 | `bmj-item-bloody-red` | Bloody Red | `premium` | 200ml | ₹156.09 | 15609 | `bmj-item-bloody-red-200ml` | ❌ no |
| 5 | `bmj-item-bloody-red` | Bloody Red | `premium` | 300ml | ₹192.39 | 19239 | `bmj-item-bloody-red-300ml` | ❌ no |
| 6 | `bmj-item-bloody-red` | Bloody Red | `premium` | 500ml | ₹266.20 | 26620 | `bmj-item-bloody-red-500ml` | ❌ no |
| 7 | `bmj-item-coconut-milk` | Coconut Milk | `premium` | 200ml | ₹156.09 | 15609 | `bmj-item-coconut-milk-200ml` | ❌ no |
| 8 | `bmj-item-coconut-milk` | Coconut Milk | `premium` | 300ml | ₹192.39 | 19239 | `bmj-item-coconut-milk-300ml` | ❌ no |
| 9 | `bmj-item-coconut-milk` | Coconut Milk | `premium` | 500ml | ₹266.20 | 26620 | `bmj-item-coconut-milk-500ml` | ❌ no |
| 10 | `bmj-item-detox-smoothie` | Detox Smoothie | `premium` | 200ml | ₹156.09 | 15609 | `bmj-item-detox-smoothie-200ml` | ❌ no |
| 11 | `bmj-item-detox-smoothie` | Detox Smoothie | `premium` | 300ml | ₹192.39 | 19239 | `bmj-item-detox-smoothie-300ml` | ❌ no |
| 12 | `bmj-item-detox-smoothie` | Detox Smoothie | `premium` | 500ml | ₹266.20 | 26620 | `bmj-item-detox-smoothie-500ml` | ❌ no |
| 13 | `bmj-item-wheatgrass-juice` | Wheatgrass Juice | `premium` | 200ml | ₹156.09 | 15609 | `bmj-item-wheatgrass-juice-200ml` | ❌ no |
| 14 | `bmj-item-wheatgrass-juice` | Wheatgrass Juice | `premium` | 300ml | ₹192.39 | 19239 | `bmj-item-wheatgrass-juice-300ml` | ❌ no |
| 15 | `bmj-item-wheatgrass-juice` | Wheatgrass Juice | `premium` | 500ml | ₹266.20 | 26620 | `bmj-item-wheatgrass-juice-500ml` | ❌ no |

## 5. Subtotals and integrity

| Family | rows | items | distinct price points | live today |
| :--- | :-: | :-: | :--- | :-: |
| `delight` | 15 | 5 | 3 (12900 / 15900 / 22000) | 0 |
| `signature` | 15 | 5 | 3 (14190 / 17490 / 24200) | 0 |
| `premium` | 15 | 5 | 3 (15609 / 19239 / 26620) | 0 |
| **Total** | **45** | **15** | **9** | **0** |

`A1`–`A7` all passed — the join is **executed**, not eyeballed. Expected site totals after an approved creation: item prices `314 → 359`; `charge`-type prices `5 → 50`; items with zero prices `15 → 0`.

---

## 6. Discrepancy register — 0 price discrepancies, 4 documentation discrepancies

> **No price value is in dispute.** The four items below are **documentation debt**: stale or false statements that would cause a future operator to import the **wrong** table. Recorded so the freeze commit can correct them.

| # | Location | Finding | Severity |
| :-: | :--- | :--- | :--- |
| `D-1` | `docs/PRICING_STRUCTURE.md:17-35` | Carries a **different price table**: delight 500ml **₹229**, signature **₹199 / ₹249 / ₹349**, premium **₹299 / ₹349 / ₹449** → **8 of 9 points wrong**. Also states *"2 % Overhead"* where the workbook column is headed **2.5 %**; claims *"Total ItemPrices in Chargebee: 90 (45 items × Weekly + Monthly)"* (untrue: 314 prices, 0 attached to these items); and cites `x:\BMJ\pricing table1.xlsx`, which **does not exist** anywhere in the repository — the workbook in use is `docs/business-requirements/pricing-table.xlsx`. | 🔴 **must not be used as a price source** |
| `D-2` | `scripts/chargebee/chargebee_setup_catalog.py:72-76` | The same stale ladder in code (delight 500ml `22900`, signature `19900/24900/34900`, premium `29900/34900/44900`), with an **abandoned import shape**: juices `Orange/Apple/Mango/Mixed/Black_Grapes` (not the 15 real products) and one-time prices pointed at **plan** items (`item_id: f"{cat}_{size}ml_weekly"`). Retained as **evidence of the historical mis-shape only**. | 🟠 historical artefact |
| `D-3` | `docs/chargebee_final_state.md:75-80` | States *"Charge types use flat pricing via `item.price` field, not separate `item_prices`"* — **false** (no `price` on any of the 15 items; 5 charge items on this site hold item prices). Lists one-time ids as `bmj-signature-*` / `bmj-premium-*`, which **do not exist**; the live ids are `bmj-item-*`. | 🔴 **false premise behind the undetected gap** |
| `D-4` | `chargebee_items_payload.json` | Omits `is_taxable`, which **all 5** working charge prices set to `true`; also omits `external_name`, `show_description_in_invoices`, `show_description_in_quotes`, `free_quantity`, `invoice_notes`, `channel`, `metadata` (all present on the working rows). `is_taxable` is **GST-relevant** → see `CHARGEBEE_IMPORT_ROOT_CAUSE.md` §6. | 🟡 open (`P-4`) |

---

## 7. Decision register — what this validation resolves

| # | Decision (creation plan §3) | State after this validation |
| :-: | :--- | :--- |
| `P-1` | Which price list wins? | ✅ **RESOLVED** — the business workbook wins, and the prepared payload **already agrees with it 45/45**. Nothing to arbitrate. |
| `P-2` | Delight 500ml — ₹220 or ₹229? | ✅ **RESOLVED: ₹220** (`22000` paise). ₹229 exists only in the two stale sources `D-1` / `D-2`. |
| `P-3` | Ladder or absolute values? | ✅ **RESOLVED in effect: absolute** per family+size. The exact `×1.1 / ×1.21` ratio is an artefact of how the sheet was built (§3.3), **not** a rule to derive from. |
| `P-4` | Is GST included in the stored price? | 🟡 **OPEN** — recommendation: set `is_taxable: true` to mirror every working charge price; Finance to confirm the paise are GST-inclusive. |
| `P-5` | Relationship to subscription plans? | ✅ **RESOLVED by architecture decision** — one-time `charge` prices are **independent** of the Delight/Signature/Premium plans and **must not be derived from them**. |

---

## 8. Reproduce this document

```powershell
# 1. Approved prices - read the workbook directly (no openpyxl in the venv; use stdlib zip+XML)
#    docs/business-requirements/pricing-table.xlsx -> xl/worksheets/sheet1.xml   (sheet "Pricing")
#    col A = family ("Permium" typo -> premium) . col B = size . col C = Regular price per bottle
# 2. Live census - read-only data_lookup_agent, see CATALOG_PRICE_MATRIX.md §8  (15 items / 314 prices)
# 3. Join + assert A1..A7 (45 rows, 15 items, 0 mismatches, 0 id collisions)
```

**Assertions executed for this document (all green):** approved prices parsed 9/9 · payload rows 45 · distinct items 15 · `A1` 0 mismatches · `A2` 45/45 items present · `A3` 45/45 size tokens · `A4` 0 price-id collisions and 0 item-id collisions · `A5` 0 live items missing from the payload · `A6` 15 items / 45 prices · `A7` 45/45 family match.

---

## 9. Cross-reference

| Document | Relationship |
| :--- | :--- |
| [`CATALOG_PRICE_MATRIX.md`](CATALOG_PRICE_MATRIX.md) | the census this matrix is built on |
| [`CHARGEBEE_PRICE_CREATION_PLAN.md`](CHARGEBEE_PRICE_CREATION_PLAN.md) | execution plan; §2/§4 carry the `C-1`/`C-2` payload corrections; §3's price dispute is **resolved here** |
| [`CHARGEBEE_IMPORT_ROOT_CAUSE.md`](CHARGEBEE_IMPORT_ROOT_CAUSE.md) | why the historical import produced items without prices |
| [`CATALOG_PRICE_LOADING_VERDICT.md`](CATALOG_PRICE_LOADING_VERDICT.md) | whether these 45 prices would actually be served (`PR-17`) |
| [`CATALOG_LEGACY_ITEM_REPORT.md`](CATALOG_LEGACY_ITEM_REPORT.md) | the legacy-item question (`PR-19`) |
| [`CHARGEBEE_GO_LIVE_RECOMMENDATION.md`](CHARGEBEE_GO_LIVE_RECOMMENDATION.md) | the single go/no-go recommendation (`T6`) |
| `docs/business-requirements/pricing-table.xlsx` | the authoritative workbook (sheets `Pricing`, `Families`) |

---

**End of matrix.** Every price in §4 is traceable to a cell in `pricing-table.xlsx` and to a row in `chargebee_items_payload.json`; no value was inferred. **No Chargebee object was created, modified or deleted while producing this document.**




