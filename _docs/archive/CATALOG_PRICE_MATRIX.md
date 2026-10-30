# Catalog Price Matrix — Storefront Products

> **Site:** `bookmyjuice-test` (TEST environment) · **Currency:** INR, stored in **paise** (÷100 = ₹)
> **Generated:** 2026-10-16
> **Method:** **read-only** Chargebee MCP census via the `data_lookup_agent` — **nothing was created, changed or deleted**
> **Endpoint under test:** `GET /api/v1/catalog/charge-items`
> **Findings:** `PR-18` / `B14` · **Companion document:** [`CHARGEBEE_PRICE_CREATION_PLAN.md`](CHARGEBEE_PRICE_CREATION_PLAN.md)
> **Verdict:** 🔴 **15 / 15 storefront products carry ZERO Chargebee item prices.** The catalog is visible but **not commercially usable** — every product renders with `"prices":[]`.

---

## 0. TL;DR

| Question | Answer (measured, not inferred) |
| :--- | :--- |
| How many products does the storefront show? | **15** — measured from the runtime log, not inferred (see §10) |
| How many of those have a usable price? | **0** — all 15 return `"prices":[]`. (The earlier "18 items / 1 legacy ₹99" came from a *static* filter evaluation and was wrong — see §10 and `CATALOG_LEGACY_ITEM_REPORT.md`.) |
| How many of the 15 real BMJ products have prices? | **0 / 15** |
| How many item prices must be created to fix it? | **45** (15 products × 3 sizes) |
| Do the 15 items themselves exist and look correct? | ✅ Yes — all `active`, `charge`, correct families, checkout + portal enabled |
| Is the price data "mis-linked" (recoverable by re-pointing)? | ❌ No — the prices **do not exist anywhere** on the site |
| Is `item.price` (the flat-pricing claim in `docs/chargebee_final_state.md:80`) real? | ❌ No — `retrieve_item` returns **no `price` field on any of the 15**; the claim is false |

---

## 1. Evidence base — how the numbers in this document were produced

Everything below is a **read-only** measurement taken from the live TEST site on 2026-10-16. Reproduce with §8.

| Quantity | Tool | Observed |
| :--- | :--- | :--- |
| Items (all) | `list_items` (2 pages of `limit=100`) | **176** |
| Item price rows (all) | `list_item_prices` (4 pages: 100 + 100 + 100 + 14) | **314** |
| Item families | `list_item_families` | **8** |
| Detail on each of the 15 products | `retrieve_item` × 15 | all found, all `active` |

| Distribution | Count |
| :--- | :--- |
| Items by type | `plan` **151** · `charge` **20** · `addon` **5** |
| Item prices by `item_type` | `plan` **300** · `addon` **9** · **`charge` 5** |
| Items with ≥1 price | **161** |
| **Items with 0 prices** | **15 — exactly the 15 `bmj-item-*` storefront products** |
| Item prices whose `item_id` starts with `bmj-item-` | **0** |

> **The two decisive measurements.** (a) The number of `bmj-item-*` item prices is **0**, from both a page-walk of all 314 rows and its inverse (which `item_id`s *are* referenced — the 15 are absent). (b) The 5 `charge`-type prices that **do** exist belong to **other items** (`ABC`, `abc200`, `carrot300`, `pineapple300`, `cbdemo_one-time-setup-fee`) — see §4.
>
> **Why this matters:** a `WARN` log or a swallowed exception proves a **read failed**. It does not prove the **data is absent**. Only a count does. See `PRODUCTION_READINESS_REPORT.md` §4 (`PR-18`) for the false premise that hid this.

### 1.1 The false premise this matrix falsifies

`docs/chargebee_final_state.md:79-80` states:

> *"Charge types use flat pricing via `item.price` field, not separate `item_prices`."*

**Falsified, twice, from live data:**

1. `retrieve_item` on all 15 `bmj-item-*` items returns **no `price` field at all** (the field is absent — `Item` in Chargebee Product Catalog 2.0 has no price; prices live in item prices).
2. **5 `charge` items on this very site already carry item prices** (`abc200-INR`, `carrot300-INR`, `pineapple300-INR`, `ABC-INR`, `cbdemo_one-time-setup-fee`) — e.g. `abc200-INR` is `item_type: "charge"`, `price: 9900`, `pricing_model: "per_unit"`, `status: "active"`. A charge item **can** hold an item price; this site proves it.

