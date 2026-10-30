# Chargebee one-time price modelling — decision needed

> **Generated:** 2026-10-29 · **Site:** `bookmyjuice-test` (TEST) · **Currency:** INR
> **Status:** ✅ **OPTION A APPROVED (2026-10-29)** — variant rollout prepared, gated on Chargebee enablement.
> **Evidence:** read-only MCP calls only (`census`, `list_price_variants`, plan-price
> shape probe). Nothing was created, updated or deleted in this pass.

**Prepared artefacts after approval**

| Artefact | Purpose |
| :--- | :--- |
| [`CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md`](CHARGEBEE_VARIANT_PRICING_SUPPORT_REQUEST.md) | Enablement request: UI toggle first, copy-paste support ticket as fallback. |
| [`CHARGEBEE_PRICE_VARIANTS_MAPPING.md`](CHARGEBEE_PRICE_VARIANTS_MAPPING.md) | Target model, the 3 variants, all 45 rows, runbook, A-9/A-10 gates, the 2-row reconciliation, rollback. |
| [`chargebee_items_payload.json`](chargebee_items_payload.json) | All 45 rows now carry `price_variant_id` (`bmj-200ml` / `bmj-300ml` / `bmj-500ml`). |
| [`_captures/cb_add_price_variants.py`](_captures/cb_add_price_variants.py) | Idempotent payload preparation (`--check` reports without writing). |
| [`_captures/chargebee_price_rollout.py`](_captures/chargebee_price_rollout.py) | 9-key body shaping, A-9/A-10 payload assertions, `price_variant_id` read-back, and the `preflight` gate. |

Option B is **not** to be implemented; it is revisited only if Chargebee confirms variants cannot be enabled.

## 1. What the approved plan assumes

[`CHARGEBEE_FINAL_PRICE_MATRIX.md`](CHARGEBEE_FINAL_PRICE_MATRIX.md) approves
**45 one-time prices = 15 products × 3 sizes (200 / 300 / 500 ml)**, modelled as
**three `charge` item prices on one `charge` item per product**
(`bmj-item-bloody-red` → `bmj-item-bloody-red-200ml|300ml|500ml`).

That model is not implementable on this site.

## 2. What actually happened

| Step | Result |
| :--- | :--- |
| `plan` | 45 rows valid, schema A-1..A-8 pass |
| `canary` | ✅ `bmj-item-bloody-red-200ml` created and read back (1/1) |
| first `batch delight` row (`bmj-item-bloody-red-300ml`) | ❌ **HTTP 400** — `An item price with INR currency code already exists for this charge item` |
| second independent success | `bmj-item-mix-punch-200ml` (canary rerun for another product) |

Live census (`python chargebee_price_rollout.py census`):

```
item prices on site : 316
by item_type        : addon=9, charge=7, plan=300
approved prices     : 2/45
zero/negative prices: 0
non-INR prices      : 0
```

So **2 of the 45 exist**, both 200 ml, both on their own item. The remaining 43
are the two other sizes of those products plus the 13 untouched products.

## 3. Why it is blocked

Chargebee's uniqueness rule for a **`charge`** item price is
`item_id + currency_code` — a charge price has no period, so there is no second
dimension to differentiate a second INR price on the same item. Multiple
same-currency price points on one item are only allowed with **Variant Pricing**
enabled, where the uniqueness key becomes currency + price variant.

Variant Pricing is **not enabled on this site**, and it cannot be enabled
through the API:

```
list_price_variants -> "This API operation is not enabled for this site.
                        Please contact support@chargebee.com to get this enabled"
```

## 4. How the live catalog models sizes today (the consistency argument)

Read-only probe of the 300 plan prices
([`_captures/cb_plan_shape.py`](_captures/cb_plan_shape.py)):

```
bmj-delight-carrot-juice-200ml: 2 prices -> [...-weekly, ...-monthly]
bmj-delight-carrot-juice-300ml: 2 prices -> [...-weekly, ...-monthly]
```

* Sizes are **separate items** (`…-200ml`, `…-300ml`, `…-500ml`).
* The two prices on one item differ by **period** (weekly vs monthly), which is
  allowed on `plan` prices without variants.

So the subscription catalogue avoids variants by using item-per-size. The
one-time catalogue cannot express "3 sizes on 1 item" at all without variants.

## 5. Options

### Option A — enable Variant Pricing in Chargebee (recommended)

* **Owner:** Chargebee support (`support@chargebee.com`) — a site-level setting
  (Settings → Product Catalog → Price Variants) that must be switched on for
  `bookmyjuice-test` (and later for production).
* **Catalogue change:** none in the approved matrix. All 45 prices stay on the
  15 `bmj-item-*` items; each row additionally carries
  `price_variant_id` = `200ml` / `300ml` / `500ml` (three price variants created
  once, one per size).
* **Rollout change:** small and contained — add `price_variant_id` to the 45-row
  payload, extend the 8-key body shaping in
  [`_captures/chargebee_price_rollout.py`](_captures/chargebee_price_rollout.py)
  by one key, revalidate A-1..A-8, rerun `plan` → `canary` → `batch`.
* **Client contract:** **unchanged.** `GET /api/v1/catalog/charge-items` keeps
  returning one row per product with a `prices[]` array of three sizes, which is
  exactly what the PDP size sheet and `ItemPrice.fromJson` already consume.
* **Risk:** waiting on Chargebee support; the two existing rows are compatible
  (they can be attached to the 200 ml variant later, or left as the
  no-variant default).

### Option B — one `charge` item per (product, size), no variants

* **Owner:** this repo; no Chargebee support involvement.
* **Catalogue change:** 45 items instead of 15 (`bmj-item-bloody-red-200ml` is
  now an *item*, not a price), each holding exactly one INR price. Consistent
  with how plan sizes are modelled.
* **Client/backend change (the cost):** the whole catalogue contract assumes
  "one item = one product, `prices[]` = its sizes":
  * `ItemService.getChargeItems()` → one row per item with a `prices[]` array
    (grouping, category derivation from item family/metadata).
  * Flutter `ItemPrice.fromJson` / `dynamic_item` / `dynamic_juice` → size list
    per product; the PDP size sheet and `cheapestPricedOption` iterate it.
  * Cart, checkout `price_id` usage, and the catalog check script.
  All of these need a product↔size regrouping layer (match by a shared
  `product_id` in `meta_data`, or strip the `-200ml` suffix) plus tests.
* **Risk:** this is a catalogue-contract change during a launch freeze, and it
  touches the PDP/cart/checkout money path.

## 6. Recommendation

**Option A.** It is the only option that keeps the approved 45-price matrix and
the existing storefront contract intact; the only external dependency is a
Chargebee support ticket, and the two prices already created stay valid.

If Option A is not acceptable (support delay is too long for launch), Option B
is technically sound but must be scheduled as an explicit catalogue-contract
change, not slipped into the price rollout.

## 7. State after this pass (nothing to clean up)

* 2 prices exist and are correct in isolation (INR, positive, `flat_fee`,
  `charge` item). The rollout is **idempotent**: `census` reports 2/45 and
  `create_one` skips existing rows, so either option resumes cleanly.
* `nextDeliveryAt` work (independent of this blocker) is complete — see
  [`_captures/README.md`](_captures/README.md) §"Subscription Next delivery".
