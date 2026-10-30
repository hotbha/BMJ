# Chargebee one-time prices — Price Variants mapping (approved Option A)

> **Generated:** 2026-10-29 · **Site:** `bookmyjuice-test` (TEST) · **Currency:** INR, stored in **paise**
> **Decision:** Option A of [`CHARGEBEE_ONE_TIME_PRICE_MODELLING_DECISION.md`](CHARGEBEE_ONE_TIME_PRICE_MODELLING_DECISION.md) — **approved**
> **Status:** prepared, **not yet written to Chargebee** beyond the 2 pre-existing 200 ml prices.
> **Enablement request:** [`CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md`](CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md)

## 1. Target model

```
15 charge items  x  3 price variants  =  45 charge item prices
   bmj-item-mix-punch             bmj-200ml -> bmj-item-mix-punch-200ml  (INR 129.00)
   (one per product, unchanged)   bmj-300ml -> bmj-item-mix-punch-300ml  (INR 159.00)
                                  bmj-500ml -> bmj-item-mix-punch-500ml  (INR 220.00)
```

Chargebee's uniqueness key becomes **item + currency + price variant**, which is
what makes the second and third INR price on the same `charge` item legal.

**Nothing else changes:** the same 15 items, the same price ids, the same
names/descriptions, the same `flat_fee` pricing model, the same amounts. The
only addition to each price is `price_variant_id`.

## 2. The three price variants

Create these once, site-wide (they are not per item):

| `id` | `name` | `description` | Used by |
| :--- | :--- | :--- | :--- |
| `bmj-200ml` | 200 ml | One-time 200ml bottle | 15 prices (`…-200ml`) |
| `bmj-300ml` | 300 ml | One-time 300ml bottle | 15 prices (`…-300ml`) |
| `bmj-500ml` | 500 ml | One-time 500ml bottle | 15 prices (`…-500ml`) |

Do **not** create a fourth variant: with variant pricing enabled, a price
*without* `price_variant_id` becomes the "no variant / default" price point, and
only one of those is allowed per item + currency. Keeping every one-time price
on one of the three variants above keeps the model uniform.

## 3. Enablement (owner: Chargebee site admin)

Documented path — **Settings → Configure Chargebee → Product Catalog → Price Variants → Enable**
(<https://www.chargebee.com/docs/billing/2.0/product-catalog/variant-pricing-enable>).

The API currently reports the feature as unavailable for this site:

```
list_price_variants -> "This API operation is not enabled for this site.
                        Please contact support@chargebee.com to get this enabled"
```

So: try the UI toggle first; if the toggle is absent or the API still refuses,
send the prepared support request. Verify with:

```
python _captures/cb_variants.py          # read-only probe
python _captures/chargebee_price_rollout.py preflight
```

`preflight` prints `price variants: READY` only when the API works **and** all
three variants exist; otherwise it lists exactly what is missing and writes
nothing.

## 4. Product → price mapping (all 45 rows)

Variant per size: `200ml → bmj-200ml`, `300ml → bmj-300ml`, `500ml → bmj-500ml`.

| Family | Product | Item (15) | 200 ml | 300 ml | 500 ml |
| :--- | :--- | :--- | :--- | :--- | :--- |
| delight | Mix Punch | `bmj-item-mix-punch` | `…-200ml` ₹129.00 | `…-300ml` ₹159.00 | `…-500ml` ₹220.00 |
| delight | Carrot Juice | `bmj-item-carrot-juice` | `…-200ml` ₹129.00 | `…-300ml` ₹159.00 | `…-500ml` ₹220.00 |
| delight | Colon Cleanser | `bmj-item-colon-cleanser` | `…-200ml` ₹129.00 | `…-300ml` ₹159.00 | `…-500ml` ₹220.00 |
| delight | Beat the Heat | `bmj-item-beat-the-heat` | `…-200ml` ₹129.00 | `…-300ml` ₹159.00 | `…-500ml` ₹220.00 |
| delight | Winter Special | `bmj-item-winter-special` | `…-200ml` ₹129.00 | `…-300ml` ₹159.00 | `…-500ml` ₹220.00 |
| signature | ABC Juice | `bmj-item-abc-juice` | `…-200ml` ₹141.90 | `…-300ml` ₹174.90 | `…-500ml` ₹242.00 |
| signature | Pineapple | `bmj-item-pineapple` | `…-200ml` ₹141.90 | `…-300ml` ₹174.90 | `…-500ml` ₹242.00 |
| signature | Amla Juice | `bmj-item-amla-juice` | `…-200ml` ₹141.90 | `…-300ml` ₹174.90 | `…-500ml` ₹242.00 |
| signature | Ashguard Juice | `bmj-item-ashguard-juice` | `…-200ml` ₹141.90 | `…-300ml` ₹174.90 | `…-500ml` ₹242.00 |
| signature | Citrus Juice | `bmj-item-citrus-juice` | `…-200ml` ₹141.90 | `…-300ml` ₹174.90 | `…-500ml` ₹242.00 |
| premium | Bloody Red | `bmj-item-bloody-red` | `…-200ml` ₹156.09 | `…-300ml` ₹192.39 | `…-500ml` ₹266.20 |
| premium | Antioxidant Juice | `bmj-item-antioxidant-juice` | `…-200ml` ₹156.09 | `…-300ml` ₹192.39 | `…-500ml` ₹266.20 |
| premium | Wheatgrass Juice | `bmj-item-wheatgrass-juice` | `…-200ml` ₹156.09 | `…-300ml` ₹192.39 | `…-500ml` ₹266.20 |
| premium | Coconut Milk | `bmj-item-coconut-milk` | `…-200ml` ₹156.09 | `…-300ml` ₹192.39 | `…-500ml` ₹266.20 |
| premium | Detox Smoothie | `bmj-item-detox-smoothie` | `…-200ml` ₹156.09 | `…-300ml` ₹192.39 | `…-500ml` ₹266.20 |

`…` expands to the item id without the `bmj-item-` prefix repeated — i.e.
`bmj-item-mix-punch` + `-200ml` = `bmj-item-mix-punch-200ml` (the exact ids are
in [`chargebee_items_payload.json`](chargebee_items_payload.json), which
`python _captures/chargebee_price_rollout.py plan` prints in full).

Amounts are **paise** in the payload (`12900` = ₹129.00) because Chargebee
stores INR in the lowest unit; the catalog API divides by 100 before the client
sees it.

## 5. What the storefront sees (contract unchanged)

`GET /api/v1/catalog/charge-items` (`ItemService.getChargeItemsWithCategoriesAndSizes`)
already builds one row per product with a `prices[]` array, and derives the size
from each price's **name/description** (`extractSizeFromItemPrice`: `200ml` /
`300ml` / `500ml`). Because every price keeps its size token in both name and
description (asserted as **A-2** in the rollout payload checks), a variant-tagged
price lands in exactly the same place as before:

```json
{
  "itemId": "bmj-item-mix-punch",
  "name": "Mix Punch",
  "category": "delight",
  "prices": [
    { "priceId": "bmj-item-mix-punch-200ml", "size": "200ml", "price": 129.00, "currencyCode": "INR" },
    { "priceId": "bmj-item-mix-punch-300ml", "size": "300ml", "price": 159.00, "currencyCode": "INR" },
    { "priceId": "bmj-item-mix-punch-500ml", "size": "500ml", "price": 220.00, "currencyCode": "INR" }
  ]
}
```

Therefore, per the approved decision:

* **no Flutter change** — the PDP size sheet, `ItemPrice.fromJson`,
  `cheapestPricedOption` and cart continue to read `prices[]`;
* **no `ItemService` change** — size parsing is by name/description, not by variant;
* **no catalog regrouping** — still 15 item rows;
* **no checkout change** — the cart already sends the existing `price_id`.

`price_variant_id` is Chargebee-side metadata only. It is *not* required in the
API response; adding it later would be additive, not breaking.

## 6. Runbook (gated, in order)

```
# 0. read-only state
python _captures/chargebee_price_rollout.py plan        # A-1..A-10 on 45 rows
python _captures/chargebee_price_rollout.py preflight   # variants enabled + 3 exist
python _captures/chargebee_price_rollout.py census      # 2/45 today

# 1. one row
python _captures/chargebee_price_rollout.py canary      # 1/1, read back + assert

# 2. families, stopping on any failure
python _captures/chargebee_price_rollout.py batch delight      # 15
python _captures/chargebee_price_rollout.py batch signature    # 15
python _captures/chargebee_price_rollout.py batch premium      # 14 (1 canary row already exists)

# 3. prove it
python _captures/chargebee_price_rollout.py verify      # 45/45 read-back assertions
python _captures/chargebee_price_rollout.py census      # approved 45/45, 0 zero/negative, 0 non-INR
python _captures/chargebee_catalog_check.py             # Home -> PDP -> Cart -> Checkout prices
```

Per-row gates enforced by the script:

| Check | Rule |
| :--- | :--- |
| A-1 | exactly 45 rows, unique ids |
| A-2 | id, name **and** description carry the size token |
| A-3 | exactly 15 items, each with 200/300/500 ml |
| A-5 | positive integer paise, INR only |
| A-6 | family ∈ delight / signature / premium |
| A-7 | `pricing_model=flat_fee`, exactly the 9 create keys |
| A-8 | `is_taxable=true` |
| **A-9** | `price_variant_id` equals the variant of the row's size |
| **A-10** | no two rows share `(item_id, currency_code, price_variant_id)` |
| read-back | stored name/item/pricing_model/currency/price/is_taxable/status/item_type/**price_variant_id** match |

Idempotency: the create call carries
`chargebee-idempotency-key = uuid5("bmj-price:<price_id>")` and every row that
already exists is skipped and re-verified, never rewritten.

Safety gate: `canary` and `batch` run `preflight` first and stop with exit 1 if
variant pricing is unavailable or a variant is missing — no price can be written
while the site is not ready (verified 2026-10-29: `canary` exits 1 and writes
nothing).

## 7. The two prices that already exist (reconciliation)

`census` today reports:

```
approved prices     : 2/45
with price variant  : 0/45
no-variant prices   : bmj-item-mix-punch-200ml, bmj-item-bloody-red-200ml
```

Both were created before variant pricing was available, so they are the item's
**default (no variant) price point**. They do not block the rollout — a
variant-tagged price is a different price point — but they must be tagged before
`verify` can go green (it compares `price_variant_id`) and to keep the model
uniform.

**Recommended fix (needs approval, UI only):** in Chargebee open each of the two
item prices and set its **price variant** to `bmj-200ml`. The ids, names,
descriptions and amounts stay identical, so nothing in the catalog or client
changes and no price id is orphaned.

The MCP surface exposes only `create_an_item_price` for writes, so this cannot be
done from the scripts; do **not** archive-and-recreate these two rows unless the
UI edit is impossible — that would churn ids that the storefront already serves.

## 8. Rollback

* Variant rollout adds prices only; nothing is overwritten. To reverse a batch,
  archive the created item prices in Chargebee (UI) — the rollout's `census`
  then reports them missing and a rerun recreates them.
* Enabling Price Variants is a site setting; Chargebee does not document a
  revert path, so treat enablement as one-way for the TEST site and confirm
  parity in production before enabling it there.
* The 2 default 200 ml prices remain valid either way.