The same document books the shortfall as `⚠️ One-time item prices 0/45` — i.e. the gap was **recorded but rationalised away** instead of investigated. `ItemService.java:937` reading `ItemPrice.list()` is the correct implementation; the *data* was never created.

---

## 2. How the storefront resolves a product (the code contract)

`ItemService.getChargeItemsWithCategoriesAndSizes()` (`bmjServer/.../services/ItemService.java:902`) is the single source for `GET /api/v1/catalog/charge-items`:

| Step | Code | Consequence for this matrix |
| :--- | :--- | :--- |
| 1 | `Item.list().limit(100)` **paginated** (`:910-923`) | all 20 charge items are fetched |
| 2 | keep `item.type() == CHARGE` (`:928-930`) | only the 20 charge items are candidates |
| 3 | **category = `familyId` contains `delight` \| `signature` \| `premium`** (`:985-994`; metadata on these items is only `{"is_custom_pricing":false}`) | ⚠️ `Delight-Juices`, `Premium-Juices`, `Signature-Juices` **would also pass** — but the metadata branch at `:951-955` runs first and rejects the legacy items, so **nothing leaks today** (measured). The hazard is latent — `CATALOG_LEGACY_ITEM_REPORT.md` |
| 4 | `ItemPrice.list().limit(200)` — **NOT paginated** (`:937`) | ⚠️ `PR-17`: the call **fails outright** — `limit` 200 exceeds the documented maximum of 100 — so the pre-fetch is dead code and the per-item fallback at `:1112` reads the prices anyway — `CATALOG_PRICE_LOADING_VERDICT.md` |
| 5 | group prices by `item_id` (`:940`) → `extractSizePricesFromList` (`:1109`) | a product with no matching rows gets `prices: []` |
| 6 | size is derived from the price **`name`/`description` containing `200ml` \| `300ml` \| `500ml`** (`:1165-1177`) | **a created price must contain the literal size string** or it is silently discarded |
| 7 | `price` paise → ₹ via `movePointLeft(2)` (`:1144-1146`) | storefront shows ₹ from the paise stored in Chargebee |

**Design consequences:**

- Price `name`/`description` **must** contain `200ml` / `300ml` / `500ml`.
- Prices must be attached to the **same `item_id`** as the storefront item, in the **same `item_family_id`** the category filter matches (`delight` / `signature` / `premium`).
- **Every charge price that exists in this site has `period: null` / `period_unit: null`** — see `CHARGEBEE_PRICE_CREATION_PLAN.md` §4.2.

---

## 3. THE MATRIX — the 15 storefront products

`Item price present?` is answered from the census (`list_item_prices`), not from documentation.

| # | Item ID | Product name | Family | Live Chargebee state | **Item price present?** | # prices | Expected one-time ₹ (200 / 300 / 500ml) |
| :-: | :--- | :--- | :--- | :--- | :-: | :-: | :--- |
| 1 | `bmj-item-mix-punch` | Mix Punch | `delight` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹129 / ₹159 / ₹220 |
| 2 | `bmj-item-carrot-juice` | Carrot Juice | `delight` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹129 / ₹159 / ₹220 |
| 3 | `bmj-item-colon-cleanser` | Colon Cleanser | `delight` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹129 / ₹159 / ₹220 |
| 4 | `bmj-item-beat-the-heat` | Beat the Heat | `delight` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹129 / ₹159 / ₹220 |
| 5 | `bmj-item-winter-special` | Winter Special | `delight` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹129 / ₹159 / ₹220 |
| 6 | `bmj-item-abc-juice` | ABC Juice | `signature` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹141.90 / ₹174.90 / ₹242 |
| 7 | `bmj-item-pineapple` | Pineapple | `signature` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹141.90 / ₹174.90 / ₹242 |
| 8 | `bmj-item-amla-juice` | Amla Juice | `signature` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹141.90 / ₹174.90 / ₹242 |
| 9 | `bmj-item-ashguard-juice` | Ashguard Juice | `signature` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹141.90 / ₹174.90 / ₹242 |
| 10 | `bmj-item-citrus-juice` | Citrus Juice | `signature` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹141.90 / ₹174.90 / ₹242 |
| 11 | `bmj-item-bloody-red` | Bloody Red | `premium` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹156.09 / ₹192.39 / ₹266.20 |
| 12 | `bmj-item-antioxidant-juice` | Antioxidant Juice | `premium` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹156.09 / ₹192.39 / ₹266.20 |
| 13 | `bmj-item-wheatgrass-juice` | Wheatgrass Juice | `premium` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹156.09 / ₹192.39 / ₹266.20 |
| 14 | `bmj-item-coconut-milk` | Coconut Milk | `premium` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹156.09 / ₹192.39 / ₹266.20 |
| 15 | `bmj-item-detox-smoothie` | Detox Smoothie | `premium` | `charge` · active · checkout ✓ · portal ✓ | **❌ N** | 0 | ₹156.09 / ₹192.39 / ₹266.20 |

