# CACHE Module — Detailed Test Cases

> **Document Version:** 1.0
> **Last Updated:** 2026-05-11

---

**Note:** Cache module is partially implemented. The `ItemService` has local caching logic (`cacheItemsLocally`, `getItemsFromLocalCache`). These tests verify the caching behavior.

## TC-CACHE-001: Local cache fallback on API failure (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CACHE-001 |
| **Module** | CACHE |
| **Type** | Unit |
| **Priority** | P1-High |
| **Severity** | S1-Major |
| **Preconditions** | Mock ItemService, simulate API failure |
| **Steps** | fetchItems() when Chargebee API fails |
| **Expected** | Falls back to local database cache |
| **Auto** | ✅ Automated |

## TC-CACHE-002: CacheItemsLocally no-throw guarantee (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CACHE-002 |
| **Module** | CACHE |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Mock ItemService |
| **Steps** | cacheItemsLocally(validItems) |
| **Expected** | Does not throw exception |
| **Auto** | ✅ Automated |

## TC-CACHE-003: IdempotencyService cache size tracking (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CACHE-003 |
| **Module** | CACHE |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Fresh IdempotencyService |
| **Steps** | getTrackedEventCount() |
| **Expected** | 0 |
| **Auto** | ✅ Automated |

## TC-CACHE-004: RateLimiterService — token bucket cache behavior (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CACHE-004 |
| **Module** | CACHE |
| **Type** | Unit |
| **Priority** | P2-Medium |
| **Severity** | S2-Minor |
| **Preconditions** | Fresh RateLimiterService |
| **Steps** | isAllowed multiple times on same key |
| **Expected** | Returns true for first calls |
| **Auto** | ✅ Automated |

## TC-CACHE-005: Empty local cache returns empty list (NEW)

| Field | Value |
|-------|-------|
| **ID** | TC-CACHE-005 |
| **Module** | CACHE |
| **Type** | Unit |
| **Priority** | P3-Low |
| **Severity** | S3-Trivial |
| **Preconditions** | Empty database |
| **Steps** | getItemsFromLocalCache() |
| **Expected** | Returns empty list |
| **Auto** | ✅ Automated |

## Total: 5 test cases (all new)
