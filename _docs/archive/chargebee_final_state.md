# Chargebee Final State

> **Site:** bookmyjuice-test  
> **Type:** TEST environment — not production  
> **Date updated:** 2026-05-28  
> **Source:** `chargebee_catalog.json` + MCP imports (batches 1-2)  
> **Plans created:** 2026-05-28 via Chargebee MCP  

## Environment

| Property | Value |
|----------|-------|
| Site | bookmyjuice-test |
| Environment | TEST |
| Currency | INR (all prices in paise — divide by 100 for rupees) |

## Item Families (3)

| ID | Name | Description |
|----|------|-------------|
| `delight` | Delight | Entry-level juice subscription category |
| `signature` | Signature | Mid-range juice subscription category |
| `signature` | Premium | Premium juice subscription category |

## TYPE A — Generic Plans (9 items × 2 prices = 18 prices)

One generic plan per family × size. Customer picks juice flavor on the day-wise screen.

| Item ID | Name | Family | Size | Weekly (paise/₹) | Monthly (paise/₹) |
|---------|------|--------|------|:---:|:---:|
| `bmj-generic-delight-200ml` | Delight 200ml | delight | 200ml | 46,100 / ₹461 | 169,700 / ₹1,697 |
| `bmj-generic-delight-300ml` | Delight 300ml | delight | 300ml | 60,900 / ₹609 | 218,900 / ₹2,189 |
| `bmj-generic-delight-500ml` | Delight 500ml | delight | 500ml | 103,900 / ₹1,039 | 366,500 / ₹3,665 |
| `bmj-generic-signature-200ml` | Signature 200ml | signature | 200ml | 49,200 / ₹492 | 184,500 / ₹1,845 |
| `bmj-generic-signature-300ml` | Signature 300ml | signature | 300ml | 64,600 / ₹646 | 233,700 / ₹2,337 |
| `bmj-generic-signature-500ml` | Signature 500ml | signature | 500ml | 106,400 / ₹1,064 | 415,700 / ₹4,157 |
| `bmj-generic-premium-200ml` | Premium 200ml | premium | 200ml | 55,400 / ₹554 | 204,200 / ₹2,042 |
| `bmj-generic-premium-300ml` | Premium 300ml | premium | 300ml | 67,000 / ₹670 | 243,500 / ₹2,435 |
| `bmj-generic-premium-500ml` | Premium 500ml | premium | 500ml | 112,500 / ₹1,125 | 440,300 / ₹4,403 |

## TYPE B — Juice-Specific Plans (42/45 items × 2 prices = 84/90 prices)

### Delight Family (15 items)

| Juice | 200ml Item ID | 300ml Item ID | 500ml Item ID |
|-------|--------------|--------------|--------------|
| Mix Punch | `bmj-delight-mix-punch-200ml` | `bmj-delight-mix-punch-300ml` | `bmj-delight-mix-punch-500ml` |
| Carrot Juice | `bmj-delight-carrot-juice-200ml` | `bmj-delight-carrot-juice-300ml` | `bmj-delight-carrot-juice-500ml` |
| Colon Cleanser | `bmj-delight-colon-cleanser-200ml` | `bmj-delight-colon-cleanser-300ml` | `bmj-delight-colon-cleanser-500ml` |
| Beat the Heat | `bmj-delight-beat-the-heat-200ml` | `bmj-delight-beat-the-heat-300ml` | `bmj-delight-beat-the-heat-500ml` |
| Winter Special | `bmj-delight-winter-special-200ml` | `bmj-delight-winter-special-300ml` | `bmj-delight-winter-special-500ml` |

### Signature Family (15 items)

| Juice | 200ml Item ID | 300ml Item ID | 500ml Item ID |
|-------|--------------|--------------|--------------|
| ABC Juice | `bmj-signature-abc-juice-200ml` | `bmj-signature-abc-juice-300ml` | `bmj-signature-abc-juice-500ml` |
| Pineapple | `bmj-signature-pineapple-200ml` | `bmj-signature-pineapple-300ml` | `bmj-signature-pineapple-500ml` |
| Amla Juice | `bmj-signature-amla-juice-200ml` | `bmj-signature-amla-juice-300ml` | `bmj-signature-amla-juice-500ml` |
| Ashguard Juice | `bmj-signature-ashguard-juice-200ml` | `bmj-signature-ashguard-juice-300ml` | `bmj-signature-ashguard-juice-500ml` |
| Citrus Juice | `bmj-signature-citrus-juice-200ml` | `bmj-signature-citrus-juice-300ml` | `bmj-signature-citrus-juice-500ml` |

### Premium Family (12/15 items — 3 failed due to name conflicts)

| Juice | 200ml Item ID | 300ml Item ID | 500ml Item ID |
|-------|--------------|--------------|--------------|
| Black Grapes | ⚠️ FAILED | ⚠️ FAILED | ⚠️ FAILED |
| Antioxidant Juice | `bmj-premium-antioxidant-juice-200ml` | `bmj-premium-antioxidant-juice-300ml` | `bmj-premium-antioxidant-juice-500ml` |
| Wheatgrass Juice | `bmj-premium-wheatgrass-juice-200ml` | `bmj-premium-wheatgrass-juice-300ml` | `bmj-premium-wheatgrass-juice-500ml` |
| Coconut Milk | `bmj-premium-coconut-milk-200ml` | `bmj-premium-coconut-milk-300ml` | `bmj-premium-coconut-milk-500ml` |
| Detox Smoothie | `bmj-premium-detox-smoothie-200ml` | `bmj-premium-detox-smoothie-300ml` | `bmj-premium-detox-smoothie-500ml` |

> ⚠️ **Known Issue:** 3 premium-black-grapes items failed with "Internal name must be unique" — conflicting with old catalog entries. Must be manually cleaned in Chargebee dashboard before retry.

All juice-specific prices match their generic plan of same family+size.

## One-Time Juice Items (15)

Created 2026-05-28 via MCP. Type: `charge`. IDs: `bmj-item-*` pattern.
Charge types use flat pricing via `item.price` field, not separate `item_prices`.

## Summary

| Type | Created | Target | Status |
|------|:------:|:------:|--------|
| TYPE A generic items | 9 | 9 | ✅ Complete |
| TYPE A prices (weekly+monthly) | 18 | 18 | ✅ Complete |
| TYPE B juice-specific items | 42 | 45 | ⚠️ 3 failed (premium-black-grapes) |
| TYPE B prices | 84 | 90 | ⚠️ 6 prices failed (dependent on failed items) |
| One-time order items | 15 | 15 | ✅ Complete |
| One-time item prices | 0 | 45 | ⚠️ Charge type doesn't use item_prices |
| **Total items** | **66** | **69** | |
| **Total prices** | **102** | **108** | |

## Chargebee JSON Field Names (snake_case)

| Chargebee Key | Dart Field (in DynamicItem) | Type |
|---------------|---------------------------|------|
| `id` | `itemID` | String |
| `name` | `name` | String |
| `description` | `description` | String |
| `type` | `type` | String |
| `item_family_id` | `itemFamilyId` | String |
| `metered` | (not in DynamicItem) | bool |
| `metadata` | `metaData` | Map |
| `status` | `status` | String |
| `item_prices` | `itemPrices` | List |