# Chargebee TEST Site Verification

> **Date:** 2026-05-28
> **Site:** bookmyjuice-test (TEST environment)
> **Source:** `chargebee_final_state.md` + MCP data lookup agent verification

## Item Counts

| Category | ID Pattern | Target | Actual | Status |
|----------|-----------|:------:|:------:|--------|
| Generic subscription | `bmj-generic-*` | 9 | 9 | ✅ |
| Juice-specific (delight) | `bmj-delight-*-*` | 15 | 15 | ✅ |
| Juice-specific (signature) | `bmj-signature-*-*` | 15 | 15 | ✅ |
| Juice-specific (premium) | `bmj-premium-*-*` | 15 | 12 | ⚠️ 3 missing |
| One-time order | `bmj-item-*` | 15 | 15 | ✅ |
| **Total items** | | **69** | **66** | |
| **Total item prices** | | **153** | **102** | ⚠️ |

## Missing Items

### STEP 3 needed: premium-black-grapes (3 items × 2 prices = 6 total)

| Item ID | Size | Weekly Price | Monthly Price |
|---------|------|:-----------:|:------------:|
| `bmj-premium-black-grapes-200ml` | 200ml | 55,400 paise / ₹554 | 204,200 paise / ₹2,042 |
| `bmj-premium-black-grapes-300ml` | 300ml | 67,000 paise / ₹670 | 243,500 paise / ₹2,435 |
| `bmj-premium-black-grapes-500ml` | 500ml | 112,500 paise / ₹1,125 | 440,300 paise / ₹4,403 |

**Root cause:** "Internal name must be unique" — conflicting with old catalog entries.
**Fix:** Manual cleanup in Chargebee dashboard required, then MCP import_product_catalog.

## Environment

- Site: bookmyjuice-test
- Environment: TEST
- API Key: test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E (read-only test key)
- MCP Agent: onboarding_agent (import tools), data_lookup_agent (query tools)