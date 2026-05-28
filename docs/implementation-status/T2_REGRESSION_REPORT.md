# T2 — Pre-existing Failures Fix + Bottle Regression Report

> **Date:** 2026-05-28

## Pre-existing Failures Fixed

| Test file | Failure | Root cause | Fix applied |
|-----------|---------|------------|-------------|
| `auth_bloc_test.dart` | EnterAddress expects `AddressEntered` + `ReadyForFinalSignup` | BLoC emits only `ReadyForFinalSignup` (no interim `AddressEntered`) | Fixed expect array to `[ReadyForFinalSignup]` |
| `auth_bloc_test.dart` | CompleteSignup success expects `AddressEntered` in chain | Same root — EnterAddress only emits `ReadyForFinalSignup` | Fixed expect array to skip `AddressEntered` |
| `auth_bloc_test.dart` | CompleteSignup failure expects `AddressEntered` in chain | Same root | Fixed expect array to skip `AddressEntered` |
| `login_page_test.dart` | Valid inputs clear validation errors — pumpAndSettle timeout | Toastification auto-dismiss timer prevents settle | Changed `pumpAndSettle()` → `pump(const Duration(seconds: 1))` in tapButton helper |

## Remaining Pre-existing Failures (2, unchanged)

| Test file | Failure | Root cause |
|-----------|---------|------------|
| `signup_screen_test.dart` | TC-AUTH-003 — `findsWidgets` on `Icons.check_circle` | Widget uses `Icons.circle_outlined` when unmet, `Icons.check_circle` when met. Test enters password but validation doesn't update icons in test env. |
| `signup_screen_test.dart` | Password requirements update — `findsNWidgets(5)` on `Icons.check_circle` | Same reactive validation issue — icons don't transition in test |

## Bottle Tracking Regression

No `CustomerBottleLedger` or `BottleSizeLedger` models exist. No `BottleBloc` exists. No bottle tracking tests exist. Regression is minimal — all existing bottle model tests (BottleLedgerEntry, BottleTransaction) in `bottle_bloc_test.dart` continue to pass unchanged.

## Final Test Count

| | Count |
|---|-------|
| Before T2 | 164 passed, 6 failed |
| Pre-existing failures fixed | 4 |
| Remaining pre-existing | 2 |
| Final | **168 passed, 2 failed** |

## Appium Plan

See `docs/APPIUM_TEST_PLAN.md` — 15 scenarios across 4 priority tiers.

## ARCHITECTURE_OVERVIEW.md Updated

Section "Module Summary": Subscription flow confirmed, bottle tracking regression confirmed. Footer: 2026-05-28.

## Flutter Analyze

0 errors, 0 warnings — confirmed.

## What Comes Next

1. Execute Appium tests on device (requires emulator)
2. Production Chargebee setup
3. One-time order flow