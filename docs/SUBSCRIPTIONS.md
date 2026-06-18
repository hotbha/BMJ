# Subscription System

> **Purpose:** Complete subscription system reference — screen flow specification, service/BLoC/backend mapping, and Chargebee integration for BookMyJuice.

> **Catalog structure:** Item (family + size or family + juice + size) + Item Prices (weekly + monthly)

---

## PART 1: SUBSCRIPTION SCREEN FLOW

### Screen 1 — Family Selection

3 cards: Delight, Signature, Premium
- Each card: emoji, name, tagline, description
- Source: metadata from items of that family
- Tap → Screen 2 filtered to that family

### Screen 2 — Plan Selection

#### Section A: "Choose a Plan" (generic items for selected family)
- 3 cards — one per size: 200ml | 300ml | 500ml
- Each card shows BOTH prices:
  - Weekly: ₹[price] (6 bottles)
  - Monthly: ₹[price] (24 bottles)
- Duration toggle on card: Weekly | Monthly
- Tap card → Screen 3 (day-wise, all days empty)
- Carries: selected itemId + selected itemPriceId

#### Section B: "Start with a Favourite"
- Grid of 5 juice cards for this family
- Each juice card: name, weekly price for 200ml
- Tap juice → size selector (200ml | 300ml | 500ml)
  - Each size option shows weekly + monthly price
  - Customer picks size + duration
- → Screen 3 (day-wise, all days pre-filled)
- Carries: selected itemId + selected itemPriceId

### Screen 3 — Day-wise Juice Selection

- Header: shows selected plan name + size + price
- Checkbox top: "Same Everyday" (default: ON)
  - ON → changing one day updates all 6 days
  - OFF → each day independent
- 6 rows: Mon | Tue | Wed | Thu | Fri | Sat (Sunday excluded)
- Each row: day label + juice dropdown
- Dropdown: juices of selected family only

For juice_specific entry:
- All 6 rows pre-filled with default_juice
- "Same Everyday" checked ON

For generic entry:
- All 6 rows empty
- "Same Everyday" checked ON
- All 6 rows must be filled to enable CTA

CTA: "Review Order" (disabled until all days filled)
→ Screen 4

### Screen 4 — Summary + Checkout

- Plan: [Family] [Size] [Weekly/Monthly]
- Price: ₹[amount] per [week/month]
- Schedule: Mon–Sat with juice names
- Delivery address (from profile)
- CTA: "Start Subscription" → Chargebee checkout
- Carries: itemPriceId + day-wise juice metadata

### Data Model — SubscriptionSelection

```dart
class SubscriptionSelection {
  final String itemId;
  final String itemPriceId;  // weekly or monthly price
  final String family;
  final String size;
  final String period;       // 'weekly' | 'monthly'
  final int priceInPaise;
  final Map<String, String> daySchedule;
  final String? defaultJuice;

  Map<String, dynamic> toChargebeeMetadata() => {
    'item_id': itemId,
    'item_price_id': itemPriceId,
    'period': period,
    'day_schedule': daySchedule,
    'default_juice': defaultJuice,
  };
}
```

---

## PART 2: SERVICE & BACKEND MAPPING

### Architecture

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

### Service-to-Endpoint Mapping

#### Dart Service: `lib/services/subscription_service.dart`

| Method | API Route | HTTP | BLoC Event | BLoC State |
|--------|-----------|------|------------|------------|
| `fetchPlans()` | `/api/v1/subscriptions/plans` | GET | `LoadPlans` | `PlansLoaded` / `SubscriptionError` |
| `fetchCheckoutUrl(planId)` | `/api/v1/subscriptions/checkout-url` | GET | `CreateCheckoutSession` | `CheckoutUrlReady` / `SubscriptionError` |
| `fetchActiveSubscription()` | `/api/v1/subscriptions/active` | GET | `LoadActiveSubscription` | `ActiveSubscriptionLoaded` / `SubscriptionError` |
| `pauseSubscription(id, reason)` | `/api/v1/subscriptions/{id}/pause` | POST | `PauseSubscription` | `SubscriptionPaused` / `SubscriptionError` |
| `resumeSubscription(id)` | `/api/v1/subscriptions/{id}/resume` | POST | `ResumeSubscription` | `SubscriptionResumed` / `SubscriptionError` |
| `cancelSubscription(id, reason)` | `/api/v1/subscriptions/{id}/cancel` | POST | `CancelSubscription` | `SubscriptionCancelled` / `SubscriptionError` |
| `getMySubscriptions` | `GET /api/subscriptions/my` | GET | — | — |

#### Dart Service: `lib/services/subscription_sync_service.dart`

| Method | API Route | HTTP | Description |
|--------|-----------|------|-------------|
| `syncPlans()` | `/api/v1/subscriptions/plans` | GET | Force refresh All Plans (Cache + DB) |
| `syncActiveSubscription()` | `/api/v1/subscriptions/active` | GET | Force refresh Active Subscription |

#### Dart Service: `lib/services/bottle_service.dart`

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

#### Chargebee Webhook → Bottle Auto-Dispatch

```
INVOICE_PAID webhook → WebhookEventProcessor
  → processRelatedEntitiesForInvoice()
    → build line items JSON from invoice.lineItems()
    → bottleTrackingService.autoDispatchBottles(invoiceId, customerId, itemsJson)
      → recordIssue() creates bottle_transactions entry
```

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

### BLoC Event Handler Call Graph

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

## PART 3: SCHEDULE CHANGE & CANCELLATION SEMANTICS

### 3.1 Mid-Cycle Schedule Changes

