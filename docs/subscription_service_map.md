# Subscription Service Map

> **Purpose:** Cross-reference all subscription-related service classes, BLoC handlers, API endpoints, and Chargebee integration points.

## Architecture

```
┌─────────────────┐       ┌───────────────┐       ┌──────────────────┐
│   Flutter UI    │◀──────│  BLoC Layer   │◀──────│  Service Layer   │
│  (Widgets)      │       │ (user_bloc)   │       │  (subscription   │
└─────────────────┘       └───────────────┘       │   + sync)        │
                           ┌───────────────┐       └────────┬─────────┘
                           │  user_events  │                │
                           │  user_state   │                ▼
                           └───────────────┘       ┌──────────────────┐
                                                   │  bmjServer       │
                                                   │  (Spring Boot)   │
                                                   └────────┬─────────┘
                                                            │
                                                            ▼
                                                   ┌──────────────────┐
                                                   │  Chargebee API   │
                                                   │  (SOT)           │
                                                   └──────────────────┘
```

## Service-to-Endpoint Mapping

### Dart Service: `lib/services/subscription_service.dart`

| Method | API Route | HTTP | BLoC Event | BLoC State |
|--------|-----------|------|------------|------------|
| `fetchPlans()` | `/api/v1/subscriptions/plans` | GET | `LoadPlans` | `PlansLoaded` / `SubscriptionError` |
| `fetchCheckoutUrl(planId)` | `/api/v1/subscriptions/checkout-url` | GET | `CreateCheckoutSession` | `CheckoutUrlReady` / `SubscriptionError` |
| `fetchActiveSubscription()` | `/api/v1/subscriptions/active` | GET | `LoadActiveSubscription` | `ActiveSubscriptionLoaded` / `SubscriptionError` |
| `pauseSubscription(id, reason)` | `/api/v1/subscriptions/{id}/pause` | POST | `PauseSubscription` | `SubscriptionPaused` / `SubscriptionError` |
| `resumeSubscription(id)` | `/api/v1/subscriptions/{id}/resume` | POST | `ResumeSubscription` | `SubscriptionResumed` / `SubscriptionError` |
| `cancelSubscription(id, reason)` | `/api/v1/subscriptions/{id}/cancel` | POST | `CancelSubscription` | `SubscriptionCancelled` / `SubscriptionError` |

### Dart Service: `lib/services/subscription_sync_service.dart`

| Method | API Route | HTTP | Description |
|--------|-----------|------|-------------|
| `syncPlans()` | `/api/v1/subscriptions/plans` | GET | Force refresh All Plans (Cache + DB) |
| `syncActiveSubscription()` | `/api/v1/subscriptions/active` | GET | Force refresh Active Subscription |

### Dart Service: `lib/services/bottle_service.dart`

| Method | API Route | HTTP | Description |
|--------|-----------|------|-------------|
| `getLedger()` | `/api/bottles/ledger` | GET | Get computed bottle ledger |
| `getTransactions()` | `/api/bottles/transactions` | GET | Get bottle transaction history |
| `recordReturn(orderId, bottleType, quantity)` | `/api/bottles/return` | POST | Record bottle return |
| `recordBroken(orderId, bottleType, quantity)` | `/api/bottles/broken` | POST | Report broken/lost bottle |

### BLoC Events (`lib/bloc/UserBloc/user_events.dart`)

```dart
sealed class UserEvent extends Equatable {
  const UserEvent();
  @override List<Object?> get props => [];
}

// Original events
final class LoadUserProfile extends UserEvent {}
final class UpdateUserProfile extends UserEvent {
  final Map<String, dynamic> profile; const UpdateUserProfile(this.profile);
  @override List<Object?> get props => [profile];
}
final class RefreshUserProfile extends UserEvent {}

// Bottle tracking events
final class LoadBottleLedger extends UserEvent {}
final class ReportReturn extends UserEvent {
  final String orderId, bottleType; final int quantity; final String? notes;
  const ReportReturn({required this.orderId, required this.bottleType, required this.quantity, this.notes});
  @override List<Object?> get props => [orderId, bottleType, quantity];
}
final class ReportBroken extends UserEvent {
  final String orderId, bottleType; final int quantity; final String? notes;
  const ReportBroken({required this.orderId, required this.bottleType, required this.quantity, this.notes});
  @override List<Object?> get props => [orderId, bottleType, quantity];
}
```