**Totals: 15 products · 0 item prices present · 45 item prices missing.** Every row reads **N**. All 15 items also carry `metadata: {"is_custom_pricing": false}`, `channel: web`, `deleted: false`.

The items are otherwise **correct and ready** — nothing on the item side needs changing to attach prices.

> ✅ The "Expected one-time ₹" column is the **decoded content of `chargebee_items_payload.json`**. It was *unapproved* when this matrix was written; it has since been **validated against the business workbook `docs/business-requirements/pricing-table.xlsx` (sheet `Pricing`) and agrees 45/45** — see `CHARGEBEE_FINAL_PRICE_MATRIX.md` §3.

---

## 4. What the endpoint actually returns today

> ⚠️ **This section is a *static* replay of the filter chain and it omitted the metadata branch (`:951-955`).** The measured answer, from the runtime log, is **15 items served · 0 priced** — see §10 (`X-1`–`X-4`). The table is retained only to show how the static reading produced the wrong figure:

| Item ID | Name | Matched category | Family | Raw prices | **Usable prices** |
| :--- | :--- | :--- | :--- | :-: | :--- |
| `bmj-item-*` (all 15) | … | delight / signature / premium | delight / signature / premium | 0 | **none → `"prices":[]`** |
| `abc200` | abc200 | *rejected* — `metadata.category = "juice"` | `Premium-Juices` | 1 | **not served** — the family test would have matched `premium`, but the metadata branch runs first |
| `carrot300` | carrot300 | delight | `Delight-Juices` | 1 | none — its price text has no exact `200ml`/`300ml`/`500ml` token (`"…for Carrot 300 ml…"` has a space) |
| `pineapple300` | pineapple300 | delight | `Delight-Juices` | 1 | none — price text is `"customer facing info"` |
| `ABC` | ABC | — | `Juices` | 1 | excluded — family matches no category |
| `cbdemo_one-time-setup-fee` | One-Time Setup Fee | — | `cbdemo_omnisupport-solutions` | 1 | excluded — family matches no category |

> **Column semantics:** "Matched category" is what the **static** replay computed from the family id. The real code consults `metadata.category` **first**, and every legacy item carries `"juice"` — not a valid category — so all of them are rejected before the family test is reached.

**Result (measured from the runtime log — the table above is the superseded static reconstruction): 15 items served · 0 with a price · 15 with `"prices":[]`.**

Two distinct defects are visible in one payload:

1. **`PR-18` (the commercial blocker):** all 15 real products are unpurchasable.
2. **`PR-19` — FALSIFIED as a present defect, retained as a latent risk.** These legacy items are **not** served today: the runtime log rejects each one by name (`Skipping item abc200 - invalid category: juice`) and the endpoint returns exactly **15** items. The static reading in §2 step 3 is what produced the earlier, incorrect claim. See `CATALOG_LEGACY_ITEM_REPORT.md`. *(Nothing was deleted; the hardening is code-side.)*

---

## 5. Missing item prices — the complete gap

**45 missing item prices**, all on the 15 items in §3 (`0 / 45` present):

| Family | Products | Sizes each | Prices missing | Price IDs that must exist |
| :--- | :-: | :-: | :-: | :--- |
| `delight` | 5 | 3 | **15** | `bmj-item-<juice>-200ml` / `-300ml` / `-500ml` |
| `signature` | 5 | 3 | **15** | same pattern |
| `premium` | 5 | 3 | **15** | same pattern |
| **Total** | **15** | — | **45** | — |

