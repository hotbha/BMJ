# Subscription checkout — Product Catalog 2.0 migration (P0)

Date: 2026-10-29 · Chargebee site `bookmyjuice-test` (catalog **2.0**) · SDK `chargebee-java 3.34.0`

## 1. What was wrong

Every subscription hosted page was built with the catalog **1.0** call:

```java
HostedPage.checkoutNew().customerId(id).subscriptionPlanId(planId)   // POST /hosted_pages/checkout_new
```

On a catalog 2.0 site Chargebee rejects it with
`API endpoint is incompatible with the product catalog version`, so **no subscription could be
created at all**. 4 call sites were affected.

## 2. Exact Chargebee API now used

| | |
|---|---|
| Endpoint | **`POST /api/v2/hosted_pages/checkout_new_for_items`** |
| SDK call | `HostedPage.checkoutNewForItems()` → `HostedPage.CheckoutNewForItemsRequest` |
| Plan | `subscription_items[item_price_id][0] = <item_price_id>` |
| Customer | `customer[id] = <chargebee_customer_id>` |
| Reserved subscription id | `subscription[id] = <reserved id>` (unchanged join key) |

Verified request shape (from `Request.uri()` / `Request.params()`):

```
method = POST
uri    = /hosted_pages/checkout_new_for_items
param: [customer[id]]                         = bmj-cust-0001
param: [subscription_items[item_price_id][0]] = bmj-delight-mix-punch-200ml-weekly
param: [subscription[id]]                     = bmj-sub-reserved-0001
```

`subscription[plan_id]` (catalog 1.0) is **never** sent any more — asserted by the new unit test.

## 3. Code changes

| File | Change |
|---|---|
| `bmjServer/.../services/SubscriptionApiService.java` | `createSubscriptionHostedPage(customer, plan, reservedId)` now calls the new package-private `buildHostedPageRequest(...)`, which builds `checkoutNewForItems` + `subscriptionItemItemPriceId(0, planId)` + optional `subscriptionId(reserved)`. `getPricingPageUrl(...)` **removed** — a plan-less `checkoutNew` page has no catalog 2.0 equivalent, it had no controller route, and `PricingPageController` already answers `410 Gone`. |
| `bmjServer/.../services/SubscriptionCheckoutService.java` | Both flows (`checkoutSubscription` cart flow, `checkoutSubscriptionDirect`) call the new `buildHostedPageRequest(chargebeeCustomerId, planId)`. Quantity behaviour deliberately unchanged (still not sent) so the charged amount does not change as a side effect. |
| `bmjServer/src/test/java/.../services/SubscriptionCheckoutCatalog2Test.java` | **New.** 7 tests pinning the request: endpoint URI, method, item price index 0, customer id, reserved id present/absent, legacy `subscription[plan_id]` absent, quantity absent. No network. |

Preserved unchanged: plan catalogue, `DeliveryScheduleService.reserve()` before checkout, reserved-id
join to the `subscription_created` webhook, `nextDeliveryAt` / `deliverySchedule` publication, response
shapes, all other endpoints.

## 4. Plan item prices — verified, not assumed

`_captures/plan_price_census.py` (read-only, via the Chargebee data-lookup MCP) over all 300 plan item
prices on the test site:

```
category   size    day       week      month     year
delight    200ml   MISSING   ok        ok        MISSING
delight    300ml   MISSING   ok        ok        MISSING
delight    500ml   MISSING   ok        ok        MISSING
signature  200ml   MISSING   ok        ok        MISSING
```

* **weekly = 56, monthly = 149** plan prices exist, active, INR.
* **`bmj-*-day` and `bmj-*-year` do not exist** (there is no daily or yearly bmj plan). The 91 `day`
  prices belong to other (demo) items.
* Naming is *not* guessable: `bmj-signature-abc-weekly` does not exist —
  `bmj-signature-abc-juice-200ml-weekly` does.

Verified individually (`_captures/verify_plan_prices.py`, `retrieve_item_price`):

| item_price_id | price | period | item_type | status |
|---|---|---|---|---|
| `bmj-delight-mix-punch-200ml-weekly` | INR 461.00 | 1 week | plan | active |
| `bmj-delight-mix-punch-200ml-monthly` | INR 1697.00 | 1 month | plan | active |
| `bmj-delight-mix-punch-300ml-weekly` | INR 609.00 | 1 week | plan | active |
| `bmj-delight-mix-punch-300ml-monthly` | INR 2189.00 | 1 month | plan | active |
| `ip-0007` (id served to the app by `/api/subscriptions/pricing/plans`) | INR 774.00 | 6 days | plan | active |

## 5. Verification

### 5.1 Compile
`mvnw.cmd -DskipTests compile` → BUILD SUCCESS. `mvnw.cmd -DskipTests package` → BUILD SUCCESS
(`target/com.bookmyjuice.bmjServer-0.0.2-SNAPSHOT.jar`, 15:48).

