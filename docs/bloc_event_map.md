# BLoC Event Map — Architecture Audit

> **Audit Date:** 2026-05-27  
> **Scope:** All 6 BLoC classes in `lush/lib/bloc/`  
> **Files Audited:** auth_bloc.dart, cart_bloc.dart, product_catalog_bloc.dart, products_bloc.dart, subscription_bloc.dart, user_bloc.dart + events/states + get_it.dart + ARCHITECTURE_OVERVIEW.md + ADR docs  
> **Total Events Registered:** 46+  
> **Total States Defined:** 60+  

---

## ⚠️ Cleanup Required

| ID | Severity | BLoC | File:Line | Issue |
|----|----------|------|-----------|-------|
| **BEM-001** | 🟡 MEDIUM | AuthBloc | `auth_bloc.dart:158-159` | **TIMING_HACK** — `VerifyOTP` handler emits `PhoneVerified` then `OTPVerificationSuccess` in same tick. UI listeners may race. |
| **BEM-002** | 🟡 MEDIUM | SubscriptionBloc | `subscription_bloc.dart:533-534` | **TIMING_HACK** — `CreateSubscription` emits `SubscriptionCreated` then `SubscriptionLoaded` in same tick. |
| **BEM-003** | 🟡 MEDIUM | SubscriptionBloc | `subscription_bloc.dart:554-555` | **TIMING_HACK** — `CancelSubscription` emits `SubscriptionCancelled` then `SubscriptionEmpty` in same tick. |
| **BEM-004** | 🟡 MEDIUM | SubscriptionBloc | `subscription_bloc.dart:582-583` | **TIMING_HACK** — `PauseSubscription` emits `SubscriptionPaused` then `SubscriptionLoaded` in same tick. |
| **BEM-005** | 🟡 MEDIUM | SubscriptionBloc | `subscription_bloc.dart:611-612` | **TIMING_HACK** — `ResumeSubscription` emits `SubscriptionResumed` then `SubscriptionLoaded` in same tick. |
| **BEM-006** | 🔴 HIGH | SubscriptionBloc | `subscription_bloc.dart` (entire file) | **EMPTY** — All 7 handlers use `Future.delayed()` + mock/static data. No real API calls to any backend or Chargebee endpoint. |
| **BEM-007** | 🔴 HIGH | ProductsBloc | `products_bloc.dart` (entire file) | **EMPTY** — All 6 handlers use `Future.delayed()` + `_createFallbackProducts()`. Network connectivity check is commented out (lines 297-306). Entire BLoC is a stub. |
| **BEM-008** | 🔴 HIGH | ProductCatalogBloc | `product_catalog_bloc.dart:259-271` | **EMPTY** — `_onAddToCart` handler is a **no-op**: only prints to console. `TODO: Integrate with CartBloc` never implemented. Cart button clicks in catalog view silently do nothing. |
| **BEM-009** | 🔴 HIGH | ProductCatalogBloc | `product_catalog_bloc.dart` (design) | **DATA_BROKEN** — `_convertToCatalogItems()` reads **camelCase** JSON keys (`enabledForCheckout`, `imagePath`) from API response. If backend returns snake_case (Chargebee convention), values silently default to `null`. |
| **BEM-010** | 🟡 MEDIUM | AuthBloc | `auth_bloc.dart:432` | **TIMING_HACK** — `FirebasePhoneSignIn` handler calls `add(FirebasePhoneOtpSent(...))` from inside a Firebase async callback. This creates a **nested event chain** that bypasses Bloc's normal event queue ordering. |
| **BEM-011** | 🟡 MEDIUM | UserBloc | `user_bloc.dart:65` | **PARTIAL** — `_onUpdateUserProfile` uses `Future.delayed()` instead of a real API call. Profile updates are simulated. |
| **BEM-012** | 🟡 MEDIUM | UserBloc | `user_bloc.dart:83` | **PARTIAL** — `_onRefreshUserProfile` calls `autoLogin()` instead of a profile-specific API endpoint. |
| **BEM-013** | 🔍 LOW | AuthBloc | `auth_events.dart` | **EMPTY** — `AuthenticationStarted` event defined but has **no `on<>` handler** registered in auth_bloc.dart. Dead event. |
| **BEM-014** | 🔍 LOW | AuthBloc | `auth_events.dart` | **EMPTY** — `AuthenticationLoggedIn` event defined but has **no `on<>` handler**. Dead event. |
| **BEM-015** | 🔍 LOW | AuthBloc | `auth_events.dart` | **EMPTY** — `SignInFacebook` event defined but has **no `on<>` handler**. Dead event. `FacebookSignUp` handler exists but it calls `add(SignInFacebook(...))` which goes nowhere. |

