# ADR-005: Charge-Based Catalog — Chargebee as the Sole Pricing Source

**Date:** October 16, 2026
**Status:** ACCEPTED
**Supersedes:** the `item.price` premise in `docs/chargebee_final_state.md:79-80`; the per-bottle price table in `docs/PRICING_STRUCTURE.md:17-35`
**Related:** ADR-003 (Chargebee Integration & Data Sync), ADR-004 (Unified Signup Flow)

---

## Context

The one-time ("bottle") catalog is **visible but not purchasable**: 15 `bmj-item-*` products exist in Chargebee TEST as `type: charge`, the site holds 314 ItemPrices, and **0** of them belong to those 15 products. The storefront therefore renders every product with `"prices":[]` (`B14` / `PR-18`).

Three competing answers were on the table:

| Option | Outcome |
| :--- | :--- |
| Serve prices from a local source (Flutter constants, DB seed, JSON asset) | ❌ **Rejected** — creates a second source of price truth; diverges silently from checkout, invoices and Chargebee-hosted pages |
| Model one-time bottles as Plans or Add-ons | ❌ **Rejected** — category error: plans and add-ons are recurring objects, a bottle is a `charge` |
| **Charge items + per-size `ItemPrice` records** | ✅ **Chosen** — the only modelling Chargebee's own checkout accepts |

The gap went undetected because of a **false premise in our own documentation**: `docs/chargebee_final_state.md:79-80` states *"Charge types use flat pricing via `item.price` field, not separate `item_prices`"*. This is false — no `bmj-item-*` item carries `price`, and the read path consumes `ItemPrice` objects exclusively.

**Measured read path** (source of truth for this ADR; see `CATALOG_PRICE_LOADING_VERDICT.md`):

| Line | Behaviour |
| :--- | :--- |
| `ItemService.java:951-958` | category = `metadata.category` first, then `item_family_id`; invalid category → item **skipped** |
| `:1109-1113` | prices come from the pre-fetched map **if** populated, else from a per-item `ItemPrice.list().itemId().is(...)` call |
| `:1144-1146` | `price` (paise) → ₹ via `BigDecimal.movePointLeft(2)` |
| `:1165-1177` | the size token is derived from `ItemPrice.name` / `description` containing `200ml` / `300ml` / `500ml` |
| `:1230-1234` `cacheItemsLocally` | a **no-op placeholder** — *"Items are already cached via webhooks"*; it writes nothing |
| `:1255-1264` `convertEntityToChargeItemDTO` | builds the DTO **without** `prices` → the DB-cache fallback (`:1239-1250`) **cannot** serve a price |
| `:974-979` | any upstream failure falls back to the **local DB cache** |

---

## Decision

1. **Charge-based catalog confirmed.** A one-time product is a Chargebee `item` of `type: charge`, carrying **one `ItemPrice` per sellable size** (200ml / 300ml / 500ml), `pricing_model: flat_fee`, `currency_code: INR`, `price` in **paise**.
2. **Chargebee is the sole source of price values.** No price may be written into code, docs, tests, seed data, CI fixtures or the database as an input to a price decision.
3. **No pricing logic in the Flutter client.** The app remains a renderer of the `prices` array served by bmjServer. It must not compute, adjust, default or fall back to a price.
4. **bmjServer is a read-through cache, never an author.** Anything it stores locally (ADR-003 CQRS) is *derived* from Chargebee, is never hand-edited, and loses to Chargebee on any disagreement.
5. **No alternate pricing source may be introduced** — not in Flutter assets/constants, not in DB seeds, not in a new service, not in documentation, not in CI.
6. **Price mutations happen only in Chargebee**, through the sanctioned MCP path (`import_product_catalog`), under change control with a named rollback owner.
7. **Existing code is frozen for this change.** The 45-price population is a **data** change. `ItemService`, `CatalogController` and the whole `lush/**` tree are not edited by it.

### Invariants (machine-checkable)

| # | Invariant | Check |
| :-: | :--- | :--- |
| `I-1` | 45 `ItemPrice` objects exist — 3 per item × 15 items | `list_item_prices` per item returns 3 |
| `I-2` | each `price` equals the approved workbook value, in paise | join against `docs/business-requirements/pricing-table.xlsx` |
| `I-3` | each `name` **or** `description` contains the literal size token | `ItemService.java:1165-1177` |
| `I-4` | `pricing_model: flat_fee`, `currency_code: INR`, `item_id` = the intended item | `retrieve_item_price` per id |
| `I-5` | **zero** price literals in `lush/lib/**` | static scan |
| `I-6` | **zero** price tables outside Chargebee | static scan + review |
| `I-7` | items remain `type: charge`, `deleted: false`; legacy `metadata.category = "juice"` items remain unserved | live census |

