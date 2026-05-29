# BMJ E2E Bug Tracker
**Run Date:** 2026-05-29  
**Device:** `1f3431ad` (Android physical device)  
**bmjServer:** Running at `http://10.106.30.106:8080`  
**Total:** 10 passed / 2 failed / 0 skipped

## ✅ Passing Tests
| # | Test Name | Suite |
|---|-----------|-------|
| 1 | TC-E2E-001: App launches successfully | Smoke |
| 2 | TC-E2E-002: Splash screen displays correctly | Smoke |
| 3 | TC-E2E-004: Login screen has email and password fields | Auth |
| 4 | TC-E2E-005: Login button is present | Auth |
| 5 | TC-E2E-007: Product catalog renders juice items | Catalog |
| 6 | TC-E2E-008: Product search bar exists | Catalog |
| 7 | TC-E2E-009: Category/size filter chips are interactive | Catalog |
| 8 | TC-E2E-010: Product detail bottom sheet shows size options | Catalog |
| 9 | TC-E2E-011: Size options display works | Catalog |
| 10 | TC-E2E-012: Navigation flow works | Smoke |

## 🔴 Bugs Found
| Bug ID | Test | Error Message | Suspected Cause | Priority |
|--------|------|---------------|-----------------|----------|
| BUG-001 | TC-E2E-003 | `ProviderNotFoundException: Could not find the correct Provider<OrderBloc>` | Dashboard `initState` calls `context.read<OrderBloc>()` but `OrderBloc` is not registered in `main.dart`'s `MultiBlocProvider` | **P0** |
| BUG-002 | TC-E2E-006 | `ProviderNotFoundException: Could not find the correct Provider<OrderBloc>` (same cascade) | Same root cause — Dashboard crashes before test interactions can proceed | **P0** |

## 📋 Bug Details

### BUG-001 — Provider<OrderBloc> not registered
**Error:**
```
ProviderNotFoundException: Could not find the correct Provider<OrderBloc> above this Dashboard Widget
HomePage2State.initState (package:lush/views/screens/dashboard.dart:55:13)
```
**Stack trace (first 5 lines):**
```
#0 Provider._inheritedElementOf (package:provider/src/provider.dart:377:7)
#1 Provider.of (package:provider/src/provider.dart:327:30)
#2 ReadContext.read (package:provider/src/provider.dart:683:21)
#3 HomePage2State.initState (package:lush/views/screens/dashboard.dart:55:13)
#4 StatefulElement._firstBuild (package:flutter/src/widgets/framework.dart:5950:55)
```
**Suspected cause:** `dashboard.dart` initState line 55 dispatches `context.read<OrderBloc>().add(const LoadOrderHistory())` but `OrderBloc` is not provided anywhere in the widget tree. It's only used locally inside `OrderHistoryScreen` which creates its own `OrderBloc` internally. The `context.read<OrderBloc>()` throws because no ancestor `BlocProvider<OrderBloc>` exists.

**File to fix:** `lush/lib/views/screens/dashboard.dart` line 55

**Fix needed:** Remove `context.read<OrderBloc>().add(const LoadOrderHistory())` from initState, OR add `BlocProvider<OrderBloc>` to main.dart's MultiBlocProvider

### BUG-002 — Cascade from BUG-001
**Error:** Same `ProviderNotFoundException` — occurs on every test that navigates to a screen containing Dashboard after the first build. Since Dashboard crashes on mount, all subsequent tests fail when they try to interact with any widget.

**Suspected cause:** Direct consequence of BUG-001. The `OrderHistoryScreen` tab in the `IndexedStack` also contributes: when `OrderHistoryScreen` is constructed, its own `initState` creates an `OrderBloc` internally, but the dashboard's direct `context.read<OrderBloc>()` call occurs before that, during the State's own initState.

**File to fix:** `lush/lib/views/screens/dashboard.dart` (same as BUG-001)

**Fix needed:** Remove the `context.read<OrderBloc>()` call from dashboard initState since OrderBloc is not a globally provided dependency.

## 📊 Summary by Suite
| Suite | Passed | Failed |
|-------|--------|--------|
| Smoke (app launch, splash, nav) | 3 | 0 |
| Auth (login screen fields) | 2 | 0 |
| Catalog (product display, search, filters, detail) | 5 | 0 |
| Data-dependent (dashboard load, order fetch) | 0 | 2 |
| **Total** | **10** | **2** |