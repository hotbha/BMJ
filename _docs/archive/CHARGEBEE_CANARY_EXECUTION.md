# Chargebee Canary Execution — `bmj-item-bloody-red-200ml`

**Status: AUTHORISED — NOT YET EXECUTED.** `G1` granted (canary only, exactly one price).
Nothing in this document has been run against Chargebee except the read-only checks in §1.

| Field | Value |
| :--- | :--- |
| Date prepared | 2026-10-17 |
| Gate | `G1` **APPROVED** — one price, canary only |
| Target | `bmj-item-bloody-red-200ml` (Bloody Red, 200ml, `premium`) |
| Amount | **15609 paise = ₹156.09** (approved: `pricing-table.xlsx` sheet `Pricing`, matched 9/9 in `CHARGEBEE_FINAL_PRICE_MATRIX.md` §3.2) |
| Supersedes | `CHARGEBEE_EXECUTION_PLAN.md` §6 `S-1` — `G1` names Bloody Red, not Mix Punch, as the canary |
| Blast radius | **1 price.** 314 → 315. 15 zero-price items → 14. |

---

## 0. Scope — what is and is not authorised

| | |
| :--- | :--- |
| ✅ **Authorised** | Create **exactly one** item price: `bmj-item-bloody-red-200ml`, ₹156.09, flat fee, taxable |
| ✅ **Authorised** | Verify it through Chargebee → catalog API → Flutter → checkout (§5) |
| ✅ **Authorised** | Delete that one price if any check fails (§6) |
| ⛔ **Not authorised** | The remaining **44** prices |
| ⛔ **Not authorised** | Any change to `ItemService.java`, the Flutter app, or any server config |
| ⛔ **Not authorised** | Editing or deleting an *existing* price (the 5 charge prices are untouched) |
| ⛔ **Not authorised** | Any second attempt after a failure — a failure stops and escalates (§8) |

---

## 1. Pre-write verification — already executed (read-only)

Run 2026-10-17 via `data_lookup_agent`. These are the three facts that must hold *before* a create is safe.

| # | Check | Tool | Result |
| :--- | :--- | :--- | :--- |
| `V-0a` | Item `bmj-item-bloody-red` exists, is a **charge**, is live | `retrieve_item` | ✅ `type: charge`, `status: active`, `item_family_id: premium`, `enabled_for_checkout: true`, `metered: false`, `is_custom_pricing: false`, `updated_at 2026-05-28 05:00:37 UTC` |
| `V-0b` | Price `bmj-item-bloody-red-200ml` does **not** already exist | `retrieve_item_price` | ✅ `404 — "Resource not found: item_price with id bmj-item-bloody-red-200ml is not found"` |
| `V-0c` | The item has **no** prices at all (nothing to collide with) | `list_item_prices` `item_id[is]=bmj-item-bloody-red` | ✅ `{"list": []}` — zero prices |

`V-0b` is the important one: it proves this is a **create**, not an update. Had the id existed we would be modifying a live price, which is out of scope.

The item's family is `premium` **on the item itself** — which is why `item_family_id` must not be sent on create (§3).

| # | Check | Tool | Result |
| :--- | :--- | :--- | :--- |
| `V-0d` | **No write has occurred** — re-verified after this document was prepared | `retrieve_item_price` + `list_item_prices` | ✅ still `404`; item still returns `{"list": []}`; `item_type[is]=charge` still returns **exactly 5** (`abc200-INR`, `carrot300-INR`, `pineapple300-INR`, `ABC-INR`, `cbdemo_one-time-setup-fee`) |

The five live charge prices also corroborate the payload shape: **`ABC-INR` and `cbdemo_one-time-setup-fee` are `flat_fee`** (the other three are legacy `per_unit`), all five are `is_taxable: true` / `status: active` / `channel: web`. `flat_fee` is therefore already proven to work on charge items on this site — the canary is not introducing a new pricing model.


---

## 2. The canary payload

Canonical file: **`x:\BMJ\chargebee_item_prices_canary_payload.json`** (324 bytes)

```json
{
  "itemPrices": [
    {
      "id": "bmj-item-bloody-red-200ml",
      "name": "Bloody Red 200ml",
      "description": "Bloody Red - 200ml",
      "pricing_model": "flat_fee",
      "item_id": "bmj-item-bloody-red",
      "price": 15609,
      "currency_code": "INR",
      "is_taxable": true
    }
  ]
}
```

CSV companion for the dashboard importer: **`x:\BMJ\chargebee_item_prices_canary_payload.csv`**

```csv
id,name,description,item_id,pricing_model,price,currency_code,is_taxable
bmj-item-bloody-red-200ml,Bloody Red 200ml,Bloody Red - 200ml,bmj-item-bloody-red,flat_fee,15609,INR,true
```