---

## Consequences

### Positive

1. **One source of price truth** — storefront, checkout, invoices and hosted pages cannot disagree.
2. **No client release to change a price** — no rebuild, no store submission.
3. **Closes `B14` / `PR-18` without touching application code** — the frozen read path already serves the required shape.

### Negative / accepted trade-offs

1. **Prices are not available offline.** If Chargebee is unreachable and the webhook-populated cache is empty, the catalog is empty — and `PR-16` can currently present that as `200 []`. The remedy is `PR-16`, **not** a local price table.
2. **A price change becomes an operational act**, not a code review; it requires Chargebee access and an audit trail.
3. `period` / `period_unit` / `trial_*` / `tiers` are **plan/addon-only** fields, undocumented for `charge`. Including them is a category error and is the leading hypothesis for the failed import (`CHARGEBEE_IMPORT_ROOT_CAUSE.md` §0).
4. `PR-17` (the pre-fetch requesting `limit(200)` against a vendor maximum of 100) leaves the intended N+1 optimisation **dead** — every request uses the per-item path. Non-blocking for correctness; tracked as performance debt.

### Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Someone re-introduces a local price table "for speed" | Price shown ≠ price charged | This ADR; `I-5`/`I-6`; stale tables marked non-authoritative |
| The bulk import is **not transactional** (vendor-documented) | Partial creation: some prices land, some silently skip | Canary-first sequencing, per-id read-back, closing census |
| A price lands without its size token | The item keeps `"prices":[]` with no error anywhere | `I-3` asserted on the payload **before** the write and on the read-back **after** each batch |
| TEST and production diverge | Prod behaves differently at launch | Same corrected payload, same verification, run against prod before go-live |
| A created id is later reused for something else | Wrong price shown on a product | Ids are deterministic (`<item_id>-<size>ml`) and reserved by `I-1` |

---

## Implementation Checklist

- [x] Execution plan written — `CHARGEBEE_EXECUTION_PLAN.md` (execution itself remains blocked on `G1`/`G5`)
- [ ] Populate the 45 one-time item prices — `CHARGEBEE_EXECUTION_PLAN.md` (**requires written authorisation**)
- [ ] Correct `docs/chargebee_final_state.md:79-80` to describe `ItemPrice`, not `item.price`
- [x] Mark `docs/PRICING_STRUCTURE.md:17-35` **non-authoritative** (wrong at 8 of 9 points) — 2026-10-16
- [x] Annotate `scripts/chargebee/chargebee_setup_catalog.py:72-76` as a historical artefact, not a price source — 2026-10-16
- [ ] Add a static guard so no price literal can enter `lush/lib/**` (activation needs separate approval)
- [ ] Record in the release notes that **no Flutter change** was required — and why

---

## References

- `CHARGEBEE_FINAL_PRICE_MATRIX.md` — the 45 approved rows and their target ids
- `CHARGEBEE_IMPORT_ROOT_CAUSE.md` — why the 2026-05-28 import created the items but skipped the prices
- `CATALOG_PRICE_LOADING_VERDICT.md` — proof that created prices will be served without code changes
- `CATALOG_LEGACY_ITEM_REPORT.md` — the `metadata.category` guard, and why it must not be "simplified"
- `docs/CHARGEBEE_MCP.md` — sanctioned MCP agents and their tool surfaces
- `docs/business-requirements/pricing-table.xlsx` — the approved price list

## Notes

The two MCP agents are **not** interchangeable. `data_lookup_agent` is read-only (40 tools). `onboarding_agent` is destructive (10 tools) and can write catalog data **only** via `import_product_catalog` — there is **no granular item-price create/update/delete tool**. That single fact constrains both execution (the canary must be a minimal import, not a single create) and rollback (deletion is manual or REST, not tool-driven). See the execution plan §5/§8.

---

**Approved By:** Product + Engineering — architecture decision recorded 2026-10-16
**Approval Date:** October 16, 2026
**Review Date:** after the one-time catalog go-live