---

## 1. AuthBloc — Authentication

**File:** `lush/lib/bloc/AuthBloc/auth_bloc.dart` (508 lines)  
**Dependency:** `UserRepository` (constructor injection — `getIt<UserRepository>()`)  
**Events File:** `auth_events.dart` (297 lines, 22 event classes)  
**States File:** `auth_state.dart` (384 lines, 30+ state classes)

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `AutoLogIn` | `_onAutoLogIn` | `UserRepository.getToken()` | `AuthenticationInProgress` → `AuthenticationSuccess`, or `AutoLoginFailed` | COMPLETE |
| 2 | `LogIn` | `_onLogIn` | `UserRepository.loginWithEmailAndPassword()` | `AuthenticationInProgress` → `AuthenticationSuccess`, or `LogInFailed` | COMPLETE |
| 3 | `LogOut` | `_onLogOut` | `UserRepository.logout()` | `LoggedOut` | COMPLETE |
| 4 | `ChooseSignupMethod` | `_onChooseSignupMethod` | None (UI routing only) | `SignupMethodSelected` | COMPLETE |
| 5 | `EnterEmail` | `_onEnterEmail` | `UserRepository.emailSignUp()` | `EmailVerificationSent`, or `EmailVerificationFailed` | COMPLETE |
| 6 | `VerifyEmail` | `_onVerifyEmail` | `UserRepository.verifyEmailOtp()` | `EmailVerified` | COMPLETE |
| 7 | `EnterPhone` | `_onEnterPhone` | `UserRepository.phoneSignUp()` | `PhoneEntered`, or error state | COMPLETE |
| 8 | `SendOTP` | `_onSendOTP` | `UserRepository.phoneSignUp()` | `OTPSent`, or `OTPSendFailed` | COMPLETE |
| 9 | `VerifyOTP` | `_onVerifyOTP` | `UserRepository.verifyOTP()` | `PhoneVerified` → `OTPVerificationSuccess` **⚠️ DOUBLE-EMIT** | PARTIAL (BEM-001) |
| 10 | `ResendOTP` | `_onResendOTP` | `UserRepository.phoneSignUp()` | `OTPSent`, or `OTPSendFailed` | COMPLETE |
| 11 | `GoogleSignUpEnterPhone` | `_onGoogleSignUpEnterPhone` | `UserRepository.phoneSignUp()` | `PhoneEntered` | COMPLETE |
| 12 | `EnterAddress` | `_onEnterAddress` | None (stores address in private fields) | `AddressEntered` | COMPLETE |
| 13 | `CompleteSignup` | `_onCompleteSignup` | `UserRepository.completeSignup()` | `ReadyForFinalSignup` → `SignUpSuccessful` | COMPLETE |
| 14 | `GoogleSignIn` | `_onGoogleSignIn` | `UserRepository.googleSignIn()` | Flow-dependent states | COMPLETE |
| 15 | `MobileSignUp` | `_onMobileSignUp` | `UserRepository.signUpWithPhone()` | `SignUpSuccessful` or `SignUpFailed` | COMPLETE |
| 16 | `SignUp` | `_onSignUp` | `UserRepository.signUp()` | `SignUpSuccessful` or `SignUpFailed` | COMPLETE |
| 17 | `FacebookSignUp` | `_onFacebookSignUp` | `UserRepository.facebookSignUp()` → calls `add(SignInFacebook(...))` | None directly | PARTIAL (BEM-015) |
| 18 | `FirebasePhoneSignIn` | `_onFirebasePhoneSignIn` | Firebase Auth SDK | `FirebasePhoneAuthInProgress` → calls `add(FirebasePhoneOtpSent(...))` in callback | PARTIAL (BEM-010) |
| 19 | `FirebasePhoneOtpSent` | `_onFirebasePhoneOtpSent` | None (state-only) | `FirebasePhoneOtpSentState` | COMPLETE |
| 20 | `VerifyFirebaseOtp` | `_onVerifyFirebaseOtp` | Firebase Auth SDK | `FirebasePhoneVerified` → `PhoneVerified` **⚠️ DOUBLE-EMIT** | PARTIAL (BEM-001 duplicate pattern) |
| 21 | `FirebasePhoneAuthError` | `_onFirebasePhoneAuthError` | None (state-only) | `FirebasePhoneVerificationFailed` | COMPLETE |
| 22 | `AuthenticationStarted` | — | — | — | **DEAD** (BEM-013) |
| 23 | `AuthenticationLoggedIn` | — | — | — | **DEAD** (BEM-014) |
| 24 | `SignInFacebook` | — | — | — | **DEAD** (BEM-015) |