| Integrity | |
| :--- | :--- |
| `SHA-256` (JSON) | `100d26fe4a88e6f2e2961d7f51f4cab0b76515704ad892c6aeafa2363d6faab4` |
| Assertions | **8/8 PASS** — `A-1`…`A-8` re-run against the generated file (§4) |


---

## 3. Field-by-field decisions

Every key is deliberate. Eight keys go in the body; six are deliberately absent.

| Key | Value | Why | Source |
| :--- | :--- | :--- | :--- |
| `id` | `bmj-item-bloody-red-200ml` | The id the app and Finance already expect; `B-1` in the matrix. Verified unused (§1 `V-0b`). | matrix row 4 |
| `name` | `Bloody Red 200ml` | **Load-bearing.** Flutter derives size from `price.name` via `RegExp(r'(\d+ml)')` — `_extractSizes` (`product_catalog_bloc.dart:406-420`) and the size filter (`:306-308`) both match on the name, **not** on the DTO's `size` field. No `200ml` in the name ⇒ the price is created, billed, and never rendered (`A-2`). | live code |
| `description` | `Bloody Red - 200ml` | Human-readable on invoices; also carries the size token as a second chance for `extractSizeFromItemPrice` (`ItemService.java:1165-1177`), which checks name **or** description. | `ItemService.java` |
| `pricing_model` | `flat_fee` | One-time charge item. `tiered`/`volume` would require `tiers` and change the billing engine. | matrix |
| `item_id` | `bmj-item-bloody-red` | Link to the existing charge item (§1 `V-0a`). **Required** on create. | API docs |
| `price` | `15609` | **Minor units (paise).** Server does `BigDecimal.valueOf(price).movePointLeft(2)` → `156.09` (`ItemService.java:1144-1146`). Sending `156.09` would bill ₹1.56. | live code + matrix |
| `currency_code` | `INR` | Matches the 5 live charge prices and the item. | live read |
| `is_taxable` | `true` | Matches all 5 live charge prices exactly. See the correction note below. | live read |

### Deliberately omitted

| Key | Omitted because |
| :--- | :--- |
| `period` | `C-1` — recurrence. A one-time charge has no period; sending one is what made the 2026-05-28 import create 15 items and **0** prices. Docs confirm `period` is mandatory only for `plan`/`addon` items, "not writable for charge item prices". |
| `period_unit` | `C-2` — same reason as `period`. |
| `trial_period` | `C-3` — trial semantics belong to subscriptions; meaningless on a one-time charge. |
| `trial_period_unit` | `C-3` — as above. |
| `tiers` | `C-3` — only valid for `tiered` / `volume` / `stairstep`. With `flat_fee` it is noise at best, a validation error at worst. |
| `item_family_id` | **`C-6` (new).** Read-only on `item_price` create — it is derived from `item_id`. Verified live: the item's family is already `premium`. Sending a read-only field risks a rejected canary for no benefit. |

> **Correction to `C-5`'s rationale (recorded, not rewritten).** The execution plan justified `is_taxable: true` on the grounds that omitting it would create the only non-taxable prices on the site. Chargebee's create schema documents `is_taxable` as **optional, defaulting to `true`**. So `C-5` is *belt-and-braces explicitness*, not a defect fix. The instruction stands (send it — asserted in `A-8`); only the "would otherwise be wrong" claim was overstated. Live evidence still supports mirroring the 5 existing charge prices exactly.

### The unit trap — read before creating

Chargebee's **API** takes `price` in **minor units** (paise → `15609`). The **dashboard importer** displays amounts in the **account currency** (rupees → `156.09`). If the import is fed `15609` where it expects `156.09`, the result is **₹15,609.00 — a 100× price on a live site.**

This is precisely what the canary exists to catch, and it must be caught in the **import preview**, before the commit:

- Preview shows **156.09** → correct → proceed.
- Preview shows **15,609.00** → **STOP.** Do not commit. Re-import `156.09`, or use the REST path (§5, option B) which takes paise unambiguously.

`A` of §6 re-checks the stored value independently: pass only if it reads **15609 paise**.

---

## 4. Payload assertions — re-run on the generated file

Executed against `chargebee_item_prices_canary_payload.json` — **8/8 PASS**.

| # | Assertion | Result |
| :--- | :--- | :--- |
| `A-1` | exactly 1 row | ✅ |
| `A-2` | `200ml` present in name/description | ✅ |
| `A-3` | `price` is an integer and equals `15609` | ✅ |
| `A-4` | only the 8 allowed keys are present | ✅ |
| `A-5` | `currency_code` is `INR` | ✅ |
| `A-6` | `item_id` is `bmj-item-bloody-red`; `item_family_id` **not sent** | ✅ |
| `A-7` | none of `period`, `period_unit`, `trial_period`, `trial_period_unit`, `tiers` | ✅ |
| `A-8` | `is_taxable` is boolean `true` | ✅ |

