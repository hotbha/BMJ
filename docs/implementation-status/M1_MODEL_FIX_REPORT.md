# M1 Model Fix Report

> **Date:** 2026-05-27  
> **Scope:** Fixes 1-6 from docs/data_models_map.md audit  
> **Status:** Complete  

## Fixes 1-3 (HIGH priority)

| Fix | File | Flag | What changed |
|-----|------|------|-------------|
| 1 | `dynamic_item.dart` | FLAG-002 | `fromApiResponse()`: camelCase JSON keys → snake_case with camelCase fallback. Added `_parseBool()` helper. |
| 2 | `dynamic_item.dart` | FLAG-003 | Dead `as bool? ?? false` expressions → `_parseBool()` calls. Removed dead `as String?` null-checks. |
| 3 | `item.dart` | FLAG-006 | Split `toJson()` → `toChargebeeJson()` + `toDisplayJson()`. `cart_repository.dart` caller updated to `toDisplayJson()`. |

## Fixes 4-6 (MEDIUM priority)

| Fix | File | Flag | What changed |
|-----|------|------|-------------|
| 4 | `contact.dart` | FLAG-004 | Added `fromJson()` (snake_case with camelCase fallback), `toJson()` (snake_case), `toDisplayJson()` (camelCase). |
| 5 | `address.dart` | FLAG-005 | Standardized getter naming: `getFirstName` → `firstNameGetter`, `extendedaddr` → `extendedAddrGetter`, `statecode` → `stateCodeGetter`. Consistent `XxxGetter` convention. |
| 6 | `plan.dart` | FLAG-011 | Replaced empty file with skeleton class. Plan model unused — all plan handling uses inline `SubscriptionPlan` in `subscription_bloc.dart`. |

## Address Getter Usages Updated

| File:line | Old getter | New getter |
|-----------|-----------|------------|
| (none) | `extendedaddr` | `extendedAddrGetter` |
| (none) | `statecode` | `stateCodeGetter` |
| (none) | `getFirstName` (on Address) | `firstNameGetter` |

No external callers existed — 0 files required updates outside address.dart.

## Plan.dart Decision

- **Used in codebase:** No — zero usages of `Plan` class
- **Action taken:** Skeleton with TODO. All plan handling uses `SubscriptionPlan` inline in `subscription_bloc.dart`.

## Final Flutter Analyze

- **Models directory:** 0 errors, 0 warnings (1 info: trailing comma in address.dart)  
- **Full lib/:** 0 errors, 0 warnings (976 info-level findings, all pre-existing)  
- **No new issues introduced**