Expected one-time prices per product (decoded from `chargebee_items_payload.json`, paise / ₹):

| Family | 200ml | 300ml | 500ml |
| :--- | :--- | :--- | :--- |
| `delight` | 12900 / ₹129.00 | 15900 / ₹159.00 | 22000 / ₹220.00 |
| `signature` | 14190 / ₹141.90 | 17490 / ₹174.90 | 24200 / ₹242.00 |
| `premium` | 15609 / ₹156.09 | 19239 / ₹192.39 | 26620 / ₹266.20 |

> ⚠️ These are the **prepared** values, not approved ones — 8 of the 9 distinct price points disagree with `docs/PRICING_STRUCTURE.md`. Resolution is `CHARGEBEE_PRICE_CREATION_PLAN.md` §3 (`P-1`–`P-5`). The full ready-to-send payload is in §4 of that document.

---

## 6. Subscription pricing — current state (documented **separately** from one-time)

Subscription pricing is **not** affected by `PR-18` and **is already live**. It is documented here so the two pricing models are not conflated, and to stop the one-time gap being "fixed" by re-pointing subscription prices at charge items.

**51 items** carry **102 item prices** (`bmj-generic-*`: 9 items / 18 prices; `bmj-<family>-<juice>-<size>`: 42 items / 84 prices). All are `item_type: plan`, `pricing_model: flat_fee`, `INR`.

| Family | Size | Weekly (paise / ₹) | Implied ₹/bottle | Monthly (paise / ₹) | Implied ₹/bottle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `delight` | 200ml | 46100 / ₹461 | ₹76.83 | 169700 / ₹1,697 | ₹70.71 |
| `delight` | 300ml | 60900 / ₹609 | ₹101.50 | 218900 / ₹2,189 | ₹91.21 |
| `delight` | 500ml | 103900 / ₹1,039 | ₹173.17 | 366500 / ₹3,665 | ₹152.71 |
| `signature` | 200ml | 49200 / ₹492 | ₹82.00 | 184500 / ₹1,845 | ₹76.88 |
| `signature` | 300ml | 64600 / ₹646 | ₹107.67 | 233700 / ₹2,337 | ₹97.38 |
| `signature` | 500ml | 106400 / ₹1,064 | ₹177.33 | 415700 / ₹4,157 | ₹173.21 |
| `premium` | 200ml | 55400 / ₹554 | ₹92.33 | 204200 / ₹2,042 | ₹85.08 |
| `premium` | 300ml | 67000 / ₹670 | ₹111.67 | 243500 / ₹2,435 | ₹101.46 |
| `premium` | 500ml | 112500 / ₹1,125 | ₹187.50 | 440300 / ₹4,403 | ₹183.46 |

**Verified facts:**