---

## 5. Mechanism — and why the canary must use the batch's mechanism

The 44 remaining prices will be created by **import**. A canary created by a *different* mechanism (e.g. a single REST POST) would prove the payload shape and the read path, but **not** the import tooling — leaving the 44 exposed to exactly the failure that hit the 2026-05-28 import. So:

**Option A — import (primary, matches the batch).**
Import `chargebee_item_prices_canary_payload.csv` through the Chargebee dashboard item-price importer. Single row, single file. Apply the unit gate above at the preview.

**Option B — REST (fallback, only if the importer is unavailable).**
`POST /api/v2/item_prices` with the JSON body fields as flat form params
(`id`, `name`, `description`, `item_id`, `pricing_model=flat_fee`, `price=15609`, `currency_code=INR`, `is_taxable=true`).
Unambiguous units, atomic, trivially reversible (`DELETE /api/v2/item_prices/bmj-item-bloody-red-200ml`).
**If Option B is used, record that the import path remains unvalidated** — the canary no longer de-risks the batch, and the first batch must then be run as its own 1-item canary.

Neither agent exposes a granular item-price *create* or *delete* tool — hence a file/REST action plus a manual rollback (§7).

---

## 6. Verification checklist — A → B → C → D, in that order

Each step is a gate: **do not proceed to the next until the current one passes.** Record actual values in §10.

### A — Chargebee shows the price

| | |
| :--- | :--- |
| Command | `data_lookup_agent` → `retrieve_item_price` `{"item_price_id":"bmj-item-bloody-red-200ml"}` |
| Must show | `id = bmj-item-bloody-red-200ml`, `item_id = bmj-item-bloody-red`, `price = 15609`, `currency_code = INR`, `pricing_model = flat_fee`, `is_taxable = true`, `status = active`, `name` containing `200ml` |
| Also | `list_item_prices` with `item_id[is]=bmj-item-bloody-red` returns **exactly 1** row |
| **Kill switch** | `price` ≠ `15609` (e.g. `1560900`, or `156`) → **roll back now** (§7). This is the unit trap. |

### B — Catalog API returns the price

| | |
| :--- | :--- |
| Precondition | `bmjServer` running on `:8080`. Route is `permitAll` — no token needed (`WebSecurityConfig.java:92`). |
| Command | `Invoke-RestMethod http://localhost:8080/api/v1/catalog/charge-items` |
| Find | the object with `itemId = "bmj-item-bloody-red"` → its `prices` array |
| Must show | exactly **1** element: `priceId = bmj-item-bloody-red-200ml`, `name = Bloody Red 200ml`, `size = 200ml`, `price = 156.09`, `currencyCode = INR`, `pricingModel = flat_fee` |
| Before this canary | that same `prices` array was `[]` (the item is one of the 15 zero-price items) — so a **non-empty array is the proof** |
| Note | A restart is **not** required: the DTO is assembled per request from a per-item Chargebee read (`ItemService.java:1112` → `extractSizePrices` → `:1126-1128`). The `limit(200)` pre-fetch still throws and is still swallowed (`:937-944`) — that is the known, tolerated path, unchanged by this canary. |

`price` must read **156.09** here, not `15609` — the server already divided by 100 (`:1144-1146`). If it reads `15609.00`, the price was stored in rupees and the browser will show ₹15,609 → roll back.

### C — Flutter displays the price

| | |
| :--- | :--- |
| Steps | Launch the app → Premium category → Bloody Red. Confirm **₹156.09** renders on the 200ml size and the item becomes selectable. |
| Why it was broken | the size chips and the size filter both require a non-empty `prices` list (`product_catalog_bloc.dart:306-308`, `:406-420`) — with `[]` the item could not be filtered, selected, or priced |
| Also check | The **200ml** size chip now counts this item. The other 4 Premium items stay unpriced — expected, and proof the change is scoped to one item. |
| **Kill switch** | price shows but size is wrong/missing → the `name` token is wrong; fix by correcting the name, not by patching Flutter |

### D — Checkout uses the price