### BLoC States (`lib/bloc/UserBloc/user_state.dart`)

```dart
sealed class UserState extends Equatable {
  const UserState();
  @override List<Object?> get props => [];
}
final class UserInitial extends UserState {}
final class UserLoading extends UserState {}
final class UserLoaded extends UserState { final User user; const UserLoaded(this.user); @override List<Object?> get props => [user]; }
final class UserError extends UserState { final String message; const UserError(this.message); @override List<Object?> get props => [message]; }

// Bottle tracking states
final class BottleLedgerLoaded extends UserState {
  final List<BottleLedgerEntry> ledger; final List<BottleTransaction> transactions;
  const BottleLedgerLoaded(this.ledger, this.transactions);
  @override List<Object?> get props => [ledger, transactions];
}
final class BottleReportSuccess extends UserState { final String message; const BottleReportSuccess(this.message); @override List<Object?> get props => [message]; }
```

### Java Backend: Controllers

| Controller | Base Path | Authentication |
|------------|-----------|----------------|
| `AuthController` | `/api/auth` | Public (signin/signup/OTP) |
| `AddressController` | `/api/v1/address` | Bearer JWT |
| `CheckoutController` | `/api/v2/checkout` | Bearer JWT |
| `CartController` | `/api/v1/cart` | Bearer JWT |
| `ProductController` | `/api/v1/products` | Public |
| `PlanController` | `/api/v1/subscriptions` | Bearer JWT |
| `OrderController` | `/api/v1/orders` | Bearer JWT |
| `BottleTrackingController` | `/api/bottles` | Bearer JWT (USER/MODERATOR/ADMIN) |

### Java Backend: BottleTrackingController Endpoints

| Method | Endpoint | PreAuthorize | Description |
|--------|----------|--------------|-------------|
| GET | `/api/bottles/ledger` | USER/MODERATOR/ADMIN | Get computed bottle ledger |
| GET | `/api/bottles/transactions` | USER/MODERATOR/ADMIN | Get bottle transaction history |
| POST | `/api/bottles/return` | USER/MODERATOR/ADMIN | Record bottle return |
| POST | `/api/bottles/broken` | USER/MODERATOR/ADMIN | Report broken/lost bottle |

### Java Backend: Webhook Integration

On `INVOICE_PAID` event, `WebhookEventProcessor.processRelatedEntitiesForInvoice()` calls `bottleTrackingService.autoDispatchBottles()` to automatically record bottle issuance. This is best-effort and non-blocking.

## Dependency Map

```
subscription_service.dart → get_it.dart (singleton)
subscription_sync_service.dart → get_it.dart (singleton)
bottle_service.dart → get_it.dart (singleton)
user_bloc.dart → user_events.dart, user_state.dart, subscription_service.dart, bottle_service.dart
```

### Dependency Graph

```
user_bloc.dart
  ├── user_events.dart: LoadUserProfile, UpdateUserProfile, RefreshUserProfile,
  │                     LoadBottleLedger, ReportReturn, ReportBroken
  ├── user_state.dart: UserInitial, UserLoading, UserLoaded, UserError,
  │                    BottleLedgerLoaded, BottleReportSuccess
  ├── subscription_service.dart: fetchPlans, fetchCheckoutUrl, fetchActiveSubscription,
  │                              pauseSubscription, resumeSubscription, cancelSubscription
  └── bottle_service.dart: getLedger, getTransactions, recordReturn, recordBroken
```

## BLoC Event Handler Call Graph

```
LoadUserProfile → subscription_service.fetchActiveSubscription()
   │                 │
   ├─ Success ───── UserLoaded(user)
   └─ Failure ──── UserError(message)

UpdateUserProfile → subscription_service (indirect via API)
   │                 │
   ├─ Success ───── LoadUserProfile (re-fetch)
   └─ Failure ──── UserError(message)

RefreshUserProfile → subscription_service.fetchActiveSubscription()
   │
   ├─ Success ───── UserLoaded(user)
   └─ Failure ──── (retains current state, logs error)

LoadBottleLedger → bottle_service.getLedger() + bottle_service.getTransactions()
   │                 │
   ├─ Success ───── BottleLedgerLoaded(ledger, transactions)
   └─ Failure ──── UserError(message)

ReportReturn → bottle_service.recordReturn()
   │              │
   ├─ Success ─── BottleReportSuccess → LoadBottleLedger (auto-refresh)
   └─ Failure ─── UserError(message)

ReportBroken → bottle_service.recordBroken()
   │               │
   ├─ Success ──── BottleReportSuccess → LoadBottleLedger (auto-refresh)
   └─ Failure ──── UserError(message)
```