### 5.2 Unit tests
* New: `SubscriptionCheckoutCatalog2Test` → **7/7 pass** (4 in `ApiService`, 3 in `CheckoutService`).
* Full suite with the dev DB env loaded: **219 run, 4 failures, 6 errors** — all pre-existing and in auth
  only (`AuthControllerTest$SignupTests` ×2 expect the old `500` that signup no longer returns,
  `PasswordlessSignupTests`, `UnifiedSignupTests`, `OTPUtilTest` ×6 `smsService` is null). None touch
  subscription code. Without the env loaded, 17 errors are `Access denied for user 'bmj'@'localhost'`
  (a missing-`SPRING_DATASOURCE_URL` artefact, not code).

### 5.3 Integration / live subscription checkout
`_captures/subscription_checkout_validation.ps1` — QA user → signin → `POST /api/subscriptions/create`
(real Chargebee, no payment).

| Plan | HTTP | hostedPageId | reserved subscriptionId |
|---|---|---|---|
| Weekly `bmj-delight-mix-punch-200ml-weekly` | 200 | `MBgZGzXjgJMcuDq37dBurd6H64lngZ1dT` | `bmj4477b28155ec4b7a908b36393cd83c06` |
| Monthly `bmj-delight-mix-punch-200ml-monthly` | 200 | `YX0RWi0ZcucUvZIOzTkEGhSpoYfcu7gZVcu` | `bmj97ff84514647460da77ef80d9af37c54` |
| App plan `ip-0007` (served by `/api/subscriptions/pricing/plans`) | 200 | `5rrzso83gorKTxmlfPfWcuIx2u3pmhJLR` | `bmj6f86d21a74f14e179d474ed55726fb82` |

Hosted pages rendered (Playwright):

| Hosted page | Rendered line item | Amount | Next charge | Proceed |
|---|---|---|---|---|
| weekly | `Delight Mix Punch 200ml Weekly` | ₹461.00 /week | November 5, 2026 | enabled |
| monthly | `Delight Mix Punch 200ml Monthly` | ₹1,697.00 /month | November 29, 2026 | enabled |
| ip-0007 | `Carrot Juice 200ml Weekly` | ₹774.00 /6 days | — | enabled |

Screenshots: `hosted-weekly.png`, `hosted-monthly.png`, `hosted-app-plan-ip-0007.png`.
Raw responses: `weekly-create.json`, `monthly-create.json`, `result.json`.

Server log (`bmjServer/logs/local-run.log`):

```
15:54:52 INFO SubscriptionApiService - Creating subscription hosted page for customer: 16CS3UVZQtF20nFJ to plan: bmj-delight-mix-punch-200ml-weekly
15:54:53 INFO SubscriptionApiService - Subscription hosted page created successfully: MBgZGzXjgJMcuDq37dBurd6H64lngZ1dT
15:54:54 INFO SubscriptionApiService - Creating subscription hosted page for customer: 16CS3UVZQtF20nFJ to plan: bmj-delight-mix-punch-200ml-monthly
15:54:54 INFO SubscriptionApiService - Subscription hosted page created successfully: YX0RWi0ZcucUvZIOzTkEGhSpoYfcu7gZVcu
```

### 5.4 Delivery schedule persistence still works
`delivery_schedule` rows carry the reserved ids that went to Chargebee, so the
`subscription_created` webhook can still join schedule → subscription:

```
bmj4477b28155ec4b7a908b36393cd83c06  16CS3UVZQtF20nFJ  {"friday":"true","monday":"true","wednesday":"true"}  2026-10-29 10:24:52
bmj97ff84514647460da77ef80d9af37c54  16CS3UVZQtF20nFJ  {"friday":"true","monday":"true","wednesday":"true"}  2026-10-29 10:24:54
```

### 5.5 Nothing was charged
`retrieve_subscription("bmj4477b28155ec4b7a908b36393cd83c06")` → *"Resource not found"*. No subscription,
invoice or payment exists; only the hosted page was created, as intended for this test.

## 6. Remaining, out of scope of this migration

1. **Legacy `/api/v1/subscribe` and `/api/v1/subscribe/direct`** (both migrated) cannot be exercised
   live: they validate `planId` against the **empty `subscription_plans` table** and fail with
   `Invalid subscription plan: ...` before Chargebee is reached. Pre-existing data gap; the app uses
   `POST /api/subscriptions/create` (`lush/lib/services/subscription_service.dart:112`), proven above.
2. **`DeliveryScheduleService.reserve()` runs before the Chargebee call** in all three checkout paths, so
   an abandoned or failed checkout leaves a `delivery_schedule` row with no subscription (this run added
   three such rows). Moving the reserve after a successful hosted-page creation, or adding a sweeper,
   is still open.
3. Chargebee price variants (`data.list_price_variants`) remain disabled on the site — the 43 one-time
   prices still cannot be written (`catalog_audit.py` reports `items=15 prices=2 target=45`).