| | |
| :--- | :--- |
| Steps | Add Bloody Red 200ml to cart → confirm the cart call carries `priceId = bmj-item-bloody-red-200ml` (`cart_repository.dart:312-315` → `POST /api/v1/cart/items`) → open checkout and read the line amount |
| Must show | line amount **₹156.09**, currency INR, quantity 1, tax applied per the site's tax profile |
| **Limit** | Stop at the **checkout preview**. **Do not complete a payment** — G1 authorises creating a price, not creating a subscription or taking money. Completing checkout needs its own authorisation. |
| **Kill switch** | amount ≠ ₹156.09, or an "invalid item price" error → the price is not usable for billing → roll back (§7) |

---

## 7. Rollback

Target state after rollback = the state captured in §1: price absent, item has 0 prices, site at 314 prices.

| # | Step | Detail |
| :--- | :--- | :--- |
| `R-1` | **Delete the price** | Dashboard: `Items → Item prices → bmj-item-bloody-red-200ml → Delete`. Or REST: `DELETE /api/v2/item_prices/bmj-item-bloody-red-200ml`. One record. |
| `R-2` | **Confirm it is gone** | `retrieve_item_price` → must return `404 not found`; `list_item_prices item_id[is]=bmj-item-bloody-red` → must return `{"list": []}` |
| `R-3` | **Confirm the site is back to baseline** | total item prices **314**; `item_type[is]=charge` prices **5**; items with zero prices **15** |
| `R-4` | **Undo any checkout side effect** | If `D` created a cart line, subscription or invoice, void/delete it separately — deleting the price does **not** clean those up. Escalate to the named owner; this is outside G1 and needs its own approval. |

Rollback is **one operation on one record**, which is the entire reason the blast radius was held at 1.
If `R-1` fails (permission denied / price in use), the abort path is §8 `X-3` — not a retry.

---

## 8. Stop conditions

| # | Condition | Action |
| :--- | :--- | :--- |
| `X-1` | Import preview shows any amount other than **156.09** | Cancel before commit. No write. |
| `X-2` | Import reports **partial** success, or creates more than 1 record | Roll back (§7), then stop. Do not "fix forward". |
| `X-3` | `R-1` delete is refused | Stop immediately; escalate. Leave the price in place, do not attempt alternatives. |
| `X-4` | `A` passes but `B` returns `prices: []` | Stop. Do not touch Flutter or Java — this is a data problem until proven otherwise. |
| `X-5` | Any prompt to create the **remaining 44** | Refuse. G1 covers one price. |
| `X-6` | Any prompt to create 2–44 prices "since the canary worked" | Refuse. A batch needs a fresh, written authorisation. |

---

## 9. Go / no-go

**GO — for this single price; every precondition is met:**

| Requirement | State |
| :--- | :--- |
| Written authorisation for exactly one price | ✅ `G1` |
| Target item exists, right type | ✅ `charge`, `active`, `premium` (§1) |
| Target id does not already exist | ✅ `404` (§1) |
| Amount cross-checked against the business workbook | ✅ `15609` paise, 9/9 exact in matrix §3.2 |
| Payload satisfies `C-1`…`C-6` | ✅ 8/8 assertions (§4) |
| Rollback is a single, known operation | ✅ `R-1` (§7) |
| Blast radius | ✅ 1 price |
| Same mechanism as the batch | ✅ import (Option A) |

**NO-GO — what stays blocked:**

| Item | Why |
| :--- | :--- |
| The remaining **44** prices | not authorised; and their payload does not exist yet — only the single-row canary file was generated |
| Any Flutter / `bmjServer` change | not needed: the read path already works and is frozen |
| Completing a real payment in step `D` | G1 covers creating a price, not a subscription or a charge |
| Scaling to 45 on the strength of this canary | the canary proves 1 of 45; the size-token check (`A-2`) and the unit trap must be re-asserted per batch |

> **Recommendation: GO — canary only.** Create `bmj-item-bloody-red-200ml` at ₹156.09 via Option A, holding at the import preview until the amount reads `156.09`; then run `A → B → C → D` in order and stop at the checkout preview. Record the evidence in §10 and **stop**. The 44 stay untouched pending review.

---

## 10. Evidence log — to be filled during execution

| Check | Expected | Actual | Verdict |
| :--- | :--- | :--- | :--- |
| Import preview amount | `156.09` | | |
| `A` `retrieve_item_price` | `price 15609`, `is_taxable true`, `status active` | | |
| `A` price count for item | exactly 1 | | |
| `B` `/api/v1/catalog/charge-items` | `prices` length 1, `price 156.09`, `size 200ml` | | |
| `C` Flutter Premium → Bloody Red | ₹156.09 on 200ml, selectable | | |
| `D` cart line | `priceId = bmj-item-bloody-red-200ml` | | |
| `D` checkout preview | ₹156.09, tax applied | | |
| Site totals after | 315 prices / 6 charge-type / 14 zero-price items | | |

Signed off by: __________________________  Date: ______________