## Widget Integration

### Drawer (lib/views/screens/dashboard.dart)

Navigation drawer contains:
- User header card (name, email)
- "PROFILE" section with profile Tile
- "BOTTLES" section with "My Bottles" Tile (Icons.recycling)
- "ACCOUNT" section with logout Tile

### My Bottles Screen (lib/views/widgets/my_bottles_widget.dart)

- `initState` dispatches `LoadBottleLedger`
- `BlocBuilder<UserBloc, UserState>` handles:
  - `UserLoading` → CircularProgressIndicator
  - `BottleLedgerLoaded` → Summary header card + ledger cards + recent transactions
  - `UserError` → Error text + Retry button
  - Empty state → "No Bottles Yet" with recycling icon
- Pull-to-refresh via `RefreshIndicator`

### Screens

| Screen | Route | File |
|--------|-------|------|
| Plan Catalog | `/plans` | `plan_catalog_screen.dart` |
| Subscription Detail | `/subscription` | `subscription_detail_screen.dart` |
| Address | `/address` | `address_screen.dart` |
| Cart | `/cart` | `cart_screen.dart` |
| Checkout | `/checkout` | `checkout_screen.dart` |
| Order History | `/orders` | `order_screen.dart` |
| Dashboard (Drawer) | `/dashboard` | `dashboard.dart` |
| My Bottles | (drawer tile) | `my_bottles_widget.dart` |

## DI Registration (get_it.dart)

```dart
void registerServices() {
  getIt.registerLazySingleton<SubscriptionService>(() => SubscriptionService());
  getIt.registerLazySingleton<SubscriptionSyncService>(() => SubscriptionSyncService());
  getIt.registerLazySingleton<BottleService>(() => BottleService());
  // ...
}
```

## Integration Points

### Chargebee Webhook → Bottle Auto-Dispatch

```
INVOICE_PAID webhook → WebhookEventProcessor
  → processRelatedEntitiesForInvoice()
    → build line items JSON from invoice.lineItems()
    → bottleTrackingService.autoDispatchBottles(invoiceId, customerId, itemsJson)
      → recordIssue() creates bottle_transactions entry
```

---

## IMPLEMENTED BUT UNDOCUMENTED

| Method | Endpoint | Notes |
|--------|----------|-------|
| `getMySubscriptions` | `GET /api/subscriptions/my` | Discovered during D7 preparation. Present in `subscription_service.dart` (v1). Returns all subscriptions for the authenticated user. Token is read internally via `SecureStorageService`. Now documented in `docs/API.md`. |

---

## Summary of Flags

| Flag | Count | Details |
|------|-------|---------|
| **CONTRADICTION** | 6 | HTTP verb/body mismatch (3), endpoint path mismatch (3), versioning statement vs implementation, price unit ambiguity |
| **PHANTOM DOC** | 5 | `/api/v1/subscriptions/checkout-url`, `POST /api/v1/subscribe`, `POST /api/v1/subscribe/direct`, `GET /api/subscriptions/pricing-page` (backend method exists but no controller route), API request body fields backend doesn't accept |
| **DUPLICATE** | 2 | v1 + v2 service files implement identical endpoints (86% of v2 is dead weight), subscription endpoint lists duplicated across API.md and NATIVE_BILLING_FLOW.md |
| **DEAD CODE** | 7 | v2 methods unused: `getSubscription`, `createSubscription`, `pauseSubscription`, `resumeSubscription`, `cancelSubscription`, `getAllPlans`, `getPricingPageUrl` |
| **NOT TESTED** | 6 | All 6 wired subscription methods lack integration/Appium test coverage for actual API calls |
| **🔴 STUB** | 2 | **ProductsBloc** (BEM-007): all 6 handlers use `Future.delayed()` + mock data, network check commented out. **SubscriptionBloc** (BEM-006): all 7 handlers use `Future.delayed()` + mock/static data, no real API calls. |

---

*Generated from analysis of Dart service files, Java backend controllers, BLoC event handlers, and documentation comparison.*
