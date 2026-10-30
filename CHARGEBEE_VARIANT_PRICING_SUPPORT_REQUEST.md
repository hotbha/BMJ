# Request: enable Price Variants (Variant Pricing) on `bookmyjuice-test`

> **Prepared:** 2026-10-29 · **Action owner:** Chargebee site admin (then, if needed, Chargebee support)
> **Blocked work:** the 45 approved one-time prices — see
> [`CHARGEBEE_PRICE_VARIANTS_MAPPING.md`](CHARGEBEE_PRICE_VARIANTS_MAPPING.md)
> **Writes performed so far:** none in this pass; the site holds 2 of the 45 prices
> (`bmj-item-mix-punch-200ml`, `bmj-item-bloody-red-200ml`), both created before this request.

## 1. Why this is needed

Chargebee stores only **one INR price point per `charge` item** unless Price
Variants is enabled. The approved catalogue needs three price points per product
(200 / 300 / 500 ml), so the first attempt to add the second size was rejected:

```
POST create_an_item_price  (body: bmj-item-bloody-red-300ml)
HTTP 400
An item price with INR currency code already exists for this charge item
```

With Price Variants enabled the uniqueness key becomes
**item + currency + price variant**, which is exactly the model we need. The
read-only check currently reports the feature as unavailable for this site:

```
$ list_price_variants
"This API operation is not enabled for this site. Please contact support@chargebee.com to get this enabled"
```

## 2. Primary path — self-service toggle

Chargebee documents Variant Pricing as a site setting:

1. **Settings → Configure Chargebee → Product Catalog → Price Variants**
2. Click **Enable**.
3. Create the three variants (Product Catalog → Price Variants → Create):

| id | name | description |
| :--- | :--- | :--- |
| `bmj-200ml` | 200 ml | One-time 200ml bottle |
| `bmj-300ml` | 300 ml | One-time 300ml bottle |
| `bmj-500ml` | 500 ml | One-time 500ml bottle |

Docs: [Enabling Variant Pricing](https://www.chargebee.com/docs/billing/2.0/product-catalog/variant-pricing-enable) ·
[Configuring a Price Variant](https://www.chargebee.com/docs/billing/2.0/product-catalog/variant-pricing-config) ·
[Impact on other features](https://www.chargebee.com/docs/billing/2.0/product-catalog/variant-pricing-impacted-features)

The API must also stop refusing `list_price_variants`; the toggle alone is only
sufficient if that call starts returning a list.

## 3. Fallback — support ticket (copy/paste)

> **Subject:** Enable Price Variants / Variant Pricing API on site `bookmyjuice-test`
>
> **Body:**
> Hello Chargebee Support,
>
> We use Product Catalog 2.0 on our test site `bookmyjuice-test` (API key scoped
> to that site). We need **Variant Pricing (Price Variants)** enabled so a single
> `charge` item can hold more than one INR price point.
>
> Attempting to create a second INR price on the same charge item is rejected:
> `An item price with INR currency code already exists for this charge item`.
>
> Attempting to list price variants returns:
> `This API operation is not enabled for this site. Please contact support@chargebee.com to get this enabled`.
>
> Please confirm whether Price Variants is available for this site, and enable it
> (plus API access to the `price_variants` resource) if it is not yet active.
>
> For context, our target model is 15 charge items × 3 price variants
> (200 ml / 300 ml / 500 ml) = 45 one-time prices. We do not need any data
> migration; the 2 existing no-variant INR prices can stay as-is.
>
> Please also confirm whether enabling the feature is reversible, since we would
> later enable it on our production site as well.
>
> Thank you.

## 4. Acceptance check (run after enablement)

```
python _captures/cb_variants.py                             # read-only probe: API works?
python _captures/chargebee_price_rollout.py preflight        # variants enabled + 3 variants exist
python _captures/chargebee_price_rollout.py plan             # A-1..A-10 on the 45 rows
python _captures/chargebee_price_rollout.py canary           # 1/1, read back and asserted
```

`preflight` must print `price variants: READY` before any batch runs. It exits
non-zero and prints the exact missing variant ids otherwise, and it never writes.

Once the canary passes, the rollout continues exactly as documented in
[`CHARGEBEE_PRICE_VARIANTS_MAPPING.md`](CHARGEBEE_PRICE_VARIANTS_MAPPING.md) §6
(delight → signature → premium, then `verify` and `census`).

## 5. If variants cannot be enabled

Only then produce a scoped impact assessment for **Option B** (one `charge` item
per product+size), per the approved instruction. Option B is **not** to be
implemented without that separate approval, because it changes the catalogue
contract the storefront consumes.