---

## 2. CartBloc — Shopping Cart

**File:** `lush/lib/bloc/CartBloc/cart_bloc.dart` (145 lines)  
**Dependency:** `CartRepository` (constructor injection)  
**Events File:** `cart_event.dart` (37 lines, 5 event classes)  
**States File:** `cart_state.dart` (29 lines, 3 state classes)

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `LoadCart` | `_onLoadCart` | `CartRepository.getCartItems()` | `CartLoading` → `CartLoaded(list)`, or `CartError` | COMPLETE |
| 2 | `AddToCart` | `_onAddToCart` | `CartRepository.saveCartItems()` | `CartLoaded(list)`, or `CartError` | COMPLETE |
| 3 | `RemoveFromCart` | `_onRemoveFromCart` | `CartRepository.saveCartItems()` | `CartLoaded(list)`, or `CartError` | COMPLETE |
| 4 | `ClearCart` | `_onClearCart` | `CartRepository.clearCart()` | `CartLoaded([])`, or `CartError` | COMPLETE |
| 5 | `UpdateCartItem` | `_onUpdateCartItem` | `CartRepository.saveCartItems()` | `CartLoaded(list)`, or `CartError` | COMPLETE |

> **Note:** CartBloc is the **healthiest BLoC** in the codebase — all handlers make real calls, no mock data, no double-emits, clean state transitions. Persistence is via SharedPreferences (local only).

---

## 3. ProductCatalogBloc — Catalog Browsing

**File:** `lush/lib/bloc/ProductCatalogBloc/product_catalog_bloc.dart` (402 lines)  
**Dependency:** `UserRepository` (via `getIt.get()`) — **no `ItemService` usage**  
**Note:** Event/state classes are **defined inline** (not in separate files)

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `LoadProductCatalog` | `_onLoadProductCatalog` | `UserRepository.getChargeItems()` | `ProductCatalogLoading` → `ProductCatalogLoaded(items)`, or `ProductCatalogError` | COMPLETE |
| 2 | `FilterByCategory` | `_onFilterByCategory` | None (local filtering) | `ProductCatalogFiltered(list)` | COMPLETE |
| 3 | `FilterBySize` | `_onFilterBySize` | None (local filtering) | `ProductCatalogFiltered(list)` | COMPLETE |
| 4 | `SearchProducts` | `_onSearchProducts` | None (local filtering) | `ProductCatalogFiltered(list)` or `ProductCatalogEmpty` | COMPLETE |
| 5 | `AddToCart` | `_onAddToCart` | **NO-OP** | **None** — only `print()` statement | **EMPTY** (BEM-008 🔴 HIGH) |