| Scenario | Behavior | Pricing Impact |
|----------|----------|----------------|
| **User changes day-wise juice selection** (e.g., swap Monday from ABC Juice to Pineapple Juice) | Change is saved on bmjServer via `PUT /api/v1/subscriptions/{id}/schedule`. Since the schedule is metadata on the Chargebee subscription, the metadata is updated immediately. The new schedule applies **from the next scheduled delivery date** (not retroactively). | No price change (same plan, same size — different juice only) |
| **User changes plan mid-cycle** (e.g., upgrades from Delight 200ml weekly to Signature 300ml weekly) | **Not supported in current version.** User must cancel existing subscription and create a new one. This is a Chargebee limitation — mid-cycle plan changes on existing subscriptions require a `change_term` call which is not implemented. | Full pricing for old plan remains; new plan is a separate subscription |
| **User changes frequency mid-cycle** (e.g., weekly → monthly) | **Not supported in current version.** Same as plan change — cancel + re-subscribe. | — |

### 3.2 Mid-Week/Period Cancellation

| Scenario | Refund Behavior | Bottle Dispatch |
|----------|-----------------|-----------------|
| **Cancel weekly plan mid-week** (e.g., cancel on Wednesday, next charge is Saturday) | **No pro-rated refund.** The subscription runs until the end of the current billing period. This is handled entirely by Chargebee's `cancel_at_period_end` option. | Pre-scheduled bottles for remaining days of the week are **cancelled** if the dispatch has not yet occurred. Bottles already dispatched for past days are unaffected. |
| **Cancel monthly plan mid-month** (e.g., cancel on day 10, 14 days remain) | Same as above — `cancel_at_period_end`. No pro-rated refund. User retains access for the remainder of the paid period. | Same as weekly — future unshipped bottles cancelled. |
| **Immediate cancellation** (user selects "Cancel Now") | `cancel_immediately` is passed to Chargebee. The subscription is cancelled right away. **No refund is issued** unless the bmjServer admin processes a manual refund via Chargebee dashboard. | All future bottles (including same-day if not yet dispatched) are cancelled. |
| **Cancel on specific date** (user selects a future cancellation date) | Subscription continues until that date, then auto-cancels at end of that billing period. | Bottles scheduled up to the cancel date are dispatched as normal. Bottles after the cancel date are cancelled. |

### 3.3 Pause/Resume During a Period

| Action | Behavior | Bottle Impact |
|--------|----------|---------------|
| **Pause mid-week** | Pause takes effect **next day** if requested before 9 PM IST. If after 9 PM, takes effect day after next. The billing period is **not extended** — Chargebee still charges on the original schedule. | All bottles scheduled after the pause effective date are skipped. Any bottles scheduled before the pause date but not yet dispatched may still go out if within lead time. |
| **Resume mid-week** | Resume takes effect **next day** if before 9 PM IST. Same cutoff logic as pause. | Bottles resume on the day-wise schedule from the effective date forward. |
| **Pause at end of billing period** | Subscription pauses at the end of the current billing period (no next charge). | All bottles for the next period are skipped. |

### 3.4 Bottle Cap / Hard Limit Behavior

| Property | Value |
|----------|-------|
| **Bottle cap** | No hard cap defined in current version. Users can accumulate bottles indefinitely. |
| **UI when cart exceeds hypothetical cap** | N/A — no cap enforced. The `bottle_tracking` system records all bottle movements (dispatch, return, broken) but does not prevent further orders. |
| **Auto-dispatch on payment** | On `INVOICE_PAID` webhook, the system auto-creates bottle_transactions entries via `bottleTrackingService.autoDispatchBottles()`. This is **best-effort and non-blocking** — it won't prevent the order from completing even if auto-dispatch fails. |
| **Future cap implementation** | If a bottle cap is introduced later, the cart screen should check `GET /api/bottles/ledger` and show a warning when approaching the limit. The actual enforcement would be on the bmjServer side at checkout. |

### 3.5 Schedule Change API Contract

| Method | Endpoint | HTTP | Auth | Description |
|--------|----------|------|------|-------------|
| `updateSchedule(subscriptionId, schedule)` | `/api/v1/subscriptions/{id}/schedule` | PUT | Bearer JWT | Updates day-wise juice schedule for an active subscription |
| `getSchedule(subscriptionId)` | `/api/v1/subscriptions/{id}/schedule` | GET | Bearer JWT | Returns current day-wise schedule for debugging/display |

**Schedule Update Request Body:**
```json
{
  "day_schedule": {
    "Monday": "ABC Juice",
    "Tuesday": "Pineapple Juice",
    "Wednesday": "Pineapple Juice",
    "Thursday": "Pineapple Juice",
    "Friday": "Pineapple Juice",
    "Saturday": "Pineapple Juice"
  }
}
```

**Schedule Update Responses:**
| Status | Meaning |
|--------|---------|
| 200 OK | Schedule updated successfully on Chargebee metadata |
| 400 BAD_REQUEST | Invalid day names or juice names |
| 401 UNAUTHORIZED | Missing/invalid JWT |
| 403 FORBIDDEN | Not your subscription |
| 404 NOT_FOUND | Subscription not found |
| 409 CONFLICT | Subscription is not active (paused/cancelled) — cannot update schedule |

### 3.6 Cancel/Change Timeout & Retry

| Operation | Backend Timeout | Retry Strategy |
|-----------|-----------------|----------------|
| Cancel subscription | 10 seconds (Chargebee API) | Retry up to 3 times with exponential backoff (1s, 2s, 4s) |
| Pause subscription | 10 seconds (Chargebee API) | Retry up to 3 times |
| Resume subscription | 10 seconds (Chargebee API) | Retry up to 3 times |
| Update schedule | 5 seconds (Chargebee metadata update) | No retry — idempotent, user can retry manually |

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