- Prices are **per family + size**, identical across the 5 juices of a family (e.g. `bmj-generic-delight-200ml-weekly` and `bmj-delight-mix-punch-200ml-weekly` are both `46100`). **18 distinct price points**, replicated across 51 items.
- **3 items are missing:** `bmj-premium-bloody-red-200ml` / `-300ml` / `-500ml` **do not exist** (census: 0 rows) — the original `⚠️ 42/45` shortfall in `docs/chargebee_final_state.md:63-73`. Their 6 prices are absent too.
- The `premium` family holds `bmj-item-bloody-red` (one-time, §3 #11) but **no** `bmj-premium-bloody-red-*` subscription plan. Legacy `premium-black-grapes-*` items exist in that family but are a **different id space** (`plan`, no `bmj-` prefix) and are not served by this endpoint.
- Implied per-bottle ₹/bottle (§6, ₹76.83–₹187.50) is **far below** the per-bottle figures in `docs/PRICING_STRUCTURE.md` (₹129–₹449), and below the prepared one-time prices (§5). This is the sanity check `P-5` in the creation plan.

**Subscription pricing must not be used to fill the one-time gap.** A `plan` price is recurring; attaching one to a `charge` item is a data-model error — exactly what the abandoned `scripts/chargebee/chargebee_setup_catalog.py:119` did by pointing 45 "one-time" prices at **plan** items `{cat}_{size}ml_weekly`.

---

## 7. Findings

### 7.1 `PR-18` / `B14` — confirmed, and the shape of the fix
15 items × 3 sizes = **45 item prices must be created**. Nothing needs to be fixed, moved or re-linked: the target rows are absent from all 314 existing prices. Creation alone unblocks the storefront: the prices would be served immediately (`PR-17` does not gate visibility — §7.2).

### 7.2 `PR-17` — reclassified: not a blocker for price visibility
`ItemService.java:937` calls `ItemPrice.list().limit(200)`, and **200 exceeds the documented maximum of 100**, so the call **throws on every request** and `pricesByItemId` is always empty. That is not a truncation bug — and because it fails *totally*, the per-item fallback at `:1112` always runs and supplies the prices. **If the 45 prices existed, the catalog would return them.** `PR-17` must still be fixed (N+1 latency, alert blindness, partial-fix hazard), but it does **not** gate the data change: see `CATALOG_PRICE_LOADING_VERDICT.md`.

### 7.3 The price list — RESOLVED by `pricing-table.xlsx`

> **Update (validation):** the business workbook was located at `docs/business-requirements/pricing-table.xlsx` and its sheet `Pricing` **agrees with the payload 45/45**. The table below is retained as history; the `PRICING_STRUCTURE.md` numbers are the stale ones. See `CHARGEBEE_FINAL_PRICE_MATRIX.md` §3 and §7.
This is the business risk underneath `B14`, and the reason creation is **blocked pending Product sign-off**:

| Source | delight 200/300/500 | signature 200/300/500 | premium 200/300/500 |
| :--- | :--- | :--- | :--- |
| `chargebee_items_payload.json` (prepared 45-price payload) | 129 / 159 / **220** | **141.90 / 174.90 / 242** | **156.09 / 192.39 / 266.20** |
| `docs/PRICING_STRUCTURE.md` (per-bottle table) | 129 / 159 / **229** | **199 / 249 / 349** | **299 / 349 / 449** |
| Live subscription, implied ₹/bottle (§6) | 76.83 / 101.50 / 173.17 | 82.00 / 107.67 / 177.33 | 92.33 / 111.67 / 187.50 |

- The payload's `signature` is **exactly `delight × 1.1`** and `premium` **exactly `delight × 1.21`** — a 10 %-step ladder over the delight base, **not** the absolute per-bottle prices documented in `PRICING_STRUCTURE.md`.
- The payload's `delight` 500ml is `22000` (₹220) where both `PRICING_STRUCTURE.md` **and** `scripts/chargebee/import_catalog.py` say `22900` (₹229) — likely a typo.
- Net: **8 of 9 distinct price points differ** between the payload and the documented list. Copying the payload in commits the business to values nobody has formally approved.

### 7.4 The item side is healthy
All 15 items are `active`, `type: charge`, correct family, `enabled_for_checkout: true`, `enabled_in_portal: true`, `channel: web`, `metadata: {"is_custom_pricing": false}`. **No item-side change is required.**

### 7.5 What this changes for the launch gates
- **`B5` smoke probe `2b`** fails *because the data is absent* — this matrix supplies the census proving it is a **data gap, not a code regression** (`PR-17` is the code defect). The probe must **not** be softened or skipped; it stays red until the creation plan is executed.
- The one-line code fixes already catalogued (`PR-16` degraded signal, `PR-14` DTO/`@JsonIgnore`, `PR-15` 401→200 + `D-2` backfill, `PR-12` `SPRING_PROFILES_ACTIVE`, `PR-13` Flyway, `PR-1`/`B8` untracked files) are **unaffected** and remain valid.
- **`B14` can now be stated as a data-action item with a price blocker**, instead of a vague "catalog broken".

---

## 8. Reproduce this matrix (read-only)

```powershell
# 1. Session against the READ-ONLY agent (never the onboarding/write agent)
$t   = 'test_ai_WvyPvGTh7AKfZ6vM6UHOrWZduN1xKiU1Ir_MxccF3-Q'
$url = 'https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent'
$h   = @{Authorization="Bearer $t";'Content-Type'='application/json';Accept='text/event-stream'}
$init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl-client","version":"1.0.0"}}}'
$r   = Invoke-WebRequest -UseBasicParsing -Uri $url -Method Post -Headers $h -Body $init -TimeoutSec 25
$sid = ($r.Headers['mcp-session-id'] | Out-String).Trim()

# 2. Then call ONLY read tools, with header  "mcp-session-id: $sid"
#      list_items        limit=100, page via next_offset   -> expect 176
#      list_item_prices  limit=100, page via next_offset   -> expect 314 (charge = 5)
#      list_item_families                                  -> expect 8
#      retrieve_item     item_id=bmj-item-<x>              -> expect NO "price" field
#
# Assertions this matrix is built on:
#   prices with item_id starting "bmj-item-"   == 0    (§1)
#   of the 314 prices, item_type == "charge"   == 5    (§1, §4)
#   items with type == "charge"                == 20   (§4)
#   items with zero prices                     == the 15 bmj-item-*  (§3)
```

After any change in Chargebee, **re-run the same census** and compare against §7 of `CHARGEBEE_PRICE_CREATION_PLAN.md`.

---

## 9. Cross-reference

| Document | Relationship |
| :--- | :--- |
| [`CHARGEBEE_PRICE_CREATION_PLAN.md`](CHARGEBEE_PRICE_CREATION_PLAN.md) | **The fix** — exact payload, gates, verification, rollback |
| [`PRODUCTION_READINESS_REPORT.md`](PRODUCTION_READINESS_REPORT.md) §3.5 / §4 | `PR-18` root cause and the price census; `PR-17` code defect |
| [`BMJ_LAUNCH_CHECKLIST.md`](BMJ_LAUNCH_CHECKLIST.md) | `B14` row; `B10` (`PR-17`) gate row |
| [`B5_SMOKE_TEST_PLAN.md`](B5_SMOKE_TEST_PLAN.md) | probe `2b`; the code-vs-data discriminator |
| `docs/chargebee_final_state.md` | ⚠️ holds the **falsified** `item.price` premise (§1.1) and the `0/45` line — correct both when `B14` closes |
| `chargebee_items_payload.json` | source of the 45 prepared prices (§5) |
| `docs/PRICING_STRUCTURE.md` | competing price list (§7.3) |
| `scripts/chargebee/import_catalog.py`, `chargebee_setup_catalog.py` | historical, abandoned import shapes — retained only as evidence of the `22000` / plan-linked-price errors |

---

## 10. Correction log (2026-10-16, post-validation)

| # | Corrected | Was | Now | Cause |
| :-: | :--- | :--- | :--- | :--- |
| `X-1` | §0 "items served" | 18 | **15** | the filter was evaluated **statically**; the runtime log is authoritative |
| `X-2` | §0 "with a price" | 1 (`abc200`, ₹99) | **0** | a statically-predicted leak that does not occur — `metadata.category = "juice"` rejects those items first |
| `X-3` | §2 steps 3-4 | "legacy items leak in"; "only 200 of 314 prices are read" | latent hazard only; the batch price call **fails outright** | runtime log + the vendor `limit` maximum of 100 |
| `X-4` | §5/§6 result line and `PR-19` paragraph | "18 served · 1 priced"; "legacy items are served as products" | **15 served · 0 priced**; not served | same as `X-1`/`X-2` |
| `X-5` | §7.2 | "`PR-17` is a hard dependency — `PR-18` alone may still ship `prices:[]`" | `PR-17` **reclassified: non-blocking** for price visibility | the fallback at `:1112` is the live path |
| `X-6` | §7.3 | "the price list is genuinely undecided" | **resolved**: `pricing-table.xlsx` agrees with the payload 45/45 | the workbook was located and parsed |

**Authoritative successors:** `CATALOG_LEGACY_ITEM_REPORT.md` (`X-1`-`X-4`) · `CATALOG_PRICE_LOADING_VERDICT.md` (`X-5`) · `CHARGEBEE_FINAL_PRICE_MATRIX.md` (`X-6`) · `CHARGEBEE_GO_LIVE_RECOMMENDATION.md` (the decision).

---

**End of matrix.** Every count in this document is reproducible from the read-only census in §8; no value has been inferred from documentation where a measurement was possible. **Where this document and the correction log above disagree, the correction log and its successor documents win.**