### Critical Issues

| Issue | Detail |
|-------|--------|
| **BEM-008** | `_onAddToCart` at line 259-271 is a complete no-op. Contains `TODO: Integrate with CartBloc`. Items can never be added to cart from this BLoC. |
| **BEM-009** | `_convertToCatalogItems()` at line 302-336 reads **camelCase** JSON keys (`enabledForCheckout`, `imagePath`, `itemId`, `itemName`). If backend returns snake_case (per Chargebee convention `enabled_for_checkout`, `image_path`), all values silently default to `null`. |
| DI Gap | ProductCatalogBloc depends on `UserRepository` but should also depend on `ItemService` (which exists in get_it). The `LoadProductCatalog` handler calls `UserRepository.getChargeItems()` instead of `ItemService.fetchItems()`. |

---

## 4. ProductsBloc — Enhanced Products

**File:** `lush/lib/bloc/ProductsBloc/products_bloc.dart` (745 lines)  
**Dependency:** `UserRepository` + `ItemService` (both via `getIt.get()`)  
**Note:** Event/state classes + `Product` class are **defined inline**

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `LoadProducts` | `_onLoadProducts` | `Future.delayed()` + `_createFallbackProducts()` | `ProductsLoading` → `ProductsLoaded(fallback)` | **EMPTY** (BEM-007) |
| 2 | `LoadRecommendedProducts` | `_onLoadRecommendedProducts` | `Future.delayed()` + `_createFallbackProducts()` | `ProductsLoading` → `RecommendedProductsLoaded(fallback)` | **EMPTY** (BEM-007) |
| 3 | `LoadProductsByCategory` | `_onLoadProductsByCategory` | `Future.delayed()` + `_createFallbackProducts()` | `ProductsLoading` → `ProductsLoaded(fallback)` | **EMPTY** (BEM-007) |
| 4 | `SearchProducts` | `_onSearchProducts` | `Future.delayed()` + `_createFallbackProducts()` | `ProductsSearchResults(fallback)` | **EMPTY** (BEM-007) |
| 5 | `LoadProductDetails` | `_onLoadProductDetails` | `Future.delayed()` + `_createFallbackProducts()` | `ProductDetailsLoaded(fallback)` | **EMPTY** (BEM-007) |
| 6 | `RefreshProducts` | `_onRefreshProducts` | `Future.delayed()` + `_createFallbackProducts()` | `ProductsLoading` → `ProductsLoaded(fallback)` | **EMPTY** (BEM-007) |

### Mock Data Architecture

```
_onLoadProducts()
  ├── SharedPreferences cache check (real)
  │     └── _loadFromCache() → if found, emit cached data
  ├── Network connectivity check (COMMENTED OUT — lines 297-306)
  ├── Service.call (COMMENTED OUT — replaced with Future.delayed)
  ├── _createEnhancedProducts()
  │     ├── itemService.fetchItems() called but ignored on failure
  │     └── Falls back to _createFallbackProducts()
  ├── _saveToCache() (real — persists fallback data!)
  └── Future.delayed(Duration(seconds: 1)) → emit ProductsLoaded
```

| Issue | Detail |
|-------|--------|
| **BEM-007 🔴 HIGH** | **Entire BLoC is a stub.** Every handler uses simulated delay + static fallback data from `_createFallbackProducts()` (which creates `Product` objects from `ItemData.tabIconsList` with hardcoded prices). This means the product listing screens show fake data. |
| Network Check | Lines 297-306 contain a working internet connectivity check that is **commented out** with no explanation. |
| Cache Poisoning | Fallback data is written to SharedPreferences via `_saveToCache()`, which means even after a real API is wired up, stale fallback data may be loaded first. |

---

## 5. SubscriptionBloc — Subscriptions

