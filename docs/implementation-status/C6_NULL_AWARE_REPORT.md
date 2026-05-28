# C6 Dead Null-Aware Expression Audit Report

> **Date:** 2026-05-28
> **Scope:** Audit dead `??` null-aware expressions against CHARGEbee field nullability

## dynamic_item.dart

Already fixed by M1 (FIX 1+2). `_parseBool` helper replaced all `as bool? ?? false` patterns. Remaining `??` on strings are legitimate metadata-extracted fields.

## Fixes Applied

| File:line | Field | Case | Action taken |
|-----------|-------|------|-------------|
| (none) | — | — | No removals needed |

## Left in place (Case B — legitimate null safety)

| File:line | Reason kept |
|-----------|------------|
| `cart_repository.dart:219` | Error recovery catch block — creates minimal valid Item when JSON parsing fails. Removing `??` risks null crash on corrupted SharedPreferences data. |
| `cart_repository.dart:220` | Same error recovery context — `name` may be missing from corrupted JSON. |
| `cart_repository.dart:222` | Same error recovery context — `servingSize` may be missing from corrupted JSON. |
| `cart_repository.dart:235` | Error recovery for selectedPrice — creates minimal valid ItemPrice. |
| `cart_repository.dart:236` | Same error recovery context. |
| `cart_repository.dart:257` | Default quantity fallback — `quantity` may be missing from corrupted JSON. |
| `cart_repository.dart:259` | Default size fallback — `selectedSize` may be missing from corrupted JSON. |
| `subscription_bloc.dart:180-184` | `copyWith` pattern in `ActiveSubscription` — `?? this.field` preserves existing value when new value is null. Legitimate Dart pattern, not dead code. |

## Flutter Analyze

Before: 0 errors, 0 warnings
After: 0 errors, 0 warnings

## Test Results

Baseline: 133 passed, 6 failed — confirmed (zero new failures)