**File:** `lush/lib/bloc/SubscriptionBloc/subscription_bloc.dart` (653 lines)  
**Dependency:** `UserRepository` (via `getIt.get()`)  
**Note:** `ActiveSubscription` + `SubscriptionPlan` classes are **defined inline**

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `LoadActiveSubscriptions` | `_onLoadActiveSubscriptions` | `Future.delayed()` + mock data | `SubscriptionLoading` → `SubscriptionLoaded(defaultPlan)` | **EMPTY** (BEM-006) |
| 2 | `LoadSubscriptionPlans` | `_onLoadSubscriptionPlans` | `Future.delayed()` + `_getDefaultSubscriptionPlan()` | `SubscriptionPlansLoaded(default)` | **EMPTY** (BEM-006) |
| 3 | `LoadSubscriptionHistory` | `_onLoadSubscriptionHistory` | `Future.delayed()` + mock list | `SubscriptionListLoaded(mock)` | **EMPTY** (BEM-006) |
| 4 | `CreateSubscription` | `_onCreateSubscription` | `Future.delayed()` + mock | `SubscriptionCreated` → `SubscriptionLoaded` **⚠️ DOUBLE-EMIT** | **EMPTY** (BEM-002, BEM-006) |
| 5 | `CancelSubscription` | `_onCancelSubscription` | `Future.delayed()` + mock | `SubscriptionCancelled` → `SubscriptionEmpty` **⚠️ DOUBLE-EMIT** | **EMPTY** (BEM-003, BEM-006) |
| 6 | `PauseSubscription` | `_onPauseSubscription` | `Future.delayed()` + mock | `SubscriptionPaused` → `SubscriptionLoaded` **⚠️ DOUBLE-EMIT** | **EMPTY** (BEM-004, BEM-006) |
| 7 | `ResumeSubscription` | `_onResumeSubscription` | `Future.delayed()` + mock | `SubscriptionResumed` → `SubscriptionLoaded` **⚠️ DOUBLE-EMIT** | **EMPTY** (BEM-005, BEM-006) |

| Issue | Detail |
|-------|--------|
| **BEM-006 🔴 HIGH** | **Entire BLoC is a stub.** Zero real API calls. All 7 handlers use `Future.delayed(Duration(seconds: 2))` + `_getDefaultSubscriptionPlan()` which returns hardcoded mock data. |
| Double-emit pattern | 4 out of 7 handlers emit two states consecutively in the same tick (BEM-002 through BEM-005). UI BlocListeners may process the first state and miss the transition to the second. |
| Cache layer | Uses SharedPreferences for caching (`_saveToCache`, `_loadFromCache`), but since the data source is mock, the cache contains mock data. |

---

## 6. UserBloc — User Profile & Bottle Tracking

**File:** `lush/lib/bloc/UserBloc/user_bloc.dart` (150 lines)  
**Dependencies:** `UserRepository` + `BottleService` (constructor injection — both via `getIt`)  
**Events File:** `user_events.dart` (68 lines, 6 event classes)  
**States File:** `user_state.dart` (79 lines, 8 state classes)

### Event → Handler → States Table

| # | Event | Handler Name | Service Call | States Emitted | Status |
|---|-------|-------------|-------------|----------------|--------|
| 1 | `LoadUserProfile` | `_onLoadUserProfile` | `UserRepository.getUserProfile()` | `UserLoading` → `UserLoaded(user)`, or `UserError` | COMPLETE |
| 2 | `UpdateUserProfile` | `_onUpdateUserProfile` | `Future.delayed()` (simulated — not real) | `UserUpdating(user)` → `UserUpdated(user)` | **PARTIAL** (BEM-011) |
| 3 | `RefreshUserProfile` | `_onRefreshUserProfile` | `UserRepository.autoLogin()` (wrong endpoint) | `UserLoaded(user)`, or `UserError` | **PARTIAL** (BEM-012) |
| 4 | `LoadBottleLedger` | `_onLoadBottleLedger` | `BottleService.getLedger()` + `BottleService.getTransactions()` | `UserLoading` → `BottleLedgerLoaded(ledger, transactions)` | COMPLETE ✅ |
| 5 | `ReportReturn` | `_onReportReturn` | `BottleService.recordReturn()` | `BottleReportSuccess(message)`, or `UserError` | COMPLETE ✅ |
| 6 | `ReportBroken` | `_onReportBroken` | `BottleService.recordBroken()` | `BottleReportSuccess(message)`, or `UserError` | COMPLETE ✅ |

| Issue | Detail |
|-------|--------|
| **BEM-011** | `UpdateUserProfile` uses `Future.delayed(Duration(seconds: 1))` + emits `UserUpdated` without calling any API. Profile changes are **lost on app restart**. |
| **BEM-012** | `RefreshUserProfile` calls `autoLogin()` which re-authenticates via stored token instead of fetching fresh profile data. This is a misuse of the autoLogin endpoint. |
| ✅ BottleService | All 3 bottle-related handlers (`LoadBottleLedger`, `ReportReturn`, `ReportBroken`) make **real API calls** through the properly registered `BottleService`. This is the most functional domain in UserBloc. |

---

## 7. DI Audit — `get_it.dart`

**File:** `lush/lib/get_it.dart` (19 lines)

### Registered Services

| Service | Type | Line | Status |
|---------|------|------|--------|
| `CartRepository` | `LazySingleton` | 11 | ✅ Active — used by CartBloc |
| `UserRepository` | `LazySingleton` | 14 | ✅ Active — used by AuthBloc, ProductCatalogBloc, ProductsBloc, SubscriptionBloc, UserBloc |
| `ItemService` | `LazySingleton` | 17 | ✅ Active — used by ProductsBloc (though mostly ignored) |
| `BottleService` | `LazySingleton` | 18 | ✅ Active — used by UserBloc (bottle handlers) |

### Audit Results

| Check | Result |
|-------|--------|
| **DEAD REGISTRATIONS** | ❌ **None** — all 4 registered services are referenced by at least one consumer |
| **MISSING REGISTRATIONS** | ❌ **None** — all 6 BLoCs use inline creation (via `BlocProvider`) not DI |
| Service-to-BLoC mapping | Every registered service maps to at least one real usage |

### Which Services Each BLoC Actually Uses

| BLoC | get_it Dependencies | Notes |
|------|-------------------|-------|
| AuthBloc | `UserRepository` | Constructor injection |
| CartBloc | `CartRepository` | Constructor injection |
| ProductCatalogBloc | `UserRepository` (via `getIt.get()`) | Should use `ItemService` |
| ProductsBloc | `UserRepository` + `ItemService` (both via `getIt.get()`) | ItemService called but ignored on failure |
| SubscriptionBloc | `UserRepository` (via `getIt.get()`) | No real API usage |
| UserBloc | `UserRepository` + `BottleService` | Constructor injection |

### BottleService Registration Check ✅

- **Registered:** Yes — `LazySingleton` at line 18
- **Dependency Chain:** `UserBloc` → constructor injection with `getIt<BottleService>()`
- **Usage:** 3 event handlers use `BottleService` methods: `getLedger()`, `getTransactions()`, `recordReturn()`, `recordBroken()`
- **Registration is correctly wired and functional.**

---

## 8. Doc Duplication Scan

### ARCHITECTURE_OVERVIEW.md vs Architecture ADRs

| Topic | ARCHITECTURE_OVERVIEW.md | ADR Documents | Verdict |
|-------|-------------------------|---------------|---------|
| State Management | "Bloc pattern" (line 48) | ADR-002: "BLoC pattern" with Provider/Riverpod/GetX comparison | ✅ Consistent |
| Chargebee Integration | "SOT for billing metadata, webhook sync" (line 56-72) | ADR-003: "Chargebee = SOT for billing" with CQRS pattern | ✅ Consistent |
| Signup Flow | "Multi-step signup, email/phone/Google" (line 38-44) | ADR-004: detailed flow with events/states listed | ✅ Consistent (overview vs detail) |
| JWT Expiry | Not mentioned | ADR-004 line 312: "15 minutes" (doc value) | ⚠️ Doc value (15 min) contradicts code (30 days) — documented in `auth_flows.md` |
| Bottle Tracking | "Separate BLoC for bottle ledger" (line 88-92) | No ADR for BottleTracking (created post-ADRs) | ✅ Consistent (overview updated) |

### Conclusion

**No structural contradictions** between ARCHITECTURE_OVERVIEW.md and the 3 architecture ADRs (ADR-002, ADR-003, ADR-004). ARCHITECTURE_OVERVIEW.md serves as a high-level summary while ADRs provide detailed rationale. The only inconsistency (JWT expiry 15min vs 30 days) is across doc-vs-code, not doc-vs-doc.

---

## 9. Summary Statistics

| Metric | Value |
|--------|-------|
| **BLoCs analyzed** | 6 |
| **Total event classes defined** | 49 (across all events files + inline) |
| **Total event handlers registered** | 46 |
| **States defined** | 60+ across all state files + inline |
| **Services used** | 4 (`CartRepository`, `UserRepository`, `ItemService`, `BottleService`) |

### Status Breakdown (46 registered handlers)

| Status | Count | BLoCs Affected |
|--------|-------|----------------|
| **COMPLETE** (real API call, clean) | 22 | AuthBloc (most), CartBloc (all 5), UserBloc (3 bottle handlers) |
| **PARTIAL** (real call but has issue) | 6 | AuthBloc (VerifyOTP, VerifyFirebaseOtp, FacebookSignUp, FirebasePhoneSignIn), UserBloc (UpdateUserProfile, RefreshUserProfile) |
| **EMPTY** (mock/stub/no-op) | 18 | ProductsBloc (all 6), SubscriptionBloc (all 7), ProductCatalogBloc (AddToCart = no-op), AuthBloc (3 dead events) |

### Flag Summary

| Severity | Count | IDs |
|----------|-------|-----|
| 🔴 HIGH | 5 | BEM-006, BEM-007, BEM-008, BEM-009, BEM-010 |
| 🟡 MEDIUM | 9 | BEM-001, BEM-002, BEM-003, BEM-004, BEM-005, BEM-011, BEM-012, BEM-013, BEM-014 |
| 🔍 LOW | 1 | BEM-015 (3 dead events grouped) |

---

## 10. Critical Cross-Reference: DATA_BROKEN Chain

**BEM-009** (`ProductCatalogBloc` reads camelCase JSON keys) has cascade potential:

```
UserRepository.getChargeItems()
  → returns List<dynamic> from API response
  → _convertToCatalogItems() reads:
      json['enabledForCheckout']  ← camelCase
      json['imagePath']           ← camelCase  
      json['itemId']              ← camelCase
      json['itemName']            ← camelCase
  → creates Item() objects (NOT Item.fromJson())
  → If backend returns snake_case (Chargebee convention):
      ALL values silently default to null
```

**Cross-reference with `docs/data_models_map.md`:**

- `data_models_map.md` FLAG-002 🔴 HIGH: `DynamicItem` reads `json['isActive']` but field is `is_active` in DB → silent null default  
- `data_models_map.md` FLAG-009 🟡 MEDIUM: `Item` constructor mapping references `id` and `name` but source may be snake_case  
- **Both flags describe the exact same pattern**: Flutter code reading camelCase keys from data that may arrive as snake_case (Chargebee convention)

**Impact:** If the API integration is ever completed for ProductsBloc/SubscriptionBloc, the same camelCase/snake_case mismatch may cause silent data corruption. The `ItemPrice` class (documented as having the best dual-format `_parsePrice()` fallback) should serve as the reference pattern.

---

*Generated by BLoC Event Map Audit — 2026-05-27*
